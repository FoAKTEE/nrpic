#!/usr/bin/env python3
"""Publication figure: Self-gravitating Z4c+AMR collapse (OS, Prolate, Shapiro-Teukolsky QMC)."""
import glob
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
OUT_DIR = os.path.join(PAPER_DIR, "figures")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
W4B_BASE = os.path.join(SCRATCH, "runs", "repro_wave4b")


def safe_loadtxt(path: str):
    """Read whitespace numeric rows safely even if the final line is actively being flushed."""
    rows = []
    ncols = None
    with open(path, "r") as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            try:
                vals = [float(p) for p in parts]
            except ValueError:
                continue
            if ncols is None:
                ncols = len(vals)
            if len(vals) == ncols:
                rows.append(vals)
    return np.asarray(rows, dtype=np.float64)


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.0))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.09, top=0.955, wspace=0.28, hspace=0.33)

    # Top-Left: M5a Oppenheimer-Snyder R0=5M central proper-density relative error
    ax = axes[0, 0]
    E0 = float(_osn.rho0(5.0, 1.0))
    os_specs = [
        ("os_10k_lat_mid",  cz.PAL["blue"],   "-",  r"Lattice $10^4$ (plain)"),
        ("os_10k_lat_hyb",  cz.PAL["red"],    "-",  r"Lattice $10^4$ (densitized)"),
        ("os_100k_lat_mid", cz.PAL["green"],  "--", r"Lattice $10^5$"),
        ("os_100k_qmc_hyb", cz.PAL["orange"], "-",  r"Octant QMC $10^5$"),
    ]
    for lbl, col, ls, leg in os_specs:
        d = safe_loadtxt(os.path.join(W4B_BASE, "m5a", lbl, f"{lbl}.nrpic.hst"))
        tau = d[:, 14]
        e_p = d[:, 13]
        mask = (tau > 0.05) & (tau <= 2.60) & (e_p > 0.0)
        rho_cyc = np.array([float(_osn.cycloid_rho(xt)) for xt in tau[mask]]) / E0
        rel_err = np.maximum(np.abs(e_p[mask] / E0 - rho_cyc) / rho_cyc, 2.0e-6)
        ax.semilogy(tau[mask], rel_err, ls=ls, color=col, lw=1.4, label=leg)

    ax.set_xlim(0.0, 2.65)
    ax.set_ylim(2.0e-6, 12.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Central proper time $\tau_c\,[M]$")
    ax.set_ylabel(r"Central density error $|\rho_c/\rho_{\rm OS}-1|$")
    ax.legend(loc="upper left", fontsize=7.0, frameon=False)

    # Top-Right: M5b Prolate Spheroid e=0.9, b=10M Z4c Hamiltonian constraint L2 norm
    ax = axes[0, 1]
    prol_specs = [
        ("prol_10k_mc_mid",   cz.PAL["blue"],   "--", r"MC $10^4$ ($q_{xy,0}=6.4\times10^{-3}$)"),
        ("prol_10k_qmc_hyb",  cz.PAL["red"],    "-",  r"Octant QMC $10^4$ ($q_{xy,0}=0$)"),
        ("prol_100k_mc_mid",  cz.PAL["green"],  "--", r"MC $10^5$ ($q_{xy,0}=2.7\times10^{-3}$)"),
        ("prol_100k_qmc_hyb", cz.PAL["orange"], "-",  r"Octant QMC $10^5$ ($q_{xy,0}=0$)"),
    ]
    for lbl, col, ls, leg in prol_specs:
        z = safe_loadtxt(os.path.join(W4B_BASE, "m5b", lbl, f"{lbl}.z4c.user.hst"))
        H = np.sqrt(np.maximum(z[:, 3], 1.0e-24))
        ax.semilogy(z[:, 0], H, ls=ls, color=col, lw=1.35, label=leg)

    ax.axvline(32.15, **cz.MASK_LINE)
    ax.text(32.8, 0.08, r"$t_{\rm AH}\approx 32.1M$", transform=ax.get_xaxis_transform(), fontsize=7.6)
    ax.set_xlim(0.0, 45.0)
    ax.set_ylim(3.0e-2, 45.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Hamiltonian norm $\|\mathcal{H}\|_2$")
    ax.legend(loc="upper left", fontsize=6.6, frameon=False)

    # Bottom-Left: M5c Shapiro-Teukolsky yc=0.819, N=10^4 3-way QMC comparison
    ax = axes[1, 0]
    st819_specs = [
        ("st_yc0819_vp01_10k_mid",  cz.PAL["blue"],   "--", r"Stratified + Mid"),
        ("st_yc0819_vp01_10k_hyb",  cz.PAL["orange"], ":",  r"Lebedev $Q=14$ + GL4"),
        ("st_yc0819_vp01_10k_anti", cz.PAL["red"],    "-",  r"Antipodal $Q=4$ + GL4"),
    ]
    h_min_819 = 1.0
    for lbl, col, ls, leg in st819_specs:
        z = safe_loadtxt(os.path.join(W4B_BASE, "m5c", lbl, f"{lbl}.z4c.user.hst"))
        H = np.sqrt(np.maximum(z[:, 3], 1.0e-24))
        h_min_819 = min(h_min_819, float(np.min(H)))
        ax.semilogy(z[:, 0], H, ls=ls, color=col, lw=1.45, label=leg)

    ax.text(0.97, 0.06,
            r"$y_c=0.819$, $N=10^4$" "\n" r"Antipodal $|\mathbf{COM}(300M)|=3.7\times10^{-14}$",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.9)
    ax.set_xlim(0.0, 300.0)
    ax.set_ylim(max(1.0e-4, 0.45 * h_min_819), 1.4)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Hamiltonian norm $\|\mathcal{H}\|_2$")
    ax.legend(loc="upper right", fontsize=7.0, frameon=False)

    # Bottom-Right: M5c Shapiro-Teukolsky compact collapse central lapse alpha_c(t)
    ax = axes[1, 1]
    st_col_specs = [
        ("st_yc0756_dp10_10k_mid", cz.PAL["blue"],   "--", r"$y_c=0.756$ Stratified + Mid"),
        ("st_yc0756_dp10_10k_hyb", cz.PAL["green"],  "-",  r"$y_c=0.756$ Lebedev QMC + GL4"),
        ("st_yc0605_vp01_10k_mid", cz.PAL["orange"], "--", r"$y_c=0.605$ Stratified + Mid"),
        ("st_yc0605_vp01_10k_hyb", cz.PAL["red"],    "-",  r"$y_c=0.605$ Antipodal QMC + GL4"),
    ]
    for lbl, col, ls, leg in st_col_specs:
        nrp_p = os.path.join(W4B_BASE, "m5c", lbl, f"{lbl}.nrpic.hst")
        if not os.path.isfile(nrp_p):
            continue
        d = safe_loadtxt(nrp_p)
        if len(d) < 5:
            continue
        ax.plot(d[:, 0], d[:, 12], ls=ls, color=col, lw=1.4, label=leg)
        ah_p = os.path.join(W4B_BASE, "m5c", lbl, f"{lbl}.horizon_summary_0.txt")
        if os.path.isfile(ah_p):
            ah = safe_loadtxt(ah_p)
            ah = ah[np.isfinite(ah[:, 2])] if len(ah) else ah
            if len(ah):
                t_ah = float(ah[0, 1])
                idx_ah = int(np.argmin(np.abs(d[:, 0] - t_ah)))
                ax.plot([t_ah], [d[idx_ah, 12]], "o", color=col, ms=4.5, zorder=5)

    ax.set_xlim(0.0, 255.0)
    ax.set_ylim(-0.03, 0.99)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Central lapse $\alpha_c(t)$")
    ax.legend(loc="upper right", fontsize=6.5, frameon=False)
    ax.text(0.97, 0.28, "Circles mark\nfirst horizon", transform=ax.transAxes,
            ha="right", va="center", fontsize=6.8, color="0.3")

    os.makedirs(OUT_DIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT_DIR, f"fig_selfgrav_collapse_st.{ext}"), dpi=300)
    print(f"Saved fig_selfgrav_collapse_st in {OUT_DIR}")


if __name__ == "__main__":
    main()
