#!/usr/bin/env python3
"""Figure of G2M-1: the tree model against P1's restart trees and `athena -m`.

(a) MeshBlocks of P1's restart files (t = 0 ... 110) and of the model at P1's tracker
    positions, with the mean MeshBlock count of each chain segment (MeshBlock-cycles /
    cycles of its log); (b) model against `athena -m` at the start for the eight variants and
    core's by_triple. Reads <model run>/model.json.
Usage: fig_model_check.py <model.json> <outdir>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def main():
    d = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2),
                           gridspec_kw=dict(width_ratios=[1.25, 1]))
    C = d["C_p1_restarts"]
    t = np.array([r["time"] for r in C["rst"]])
    n = np.array([r["nmb"] for r in C["rst"]])
    mdl = np.array([r["model"] for r in C["rst"]])
    ax[0].plot(t, n, "o", ms=5, mfc="none", color=fs.PAL["blue"], label="restart files of P1")
    ax[0].plot(t, mdl, "x", ms=5, color=fs.PAL["red"], label="model at the tracker positions")
    bad = [r for r in C["rst"] if not r["equal_levels"]]
    for r in bad:
        ax[0].annotate("model 8 cycles earlier: %d" % r["model_back"]["8"],
                       (r["time"], r["model"]), xytext=(r["time"] + 8, r["model"] + 60),
                       fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.6))
    for k, s in enumerate(C["segments"]):
        if s.get("mean_nmb"):
            ax[0].plot([s["t0"], s["t1"]], [s["mean_nmb"]] * 2, "-", color=fs.PAL["green"],
                       lw=2, label="mean of a chain segment" if k == 0 else None)
    ax[0].set_xlabel(r"$t\,[M]$")
    ax[0].set_ylabel("MeshBlocks (16$^3$)")
    ax[0].set_title("P1 (m/8): %d of %d trees equal level by level" %
                    (sum(r["equal_levels"] for r in C["rst"]), len(C["rst"])), fontsize=8)
    ax[0].legend(fontsize=7, loc="lower left")
    ax[0].set_ylim(800, 2100)

    B = d["B_athena_m"]["rows"]
    lab = [r["case"].replace("_b", "\n") for r in B]
    x = np.arange(len(B))
    ax[1].bar(x - 0.2, [r["athena_m"] for r in B], 0.4, color=fs.PAL["blue"],
              label="athena -m (core-v0.3)")
    ax[1].bar(x + 0.2, [r["model"] for r in B], 0.4, color=fs.PAL["red"], label="model")
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(lab, fontsize=6)
    ax[1].set_ylabel("MeshBlocks at the start")
    ax[1].set_title("start rule: %s" % ("all equal level by level" if d["B_athena_m"]["all_equal"]
                                        else "DIFFERENCES"), fontsize=8)
    ax[1].legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    for p in fs.save(fig, os.path.join(out, "fig_model_check")):
        print("figure:", p)


if __name__ == "__main__":
    main()
