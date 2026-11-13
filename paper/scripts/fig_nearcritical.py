"""The near-critical monoenergetic cluster y_c = 0.756 with 10^4 particles: a homologous
ten-percent change of the density decides the outcome by its sign. Compression collapses
to a black hole; expansion, and the unperturbed model, oscillate and keep every particle.

Top: central lapse against time for the density raised by ten percent (red, solid),
lowered by ten percent (green, dashed) and unperturbed (orange, dotted); black: central
lapse of the equilibrium model; blue band: the range about which the central lapse of
the original paper's figure for this model oscillates, read from that figure. The
compressed run leaves the panel downwards; black dashed (both panels): its first
apparent horizon. Bottom: coordinate radii about the origin enclosing 90 and 10
percent of the rest mass, from the particle snapshots, drawn while at least half of
the rest mass remains.

Reads paper/data/nearcritical.npz, written by make_data_nearcritical.py.

    python3 paper/scripts/fig_nearcritical.py
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
from matplotlib.patches import Patch

import figstyle as fs

DATA = HERE.parent / "data" / "nearcritical.npz"
OUT = HERE.parent / "figures" / "fig_nearcritical"
W = 3.4                  # one column of the two-column journal page, in inches
LAB_PT = 9
BLUE = fs.PAL["blue"]
DASH = (0, (4.0, 1.8))
DOT = (0, (1.0, 1.5))
RUN = {   # key: label, colour, line style, line width
    "plus": ("density +10%", fs.PAL["red"], "-", 1.2),
    "minus": ("density −10%", fs.PAL["green"], DASH, 1.2),
    "unpert": ("unperturbed", fs.PAL["orange"], DOT, 1.5),
}
ORDER = ("unpert", "minus", "plus")      # drawing order, last on top
MIN_LEFT = 0.5           # radii drawn while this fraction of the rest mass remains
YLIM_LAPSE = (0.52, 0.86)      # room for the key below the oscillating curves
LEG = dict(fontsize=LAB_PT, handlelength=2.2, borderaxespad=0.3, labelspacing=0.25)


def lapse(ax, d):
    o = d["original"]
    ax.plot(o[:, 0], o[:, 1], ls="none", marker="o", ms=3.2, mfc="white", mec=BLUE,
            mew=0.9, zorder=4)
    ax.axhline(float(d["alpha_eq"]), zorder=2, **fs.THIN)
    for k in ORDER:
        lab, col, ls, lw = RUN[k]
        ax.plot(d[f"{k}_t"], d[f"{k}_alpha"], color=col, ls=ls, lw=lw, zorder=3)
    ax.set_ylim(*YLIM_LAPSE)
    ax.set_yticks((0.6, 0.7, 0.8))
    ax.set_ylabel(r"$\alpha_c$")
    ax.text(0.97, 0.96, r"$y_c = 0.756$", transform=ax.transAxes, ha="right", va="top")
    keys = ("plus", "minus", "unpert")
    h = [Line2D([], [], color=RUN[k][1], ls=RUN[k][2], lw=RUN[k][3]) for k in keys]
    h += [Line2D([], [], ls="none", marker="o", ms=3.2, mfc="white", mec=BLUE, mew=0.9),
          Line2D([], [], **fs.THIN)]
    ax.legend(h, [RUN[k][0] for k in keys] + ["original, perturbed (read)", "equilibrium"],
              loc="lower right", frameon=False, **LEG)


def radii(ax, d):
    for k in ORDER:
        lab, col, ls, lw = RUN[k]
        T, R, m = d[f"{k}_snap_t"], d[f"{k}_r"], d[f"{k}_snap_m"]
        w = m >= MIN_LEFT * m[0]
        for j in (8, 0):
            ax.plot(T[w], R[w, j], color=col, ls=ls, lw=lw, zorder=3)
    ax.set_ylim(0, 10.5)
    t_lab = 0.985 * max(float(d[f"{k}_t_end"]) for k in RUN)
    ax.text(t_lab, 8.2, "90%", ha="right", va="bottom", fontsize=LAB_PT)
    ax.text(t_lab, 4.1, "10%", ha="right", va="bottom", fontsize=LAB_PT)
    ax.set_ylabel(r"$r/M$")
    ax.set_xlabel(r"$t/M$", labelpad=1)


def make():
    fs.use_style()
    d = np.load(DATA)
    Hfig = 4.5
    fig = plt.figure(figsize=(W, Hfig))
    left, right, bot, top, gap = 0.56, 0.20, 0.42, 0.08, 0.06
    h = (Hfig - bot - top - gap) * 0.42          # radii panel; the lapse panel is taller
    hl = (Hfig - bot - top - gap) - h
    a_r = fs.inch_axes(fig, left, bot, W - left - right, h)
    a_l = fs.inch_axes(fig, left, bot + h + gap, W - left - right, hl)
    lapse(a_l, d)
    radii(a_r, d)
    t_max = max(float(d[f"{k}_t_end"]) for k in RUN)
    if len(d["plus_ah_t"]):
        for ax in (a_l, a_r):
            ax.axvline(float(d["plus_ah_t"][0]), ls=DASH, zorder=2, **fs.THIN)
        a_r.text(float(d["plus_ah_t"][0]) + 12, 0.25, "apparent horizon", ha="left",
                 va="bottom", fontsize=LAB_PT)
    for ax in (a_l, a_r):
        ax.set_xlim(0, t_max)
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(200))
        ax.yaxis.set_label_coords(-0.42 / (W - left - right), 0.5)
    a_l.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
