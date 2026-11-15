#!/usr/bin/env python3
"""Lead's wave-2 re-check of the Newtonian-mode infall runs (JOURNAL.md, prediction W6).

My own reader and loop over the AthenaK snapshots of the cell-centred runs (N128c
D-20261115-171503-4262f03, N64c -171505-62940f4, N128Lc -171507-d1058a9); the definitions
of the turnaround mass and the dress are those stated in the docstring of
secondary_infall/nm_analyze.py (re-implemented here, not imported). As a definition-free
cross-check, the mass inside r_ta, the outermost radius where the mass-weighted mean radial
velocity in 0.05-dex shells changes sign from negative (inside) to positive (outside).
Writes infall_check.json and infall_check.png into --out.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
RUNS = {"N128c": "D-20261115-171503-4262f03", "N64c": "D-20261115-171505-62940f4",
        "N128Lc": "D-20261115-171507-d1058a9"}
CLAIM = {"N128c": (2.597, 0.797), "N64c": (2.597, 0.797), "N128Lc": (4.816, 2.154)}


def snap(path):
    with open(path, "rb") as fh:
        assert fh.read(8) == b"NRPSNAP1"
        t = float(np.frombuffer(fh.read(8), "<f8")[0])
        n = int(np.frombuffer(fh.read(8), "<i8")[0])
        fh.read(8)
        rec = np.frombuffer(fh.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(fh.read(4 * n), "<i4")
    return t, rec, tag


def r_ta_mass(r, vr, m, mclump):
    edges = np.geomspace(0.3, 300.0, 3 * 20 + 1)
    w, _ = np.histogram(r, edges, weights=m)
    wv, _ = np.histogram(r, edges, weights=m * vr)
    with np.errstate(invalid="ignore"):
        v = wv / w
    good = w > 0
    # outermost i with v[i] < 0 and v[i+1] > 0
    idx = [i for i in range(len(v) - 1) if good[i] and good[i + 1] and v[i] < 0 < v[i + 1]]
    if not idx:
        return None, None
    i = idx[-1]
    # linear interpolation of the zero in ln r between bin centres
    c = np.sqrt(edges[:-1] * edges[1:])
    lr = np.log(c[i]) + (np.log(c[i + 1]) - np.log(c[i])) * (-v[i]) / (v[i + 1] - v[i])
    rta = float(np.exp(lr))
    return rta, float(mclump + m[r < rta].sum())


def analyse(rundir):
    p = json.load(open(os.path.join(rundir, "setup.json")))
    files = sorted(glob.glob(os.path.join(rundir, "infall.part.*.bin")))
    c0, c1 = p["tag_clump"]
    d0, d1 = p["tag_dust"]
    shift = np.asarray(p.get("shift", [0, 0, 0]), float)
    n = p["n_total"]
    t0, rec, tag = snap(files[0])
    x0 = np.zeros((n, 3))
    x0[tag] = rec[:, :3] - shift
    mass = np.zeros(n)
    mass[tag] = rec[:, 6]
    turned = np.zeros(n, bool)
    passed = np.zeros(n, bool)
    dust = np.zeros(n, bool)
    dust[d0:d1] = True
    mclump = mass[c0:c1].sum()
    rows = []
    for fn in files:
        t, rec, tag = snap(fn)
        x = np.full((n, 3), np.nan)
        u = np.full((n, 3), np.nan)
        x[tag] = rec[:, :3] - shift
        u[tag] = rec[:, 3:6]
        alive = ~np.isnan(x[:, 0])
        r = np.sqrt((x ** 2).sum(1))
        with np.errstate(invalid="ignore", divide="ignore"):
            vr = (x * u).sum(1) / r
        other_side = (x * x0).sum(1) < 0
        passed |= alive & dust & (other_side | (turned & (vr > 0)))
        turned |= alive & dust & (vr < 0)
        a = ((p["t_i"] + t) / p["t_i"]) ** (2.0 / 3.0)
        sel = alive & dust
        rta, mrta = r_ta_mass(r[sel], vr[sel], mass[sel], mclump)
        rows.append(dict(t=t, a=a, M_ta=float(mclump + mass[turned].sum()),
                         dress=float(mass[passed].sum()), r_ta=rta, M_in_rta=mrta))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    out = {}
    res = {}
    for lab, rid in RUNS.items():
        rows = analyse(os.path.join(SCR, rid))
        res[lab] = rows
        last = rows[-1]
        a4 = min(rows, key=lambda r: abs(r["a"] - 4.0))
        out[lab] = dict(run=rid, a_end=last["a"], end=last, at_a4=a4,
                        claim_end=CLAIM[lab],
                        rel_Mta=last["M_ta"] / CLAIM[lab][0] - 1,
                        rel_dress=last["dress"] / CLAIM[lab][1] - 1,
                        Min_rta_over_Mta=(last["M_in_rta"] / last["M_ta"]) if last["M_in_rta"] else None)
    with open(os.path.join(args.out, "infall_check.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4, 3.2))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.97)
    cols = {"N128c": fs.PAL["red"], "N64c": fs.PAL["yellow"], "N128Lc": fs.PAL["green"]}
    for lab, rows in res.items():
        a = [r["a"] for r in rows]
        ax.plot(a, [r["M_ta"] for r in rows], color=cols[lab], label=f"{lab}: $M_{{ta}}$")
        ax.plot(a, [r["dress"] for r in rows], color=cols[lab], ls="--")
        ax.plot(a, [r["M_in_rta"] if r["M_in_rta"] else np.nan for r in rows], ".", color=cols[lab], ms=3)
    for lab, (mta, md) in CLAIM.items():
        aa = 8.0 if lab == "N128Lc" else 4.0
        ax.plot([aa], [mta], "o", mfc="none", color=fs.PAL["blue"])
        ax.plot([aa], [md], "s", mfc="none", color=fs.PAL["blue"])
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel(r"mass [$M$]")
    ax.legend(frameon=False)
    fs.save(fig, os.path.join(args.out, "infall_check"))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
