"""Clusters of 10^4 test particles around a black hole of spin a = 0.9 M.

Top: a bound cluster started on a circular orbit phase-mixes into a ring (particle
positions in the orbital plane, mesh metric, implicit midpoint pusher; black disk: the
black hole). Bottom left: median (solid) and 99th percentile (dashed) over the particles
of the relative errors of the geodesic energy and of the axial angular momentum, with the
exact invariants; colour = pusher, thick = mesh metric (the spacetime Boris run drawn
wider underneath the implicit midpoint run), thin = analytic metric. Bottom right, for a
cluster of lower angular momentum: the conservation identity of the deposition before the
filter, every cycle (red), with the rate of refinement-level changes (grey), and the
cumulative number of particles removed by lapse excision (red) against the exact
prediction (blue dashed).

Reads paper/data/tp_cluster.npz, written by make_data_tp_cluster.py.

    python3 paper/scripts/fig_tp_cluster.py
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
from matplotlib.patches import Circle

import figstyle as fs

DATA = HERE.parent / "data" / "tp_cluster.npz"
OUT = HERE.parent / "figures" / "fig_tp_cluster"
LEG_PT = 9
RED, YEL, GRN, BLUE = fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["blue"]
GREY = "0.55"
HALF = 24.0                     # half-width of the snapshot panels [M]
LW_THIN, LW_MESH, LW_HALO = 1.2, 2.2, 4.2
DASH = (5.0, 2.5)               # dash pattern of the 99th percentile in points
FLOOR = 1e-17


def dashed(lw):
    """Dash pattern in points, independent of the line width."""
    return (0, (DASH[0] / lw, DASH[1] / lw))


def binned_max(t, v, width):
    edges = np.arange(0.0, t[-1] + width, width)
    k = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, len(edges) - 2)
    out = np.zeros(len(edges) - 1)
    np.maximum.at(out, k, np.abs(v))
    return 0.5 * (edges[1:] + edges[:-1]), out


def snapshots(fig, d, x0, y0, side):
    a = float(d["a"])
    r_hor = np.sqrt((1 + np.sqrt(1 - a * a)) ** 2 + a * a)   # equatorial horizon, KS x-y
    axes = []
    for k, t in enumerate(d["snap_t"]):
        ax = fs.inch_axes(fig, x0 + k * side, y0, side, side)
        xy = d["snap_xy"][k]
        xy = xy[np.isfinite(xy[:, 0])]
        ax.scatter(xy[:, 0], xy[:, 1], s=0.15, lw=0, color=RED, rasterized=True)
        ax.add_patch(Circle((0, 0), r_hor, color="k", zorder=3))
        ax.set_xlim(-HALF, HALF)
        ax.set_ylim(-HALF, HALF)
        ax.set_aspect("equal")
        fs.slice_ticks(ax, HALF, show_y=(k == 0))
        lab = r"$t = 0$" if t == 0 else rf"$t = {t:.0f}\,M$"
        ax.text(0.05, 0.94, lab, transform=ax.transAxes, ha="left", va="top")
        ax.set_xlabel(r"$x/M$", labelpad=1)
        if k == 0:
            ax.set_ylabel(r"$y/M$", labelpad=0)
        axes.append(ax)
    return axes


def invariants(aE, aL, d):
    t = d["inv_t"]
    s = slice(1, None)                       # the errors vanish at t = 0
    runs = [("ana_mid", RED), ("ana_boris", YEL), ("ana_chol", GRN)]
    for ax, q in ((aE, "E"), (aL, "L")):
        # mesh metric: Boris (yellow, wide) underneath the implicit midpoint (red)
        for key, col, lw in (("mesh_boris", YEL, LW_HALO), ("mesh_mid", RED, LW_MESH)):
            ax.plot(t[s], d[f"inv_{key}_{q}_med"][s], color=col, lw=lw,
                    solid_capstyle="butt")
            ax.plot(t[s], d[f"inv_{key}_{q}_p99"][s], color=col, lw=lw, ls=dashed(lw),
                    dash_capstyle="butt")
        for key, col in runs:
            ax.plot(t[s], d[f"inv_{key}_{q}_med"][s], color=col, lw=LW_THIN)
            ax.plot(t[s], d[f"inv_{key}_{q}_p99"][s], color=col, lw=LW_THIN,
                    ls=dashed(LW_THIN))
        ax.set_yscale("log")
        ax.set_xlim(0, t[-1])
    aE.set_ylim(1e-10, 1e-1)
    aL.set_ylim(1e-16, 1e0)
    aE.set_ylabel(r"$|\Delta\mathcal{E}/\mathcal{E}|$")
    aL.set_ylabel(r"$|\Delta L_z/L_z|$")
    aL.set_xlabel(r"$t/M$", labelpad=1)
    aE.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    aE.set_yticks(10.0 ** np.arange(-9, -2, 2))
    aL.set_yticks(10.0 ** np.arange(-14, -1, 4))
    for ax in (aE, aL):
        ax.yaxis.set_minor_locator(matplotlib.ticker.LogLocator(numticks=30))
        fs.no_minor_labels(ax)
    aE.legend([Line2D([], [], color=c, lw=LW_THIN) for c in (RED, YEL, GRN)],
              ["implicit midpoint", "spacetime Boris, symmetric gauge",
               "spacetime Boris, Cholesky gauge"],
              loc="upper left", fontsize=LEG_PT, handlelength=1.6, borderaxespad=0.3,
              labelspacing=0.25)
    aL.legend([Line2D([], [], color="k", lw=LW_MESH), Line2D([], [], color="k", lw=LW_THIN),
               Line2D([], [], color="k", lw=LW_THIN),
               Line2D([], [], color="k", lw=LW_THIN, ls=dashed(LW_THIN))],
              ["mesh metric", "analytic metric", "median", "99th percentile"],
              loc="upper left", ncol=2, fontsize=LEG_PT, handlelength=1.8,
              borderaxespad=0.3, labelspacing=0.25, columnspacing=1.2)


def deposition(ax, d):
    t, res = d["dep_plunge_t"], d["dep_plunge_res"]
    tb, vb = binned_max(t, res, 10.0)
    vb = np.maximum(vb, FLOOR)            # exact zeros
    tl, rate = d["lev_plunge_t"], d["lev_plunge_rate"]
    ar = ax.twinx()
    ar.fill_between(tl, 0, rate, color=GREY, alpha=0.35, lw=0, step="mid")
    ar.set_ylim(0, 1.25 * rate.max())
    ar.set_ylabel(r"level changes per $M$", color=GREY, labelpad=3)
    ar.tick_params(axis="y", colors=GREY, which="both")
    ar.spines["right"].set_color(GREY)
    ax.set_zorder(ar.get_zorder() + 1)
    ax.patch.set_visible(False)
    ax.plot(tb, vb, color=RED, lw=1.5)
    ax.set_yscale("log")
    ax.set_ylim(FLOOR, 1e-11)
    ax.set_yticks(10.0 ** np.arange(-16, -11, 2))
    ax.yaxis.set_minor_locator(matplotlib.ticker.LogLocator(numticks=30))
    fs.no_minor_labels(ax)
    ax.tick_params(axis="y", which="both", right=False)
    ax.set_xlim(0, t[-1])
    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    ax.set_ylabel("relative difference")
    ax.legend([Line2D([], [], color=RED)],
              [r"$|\int E\sqrt{\gamma}\,\mathrm{d}V\,/\sum\, m_p W_p - 1|$"],
              loc="upper right", fontsize=LEG_PT, handlelength=1.6, borderaxespad=0.3)
    return ar


def removal(ax, d):
    t, n = d["exc_t"], d["exc_n"]
    tp = d["pred_t"]
    ax.plot(np.concatenate([[0.0], tp, [t[-1]]]),
            np.concatenate([[0], np.arange(1, len(tp) + 1), [len(tp)]]),
            color=BLUE, lw=1.5, ls="--", drawstyle="steps-post", zorder=3)
    ax.plot(t, n, color=RED, lw=2.4, drawstyle="steps-post", zorder=2)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(0, 4000)
    ax.set_yticks([0, 1000, 2000, 3000])
    ax.set_xlabel(r"$t/M$", labelpad=1)
    ax.set_ylabel("removed particles")
    ax.legend([Line2D([], [], color=RED), Line2D([], [], color=BLUE, ls="--")],
              ["lapse excision", "exact geodesics"], loc="lower right",
              fontsize=LEG_PT, handlelength=1.8, borderaxespad=0.4)


def make():
    fs.use_style()
    d = np.load(DATA)
    W, Hfig = fs.FULL_WIDTH, 5.92
    fig = plt.figure(figsize=(W, Hfig))
    xl, wl, gap, wr = 0.66, 3.22, 0.80, 2.72
    b0, hp, hg = 0.42, 1.50, 0.06
    snapshots(fig, d, xl, b0 + 2 * hp + hg + 0.58, (W - xl - 0.08) / 4)
    aL = fs.inch_axes(fig, xl, b0, wl, hp)
    aE = fs.inch_axes(fig, xl, b0 + hp + hg, wl, hp)
    aR = fs.inch_axes(fig, xl + wl + gap, b0, wr, hp)
    aD = fs.inch_axes(fig, xl + wl + gap, b0 + hp + hg, wr, hp)
    invariants(aE, aL, d)
    deposition(aD, d)
    removal(aR, d)
    for ax in (aE, aL):
        ax.yaxis.set_label_coords(-0.15, 0.5)
    for ax in (aD, aR):
        ax.yaxis.set_label_coords(-0.19, 0.5)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
