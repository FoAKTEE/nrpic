#!/usr/bin/env python3
"""Illustrative methodology diagram: curved AMR refluxing filter, causal (d0, d1) coupling, and back-reaction."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG_OUT = HERE.parent / "figures" / "fig_method_backreaction"
INK = "0.15"


def tint(color: str, f: float):
    c = to_rgb(color)
    return tuple(1.0 - f * (1.0 - x) for x in c)


def draw_box(ax, x, y, w, h, title, sub, color, fs=6.8):
    ax.add_patch(
        FancyBboxPatch(
            (x - 0.5 * w, y - 0.5 * h),
            w,
            h,
            boxstyle="round,pad=0,rounding_size=0.10",
            fc=tint(color, 0.13),
            ec=color,
            lw=1.0,
            zorder=2,
        )
    )
    ax.text(x, y + 0.19 * h, title, ha="center", va="center", fontsize=fs + 0.4,
            color=color, weight="bold", zorder=3)
    ax.text(x, y - 0.19 * h, sub, ha="center", va="center", fontsize=fs,
            color=INK, zorder=3)


def make():
    cz.use_style()
    blue, red, green, orange = cz.PAL["blue"], cz.PAL["red"], cz.PAL["green"], cz.PAL["orange"]

    fig = plt.figure(figsize=(8.0, 5.15))
    ax_amr = cz.inch_axes(fig, 0.34, 0.50, 3.35, 4.25)
    ax_caus = cz.inch_axes(fig, 4.46, 2.86, 3.32, 1.90)
    ax_loop = cz.inch_axes(fig, 4.18, 0.24, 3.74, 1.92)

    # ------------------------------------------------------------------
    # Left: 2D AMR B-spline deposition + unsplit harmonic refluxing filter
    # ------------------------------------------------------------------
    ax = ax_amr
    # Subtle pale blue-slate metric background representing sqrt(gamma) near a puncture at (1.5, 2.0)
    gx = np.linspace(0.0, 4.0, 160)
    gy = np.linspace(0.0, 4.0, 160)
    GX, GY = np.meshgrid(gx, gy)
    rr = np.sqrt((GX - 1.4) ** 2 + (GY - 2.0) ** 2 + 0.55 ** 2)
    sdet = (1.0 + 0.45 / rr) ** 3
    cmap = LinearSegmentedColormap.from_list("metric_bg", ["white", tint(blue, 0.28), tint(blue, 0.55)])
    ax.pcolormesh(GX, GY, sdet, cmap=cmap, shading="auto", rasterized=True, zorder=0)

    # Quadtree lines: coarse level l on x<2 (h=1.0), fine level l+1 on x>=2 (h=0.5)
    for xv in (0.0, 1.0, 2.0):
        ax.plot([xv, xv], [0.0, 4.0], color="0.50", lw=0.6, zorder=1)
    for yv in np.arange(0.0, 4.01, 1.0):
        ax.plot([0.0, 2.0], [yv, yv], color="0.50", lw=0.6, zorder=1)
    for xv in np.arange(2.0, 4.01, 0.5):
        ax.plot([xv, xv], [0.0, 4.0], color="0.50", lw=0.55, zorder=1)
    for yv in np.arange(0.0, 4.01, 0.5):
        ax.plot([2.0, 4.0], [yv, yv], color="0.50", lw=0.55, zorder=1)
    # Refinement jump border
    ax.plot([2.0, 2.0], [0.0, 4.0], color="0.15", lw=1.4, zorder=2)

    # Upper half: Particle straddling x=2 with virtual B-spline stencil
    xp, yp = 1.90, 2.95
    ax.plot(xp, yp, "o", color=red, ms=5.0, zorder=5)
    # Virtual fine stencil outline around (xp, yp)
    ax.add_patch(Rectangle((1.50, 2.50), 1.0, 1.0, fc="none", ec=red, lw=1.2, ls="--", zorder=4))
    ax.add_patch(Rectangle((1.00, 2.00), 1.0, 1.0, fc=tint(red, 0.16), ec=red, lw=0.9, zorder=3))
    ax.add_patch(Rectangle((1.05, 3.63), 1.90, 0.28, fc="white", ec="none", alpha=0.88, zorder=5))
    ax.text(2.0, 3.77, r"Deposition: $\sum_C \omega_{Cp} = 1$", ha="center", va="center",
            fontsize=7.3, color=red, weight="bold", zorder=6)
    ax.text(0.50, 3.35, r"level $\ell$", ha="center", va="center", fontsize=7.4, color="0.25", zorder=6)
    ax.text(3.38, 3.35, r"level $\ell{+}1$", ha="center", va="center", fontsize=7.4, color="0.25", zorder=6)
    ax.text(1.50, 2.34, r"$\sum_{q\subset C} \tilde{\omega}_{qp}$", ha="center", va="center",
            fontsize=7.2, color=red, zorder=6)

    # Lower half: Unsplit harmonic stencil & skipped vacuum block + boundary reflux
    # Masked inactive exterior cells (right corner)
    ax.add_patch(Rectangle((3.0, 0.0), 1.0, 1.5, fc="0.86", ec="0.55", lw=0.8, hatch="///", alpha=0.85, zorder=3))
    ax.text(3.50, 0.75, "Skipped\nvacuum", ha="center", va="center", fontsize=7.0, color="0.25", zorder=5)

    # Active 5-point slice centered at (2.25, 0.75)
    for dx, dy in ((0.0, 0.0), (-0.5, 0.0), (0.5, 0.0), (0.0, -0.5), (0.0, 0.5)):
        ax.add_patch(Rectangle((2.0 + dx, 0.5 + dy), 0.5, 0.5, fc=tint(green, 0.25), ec=green, lw=1.1, zorder=4))
    ax.text(2.25, 0.75, r"$c$", ha="center", va="center", fontsize=7.5, color=green, weight="bold", zorder=6)
    # Boundary-only reflux arrows across x=2 face for y in [0, 1]
    for fy in (0.25, 0.75):
        ax.add_patch(FancyArrowPatch((2.15, fy), (1.78, fy),
                                     arrowstyle="-|>,head_length=4.0,head_width=2.0",
                                     lw=1.1, color=blue, zorder=6))
    ax.text(0.76, 1.42, "Unsplit filter", ha="center", va="center",
            fontsize=7.4, color=green, weight="bold", zorder=6)
    ax.text(0.76, 0.96, r"$\sigma_{c+1/2}=\frac{2\sqrt{\gamma}_c\sqrt{\gamma}_{c+1}}{\sqrt{\gamma}_c+\sqrt{\gamma}_{c+1}}$",
            ha="center", va="center", fontsize=6.7, color=INK, zorder=6)
    ax.text(0.86, 0.34, r"Reflux: $F_C\Delta A_C = \sum_{f\subset C} F_f\Delta A_f$",
            ha="center", va="center", fontsize=6.5, color=blue, zorder=6)

    ax.set_xlim(0.0, 4.0)
    ax.set_ylim(0.0, 4.0)
    ax.set_aspect("equal")
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.tick_params(axis="both", which="minor", bottom=False, top=False, left=False, right=False)
    ax.set_xlabel(r"Coordinate $x / \Delta x_\ell$ (shaded by $\sqrt{\gamma}$)", labelpad=3, fontsize=8.6)
    ax.set_ylabel(r"Coordinate $y / \Delta x_\ell$", fontsize=8.6)
    ax.set_title("Conservative AMR & boundary refluxing", fontsize=9.8, pad=6)

    # ------------------------------------------------------------------
    # Top-Right: Causal (d0, d1) stage coupling & multi-rate subcycling
    # ------------------------------------------------------------------
    ax = ax_caus
    t_arr = np.linspace(-1.0, 1.0, 200)
    u_true = 0.25 + 0.42 * (t_arr + 1.0) + 0.14 * ((t_arr + 1.0) ** 2)
    u_m1 = u_true[0]       # t = -1 (t^{n-s_m})
    u_0 = u_true[100]      # t =  0 (t^n)
    slope = u_0 - u_m1     # d1 per macro-step

    # Baseline frozen-Tmunu staircase on [0, 1]
    ax.plot(t_arr, u_true, "k-", lw=1.35, label=r"Exact $U_{\rm den}(t)$")
    ax.plot([0.0, 1.0], [u_0, u_0], "--", color=blue, lw=1.5, label=r"Frozen $T_{\mu\nu}$ (lag $\mathcal{O}(\Delta t)$)")

    # Causal linear extrapolation across s_m = 2 Z4c substeps in [0, 1]
    t_ext = np.linspace(0.0, 1.0, 80)
    d_caus = u_0 + slope * t_ext
    ax.plot(t_ext, d_caus, "-", color=red, lw=1.6, label=r"Causal $(d_0,d_1)$, $s_{\rm m}=2$")

    # Show SSP-RK3 stage abscissae c_s in {0, 1, 0.5} for substep 1 [0, 0.5] and substep 2 [0.5, 1.0]
    for s_idx, t0 in enumerate((0.0, 0.5)):
        ax.axvline(t0, color="0.65", lw=0.75, ls=":")
        for cs in (0.0, 0.5, 1.0):
            ts = t0 + 0.5 * cs
            ax.plot(ts, u_0 + slope * ts, "o", color=red, ms=4.0, zorder=5)
    ax.text(0.25, 0.55, "substep 1", ha="center", va="center", fontsize=7.0, color="0.35")
    ax.text(0.75, 0.55, "substep 2", ha="center", va="center", fontsize=7.0, color="0.35")

    ax.annotate("", xy=(0.88, u_true[188]), xytext=(0.88, u_0),
                arrowprops=dict(arrowstyle="<->", color=blue, lw=0.9))
    ax.text(0.84, 0.99, r"$\mathcal{O}(\Delta t)$" "\nlag",
            ha="right", va="center", fontsize=6.9, color=blue)

    ax.set_xlim(-1.02, 1.05)
    ax.set_ylim(0.18, 1.98)
    ax.set_xticks([-1.0, 0.0, 0.5, 1.0])
    ax.set_xticklabels([r"$t^{n-s_{\rm m}}$", r"$t^n$", r"$t^{n+1}$", r"$t^{n+2}$"], fontsize=8.0)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlabel(r"Multi-rate subcycle time ($s_{\rm m}=2$)", labelpad=3, fontsize=8.6)
    ax.set_ylabel(r"Densitized source $D^{(s)}$", fontsize=8.6)
    ax.legend(loc="upper left", fontsize=7.2, frameon=False)
    ax.set_title(r"Causal stage source & multi-rate subcycling", fontsize=9.8, pad=6)

    # ------------------------------------------------------------------
    # Bottom-Right: Self-gravitating puncture-split back-reaction cycle
    # ------------------------------------------------------------------
    ax = ax_loop
    ax.set_xlim(0.0, 10.0)
    ax.set_ylim(0.0, 4.6)
    ax.axis("off")
    ax.set_title("Puncture-split back-reaction coupling", fontsize=9.8, pad=2)

    draw_box(ax, 2.35, 3.25, 4.35, 1.38,
             "Puncture-split constraints",
             r"$\psi=\psi_s+u$,\; $\bar{A}_{ij}=\bar{A}_{ij}^{\rm BY}+(\mathbb{L}W)_{ij}$", blue, fs=6.4)
    draw_box(ax, 7.65, 3.25, 4.35, 1.38,
             r"Harmonic $T_{\mu\nu}$ + $(d_0,d_1)$",
             r"Flux refluxing & causal stages", green, fs=6.4)
    draw_box(ax, 7.65, 0.92, 4.35, 1.38,
             "Coupled Z4c + GL4",
             r"Self-force plunge & recoil $\mathbf{x}_{\rm BH}(t)$", red, fs=6.4)
    draw_box(ax, 2.35, 0.92, 4.35, 1.38,
             "Horizons & radiation",
             r"FastFlow $(M_{\rm AH},\chi_{\rm AH})$, $r\Psi_4^{22}$", orange, fs=6.4)

    # Loop arrows clockwise
    ax.add_patch(FancyArrowPatch((4.53, 3.25), (5.47, 3.25),
                                 arrowstyle="-|>,head_length=4.5,head_width=2.3", lw=1.05, color=INK))
    ax.add_patch(FancyArrowPatch((7.65, 2.55), (7.65, 1.62),
                                 arrowstyle="-|>,head_length=4.5,head_width=2.3", lw=1.05, color=INK))
    ax.add_patch(FancyArrowPatch((5.47, 0.92), (4.53, 0.92),
                                 arrowstyle="-|>,head_length=4.5,head_width=2.3", lw=1.05, color=INK))
    ax.add_patch(FancyArrowPatch((2.35, 1.62), (2.35, 2.55), ls="--",
                                 arrowstyle="-|>,head_length=4.5,head_width=2.3", lw=1.0, color="0.45"))

    return fig


if __name__ == "__main__":
    fig = make()
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    print(f"Saved {FIG_OUT}.{{pdf,png}}")
