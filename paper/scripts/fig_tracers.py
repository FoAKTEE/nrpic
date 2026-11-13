"""Test particles around a puncture of unit mass evolved in moving-puncture gauge.

Top: areal radius against proper time for a radial infall and a plunging orbit
(red) on top of the exact Schwarzschild geodesics from the same initial data (blue
dashed). Middle: their relative difference on a log axis (solid); dotted: the plunge
against the geodesic of the Misner-Sharp mass of the evolved slice, started from the
particle's own state once that mass has settled; grey lines: crossing of R = 2M.
Bottom: the mass implied by the radial acceleration of each of four circular orbits
(red) and the Misner-Sharp mass of the slice over the shell of the orbits (black,
median with 16th-84th percentile bars), both relative to the initial mass (blue).

Reads paper/data/tracers.npz, written by make_data_tracers.py.

    python3 paper/scripts/fig_tracers.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import figstyle as fs

DATA = HERE.parent / "data" / "tracers.npz"
OUT = HERE.parent / "figures" / "fig_tracers"
LEG_PT = 9
RED, BLUE = fs.PAL["red"], fs.PAL["blue"]
SHELL = "orbit"                      # Misner-Sharp statistics over 6 M < R < 12 M
FLOOR = 1e-7


def radius(ax, d):
    for name in ("infall", "plunge"):
        ax.plot(d[f"{name}_tau"], d[f"{name}_R"], color=RED, lw=1.5)
        ax.plot(d[f"{name}_tau"], d[f"{name}_Rex"], color=BLUE, lw=1.5, ls="--")
    ax.axhline(2.0, **{**fs.MASK_LINE, "lw": 1.0})
    ax.text(3.0, 2.25, r"$R = 2M$", color="0.45", fontsize=LEG_PT, va="bottom")
    ax.text(23.0, 6.0, "radial\ninfall", fontsize=LEG_PT, ha="right", va="center",
            linespacing=1.1)
    ax.text(56.0, 6.0, "plunge", fontsize=LEG_PT, ha="left", va="center")
    ax.set_ylim(0, 14.5)
    ax.set_yticks([0, 4, 8, 12])
    ax.set_ylabel(r"$R/M$")
    ax.legend([Line2D([], [], color=RED), Line2D([], [], color=BLUE, ls="--")],
              ["numerical", "exact geodesic"], loc="upper right", fontsize=LEG_PT,
              handlelength=1.8, borderaxespad=0.3, labelspacing=0.25, frameon=False)
    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())


def residual(ax, d):
    for name in ("infall", "plunge"):
        r = np.abs(d[f"{name}_R"] / d[f"{name}_Rex"] - 1)
        ax.plot(d[f"{name}_tau"], np.maximum(r, FLOOR / 10), color=RED, lw=1.3)
        ax.axvline(float(d[f"{name}_tau_hor"]), **{**fs.MASK_LINE, "lw": 1.0})
    ax.plot(d["plunge_slice_tau"], np.maximum(np.abs(d["plunge_slice_res"]), FLOOR / 10),
            color=RED, lw=1.3, ls=":")
    ax.text(21.0, 1.1e-3, "radial infall", fontsize=LEG_PT, ha="center", va="bottom")
    ax.text(21.0, 3.0e-5, "plunge", fontsize=LEG_PT, ha="center", va="top")
    ax.set_yscale("log")
    ax.set_ylim(FLOOR, 1.0)
    ax.set_yticks(10.0 ** np.arange(-6, 0, 2))
    ax.yaxis.set_minor_locator(matplotlib.ticker.LogLocator(numticks=30))
    fs.no_minor_labels(ax)
    ax.set_ylabel(r"$|R/R_{\rm exact} - 1|$")
    ax.set_xlabel(r"$\tau/M$", labelpad=1)
    ax.legend([Line2D([], [], color=RED, lw=1.3), Line2D([], [], color=RED, lw=1.3, ls=":")],
              [r"exact, mass $M$", "exact, mass of the slice"], loc="upper left",
              fontsize=LEG_PT, handlelength=1.8, borderaxespad=0.3, labelspacing=0.25, frameon=False)


def mass(ax, d):
    ax.axhline(0.0, color=BLUE, lw=1.5, zorder=1)
    for k in range(4):
        ax.plot(d[f"circ{k}_t"], 1e3 * (d[f"circ{k}_Meff"] - 1), color=RED, lw=1.0)
    m = d[f"dump_m_{SHELL}"]
    med = 1e3 * (m[:, 0] - 1)
    err = np.abs(1e3 * (m[:, 1:3].T - 1) - med)
    ax.errorbar(d["dump_t"], med, yerr=err, fmt="s", ms=4.5, color="k", capsize=2.5,
                lw=1.2, zorder=6)
    ax.text(62.0, 0.12, r"initial mass $M$", color=BLUE, fontsize=LEG_PT, va="bottom")
    ax.set_xlim(-6, 256)
    ax.set_ylim(-1.45, 3.8)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_xlabel(r"$t/M$", labelpad=1)
    ax.set_ylabel(r"mass$/M - 1\ \ [10^{-3}]$")
    ax.legend([Line2D([], [], color=RED, lw=1.0),
               Line2D([], [], color="k", ls="none", marker="s", ms=4.5)],
              ["from circular orbits", "Misner-Sharp, slice"],
              loc="lower right", fontsize=LEG_PT, handlelength=1.8, borderaxespad=0.3,
              labelspacing=0.25, frameon=False)


def make():
    fs.use_style()
    d = np.load(DATA)
    W, Hfig = fs.COLUMN_WIDTH, 5.55
    fig = plt.figure(figsize=(W, Hfig))
    xl, w = 0.78, W - 0.78 - 0.16
    b0, hm, gap, hr, hg, hR = 0.42, 1.55, 0.52, 1.55, 0.06, 1.35
    aM = fs.inch_axes(fig, xl, b0, w, hm)
    aD = fs.inch_axes(fig, xl, b0 + hm + gap, w, hr)
    aR = fs.inch_axes(fig, xl, b0 + hm + gap + hr + hg, w, hR)
    radius(aR, d)
    residual(aD, d)
    mass(aM, d)
    tmax = 1.02 * float(d["plunge_tau"][-1])
    for ax in (aR, aD):
        ax.set_xlim(0, tmax)
    for ax in (aR, aD, aM):
        ax.yaxis.set_label_coords(-0.17, 0.5)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
