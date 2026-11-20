#!/usr/bin/env python3
"""Figure of G2M-1 (and G2M-3): MeshBlocks against time for each resolution, 16^3 and 32^3,
along the Newtonian tracks to 280 M (solid) and P1's measured tracks to the latest tracker
time (dashed), with the slot limits of one card.

Slot limits: 2700 (P1), and the card limit of each block size, from the measured memory when
a card analysis JSON is given (G2M-3: card_analysis.json, key 'slot_limit'), else from the
predictions of G2M-2 (16^3: 25.65 MiB per slot after 70847 MiB at 2700 slots; 32^3: 119 MiB
per slot) [JUDGEMENT until measured].
Usage: fig_blocks_time.py <model.json> <outdir> [<card_analysis.json>]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

CARD_MIB = 81920.0


def main():
    d = json.load(open(sys.argv[1]))["D_tracks"]
    out = sys.argv[2]
    lim = {16: (CARD_MIB - (70847 - 2700 * 25.65)) / 25.65,
           32: (CARD_MIB - (70847 - 2700 * 25.65)) / 119.0}
    src = "predicted (G2M-2)"
    if len(sys.argv) > 3:
        ca = json.load(open(sys.argv[3]))
        lim = {int(k): v for k, v in ca["slot_limit"].items()}
        src = "measured (G2M-3)"
    os.makedirs(out, exist_ok=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4), sharex=True)
    res = [("R8", "m/8 (P1)"), ("R12", "m/12, all cells x 2/3"),
           ("R16n", "m/16, nests only"), ("R16u", "m/16, all cells x 1/2")]
    cols = dict(zip([r for r, _ in res], fs.SERIES))
    for ax, b in zip(axs, (16, 32)):
        for r, lab in res:
            v = d[f"{r}_b{b}"]
            ax.plot(v["newton"]["t"], v["newton"]["n"], "-", color=cols[r], lw=1.0,
                    label=f"{lab}: max {v['newton']['n_max']}")
            ax.plot(v["p1"]["t"], v["p1"]["n"], "--", color=cols[r], lw=0.8)
        ax.axhline(2700, **fs.MASK_LINE)
        ax.text(3, 2700 + 25, "2700 slots (P1)", fontsize=7, color="grey")
        ax.axhline(lim[b], **fs.GUIDE)
        ax.text(3, lim[b] + 25, "card limit, %s: %.0f slots" % (src, lim[b]), fontsize=7)
        ax.set_xlabel(r"$t\,[M]$")
        ax.set_title(f"{b}$^3$ MeshBlocks (solid: Newtonian tracks; dashed: P1 measured)",
                     fontsize=8)
        ax.legend(fontsize=6.5, loc="lower right")
    axs[0].set_ylabel("MeshBlocks (model)")
    axs[0].set_ylim(0, 3800)
    axs[1].set_ylim(0, 3800)
    fig.tight_layout()
    for p in fs.save(fig, os.path.join(out, "fig_blocks_time")):
        print("figure:", p)


if __name__ == "__main__":
    main()
