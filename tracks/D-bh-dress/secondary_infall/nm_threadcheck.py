#!/usr/bin/env python3
"""Check of the threaded processor build against the serial release build on one input
(wave 3, R8 against N128Lc). Analysis of AthenaK output only (decision 0010).

Two runs of nm_run.py with the same particle file and deck (A = reference, B = test):
  inputs     sha256 of particles.nrp and of the deck; command lines without the output path;
  history    <base>.newton.hst: first record (K, W, W_mesh, C) relative differences; step
             count; records matched by cycle: largest relative difference of K and W, dt;
  particles  snapshots with the same index (same snap_dt): by tag, max and rms of
             |x_B - x_A| for dust and clump in units of dx, the fraction of dust farther apart
             than 1e-6 dx and 1e-2 dx; clump centre of mass difference;
  physics    nm_analyze.analyse_run of both: M_ta and dress at every snapshot and at the
             round a/a_i (4, 8), the dust profile rho/rho_b per 0.1-dex bin for 4 dx <= r <= r_ta
             with the bins of the outermost caustic (steepest fall of A's profile inside
             1.5 r_ta, as nm_analyze.py) reported separately.
Writes nm_threadcheck.json and the figure nm_threadcheck (positions, masses, profiles).

Usage: python3 nm_threadcheck.py --a LABEL:RUNDIR --b LABEL:RUNDIR [--at 4 8] --out DIR
"""
import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import load_figstyle, KAPPA      # noqa: E402
from nrpic import newton as nw               # noqa: E402
import nm_analyze as NA                      # noqa: E402


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def by_tag(fn, n_tot, shift):
    t, cyc, x, u, m, tag = nw.read_snapshot(fn)
    X = np.full((n_tot, 3), np.nan)
    X[tag] = x - shift
    return t, cyc, X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--a", required=True, help="LABEL:RUNDIR of the reference run")
    ap.add_argument("--b", required=True, help="LABEL:RUNDIR of the run checked")
    ap.add_argument("--at", type=float, nargs="+", default=[4.0, 8.0])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    la, da = a.a.split(":", 1)
    lb, db = a.b.split(":", 1)
    res = dict(a=dict(label=la, dir=da), b=dict(label=lb, dir=db))

    # ---- inputs
    ma = json.load(open(os.path.join(da, "nm_run.json")))
    mb = json.load(open(os.path.join(db, "nm_run.json")))
    strip = lambda c, d: [x.replace(d, "<run>") for x in c[1:]]
    res["inputs"] = dict(
        particles_sha256=[sha(os.path.join(da, "particles.nrp")), sha(os.path.join(db, "particles.nrp"))],
        deck_sha256=[ma["deck_sha256"], mb["deck_sha256"]],
        exe=[ma["exe"], mb["exe"]], exe_sha256=[ma["exe_sha256"], mb["exe_sha256"]],
        threads=[ma.get("threads", 1), mb.get("threads", 1)],
        args_equal=strip(ma["cmd"], da) == strip(mb["cmd"], db),
        args_a=strip(ma["cmd"], da), args_b=strip(mb["cmd"], db))
    res["inputs"]["particles_identical"] = res["inputs"]["particles_sha256"][0] == res["inputs"]["particles_sha256"][1]

    # ---- history
    ha = nw.read_newton_hst(glob.glob(os.path.join(da, "*.newton.hst"))[0])
    hb = nw.read_newton_hst(glob.glob(os.path.join(db, "*.newton.hst"))[0])
    first = {k: float(abs(hb[k][0] / ha[k][0] - 1)) for k in ("K", "W", "W_mesh", "C")}
    ca, cb = ha["ncycle"].astype(int), hb["ncycle"].astype(int)
    common = np.intersect1d(ca, cb)
    ia = np.searchsorted(ca, common)
    ib = np.searchsorted(cb, common)
    relK = np.abs(hb["K"][ib] / ha["K"][ia] - 1)
    relW = np.abs(hb["W"][ib] / ha["W"][ia] - 1)
    reldt = np.abs(hb["dt"][ib] / np.where(ha["dt"][ia] != 0, ha["dt"][ia], np.nan) - 1)
    res["history"] = dict(first_record_rel=first, steps=[int(ca[-1]), int(cb[-1])],
                          t_end=[float(ha["time"][-1]), float(hb["time"][-1])],
                          K_rel_max=float(np.nanmax(relK)), W_rel_max=float(np.nanmax(relW)),
                          dt_rel_max=float(np.nanmax(reldt[1:])) if reldt.size > 1 else None,
                          mg_cycles_mean=[float(np.mean(ha["mg_cycles"])), float(np.mean(hb["mg_cycles"]))])

    # ---- particles snapshot by snapshot
    p = json.load(open(os.path.join(da, "setup.json")))
    n_tot, (c0, c1), (d0, d1) = p["n_total"], p["tag_clump"], p["tag_dust"]
    shift = np.asarray(p.get("shift", [0, 0, 0]))
    dx = ma["dx"]
    fa = sorted(glob.glob(os.path.join(da, "infall.part.*.bin")))
    fb = sorted(glob.glob(os.path.join(db, "infall.part.*.bin")))
    n = min(len(fa), len(fb))
    snaps = []
    for k in range(n):
        ta, _, Xa = by_tag(fa[k], n_tot, shift)
        tb, _, Xb = by_tag(fb[k], n_tot, shift)
        d = np.sqrt(((Xb - Xa) ** 2).sum(1)) / dx
        dd, dc = d[d0:d1], d[c0:c1]
        okd, okc = np.isfinite(dd), np.isfinite(dc)
        coma = np.nanmean(Xa[c0:c1], axis=0)
        comb = np.nanmean(Xb[c0:c1], axis=0)
        snaps.append(dict(k=k, t_a=ta, t_b=tb, a=((p["t_i"] + ta) / p["t_i"]) ** (2.0 / 3.0),
                          dust_max=float(dd[okd].max()), dust_rms=float(np.sqrt(np.mean(dd[okd] ** 2))),
                          dust_median=float(np.median(dd[okd])),
                          dust_frac_gt_1em6=float(np.mean(dd[okd] > 1e-6)),
                          dust_frac_gt_1em2=float(np.mean(dd[okd] > 1e-2)),
                          clump_max=float(dc[okc].max()), clump_rms=float(np.sqrt(np.mean(dc[okc] ** 2))),
                          com_diff=float(np.sqrt(((comb - coma) ** 2).sum()) / dx),
                          n_alive=[int(np.isfinite(Xa[:, 0]).sum()), int(np.isfinite(Xb[:, 0]).sum())]))
    res["particles"] = snaps

    # ---- physics: masses, profiles
    Ra, Rb = NA.analyse_run(da), NA.analyse_run(db)
    rows_a, rows_b = Ra["rows"], Rb["rows"]
    av = np.array([x["a"] for x in rows_a])
    mta_a = np.array([x["mta"] for x in rows_a])
    mta_b = np.array([x["mta"] for x in rows_b])
    dr_a = np.array([x["dress"] for x in rows_a])
    dr_b = np.array([x["dress"] for x in rows_b])
    m = min(len(av), len(mta_b))
    late = av[:m] >= 1.5
    res["masses"] = dict(
        mta_rel_max_after_1p5=float(np.max(np.abs(mta_b[:m][late] / mta_a[:m][late] - 1))),
        dress_rel_max_after_2=float(np.max(np.abs(dr_b[:m][av[:m] >= 2] / dr_a[:m][av[:m] >= 2] - 1))),
        dust_particle_mass=float(Ra["md"][0]))
    rc = np.sqrt(NA.LEDGES[1:] * NA.LEDGES[:-1])
    at = []
    for aa in a.at:
        k = int(np.argmin(np.abs(av[:m] - aa)))
        pa_, pb_ = np.array(Ra["profiles"][k]["rho"]), np.array(Rb["profiles"][k]["rho"])
        tc = p["t_i"] + rows_a[k]["t"]
        r_ta = (rows_a[k]["mta"] * tc ** 2 / KAPPA) ** (1.0 / 3.0)
        ok = (rc >= 4 * dx) & (rc <= r_ta) & (pa_ > 0) & (pb_ > 0)
        lr = np.log(np.where(pa_ > 0, pa_, np.nan))
        jump = np.where(rc[1:] < 1.5 * r_ta, np.diff(lr), np.nan)
        jc = int(np.nanargmin(jump)) if np.isfinite(jump).any() else -10
        near = np.zeros(rc.size, bool)
        near[max(jc - 1, 0):jc + 3] = True
        ratio = pb_[ok] / pa_[ok]
        keep = ~near[ok]
        com_a = np.array(rows_a[k]["com"])
        com_b = np.array(rows_b[k]["com"])
        at.append(dict(a_target=aa, a=float(av[k]), mta=[rows_a[k]["mta"], rows_b[k]["mta"]],
                       dress=[rows_a[k]["dress"], rows_b[k]["dress"]],
                       mta_rel=rows_b[k]["mta"] / rows_a[k]["mta"] - 1,
                       dress_rel=rows_b[k]["dress"] / rows_a[k]["dress"] - 1,
                       dress_diff_particles=(rows_b[k]["dress"] - rows_a[k]["dress"]) / float(Ra["md"][0]),
                       mta_diff_particles=(rows_b[k]["mta"] - rows_a[k]["mta"]) / float(Ra["md"][0]),
                       r=rc[ok].tolist(), ratio=ratio.tolist(),
                       caustic_r=float(np.sqrt(rc[jc] * rc[jc + 1])) if jc >= 0 else None,
                       max_dev_excl_caustic=float(np.max(np.abs(ratio[keep] - 1))) if keep.any() else None,
                       max_dev_caustic=float(np.max(np.abs(ratio[~keep] - 1))) if (~keep).any() else None,
                       com_a_over_dx=float(np.abs(com_a).max() / dx), com_b_over_dx=float(np.abs(com_b).max() / dx),
                       com_diff_over_dx=float(np.sqrt(((com_b - com_a) ** 2).sum()) / dx),
                       r_sp99=[rows_a[k].get("r_sp99"), rows_b[k].get("r_sp99")]))
    res["at"] = at
    with open(os.path.join(a.out, "nm_threadcheck.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "particles"}, indent=1))
    print("particles (a, dust max/rms/median in dx, frac > 1e-6 dx, clump max, com diff):")
    for s in snaps[::5] + snaps[-1:]:
        print(f"  {s['a']:.3f} {s['dust_max']:.3e} {s['dust_rms']:.3e} {s['dust_median']:.3e} "
              f"{s['dust_frac_gt_1em6']:.4f} {s['clump_max']:.3e} {s['com_diff']:.3e}")

    # ---- figure
    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 7.4))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.07, top=0.98, hspace=0.32)
    sa = np.array([s["a"] for s in snaps])
    tiny = 1e-18
    axs[0].plot(sa, [s["dust_max"] + tiny for s in snaps], "-", color=fs.PAL["red"], label="dust, max")
    axs[0].plot(sa, [s["dust_rms"] + tiny for s in snaps], "--", color=fs.PAL["red"], label="dust, rms")
    axs[0].plot(sa, [s["dust_median"] + tiny for s in snaps], ":", color=fs.PAL["red"], label="dust, median")
    axs[0].plot(sa, [s["clump_max"] + tiny for s in snaps], "-", color=fs.PAL["blue"], label="clump, max")
    axs[0].plot(sa, [s["com_diff"] + tiny for s in snaps], "-.", color=fs.PAL["green"], label="clump centre of mass")
    axs[0].set_yscale("log")
    axs[0].set_xscale("log")
    axs[0].set_ylabel(f"$|x_{{\\rm {lb}}} - x_{{\\rm {la}}}|/\\Delta x$")
    axs[0].set_xlabel(r"$a/a_i$", labelpad=-2)
    axs[0].legend(fontsize=6.5, loc="lower right", ncol=2)
    k = av[:m] >= 1.2
    axs[1].plot(av[:m][k], mta_b[:m][k] / mta_a[:m][k] - 1, "o", ms=2.5, color=fs.PAL["red"], label="$M_{\\rm ta}$")
    kd = k & (dr_a[:m] > 0.02)
    axs[1].plot(av[:m][kd], dr_b[:m][kd] / dr_a[:m][kd] - 1, "s", ms=2.5, mfc="none", color=fs.PAL["blue"],
                label="dress")
    axs[1].axhline(0, **fs.GUIDE)
    axs[1].axhspan(-1e-3, 1e-3, color="grey", alpha=0.15)
    axs[1].set_xscale("log")
    axs[1].set_ylim(-3e-3, 3e-3)
    axs[1].set_ylabel(f"{lb} / {la} $-$ 1")
    axs[1].set_xlabel(r"$a/a_i$", labelpad=-2)
    axs[1].legend(fontsize=7, loc="lower right")
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"]]
    for i, e in enumerate(at):
        axs[2].plot(e["r"], np.array(e["ratio"]) - 1, "o-", ms=3, lw=1.0, color=cols[i % 3],
                    label=f"$a/a_i$ = {e['a']:.2f}")
        if e["caustic_r"]:
            axs[2].axvline(e["caustic_r"], color=cols[i % 3], lw=0.8, ls=":")
    axs[2].axhline(0, **fs.GUIDE)
    axs[2].axhspan(-0.01, 0.01, color="grey", alpha=0.15)
    axs[2].set_xscale("log")
    axs[2].set_ylim(-0.06, 0.06)
    axs[2].set_xlabel(r"$r$ [$GM/c^2$] ($4\Delta x \leq r \leq r_{\rm ta}$)", labelpad=-2)
    axs[2].set_ylabel(r"$\rho_{\rm " + lb + r"}/\rho_{\rm " + la + r"} - 1$")
    axs[2].legend(fontsize=7, loc="lower left")
    fs.save(fig, os.path.join(a.out, "nm_threadcheck"))
    plt.close(fig)


if __name__ == "__main__":
    main()
