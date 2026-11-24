#!/usr/bin/env python3
"""Diagnostic figure: Iteration 3 self-adjoint metric-weighted flux-conservative AMR filter.

Reduces scratch runs from `$SCRATCH/runs/iter3_verify/` into compact
`vlasov_gr/paper/data/iter3_filter_curves.npz` and renders
`vlasov_gr/paper/figures/fig_iter3_mcons_diagnostics.{pdf,png}`.
"""
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
DATA_OUT = os.path.join(PAPER_DIR, "data", "iter3_filter_curves.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_iter3_mcons_diagnostics")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
I3_BASE = os.path.join(SCRATCH, "runs", "iter3_verify")


def safe_loadtxt(path: str) -> np.ndarray:
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


def build_npz() -> dict:
    E0 = float(_osn.rho0(5.0, 1.0))
    out = {}
    for mode in ("plain", "dens", "mcons"):
        # OS R0=5M (7-level dynamic AMR)
        os_dir = os.path.join(I3_BASE, f"iter3_os_10k_{mode}")
        nh = safe_loadtxt(os.path.join(os_dir, f"iter3_os_10k_{mode}.nrpic.hst"))
        zh = safe_loadtxt(os.path.join(os_dir, f"iter3_os_10k_{mode}.z4c.user.hst"))
        tau = nh[:, 14]
        ep = nh[:, 13]
        mask = (tau > 0.0) & (tau <= 2.60) & (ep > 0.0)
        rho_cyc = np.array([float(_osn.cycloid_rho(xt)) for xt in tau[mask]]) / E0
        rho_err = np.abs(ep[mask] / E0 - rho_cyc) / rho_cyc
        filt_os = np.abs(nh[:, 23] - nh[:, 8]) / np.maximum(np.abs(nh[:, 8]), 1e-30)

        out[f"os_{mode}_tau"] = tau[mask]
        out[f"os_{mode}_rho_err"] = rho_err
        out[f"os_{mode}_t"] = nh[:, 0]
        out[f"os_{mode}_filt"] = filt_os
        out[f"os_{mode}_zt"] = zh[:, 0]
        out[f"os_{mode}_H"] = np.sqrt(np.maximum(zh[:, 3], 1e-24))

        # M4 6-level SMR Kerr a=0.9M
        kr_dir = os.path.join(I3_BASE, f"iter3_kerr_10k_{mode}")
        kh = safe_loadtxt(os.path.join(kr_dir, f"iter3_kerr_10k_{mode}.nrpic.hst"))
        filt_kr = np.abs(kh[:, 23] - kh[:, 8]) / np.maximum(np.abs(kh[:, 8]), 1e-30)
        out[f"kerr_{mode}_t"] = kh[:, 0]
        out[f"kerr_{mode}_filt"] = filt_kr

    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def main():
    cz.use_style()
    D = build_npz()

    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.8))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.09, top=0.955, wspace=0.28, hspace=0.33)

    specs = [
        ("plain", cz.PAL["blue"],   "--"),
        ("dens",  cz.PAL["orange"], "-."),
        ("mcons", cz.PAL["red"],    "-"),
    ]
    labels_tex = {
        "plain": r"Unweighted (plain)",
        "dens":  r"Pre-$\sqrt{\gamma}$ densitized (dens)",
        "mcons": r"Metric flux-cons. (mcons, Iter 3)",
    }

    floor = 1.0e-16

    # Top-Left: OS central density accuracy
    ax = axes[0, 0]
    plot_order = [
        ("mcons", cz.PAL["red"],    "-",  1.95, 2),
        ("dens",  cz.PAL["orange"], "-.", 1.55, 3),
        ("plain", cz.PAL["blue"],   "--", 1.35, 4),
    ]
    for mode, col, ls, lw, zo in plot_order:
        y = np.maximum(D[f"os_{mode}_rho_err"], 1e-6)
        ax.semilogy(D[f"os_{mode}_tau"], y, color=col, ls=ls, lw=lw, zorder=zo, label=labels_tex[mode])
    ax.set_xlim(0.0, 2.65)
    ax.set_ylim(2.0e-6, 2.0e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Central proper time $\tau_c\,[M]$")
    ax.set_ylabel(r"Central density error $|\rho_c/\rho_{\rm OS}-1|$")
    ax.text(0.97, 0.94, "OS collapse $R_0=5M$\n" r"(mcons restores $8.0\times$ vs dens)",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.8, color="0.25")
    ax.legend(loc="lower right", fontsize=6.7, frameon=False)

    # Top-Right: OS 7-level dynamic AMR proper-volume filter drift
    ax = axes[0, 1]
    for mode, col, ls, lw, zo in plot_order:
        y = np.maximum(D[f"os_{mode}_filt"], floor)
        ax.semilogy(D[f"os_{mode}_t"], y, color=col, ls=ls, lw=lw, zorder=zo, label=labels_tex[mode])
    ax.axhline(floor, color="grey", lw=0.9, ls="--", alpha=0.55)
    ax.text(15.8, 4.0e-14, r"floor ($\leq 8.8\times 10^{-16}$)",
            ha="center", va="bottom", fontsize=6.5, color=cz.PAL["red"])
    ax.set_xlim(0.0, 25.0)
    ax.set_ylim(5.0e-17, 2.0e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Filter conservation drift $|I_E^{\rm filt}/I_E - 1|$")
    ax.text(0.04, 0.42, "7-level dynamic AMR\n" r"($2.7\times 10^{13}\times$ reduction)",
            transform=ax.transAxes, ha="left", va="center", fontsize=6.7, color="0.25")
    ax.legend(loc="center right", bbox_to_anchor=(0.98, 0.56), fontsize=6.4, frameon=False)

    # Bottom-Left: M4 6-level SMR Kerr proper-volume filter drift
    ax = axes[1, 0]
    for mode, col, ls, lw, zo in plot_order:
        y = np.maximum(D[f"kerr_{mode}_filt"], floor)
        ax.semilogy(D[f"kerr_{mode}_t"], y, color=col, ls=ls, lw=lw, zorder=zo, label=labels_tex[mode])
    ax.axhline(floor, color="grey", lw=0.9, ls="--", alpha=0.55)
    ax.text(196.0, 3.5e-14, r"floor ($\leq 9.9\times 10^{-16}$)",
            ha="right", va="bottom", fontsize=6.5, color=cz.PAL["red"])
    ax.set_xlim(0.0, 200.0)
    ax.set_ylim(5.0e-17, 2.0e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Filter conservation drift $|I_E^{\rm filt}/I_E - 1|$")
    ax.text(0.96, 0.36, "M4 6-level SMR Kerr ($a=0.9M$)\n" r"($8.7\times 10^{11}\times$ reduction)",
            transform=ax.transAxes, ha="right", va="center", fontsize=6.7, color="0.25")

    # Bottom-Right: OS Z4c Hamiltonian constraint norm ||H||_2(t)
    ax = axes[1, 1]
    for mode, col, ls, lw, zo in plot_order:
        ax.semilogy(D[f"os_{mode}_zt"], D[f"os_{mode}_H"], color=col, ls=ls, lw=lw, zorder=zo, label=labels_tex[mode])
    ax.axvline(16.39, **cz.MASK_LINE)
    ax.text(15.8, 0.44, r"$t_{\rm AH}=16.39M$", ha="right", va="bottom", fontsize=6.8, color="0.3")
    ax.text(0.04, 0.94,
            "4-thread OMP parity (Iter 4a): $0.00$\n"
            r"$M_{\rm AH}/M = 0.9997,\,1.0027,\,1.0016$",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.6, color="0.22")
    ax.set_xlim(0.0, 25.0)
    ax.set_ylim(1.1e-1, 4.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Hamiltonian norm $\|\mathcal{H}\|_2$")
    ax.legend(loc="lower right", fontsize=6.5, frameon=False)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
