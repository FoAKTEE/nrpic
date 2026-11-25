#!/usr/bin/env python3
"""Remade PRX figure: Dimensionless multi-rate speedups, Courant scaling, and Pareto frontiers."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
D = np.load(PAPER_DIR / "data" / "iter5_pareto_curves.npz")
OUT = PAPER_DIR / "figures" / "fig_multirate_speedup"


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.85))
    fig.subplots_adjust(left=0.105, right=0.98, bottom=0.095, top=0.955, wspace=0.28, hspace=0.35)

    # Top-Left: 6-level Kerr SMR dimensionless filter speedup ratio
    ax = axes[0, 0]
    kerr_names = [
        "Directional\n" r"($n_{\rm f}=2$)",
        "Unsplit 7-pt\n" r"($n_{\rm f}=2$)",
        "Unsplit 7-pt\n" r"($n_{\rm f}=1$)",
    ]
    w_base = 209.3
    kerr_walls = [w_base, float(D["m4_uns_nf2_wall"]), float(D["m4_uns_nf1_wall"])]
    speedups = [w_base / w for w in kerr_walls]
    cols_tl = ["0.55", cz.PAL["blue"], cz.PAL["red"]]
    x_pos = np.arange(len(speedups))
    bars = ax.bar(x_pos, speedups, width=0.52, color=cols_tl, edgecolor="k", lw=0.7)
    for b, sp in zip(bars, speedups):
        ax.text(b.get_x() + 0.5 * b.get_width(), sp + 0.08, rf"${sp:.2f}\times$",
                ha="center", va="bottom", fontsize=7.6, weight="bold")
    ax.axhline(1.0, **cz.GUIDE)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(kerr_names, fontsize=7.8)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_ylim(0.0, 3.85)
    ax.set_xlabel("Harmonic conservative filter pass", labelpad=1)
    ax.set_ylabel(r"Kerr SMR speedup $T_{\rm dir}/T$")
    ax.text(0.04, 0.94,
            "6-lvl SMR (1128 blocks, quintic)\n"
            r"Identical $|\Delta \mathcal{E}_{\rm geo}/\mathcal{E}_0|_{\rm med}=3.38\times 10^{-10}$" "\n"
            r"Filter mass drift $\leq 9.8\times 10^{-16}$",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.7, color="0.20")

    # Top-Right: OS 10^4 normalized runtime vs Courant number and subcycling
    ax = axes[0, 1]
    w_ref = float(D["cfl_rk4_025_wall"])
    cfl_rk4 = np.array([0.25, 0.35, 0.40, 0.45, 0.50])
    r_rk4 = np.array([float(D[f"cfl_rk4_{s}_wall"]) for s in ("025", "035", "04", "045", "05")]) / w_ref
    cfl_rk3 = np.array([0.25, 0.35, 0.40, 0.45])
    r_rk3 = np.array([float(D[f"cfl_rk3_{s}_wall"]) for s in ("025", "035", "04", "045")]) / w_ref

    ax.plot(cfl_rk4, r_rk4, "s--", color=cz.PAL["blue"], lw=1.55, ms=5.4,
            label=r"RK4 ($\nu_{\rm CFL}\leq 0.50$)")
    ax.plot(cfl_rk3, r_rk3, "o-", color=cz.PAL["green"], lw=1.65, ms=5.6,
            label=r"SSP-RK3 + Dir ($s_{\rm m}=1$)")
    ax.plot([0.50], [65.5 / w_ref], "X", color="0.35", ms=7.0, label=r"SSP-RK3 $\nu=0.50$ unstable")

    cfl_mr = np.array([0.40, 0.45])
    r_dir_s2 = np.array([float(D["os10k_rk3_040_dir1_s2_wall"]),
                         float(D["os10k_rk3_045_dir1_s2_wall"])]) / w_ref
    r_uns_s2 = np.array([float(D["os10k_rk3_040_uns1_s2_wall"]),
                         float(D["os10k_rk3_045_uns1_s2_wall"])]) / w_ref
    ax.plot(cfl_mr, r_dir_s2, "D-", color=cz.PAL["orange"], lw=1.5, ms=5.5,
            label=r"SSP-RK3 + Dir ($s_{\rm m}=2$)")
    ax.plot(cfl_mr, r_uns_s2, "^-", color=cz.PAL["red"], lw=1.5, ms=6.0,
            label=r"SSP-RK3 + Unsplit ($s_{\rm m}=2$)")

    ax.annotate(rf"${1.0/r_uns_s2[1]:.2f}\times$ faster",
                xy=(0.45, r_uns_s2[1]), xytext=(0.35, 0.28),
                fontsize=7.0, color=cz.PAL["red"], ha="center",
                arrowprops=dict(arrowstyle="->", color=cz.PAL["red"], lw=0.9))
    ax.set_xlim(0.23, 0.52)
    ax.set_ylim(0.20, 1.12)
    ax.set_xlabel(r"Courant number $\nu_{\rm CFL}$", labelpad=-1)
    ax.set_ylabel(r"Normalized runtime $T/T_{\rm RK4(0.25)}$")
    ax.legend(loc="upper right", fontsize=6.4, frameon=False)

    # Bottom-Left: OS 10^4 & 10^5 Pareto Frontier (normalized runtime vs |M_AH/M_0 - 1|)
    ax = axes[1, 0]
    w10_base = float(D["os10k_rk4_025_dir1_wall"])
    w100_base = float(D["os100k_rk4_025_dir_s1_wall"])
    pts_10k = [
        ("os10k_rk4_025_dir1",    "s", "0.40",           r"$10^4$ RK4 (0.25)"),
        ("os10k_rk3_040_dir1_s1", "o", cz.PAL["blue"],   r"$10^4$ SSP-RK3 ($s_{\rm m}=1$)"),
        ("os10k_rk3_040_dir1_s2", "D", cz.PAL["green"],  r"$10^4$ SSP-RK3 ($s_{\rm m}=2$)"),
        ("os10k_rk3_040_dir1_s4", "P", cz.PAL["orange"], r"$10^4$ SSP-RK3 ($s_{\rm m}=4$)"),
        ("os10k_rk3_045_dir1_s2", "*", "#8E24AA",        r"$10^4$ SSP-RK3 (0.45,$s_{\rm m}=2$)"),
    ]
    pts_100k = [
        ("os100k_rk4_025_dir_s1",  "s", "k",            r"$10^5$ RK4 (0.25)"),
        ("os100k_rk3_040_dir1_s2", "o", cz.PAL["red"],  r"$10^5$ Dir ($s_{\rm m}=2$)"),
        ("os100k_rk3_040_uns3_s2", "^", "#008B8B",      r"$10^5$ Unsplit ($s_{\rm m}=2$)"),
        ("os100k_rk3_040_dir1_s4", "D", "#D48800",      r"$10^5$ Dir ($s_{\rm m}=4$)"),
    ]
    for key, mk, col, lab in pts_10k:
        w = float(D[f"{key}_wall"]) / w10_base
        merr = max(abs(float(D[f"{key}_M_AH"]) - 1.0), 1.0e-5)
        ax.semilogy([w], [merr], marker=mk, color=col, ms=6.2 if mk != "*" else 8.0,
                    ls="none", mec="k", mew=0.45, label=lab)
    for key, mk, col, lab in pts_100k:
        w = float(D[f"{key}_wall"]) / w100_base
        merr = max(abs(float(D[f"{key}_M_AH"]) - 1.0), 1.0e-5)
        ax.semilogy([w], [merr], marker=mk, color=col, ms=6.5, ls="none",
                    mec="k", mew=0.7, label=lab)

    w100_u = float(D["os100k_rk3_040_uns3_s2_wall"]) / w100_base
    m100_0 = abs(float(D["os100k_rk4_025_dir_s1_M_AH"]) - 1.0)
    m100_u = abs(float(D["os100k_rk3_040_uns3_s2_M_AH"]) - 1.0)
    ax.annotate("", xy=(w100_u + 0.02, m100_u), xytext=(0.98, m100_0),
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0, ls="--"))
    ax.text(0.5 * (1.0 + w100_u), 5.8e-4, rf"${1.0/w100_u:.2f}\times$ faster ($10^5$)",
            ha="center", va="top", fontsize=6.8, color="0.20")
    ax.set_xlim(0.30, 1.08)
    ax.set_ylim(2.0e-4, 3.5e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Normalized OS collapse runtime $T/T_{\rm RK4(0.25)}$", labelpad=-1)
    ax.set_ylabel(r"Horizon mass error $|M_{\rm AH}/M_0 - 1|$")
    ax.legend(loc="upper right", ncol=2, columnspacing=0.55, fontsize=5.4, frameon=False)

    # Bottom-Right: ST y_c=0.500 9-level AMR RK4 vs multi-rate SSP-RK3
    ax = axes[1, 1]
    sp_st = float(D["st_quin_stgA_wall"]) / float(D["st10k_rk3_040_dir4c_s2_wall"])
    ax.plot(D["st_quin_stgA_t"], D["st_quin_stgA_ac"], "--", color=cz.PAL["blue"], lw=1.55,
            label=rf"RK4 $\nu=0.25$ ($M_{{\rm AH}}={float(D['st_quin_stgA_M_AH']):.5f}M$)")
    if "st5_t" in D:
        ax.plot(D["st5_t"], D["st5_ac"], "-", color=cz.PAL["red"], lw=1.65,
                label=rf"SSP-RK3+$s_{{\rm m}}=2$ ($M_{{\rm AH}}={float(D['st10k_rk3_040_dir4c_s2_M_AH']):.5f}M$)")
    tah4 = float(D["st_quin_stgA_t_AH"])
    tah5 = float(D["st10k_rk3_040_dir4c_s2_t_AH"])
    ax.plot([tah4, tah4], [-0.03, 0.52], color=cz.PAL["blue"], ls=":", lw=1.0, alpha=0.65)
    ax.plot([tah5, tah5], [-0.03, 0.52], color=cz.PAL["red"], ls=":", lw=1.0, alpha=0.75)

    ax.text(0.04, 0.25,
            r"Critical cluster ($y_c=0.500$, 9-lvl AMR):" "\n"
            rf"Speedup $= {sp_st:.2f}\times$ vs RK4 ($\nu=0.25$)" "\n"
            r"$|\mathbf{P}|/M_0 = 3.9\times 10^{-15}$, filter $\leq 10^{-15}$" "\n"
            "Uncompensated filter disperses (no AH)",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=6.5, color="0.20")
    ax.set_xlim(0.0, 90.0)
    ax.set_ylim(-0.03, 0.65)
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Central lapse $\alpha_c(t)$")
    ax.legend(loc="lower left", fontsize=6.3, frameon=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
