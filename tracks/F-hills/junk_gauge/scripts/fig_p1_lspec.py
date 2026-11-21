#!/usr/bin/env python3
"""Figure of J4c: P1's J4b window by multipole and frequency. Left: E_l against l at the four
spheres (log scale). Right: share of the window's energy spectrum per frequency band at the four
spheres (all modes: bars; l = 2 alone: open markers). Reads p1_lspec.json.
Usage: fig_p1_lspec.py <dir | ->
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def main():
    d = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    res = json.load(open(os.path.join(d, "p1_lspec.json")))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    radii = sorted(res["radii"], key=int)
    for i, R in enumerate(radii):
        r = res["radii"][R]
        ls = sorted(r["E_l"], key=int)
        ax[0].semilogy([int(l) for l in ls], [r["E_l"][l] for l in ls], "o-", ms=3, lw=1.0,
                       color=fs.SERIES[i % len(fs.SERIES)], label=f"R = {R} M")
        keys = list(r["band_share_all"])
        x = np.arange(len(keys)) + (i - 1.5) * 0.18
        ax[1].bar(x, [r["band_share_all"][k] for k in keys], width=0.17,
                  color=fs.SERIES[i % len(fs.SERIES)], label=f"R = {R} M")
        ax[1].plot(x, [r["band_share_l2"][k] for k in keys], "o", mfc="none", ms=4,
                   color="k")
    ax[0].set_xlabel(r"$l$")
    ax[0].set_ylabel(r"$E_l$ in $u\in[-35,6]$ [$M$]")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].set_xticks(np.arange(len(keys)))
    ax[1].set_xticklabels([k.replace("1e+09", "") for k in keys])
    ax[1].set_xlabel(r"band of $|\omega|$ [$M^{-1}$] (open: $l = 2$ only)")
    ax[1].set_ylabel("share of the window's spectrum")
    ax[1].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(d, "fig_p1_lspec")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
