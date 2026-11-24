#!/usr/bin/env python3
"""Publication figure: Self-gravitating Z4c+AMR collapse (OS, Prolate, Shapiro-Teukolsky QMC)."""
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
I3_BASE = os.path.join(SCRATCH, "runs", "iter3_verify")


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
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.0))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.09, top=0.955, wspace=0.28, hspace=0.33)

    # Top-Left: M5a Oppenheimer-Snyder R0=5M central proper-density relative error
    ax = axes[0, 0]
    E0 = float(_osn.rho0(5.0, 1.0))
    os_specs = [
        (os.path.join(I3_BASE, "iter3_os_10k_mcons", "iter3_os_10k_mcons.nrpic.hst"),
         cz.PAL["red"], "-", 1.85, 2, r"Lattice $10^4$ (mcons, Iter 3)"),
        (os.path.join(W4B_BASE, "m5a", "os_10k_lat_mid", "os_10k_lat_mid.nrpic.hst"),
         cz.PAL["blue"], "--", 1.35, 3, r"Lattice $10^4$ (plain + Mid)"),
        (os.path.join(W4B_BASE, "m5a", "os_10k_lat_hyb", "os_10k_lat_hyb.nrpic.hst"),
         cz.PAL["orange"], "-.", 1.50, 4, r"Lattice $10^4$ (densitized)"),
        (os.path.join(W4B_BASE, "m5a", "os_100k_lat_mid", "os_100k_lat_mid.nrpic.hst"),
         cz.PAL["green"], "--", 1.45, 5, r"Lattice $10^5$"),
        (os.path.join(W4B_BASE, "m5a", "os_100k_qmc_hyb", "os_100k_qmc_hyb.nrpic.hst"),
         "0.35", ":", 1.55, 6, r"Octant QMC $10^5$"),
    ]
    for path, col, ls, lw, zo, leg in os_specs:
        d = safe_loadtxt(path)
        tau = d[:, 14]
        e_p = d[:, 13]
        mask = (tau > 0.05) & (tau <= 2.60) & (e_p > 0.0)
        rho_cyc = np.array([float(_osn.cycloid_rho(xt)) for xt in tau[mask]]) / E0
        rel_err = np.maximum(np.abs(e_p[mask] / E0 - rho_cyc) / rho_cyc, 2.0e-6)
        ax.semilogy(tau[mask], rel_err, ls=ls, color=col, lw=lw, zorder=zo, label=leg)

    ax.set_xlim(0.0, 2.65)
    ax.set_ylim(2.0e-6, 95.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Central proper time $\tau_c\,[M]$")
    ax.set_ylabel(r"Central density error $|\rho_c/\rho_{\rm OS}-1|$")
    ax.legend(loc="upper left", fontsize=6.1, frameon=False, labelspacing=0.22)

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
    ax.text(32.8, 0.08, r"$t_{\rm AH}\approx 32.1M$", transform=ax.get_xaxis_transform(), fontsize=7.5)
    ax.set_xlim(0.0, 45.0)
    ax.set_ylim(3.0e-2, 45.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Hamiltonian norm $\|\mathcal{H}\|_2$")
    ax.legend(loc="upper left", fontsize=6.5, frameon=False)

    # Bottom-Left: M5c Shapiro-Teukolsky yc=0.819 N=10^4 & N=10^5 constraint convergence
    ax = axes[1, 0]
    st819_specs = [
        ("st_yc0819_vp01_10k_hyb",  cz.PAL["orange"], ":",  r"Lebedev $Q=14$ ($10^4$)"),
        ("st_yc0819_vp01_10k_mid",  cz.PAL["blue"],   "--", r"Stratified MC + Mid ($10^4$)"),
        ("st_yc0819_vp01_10k_anti", cz.PAL["red"],    "-",  r"Antipodal $Q=4$ ($10^4$)"),
        ("st_yc0819_vp01_100k_mid", cz.PAL["green"],  "--", r"Stratified MC + Mid ($10^5$)"),
        ("st_yc0819_vp01_100k_hyb", "0.25",           "-",  r"Lebedev $Q=14$ ($10^5$)"),
    ]
    h_min_819 = 1.0
    for lbl, col, ls, leg in st819_specs:
        z = safe_loadtxt(os.path.join(W4B_BASE, "m5c", lbl, f"{lbl}.z4c.user.hst"))
        H = np.sqrt(np.maximum(z[:, 3], 1.0e-24))
        h_min_819 = min(h_min_819, float(np.min(H)))
        ax.semilogy(z[:, 0], H, ls=ls, color=col, lw=1.35, label=leg)

    ax.text(0.97, 0.04,
            r"$y_c=0.819$ ($R=9.96M$)" "\n" r"Antipodal $|\mathbf{COM}(300M)|=3.7\times10^{-14}$",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5)
    ax.set_xlim(0.0, 300.0)
    ax.set_ylim(max(1.0e-4, 0.25 * h_min_819), 1.8)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Hamiltonian norm $\|\mathcal{H}\|_2$")
    ax.legend(loc="upper right", fontsize=6.4, frameon=False)

    # Bottom-Right: M5c ST yc=0.500 & 0.605 collapse central lapse alpha_c(t) + first horizons
    ax = axes[1, 1]
    st_col_specs = [
        ("st_yc0500_vp01_100k_hyb", cz.PAL["green"],  "-",  r"$y_c=0.500$, $10^5$ Anti + GL4"),
        ("st_yc0500_vp01_100k_mid", "0.25",           ":",  r"$y_c=0.500$, $10^5$ MC + Mid"),
        ("st_yc0500_vp01_10k_hyb",  cz.PAL["red"],    "-",  r"$y_c=0.500$, $10^4$ Anti + GL4"),
        ("st_yc0500_vp01_10k_mid",  cz.PAL["blue"],   "--", r"$y_c=0.500$, $10^4$ MC + Mid"),
        ("st_yc0605_vp01_10k_hyb",  cz.PAL["orange"], "-",  r"$y_c=0.605$, $10^4$ Anti + GL4"),
        ("st_yc0605_vp01_10k_mid",  "0.55",           "--", r"$y_c=0.605$, $10^4$ MC + Mid"),
    ]
    for lbl, col, ls, leg in st_col_specs:
        nrp_p = os.path.join(W4B_BASE, "m5c", lbl, f"{lbl}.nrpic.hst")
        if not os.path.isfile(nrp_p):
            continue
        d = safe_loadtxt(nrp_p)
        if len(d) < 5:
            continue
        ax.plot(d[:, 0], d[:, 12], ls=ls, color=col, lw=1.35, label=leg)
        ah_p = os.path.join(W4B_BASE, "m5c", lbl, f"{lbl}.horizon_summary_0.txt")
        if os.path.isfile(ah_p):
            ah = safe_loadtxt(ah_p)
            ah = ah[np.isfinite(ah[:, 2])] if len(ah) else ah
            if len(ah):
                t_ah = float(ah[0, 1])
                idx_ah = int(np.argmin(np.abs(d[:, 0] - t_ah)))
                ax.plot([t_ah], [d[idx_ah, 12]], "o", color=col, ms=4.2, zorder=5)

    ax.set_xlim(0.0, 240.0)
    ax.set_ylim(-0.03, 0.99)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Central lapse $\alpha_c(t)$")
    ax.legend(loc="upper right", fontsize=6.1, frameon=False, labelspacing=0.22)
    ax.text(0.04, 0.16, "Circles mark\nfirst horizon", transform=ax.transAxes,
            ha="left", va="center", fontsize=6.8, color="0.3")

    os.makedirs(OUT_DIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT_DIR, f"fig_selfgrav_collapse_st.{ext}"), dpi=300)
    plt.close(fig)
    print(f"Saved fig_selfgrav_collapse_st in {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
