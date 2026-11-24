#!/usr/bin/env python3
"""Publication figure: Shapiro-Teukolsky relativistic cluster (r, u_r) phase-space
portraits, collapse threshold bifurcation, spurious BH spin suppression, and momentum."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LogNorm

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
D = np.load(os.path.join(PAPER_DIR, "data/physics_st_phase.npz"))
OUT = os.path.join(PAPER_DIR, "figures/fig_physics_st_phase_space")


def main():
    cz.use_style()
    W = 7.2
    fig = plt.figure(figsize=(W, 4.70))

    # Top row: 4 equal (r, u_r) phase-space density portraits sharing unified u_r scale
    left_t, gap_t, cb_w, cb_pad, right_t = 0.56, 0.14, 0.12, 0.06, 0.44
    P = (W - left_t - right_t - 3 * gap_t - cb_w - cb_pad) / 4.0
    bot, hb, gap_y = 0.44, 1.70, 0.52
    y_top = bot + hb + gap_y

    panels = [
        ("ps0", r"$y_c=0.819,\; t=0$", (0.0, 10.2), (-2.1, 2.1)),
        ("ps1", r"$y_c=0.819,\; t=300\,M$", (0.0, 10.2), (-2.1, 2.1)),
        ("ps2", r"$y_c=0.605,\; t=50\,M$", (0.0, 5.2), (-2.1, 2.1)),
        ("ps3", r"$y_c=0.605,\; t=100\,M$", (0.0, 5.2), (-2.1, 2.1)),
    ]

    mesh_ref = None
    norm = LogNorm(vmin=1.0, vmax=2.5e2)
    cmap = cz.CMAP["dens"]

    for j, (key, ttl, xlim, ylim) in enumerate(panels):
        ax = cz.inch_axes(fig, left_t + j * (P + gap_t), y_top, P, P)
        r = D[f"{key}_r"]
        ur = D[f"{key}_ur"]
        H, xe, ye = np.histogram2d(r, ur, bins=56, range=[xlim, ylim])
        H_masked = np.ma.masked_less(H.T, 1.0)
        mesh_ref = ax.pcolormesh(xe, ye, H_masked, cmap=cmap, norm=norm, shading="flat", rasterized=True)
        ax.axhline(0.0, ls=":", color="0.5", lw=0.65)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_yticks([-2, -1, 0, 1, 2])
        ax.set_xlabel(r"$r/M$", labelpad=1)
        ax.text(0.5, 1.04, ttl, transform=ax.transAxes, ha="center", va="bottom", fontsize=7.5)
        if j == 0:
            ax.set_ylabel(r"$u_r$", labelpad=2)
        else:
            ax.yaxis.set_major_formatter(mticker.NullFormatter())
        if j in (0, 1):
            ax.set_xticks([0, 4, 8])
        else:
            ax.set_xticks([0, 2, 4])

    cax = cz.inch_axes(fig, left_t + 4 * P + 3 * gap_t + cb_pad, y_top, cb_w, P)
    cb = fig.colorbar(mesh_ref, cax=cax)
    cb.set_label("Packets/bin", labelpad=3, fontsize=7.5)
    cb.set_ticks([1, 10, 100])
    cb.ax.minorticks_off()
    cb.ax.tick_params(labelsize=7.0)

    # Bottom row: 3 stability & conservation panels with ample gaps
    left_b, gap_b, right_b = 0.62, 0.72, 0.14
    wb = (W - left_b - right_b - 2 * gap_b) / 3.0
    a_lap = cz.inch_axes(fig, left_b, bot, wb, hb)
    hs = (hb - 0.08) / 2.0
    a_ahM = cz.inch_axes(fig, left_b + wb + gap_b, bot + hs + 0.08, wb, hs)
    a_ahS = cz.inch_axes(fig, left_b + wb + gap_b, bot, wb, hs)
    a_mom = cz.inch_axes(fig, left_b + 2 * (wb + gap_b), bot, wb, hb)

    # Bottom-Left: Central/min lapse bifurcation across y_c sequence
    specs = [
        ("st_yc0900_vp01_10k_hyb", cz.PAL["green"], "-", r"$y_c=0.900$"),
        ("st_yc0819_vp01_10k_anti", cz.PAL["blue"], "-", r"$y_c=0.819$ anti"),
        ("st_yc0756_dp10_10k_hyb", cz.PAL["orange"], "-", r"$y_c=0.756$ DP10"),
        ("st_yc0605_vp01_10k_hyb", cz.PAL["red"], "-", r"$y_c=0.605$ anti+GL4"),
        ("st_yc0605_vp01_10k_mid", "0.45", "--", r"$y_c=0.605$ MC+Mid"),
    ]
    a_lap.axhline(0.05, ls=":", color="k", lw=0.9)
    for run, col, ls, lbl in specs:
        a_lap.plot(D[f"{run}_t"], D[f"{run}_amin"], color=col, ls=ls, lw=1.25, label=lbl)
    a_lap.set_xlim(0, 300)
    a_lap.set_xticks([0, 100, 200])
    a_lap.set_ylim(0, 1.02)
    a_lap.set_yticks([0.0, 0.4, 0.8])
    a_lap.set_xlabel(r"$t/M$", labelpad=2)
    a_lap.set_ylabel(r"Minimum lapse $\alpha_{\min}$", labelpad=3)
    a_lap.legend(loc="lower left", bbox_to_anchor=(0.0, 0.07), fontsize=5.7, frameon=False, handlelength=1.2, labelspacing=0.18)

    # Bottom-Middle top & bottom: M_AH/M and spurious spin |a_AH| = S/M^2
    ah_specs = [
        ("st_yc0605_vp01_10k_hyb", cz.PAL["red"], "-", r"$0.605$ anti"),
        ("st_yc0605_vp01_10k_mid", "0.45", "--", r"$0.605$ MC"),
        ("st_yc0756_dp10_10k_hyb", cz.PAL["orange"], "-", r"$0.756$ anti"),
        ("st_yc0756_dp10_10k_mid", cz.PAL["blue"], "--", r"$0.756$ MC"),
    ]
    a_ahM.axhline(1.0, ls=":", color="0.4", lw=0.9)
    for run, col, ls, lbl in ah_specs:
        th = D[f"{run}_ah_t"]
        a_ahM.plot(th, D[f"{run}_ah_M"], color=col, ls=ls, lw=1.2, label=lbl)
        a_ahS.plot(th, np.abs(D[f"{run}_ah_a"]), color=col, ls=ls, lw=1.2)
    a_ahM.set_xlim(105, 250)
    a_ahS.set_xlim(105, 250)
    a_ahM.set_xticks([120, 160, 200, 240])
    a_ahM.xaxis.set_major_formatter(mticker.NullFormatter())
    a_ahM.set_ylim(0.75, 1.04)
    a_ahM.set_yticks([0.8, 0.9, 1.0])
    a_ahM.set_ylabel(r"$M_{\rm AH}/M$")
    a_ahM.legend(loc="lower left", fontsize=5.8, frameon=False, handlelength=1.2, labelspacing=0.16)

    a_ahS.set_yscale("log")
    a_ahS.set_xticks([120, 160, 200, 240])
    a_ahS.set_ylim(3e-4, 4e-2)
    a_ahS.set_yticks([1e-3, 1e-2])
    cz.no_minor_labels(a_ahS, "y")
    a_ahS.set_xlabel(r"$t/M$", labelpad=2)
    a_ahS.set_ylabel(r"Spurious $|a|/M$")
    for ax in (a_ahM, a_ahS):
        ax.yaxis.set_label_coords(-0.46 / wb, 0.5)

    # Bottom-Right: Total linear momentum conservation |P(t)|/M_0
    p_specs = [
        ("st_yc0605_vp01_10k_mid", "0.45", "--", r"$0.605$ MC"),
        ("st_yc0819_vp01_10k_mid", cz.PAL["blue"], "--", r"$0.819$ MC"),
        ("st_yc0900_vp01_10k_hyb", cz.PAL["green"], "-", r"$0.900$ Leb"),
        ("st_yc0605_vp01_10k_hyb", cz.PAL["red"], "-", r"$0.605$ anti"),
        ("st_yc0819_vp01_10k_anti", cz.PAL["orange"], "-", r"$0.819$ anti"),
    ]
    for run, col, ls, lbl in p_specs:
        t_r = D[f"{run}_t"]
        P_r = np.maximum(D[f"{run}_P"], 1e-18)
        a_mom.plot(t_r[1:], P_r[1:], color=col, ls=ls, lw=1.25, label=lbl)
    a_mom.set_yscale("log")
    a_mom.set_xlim(0, 300)
    a_mom.set_xticks([0, 100, 200])
    a_mom.set_ylim(1e-18, 2.0)
    a_mom.set_yticks([1e-16, 1e-12, 1e-8, 1e-4, 1.0])
    cz.no_minor_labels(a_mom, "y")
    a_mom.set_xlabel(r"$t/M$", labelpad=2)
    a_mom.set_ylabel(r"$|\mathbf{P}|/M_0$", labelpad=3)
    a_mom.legend(loc="lower left", bbox_to_anchor=(0.02, 0.25), ncol=2, columnspacing=0.6,
                 fontsize=5.6, frameon=False, handlelength=1.1, labelspacing=0.18)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
