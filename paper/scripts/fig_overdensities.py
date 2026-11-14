"""Relativistic cluster with two collapsing overdensities: each overdensity collapses to
a black hole (A, B), which then orbits inside the envelope and accretes.

Top: macroparticles projected on the orbital (x-y) plane at t = 0, 12 M, 50 M (while
the run has not passed 60 M: half-way between 12 M and the last snapshot) and the last
snapshot, coloured by species (envelope grey, the overdensities of A and B red and
blue), the same window in every panel; black circles: apparent horizons at true size
(mean coordinate radius) at the black-hole positions, with an open marker where they
are too small to see; the bar gives the scale. Bottom left: coordinate separation of
the black holes (top strip) and orbital phase, the angle of the line from A to B in
turns (bottom strip). The positions are those of the data script: before the first
horizon the densest point of each overdensity, after it the trackers stored with the
restart dumps (dots: filled M/64, open M/128) and in the tracker files, interpolated
between them; the line breaks where they are too far apart to interpolate. After the
merger the code joins the two trackers into one point: the separation is drawn up to
the first record with coincident trackers, the phase while the separation exceeds
0.1 M. Bottom middle: apparent-horizon masses of A, B and of the common horizon (found
searches only; searches of A or B that converged on the common horizon are left out),
dotted line at the total mass M of the initial data. Bottom right: fraction of the
macroparticles of each species remaining (and the dimensionless spin of the common
horizon on a right axis once one is found). Thick solid: finest cells M/64; thin
dashed: M/128. Black open circles and ticks at the top: values and times of the
original paper (black, because blue marks B). Time axes end where the M/64 run has got
to (rounded up to 5 M), so values of the original beyond that time are not drawn.

Reads paper/data/overdensities.npz, written by make_data_overdensities.py.

    python3 paper/scripts/fig_overdensities.py
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
from matplotlib.transforms import offset_copy

import figstyle as fs

DATA = HERE.parent / "data" / "overdensities.npz"
OUT = HERE.parent / "figures" / "fig_overdensities"
W = 7.0                  # full width of the two-column journal page, in inches
LAB_PT = 8
COL = {"env": "0.62", "A": fs.PAL["red"], "B": fs.PAL["blue"], "C": "k"}
ORIG = "k"               # values of the original paper (blue is taken by B)
SP_COL = (COL["env"], COL["A"], COL["B"])         # species 0, 1, 2
ORIG_KW = dict(ls="none", marker="o", ms=4.5, mfc="none", mec=ORIG, mew=1.0, zorder=7)
DASH = (0, (3.5, 1.6))
MESH = {"64": dict(lw=1.5, ls="-"), "128": dict(lw=0.9, ls=DASH)}
DOT = {"64": dict(ls="none", marker="o", ms=3.0, mfc="k", mec="k", mew=0.0, zorder=5),
       "128": dict(ls="none", marker="o", ms=3.0, mfc="white", mec="k", mew=0.7, zorder=5)}
HALF = 8.0               # half-width of the particle windows, in M
BAR = 4.0                # scale bar, in M
GAP_BREAK = 1.0          # break a horizon curve where no horizon was found for longer
SEP_MIN = 0.1            # smallest tracker separation at which the phase is drawn, in M


def scale_bar(ax, half, length):
    """Bar of the given length in the lower right corner, label above it."""
    x1 = 0.92 * half
    y = -0.88 * half
    ax.plot([x1 - length, x1], [y, y], color="k", lw=1.5, solid_capstyle="butt")
    ax.text(x1 - length / 2, y + 0.05 * half, f"{length:g} M", ha="center", va="bottom",
            fontsize=LAB_PT)


def snapshots(axes, d):
    for j, ax in enumerate(axes):
        x, y, sp = d[f"p{j}_x"], d[f"p{j}_y"], d[f"p{j}_sp"]
        for s, size in ((0, 0.18), (1, 0.35), (2, 0.35)):
            m = sp == s
            ax.scatter(x[m], y[m], s=size, lw=0, color=SP_COL[s], rasterized=True,
                       zorder=2 + s)
        L = HALF
        ax.set_xlim(-L, L)
        ax.set_ylim(-L, L)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.minorticks_off()
        t = float(d[f"p{j}_t"])
        ax.text(0.04, 0.96, rf"$t={t:g}\,M$", transform=ax.transAxes, ha="left",
                va="top", fontsize=9)
        scale_bar(ax, L, BAR)
        hz = d[f"p{j}_hz"]
        for k, (hx, hy, r, _) in enumerate(hz):
            if not np.isfinite(r):
                continue
            ax.add_patch(plt.Circle((hx, hy), r, fill=False, color="k", lw=0.6, zorder=8))
            # open marker where the true size is below about 2 pt across
            if 2 * r / (2 * L) * ax.get_window_extent().width / ax.figure.dpi * 72 < 2.0:
                ax.plot(hx, hy, ls="none", marker="o", ms=4.0, mfc="none", mec="k",
                        mew=0.8, zorder=8)
        ax.set_xlabel(r"$x$", labelpad=2)
    axes[0].set_ylabel(r"$y$", labelpad=4)
    # direct labels in the first panel
    a0 = axes[0]
    a0.text(-3.0, -1.6, "A", color=COL["A"], ha="center", va="top", fontsize=9)
    a0.text(3.0, -1.6, "B", color=COL["B"], ha="center", va="top", fontsize=9)
    a0.text(0.0, 5.6, "envelope", color="0.35", ha="center", va="center",
            fontsize=LAB_PT)
    # label the horizons once, in the first panel that has one
    for j, ax in enumerate(axes):
        hz = d[f"p{j}_hz"]
        if np.isfinite(hz[1, 2]):
            ax.annotate("apparent\nhorizon", xy=(hz[1, 0] + 0.25, hz[1, 1] + 0.25),
                        xytext=(hz[1, 0] + 0.6, hz[1, 1] + 2.6), fontsize=LAB_PT,
                        ha="center", va="bottom", linespacing=1.0,
                        arrowprops=dict(arrowstyle="-", color="k", lw=0.7, shrinkA=0,
                                        shrinkB=1))
            break


def x_end(d):
    """Right end of the time axes: the M/64 run's last time, rounded up to 5 M."""
    t = float(d["m64_h_t"][-1])
    return min(float(d["t_end"]), 5.0 * np.ceil(t / 5.0 + 1e-9))


def tick(ax, t, label=None, side="left"):
    """Tick at the top of the axes at time t (original paper), label beside it."""
    ax.plot([t, t], [1.0, 0.90], transform=ax.get_xaxis_transform(), color=ORIG,
            lw=1.2, clip_on=False, zorder=6)
    if label:
        off = (-1 if side == "left" else 1) * 0.015 * np.diff(ax.get_xlim())[0]
        ax.text(t + off, 0.985, label, color=ORIG, transform=ax.get_xaxis_transform(),
                ha="right" if side == "left" else "left", va="top", fontsize=LAB_PT,
                linespacing=1.0)


def ab_label(ax, x, y, coords="data", size=LAB_PT):
    """'A, B' with each letter in its colour."""
    tr = ax.transData if coords == "data" else ax.transAxes
    ax.text(x, y, "A", color=COL["A"], transform=tr, ha="left", va="center", fontsize=size)
    ax.text(x, y, ",", transform=offset_copy(tr, fig=ax.figure, x=0.62 * size, units="points"),
            ha="left", va="center", fontsize=size)
    ax.text(x, y, "B", color=COL["B"],
            transform=offset_copy(tr, fig=ax.figure, x=1.05 * size, units="points"),
            ha="left", va="center", fontsize=size)


def broken(t, y, gap=GAP_BREAK):
    """Insert nan where consecutive points are further apart than gap in time."""
    if len(t) < 2:
        return t, y
    k = np.where(np.diff(t) > gap)[0] + 1
    return np.insert(t, k, np.nan), np.insert(y, k, np.nan)


def found(d, m, lab):
    M = d[f"m{m}_ah{lab}_M"]
    ok = np.isfinite(M)
    return d[f"m{m}_ah{lab}_t"][ok], M[ok], d[f"m{m}_ah{lab}_S"][ok]


def orbit(a_d, a_p, d, xmax):
    """Top strip: coordinate separation of the trackers; bottom strip: orbital phase
    (angle of the line from A to B about the z axis, in turns)."""
    pmax = 0.05
    for m in ("64", "128"):
        t = d[f"m{m}_pos_t"]
        if len(t) == 0:
            continue
        sep = d[f"m{m}_pos_sep"].copy()
        # the code joins the two trackers into one point after the merger: the separation
        # is drawn up to the first record with coincident trackers, not along the axis
        z0 = np.where(np.isfinite(sep) & (sep < 1e-9) & (t > float(d[f"m{m}_t_switch"])))[0]
        if len(z0):
            sep[z0[0] + 1:] = np.nan
        # the phase is defined while the black holes are apart (nan: gap in the record)
        phi = np.where(sep > SEP_MIN, d[f"m{m}_pos_phi"], np.nan) / (2 * np.pi)
        a_d.plot(t, sep, color="k", **MESH[m])
        a_p.plot(t, phi, color="k", **MESH[m])
        if np.isfinite(phi).any():
            pmax = max(pmax, float(np.nanmax(phi)))
        # dots: positions stored with the restart dumps, where the record is built on them,
        # while the trackers are apart
        ta, ka = d[f"m{m}_anc_t"], d[f"m{m}_anc_kind"]
        dx = d[f"m{m}_anc_B"] - d[f"m{m}_anc_A"]
        sa = np.sqrt((dx ** 2).sum(1))
        sel = (ka == 0) & (ta >= float(d[f"m{m}_t_switch"]) - 1e-9) & (sa > SEP_MIN)
        mk = DOT[m]
        a_d.plot(ta[sel], sa[sel], **mk)
        a_p.plot(ta[sel], np.interp(ta[sel], t[np.isfinite(phi)], phi[np.isfinite(phi)]),
                 **mk)
    a_d.set_ylim(0, 7.5)
    a_d.set_yticks((3, 6))
    a_d.set_ylabel(r"$d/M$")
    a_d.text(0.04 * xmax, 3.9, "separation", fontsize=LAB_PT, ha="left", va="top")
    step = 0.05 if pmax < 0.5 else (0.5 if pmax < 5 else 5.0)
    top = step * np.ceil(pmax / 0.8 / step)
    a_p.set_ylim(0, top)
    # ticks below the top edge, clear of the labels of the strip above
    tv = matplotlib.ticker.MaxNLocator(3, steps=(1, 2, 2.5, 5, 10)).tick_values(0, 0.8 * top)
    a_p.set_yticks([v for v in tv if 0 <= v <= 0.8 * top + 1e-12])
    a_p.set_ylabel(r"$\varphi/2\pi$")
    a_p.text(0.04, 0.93, "orbital phase", transform=a_p.transAxes,
             fontsize=LAB_PT, ha="left", va="top")
    tm = float(d["orig_t_common"])
    for ax in (a_d, a_p):
        ax.set_xlim(0, xmax)
        if tm <= xmax:
            tick(ax, tm, "original\nmerger" if ax is a_d else None,
                 side="right" if xmax - tm > 0.3 * xmax else "left")
    a_d.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())


def masses(ax, d, xmax):
    ymax = 0.0
    for m in ("64", "128"):
        for lab in "ABC":
            t, M, _ = found(d, m, lab)
            if len(t) == 0:
                continue
            ax.plot(*broken(t, M), color=COL[lab], **MESH[m])
            ymax = max(ymax, M.max())
    # original values inside the time range
    to, Mo = d["orig_t_M"], d["orig_M"]
    for k, (t, M) in enumerate(zip(to, Mo)):
        if t <= xmax:
            ax.plot(t, M, **ORIG_KW)
            ymax = max(ymax, M)
    for t, M in ((d["orig_t_common"], d["orig_M_common"]),
                 (d["orig_t_final"], d["orig_M_final"])):
        if float(t) <= xmax:
            ax.plot(float(t), float(M), **ORIG_KW)
            ymax = max(ymax, float(M))
    x0 = 8.0
    ax.set_xlim(x0, xmax)
    for k, t in enumerate(d["orig_t_first"]):
        tick(ax, float(t), "original" if k == 1 else None, side="right")
    ax.set_ylim(0, 1.15 * ymax if ymax > 0 else 0.2)
    if ymax > 0.8:                      # reference: the total (ADM) mass of the data
        ax.axhline(1.0, color="0.55", lw=0.7, ls=(0, (1, 1.5)), zorder=1)
        ax.text(x0 + 0.22 * (xmax - x0), 0.985, "total mass", color="0.4", fontsize=LAB_PT,
                ha="left", va="top")
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
    ax.set_ylabel(r"$M_{\rm AH}/M$")
    # label A, B at the end of the M/64 curves
    t, M, _ = found(d, "64", "A")
    if len(t):
        ab_label(ax, t[-1] - 0.16 * (xmax - x0), M[-1] + 0.07 * ax.get_ylim()[1])
    t, M, _ = found(d, "64", "C")
    if len(t):
        ax.text(t[0] - 0.03 * (xmax - x0), M[0], "common", fontsize=LAB_PT,
                ha="right", va="center")


def fractions(ax, d, xmax):
    for m in ("64", "128"):
        t, n = d[f"m{m}_snap_t"], d[f"m{m}_snap_n"]
        if len(t) == 0:
            continue
        f = n / n[0]
        for s, lab in enumerate(("env", "A", "B")):
            ax.plot(t, f[:, s], color=COL[lab], **MESH[m])
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, 1.12)
    ax.set_yticks((0, 0.5, 1))
    ax.set_ylabel("fraction remaining")
    ax.text(0.04 * xmax, 1.03, "envelope", color="0.4", fontsize=LAB_PT, ha="left",
            va="bottom")
    # 'A, B' to the right of the drop of the M/64 curves, at half height
    t, n = d["m64_snap_t"], d["m64_snap_n"]
    f = n[:, 1] / n[0, 1]
    k = int(np.argmax(f < 0.5)) if (f < 0.5).any() else len(t) - 1
    ab_label(ax, t[k] + 0.04 * xmax, 0.5)
    # spin of the common horizon, once found
    tc, Mc, Sc = found(d, "64", "C")
    t2, M2, S2 = found(d, "128", "C")
    # legend in the empty area: right middle, or low centre once the spin is drawn
    spin = bool(len(tc) or len(t2))
    ax.legend([Line2D([], [], color="k", **MESH["64"]), Line2D([], [], color="k", **MESH["128"])],
              [r"$\Delta x=M/64$", r"$\Delta x=M/128$"], frameon=False, fontsize=LAB_PT,
              handlelength=2.2, borderaxespad=0.3,
              **(dict(loc="lower center", bbox_to_anchor=(0.56, 0.05)) if spin else
                 dict(loc="center right", bbox_to_anchor=(1.0, 0.36))))
    if len(tc) or len(t2):
        axr = ax.twinx()
        for m, (t, M, S) in (("64", (tc, Mc, Sc)), ("128", (t2, M2, S2))):
            if len(t):
                axr.plot(*broken(t, S / M ** 2), color=COL["C"], **MESH[m])
        for t, c in ((d["orig_t_common"], d["orig_chi_common"]),
                     (d["orig_t_final"], d["orig_chi_final"])):
            if float(t) <= xmax:
                axr.plot(float(t), float(c), **ORIG_KW)
        axr.set_ylim(0, 1.12)
        axr.set_yticks((0, 0.5, 1))
        axr.set_ylabel(r"$S/M_{\rm AH}^2$", labelpad=2)
        ax.tick_params(axis="y", which="both", right=False)
        t = tc if len(tc) else t2
        chi = (Sc / Mc ** 2) if len(tc) else (S2 / M2 ** 2)
        # above and to the left of the start of the curve, clear of the original's marker,
        # the 'A, B' label and the legend
        axr.text(t[0] - 0.01 * xmax, chi[0] + 0.06, "spin of\ncommon\nhorizon", fontsize=LAB_PT,
                 ha="right", va="bottom", linespacing=1.0)
        return axr
    return None


def make():
    fs.use_style()
    d = np.load(DATA)
    xmax = x_end(d)
    spin_axis = bool(np.isfinite(d["m64_ahC_M"]).any() or np.isfinite(d["m128_ahC_M"]).any())
    # ---- geometry (inches) ----
    left_t, gap_t, right_t = 0.30, 0.06, 0.04
    P = (W - left_t - right_t - 3 * gap_t) / 4
    bot, hb, gap_rows, top = 0.40, 1.60, 0.50, 0.04
    Hfig = bot + hb + gap_rows + P + top
    fig = plt.figure(figsize=(W, Hfig))
    y_top = bot + hb + gap_rows
    snaps = [fs.inch_axes(fig, left_t + j * (P + gap_t), y_top, P, P) for j in range(4)]
    left_b, right_b = 0.55, (0.55 if spin_axis else 0.08)
    gap_b = 0.62
    w = (W - left_b - right_b - 2 * gap_b) / 3
    hs = (hb - 0.06) / 2
    a_d = fs.inch_axes(fig, left_b, bot + hs + 0.06, w, hs)
    a_p = fs.inch_axes(fig, left_b, bot, w, hs)
    a_m = fs.inch_axes(fig, left_b + w + gap_b, bot, w, hb)
    a_f = fs.inch_axes(fig, left_b + 2 * (w + gap_b), bot, w, hb)

    snapshots(snaps, d)
    orbit(a_d, a_p, d, xmax)
    masses(a_m, d, xmax)
    fractions(a_f, d, xmax)
    for ax in (a_d, a_p, a_m, a_f):
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4, steps=(1, 2, 2.5, 5, 10)))
    for ax in (a_p, a_m, a_f):
        ax.set_xlabel(r"$t/M$", labelpad=1)
    for ax in (a_d, a_p):
        ax.yaxis.set_label_coords(-0.42 / w, 0.5)
    return fig


if __name__ == "__main__":
    fig = make()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("\n".join(fs.save(fig, str(OUT))))
