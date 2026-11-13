"""Collapse of a dust ball of 9328 particles and initial areal radius R_0 = 5 M on an
adaptive mesh, until a black hole forms and all matter is removed.

Top left: central lapse against the proper time of the central normal observer, with
the analytic lapse bound of collapsing dust in 1+log slicing (blue dashed). Top right:
central energy density over its initial value with the cycloid (blue dashed), for the
cloud at the finest level (red) and the level-capped cloud (yellow), until the central
lapse reaches the excision threshold. Bottom left: apparent-horizon mass against time
for four runs (colour) with the total mass (blue). Bottom right: norm of the
Hamiltonian constraint for the same runs (orange, drawn wider, lies under red). Red: cloud at the finest local level with
lattice masses that sum to the rest mass of the initial data; yellow: level-capped
cloud; green: cloud at most one level coarser; orange: as red with the published
lattice mass rule.

Reads paper/data/dust.npz, written by make_data_dust.py.

    python3 paper/scripts/fig_dust.py
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

DATA = HERE.parent / "data" / "dust.npz"
OUT = HERE.parent / "figures" / "fig_dust"
LEG_PT = 9
BLUE = fs.PAL["blue"]
COL = {"ref": fs.PAL["red"], "adapt": fs.PAL["yellow"], "mc1": fs.PAL["green"],
       "pub": fs.PAL["orange"]}
LABEL = {"ref": "cloud at the finest level", "adapt": "level-capped cloud",
         "mc1": "at most one level coarser", "pub": "published lattice masses"}
ORDER = ("ref", "adapt", "mc1", "pub")
DRAW = ("pub", "mc1", "adapt", "ref")          # reference on top
DASH = (0, (4.0, 1.8))
LEG = dict(fontsize=LEG_PT, handlelength=1.9, borderaxespad=0.35, labelspacing=0.25)


def lapse(ax, d):
    ax.plot(d["an_tau"], d["an_alpha"], color=BLUE, lw=1.5, ls=DASH, zorder=5)
    ax.plot(d["ref_tau"], d["ref_alpha"], color=COL["ref"], lw=1.5)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(-0.04, 1.04)
    ax.set_xlabel(r"$\tau_c/M$", labelpad=1)
    ax.set_ylabel(r"$\alpha_c$")
    ax.legend([Line2D([], [], color=COL["ref"]), Line2D([], [], color=BLUE, ls=DASH)],
              ["central lapse", "lapse bound"], loc="lower left", frameon=False, **LEG)


def density(ax, d):
    E0 = float(d["rho0"])
    ax.plot(d["an_tau"], d["an_rho"] / E0, color=BLUE, lw=1.5, ls=DASH, zorder=5)
    for key in ("adapt", "ref"):
        w = d[f"{key}_alpha"] > float(d["alpha_exc"])
        ax.plot(d[f"{key}_tau"][w], d[f"{key}_E"][w] / E0, color=COL[key], lw=1.5)
    ax.set_yscale("log")
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0.3, 40)
    ax.set_xlabel(r"$\tau_c/M$", labelpad=1)
    ax.set_ylabel(r"$E_c/E_0$")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    fs.no_minor_labels(ax)
    ax.legend([Line2D([], [], color=COL["ref"]), Line2D([], [], color=COL["adapt"]),
               Line2D([], [], color=BLUE, ls=DASH)],
              [LABEL["ref"], LABEL["adapt"], "cycloid"], loc="upper left", frameon=False, **LEG)


def horizon(ax, d):
    ax.axhline(1.0, color=BLUE, lw=1.5, zorder=1)
    for key in DRAW:
        ax.plot(d[f"{key}_ah_t"], d[f"{key}_ah_M"], color=COL[key], lw=1.5)
    ax.set_xlim(15, 60)
    ax.set_ylim(0.986, 1.016)
    ax.set_xlabel(r"$t/M$", labelpad=1)
    ax.set_ylabel(r"apparent-horizon mass$/M$")
    ax.text(58.5, 1.0007, "total mass", color=BLUE, fontsize=LEG_PT, ha="right",
            va="bottom")


def constraint(ax, d):
    for key in DRAW:
        # the published lattice masses coincide with the reference here: drawn wider
        # underneath it
        ax.plot(d[f"{key}_z_t"], d[f"{key}_Hnorm"], color=COL[key],
                lw=3.2 if key == "pub" else 1.5)
    ax.set_yscale("log")
    ax.set_xlim(0, 60)
    ax.set_ylim(0.009, 12)
    ax.set_xlabel(r"$t/M$", labelpad=1)
    ax.set_ylabel(r"$\|\mathcal{H}\|$")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    fs.no_minor_labels(ax)
    ax.legend([Line2D([], [], color=COL[k]) for k in ORDER], [LABEL[k] for k in ORDER],
              loc="lower left", frameon=False, **LEG)


def make():
    fs.use_style()
    d = np.load(DATA)
    W, Hfig = fs.FULL_WIDTH, 5.5
    fig = plt.figure(figsize=(W, Hfig))
    left, gap_x, right, bot, gap_y, top = 0.72, 0.78, 0.12, 0.45, 0.55, 0.08
    w = (W - left - gap_x - right) / 2
    h = (Hfig - bot - gap_y - top) / 2
    a_l = fs.inch_axes(fig, left, bot + h + gap_y, w, h)
    a_e = fs.inch_axes(fig, left + w + gap_x, bot + h + gap_y, w, h)
    a_m = fs.inch_axes(fig, left, bot, w, h)
    a_h = fs.inch_axes(fig, left + w + gap_x, bot, w, h)
    lapse(a_l, d)
    density(a_e, d)
    horizon(a_m, d)
    constraint(a_h, d)
    for ax in (a_l, a_m):
        ax.yaxis.set_label_coords(-0.15, 0.5)
    for ax in (a_e, a_h):
        ax.yaxis.set_label_coords(-0.13, 0.5)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
