"""Cluster with two collapsing overdensities: the envelope at the radius at which the
stated orbital speed is the circular speed (speed-matched radius, areal radius 13.3 M)
against the envelope at the areal radius the original paper states in its text (stated
radius, 30 M), both with finest cells M/64 and otherwise the same configuration.

Top: coordinate separation of the black holes A and B (the record of the data script:
before the first apparent horizon the densest point of each overdensity, after it the
puncture trackers); after the merger the code joins the two trackers into one point, so
the separation is drawn up to the first record with coincident trackers. Middle:
apparent-horizon masses (found searches only, as in fig_overdensities.py) of the
individual black holes and of the common horizon, logarithmic axis; dotted line: the
total mass M of the initial data. A and B coincide at the line width in both runs, so
one line, A, stands for both (for the caption: "A and B coincide"). The script prints
the largest difference and where it exceeds half the line width (speed-matched radius:
three searches in the last M before the individual horizons end, |M_A - M_B| up to
0.011; stated radius: nowhere), and draws B dotted in the run's colour should that
last longer than B_VISIBLE. Bottom:
rest mass of the envelope's macroparticles still present (neither removed inside the
black holes nor left the domain), as a fraction of its value at t = 0, from the particle
snapshots (fig_overdensities.py plots the number fraction of the same macroparticles;
the two differ by less than 10^-3 because the macroparticle masses are nearly equal).
Dark blue dashed: speed-matched radius; orange solid: stated radius (labelled in the
top panel). Black open circles: masses of the original paper (individual black holes at
10 M and 60 M, the common apparent horizon when it is first found and at 100 M), not
clipped at the frame; black ticks at the top: the original's merger time (first common
apparent horizon). Lines end where the runs have got to; the time axis runs a little
past 100 M (PAD) so that nothing ends on the frame.

Reads paper/data/overdensities.npz, written by make_data_overdensities.py.

    python3 paper/scripts/fig_overdensities_radius.py
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

DATA = HERE.parent / "data" / "overdensities.npz"
OUT = HERE.parent / "figures" / "fig_overdensities_radius"
W = 3.4                  # one column of the two-column journal page, in inches
LAB_PT = 9
T_MAX = 100.0            # common time axis, in M
PAD = 2.0                # the axis runs this far past T_MAX, in M
DASH = (0, (3.5, 1.6))
LW = 1.5
# key of the evolution in the data file: label, colour, line style, areal radius of the
# envelope it must have (checked against R_env_<key>, in M)
RUN = {"64": ("speed-matched radius", fs.PAL2["blue"], DASH, 13.3),
       "64R30": ("stated radius", fs.PAL["orange"], "-", 30.0)}
ORDER = ("64", "64R30")                     # drawing order, last on top
ORIG = "k"               # values of the original paper
ORIG_KW = dict(ls="none", marker="o", ms=4.0, mfc="none", mec=ORIG, mew=1.0, zorder=7,
               clip_on=False)
GAP_BREAK = 1.0          # break a horizon curve where no horizon was found for longer
M_LIM = (0.07, 1.6)      # range of the horizon-mass axis
B_VISIBLE = 1.0          # B drawn if it differs from A by half a line width for longer, in M


def found(d, m, lab):
    M = d[f"m{m}_ah{lab}_M"]
    ok = np.isfinite(M)
    return d[f"m{m}_ah{lab}_t"][ok], M[ok]


def broken(t, y, gap=GAP_BREAK):
    """Insert nan where consecutive points are further apart than gap in time."""
    if len(t) < 2:
        return t, y
    k = np.where(np.diff(t) > gap)[0] + 1
    return np.insert(t, k, np.nan), np.insert(y, k, np.nan)


def tick(ax, t, label=None, length=0.12):
    """Tick at the top of the axes at time t (original paper), label to its left."""
    ax.plot([t, t], [1.0, 1.0 - length], transform=ax.get_xaxis_transform(), color=ORIG,
            lw=1.2, clip_on=False, zorder=6)
    if label:
        ax.text(t - 0.015 * T_MAX, 0.97, label, color=ORIG, transform=ax.get_xaxis_transform(),
                ha="right", va="top", fontsize=LAB_PT, linespacing=1.0)


def separation(ax, d):
    for m in ORDER:
        lab, col, ls, _ = RUN[m]
        t, sep = d[f"m{m}_pos_t"], d[f"m{m}_pos_sep"].copy()
        # after the merger the code joins the two trackers into one point: the separation
        # is drawn up to the first record with coincident trackers (as fig_overdensities)
        z0 = np.where(np.isfinite(sep) & (sep < 1e-9) & (t > float(d[f"m{m}_t_switch"])))[0]
        if len(z0):
            sep[z0[0] + 1:] = np.nan
        ax.plot(t, sep, color=col, ls=ls, lw=LW, zorder=3)
    ax.set_ylim(0, 12.5)
    ax.set_yticks((0, 4, 8, 12))
    ax.set_ylabel(r"$d_{AB}/M$")
    # direct labels where the curves are apart: the stated radius below its curve, the
    # speed-matched one right of the end of its curve
    ax.text(63.0, 8.0, RUN["64R30"][0], color=RUN["64R30"][1], ha="left", va="top",
            fontsize=LAB_PT)
    ax.text(63.0, 0.5, "\n".join(RUN["64"][0].rsplit(" ", 1)), color=RUN["64"][1],
            ha="left", va="bottom", fontsize=LAB_PT, linespacing=1.0)
    tick(ax, float(d["orig_t_common"]), "original merger")


def masses(ax, d):
    lw_data = None
    for m in ORDER:
        lab, col, ls, _ = RUN[m]
        tA, MA = found(d, m, "A")
        tB, MB = found(d, m, "B")
        ax.plot(*broken(tA, MA), color=col, ls=ls, lw=LW, zorder=3)
        # B: drawn (dotted) only if it would be told apart from A at the line width for
        # longer than B_VISIBLE in total; otherwise A stands for both
        if len(tA) and len(tB):
            if lw_data is None:
                lw_data = line_width_in_data(ax)
            dm = np.abs(np.interp(tB, tA, np.log(MA)) - np.log(MB))
            dm[(tB < tA[0]) | (tB > tA[-1])] = 0.0
            vis = dm > 0.5 * lw_data
            span = vis.sum() * float(np.median(np.diff(tB))) if len(tB) > 1 else 0.0
            print(f"{RUN[m][0]} ({m}): largest |M_A - M_B| "
                  f"{np.abs(np.interp(tB, tA, MA) - MB).max():.5f}, |ln M_A - ln M_B| {dm.max():.4f} at "
                  f"t = {tB[np.argmax(dm)]:.3f} M; above half the line width ({0.5 * lw_data:.4f}) in "
                  f"{vis.sum()} searches" + (f" ({tB[vis][0]:.3f}-{tB[vis][-1]:.3f} M)" if vis.any() else "")
                  + (": B drawn" if span > B_VISIBLE else ": B not drawn (coincides with A)"))
            if span > B_VISIBLE:
                ax.plot(*broken(tB, MB), color=col, ls=(0, (1.2, 1.2)), lw=0.9, zorder=3)
        tC, MC = found(d, m, "C")
        if len(tC):
            ax.plot(*broken(tC, MC), color=col, ls=ls, lw=LW, zorder=3)
    # original values
    for t, M in zip(d["orig_t_M"], d["orig_M"]):
        ax.plot(float(t), float(M), **ORIG_KW)
    for t, M in ((d["orig_t_common"], d["orig_M_common"]), (d["orig_t_final"], d["orig_M_final"])):
        ax.plot(float(t), float(M), **ORIG_KW)
    ax.axhline(1.0, color="0.55", lw=0.7, ls=(0, (1, 1.5)), zorder=1)
    ax.text(2.0, 0.93, "total mass", color="0.4", fontsize=LAB_PT, ha="left", va="top")
    ax.set_yscale("log")
    ax.set_ylim(*M_LIM)
    ax.set_yticks((0.1, 0.2, 0.5, 1.0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    fs.no_minor_labels(ax)
    ax.set_ylabel(r"$M_{\rm AH}/M$")
    # labels: individual black holes below their curves, common horizon left of its start
    ax.text(30.0, 0.115, "A, B", ha="center", va="top", fontsize=LAB_PT)
    tC, MC = found(d, "64", "C")
    if len(tC):
        ax.text(tC[0] - 2.0, MC[0], "common apparent\nhorizon", ha="right", va="center",
                fontsize=LAB_PT, linespacing=1.0)
    ax.text(float(d["orig_t_final"]) - 3.0, float(d["orig_M_final"]) / 1.25, "original",
            ha="right", va="top", fontsize=LAB_PT)
    tick(ax, float(d["orig_t_common"]))


def line_width_in_data(ax):
    """The data line width (LW points) as a step in ln M on the mass axis."""
    h_pt = ax.get_window_extent().height / ax.figure.dpi * 72.0
    return LW / h_pt * np.log(M_LIM[1] / M_LIM[0])


def envelope(ax, d):
    for m in ORDER:
        lab, col, ls, _ = RUN[m]
        t, mass = d[f"m{m}_snap_t"], d[f"m{m}_snap_m"][:, 0]
        ax.plot(t, mass / mass[0], color=col, ls=ls, lw=LW, zorder=3)
    ax.set_ylim(0, 1.15)
    ax.set_yticks((0, 0.5, 1))
    ax.set_ylabel("fraction remaining")
    ax.text(3.0, 0.08, "rest mass of the envelope\noutside the black holes",
            ha="left", va="bottom", fontsize=LAB_PT, linespacing=1.1)
    tick(ax, float(d["orig_t_common"]), length=0.08)
    ax.set_xlabel(r"$t/M$", labelpad=1)


def make():
    fs.use_style()
    d = np.load(DATA)
    for m, (lab, _, _, R) in RUN.items():
        assert abs(float(d[f"R_env_{m}"]) - R) < 0.1, (m, lab, float(d[f"R_env_{m}"]))
    Hfig = 4.6
    fig = plt.figure(figsize=(W, Hfig))
    left, right, bot, top, gap = 0.56, 0.12, 0.42, 0.08, 0.06
    w = W - left - right
    h = (Hfig - bot - top - 2 * gap) / 3
    a_c = fs.inch_axes(fig, left, bot, w, h)
    a_m = fs.inch_axes(fig, left, bot + h + gap, w, h)
    a_d = fs.inch_axes(fig, left, bot + 2 * (h + gap), w, h)
    separation(a_d, d)
    masses(a_m, d)
    envelope(a_c, d)
    for ax in (a_d, a_m, a_c):
        ax.set_xlim(0, T_MAX + PAD)
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(20))
        ax.yaxis.set_label_coords(-0.42 / w, 0.5)
    for ax in (a_d, a_m):
        ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
