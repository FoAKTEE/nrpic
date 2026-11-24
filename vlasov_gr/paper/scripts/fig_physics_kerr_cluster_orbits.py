#!/usr/bin/env python3
"""Publication figure: Relativistic Kerr e=0.99 zoom orbit, Z4c head-on merger tracers,
and N=10^5 6-level SMR Kerr cluster phase-mixing & invariant conservation."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Circle

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
D = np.load(os.path.join(PAPER_DIR, "data/physics_kerr_cluster.npz"))
OUT = os.path.join(PAPER_DIR, "figures/fig_physics_kerr_cluster_orbits")


def main():
    cz.use_style()
    W = 7.2
    fig = plt.figure(figsize=(W, 4.70))

    # Top row: 4 equal square panels with clean non-overlapping tick layout
    left_t, gap_01, gap_12, gap_23, right_t = 0.56, 0.36, 0.36, 0.10, 0.08
    P = (W - left_t - right_t - gap_01 - gap_12 - gap_23) / 4.0
    bot, hb, gap_y = 0.44, 1.66, 0.52
    y_top = bot + hb + gap_y

    x_top = [
        left_t,
        left_t + P + gap_01,
        left_t + 2 * P + gap_01 + gap_12,
        left_t + 3 * P + gap_01 + gap_12 + gap_23,
    ]

    a_spin = 0.9
    r_hor = np.sqrt((1.0 + np.sqrt(1.0 - a_spin * a_spin)) ** 2 + a_spin * a_spin)

    # Panel T0: Kerr e=0.99 trajectory in equatorial projection (exact square box)
    ax = cz.inch_axes(fig, x_top[0], y_top, P, P)
    xy_g = D["cks_gl4_xy"]
    xy_m = D["cks_mid_xy"]
    ax.plot(xy_m[:, 0], xy_m[:, 1], "--", lw=1.0, color="0.55", label="Midpoint")
    ax.plot(xy_g[:, 0], xy_g[:, 1], "-", lw=1.35, color=cz.PAL["red"], label="GL4")
    ax.add_patch(Circle((0.0, 0.0), r_hor, color="k", zorder=4))
    ax.add_patch(Circle((0.0, 0.0), 2.0, fill=False, ls=":", color="0.45", lw=0.8, zorder=3))
    ax.plot(xy_g[-1, 0], xy_g[-1, 1], "o", ms=3.5, color=cz.PAL["red"], zorder=5)
    ax.plot(xy_m[-1, 0], xy_m[-1, 1], "s", ms=3.2, mfc="white", mec="0.35", zorder=5)
    ax.set_xlim(-22.0, 22.0)
    ax.set_ylim(-22.0, 22.0)
    ax.set_aspect("equal")
    ax.set_xticks([-15, 0, 15])
    ax.set_yticks([-15, 0, 15])
    ax.set_xlabel(r"$x/M$", labelpad=1)
    ax.set_ylabel(r"$y/M$", labelpad=2)
    ax.text(0.06, 0.94, r"Kerr $e=0.99$", transform=ax.transAxes, ha="left", va="top", fontsize=7.5)
    ax.legend(loc="lower right", fontsize=6.0, frameon=False, handlelength=1.2)

    # Panel T1: Dynamic Z4c binary head-on merger & tracer orbits
    ax = cz.inch_axes(fig, x_top[1], y_top, P, P)
    c0, c1 = D["ho_co0_x"], D["ho_co1_x"]
    ax.plot(c0[:, 0], c0[:, 1], "-", lw=1.8, color="k", label="BH punctures")
    ax.plot(c1[:, 0], c1[:, 1], "-", lw=1.8, color="k")
    ax.plot([c0[0, 0], c1[0, 0]], [0.0, 0.0], "ko", ms=3.2, zorder=5)
    r_ah_fin = float(D["ho_ah_rfin"])
    ax.add_patch(Circle((0.0, 0.0), r_ah_fin, color="k", alpha=0.85, zorder=4))
    cols_tr = [cz.PAL["blue"], cz.PAL["green"], cz.PAL["orange"], cz.PAL["red"], "#8E44AD"]
    for k, col in zip((0, 1, 2, 3, 4), cols_tr):
        xk = D[f"ho_tr{k}_x"]
        ax.plot(xk[:, 0], xk[:, 1], "-", lw=1.0, color=col)
    ax.set_xlim(-12.5, 12.5)
    ax.set_ylim(-12.5, 12.5)
    ax.set_aspect("equal")
    ax.set_xticks([-10, 0, 10])
    ax.set_yticks([-10, 0, 10])
    ax.set_xlabel(r"$x/M$", labelpad=1)
    ax.text(0.06, 0.94, "Head-on merger", transform=ax.transAxes, ha="left", va="top", fontsize=7.5)
    ax.legend(loc="lower left", fontsize=6.0, frameon=False, handlelength=1.2)

    # Panels T2 & T3: M4 N=10^5 6-level SMR Kerr cluster phase mixing (t=0 vs t=200M)
    for idx_p, (key, tlbl) in enumerate((("m4_xy_t0", r"Cluster $t=0$"), ("m4_xy_t200", r"Cluster $t=200\,M$"))):
        ax = cz.inch_axes(fig, x_top[2 + idx_p], y_top, P, P)
        xy = D[key]
        ax.scatter(xy[:, 0], xy[:, 1], s=0.10, lw=0, color=cz.PAL["red"], alpha=0.55, rasterized=True)
        ax.add_patch(Circle((0.0, 0.0), r_hor, color="k", zorder=4))
        ax.set_xlim(-22.0, 22.0)
        ax.set_ylim(-22.0, 22.0)
        ax.set_aspect("equal")
        ax.set_xticks([-15, 0, 15])
        ax.set_yticks([-15, 0, 15])
        if idx_p == 1:
            ax.yaxis.set_major_formatter(mticker.NullFormatter())
        ax.set_xlabel(r"$x/M$", labelpad=1)
        ax.text(0.06, 0.94, tlbl, transform=ax.transAxes, ha="left", va="top", fontsize=7.5)

    # Bottom row: 3 wide panels with generous left/inter-panel margins
    left_b, gap_b, right_b = 0.68, 0.72, 0.12
    wb = (W - left_b - right_b - 2 * gap_b) / 3.0
    ax0 = cz.inch_axes(fig, left_b, bot, wb, hb)
    ax1 = cz.inch_axes(fig, left_b + wb + gap_b, bot, wb, hb)
    ax2 = cz.inch_axes(fig, left_b + 2 * (wb + gap_b), bot, wb, hb)

    # Bottom-Left: M1 periastron passage |dE/E_0| vs time
    s = slice(1, None)
    ax0.plot(D["cks_mid_t"][s], np.maximum(D["cks_mid_dE"][s], 1e-16), "--", lw=1.15, color=cz.PAL["blue"], label="CKS Mid")
    ax0.plot(D["cks_gl4_t"][s], np.maximum(D["cks_gl4_dE"][s], 1e-16), "-", lw=1.45, color=cz.PAL["red"], label="CKS GL4")
    ax0.plot(D["lat_mid_t"][s], np.maximum(D["lat_mid_dE"][s], 1e-16), "--", lw=1.05, color="0.45", label="Lat Mid")
    ax0.plot(D["lat_gl4_t"][s], np.maximum(D["lat_gl4_dE"][s], 1e-16), "-", lw=1.2, color=cz.PAL["green"], label="Lat GL4")
    ax0.axvline(93.0, ymax=0.72, ls=":", color="0.3", lw=0.9)
    ax0.text(97.0, 4e-15, "periapse", fontsize=6.5, color="0.3", ha="left")
    ax0.set_yscale("log")
    ax0.set_xlim(0, 230)
    ax0.set_xticks([0, 100, 200])
    ax0.set_ylim(1e-16, 6e-3)
    ax0.set_yticks([1e-15, 1e-11, 1e-7, 1e-3])
    cz.no_minor_labels(ax0, "y")
    ax0.set_xlabel(r"$t/M$", labelpad=2)
    ax0.set_ylabel(r"Relative $|\Delta E/E_0|$", labelpad=3)
    ax0.legend(loc="upper left", ncol=2, fontsize=5.8, frameon=False, columnspacing=0.6, handlelength=1.2, labelspacing=0.2)

    # Bottom-Middle: Z4c head-on merger tracer axisymmetry conservation |dL_x|
    for idx_t, col, lbl in ((0, cz.PAL["blue"], "tracer 0"), (1, cz.PAL["green"], "tracer 1"), (2, cz.PAL["red"], "tracer 2")):
        tg = D[f"ho_gl4_tr{idx_t}_t"][1:]
        dg = np.maximum(D[f"ho_gl4_tr{idx_t}_dLx"][1:], 1e-12)
        ax1.plot(tg, dg, "-", lw=1.3, color=col, label=lbl)
    t_ah = float(D["ho_ah_t"][0])
    ax1.axvline(t_ah, ls="--", color="k", lw=0.9)
    ax1.text(t_ah + 3.0, 2.5e-8, "common\nAH", fontsize=6.3, ha="left", va="bottom", linespacing=0.95)
    ax1.set_yscale("log")
    ax1.set_xlim(0, 100)
    ax1.set_xticks([0, 50, 100])
    ax1.set_ylim(1e-8, 2e-3)
    ax1.set_yticks([1e-7, 1e-5, 1e-3])
    cz.no_minor_labels(ax1, "y")
    ax1.set_xlabel(r"$t/M$", labelpad=2)
    ax1.set_ylabel(r"$|\Delta L_x / L_{x,0}|$", labelpad=3)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.08, 0.02), fontsize=5.9, frameon=False, handlelength=1.2, labelspacing=0.20)

    # Bottom-Right: M4 N=10^5 Kerr cluster energy-error CDFs at t=200M
    q = D["cdf_q"]
    ax2.plot(D["cdf_ana_100k_gl4_dE"], q, "-", lw=1.5, color=cz.PAL["red"], label="Analytic GL4")
    ax2.plot(D["cdf_ana_100k_mid_dE"], q, "--", lw=1.3, color=cz.PAL["blue"], label="Analytic Mid")
    ax2.plot(D["cdf_mesh_100k_gl4_dE"], q, "-", lw=1.5, color=cz.PAL["green"], label="6-lvl SMR GL4")
    ax2.plot(D["cdf_mesh_100k_mid_dE"], q, ":", lw=1.4, color="0.35", label="6-lvl SMR Mid")
    ax2.set_xscale("log")
    ax2.set_xlim(1e-17, 1e-3)
    ax2.set_xticks([1e-16, 1e-12, 1e-8, 1e-4])
    cz.no_minor_labels(ax2, "x")
    ax2.set_ylim(0, 1.0)
    ax2.set_yticks([0.0, 0.5, 1.0])
    ax2.set_xlabel(r"$|\Delta E/E_0|$ at $t=200\,M$", labelpad=2)
    ax2.set_ylabel("Empirical CDF", labelpad=3)
    ax2.legend(loc="upper left", fontsize=6.0, frameon=False, handlelength=1.3, labelspacing=0.22)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
