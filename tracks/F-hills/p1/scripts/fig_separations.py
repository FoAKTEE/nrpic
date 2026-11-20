#!/usr/bin/env python3
"""Figure: member-hole and member-member distances of P1 against t, with the full-Newton
and HRNA baselines (same start state), and the distance of the binary's centre of mass from M.

Top: |x_1 - x_M|, |x_2 - x_M| (log scale); bottom: |x_1 - x_2| and the centre of mass
distance. P1 solid, Newton dashed, HRNA dotted. Grey: 2 a_b = 10.2 M (separation criterion of
the P1 prediction, item 2). Writes <out>/fig_separations.{pdf,png}.
Usage: fig_separations.py [--out=<dir>] [--rundir=<dir>] [--baselines-npz=<file>] [--tmax=T]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402
import figstyle as fs  # noqa: E402


def main():
    out = p1lib.out_dir(sys.argv)
    rd = p1lib.rundir(sys.argv)
    t, X, _ = p1lib.tracker_common(rd)
    b = p1lib.baselines(p1lib.baseline_path(sys.argv, out))
    tmax = max(float(t[-1]) + 30.0, 150.0)
    for a in sys.argv[1:]:
        if a.startswith("--tmax="):
            tmax = float(a.split("=")[1])
    m = p1lib.MASSES
    a_b = p1lib.baselines_json()["a_b"]

    def dists(Xa):
        xc = (m[0] * Xa[:, 0] + m[1] * Xa[:, 1]) / (m[0] + m[1])
        return (np.linalg.norm(Xa[:, 0] - Xa[:, 2], axis=1),
                np.linalg.norm(Xa[:, 1] - Xa[:, 2], axis=1),
                np.linalg.norm(Xa[:, 0] - Xa[:, 1], axis=1),
                np.linalg.norm(xc - Xa[:, 2], axis=1))

    nr_ = dists(X)
    tn = b["newton_t"]
    nw = dists(b["newton_X"])
    th = b["hrna_t"]
    Yh = b["hrna_y"]
    xch = (m[0] * Yh[:, 0:3] + m[1] * Yh[:, 6:9]) / (m[0] + m[1])
    hr = (np.linalg.norm(Yh[:, 0:3], axis=1), np.linalg.norm(Yh[:, 6:9], axis=1),
          np.linalg.norm(Yh[:, 0:3] - Yh[:, 6:9], axis=1), np.linalg.norm(xch, axis=1))

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.95, hspace=0.06)
    ax = axs[0]
    for k, col, lab in ((0, fs.PAL["blue"], r"$m_1$"), (1, fs.PAL["red"], r"$m_2$")):
        ax.plot(t, nr_[k], color=col, lw=1.5, label=f"{lab}: P1 (NR)")
        ax.plot(tn, nw[k], color=col, lw=1.0, ls="--", label=f"{lab}: Newton")
        ax.plot(th, hr[k], color=col, lw=1.0, ls=":", label=f"{lab}: HRNA")
    ax.axvline(t[-1], **fs.MASK_LINE)
    ax.set_yscale("log")
    ax.set_ylim(2, 60)
    ax.set_ylabel(r"distance from $M$ $[M]$")
    ax.legend(frameon=False, fontsize=7, ncol=2, loc="lower left")
    ax = axs[1]
    ax.plot(t, nr_[2], color=fs.PAL["yellow"], lw=1.5, label=r"$|x_1-x_2|$ P1")
    ax.plot(tn, nw[2], color=fs.PAL["yellow"], lw=1.0, ls="--", label="Newton")
    ax.plot(th, hr[2], color=fs.PAL["yellow"], lw=1.0, ls=":", label="HRNA")
    ax.plot(t, nr_[3], color=fs.PAL["green"], lw=1.5, label="centre of mass from $M$, P1")
    ax.plot(tn, nw[3], color=fs.PAL["green"], lw=1.0, ls="--", label="Newton")
    ax.plot(th, hr[3], color=fs.PAL["green"], lw=1.0, ls=":", label="HRNA")
    ax.axhline(2 * a_b, **fs.MASK_LINE)
    ax.text(3, 2 * a_b * 1.04, r"$2a_b$", fontsize=7, color="grey")
    ax.axvline(t[-1], **fs.MASK_LINE)
    ax.set_ylim(0, 40)
    ax.set_xlim(0, tmax)
    ax.set_xlabel(r"$t\ [M]$")
    ax.set_ylabel(r"distance $[M]$")
    ax.legend(frameon=False, fontsize=7, ncol=2, loc="upper left")
    for p in fs.save(fig, os.path.join(out, "fig_separations")):
        print("figure:", p)


if __name__ == "__main__":
    main()
