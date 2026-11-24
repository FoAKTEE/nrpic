#!/usr/bin/env python3
"""Publication figure: Oppenheimer-Snyder dynamical collapse and dimensionless strong scaling."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
import czstyle as cz  # noqa: E402
from nrpic import oppenheimer_snyder as _osn  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DH = np.load(os.path.join(PAPER_DIR, "data/hybrid_speed_accuracy.npz"))
D3 = np.load(os.path.join(PAPER_DIR, "data/suite3_os_collapse.npz"))
OUT_DIR = os.path.join(PAPER_DIR, "figures")


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.2))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.085, top=0.955, wspace=0.28, hspace=0.33)

    # Top-Left: Central lapse alpha_c(tau_c) vs Staley 1+log bound
    ax = axes[0, 0]
    tau_col = float(D3["tau_collapse"])
    tau_hyb = DH["s3_hyb_n26_tau_probe"]
    tt = np.linspace(0.0, min(float(np.max(tau_hyb)), 0.99 * tau_col), 400)
    a_ll = np.array([float(_osn.staley_lower_bound(x_t)) for x_t in tt])

    ax.plot(DH["s3_nrp_n26_tau_probe"], DH["s3_nrp_n26_alp_probe"], "--", lw=1.6, color=cz.PAL["blue"],
            label=r"MC ($9328$)")
    ax.plot(DH["s3_opt_n26_tau_probe"], DH["s3_opt_n26_alp_probe"], ":", lw=1.6, color=cz.PAL["orange"],
            label=r"MFM ($9328$)")
    ax.plot(tau_hyb, DH["s3_hyb_n26_alp_probe"], "-", lw=1.4, color=cz.PAL["red"],
            label=r"SCP-AP ($9328$)")
    ax.plot(tt, a_ll, label="Staley 1+log", **cz.GUIDE)
    ax.set_xlabel(r"Central proper time $\tau_c\,[M]$")
    ax.set_ylabel(r"Central lapse $\alpha_c$")
    ax.set_xlim(0.0, 13.0)
    ax.set_ylim(-0.02, 1.06)
    ax.legend(loc="upper right", fontsize=7.6, frameon=False)

    # Top-Right: Z4c constraints & apparent horizon formation
    ax = axes[0, 1]
    ax.semilogy(DH["s3_nrp_n26_t_z4c"], np.maximum(DH["s3_nrp_n26_H_l2"], 1.0e-12), "--", lw=1.5,
                color=cz.PAL["blue"], label=r"$\|\mathcal{H}\|_2$ MC")
    ax.semilogy(DH["s3_opt_n26_t_z4c"], np.maximum(DH["s3_opt_n26_H_l2"], 1.0e-12), ":", lw=1.5,
                color=cz.PAL["orange"], label=r"$\|\mathcal{H}\|_2$ MFM")
    ax.semilogy(DH["s3_hyb_n26_t_z4c"], np.maximum(DH["s3_hyb_n26_H_l2"], 1.0e-12), "-", lw=1.5,
                color=cz.PAL["red"], label=r"$\|\mathcal{H}\|_2$ SCP-AP")
    ax.semilogy(DH["s3_hyb_n26_t_z4c"], np.maximum(DH["s3_hyb_n26_M_l2"], 1.0e-12), "-.", lw=1.3,
                color=cz.PAL["green"], alpha=0.85, label=r"$\|\mathcal{M}\|_2$ SCP-AP")
    t_ah = float(DH["s3_hyb_n26_t_AH"])
    m_ah = float(DH["s3_hyb_n26_M_AH"])
    ax.axvline(t_ah, **cz.MASK_LINE)
    ax.text(t_ah + 0.4, 0.88, r"$t_{\rm AH}$", transform=ax.get_xaxis_transform(), fontsize=8.5)
    ax.text(0.05, 0.94, rf"$M_{{\rm AH}} = {m_ah:.4f}$", transform=ax.transAxes, ha="left", va="top", fontsize=8.0)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Constraint $L_2$ norm")
    ax.set_xlim(0.0, 25.0)
    ax.set_ylim(1.0e-4, 2.0e1)
    cz.no_minor_labels(ax, "y")
    ax.legend(loc="lower right", fontsize=7.4, frameon=False)

    # Bottom-Left: Strong scaling of dimensionless per-cycle runtime
    ax = axes[1, 0]
    n_mfm = DH["sc_mfm_N"].astype(float)
    c_mfm = DH["sc_mfm_comp_s"].astype(float)
    n_hyb = DH["sc_hyb_N"].astype(float)
    c_hyb = DH["sc_hyb_comp_s"].astype(float)
    n_mc = DH["sc_mc_N"].astype(float)
    c_mc = DH["sc_mc_comp_s"].astype(float)
    t_ref = float(c_mfm[0])

    ax.loglog(n_mfm, c_mfm / t_ref, "s-", color=cz.PAL["orange"], ms=5.0, lw=1.5, label="MFM")
    ax.loglog(n_hyb, c_hyb / t_ref, "o-", color=cz.PAL["red"], ms=5.0, lw=1.5, label=r"SCP-AP ($Q=14$)")
    ax.loglog(n_mc, c_mc / t_ref, "^--", color=cz.PAL["blue"], ms=4.5, lw=1.3, label="MC PIC")

    n_guide = np.array([6.0e2, 2.0e4])
    ax.loglog(n_guide, 0.95 * (n_guide / n_mfm[0]), label=r"$\propto N_{\rm eff}$", **cz.GUIDE)
    ax.set_xlabel(r"Active elements / packets $N_{\rm eff}$")
    ax.set_ylabel(r"Normalized cycle time $T_{50}/T_{\rm ref}$")
    ax.set_xlim(4.0e2, 3.0e5)
    ax.set_ylim(0.025, 45.0)
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.legend(loc="lower left", fontsize=7.5, frameon=False)

    # Bottom-Right: Normalized element/packet throughput efficiency
    ax = axes[1, 1]
    n_ref = float(n_mfm[0])
    thr_mfm = (n_mfm / n_ref) / (c_mfm / t_ref)
    thr_hyb = (n_hyb / n_ref) / (c_hyb / t_ref)
    thr_mc = (n_mc / n_ref) / (c_mc / t_ref)

    ax.loglog(n_mfm, thr_mfm, "s-", color=cz.PAL["orange"], ms=5.0, lw=1.5, label="MFM")
    ax.loglog(n_hyb, thr_hyb, "o-", color=cz.PAL["red"], ms=5.0, lw=1.5, label=r"SCP-AP ($Q=14$)")
    ax.loglog(n_mc, thr_mc, "^--", color=cz.PAL["blue"], ms=4.5, lw=1.3, label="MC PIC")
    ax.set_xlabel(r"Active elements / packets $N_{\rm eff}$")
    ax.set_ylabel(r"Normalized throughput $(N_{\rm eff}/N_0)/(T_{50}/T_{\rm ref})$")
    ax.set_xlim(4.0e2, 3.0e5)
    ax.set_ylim(0.5, 1.5e4)
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.legend(loc="upper left", fontsize=7.5, frameon=False)

    os.makedirs(OUT_DIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT_DIR, f"fig_os_and_scaling.{ext}"), dpi=300)
    print(f"Saved fig_os_and_scaling in {OUT_DIR}")


if __name__ == "__main__":
    main()
