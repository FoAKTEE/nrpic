"""Migration of the unperturbed monoenergetic cluster y_c = 0.5, past the binding-energy
maximum, with 10^4 particles: it expands, recontracts and settles into an oscillation
about a more extended state, with no collapse.

Top: central lapse (red) against time; black: the central lapse of the equilibrium
model; blue open circles: the extrema of the central lapse read from the migration
figure of the original paper, with bars over the time and lapse ranges in which they
were read (the first maximum is a plateau). Bottom: coordinate radii about the origin
enclosing 90 (dashed), 50 (solid) and 10 (dotted) percent of the rest mass, from the
particle snapshots.

Reads paper/data/migration.npz, written by make_data_migration.py.

    python3 paper/scripts/fig_migration.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figstyle as fs

DATA = HERE.parent / "data" / "migration.npz"
OUT = HERE.parent / "figures" / "fig_migration"
W = 3.4                  # one column of the two-column journal page, in inches
LAB_PT = 9
RED, BLUE = fs.PAL["red"], fs.PAL["blue"]
DASH = (0, (4.0, 1.8))
RADII = ((8, "90%", DASH), (4, "50%", "-"), (0, "10%", ":"))   # column, label, style


def lapse(ax, d):
    ax.axhline(float(d["alpha_eq"]), zorder=1, **fs.THIN)
    ax.plot(d["t"], d["alpha"], color=RED, lw=1.0, zorder=2)
    o = d["original"]
    ax.errorbar(o[:, 0], o[:, 3], xerr=[o[:, 0] - o[:, 1], o[:, 2] - o[:, 0]],
                yerr=[o[:, 3] - o[:, 4], o[:, 5] - o[:, 3]], fmt="o", ms=4.5,
                mfc="white", mec=BLUE, mew=1.2, ecolor=BLUE, elinewidth=1.2, capsize=0,
                zorder=4)
    ax.set_ylim(0.5, 0.96)
    ax.set_yticks((0.5, 0.6, 0.7, 0.8, 0.9))
    ax.set_ylabel(r"$\alpha_c$")
    t_end = float(d["t_end"])
    ax.text(0.98 * t_end, float(d["alpha_eq"]) + 0.008, "equilibrium", ha="right",
            va="bottom", fontsize=LAB_PT)
    ax.text(870, 0.715, "original\n(read from figure)", color=BLUE, ha="left",
            va="top", fontsize=LAB_PT, linespacing=1.1)
    ax.text(0.98 * t_end, 0.94, r"$N = 10^4$", color=RED, ha="right", va="top",
            fontsize=LAB_PT)
    ax.text(0.03, 0.95, r"$y_c = 0.5$", transform=ax.transAxes, ha="left", va="top")


def radii(ax, d):
    T, R = d["snap_t"], d["r"]
    t_lab = 0.93 * float(d["t_end"])
    for j, lab, ls in RADII:
        ax.plot(T, R[:, j], color=RED, ls=ls, lw=1.2)
        w = np.abs(T - t_lab) <= 60
        ax.text(t_lab, 1.22 * R[w, j].max(), lab, color=RED, ha="center", va="bottom",
                fontsize=LAB_PT)
    ax.set_yscale("log")
    ax.set_ylim(0.8, 60)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    fs.no_minor_labels(ax)
    ax.set_ylabel(r"$r/M$")
    ax.set_xlabel(r"$t/M$", labelpad=1)


def make():
    fs.use_style()
    d = np.load(DATA)
    Hfig = 3.9
    fig = plt.figure(figsize=(W, Hfig))
    left, right, bot, top, gap = 0.56, 0.08, 0.42, 0.06, 0.06
    h = (Hfig - bot - top - gap) / 2
    a_r = fs.inch_axes(fig, left, bot, W - left - right, h)
    a_l = fs.inch_axes(fig, left, bot + h + gap, W - left - right, h)
    lapse(a_l, d)
    radii(a_r, d)
    t_end = float(d["t_end"])
    for ax in (a_l, a_r):
        ax.set_xlim(0, t_end)
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))
        ax.yaxis.set_label_coords(-0.42 / (W - left - right), 0.5)
    a_l.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
