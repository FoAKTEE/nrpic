#!/usr/bin/env python3
"""Remade PRX figure: Kerr a=0.9M sheared cloud, azimuthal PDF, Killing drift, and Pareto frontier."""
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
DH = np.load(PAPER_DIR / "data" / "hybrid_speed_accuracy.npz")
OUT = PAPER_DIR / "figures" / "fig_kerr_cloud_pareto"


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.85))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.085, top=0.955, wspace=0.28, hspace=0.33)

    # Top-Left: Orbital tidal arc x-y snapshot at t=30M
    ax = axes[0, 0]
    xy_mc = DH["s2_mc10k_xy"]
    xy_mfm = DH["s2_opt_n18_xy"]
    xy_hyb = DH["s2_hyb_n18_q14_xy"]
    ax.scatter(xy_mc[::2, 0], xy_mc[::2, 1], s=3.5, alpha=0.38, color=cz.PAL["blue"],
               rasterized=True, label=r"MC ($10^4$)")
    ax.scatter(xy_mfm[:, 0], xy_mfm[:, 1], s=4.5, alpha=0.52, color=cz.PAL["orange"],
               rasterized=True, label=r"MFM ($3112$)")
    ax.scatter(xy_hyb[::3, 0], xy_hyb[::3, 1], s=3.5, alpha=0.58, color=cz.PAL["red"],
               rasterized=True, label=r"SCP ($43568$)")
    r_plus = 1.0 + np.sqrt(1.0 - 0.9 * 0.9)
    ax.add_patch(plt.Circle((0.0, 0.0), r_plus, color="0.12", zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-6.0, 3.8)
    ax.set_ylim(-2.4, 13.8)
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.legend(loc="upper left", fontsize=7.8, markerscale=1.4, frameon=False)

    # Top-Right: Normalized azimuthal density PDF at t=30M vs 10^5 MC reference
    ax = axes[0, 1]
    bins = np.linspace(-0.20, 0.20, 25)
    ax.stairs(DH["s2_mc100k_p_hist"], bins, color="k", lw=1.6, ls="--", label=r"Ref.\ ($10^5$)")
    ax.stairs(DH["s2_mc10k_p_hist"], bins, color=cz.PAL["blue"], lw=1.25, alpha=0.88, label=r"MC ($10^4$)")
    ax.stairs(DH["s2_opt_n18_p_hist"], bins, color=cz.PAL["orange"], lw=1.25, alpha=0.88, label="MFM")
    ax.stairs(DH["s2_hyb_n18_q14_p_hist"], bins, color=cz.PAL["red"], lw=1.7, label="SCP")
    ax.set_xlim(-0.20, 0.20)
    ax.set_ylim(0.0, 6.2)
    ax.set_xlabel(r"Azimuthal offset $\Delta\phi$", labelpad=-1)
    ax.set_ylabel(r"Normalized PDF $p(\Delta\phi)$")
    ax.legend(loc="upper right", ncol=2, columnspacing=0.8, fontsize=7.4, frameon=False)
    r_mc = float(DH["s2_mc10k_rough_hist"])
    r_hyb = float(DH["s2_hyb_n18_q14_rough_hist"])
    r_ref = float(DH["s2_mc100k_rough_hist"])
    ax.text(0.04, 0.95,
            rf"Roughness $R$: SCP {r_hyb:.3f}" "\n"
            rf"MC {r_mc:.3f} (Ref.\ {r_ref:.3f})",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.3, color="0.18")

    # Bottom-Left: Killing invariant drift vs time
    ax = axes[1, 0]

    def rel_drift(arr):
        return np.maximum(np.abs(arr - arr[0]) / abs(arr[0]), 1.0e-14)

    t_opt = DH["s2_opt_n18_times"]
    t_mc = DH["s2_mc10k_times"]
    t_hyb = DH["s2_hyb_n18_q14_times"]
    ax.semilogy(t_opt, rel_drift(DH["s2_opt_n18_E"]), "s-", color=cz.PAL["orange"], ms=3.5, lw=1.4,
                label=r"MFM $|\Delta E_\infty/E_0|$")
    ax.semilogy(t_mc, rel_drift(DH["s2_mc10k_E"]), ":", color=cz.PAL["blue"], lw=1.6,
                label=r"MC ($10^4$) $|\Delta E_\infty/E_0|$")
    ax.semilogy(t_hyb, rel_drift(DH["s2_hyb_n18_q14_E"]), "o-", color=cz.PAL["red"], ms=3.8, lw=1.6,
                label=r"SCP $|\Delta E_\infty/E_0|$")
    ax.semilogy(t_hyb, rel_drift(DH["s2_hyb_n18_q14_Lz"]), "^-", color=cz.PAL["green"], ms=3.8, lw=1.6,
                label=r"SCP $|\Delta L_z/L_{z0}|$")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel("Relative Killing drift")
    ax.set_xlim(0.0, 30.0)
    ax.set_ylim(2.0e-14, 4.0e-3)
    cz.no_minor_labels(ax, "y")
    ax.legend(loc="center left", bbox_to_anchor=(0.24, 0.30), fontsize=7.5, frameon=False)

    # Bottom-Right: Accuracy-cost Pareto frontier (dimensionless compute ratio)
    ax = axes[1, 1]
    t_base = float(DH["base_mfm_s2_n18_wall_s"])
    opt_lbls = ("s2_opt_n10", "s2_opt_n14", "s2_opt_n18")
    opt_x = [float(DH[f"{k}_comp_s"]) / t_base for k in opt_lbls]
    opt_y = [float(DH[f"{k}_l1_hist"]) for k in opt_lbls]
    ax.loglog([1.0], [float(DH["s2_opt_n18_l1_hist"])], "D", color="0.35", ms=5.8,
              label="Baseline MFM")
    ax.loglog(opt_x, opt_y, "s-", color=cz.PAL["orange"], ms=5.2, lw=1.5, label="Continuum MFM")

    mc_x = float(DH["s2_mc10k_comp_s"]) / t_base
    mc_y = float(DH["s2_mc10k_l1_hist"])
    ax.loglog([mc_x], [mc_y], "P", color=cz.PAL["blue"], ms=6.6, label=r"MC ($10^4$)")

    hyb_lbls = ("s2_hyb_n10_q14", "s2_hyb_n14_q14", "s2_hyb_n18_q8", "s2_hyb_n18_q14")
    hyb_x = [float(DH[f"{k}_comp_s"]) / t_base for k in hyb_lbls]
    hyb_y = [float(DH[f"{k}_l1_hist"]) for k in hyb_lbls]
    ax.loglog(hyb_x, hyb_y, "o-", color=cz.PAL["red"], ms=5.4, lw=1.6, label="SCP")

    ax.annotate("", xy=(hyb_x[-1] * 1.18, hyb_y[-1]), xytext=(0.82, float(DH["s2_opt_n18_l1_hist"])),
                arrowprops=dict(arrowstyle="->", color="0.45", lw=1.0, ls=":"))
    ax.set_xlabel(r"Normalized step cost $T_{\rm step}/T_{\rm base}$", labelpad=-1)
    ax.set_ylabel(r"Normalized PDF error $L_1(p - p_{\rm ref})$")
    ax.set_xlim(1.2e-3, 1.8)
    ax.set_ylim(0.025, 0.42)
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.legend(loc="upper right", fontsize=7.6, frameon=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
