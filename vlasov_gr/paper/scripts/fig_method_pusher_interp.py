#!/usr/bin/env python3
"""Illustrative methodology diagram: geodesic pushers, 3-level time blending, and C2 quintic Hermite."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
FIG_OUT = HERE.parent / "figures" / "fig_method_pusher_interp"
INK = "0.15"


def tint(color: str, f: float):
    c = to_rgb(color)
    return tuple(1.0 - f * (1.0 - x) for x in c)


def draw_flow_box(ax, x, y, w, h, text, color, fs=7.2, bold=False):
    ax.add_patch(
        FancyBboxPatch(
            (x - 0.5 * w, y - 0.5 * h),
            w,
            h,
            boxstyle="round,pad=0,rounding_size=0.10",
            fc=tint(color, 0.12),
            ec=color,
            lw=1.0,
            zorder=2,
        )
    )
    ax.text(
        x, y, text, ha="center", va="center", fontsize=fs,
        color=INK if not bold else color, weight="bold" if bold else "normal",
        linespacing=1.12, zorder=3,
    )


def draw_arrow(ax, x0, y0, x1, y1, color=INK):
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0), (x1, y1),
            arrowstyle="-|>,head_length=4.2,head_width=2.2",
            lw=0.95, color=color, shrinkA=1.5, shrinkB=1.5, zorder=2,
        )
    )


def eval_cubic_hermite(f_nodes, i0, s_arr, h):
    """Evaluate cubic Hermite f, f', f'' on cell [i0, i0+1]."""
    fm1, f0, f1, f2 = f_nodes[i0 - 1], f_nodes[i0], f_nodes[i0 + 1], f_nodes[i0 + 2]
    # Second derivative weights w_a''(s) / h^2
    wpp_m1 = (4.0 - 6.0 * s_arr) / 2.0
    wpp_0 = (-10.0 + 18.0 * s_arr) / 2.0
    wpp_1 = (8.0 - 18.0 * s_arr) / 2.0
    wpp_2 = (-2.0 + 6.0 * s_arr) / 2.0
    return wpp_m1 * fm1 + wpp_0 * f0 + wpp_1 * f1 + wpp_2 * f2


def eval_quintic_hermite_second(f_nodes, i0, s_arr):
    """Evaluate h^2 f''(s) of the C2 6-node quintic Hermite interpolant on [i0, i0+1]."""
    fm2, fm1, f0, f1, f2, f3 = [f_nodes[i0 + a] for a in (-2, -1, 0, 1, 2, 3)]
    s = s_arr
    # Second derivatives H_ab''(s)
    H00pp = -60.0 * s + 180.0 * s**2 - 120.0 * s**3
    H01pp = -H00pp
    H10pp = -36.0 * s + 96.0 * s**2 - 60.0 * s**3
    H11pp = -24.0 * s + 84.0 * s**2 - 60.0 * s**3
    H20pp = 1.0 - 9.0 * s + 18.0 * s**2 - 10.0 * s**3
    H21pp = 3.0 * s - 12.0 * s**2 + 10.0 * s**3

    wpp_m2 = (H10pp - H20pp) / 12.0
    wpp_m1 = (-8.0 * H10pp + H11pp + 16.0 * H20pp - H21pp) / 12.0
    wpp_0 = H00pp + (-8.0 * H11pp - 30.0 * H20pp + 16.0 * H21pp) / 12.0
    wpp_1 = H01pp + (8.0 * H10pp + 16.0 * H20pp - 30.0 * H21pp) / 12.0
    wpp_2 = (-H10pp + 8.0 * H11pp - H20pp + 16.0 * H21pp) / 12.0
    wpp_3 = (-H11pp - H21pp) / 12.0
    return wpp_m2 * fm2 + wpp_m1 * fm1 + wpp_0 * f0 + wpp_1 * f1 + wpp_2 * f2 + wpp_3 * f3


def make():
    cz.use_style()
    blue, red, orange, green = cz.PAL["blue"], cz.PAL["red"], cz.PAL["orange"], cz.PAL["green"]

    fig = plt.figure(figsize=(8.0, 5.80))
    # Generous vertical separation between top and bottom rows
    ax_arch = cz.inch_axes(fig, 0.12, 3.40, 3.72, 2.16)
    ax_time = cz.inch_axes(fig, 4.50, 3.55, 3.36, 1.98)
    ax_sten = cz.inch_axes(fig, 0.12, 0.35, 3.72, 2.15)
    ax_hess = cz.inch_axes(fig, 4.50, 0.50, 3.36, 1.98)

    # ------------------------------------------------------------------
    # Top-Left: Architectural comparison of GL4, Midpoint, Spacetime Boris
    # ------------------------------------------------------------------
    ax = ax_arch
    ax.set_xlim(0.0, 10.2)
    ax.set_ylim(0.0, 6.2)
    ax.axis("off")
    ax.set_title("Geodesic pusher architectures", fontsize=10.0, pad=6)

    # Row 1: Canonical Darboux GL4 (red)
    y1 = 5.05
    ax.text(0.08, y1 + 0.72, r"Darboux GL4 ($\varepsilon\in\{0,1\}$): symplectic $M_{rs}=0$, $\mathcal{O}(\Delta t^4)$",
            fontsize=7.2, color=red, weight="bold", ha="left", va="center")
    draw_flow_box(ax, 1.00, y1, 1.85, 0.86, r"$\mathbf{z}^n=(x^i,u_i)$", red, fs=6.9)
    draw_arrow(ax, 1.93, y1, 2.38, y1, red)
    draw_flow_box(ax, 4.58, y1, 4.35, 0.90, r"Coupled stages $\mathbf{Z}_1(c_1),\,\mathbf{Z}_2(c_2)$" "\n" r"exact $\Delta\tau$ & cyclic $u_k$", red, fs=6.7)
    draw_arrow(ax, 6.76, y1, 7.22, y1, red)
    draw_flow_box(ax, 8.66, y1, 2.82, 0.86, r"$\mathbf{z}^{n+1}$ ($C^2$ metric)", red, fs=6.9)

    # Row 2: Implicit Midpoint (blue)
    y2 = 3.00
    ax.text(0.08, y2 + 0.72, r"Implicit Midpoint: 1-stage symmetric, $\mathcal{O}(\Delta t^2)$ phase error",
            fontsize=7.2, color=blue, weight="bold", ha="left", va="center")
    draw_flow_box(ax, 1.00, y2, 1.85, 0.82, r"$\mathbf{z}^n$", blue, fs=6.9)
    draw_arrow(ax, 1.93, y2, 2.38, y2, blue)
    draw_flow_box(ax, 4.58, y2, 4.35, 0.82, r"Midpoint $\bar{\mathbf{z}} = \frac{1}{2}(\mathbf{z}^n+\mathbf{z}^{n+1})$", blue, fs=6.8)
    draw_arrow(ax, 6.76, y2, 7.22, y2, blue)
    draw_flow_box(ax, 8.66, y2, 2.82, 0.82, r"$\mathbf{z}^{n+1}$ ($\varepsilon\in\{0,1\}$)", blue, fs=6.9)

    # Row 3: Spacetime Boris (orange)
    y3 = 0.95
    ax.text(0.08, y3 + 0.72, r"Spacetime Boris ($\varepsilon=1$): spatial triad gauge, requires $\partial_t\gamma_{ij}$",
            fontsize=7.2, color=orange, weight="bold", ha="left", va="center")
    draw_flow_box(ax, 1.00, y3, 1.85, 0.86, r"$u_i^n \to u_{(m)}^n$" "\n" r"via $e^i_{(m)}$", orange, fs=6.7)
    draw_arrow(ax, 1.93, y3, 2.38, y3, orange)
    draw_flow_box(ax, 4.58, y3, 4.35, 0.86, r"Kick--rotate--kick in $(\bar{E}_{\rm tet},\bar{B}_{\rm tet})$", orange, fs=6.7)
    draw_arrow(ax, 6.76, y3, 7.22, y3, orange)
    draw_flow_box(ax, 8.66, y3, 2.82, 0.86, r"$u_{(m)}^{n+1}\to u_i^{n+1}$" "\n" r"via $e^{(m)}_i$", orange, fs=6.7)

    # ------------------------------------------------------------------
    # Top-Right: Three-level quadratic Lagrange time interpolation weights
    # ------------------------------------------------------------------
    ax = ax_time
    r = 1.4
    c_grid = np.linspace(-1.0 / r, 1.0, 260)
    w_m1 = (r**2 * c_grid * (c_grid - 1.0)) / (1.0 + r)
    w_0 = (1.0 - c_grid) * (1.0 + r * c_grid)
    w_1 = (c_grid * (1.0 + r * c_grid)) / (1.0 + r)

    c_pos = np.linspace(0.0, 1.0, 120)
    ax.plot(c_grid, w_1, "-", color=red, lw=1.6, label=r"$w_1(c)$")
    ax.plot(c_grid, w_0, "-", color=blue, lw=1.6, label=r"$w_0(c)$")
    ax.plot(c_grid, w_m1, "-", color=green, lw=1.6, label=r"$w_{-1}(c)$")
    ax.plot(c_pos, c_pos, "--", color="0.45", lw=1.1, label=r"Linear $c,\,1-c$")
    ax.plot(c_pos, 1.0 - c_pos, "--", color="0.45", lw=1.1)

    c1 = 0.5 - np.sqrt(3.0) / 6.0
    c2 = 0.5 + np.sqrt(3.0) / 6.0
    for cc, lbl in ((c1, r"$c_1$"), (c2, r"$c_2$")):
        ax.axvline(cc, color="0.25", lw=0.95, ls=":")
        ax.text(cc + 0.025, 1.04, lbl, fontsize=7.6, color="0.20", ha="left", va="center")
    ax.axhline(0.0, color="0.65", lw=0.7)
    ax.axvline(0.0, color="0.65", lw=0.7)

    ax.set_xlim(-1.0 / r - 0.05, 1.05)
    ax.set_ylim(-0.22, 1.24)
    ax.set_xticks([-1.0 / r, 0.0, 1.0])
    ax.set_xticklabels([r"$t^{n-1}$", r"$t^n$", r"$t^{n+1}$"], fontsize=8.4)
    ax.set_xlabel(r"Stage offset $c = (t - t^n)/\Delta t_n$ ($r=1.4$)", labelpad=3, fontsize=8.8)
    ax.set_ylabel("Temporal metric weight", fontsize=8.8)
    ax.legend(ncol=2, loc="upper left", fontsize=7.4, handlelength=1.4, columnspacing=0.8, frameon=False)
    ax.set_title(r"3-level $\mathcal{O}(\Delta t^3)$ metric interpolation", fontsize=10.0, pad=6)

    # ------------------------------------------------------------------
    # Bottom-Left: Zero-overhead n_g = 4 ghost-cell stencil schematic
    # ------------------------------------------------------------------
    ax = ax_sten
    ax.set_xlim(-2.6, 3.6)
    ax.set_ylim(-0.2, 4.1)
    ax.axis("off")
    ax.set_title(r"$n_g = 4$ ghost-cell stencil (block edge)", fontsize=10.0, pad=4)

    # Shaded ghost zone (i >= i0+1 right side: indices 1, 2, 3 represent edge + ghost cells)
    ax.add_patch(Rectangle((-2.45, 0.65), 3.45, 2.25, fc=tint(blue, 0.05), ec="none", zorder=0))
    ax.add_patch(Rectangle((1.00, 0.65), 2.45, 2.25, fc=tint(orange, 0.09), ec="none", zorder=0))
    ax.plot([1.00, 1.00], [0.55, 3.05], color="0.30", ls="--", lw=1.0, zorder=1)
    ax.text(-0.72, 2.66, "Interior cells", ha="center", va="center", fontsize=7.2, color=blue)
    ax.text(2.22, 2.66, r"Ghost zone ($n_g=4$)", ha="center", va="center", fontsize=7.2, color=orange)

    # Grid nodes and cell interval [i0, i0+1]
    nodes = [-2, -1, 0, 1, 2, 3]
    names = [r"$i_0{-}2$", r"$i_0{-}1$", r"$i_0$", r"$i_0{+}1$", r"$i_0{+}2$", r"$i_0{+}3$"]
    ax.plot([-2.3, 3.3], [1.75, 1.75], color="0.25", lw=1.1, zorder=1)
    ax.add_patch(Rectangle((0.0, 1.65), 1.0, 0.20, fc=tint(red, 0.28), ec=red, lw=1.0, zorder=2))
    ax.add_patch(Rectangle((0.08, 1.94), 0.84, 0.28, fc=tint(blue, 0.05), ec="none", alpha=0.95, zorder=3))
    ax.text(0.49, 2.08, r"$s \in [0, 1)$", ha="center", va="center", fontsize=7.2, color=red, zorder=4)
    for nd, nm in zip(nodes, names):
        ax.plot(nd, 1.75, "o", color="0.15", ms=5.0, zorder=3)
        if nd == 1:
            ax.add_patch(Rectangle((0.68, 1.15), 0.64, 0.34, fc="white", ec="none", alpha=0.88, zorder=3))
        ax.text(nd, 1.44, nm, ha="center", va="top", fontsize=7.2, color="0.15", zorder=4)

    # 6-node Quintic Hermite span
    ax.plot([-2.0, 3.0], [0.95, 0.95], color=red, lw=2.0)
    for xq in nodes:
        ax.plot([xq, xq], [0.87, 1.03], color=red, lw=1.2)
    ax.add_patch(Rectangle((0.86, 0.36), 0.28, 0.38, fc="white", ec="none", alpha=0.92, zorder=2))
    ax.text(0.5, 0.70, r"Quintic $C^2$ (6 nodes): matches $(f,\,f',\,f'')$ via 5-pt FD",
            ha="center", va="top", fontsize=7.0, color=red, weight="bold", zorder=4)

    # 4-node Cubic Hermite span
    ax.plot([-1.0, 2.0], [3.32, 3.32], color=blue, lw=1.8, ls="--")
    for xc in (-1, 0, 1, 2):
        ax.plot([xc, xc], [3.24, 3.40], color=blue, lw=1.2)
    ax.text(0.5, 3.55, r"Cubic $C^1$ (4 nodes): matches $(f,\,f')$ only",
            ha="center", va="bottom", fontsize=7.1, color=blue)

    # ------------------------------------------------------------------
    # Bottom-Right: Continuous vs discontinuous second derivative h^2 f''
    # ------------------------------------------------------------------
    ax = ax_hess
    h = 0.5
    def f_lapse(x):
        return (1.0 + 2.0 / x) ** (-0.5)

    def d2f_exact(x):
        u = 1.0 + 2.0 / x
        du = -2.0 / (x ** 2)
        d2u = 4.0 / (x ** 3)
        return (h ** 2) * (0.75 * (u ** (-2.5)) * (du ** 2) - 0.5 * (u ** (-1.5)) * d2u)

    # Nodes covering [2.0, 3.5] plus 2 ghost nodes on each side
    x_nodes = np.arange(1.0, 5.0 + 1e-9, h)
    f_nodes = f_lapse(x_nodes)

    s_cell = np.linspace(0.0, 1.0, 80, endpoint=True)
    x_all, q_all, c_all, ex_all = [], [], [], []
    for cell_i0 in range(2, 5):  # x = 2.0, 2.5, 3.0
        xc = x_nodes[cell_i0] + s_cell * h
        qpp = eval_quintic_hermite_second(f_nodes, cell_i0, s_cell)
        cpp = eval_cubic_hermite(f_nodes, cell_i0, s_cell, h)
        ex = d2f_exact(xc)
        x_all.append(xc)
        q_all.append(qpp)
        c_all.append(cpp)
        ex_all.append(ex)

    for xv in (2.5, 3.0):
        ax.axvline(xv, color="0.55", lw=0.85, ls=":")

    # Plot piecewise curves so jump discontinuity at cell faces renders cleanly without bogus vertical spikes
    for k in range(len(x_all)):
        ax.plot(x_all[k], ex_all[k], "k-", lw=1.4, label="Exact $h^2 f''(x)$" if k == 0 else None)
        ax.plot(x_all[k], q_all[k], "-", color=red, lw=1.6, label=r"$C^2$ Quintic Hermite" if k == 0 else None)
        ax.plot(x_all[k], c_all[k], "--", color=blue, lw=1.4, label=r"$C^1$ Cubic Hermite" if k == 0 else None)

    ax.annotate("Face jump", xy=(2.5, c_all[0][-1]), xytext=(2.62, -0.0255),
                arrowprops=dict(arrowstyle="->", color=blue, lw=0.9),
                fontsize=7.3, color=blue, ha="left", va="center")
    ax.text(3.45, -0.0080, r"Continuous $C^2$" "\n" "across faces", ha="right", va="top",
            fontsize=7.3, color=red)

    ax.set_xlim(2.0, 3.5)
    ax.set_ylim(-0.028, -0.0045)
    ax.set_xticks([2.0, 2.5, 3.0, 3.5])
    ax.set_xlabel(r"Radial coordinate $x\,[M]$ (spacing $h = 0.5\,M$)", labelpad=-1, fontsize=8.8)
    ax.set_ylabel(r"Normalized curvature $h^2 f''(x)$", fontsize=8.8)
    ax.legend(loc="lower right", fontsize=7.4, frameon=False)
    ax.set_title(r"Cell-interface Hessian continuity ($\alpha$-profile)", fontsize=10.0, pad=6)

    return fig


if __name__ == "__main__":
    fig = make()
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    print(f"Saved {FIG_OUT}.{{pdf,png}}")
