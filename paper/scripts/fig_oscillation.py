"""Central lapse of the stable relativistic cluster y_c = 0.819 with 10^4 particles over
long times, and its controls.

Top: central lapse minus its equilibrium value for three samples (colour), the first
continued to the end of its run. Bottom left: the same model with a small inward
velocity kick, with 10^4 and 10^3 particles. Bottom middle: the first sample against
the same run with a compensation pass that also cancels the width of the cloud.
Bottom right: difference of four control runs from the first sample, on an expanded
scale: half the time step, constraint damping kappa_1 = 0.1 and 0 (dashed),
parabolic relaxation of the Hamiltonian constraint. Black: the equilibrium, or zero
difference.

Reads paper/data/oscillation.npz, written by make_data_oscillation.py.

    python3 paper/scripts/fig_oscillation.py
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

DATA = HERE.parent / "data" / "oscillation.npz"
OUT = HERE.parent / "figures" / "fig_oscillation"
LEG_PT = 9
RED, YEL, GRN, ORA = fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]
PURPLE = "#7B3FA0"
DASH = (0, (4.0, 1.8))
CTL = {   # key: (label, colour, line style)
    "dt2": (r"$\Delta t/2$", YEL, "-"),
    "k1_0p1": (r"$\kappa_1 = 0.1$", GRN, "-"),
    "k1_0": (r"$\kappa_1 = 0$", GRN, DASH),
    "ch": (r"relaxation of $\mathcal{H}$", ORA, "-"),
}
LEG = dict(fontsize=LEG_PT, handlelength=1.9, borderaxespad=0.35, labelspacing=0.25)
SCALE = 1e4              # differences of the controls in units of 10^-4
YLIM = (-0.031, 0.022)   # central lapse minus equilibrium, all panels


def samples(ax, d):
    a0 = float(d["alpha_eq"])
    ax.axhline(0.0, **{**fs.REF_LINE, "lw": 1.0})
    for key, col in (("s3", GRN), ("s2", YEL)):
        ax.plot(d[f"{key}_t"], d[f"{key}_alpha"] - a0, color=col, lw=1.3)
    ax.plot(d["base_t"], d["base_alpha"] - a0, color=RED, lw=1.3)
    t_end = float(d["base_t_end"])
    ax.set_xlim(0, t_end)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(100 if t_end <= 700 else 200))
    ax.set_ylim(*YLIM)
    ax.set_ylabel(r"$\alpha_c - \alpha_{c,\rm eq}$")
    ax.set_xlabel(r"$t/M$", labelpad=1)
    ax.legend([Line2D([], [], color=c) for c in (RED, YEL, GRN)],
              ["sample 1", "sample 2", "sample 3"], loc="lower left", ncol=3,
              columnspacing=1.2, frameon=False, **LEG)
    ax.text(0.015, 0.94, r"$y_c = 0.819$", transform=ax.transAxes, ha="left", va="top")


def particles(ax, d):
    a0 = float(d["alpha_eq"])
    ax.axhline(0.0, **{**fs.REF_LINE, "lw": 1.0})
    ax.plot(d["kick_n3_t"], d["kick_n3_alpha"] - a0, color=ORA, lw=1.3)
    ax.plot(d["kick_n4_t"], d["kick_n4_alpha"] - a0, color=RED, lw=1.3)
    ax.set_ylabel(r"$\alpha_c - \alpha_{c,\rm eq}$")
    ax.legend([Line2D([], [], color=RED), Line2D([], [], color=ORA)],
              [r"$N = 10^4$", r"$N = 10^3$"], loc="lower left", frameon=False, **LEG)
    ax.text(0.05, 0.94, "inward kick", transform=ax.transAxes, ha="left", va="top")


def cloud(ax, d):
    a0 = float(d["alpha_eq"])
    ax.axhline(0.0, **{**fs.REF_LINE, "lw": 1.0})
    t, a = d["base_t"], d["base_alpha"]
    w = t <= 300.0
    ax.plot(d["ctl_ccloud_t"], d["ctl_ccloud_alpha"] - a0, color=PURPLE, lw=1.3)
    ax.plot(t[w], a[w] - a0, color=RED, lw=1.3)
    ax.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    ax.legend([Line2D([], [], color=RED), Line2D([], [], color=PURPLE)],
              ["sample 1", "cloud width cancelled"], loc="lower left", frameon=False, **LEG)


def controls(ax, d):
    ax.axhline(0.0, **{**fs.REF_LINE, "lw": 1.0})
    for key in ("ch", "k1_0", "k1_0p1", "dt2"):
        lab, col, ls = CTL[key]
        ax.plot(d[f"ctl_{key}_t"], SCALE * d[f"ctl_{key}_diff"], color=col, ls=ls, lw=1.3)
    ax.set_ylim(-4.6, 10.6)
    ax.set_yticks([-4, 0, 4, 8])
    ax.set_ylabel(r"difference $[10^{-4}]$")
    keys = ("dt2", "k1_0p1", "k1_0", "ch")
    ax.legend([Line2D([], [], color=CTL[k][1], ls=CTL[k][2]) for k in keys],
              [CTL[k][0] for k in keys], loc="upper left", frameon=False, **LEG)


def make():
    fs.use_style()
    d = np.load(DATA)
    W, Hfig = fs.FULL_WIDTH, 5.0
    fig = plt.figure(figsize=(W, Hfig))
    left, right, bot, gap_y, top = 0.74, 0.24, 0.45, 0.55, 0.08
    gap_shared, gap_own = 0.10, 0.74
    h = (Hfig - bot - gap_y - top) / 2
    w3 = (W - left - right - gap_shared - gap_own) / 3
    a_s = fs.inch_axes(fig, left, bot + h + gap_y, W - left - right, h)
    a_n = fs.inch_axes(fig, left, bot, w3, h)
    a_w = fs.inch_axes(fig, left + w3 + gap_shared, bot, w3, h)
    a_c = fs.inch_axes(fig, left + 2 * w3 + gap_shared + gap_own, bot, w3, h)
    samples(a_s, d)
    particles(a_n, d)
    cloud(a_w, d)
    controls(a_c, d)
    for ax in (a_n, a_w, a_c):
        ax.set_xlim(0, 300)
        ax.set_xticks([0, 100, 200, 300])
        ax.set_xlabel(r"$t/M$", labelpad=1)
    for ax in (a_n, a_w):
        ax.set_ylim(*YLIM)
    # no label at the shared edge, where 300 and 0 would meet
    a_n.set_xticklabels(["0", "100", "200", ""])
    a_w.set_xticklabels(["", "100", "200", "300"])
    # y-labels of the left column at the same distance (inches) from their axes
    for ax in (a_s, a_n, a_c):
        ax.yaxis.set_label_coords(-0.53 / (ax.get_position().width * W), 0.5)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
