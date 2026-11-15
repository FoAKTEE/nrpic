#!/usr/bin/env python3
"""Figure of the prediction for the prepared rerun of the two-overdensity case
(tracks/core/JOURNAL-clump.md, "Prediction for the rerun of the two-overdensity case"
and "Prediction for the control of the rerun"), drawn on the record of run
jeans/n1e4_v19 before the rerun exists.

    rerun_prediction_fig.py [--out DIR]

Top: horizon masses of n1e4_v19 (the two individual horizons summed, the common
horizon) against time, with the predicted band of M_AH(100 M) for the rerun and the
control (1.025 +- 0.010), the line below which the prediction is refuted (1.010) and
M = 1 of the initial data. Bottom: spin S of the common horizon, with the control's
band (0.089 +- 0.010) and the rerun's predicted range (0.105 to 0.135, refuted below
0.100). Writes figs/fig_clump_rerun_prediction.{png,pdf} and prints the values read.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
V19 = "/data/haiyangw/nrpic/runs/jeans/n1e4_v19"
sys.path.insert(0, os.path.join(WT, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def summary(k):
    """time, mass, S of horizon k (rows with nan dropped)."""
    a = np.genfromtxt(os.path.join(V19, f"jeans.horizon_summary_{k}.txt"), comments="#")
    a = a[np.isfinite(a[:, 2])]
    return a[:, 1], a[:, 2], a[:, 6]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(HERE, "figs"))
    a = ap.parse_args()
    fs.use_style()
    tA, mA, _ = summary(0)
    tB, mB, _ = summary(1)
    tC, mC, sC = summary(2)
    # both individual horizons, up to the first common horizon (later the finders
    # still return surfaces inside it)
    common = np.intersect1d(tA, tB)
    common = common[common <= tC[0]]
    mAB = np.interp(common, tA, mA) + np.interp(common, tB, mB)
    print(f"common horizon first at t = {tC[0]:.4f} M, M_AH = {mC[0]:.4f}; "
          f"last t = {tC[-1]:.4f} M, M_AH = {mC[-1]:.5f}, S = {sC[-1]:.5f}")
    print(f"individual horizons summed: first t = {common[0]:.3f} M "
          f"({mAB[0]:.4f}), last t = {common[-1]:.3f} M ({mAB[-1]:.4f})")

    fig = plt.figure(figsize=(fs.COLUMN_WIDTH * 1.5, 5.2))
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.10, top=0.98, hspace=0.0)
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
    blue, red = fs.PAL["blue"], fs.PAL["red"]

    ax1.plot(common, mAB, color=blue, ls="--", label=r"$M_A + M_B$, n1e4_v19")
    ax1.plot(tC, mC, color=blue, label=r"$M_{\rm AH}$ common, n1e4_v19")
    ax1.axhline(1.0, **fs.MASK_LINE)
    ax1.text(30.0, 1.005, r"$M = 1$ (initial data)", va="bottom", fontsize=9, color="grey")
    tb = np.array([96.0, 101.0])
    fs.band(ax1, tb, 1.015, 1.035, red)
    ax1.plot(tb, [1.025, 1.025], color=red, lw=1.5,
             label=r"predicted at 100 $M$: rerun and control")
    ax1.plot(tb, [1.010, 1.010], color=red, lw=1.0, ls=":",
             label="rerun refuted below")
    ax1.set_ylabel(r"horizon mass $/M$")
    ax1.set_ylim(0.0, 1.12)
    ax1.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax1.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86), ncol=1, fontsize=9)
    plt.setp(ax1.get_xticklabels(), visible=False)

    ax2.plot(tC, sC, color=blue, label=r"$S$ common, n1e4_v19")
    fs.band(ax2, tb, 0.079, 0.099, blue)
    ax2.plot(tb, [0.089, 0.089], color=blue, lw=1.0, ls="--", label="control, predicted")
    fs.band(ax2, tb, 0.105, 0.135, red)
    ax2.plot(tb, [0.100, 0.100], color=red, lw=1.0, ls=":", label="rerun refuted below")
    ax2.plot([], [], color=red, lw=6, alpha=0.2, label="rerun, predicted")
    ax2.axhline(0.1314, **fs.MASK_LINE)
    ax2.text(40.0, 0.1314 + 0.002, r"$J_{\rm ADM}$ of the rerun's slice (0.131)",
             va="bottom", fontsize=9, color="grey")
    ax2.set_xlabel(r"$t/M$", labelpad=-2)
    ax2.set_ylabel(r"spin $S/M^2$")
    ax2.set_xlim(0.0, 102.0)
    ax2.set_ylim(0.0, 0.15)
    ax2.set_yticks([0.0, 0.04, 0.08, 0.12])
    ax2.legend(loc="lower left", ncol=1, fontsize=9)
    os.makedirs(a.out, exist_ok=True)
    fs.save(fig, os.path.join(a.out, "fig_clump_rerun_prediction"))
    print("wrote", os.path.join(a.out, "fig_clump_rerun_prediction.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
