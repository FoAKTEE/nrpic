#!/usr/bin/env python3
"""Publication figure: GL4 symplectic geodesics, dynamic Z4c tracers, and 6-level SMR clusters."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
D4A = np.load(os.path.join(PAPER_DIR, "data/repro_wave4a.npz"))
OUT_DIR = os.path.join(PAPER_DIR, "figures")


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
    fig.subplots_adjust(left=0.11, right=0.985, bottom=0.10, top=0.955, wspace=0.30, hspace=0.37)

    # Top-Left: M1 Kerr a=0.9M e=0.99 passage (dt=0.01M, t=230M) across KS, CKS, Lattice
    ax = axes[0, 0]
    metrics = ("ks", "cks", "lat")
    x_cat = np.arange(3)
    dx_m, dx_g = -0.10, +0.10
    dE_mid = [float(D4A[f"m1_{m}_mid_dE"]) for m in metrics]
    dE_gl4 = [float(D4A[f"m1_{m}_gl4_dE"]) for m in metrics]
    dQ_mid = [float(D4A[f"m1_{m}_mid_dQ"]) for m in metrics]
    dQ_gl4 = [float(D4A[f"m1_{m}_gl4_dQ"]) for m in metrics]
    dx_mid = [float(D4A[f"m1_{m}_mid_pos_err"]) for m in metrics]
    dx_gl4 = [float(D4A[f"m1_{m}_gl4_pos_err"]) for m in metrics]

    ax.plot(x_cat + dx_m, dE_mid, "o--", color=cz.PAL["red"], mfc="white", ms=4.8, lw=1.2, label=r"Mid $|\Delta E/E_0|$")
    ax.plot(x_cat + dx_g, dE_gl4, "o-", color=cz.PAL["red"], ms=5.0, lw=1.5, label=r"GL4 $|\Delta E/E_0|$")
    ax.plot(x_cat + dx_m, dQ_mid, "s--", color=cz.PAL["blue"], mfc="white", ms=4.5, lw=1.2, label=r"Mid $|\Delta Q/Q_0|$")
    ax.plot(x_cat + dx_g, dQ_gl4, "s-", color=cz.PAL["blue"], ms=4.7, lw=1.5, label=r"GL4 $|\Delta Q/Q_0|$")
    ax.plot(x_cat + dx_m, dx_mid, "^--", color=cz.PAL["green"], mfc="white", ms=4.8, lw=1.2, label=r"Mid $|\Delta \mathbf{x}_{\rm end}|$")
    ax.plot(x_cat + dx_g, dx_gl4, "^-", color=cz.PAL["green"], ms=5.0, lw=1.5, label=r"GL4 $|\Delta \mathbf{x}_{\rm end}|$")

    ax.set_yscale("log")
    ax.set_xticks(x_cat)
    ax.set_xticklabels(["KS (sph)", "CKS", "Lattice"])
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.4, 2.4)
    ax.set_ylim(1.0e-15, 6.0e2)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel("Metric representation")
    ax.set_ylabel("Error after pericenter passage")
    ax.legend(ncol=2, loc="upper left", fontsize=6.1, columnspacing=0.6, handlelength=1.4, frameon=False)

    # Top-Right: M4 6-level SMR Kerr a=0.9M bound clusters (t=200M, N=10^4 and 10^5)
    ax = axes[0, 1]
    cl_keys = ("ana_10k", "ana_100k", "mesh_10k", "mesh_100k")
    xc4 = np.arange(4)
    medE_m = [float(D4A[f"m4_{k}_mid_medE"]) for k in cl_keys]
    medE_g = [float(D4A[f"m4_{k}_gl4_medE"]) for k in cl_keys]
    p99E_m = [float(D4A[f"m4_{k}_mid_p99E"]) for k in cl_keys]
    p99E_g = [float(D4A[f"m4_{k}_gl4_p99E"]) for k in cl_keys]
    medQ_m = [float(D4A[f"m4_{k}_mid_medQK"]) for k in cl_keys]
    medQ_g = [float(D4A[f"m4_{k}_gl4_medQK"]) for k in cl_keys]

    ax.plot(xc4 + dx_m, medE_m, "o--", color=cz.PAL["red"], mfc="white", ms=4.5, lw=1.2, label=r"Mid med $|\Delta E/E_0|$")
    ax.plot(xc4 + dx_g, medE_g, "o-", color=cz.PAL["red"], ms=4.8, lw=1.5, label=r"GL4 med $|\Delta E/E_0|$")
    ax.plot(xc4 + dx_m, p99E_m, "D--", color=cz.PAL["orange"], mfc="white", ms=4.1, lw=1.2, label=r"Mid $p_{99}$ $|\Delta E/E_0|$")
    ax.plot(xc4 + dx_g, p99E_g, "D-", color=cz.PAL["orange"], ms=4.3, lw=1.5, label=r"GL4 $p_{99}$ $|\Delta E/E_0|$")
    ax.plot(xc4 + dx_m, medQ_m, "s--", color=cz.PAL["blue"], mfc="white", ms=4.3, lw=1.2, label=r"Mid med $|\Delta Q/K|$")
    ax.plot(xc4 + dx_g, medQ_g, "s-", color=cz.PAL["blue"], ms=4.5, lw=1.5, label=r"GL4 med $|\Delta Q/K|$")

    ax.axvline(1.5, **cz.MASK_LINE)
    ax.set_yscale("log")
    ax.set_xticks(xc4)
    ax.set_xticklabels(["Ana 10k", "Ana 100k", "SMR 10k", "SMR 100k"], fontsize=8.4)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.4, 3.4)
    ax.set_ylim(2.0e-17, 1.0e-3)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel("Cluster configuration")
    ax.set_ylabel("Ensemble invariant drift")
    ax.legend(ncol=1, loc="lower right", fontsize=6.1, handlelength=1.4, frameon=False)

    # Bottom-Left: M3 Dynamic Z4c puncture tracers & head-on binary merger
    ax = axes[1, 0]
    ld_mid = D4A["m3_punc_single_mid_L_drift"]
    ld_gl4 = D4A["m3_punc_single_gl4_L_drift"]
    lx_mid = D4A["m3_punc_headon_mid_lx_err"][:5]
    lx_gl4 = D4A["m3_punc_headon_gl4_lx_err"][:5]

    x_s = np.arange(4)
    x_h = 4.6 + np.arange(5)
    ax.plot(x_s, ld_mid, "s--", color=cz.PAL["blue"], mfc="white", ms=5.5, lw=1.2, label="Midpoint")
    ax.plot(x_s, ld_gl4, "o-", color=cz.PAL["red"], ms=4.0, lw=1.4, label=r"GL4 + Quad-$t$")
    ax.plot(x_h, lx_mid, "s--", color=cz.PAL["blue"], mfc="white", ms=5.5, lw=1.2)
    ax.plot(x_h, lx_gl4, "o-", color=cz.PAL["red"], ms=4.0, lw=1.4)
    ax.axvline(3.8, **cz.MASK_LINE)
    m_single = float(D4A["m3_punc_single_gl4_M_AH"])
    m_head = float(D4A["m3_punc_headon_gl4_ah0_M"])
    ax.text(1.5, 4.5e-5, rf"Single ($M_{{\rm AH}}={m_single:.4f}$)", ha="center", va="bottom", fontsize=7.2)
    ax.text(6.6, 4.5e-5, rf"Head-on ($M_{{\rm AH}}={m_head:.4f}$)", ha="center", va="bottom", fontsize=7.2)

    ax.set_yscale("log")
    ax.set_xticks(np.concatenate([x_s, x_h]))
    ax.set_xticklabels(["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4", "H5"], fontsize=8.0)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.5, 9.1)
    ax.set_ylim(3.0e-5, 3.0e-3)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel("Tracer orbit index")
    ax.set_ylabel(r"Symmetry drift $|\Delta L|/L_0$")
    ax.legend(loc="upper left", fontsize=7.2, frameon=False)

    # Bottom-Right: M4 6-level SMR proper-volume filter conservation at t=0 and peak
    ax = axes[1, 1]
    x_b = np.arange(4)
    unw = [
        abs(float(D4A["m4_mesh_10k_mid_filt_t0"])),
        float(D4A["m4_mesh_10k_mid_filt_max"]),
        abs(float(D4A["m4_mesh_100k_mid_filt_t0"])),
        float(D4A["m4_mesh_100k_mid_filt_max"]),
    ]
    floor = 1.0e-15
    dens = [
        max(abs(float(D4A["m4_mesh_10k_gl4_filt_t0"])), floor),
        float(D4A["m4_mesh_10k_gl4_filt_max"]),
        max(abs(float(D4A["m4_mesh_100k_gl4_filt_t0"])), floor),
        float(D4A["m4_mesh_100k_gl4_filt_max"]),
    ]
    w_bar = 0.30
    ax.bar(x_b - 0.5 * w_bar, unw, width=w_bar, color=cz.PAL["blue"], alpha=0.85, label="Unweighted filter")
    ax.bar(x_b + 0.5 * w_bar, dens, width=w_bar, color=cz.PAL["red"], alpha=0.85, label="Densitized filter")
    ax.axhline(floor, color="grey", lw=0.9, ls="--", alpha=0.55)
    for xb_i in (0, 2):
        ax.text(xb_i + 0.5 * w_bar, floor * 1.8, r"$0$", ha="center", va="bottom",
                fontsize=7.2, color=cz.PAL["red"])

    ax.set_yscale("log")
    ax.set_xticks(x_b)
    ax.set_xticklabels(["10k ($t=0$)", "10k (max)", "100k ($t=0$)", "100k (max)"], fontsize=8.0)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.55, 3.55)
    ax.set_ylim(3.0e-16, 1.5e0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel("Six-level SMR filter check")
    ax.set_ylabel(r"Proper-energy error $|\Delta E_{\rm filt}/E|$")
    ax.legend(loc="upper left", fontsize=7.2, frameon=False)

    os.makedirs(OUT_DIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT_DIR, f"fig_gl4_kerr_clusters.{ext}"), dpi=300)
    print(f"Saved fig_gl4_kerr_clusters in {OUT_DIR}")


if __name__ == "__main__":
    main()
