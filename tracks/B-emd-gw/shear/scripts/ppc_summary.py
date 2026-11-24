#!/usr/bin/env python3
"""L2 of the shearing-dust test against the particle number along y (series 3-5, batch 11).

    python3 ppc_summary.py NAME:CASEDIR [NAME:CASEDIR ...] [--out DIR]   (default $NRPIC_RUN_DIR)

Each CASEDIR holds a rays.json of analyze_rays.py. Writes ppc_summary.json (Delta, the quadratic
shooting, ppc_y, N_y, constraint means over 1 <= t <= t_A) and fig_ppc (Delta against 1/ppc_y per
N_y, with the three codes of draft.tex:360).
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

CODES = {"CosmoGRaPH": -0.8183, "GRAMSES": -0.68, "gevolution": -0.619}   # draft.tex:360


def main():
    args = list(sys.argv[1:])
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    rows = []
    for spec in args:
        name, d = spec.split(":", 1)
        r = json.load(open(os.path.join(d, "rays.json")))
        cs = r["cstat_series"]
        t = np.array(cs["t"])
        sel = (t >= 1.0) & (t <= r["t_A"])
        rows.append({"name": name, "dir": d, "ny": r["ny"], "ppc_y": r["ppc_y"], "Delta": r["Delta"],
                     "Delta_quad": r["Delta_quad"], "t_A": r["t_A"], "t_B": r["t_B"],
                     "Hr_mean_1_tA": float(np.mean(np.array(cs["Hr_mean"])[sel])),
                     "Mr_mean_1_tA": float(np.mean(np.array(cs["Mr_mean"])[sel]))})
    with open(os.path.join(out, "ppc_summary.json"), "w") as f:
        json.dump(rows, f, indent=1)
    for r in rows:
        print(f"{r['name']}: N_y {r['ny']}, ppc_y {r['ppc_y']}: Delta {r['Delta']:.5f} "
              f"(quad {r['Delta_quad']:.5f}); Hr {r['Hr_mean_1_tA']:.3f}, Mr {r['Mr_mean_1_tA']:.3f}")
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH*0.5, 2.9))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.17, top=0.95)
    for ny, col in zip(sorted({r["ny"] for r in rows}), fs.SERIES):
        rr = sorted([r for r in rows if r["ny"] == ny], key=lambda r: r["ppc_y"])
        ax.plot([1.0/r["ppc_y"] for r in rr], [r["Delta"] for r in rr], "o-", color=col, lw=1.0,
                label=r"$N_y = %d$" % ny)
    for (k, v), col in zip(CODES.items(), fs.SERIES[2:]):
        if v > -0.75:
            continue
        ax.axhline(v, color=col, ls="--", lw=0.9, label=k + " (draft.tex:360)")
    ax.set_xlabel(r"$1/n_{\rm ppc,y}$")
    ax.set_ylabel(r"$\Delta$ of L2")
    ax.legend(fontsize=6.5, loc="best")
    fs.save(fig, os.path.join(out, "fig_ppc"))
    plt.close(fig)


if __name__ == "__main__":
    main()
