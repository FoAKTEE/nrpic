"""Diagnose the particles of the Kerr seed-2 run whose invariants were not conserved
(JOURNAL N4). Analysis only.

Reads the seed-2 analysis (kerr_seed2_series.npz: max |dE/E| per particle), the initial data
(ic_meta.npz: E, Lz, C, r, rp; ic_summary.json: file index), and the snapshots of the run.
For each particle with max |dE/E| above 1e-3 or not finite: its radius at every snapshot,
the snapshot of the plunge (first r < r_+), its initial distance from the capture boundary,
(C - C_crit)/C_crit with C_crit = min over r_+ < r' <= r0 of C_V(r') (kerr_lib.Kerr.ccrit),
and the change of the 0-4 time average if its snapshots after the plunge are not counted.
Also the same distance for all particles, to place it in the sample.

usage: python3 plunger.py --ana <analysis dir> --ic <ic dir> --run <run dir> --out DIR
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TRACK = HERE.parents[1]
sys.path.insert(0, str(TRACK / "spike"))
sys.path.insert(0, str(TRACK.parents[1] / "python"))
from analyze_spike import read_snap  # noqa: E402
from kerr_lib import Kerr  # noqa: E402
from nrpic import kerr as nk, figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ana", required=True)
    ap.add_argument("--ic", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    S = np.load(Path(a.ana) / "kerr_seed2_series.npz")
    A = json.load(open(Path(a.ana) / "kerr_seed2_analysis.json"))
    M = np.load(Path(a.ic) / "ic_meta.npz")
    summ = json.load(open(Path(a.ic) / "ic_summary.json"))
    spin = summ["args"]["a"]
    K = Kerr(spin)
    bad = np.flatnonzero(~np.isfinite(S["maxdE"]) | (S["maxdE"] > 1e-3))
    # capture-boundary distance for every particle (initial invariants, starting radius)
    Cc, ru, end = K.ccrit(M["E"], M["Lz"], M["r"])
    dist = (M["C"] - Cc) / Cc
    runs = sorted(p for p in Path(a.run).iterdir() if p.is_dir() and p.name.startswith("kerr_"))
    files = {r: np.array(summ["file_index"][(r / "run_file.txt").read_text().strip()]) for r in runs}
    snaps = {r: sorted(r.glob("*.part.*.bin")) for r in runs}
    nsnap = min(len(v) for v in snaps.values())
    where = {}
    for i in bad:
        for r in runs:
            if i in files[r]:
                where[int(i)] = r
    rad = {int(i): np.full(nsnap, np.nan) for i in bad}
    t = np.zeros(nsnap)
    for k in range(nsnap):
        for i in bad:
            r = where[int(i)]
            tt, rec, tag, sp = read_snap(snaps[r][k])
            g = files[r][tag]
            j = np.flatnonzero(g == i)
            t[k] = tt
            if j.size:
                rad[int(i)][k] = float(nk.cks_radius(rec[j, :3], spin)[0])
    rplus = 1.0 + np.sqrt(1.0 - spin ** 2)
    e04 = A["ranges"]["0-4"]["expected"]
    tavg04 = A["ranges"]["0-4"]["time_avg_over_expected"]
    res = {"r_plus": rplus, "n_bad": int(bad.size), "particles": [],
           "dist_all": {"min": float(np.nanmin(dist)), "quantiles_1e-4_1e-3_1e-2":
                        [float(np.nanquantile(dist, q)) for q in (1e-4, 1e-3, 1e-2)],
                        "n_below_1e-3": int(np.sum(dist < 1e-3)), "n_below_1e-2": int(np.sum(dist < 1e-2))}}
    for i in bad:
        i = int(i)
        rr = rad[i]
        inside = np.flatnonzero(rr < rplus)
        k0 = int(inside[0]) if inside.size else None
        n04_after = int(np.sum(rr[k0:] < 4.0)) if k0 is not None else 0
        res["particles"].append(dict(
            index=i, file=where[i].name, E=float(M["E"][i]), Lz=float(M["Lz"][i]), C=float(M["C"][i]),
            r0=float(M["r"][i]), rp_pred=float(M["rp"][i]), ra_pred=float(M["ra"][i]),
            C_crit=float(Cc[i]), dist_rel=float(dist[i]),
            rank_of_dist=int(np.sum(dist < dist[i])), maxdE=float(S["maxdE"][i]),
            r_min_before_plunge=float(np.nanmin(rr[:k0])) if k0 else float(np.nanmin(rr)),
            first_snapshot_inside=k0, t_plunge_bracket=[float(t[k0 - 1]), float(t[k0])] if k0 else None,
            snapshots_after_inside_0_4=n04_after,
            tavg04_shift=float(n04_after / nsnap / e04)))
    shift = sum(p["tavg04_shift"] for p in res["particles"])
    res["tavg04_seed2"] = tavg04
    res["tavg04_seed2_without_plunged"] = tavg04 - shift
    json.dump(res, open(out / "plunger.json", "w"), indent=1)
    figstyle.use_style()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.0))
    for i in bad:
        ax.plot(t, rad[int(i)], lw=1.0, label=f"particle {int(i)}")
    ax.axhline(rplus, **figstyle.GUIDE)
    ax.set_yscale("log"); ax.set_xlabel("$t$ ($M$)"); ax.set_ylabel("$r$ ($M$)")
    ax.legend(fontsize=7, frameon=False)
    ax.text(0.03, 0.05, "(a) dashed: $r_+$", transform=ax.transAxes)
    d = dist[np.isfinite(dist) & (dist > 0)]
    bx.hist(np.log10(d), bins=60, color=figstyle.PAL["blue"])
    for p in res["particles"]:
        if p["dist_rel"] > 0:
            bx.axvline(np.log10(p["dist_rel"]), color=figstyle.PAL["red"], lw=1.5)
    bx.set_xlabel(r"$\log_{10}[(C-C_{\rm crit})/C_{\rm crit}]$ at $t=0$")
    bx.set_ylabel("particles")
    bx.text(0.03, 0.9, "(b) red: plunging particle", transform=bx.transAxes)
    fig.tight_layout()
    figstyle.save(fig, str(out / "plunger"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
