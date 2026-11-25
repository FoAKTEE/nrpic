#!/usr/bin/env python3
"""Diagnostic figure: Iteration 4c Scheme A stage-accurate RK backreaction & ST nonlinear collapse.

Reads `vlasov_gr/paper/data/iter4_verify.npz` plus `.nrpic.hst` momentum/convergence time traces
from `$SCRATCH/runs/iter4_verify/` and Wave 4B ST baselines, saves compact curves to
`vlasov_gr/paper/data/iter4_stagea_curves.npz`, and renders
`vlasov_gr/paper/figures/fig_iter4_stageA_cfl_diagnostics.{pdf,png}`.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
I4_NPZ = os.path.join(PAPER_DIR, "data", "iter4_verify.npz")
DATA_OUT = os.path.join(PAPER_DIR, "data", "iter4_stagea_curves.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_iter4_stageA_cfl_diagnostics")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
I4_BASE = os.path.join(SCRATCH, "runs", "iter4_verify")
W4B_M5C = os.path.join(SCRATCH, "runs", "repro_wave4b", "m5c")


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


def p_drift_series(hst_path: str, max_pts: int = 450):
    nh = safe_loadtxt(hst_path)
    stride = max(1, len(nh) // max_pts)
    ns = nh[::stride]
    if ns[-1, 0] != nh[-1, 0]:
        ns = np.vstack([ns, nh[-1:]])
    m0 = max(float(nh[0, 3]), 1e-30)
    p = np.sqrt(ns[:, 5] ** 2 + ns[:, 6] ** 2 + ns[:, 7] ** 2) / m0
    return ns[:, 0].astype(np.float64), p.astype(np.float64)


def build_npz() -> dict:
    d4 = dict(np.load(I4_NPZ, allow_pickle=False))
    out = dict(d4)

    for lbl in ("st_herm_froz", "st_quin_stgA"):
        t, p = p_drift_series(os.path.join(I4_BASE, lbl, f"{lbl}.nrpic.hst"))
        out[f"{lbl}_pt"] = t
        out[f"{lbl}_pnorm"] = p

    for base_lbl in ("st_yc0500_vp01_10k_mid", "st_yc0500_vp01_100k_hyb"):
        t, p = p_drift_series(os.path.join(W4B_M5C, base_lbl, f"{base_lbl}.nrpic.hst"))
        out[f"ref_{base_lbl}_pt"] = t
        out[f"ref_{base_lbl}_pnorm"] = p

    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def main():
    cz.use_style()
    D = build_npz()

    fig, axes = plt.subplots(2, 2, figsize=(7.6, 5.9))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.095, top=0.955, wspace=0.29, hspace=0.33)

    # Top-Left: OS R0=5M (t=10.0M) CFL convergence of central lapse alpha_c(10M)
    ax = axes[0, 0]
    cfls = np.array([0.25, 0.125])
    f_errs = np.array([float(D["cfl_frozen_alpha_c_rel025"]), float(D["cfl_frozen_alpha_c_rel0125"])])
    s_errs = np.array([float(D["cfl_stageA_alpha_c_rel025"]), float(D["cfl_stageA_alpha_c_rel0125"])])
    pf = float(D["cfl_frozen_alpha_c_order"])
    ps = float(D["cfl_stageA_alpha_c_order"])

    ax.loglog(cfls, f_errs, "s--", color=cz.PAL["blue"], lw=1.6, ms=6.2,
              label=rf"Frozen $T_{{\mu\nu}}$ ($p={pf:.2f}$)")
    ax.loglog(cfls, s_errs, "o-", color=cz.PAL["red"], lw=1.7, ms=6.4,
              label=rf"Scheme A stage (Iter 4c, $p={ps:.2f}$)")

    # Reference slope lines
    href = np.array([0.11, 0.28])
    ax.loglog(href, 2.2e-3 * href, ":", color="0.45", lw=1.0, label=r"$\propto \Delta t^1$")
    ax.loglog(href, 1.0e-3 * (href ** 2), "-.", color="0.45", lw=1.0, label=r"$\propto \Delta t^2$")

    ax.text(0.175, float(np.sqrt(f_errs[0] * s_errs[0])),
            rf"${f_errs[0]/s_errs[0]:.0f}\times$ smaller" "\n" r"at $\nu_{\rm CFL}=0.25$",
            ha="center", va="center", fontsize=6.4, color=cz.PAL["red"])
    ax.annotate("", xy=(0.25, s_errs[0] * 1.15), xytext=(0.25, f_errs[0] * 0.85),
                arrowprops=dict(arrowstyle="<->", color=cz.PAL["red"], lw=1.0))

    ax.set_xlim(0.10, 0.30)
    ax.set_ylim(3.0e-6, 1.5e-3)
    ax.set_xticks([0.125, 0.25])
    ax.set_xticklabels(["0.125", "0.25"])
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Courant number $\nu_{\rm CFL}$")
    ax.set_ylabel(r"$|\alpha_c(10M)/\alpha_c^{\rm ref}(10M) - 1|$")
    ax.legend(loc="lower right", fontsize=5.9, frameon=False)

    # Top-Right: OS t=25M ||H||_2(t) + horizon mass M_AH summary
    ax = axes[0, 1]
    os_specs = [
        ("os_gpu4_quin_stgA", cz.PAL["red"],    "-",  1.80, 2,
         rf"Quintic + Scheme A ($M_{{\rm AH}}={float(D['os_gpu4_quin_stgA_M_AH']):.5f}M$)"),
        ("os_gpu4_quin_froz", cz.PAL["orange"], "-.", 1.45, 3,
         rf"Quintic + Frozen ($M_{{\rm AH}}={float(D['os_gpu4_quin_froz_M_AH']):.5f}M$)"),
        ("os_gpu4_herm_froz", cz.PAL["blue"],   "--", 1.30, 4,
         rf"Hermite + Frozen ($M_{{\rm AH}}={float(D['os_gpu4_herm_froz_M_AH']):.5f}M$)"),
    ]
    for lbl, col, ls, lw, zo, leg in os_specs:
        ax.semilogy(D[f"{lbl}_zt"], D[f"{lbl}_H"], color=col, ls=ls, lw=lw, zorder=zo, label=leg)
    ax.axvline(float(D["os_gpu4_herm_froz_t_AH"]), color=cz.PAL["blue"], ls=":", lw=0.95, alpha=0.65)
    ax.axvline(float(D["os_gpu4_quin_stgA_t_AH"]), color=cz.PAL["red"], ls=":", lw=0.95, alpha=0.75)
    ax.set_xlim(0.0, 25.0)
    ax.set_ylim(1.1e-1, 4.2)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Hamiltonian norm $\|\mathcal{H}\|_2$")
    ax.text(0.04, 0.94,
            "OS collapse ($R_0=5M$, $t_{\\rm AH}$):\n"
            r"Frozen: $16.39M \to$ Scheme A: $16.20M$" "\n"
            r"$M_{\rm AH}$ error halved ($1.58\to 0.77\times 10^{-3}$)",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.1, color="0.22")
    ax.legend(loc="lower right", fontsize=5.7, frameon=False)

    # Bottom-Left: ST yc=0.500 10k Anti QMC alpha_c(t) & ||H||_2 (twin or overlaid lapse + H)
    ax = axes[1, 0]
    for lbl, col, ls, leg in [
        ("st_herm_froz", cz.PAL["blue"], "--",
         rf"Hermite + Frozen ($t_{{\rm AH}}={float(D['st_herm_froz_t_AH']):.2f}M$)"),
        ("st_quin_stgA", cz.PAL["red"],  "-",
         rf"Quintic + Scheme A ($t_{{\rm AH}}={float(D['st_quin_stgA_t_AH']):.2f}M$)"),
    ]:
        ax.plot(D[f"{lbl}_t"], D[f"{lbl}_ac"], color=col, ls=ls, lw=1.6, label=leg)
        tah = float(D[f"{lbl}_t_AH"])
        idx = int(np.argmin(np.abs(D[f"{lbl}_t"] - tah)))
        ax.plot([tah], [D[f"{lbl}_ac"][idx]], "o", color=col, ms=4.8, mec="k", mew=0.5, zorder=5)
    ax.set_xlim(0.0, 90.0)
    ax.set_ylim(-0.03, 0.65)
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Central lapse $\alpha_c(t)$")
    ax.text(0.04, 0.16,
            r"ST cluster $y_c=0.500$ ($10^4$, 9-lvl AMR)" "\n"
            rf"Herm+Froz: $M_{{\rm AH}}={float(D['st_herm_froz_M_AH']):.5f}M$" "\n"
            rf"Quin+StgA: $M_{{\rm AH}}={float(D['st_quin_stgA_M_AH']):.5f}M$",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=6.2, color="0.22")
    ax.legend(loc="upper right", fontsize=6.0, frameon=False)

    # Bottom-Right: Dynamic 9-level AMR Linear Momentum Drift |P|/M_0 (densitized leak vs mcons+stgA)
    ax = axes[1, 1]
    mom_specs = [
        ("ref_st_yc0500_vp01_10k_mid",  "0.45",           ":",  r"MC ($10^4$, plain filter)"),
        ("ref_st_yc0500_vp01_100k_hyb", cz.PAL["orange"], "-.", r"Anti/Leb ($10^5$, densitized AMR)"),
        ("st_herm_froz",                cz.PAL["blue"],   "--", r"Anti QMC ($10^4$, mcons + Hermite)"),
        ("st_quin_stgA",                cz.PAL["red"],    "-",  r"Anti QMC ($10^4$, mcons + Quin + StgA)"),
    ]
    for lbl, col, ls, leg in mom_specs:
        t = D[f"{lbl}_pt"]
        p = np.maximum(D[f"{lbl}_pnorm"], 1.0e-18)
        m = p > 5.0e-18  # hide post-total-excision zero points on log plot cleanly
        if np.any(m):
            ax.semilogy(t[m], p[m], color=col, ls=ls, lw=1.45, label=leg)
    ax.set_xlim(0.0, 90.0)
    ax.set_ylim(1.0e-17, 2.0e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Linear momentum drift $|\mathbf{P}|/M_0$")
    ax.text(0.04, 0.94,
            "9-lvl dynamic AMR symmetry:\n"
            r"mcons cures $10^{-6}$ AMR leakage ($\sim 10^{8}\times$)",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.1, color="0.22")
    ax.legend(loc="center left", bbox_to_anchor=(0.02, 0.34), fontsize=5.8, frameon=False)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
