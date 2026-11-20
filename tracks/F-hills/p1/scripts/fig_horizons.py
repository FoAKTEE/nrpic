#!/usr/bin/env python3
"""Figure: apparent-horizon masses of P1 against t, read only from searches that found a
horizon with hrms < 1e-3 (members from t = 0.5 M, the heavy hole from 4 M; HANDOFF, Traps;
nrread.read_horizon drops the repeated rows of failed searches).

Top: member finders 0 and 1 while they find separate horizons (mass below 0.2):
M_AH / M_AH(first good) - 1, with the P1 prediction item 3 rate (0.6-1.1e-4 per member mass
0.1295, grey lines). Middle: the mass the member finders find from the common horizon on
(mass above 0.2). Bottom: the heavy hole (finder 2), M_AH / M_AH(first good) - 1. Small grey
dots on the right axes: hrms of every search that found a surface; dashed: the 1e-3 cut.
Writes <out>/fig_horizons.{pdf,png}.
Usage: fig_horizons.py [--out=<dir>] [--rundir=<dir>]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402
import figstyle as fs  # noqa: E402

SPLIT = 0.2      # member finders: below = one member, above = common horizon of the binary


def hrms_axis(ax, h, color):
    a2 = ax.twinx()
    a2.semilogy(h["t"], h["hrms"], ".", ms=0.8, color=color, alpha=0.25)
    a2.axhline(p1lib.HRMS_MAX, color="grey", lw=0.8, ls="--")
    a2.set_ylim(1e-8, 1e2)
    a2.set_ylabel("hrms", fontsize=8)
    return a2


def main():
    out = p1lib.out_dir(sys.argv)
    rd = p1lib.rundir(sys.argv)
    good = p1lib.horizons_good(rd)
    raw = p1lib.nr.read_horizons(rd)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 1, figsize=(fs.FULL_WIDTH, 7.0), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.90, bottom=0.07, top=0.97, hspace=0.07)
    col = {0: fs.PAL["blue"], 1: fs.PAL["red"], 2: "k"}
    lab = {0: r"$m_1$ (finder 0)", 1: r"$m_2$ (finder 1)", 2: r"$M$ (finder 2)"}
    tmax = max(float(g["t"][-1]) for g in good.values() if len(g["t"]))
    for n in (0, 1):
        h = good.get(n)
        if not h or not len(h["t"]):
            continue
        m0 = h["mass"][0]
        one = h["mass"] < SPLIT
        axs[0].plot(h["t"][one], h["mass"][one] / m0 - 1, ".", ms=2.5, color=col[n],
                    label=f"{lab[n]}: first good {m0:.5f} at t = {h['t'][0]:.2f}, "
                          f"last single {h['mass'][one][-1]:.5f} at t = {h['t'][one][-1]:.2f}")
        if (~one).any():
            axs[1].plot(h["t"][~one], h["mass"][~one], ".", ms=2.5, color=col[n],
                        label=f"{lab[n]}: common horizon from t = {h['t'][~one][0]:.2f}, "
                              f"median {np.median(h['mass'][~one]):.5f}")
        hrms_axis(axs[0] if n == 0 else axs[1], raw[n][0], col[n])
    tt = np.linspace(0, tmax, 50)
    for r in (0.6e-4, 1.1e-4):
        axs[0].plot(tt, r * tt / 0.1295, **fs.MASK_LINE)
    axs[0].text(0.55 * tmax, 1.1e-4 * 0.55 * tmax / 0.1295 + 0.004,
                "P1 prediction item 3 rate", fontsize=7, color="grey")
    axs[0].set_ylim(-0.01, 0.12)
    axs[0].set_ylabel(r"$M_{\rm AH}/M_{\rm AH,first}-1$")
    axs[1].set_ylabel(r"$M_{\rm AH}$ (binary)")
    h = good.get(2)
    if h and len(h["t"]):
        m0 = h["mass"][0]
        axs[2].plot(h["t"], h["mass"] / m0 - 1, ".", ms=2.0, color=col[2],
                    label=f"{lab[2]}: first good {m0:.5f} at t = {h['t'][0]:.2f}; "
                          f"{h['good']} good of {h['found']} found, {h['missed']} missed")
        hrms_axis(axs[2], raw[2][0], "k")
    axs[2].set_ylim(-0.0005, 0.006)
    axs[2].set_ylabel(r"$M_{\rm AH}/M_{\rm AH,first}-1$")
    for ax in axs:
        ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    axs[2].set_xlabel(r"$t\ [M]$")
    for p in fs.save(fig, os.path.join(out, "fig_horizons")):
        print("figure:", p)


if __name__ == "__main__":
    main()
