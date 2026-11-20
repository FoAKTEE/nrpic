#!/usr/bin/env python3
"""Figure: tracks of the two members in the orbital plane, relative to the heavy hole, P1
(trackers, segments joined) against the full-Newton and HRNA baselines over the same times.

P1: coordinate positions of the trackers (moving-puncture gauge), x_i - x_M. Newton: full
three-body problem, x_i - x_M. HRNA: hole fixed at the origin, Schwarzschild coordinates.
Left: the whole approach; middle: the inner 16 M. Dots every 20 M, with the time written at
P1's dots. Right: the binary's relative orbit x_1 - x_2 over t = 0-60 M (P1, Newton, HRNA),
dots every 10 M. Writes <out>/fig_tracks_plane.{pdf,png}.
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
    fig, axs3 = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.14, top=0.90, wspace=0.32)
    axs = axs3[:2]
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
    axs[0].legend(frameon=False, fontsize=6, loc="upper left", ncol=2)
    # binary's relative orbit
    ax = axs3[2]
    t_rel = 60.0
    for tt, d, ls, lab in ((t, X[:, 0] - X[:, 1], "-", "P1 (NR)"),
                           (tn, b["newton_X"][:, 0] - b["newton_X"][:, 1], "--", "Newton"),
                           (th, b["hrna_y"][:, 0:3] - b["hrna_y"][:, 6:9], ":", "HRNA")):
        k = tt <= t_rel
        ax.plot(d[k, 0], d[k, 1], color=fs.PAL["yellow"] if ls == "-" else "k", ls=ls,
                lw=1.5 if ls == "-" else 1.0, label=lab)
        for tm in np.arange(0.0, t_rel + 1e-9, 10.0):
            i = np.searchsorted(tt, tm)
            if i < len(tt) and tt[i] - tm < 2.0:
                ax.plot(d[i, 0], d[i, 1], "o", ms=2.5, mfc="none" if ls != "-" else None,
                        color=fs.PAL["yellow"] if ls == "-" else "k")
                if ls == "-":
                    ax.annotate(f"{tm:.0f}", (d[i, 0], d[i, 1]), fontsize=6,
                                xytext=(3, -8), textcoords="offset points")
    ax.plot(0, 0, "k+", ms=6)
    ax.set_xlim(-8, 8)
    ax.set_ylim(-8, 8)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x_1 - x_2\ [M]$")
    ax.set_ylabel(r"$y_1 - y_2\ [M]$")
    ax.set_title(f"binary, t = 0-{t_rel:.0f} M", fontsize=9)
    ax.legend(frameon=False, fontsize=6, loc="upper left")
    for p in fs.save(fig, os.path.join(out, "fig_tracks_plane")):
        print("figure:", p)


if __name__ == "__main__":
    main()
