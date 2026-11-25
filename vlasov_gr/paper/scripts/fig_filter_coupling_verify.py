#!/usr/bin/env python3
"""Remade PRX figure: Harmonic conservative filter, causal stage coupling, and Oppenheimer-Snyder collapse."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "python"))
import czstyle as cz  # noqa: E402
from nrpic import oppenheimer_snyder as _osn  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
DF = np.load(PAPER_DIR / "data" / "iter3_filter_curves.npz")
DS = np.load(PAPER_DIR / "data" / "iter4_stagea_curves.npz")
DH = np.load(PAPER_DIR / "data" / "hybrid_speed_accuracy.npz")
D3 = np.load(PAPER_DIR / "data" / "suite3_os_collapse.npz")
OUT = PAPER_DIR / "figures" / "fig_filter_coupling_verify"


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.85))
    fig.subplots_adjust(left=0.105, right=0.925, bottom=0.09, top=0.955, wspace=0.33, hspace=0.33)

    order = [
        ("mcons", cz.PAL["red"],    "-",  1.75, 4, "Harmonic flux-cons."),
        ("dens",  cz.PAL["orange"], "-.", 1.50, 3, r"Pre-$\sqrt{\gamma}$ densitized"),
        ("plain", cz.PAL["blue"],   "--", 1.35, 2, "Unweighted binomial"),
    ]
    floor = 1.0e-16

    # Top-Left: OS constant-state central density accuracy
    ax = axes[0, 0]
    for mode, col, ls, lw, zo, lbl in order:
        ax.semilogy(DF[f"os_{mode}_tau"], np.maximum(DF[f"os_{mode}_rho_err"], 1e-6),
                    color=col, ls=ls, lw=lw, zorder=zo, label=lbl)
    ax.set_xlim(0.0, 2.65)
    ax.set_ylim(2.0e-6, 2.0e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Central proper time $\tau_c\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Central density error $|\rho_c/\rho_{\rm OS}-1|$")
    ax.text(0.96, 0.94, "OS collapse $R_0=5M$\n" r"(restores $8.0\times$ vs pre-$\sqrt{\gamma}$)",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.9, color="0.22")
    ax.legend(loc="lower right", fontsize=6.8, frameon=False)

    # Top-Right: 7-level dynamic AMR proper-volume filter conservation drift
    ax = axes[0, 1]
    for mode, col, ls, lw, zo, lbl in order:
        ax.semilogy(DF[f"os_{mode}_t"], np.maximum(DF[f"os_{mode}_filt"], floor),
                    color=col, ls=ls, lw=lw, zorder=zo, label=lbl)
    ax.axhline(floor, color="grey", lw=0.9, ls="--", alpha=0.55)
    ax.text(0.8, 2.5e-15, "rounding floor\n" r"($\leq 8.8\times 10^{-16}$)",
            ha="left", va="bottom", fontsize=6.2, color=cz.PAL["red"])
    ax.set_xlim(0.0, 25.0)
    ax.set_ylim(3.0e-17, 2.0e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Filter conservation drift $|I_E^{\rm filt}/I_E - 1|$")
    ax.text(0.04, 0.44, "7-level dynamic AMR\n" r"($2.7\times 10^{13}\times$ reduction)",
            transform=ax.transAxes, ha="left", va="center", fontsize=6.9, color="0.22")
    ax.legend(loc="center right", bbox_to_anchor=(0.98, 0.56), fontsize=6.6, frameon=False)

    # Bottom-Left: Courant convergence comparing Causal (d0, d1) vs Frozen T_munu
    ax = axes[1, 0]
    cfls = np.array([0.25, 0.125])
    f_errs = np.array([float(DS["cfl_frozen_alpha_c_rel025"]), float(DS["cfl_frozen_alpha_c_rel0125"])])
    s_errs = np.array([float(DS["cfl_stageA_alpha_c_rel025"]), float(DS["cfl_stageA_alpha_c_rel0125"])])
    pf = float(DS["cfl_frozen_alpha_c_order"])
    ps = float(DS["cfl_stageA_alpha_c_order"])

    ax.loglog(cfls, f_errs, "s--", color=cz.PAL["blue"], lw=1.6, ms=6.2,
              label=rf"Frozen $T_{{\mu\nu}}$ ($p={pf:.2f}$)")
    ax.loglog(cfls, s_errs, "o-", color=cz.PAL["red"], lw=1.7, ms=6.4,
              label=rf"Causal $(d_0, d_1)$ ($p={ps:.2f}$)")
    href = np.array([0.11, 0.28])
    ax.loglog(href, 2.2e-3 * href, ":", color="0.45", lw=1.0, label=r"$\propto \Delta t^1$")
    ax.loglog(href, 1.0e-3 * (href ** 2), "-.", color="0.45", lw=1.0, label=r"$\propto \Delta t^2$")
    ax.annotate("", xy=(0.25, s_errs[0] * 1.15), xytext=(0.25, f_errs[0] * 0.85),
                arrowprops=dict(arrowstyle="<->", color=cz.PAL["red"], lw=1.0))
    ax.text(0.242, float(np.sqrt(f_errs[0] * s_errs[0])),
            rf"${f_errs[0]/s_errs[0]:.0f}\times$ smaller" "\n" r"at $\nu_{\rm CFL}=0.25$",
            ha="right", va="center", fontsize=6.8, color=cz.PAL["red"])
    ax.set_xlim(0.10, 0.30)
    ax.set_ylim(3.0e-6, 1.5e-3)
    ax.set_xticks([0.125, 0.25])
    ax.set_xticklabels(["0.125", "0.25"])
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlabel(r"Courant number $\nu_{\rm CFL}$", labelpad=-1)
    ax.set_ylabel(r"Lapse error $|\alpha_c(10M)/\alpha_c^{\rm ref} - 1|$")
    ax.legend(loc="lower right", fontsize=6.5, frameon=False)

    # Bottom-Right: OS Staley lapse bound vs proper time & Z4c constraint evolution
    ax = axes[1, 1]
    tau_col = float(D3["tau_collapse"])
    tau_hyb = DH["s3_hyb_n26_tau_probe"]
    tt = np.linspace(0.0, min(float(np.max(tau_hyb)), 0.99 * tau_col), 350)
    a_ll = np.array([float(_osn.staley_lower_bound(x_t)) for x_t in tt])

    h_br = []
    h_br.append(ax.plot(DH["s3_nrp_n26_tau_probe"], DH["s3_nrp_n26_alp_probe"], "--", lw=1.55,
                        color=cz.PAL["blue"], label=r"MC ($9328$)")[0])
    h_br.append(ax.plot(DH["s3_opt_n26_tau_probe"], DH["s3_opt_n26_alp_probe"], ":", lw=1.6,
                        color=cz.PAL["orange"], label=r"MFM ($9328$)")[0])
    h_br.append(ax.plot(tau_hyb, DH["s3_hyb_n26_alp_probe"], "-", lw=1.55,
                        color=cz.PAL["red"], label=r"SCP ($9328$)")[0])
    h_br.append(ax.plot(tt, a_ll, **cz.GUIDE, label=r"Staley $1+\log$ bound")[0])

    ax2 = ax.twinx()
    ax2.set_yscale("log")
    h_br.append(ax2.plot(DH["s3_hyb_n26_t_z4c"] * 0.5, np.maximum(DH["s3_hyb_n26_H_l2"], 1.0e-8),
                         "-.", color=cz.PAL["green"], lw=1.3, alpha=0.88, label=r"$\|\mathcal{H}\|_2$ vs $t/2$")[0])
    ax2.set_ylim(1.0e-5, 1.5e2)
    cz.no_minor_labels(ax2, "y")
    ax2.tick_params(which="both", direction="in", labelcolor=cz.PAL["green"])
    ax2.set_ylabel(r"Hamiltonian norm $\|\mathcal{H}\|_2$", color=cz.PAL["green"])

    t_ah = float(DH["s3_hyb_n26_t_AH"])
    m_ah = float(DH["s3_hyb_n26_M_AH"])
    ax.text(0.96, 0.95, rf"$t_{{\rm AH}}={t_ah:.1f}M,\;M_{{\rm AH}}={m_ah:.4f}M$",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.7, color="0.22")
    ax.set_xlim(0.0, 12.6)
    ax.set_ylim(-0.02, 1.06)
    ax.set_xlabel(r"Central proper time $\tau_c\,[M]$ (norm: $t/2$)", labelpad=-1)
    ax.set_ylabel(r"Central lapse $\alpha_c$")
    ax.legend(handles=h_br, loc="lower left", fontsize=6.0, frameon=False,
              labelspacing=0.18)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
