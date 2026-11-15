#!/usr/bin/env python3
"""Figure of the demonstration of the reproducible kick (run_kick_demo.py).

Left: the accumulated kick in flat space (run f1), u_i(end) - u_i(0) over sigma sqrt(t),
from the code and from the Python twin, against the normal density. Right: for every
pair of runs that is compared, the range (line) and median (dot) over the particles of
the largest difference of a position or momentum component; pairs with identical bits
sit in the band at the left (a small open circle there: some particles identical).

Usage: plot_kick_demo.py --out FIG.png label=ANALYTIC_DIR,MESH_DIR [label=...]
(one entry per build; each directory is the working directory of run_kick_demo.py)
"""
import argparse
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
    ("analytic", "n1", "n2", 2, "direction: 1 and 64 MeshBlocks"),
    ("analytic", "n1", "n3", 2, "direction: restart"),
    ("mesh", "m5", "m6", 1, "mesh metric, removal: restart"),
    ("mesh", "m1", "m2", 2, "mesh metric: 8 and 64 MeshBlocks"),
    ("mesh", "m3", "m4", 2, "same without kick"),
    ("analytic", "b1", "b2", 2, "control block: 1 and 64 MeshBlocks"),
    ("analytic", "s1", "s3", 2, "control sequence: restart"),
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

    fig = plt.figure(figsize=(8.0, 4.2))
    ax = [fig.add_axes([0.075, 0.13, 0.215, 0.83]), fig.add_axes([0.66, 0.13, 0.325, 0.83])]

    # left: the accumulated kick in flat space, code and twin
    bins = np.linspace(-5, 5, 51)
    xc = 0.5 * (bins[1:] + bins[:-1])
    for ib, ((label, dirs), c) in enumerate(zip(builds, cols)):
        kick = np.load(os.path.join(dirs["analytic"], "flat_kick_code.npy")).ravel()
        h, _ = np.histogram(kick, bins=bins, density=True)
        ax[0].step(xc, h, where="mid", color=c, lw=1.2, label=f"code, {label}")
        if ib == 0:
            twin = np.load(os.path.join(dirs["analytic"], "flat_kick_twin.npy")).ravel()
            ht, _ = np.histogram(twin, bins=bins, density=True)
            ax[0].plot(xc, ht, ".", ms=4, color="k", label="Python twin")
    xx = np.linspace(-5, 5, 400)
    ax[0].plot(xx, np.exp(-0.5 * xx * xx) / np.sqrt(2 * np.pi), label="normal",
               **figstyle.GUIDE)
    ax[0].set_xlim(-5, 5)
    ax[0].set_ylim(0, 0.62)
    ax[0].set_xlabel(r"$[u_i(t) - u_i(0)]\,/\,\sigma\sqrt{t}$, flat space")
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
    ax[1].set_xlabel("largest difference per particle")
    for (label, _), c in zip(builds, cols):
        ax[1].plot([], [], "o-", color=c, label=label)
    ax[1].legend(loc="center", bbox_to_anchor=(0.62, 0.62))
    fig.savefig(args.out, dpi=200)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
