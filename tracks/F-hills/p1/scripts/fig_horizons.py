#!/usr/bin/env python3
"""Figure: apparent-horizon masses of P1 against t, read only from searches that found a
horizon with hrms < 1e-3 (members from t = 0.5 M, the heavy hole from 4 M; HANDOFF, Traps;
nrread.read_horizon drops the repeated rows of failed searches).

Top: members, M_AH / M_AH(first good) - 1, with the P1 prediction item 3 band (10-18 percent
by t = 200 M, i.e. linear 0.6-1.1e-4 per member mass) as grey lines; bottom: the heavy hole,
same quantity; right axis: hrms of all found searches (small dots). Writes
<out>/fig_horizons.{pdf,png}.
Usage: fig_horizons.py [--out=<dir>] [--rundir=<dir>]
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
    good = p1lib.horizons_good(rd)
    raw = p1lib.nr.read_horizons(rd)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.90, bottom=0.09, top=0.95, hspace=0.06)
    col = {0: fs.PAL["blue"], 1: fs.PAL["red"], 2: "k"}
    lab = {0: r"$m_1$ (finder 0)", 1: r"$m_2$ (finder 1)", 2: r"$M$ (finder 2)"}
    tmax = 0.0
    for n, ax in ((0, axs[0]), (1, axs[0]), (2, axs[1])):
        if n not in good or not len(good[n]["t"]):
            continue
        h = good[n]
        m0 = h["mass"][0]
        ax.plot(h["t"], h["mass"] / m0 - 1, ".", ms=2.5, color=col[n],
                label=f"{lab[n]}: first good {m0:.5f} at t = {h['t'][0]:.2f}; "
                      f"{h['good']} good of {h['found']} found, {h['missed']} missed")
        tmax = max(tmax, float(h["t"][-1]))
    tt = np.linspace(0, max(tmax, 1.0), 50)
    mm = 0.1295                                   # member horizon mass of the smoke (E7)
    for r in (0.6e-4, 1.1e-4):
        axs[0].plot(tt, r * tt / mm, **fs.MASK_LINE)
    axs[0].text(0.6 * tmax, 1.1e-4 * 0.6 * tmax / mm, "prediction band\n(0.6-1.1e-4 per m)",
                fontsize=7, color="grey", va="bottom")
    axs[0].set_ylabel(r"$M_{\rm AH}/M_{\rm AH,first}-1$, members")
    axs[1].set_ylabel(r"$M_{\rm AH}/M_{\rm AH,first}-1$, heavy hole")
    for n, ax in ((0, axs[0]), (1, axs[0]), (2, axs[1])):
        if n in raw and len(raw[n][0]["t"]):
            a2 = ax.twinx() if not hasattr(ax, "_hr") else ax._hr
            ax._hr = a2
            a2.semilogy(raw[n][0]["t"], raw[n][0]["hrms"], ",", color=col[n], alpha=0.35)
            a2.axhline(p1lib.HRMS_MAX, color=col[n], lw=0.6, ls="--", alpha=0.4)
            a2.set_ylabel("hrms (dots), cut 1e-3 (dashed)", fontsize=8)
    for ax in axs:
        ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    axs[1].set_xlabel(r"$t\ [M]$")
    for p in fs.save(fig, os.path.join(out, "fig_horizons")):
        print("figure:", p)


if __name__ == "__main__":
    main()
