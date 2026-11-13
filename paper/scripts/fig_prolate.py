"""Collapse of a cold prolate spheroid (eccentricity 0.9, polar semi-axis 10 M, total
mass M) with 10^4 macroparticles: it collapses through a spindle whose two curvature
maxima on the axis move inward, and an apparent horizon forms at the time of the
original paper.

Top: macroparticle positions projected on the x-z plane at four times (each panel with
its own window; the bar gives the scale); open circles: the two maxima of the
Kretschmann scalar I on the axis; black curve in the last panel: section of the first
apparent horizon. Bottom left: largest I on the mesh (top strip) and |z| of its maximum
while it lies on the axis (dots), with the outermost macroparticle and the polar radius
of the apparent horizon (bottom strip). Bottom middle: smallest lapse, fraction of
macroparticles remaining, and the excision threshold (dotted). Bottom right:
apparent-horizon mass and total mass M (blue). Dashed: first apparent horizon; blue
ticks at the top: the times shown in the original paper.

Reads paper/data/prolate.npz, written by make_data_prolate.py.

    python3 paper/scripts/fig_prolate.py
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

DATA = HERE.parent / "data" / "prolate.npz"
OUT = HERE.parent / "figures" / "fig_prolate"
W = 7.0                  # full width of the two-column journal page, in inches
LAB_PT = 8
RED, BLUE = fs.PAL["red"], fs.PAL["blue"]
DASH = (0, (4.0, 1.8))
# half-width of the window and scale-bar length of each snapshot panel, in M
HALF = (10.5, 7.2, 4.6, 2.2)
BAR = (5.0, 5.0, 2.0, 1.0)
ON_AXIS = 0.1            # largest cylindrical radius of a cell counted as on the axis


def scale_bar(ax, half, length):
    """Bar of the given length in the lower right corner, label above it."""
    x1 = 0.92 * half
    y = -0.88 * half
    ax.plot([x1 - length, x1], [y, y], color="k", lw=1.5, solid_capstyle="butt")
    ax.text(x1 - length / 2, y + 0.05 * half, f"{length:g} M", ha="center", va="bottom",
            fontsize=LAB_PT)


def curvature_at(d, t):
    k = int(np.argmin(np.abs(d["c_t"] - t)))
    return d["c_Ix"][k], abs(d["c_Iz"][k])


def snapshots(axes, d):
    for j, ax in enumerate(axes):
        L = HALF[j]
        ax.scatter(d[f"p{j}_x"], d[f"p{j}_z"], s=0.25, lw=0, color=RED, rasterized=True)
        ax.set_xlim(-L, L)
        ax.set_ylim(-L, L)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.minorticks_off()
        t = float(d[f"p{j}_t"])
        ax.text(0.04, 0.96, rf"$t={t:g}\,M$", transform=ax.transAxes, ha="left",
                va="top", fontsize=9)
        scale_bar(ax, L, BAR[j])
        if j in (1, 2):      # the two curvature maxima on the axis
            x, z = curvature_at(d, t)
            ax.plot([x, x], [z, -z], ls="none", marker="o", ms=6, mfc="none", mec="k",
                    mew=1.0)
            if j == 1:
                ax.annotate(r"largest $I$", xy=(x + 0.45, z), xytext=(2.0, z + 0.9),
                            fontsize=LAB_PT, ha="left", va="center",
                            arrowprops=dict(arrowstyle="-", color="k", lw=0.8,
                                            shrinkA=0, shrinkB=0))
        if j == 3:
            ax.plot(d["ah_sec_x"], d["ah_sec_z"], color="k", lw=1.0)
            ax.text(0.95, 0.95, "apparent\nhorizon", transform=ax.transAxes, ha="right",
                    va="top", fontsize=LAB_PT, linespacing=1.0)
        ax.set_xlabel(r"$x$", labelpad=2)
    axes[0].set_ylabel(r"$z$", labelpad=4)


def mark_times(ax, d, label=False, y_lab=0.995):
    """Dashed line at the first horizon; blue ticks at the top for the original."""
    ax.axvline(float(d["ah_first_t"]), ls=DASH, zorder=1, **fs.THIN)
    for t in d["t_original"]:
        ax.plot([t, t], [1.0, 0.92], transform=ax.get_xaxis_transform(), color=BLUE,
                lw=1.2, clip_on=False, zorder=6)
    if label:
        ax.text(d["t_original"][0] - 1.6, y_lab, "original",
                transform=ax.get_xaxis_transform(), color=BLUE, ha="right", va="top",
                fontsize=LAB_PT)


def curvature(ax, d):
    ax.plot(d["c_t"], d["c_I"], color=RED, lw=1.2)
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 3e4)
    ax.set_yticks((1e-2, 1, 1e2, 1e4))
    ax.yaxis.set_minor_locator(matplotlib.ticker.LogLocator(numticks=20))
    fs.no_minor_labels(ax)
    ax.set_ylabel(r"$M^4 I_{\max}$")
    # the finest mesh levels appear here (time step drops)
    dt = d["h_dt"]
    tr = float(d["h_t"][np.argmax(dt < 0.5 * dt[0])])
    ax.text(tr - 1.0, 3e0, "finer\nmesh", ha="right", va="center", fontsize=LAB_PT,
            linespacing=1.0)


def position(ax, d):
    on = (np.hypot(d["c_Ix"], d["c_Iy"]) < ON_AXIS) & (d["c_t"] <= d["snap_t"][
        d["snap_n"] > 0][-1])
    ax.plot(d["c_t"][on], np.abs(d["c_Iz"][on]), ls="none", marker="o", ms=2.2, mew=0,
            color=RED)
    live = d["snap_n"] > 0
    ax.plot(d["snap_t"][live], d["snap_zmax"][live], color=RED, lw=1.0, ls=DASH)
    ax.plot(d["ah_t"], 0.5 * (d["ah_r_north"] + d["ah_r_south"]), color="k", lw=1.0)
    ax.set_ylim(0, 11)
    ax.set_yticks((0, 5, 10))
    ax.set_ylabel(r"$|z|/M$")
    ax.text(3.0, 7.6, "outermost\nparticle", color=RED, fontsize=LAB_PT, ha="left",
            va="top", linespacing=1.0)
    ax.annotate("largest $I$", xy=(19.9, 4.6), xytext=(17.0, 1.6), color=RED,
                fontsize=LAB_PT, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.8, shrinkA=1, shrinkB=0))
    ax.text(44.0, 2.2, "horizon", fontsize=LAB_PT, ha="right", va="bottom")


def lapse(ax, d):
    ax.axhline(float(d["alpha_exc"]), ls=":", zorder=1, **fs.THIN)
    ax.plot(d["h_t"], d["h_np"] / float(d["n0"]), color=RED, lw=1.2, ls=DASH)
    ax.plot(d["h_t"], d["h_alpha_min"], color=RED, lw=1.2)
    ax.set_ylim(0, 1.15)
    ax.set_yticks((0, 0.5, 1))
    ax.text(31.0, 0.95, "particles remaining", color=RED, fontsize=LAB_PT, ha="right",
            va="top")
    ax.text(1.5, 0.60, "smallest lapse", color=RED, fontsize=LAB_PT, ha="left",
            va="top")


def horizon(ax, d):
    ax.axhline(float(d["m_tot"]), color=BLUE, lw=1.0, zorder=1)
    ok = np.isfinite(d["ah_M"])
    ax.plot(d["ah_t_search"][ok], d["ah_M"][ok], color=RED, lw=1.2)
    ax.set_xlim(19, 45)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
    ax.set_ylim(0.90, 1.02)
    ax.set_yticks((0.90, 0.95, 1.0))
    ax.set_ylabel(r"$M_{\rm AH}/M$")
    ax.text(20.0, 1.003, r"total mass $M$", color=BLUE, fontsize=LAB_PT, ha="left",
            va="bottom")
    ax.text(20.0, 0.93, "no horizon\nfound", fontsize=LAB_PT, ha="left", va="center",
            linespacing=1.0, color="grey")


def make():
    fs.use_style()
    d = np.load(DATA)
    # ---- geometry (inches) ----
    left_t, gap_t, right_t = 0.30, 0.06, 0.04
    P = (W - left_t - right_t - 3 * gap_t) / 4
    bot, hb, gap_rows, top = 0.40, 1.70, 0.50, 0.04
    Hfig = bot + hb + gap_rows + P + top
    fig = plt.figure(figsize=(W, Hfig))
    y_top = bot + hb + gap_rows
    snaps = [fs.inch_axes(fig, left_t + j * (P + gap_t), y_top, P, P) for j in range(4)]
    left_b, gap_b, right_b = 0.62, 0.62, 0.08
    w = (W - left_b - right_b - 2 * gap_b) / 3
    hs = (hb - 0.06) / 2
    a_I = fs.inch_axes(fig, left_b, bot + hs + 0.06, w, hs)
    a_z = fs.inch_axes(fig, left_b, bot, w, hs)
    a_l = fs.inch_axes(fig, left_b + w + gap_b, bot, w, hb)
    a_h = fs.inch_axes(fig, left_b + 2 * (w + gap_b), bot, w, hb)

    snapshots(snaps, d)
    curvature(a_I, d)
    position(a_z, d)
    lapse(a_l, d)
    horizon(a_h, d)
    for ax in (a_I, a_z, a_l):
        ax.set_xlim(0, 45)
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
    for ax in (a_I, a_z, a_l, a_h):
        mark_times(ax, d, label=(ax is a_l))
    a_I.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    for ax in (a_z, a_l, a_h):
        ax.set_xlabel(r"$t/M$", labelpad=1)
    for ax in (a_I, a_z):
        ax.yaxis.set_label_coords(-0.47 / w, 0.5)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
