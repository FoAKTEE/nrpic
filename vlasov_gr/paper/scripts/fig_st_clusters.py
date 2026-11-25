#!/usr/bin/env python3
"""Remade PRX figure: Relativistic star cluster regimes, phase space, momentum invariance, and horizon accuracy."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LogNorm

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
DP = np.load(PAPER_DIR / "data" / "physics_st_phase.npz")
DF = np.load(PAPER_DIR / "data" / "physics_st_fates.npz")
DM = np.load(PAPER_DIR / "data" / "physics_st_mig_disp.npz")
OUT = PAPER_DIR / "figures" / "fig_st_clusters"


def main():
    cz.use_style()
    W, H_fig = 8.0, 5.25
    fig = plt.figure(figsize=(W, H_fig))

    # Top row: 4 equal phase-space (r/M, u_r) panels + right colorbar
    left_t, gap_tight, gap_wide, cb_w, cb_pad, right_t = 0.54, 0.09, 0.42, 0.13, 0.07, 0.48
    P = (W - left_t - right_t - 2 * gap_tight - gap_wide - cb_w - cb_pad) / 4.0
    x_panels = [
        left_t,
        left_t + P + gap_tight,
        left_t + 2 * (P + gap_tight),
        left_t + 2 * (P + gap_tight) + P + gap_wide,
    ]
    bot, hb, gap_y = 0.50, 1.92, 0.62
    y_top = bot + hb + gap_y

    cmap = cz.CMAP["dens"]
    norm = LogNorm(vmin=0.25, vmax=2.2e2)

    # Panels: (kind, key, title, xlim, ylim, env_key)
    top_specs = [
        ("pts", "ps1",     r"Equilibrium ($y_c=0.819,\,300M$)", (0.0, 10.5),  (-2.1, 2.1),  None),
        ("pts", "ps3",     r"Collapse ($y_c=0.605,\,100M$)",    (0.0, 5.2),   (-2.1, 2.1),  None),
        ("bin", "mig300",  r"Migration ($y_c=0.500,\,300M$)",   (0.0, 31.0),  (-2.1, 2.1),  "env05"),
        ("bin", "disp300", r"Dispersal ($y_c=0.283,\,300M$)",   (0.0, 145.0), (-0.18, 0.88), "env028"),
    ]

    mesh_ref = None
    for j, (kind, key, ttl, xlim, ylim, ekey) in enumerate(top_specs):
        ax = cz.inch_axes(fig, x_panels[j], y_top, P, P)
        if kind == "pts":
            r = DP[f"{key}_r"]
            ur = DP[f"{key}_ur"]
            H2, xe, ye = np.histogram2d(r, ur, bins=56, range=[xlim, ylim])
            H2 = H2.T
        else:
            H2 = DM[f"{key}_H"].T
            xe, ye = DM[f"{key}_xe"], DM[f"{key}_ye"]
        H_m = np.ma.masked_less(H2, 0.25)
        mesh_ref = ax.pcolormesh(xe, ye, H_m, cmap=cmap, norm=norm, shading="flat", rasterized=True)
        ax.axhline(0.0, ls=":", color="0.45", lw=0.75)
        if ekey is not None:
            ax.plot(DM[f"{ekey}_r"], DM[f"{ekey}_u"], color="k", ls="--", lw=0.95, alpha=0.75,
                    label=r"$t=0$ support" if j == 2 else None)
            if j == 2:
                ax.legend(loc="lower right", fontsize=6.0, frameon=False)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_xlabel(r"$r\,[M]$", labelpad=1)
        ax.text(0.5, 1.04, ttl, transform=ax.transAxes, ha="center", va="bottom", fontsize=7.0)
        if j == 0:
            ax.set_ylabel(r"Radial $u_r$", labelpad=2)
        if j in (1, 2):
            ax.yaxis.set_major_formatter(mticker.NullFormatter())
        if j == 3:
            ax.set_yticks([0.0, 0.4, 0.8])

    cax = cz.inch_axes(fig, x_panels[-1] + P + cb_pad, y_top, cb_w, P)
    cb = fig.colorbar(mesh_ref, cax=cax)
    cb.set_label(r"$10^4\,\Delta M/M_0$ / bin", fontsize=7.8, labelpad=3)
    cb.set_ticks([1, 10, 100])
    cb.ax.minorticks_off()
    cb.ax.tick_params(labelsize=7.2)

    # Bottom row: 3 stability & conservation panels
    left_b, gap_b, right_b = 0.62, 0.72, 0.14
    wb = (W - left_b - right_b - 2 * gap_b) / 3.0
    a_lap = cz.inch_axes(fig, left_b, bot, wb, hb)
    a_mom = cz.inch_axes(fig, left_b + wb + gap_b, bot, wb, hb)
    a_bar = cz.inch_axes(fig, left_b + 2 * (wb + gap_b), bot, wb, hb)

    # Bottom-Left: Central lapse alpha_c(t) spanning all 4 fates
    fate_specs = [
        ("st_yc0819_vp01_100k_hyb", cz.PAL["blue"],   "-",  r"Stable ($0.819$)"),
        ("st_yc0500_mig_10k_hyb",   cz.PAL["orange"], "-",  r"Migrate ($0.500$)"),
        ("st_yc0283_vp01_100k_hyb", cz.PAL["green"],  "-",  r"Disperse ($0.283$)"),
        ("st_yc0605_vp01_10k_hyb",  cz.PAL["red"],    "--", r"Collapse ($0.605$)"),
        ("st_yc0500_vp01_100k_hyb", "0.20",           "-",  r"Collapse ($0.500$)"),
    ]
    for lbl, col, ls, leg in fate_specs:
        a_lap.plot(DF[f"{lbl}_t"], DF[f"{lbl}_ac"], color=col, ls=ls, lw=1.45, label=leg)
    a_lap.set_xlim(0.0, 300.0)
    a_lap.set_ylim(-0.03, 1.05)
    a_lap.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    a_lap.set_ylabel(r"Central lapse $\alpha_c(t)$")
    a_lap.legend(loc="center right", bbox_to_anchor=(0.98, 0.56), fontsize=6.4, frameon=False, labelspacing=0.18)

    # Bottom-Middle: Linear momentum drift |P(t)|/M_0
    mom_specs = [
        ("st_yc0500_vp01_10k_mid",  cz.PAL["blue"],   "--", r"$0.500$ ($10^4$ MC)"),
        ("st_yc0500_vp01_100k_mid", cz.PAL["green"],  "--", r"$0.500$ ($10^5$ MC)"),
        ("st_yc0819_vp01_10k_mid",  cz.PAL["orange"], ":",  r"$0.819$ ($10^4$ MC)"),
        ("st_yc0500_vp01_100k_hyb", "0.20",           "-",  r"$0.500$ ($10^5$ QMC)"),
        ("st_yc0500_mig_10k_hyb",   cz.PAL["red"],    "-",  r"$0.500$ mig (QMC)"),
        ("st_yc0819_vp01_10k_anti", "#9467BD",        "-",  r"$0.819$ ($10^4$ QMC)"),
    ]
    for lbl, col, ls, leg in mom_specs:
        t = DF[f"{lbl}_t"]
        p = np.maximum(DF[f"{lbl}_P"], 1.0e-18)
        a_mom.semilogy(t[1:], p[1:], color=col, ls=ls, lw=1.35, label=leg)
    a_mom.set_xlim(0.0, 300.0)
    a_mom.set_ylim(1.0e-18, 1.0e0)
    a_mom.set_yticks([1e-16, 1e-12, 1e-8, 1e-4, 1e-1])
    cz.no_minor_labels(a_mom, "y")
    a_mom.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    a_mom.set_ylabel(r"Momentum drift $|\mathbf{P}|/M_0$")
    a_mom.legend(loc="center right", bbox_to_anchor=(0.985, 0.45), fontsize=6.0, frameon=False, labelspacing=0.16)

    # Bottom-Right: Horizon formation time t_AH and irreducible mass M_AH/M
    cases = [
        ("st_yc0500_vp01_10k",  r"$0.50$" "\n" r"$10^4$"),
        ("st_yc0500_vp01_100k", r"$0.50$" "\n" r"$10^5$"),
        ("st_yc0605_vp01_10k",  r"$0.61$" "\n" r"$10^4$"),
        ("st_yc0756_dp10_10k",  r"$0.76$" "\n" r"$10^4$"),
    ]
    xb = np.arange(len(cases))
    w = 0.36
    t_mid = [float(DF[f"{p}_mid_tah"]) for p, _ in cases]
    t_hyb = [float(DF[f"{p}_hyb_tah"]) for p, _ in cases]
    m_mid = [float(DF[f"{p}_mid_mah"]) for p, _ in cases]
    m_hyb = [float(DF[f"{p}_hyb_mah"]) for p, _ in cases]

    a_bar.bar(xb - 0.5 * w, t_mid, width=w, color=cz.PAL["blue"], alpha=0.88, edgecolor="k", lw=0.5,
              label="Stratified MC+Mid")
    a_bar.bar(xb + 0.5 * w, t_hyb, width=w, color=cz.PAL["red"], alpha=0.90, edgecolor="k", lw=0.5,
              label="Antipodal QMC+GL4")
    for i in range(len(cases)):
        a_bar.text(xb[i] - 0.5 * w, t_mid[i] + 3.0, f"{t_mid[i]:.1f}", ha="center", va="bottom",
                   fontsize=6.0, color=cz.PAL["blue"])
        a_bar.text(xb[i] + 0.5 * w, t_hyb[i] + 3.0, f"{t_hyb[i]:.1f}", ha="center", va="bottom",
                   fontsize=6.0, color=cz.PAL["red"])
        a_bar.text(xb[i] - 0.5 * w, 0.5 * t_mid[i], f"{m_mid[i]:.3f}", ha="center", va="center",
                   fontsize=5.7, color="white", rotation=90)
        a_bar.text(xb[i] + 0.5 * w, 0.5 * t_hyb[i], f"{m_hyb[i]:.3f}", ha="center", va="center",
                   fontsize=5.7, color="white", rotation=90)
    a_bar.set_xticks(xb)
    a_bar.set_xticklabels([lbl for _, lbl in cases], fontsize=7.2)
    a_bar.tick_params(axis="x", which="minor", bottom=False, top=False)
    a_bar.set_ylim(0.0, 265.0)
    a_bar.set_xlabel(r"Cluster $y_c$ & packet count", labelpad=1)
    a_bar.set_ylabel(r"Horizon time $t_{\rm AH}\,[M]$ (bars: $M_{\rm AH}/M$)")
    a_bar.legend(loc="upper left", fontsize=6.0, frameon=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
