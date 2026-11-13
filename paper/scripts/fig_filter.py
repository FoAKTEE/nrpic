"""Smoothing filter and the motion of relativistic clusters of 10^4 particles.

Left: central lapse of the stable model y_c = 0.819 minus its equilibrium value, for
three samples (colour) with four plain binomial filter passes (solid) and with four
passes plus the compensation pass (dashed). Middle: the same model and the first
sample with zero, two and four filter passes (colour), plain (solid) and compensated
(dashed). Right: central lapse of the model y_c = 0.5 past the binding-energy maximum,
same encoding as the left panel. Black: the equilibrium.

Reads paper/data/filter.npz, written by make_data_filter.py.

    python3 paper/scripts/fig_filter.py
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

DATA = HERE.parent / "data" / "filter.npz"
OUT = HERE.parent / "figures" / "fig_filter"
LEG_PT = 9
SAMPLE = {1: fs.PAL["red"], 2: fs.PAL["yellow"], 3: fs.PAL["green"]}
PASSES = {0: fs.PAL["blue"], 2: fs.PAL["orange"], 4: fs.PAL["red"]}
DASH = (0, (4.0, 1.8))
LEG = dict(fontsize=LEG_PT, handlelength=1.9, borderaxespad=0.35, labelspacing=0.25,
           frameon=False)


def line(ax, d, key, color, comp, shift=0.0, **kw):
    ax.plot(d[f"{key}_t"], d[f"{key}_alpha"] - shift, color=color,
            ls=DASH if comp else "-", lw=1.4, **kw)


def samples(ax, d):
    a0 = float(d["alpha_eq"])
    ax.axhline(0.0, **{**fs.REF_LINE, "lw": 1.0})
    for s in (3, 2, 1):
        line(ax, d, f"s{s}_p4", SAMPLE[s], False, a0)
        line(ax, d, f"s{s}_c4", SAMPLE[s], True, a0)
    leg = ax.legend([Line2D([], [], color=SAMPLE[s]) for s in (1, 2, 3)],
                    [f"sample {s}" for s in (1, 2, 3)], loc="upper right", **LEG)
    ax.add_artist(leg)
    ax.legend([Line2D([], [], color="k", lw=1.4), Line2D([], [], color="k", lw=1.4, ls=DASH)],
              ["plain filter", "compensated"], loc="lower left", **LEG)
    ax.text(0.04, 0.95, r"$y_c = 0.819$", transform=ax.transAxes, ha="left", va="top")


def passes(ax, d):
    a0 = float(d["alpha_eq"])
    ax.axhline(0.0, **{**fs.REF_LINE, "lw": 1.0})
    line(ax, d, "s1_p0", PASSES[0], False, a0)
    for n in (2, 4):
        line(ax, d, f"s1_p{n}", PASSES[n], False, a0)
        line(ax, d, f"s1_c{n}", PASSES[n], True, a0)
    ax.legend([Line2D([], [], color=PASSES[n]) for n in (0, 2, 4)],
              ["no filter", "two passes", "four passes"], loc="lower left", **LEG)
    ax.text(0.04, 0.95, r"$y_c = 0.819$", transform=ax.transAxes, ha="left", va="top")


def unstable(ax, d):
    for s in (3, 2, 1):
        line(ax, d, f"u_s{s}_c4", SAMPLE[s], True)
    line(ax, d, "u_s1_p4", SAMPLE[1], False)
    ax.legend([Line2D([], [], color="k", lw=1.4), Line2D([], [], color="k", lw=1.4, ls=DASH)],
              ["plain filter", "compensated"], loc="lower right", **LEG)
    ax.text(0.04, 0.95, r"$y_c = 0.5$", transform=ax.transAxes, ha="left", va="top")


def make():
    fs.use_style()
    d = np.load(DATA)
    W, Hfig = fs.FULL_WIDTH, 3.0
    fig = plt.figure(figsize=(W, Hfig))
    left, gap_shared, gap_own, right, bot, top = 0.74, 0.10, 0.66, 0.20, 0.45, 0.08
    w = (W - left - gap_shared - gap_own - right) / 3
    h = Hfig - bot - top
    a1 = fs.inch_axes(fig, left, bot, w, h)
    a2 = fs.inch_axes(fig, left + w + gap_shared, bot, w, h)
    a3 = fs.inch_axes(fig, left + 2 * w + gap_shared + gap_own, bot, w, h)
    samples(a1, d)
    passes(a2, d)
    unstable(a3, d)
    for ax in (a1, a2):
        ax.set_xlim(0, 300)
        ax.set_ylim(-0.029, 0.046)
        ax.set_xticks([0, 100, 200, 300])
    # no label at the shared edge, where 300 and 0 would meet
    a1.set_xticklabels(["0", "100", "200", ""])
    a2.set_xticklabels(["", "100", "200", "300"])
    a2.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    a1.set_ylabel(r"$\alpha_c - \alpha_{c,\rm eq}$")
    a3.set_xlim(0, 200)
    a3.set_xticks([0, 50, 100, 150, 200])
    a3.set_ylim(0.53, 0.96)
    a3.set_ylabel(r"$\alpha_c$")
    for ax in (a1, a2, a3):
        ax.set_xlabel(r"$t/M$", labelpad=1)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
