"""Apparent-horizon mass of a vacuum black hole of unit mass against the mass of the slice.

Top: mass reported by the apparent-horizon finder of the host code against time, for
cell spacings M/4, M/8, M/16 at the puncture (colour), with the derivatives the finder
stores (solid) and with derivatives from the interpolant of the metric (dashed, M/8);
open circles: Misner-Sharp mass of the slice at its outermost trapped sphere; filled
diamonds: the corrected finder on the same slices at t = 50 M; blue: the mass of the
black hole. Bottom: the same, enlarged about the mass of the black hole.

Reads paper/data/horizon_check.npz, written by make_data_horizon_check.py.

    python3 paper/scripts/fig_horizon_check.py
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

DATA = HERE.parent / "data" / "horizon_check.npz"
OUT = HERE.parent / "figures" / "fig_horizon_check"
LEG_PT = 9
BLUE = fs.PAL["blue"]
COL = {"dx4": fs.PAL["yellow"], "dx8": fs.PAL["red"], "dx16": fs.PAL["green"]}
LABEL = {"dx4": r"$\Delta x = M/4$", "dx8": r"$\Delta x = M/8$", "dx16": r"$\Delta x = M/16$"}
T_MIN = 8.0              # earlier rows: the finder during the initial gauge transient
SLICE_MK = dict(ls="none", marker="o", ms=5.5, mfc="white", mew=1.3, zorder=6)
CPU_MK = dict(ls="none", marker="D", ms=4.5, mew=0.0, zorder=7)
ZOOM = 1e3               # bottom panel in units of 10^-3


def draw(ax, d, scale, shift):
    """All series as (mass - shift) * scale."""
    f = lambda m: (np.asarray(m) - shift) * scale
    ax.axhline(f(1.0), color=BLUE, lw=1.5, zorder=1)
    for key in ("dx4", "dx8", "dx16"):
        t, m = d[f"{key}_t"], d[f"{key}_M"]
        w = t >= T_MIN
        ax.plot(t[w], f(m[w]), color=COL[key], lw=1.5)
    t, m = d["dx8c_t"], d["dx8c_M"]
    w = t >= T_MIN
    ax.plot(t[w], f(m[w]), color=COL["dx8"], lw=1.5, ls=(0, (4, 2)), zorder=4)
    for key, run in (("dx4", "dx4"), ("dx8", "dx8"), ("dx16", "dx16"), ("dx8", "dx8c")):
        s = d[f"{run}_slice"]
        ax.plot(s[:, 0], f(s[:, 1]), mec=COL[key], **SLICE_MK)
    for key in ("dx8", "dx16"):
        t, m = d[f"{key}_cpu"]
        ax.plot([t], [f(m)], color=COL[key], **CPU_MK)


def make():
    fs.use_style()
    d = np.load(DATA)
    W, Hfig = fs.COLUMN_WIDTH, 4.6
    fig = plt.figure(figsize=(W, Hfig))
    xl, w = 0.80, W - 0.80 - 0.14
    b0, hz, gap, ht = 0.45, 1.25, 0.06, 2.62
    az = fs.inch_axes(fig, xl, b0, w, hz)
    at = fs.inch_axes(fig, xl, b0 + hz + gap, w, ht)

    leg_kw = dict(fontsize=LEG_PT, handlelength=1.8, borderaxespad=0.3, labelspacing=0.25,
                  frameon=False)
    draw(at, d, 1.0, 0.0)
    at.set_ylim(0.897, 1.012)
    at.set_ylabel(r"horizon mass$/M$")
    at.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    keys = ("dx4", "dx8", "dx16")
    leg = at.legend([Line2D([], [], color=COL[k]) for k in keys], [LABEL[k] for k in keys],
                    loc="lower left", **leg_kw)
    at.add_artist(leg)
    at.legend([Line2D([], [], color="k", lw=1.5),
               Line2D([], [], color="k", lw=1.5, ls=(0, (4, 2)))],
              ["finder of the host code", "corrected finder"], loc="lower right", **leg_kw)

    draw(az, d, ZOOM, 1.0)
    az.set_ylim(-0.75, 2.45)
    az.set_yticks([0, 1, 2])
    az.set_ylabel(r"mass$/M - 1\ \ [10^{-3}]$")
    az.set_xlabel(r"$t/M$", labelpad=1)
    az.legend([Line2D([], [], mec="k", **SLICE_MK), Line2D([], [], color="k", **CPU_MK)],
              ["Misner-Sharp mass of the slice", "corrected finder on the same slice"],
              loc="upper left", handletextpad=0.4, **{**leg_kw, "handlelength": 1.0})
    for ax in (at, az):
        ax.set_xlim(0, 62)
        ax.yaxis.set_label_coords(-0.16, 0.5)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
