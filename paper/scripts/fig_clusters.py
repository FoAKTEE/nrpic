"""The sequence of five relativistic star clusters of 10^4 particles, from the least
compact model (left) to the unbound one (right), each with the one-percent inward kick.

Top row: coordinate radii about the origin enclosing 10, 20, ..., 90 percent of the
rest mass (half mass drawn thicker), from the particle snapshots; once particles are
removed the percentiles refer to the rest mass that remains, and the radii are drawn
while at least half of it remains. Middle row: central lapse; black dotted: lapse
threshold of particle removal. Black dashed (top and middle rows): first apparent
horizon. Bottom row, for the two models that collapse only: apparent-horizon mass
against time about the collapse, with the total mass (blue). One colour per model; the
two models that collapse in the two reds. The bottom-left cell holds the key.

Reads paper/data/clusters.npz, written by make_data_clusters.py.

    python3 paper/scripts/fig_clusters.py
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

DATA = HERE.parent / "data" / "clusters.npz"
OUT = HERE.parent / "figures" / "fig_clusters"
LEG_PT = 9
BLUE = fs.PAL["blue"]
ORDER = ("y0900", "y0819", "y0605", "y0500", "y0283")
COL = {"y0900": fs.PAL["green"], "y0819": fs.PAL["yellow"], "y0605": fs.PAL["red"],
       "y0500": fs.PAL2["red"], "y0283": fs.PAL["orange"]}
XLIM = {"y0900": (0, 300), "y0819": (0, 300), "y0605": (0, 300), "y0500": (0, 120),
        "y0283": (0, 270)}
XTICKS = {"y0900": (0, 100, 200), "y0819": (0, 100, 200), "y0605": (0, 100, 200),
          "y0500": (0, 50, 100), "y0283": (0, 100, 200)}
AH_XLIM = {"y0605": (186, 236), "y0500": (102, 120)}
AH_XTICKS = {"y0605": (190, 210, 230), "y0500": (105, 110, 115)}
OUTCOME = {"y0900": "holds", "y0819": "holds", "y0605": "black hole",
           "y0500": "black hole", "y0283": "disperses"}
MIN_LEFT = 0.5           # radii drawn while this fraction of the rest mass remains
LW_HALF, LW_SHELL = 1.8, 0.8
DASH = (0, (4.0, 1.8))
THIN = dict(color="k", lw=1.0)
LEG = dict(fontsize=LEG_PT, handlelength=2.2, borderaxespad=0.2, labelspacing=0.35)


def radii(ax, d, k):
    T, R, m = d[f"{k}_snap_t"], d[f"{k}_r"], d[f"{k}_snap_m"]
    w = m >= MIN_LEFT * m[0]
    for j, q in enumerate(d["qs"]):
        half = abs(q - 0.5) < 1e-9
        ax.plot(T[w], R[w, j], color=COL[k], lw=LW_HALF if half else LW_SHELL,
                zorder=3 if half else 2)
    ax.set_yscale("log")
    ax.set_ylim(0.08, 400)
    ax.text(0.05, 0.95, OUTCOME[k], transform=ax.transAxes, ha="left", va="top",
            fontsize=LEG_PT)


def lapse(ax, d, k):
    ax.axhline(float(d[f"{k}_alpha_exc"]), ls=":", zorder=1, **THIN)
    ax.plot(d[f"{k}_t"], d[f"{k}_alpha"], color=COL[k], lw=1.5, zorder=3)
    ax.set_ylim(0, 1.05)
    ax.set_yticks((0, 0.5, 1))


def horizon(ax, d, k):
    ax.axhline(1.0, color=BLUE, lw=1.5, zorder=1)
    ax.plot(d[f"{k}_ah_t"], d[f"{k}_ah_M"], color=COL[k], lw=1.5, zorder=3)
    ax.set_xlim(*AH_XLIM[k])
    ax.set_xticks(AH_XTICKS[k])
    ax.set_ylim(0.75, 1.03)
    ax.set_yticks((0.8, 0.9, 1.0))
    ax.set_xlabel(r"$t/M$", labelpad=1)


def key(ax):
    ax.set_axis_off()
    h = [Line2D([], [], color="k", lw=LW_HALF), Line2D([], [], color="k", lw=LW_SHELL),
         Line2D([], [], ls=":", **THIN), Line2D([], [], ls=DASH, **THIN),
         Line2D([], [], color=BLUE, lw=1.5)]
    lab = ["half-mass radius", "radii of 10, 20, ..., 90 %", "lapse threshold of removal",
           "first apparent horizon", "total mass"]
    ax.legend(h, lab, loc="upper left", frameon=False, borderpad=0, **LEG)


def make():
    fs.use_style()
    d = np.load(DATA)
    W, Hfig = fs.FULL_WIDTH, 5.05
    fig = plt.figure(figsize=(W, Hfig))
    left, right, gap_x = 0.62, 0.10, 0.16
    bot, h_ah, gap_ah, h_low, gap_y, h_top, top = 0.40, 0.95, 0.47, 1.25, 0.10, 1.55, 0.30
    w = (W - left - right - 4 * gap_x) / 5
    y_low = bot + h_ah + gap_ah
    y_top = y_low + h_low + gap_y
    for i, k in enumerate(ORDER):
        x0 = left + i * (w + gap_x)
        a_r = fs.inch_axes(fig, x0, y_top, w, h_top)
        a_l = fs.inch_axes(fig, x0, y_low, w, h_low)
        radii(a_r, d, k)
        lapse(a_l, d, k)
        if len(d[f"{k}_ah_t"]):
            for ax in (a_r, a_l):
                ax.axvline(d[f"{k}_ah_t"][0], ls=DASH, zorder=1, **THIN)
            a_h = fs.inch_axes(fig, x0, bot, w, h_ah)
            horizon(a_h, d, k)
            if k == "y0605":
                a_h.set_ylabel(r"$M_{\rm AH}/M$")
            else:
                a_h.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
        for ax in (a_r, a_l):
            ax.set_xlim(*XLIM[k])
            ax.set_xticks(XTICKS[k])
        a_r.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
        a_r.set_title(rf"$y_c = {float(d[f'{k}_yc']):.3f}$", fontsize=10, pad=4)
        a_l.set_xlabel(r"$t/M$", labelpad=1)
        if i == 0:
            a_r.set_ylabel(r"$r/M$")
            a_l.set_ylabel(r"$\alpha_c$")
            for ax in (a_r, a_l):
                ax.yaxis.set_label_coords(-0.30, 0.5)
        else:
            for ax in (a_r, a_l):
                ax.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
        a_r.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    key(fs.inch_axes(fig, left, bot, 2 * w + gap_x - 0.6, h_ah))
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
