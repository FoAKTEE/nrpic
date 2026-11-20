#!/usr/bin/env python3
"""Figure: the mesh and the speed of P1 segment by segment, from the chain logs and the
restart headers.

Top: MeshBlocks against t: restart files (header nmb_total, dots), segment starts ("Total
number of MeshBlocks") and ends ("Current number of MeshBlocks"); grey band: the P1 prediction
1716-2400; dashed: the 2700 slots. Bottom: MeshBlock-cycles per second of each finished
segment (AthenaK's "MeshBlock-cycles" / "cpu time used"), with the predicted 1900-2200 band,
and on the right axis the time advanced per 50 minutes of athena (from the elapsed= lines).
Writes <out>/fig_segments.{pdf,png}.
Usage: fig_segments.py [--out=<dir>] [--rundir=<dir>]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402
import figstyle as fs  # noqa: E402

DT = 3.90625e-3


def main():
    out = p1lib.out_dir(sys.argv)
    rd = p1lib.rundir(sys.argv)
    segs = p1lib.segment_logs(rd)
    rst = p1lib.restart_headers(rd)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.89, bottom=0.09, top=0.95, hspace=0.06)
    ax = axs[0]
    ax.axhspan(1716, 2400, color="grey", alpha=0.15, lw=0)
    ax.text(2, 2420, "P1 prediction 1716-2400", fontsize=7, color="grey")
    ax.axhline(2700, **fs.GUIDE)
    ax.text(2, 2720, "2700 slots", fontsize=7)
    ax.plot([r["time"] for r in rst], [r["nmb"] for r in rst], "o", ms=3.5,
            color=fs.PAL["blue"], label="restart files (header)")
    for i, s in enumerate(segs):
        if s.get("t_first") is None:
            continue
        ax.plot([s["t_first"]], [s["nmb_start"]], ">", ms=5, color=fs.PAL["red"],
                label="segment start" if i == 0 else None)
        if s.get("nmb_end"):
            ax.plot([s["t_last"]], [s["nmb_end"]], "<", ms=5, color=fs.PAL["yellow"],
                    label="segment end" if i == 0 else None)
        ax.axvspan(s["t_first"], s["t_last"], color=fs.SERIES[i % 2], alpha=0.05, lw=0)
        ax.text(0.5 * (s["t_first"] + s["t_last"]), 950, f"{s['seg']}\n{s['job']}",
                fontsize=6, ha="center")
    ax.set_ylim(900, 2900)
    ax.set_ylabel("MeshBlocks")
    ax.legend(frameon=False, fontsize=7, loc="upper right")
    ax = axs[1]
    ax.axhspan(1900, 2200, color="grey", alpha=0.15, lw=0)
    a2 = ax.twinx()
    for i, s in enumerate(segs):
        if s.get("t_first") is None:
            continue
        if s.get("mbc_per_s"):
            ax.plot([s["t_first"], s["t_last"]], [s["mbc_per_s"]] * 2, color=fs.PAL["red"],
                    lw=2.0, label="MeshBlock-cycles / s (finished segments)" if i == 0 else None)
        if s.get("cycles_per_s"):
            adv = s["cycles_per_s"] * 3000.0 * DT
            a2.plot([s["t_first"], s["t_last"]], [adv] * 2, color=fs.PAL["blue"], lw=1.2,
                    ls="--", label="M per 50 min (right)" if i == 0 else None)
    a2.axhspan(15, 21, color=fs.PAL["blue"], alpha=0.06, lw=0)
    a2.set_ylim(10, 24)
    a2.set_ylabel(r"advance per 50 min $[M]$")
    ax.set_ylim(1700, 2400)
    ax.set_ylabel("MeshBlock-cycles per second")
    ax.set_xlabel(r"$t\ [M]$")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = a2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=7, loc="upper left")
    ax.set_xlim(0, max(s.get("t_last", 0) for s in segs) + 5)
    for p in fs.save(fig, os.path.join(out, "fig_segments")):
        print("figure:", p)


if __name__ == "__main__":
    main()
