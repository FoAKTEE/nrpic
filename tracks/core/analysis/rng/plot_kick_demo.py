#!/usr/bin/env python3
"""Figure of the demonstration of the reproducible kick (run_kick_demo.py).

Left: the accumulated kick, u_x of the kicked run minus u_x of the run without kick,
against the normal density of width sigma sqrt(t). Right: for every pair of runs that is
compared, the distribution over the particles of the largest difference of a position or
momentum component; pairs with identical bits sit in the band at the left.

Usage: plot_kick_demo.py --out FIG.png label=ANALYTIC_DIR,MESH_DIR [label=...]
(one entry per build; each directory is the working directory of run_kick_demo.py)
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, HERE)
from nrpic import figstyle  # noqa: E402
from run_kick_demo import read_snapshot  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PAIRS = [
    ("analytic", "a1", "a2", 2, "key tag: 1 and 64 MeshBlocks"),
    ("analytic", "a1", "a3", 2, "key tag: restart"),
    ("analytic", "n1", "n2", 2, "direction kick: 1 and 64 MeshBlocks"),
    ("analytic", "n1", "n3", 2, "direction kick: restart"),
    ("mesh", "m5", "m6", 1, "mesh metric, removal: restart"),
    ("mesh", "m1", "m2", 2, "mesh metric, kick: 8 and 64 MeshBlocks"),
    ("mesh", "m3", "m4", 2, "mesh metric, no kick: 8 and 64 MeshBlocks"),
    ("analytic", "b1", "b2", 2, "control, key block: 1 and 64 MeshBlocks"),
    ("analytic", "s1", "s3", 2, "control, key sequence: restart"),
    ("analytic", "a1", "d1", 2, "another seed"),
]
ZERO = -19.0          # position of exact zeros on the logarithmic axis


def pair_diff(da, db, snap):
    _, _, ta, xa = read_snapshot(os.path.join(da, f"kick.part.{snap:05d}.bin"))
    _, _, tb, xb = read_snapshot(os.path.join(db, f"kick.part.{snap:05d}.bin"))
    if not np.array_equal(ta, tb):
        _, ia, ib = np.intersect1d(ta, tb, return_indices=True)
        xa, xb = xa[ia], xb[ib]
    return np.abs(xa[:, :6] - xb[:, :6]).max(axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("builds", nargs="+")
    args = ap.parse_args()
    figstyle.use_style()
    cols = [figstyle.PAL["blue"], figstyle.PAL["red"], figstyle.PAL["green"]]
    builds = []
    for item in args.builds:
        label, dirs = item.split("=", 1)
        d_an, d_me = dirs.split(",")
        builds.append((label, {"analytic": d_an, "mesh": d_me}))

    fig, ax = plt.subplots(1, 2, figsize=(8.0, 4.2),
                           gridspec_kw={"width_ratios": [1.0, 1.55]})
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.13, top=0.96, wspace=0.95)

    # left: the accumulated kick
    for (label, dirs), c in zip(builds, cols):
        summ = json.load(open(os.path.join(dirs["analytic"], "summary.json")))
        _, _, _, x0 = read_snapshot(os.path.join(dirs["analytic"], "a0",
                                                 "kick.part.00002.bin"))
        _, _, _, x1 = read_snapshot(os.path.join(dirs["analytic"], "a1",
                                                 "kick.part.00002.bin"))
        sig = summ["kick_expected_rms"]
        du = (x1[:, 3] - x0[:, 3]) / sig
        h, e = np.histogram(du, bins=np.linspace(-5, 5, 51), density=True)
        ax[0].step(0.5 * (e[1:] + e[:-1]), h, where="mid", color=c, lw=1.2,
                   label=f"{label}")
    xx = np.linspace(-5, 5, 400)
    ax[0].plot(xx, np.exp(-0.5 * xx * xx) / np.sqrt(2 * np.pi), label="normal",
               **figstyle.GUIDE)
    ax[0].set_xlim(-5, 5)
    ax[0].set_ylim(0, 0.62)
    ax[0].set_xlabel(r"$(u_x^{\rm kick} - u_x^{\rm no\ kick})\,/\,\sigma\sqrt{t}$")
    ax[0].set_ylabel("probability density")
    ax[0].legend(loc="upper left")

    # right: differences between pairs of runs
    ny = len(PAIRS)
    ax[1].axvspan(ZERO - 1.0, ZERO + 1.0, color="grey", alpha=0.15, lw=0)
    for row, (case, ra, rb, snap, text) in enumerate(PAIRS):
        y0 = ny - 1 - row
        for ib, ((label, dirs), c) in enumerate(zip(builds, cols)):
            d = pair_diff(os.path.join(dirs[case], ra), os.path.join(dirs[case], rb),
                          snap)
            y = y0 + 0.18 * (0.5 * (len(builds) - 1) - ib)
            nz = d[d > 0]
            if nz.size == 0:
                ax[1].plot([ZERO], [y], "o", ms=5, color=c)
            else:
                lo, med, hi = np.log10(np.percentile(nz, [0, 50, 100]))
                ax[1].plot([lo, hi], [y, y], "-", color=c, lw=1.5)
                ax[1].plot([med], [y], "o", ms=5, color=c)
                if nz.size < d.size:
                    ax[1].plot([ZERO], [y], "o", ms=3, color=c, mfc="none")
    ax[1].set_yticks(range(ny))
    ax[1].set_yticklabels([p[4] for p in PAIRS][::-1])
    ax[1].tick_params(axis="y", which="minor", left=False, right=False)
    ax[1].set_ylim(-0.6, ny - 0.4)
    ax[1].set_xlim(ZERO - 1.0, 0.5)
    ticks = [ZERO, -16, -12, -8, -4, 0]
    ax[1].set_xticks(ticks)
    ax[1].set_xticklabels(["0"] + [f"$10^{{{t}}}$" for t in ticks[1:]])
    ax[1].tick_params(axis="x", which="minor", bottom=False, top=False)
    ax[1].set_xlabel("largest difference of a particle between the two runs")
    for (label, _), c in zip(builds, cols):
        ax[1].plot([], [], "o-", color=c, label=label)
    ax[1].legend(loc="lower right")
    fig.savefig(args.out, dpi=200)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
