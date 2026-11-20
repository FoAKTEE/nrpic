#!/usr/bin/env python3
"""Figure: tracks of the two members in the orbital plane, relative to the heavy hole, P1
(trackers, segments joined) against the full-Newton and HRNA baselines over the same times.

P1: coordinate positions of the trackers (moving-puncture gauge), x_i - x_M. Newton: full
three-body problem, x_i - x_M. HRNA: hole fixed at the origin, Schwarzschild coordinates.
Left: the whole approach; right: the inner 16 M. Dots every 20 M, with the time written at
P1's dots. Writes <out>/fig_tracks_plane.{pdf,png}.
Usage: fig_tracks_plane.py [--out=<dir>] [--rundir=<dir>] [--baselines-npz=<file>]
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
    t_end = float(t[-1])
    tn = b["newton_t"]
    kn = tn <= t_end
    Xn = b["newton_X"][kn]
    th = b["hrna_t"]
    kh = th <= t_end
    Yh = b["hrna_y"][kh]
    rel = {0: X[:, 0] - X[:, 2], 1: X[:, 1] - X[:, 2]}
    reln = {0: Xn[:, 0] - Xn[:, 2], 1: Xn[:, 1] - Xn[:, 2]}
    relh = {0: Yh[:, 0:3], 1: Yh[:, 6:9]}
    col = {0: fs.PAL["blue"], 1: fs.PAL["red"]}
    name = {0: r"$m_1$", 1: r"$m_2$"}

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 4.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.12, top=0.90, wspace=0.22)
    marks = np.arange(0.0, t_end + 1e-9, 20.0)
    for ax, half in zip(axs, (36.0, 16.0)):
        for k in (0, 1):
            ax.plot(rel[k][:, 0], rel[k][:, 1], color=col[k], lw=1.5,
                    label=f"{name[k]} P1 (NR)" if ax is axs[0] else None)
            ax.plot(reln[k][:, 0], reln[k][:, 1], color=col[k], lw=1.0, ls="--",
                    label=f"{name[k]} Newton" if ax is axs[0] else None)
            ax.plot(relh[k][:, 0], relh[k][:, 1], color=col[k], lw=1.0, ls=":",
                    label=f"{name[k]} HRNA" if ax is axs[0] else None)
            for tm in marks:
                i = np.searchsorted(t, tm)
                if i < len(t):
                    ax.plot(rel[k][i, 0], rel[k][i, 1], "o", ms=2.5, color=col[k])
                    if k == 0 and abs(rel[k][i, 0]) < half and abs(rel[k][i, 1]) < half:
                        ax.annotate(f"{tm:.0f}", (rel[k][i, 0], rel[k][i, 1]), fontsize=6,
                                    xytext=(3, 3), textcoords="offset points")
                i = np.searchsorted(tn[kn], tm)
                if i < kn.sum():
                    ax.plot(reln[k][i, 0], reln[k][i, 1], "o", ms=2.5, mfc="none", color=col[k])
                i = np.searchsorted(th[kh], tm)
                if i < kh.sum():
                    ax.plot(relh[k][i, 0], relh[k][i, 1], "s", ms=2.5, mfc="none", color=col[k])
            # end points
            ax.plot(rel[k][-1, 0], rel[k][-1, 1], "*", ms=7, color=col[k])
        ax.plot(0, 0, "k+", ms=8)
        ax.set_xlim(-half, half)
        ax.set_ylim(-half, half)
        ax.set_aspect("equal")
        ax.set_xlabel(r"$x - x_M\ [M]$")
        ax.set_ylabel(r"$y - y_M\ [M]$")
    axs[0].set_title(f"P1 to t = {t_end:.1f} M, baselines to the same time", fontsize=9)
    axs[1].set_title("inner region (stars: last P1 point)", fontsize=9)
    axs[0].legend(frameon=False, fontsize=7, loc="lower right", ncol=2)
    for p in fs.save(fig, os.path.join(out, "fig_tracks_plane")):
        print("figure:", p)


if __name__ == "__main__":
    main()
