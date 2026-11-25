#!/usr/bin/env python3
"""Remade PRX figure: Special-relativistic convergence and optical-depth crossover."""
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
D1 = np.load(PAPER_DIR / "data" / "suite1_sr_flat.npz")
DH = np.load(PAPER_DIR / "data" / "hybrid_speed_accuracy.npz")
DP = np.load(PAPER_DIR / "data" / "pbgk_crossover.npz")
OUT = PAPER_DIR / "figures" / "fig_sr_crossover"


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.8))
    fig.subplots_adjust(left=0.105, right=0.98, bottom=0.09, top=0.955, wspace=0.28, hspace=0.33)

    # Top-Left: Warm-wave convergence + two-stream and collisionless summary
    ax = axes[0, 0]
    h = D1["s1b_h"]
    err = D1["s1b_l1_D"]
    p_fit = float(D1["s1b_p_fit"])
    ax.loglog(h, err, "o-", color=cz.PAL["red"], ms=5.0, lw=1.6,
              label=rf"Warm wave $L_1(D)$ (slope {p_fit:.2f})")
    ref_line = err[0] * (h / h[0]) ** 2
    ax.loglog(h, ref_line, label=r"$\propto h^2$ scaling", **cz.GUIDE)

    ex0 = DH["s1d_exact_colless_D_bin"]
    l1_mfm0 = float(np.mean(np.abs(DH["s1d_mfm_sig0_D_bin"] - ex0)) / np.mean(ex0))
    l1_scp0 = float(np.mean(np.abs(DH["s1d_hybrid_sig0_D_bin"] - ex0)) / np.mean(ex0))

    ax.set_xticks([1.0 / 16.0, 1.0 / 12.0, 1.0 / 8.0])
    ax.set_xticklabels(["1/16", "1/12", "1/8"])
    cz.no_minor_labels(ax, "x")
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Element spacing $h$", labelpad=1)
    ax.set_ylabel(r"Density error $L_1(D - D_{\rm ref})$")
    ax.legend(loc="upper left", fontsize=7.8, frameon=False)

    sep_cov = float(D1["s1a_sep_cov"][-1])
    sep_von = float(D1["s1a_sep_von"][-1])
    ax.text(0.96, 0.06,
            rf"$|u|=3$ sep.: $C^{{eb}}$ {sep_cov:.2f}, $v$-only {sep_von:.2f}" "\n"
            rf"$\sigma=0$ beam $L_1$: SCP {l1_scp0:.3f}, MFM {l1_mfm0:.3f}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.3, color="0.20")

    # Top-Right: Relativistic optical-depth beam crossover D(x) at t = 0.65
    ax = axes[0, 1]
    x = DP["xb_cent"]
    D2_w = float(DP["warm_taub_D2"])
    Vs_w = float(DP["warm_taub_Vs"])
    t_end = 0.65
    x_lo = 0.5 - Vs_w * t_end
    x_hi = 0.5 + Vs_w * t_end
    x_taub = np.array([0.22, x_lo, x_lo, x_hi, x_hi, 0.78])

    ax.plot(x, DP["pbgk_sig0_D_bin"], "-", lw=1.6, color=cz.PAL["blue"], label=r"Cell-BGK ($\sigma/\mu_p=0$)")
    ax.plot(x, DP["mfm_sig0_D_bin"], ":", lw=1.35, color=cz.PAL["blue"], label=r"AP-MFM ($\sigma/\mu_p=0$)")
    ax.plot(x, DP["pbgk_sig2_D_bin"], "-", lw=1.45, color=cz.PAL["orange"], label=r"Cell-BGK ($\sigma/\mu_p=2$)")
    ax.plot(x, DP["pbgk_sig15_D_bin"], "-", lw=1.45, color=cz.PAL["green"], label=r"Cell-BGK ($\sigma/\mu_p=15$)")
    ax.plot(x, DP["pbgk_sig1e4_D_bin"], "-", lw=1.65, color=cz.PAL["red"], label=r"Cell-BGK ($\sigma/\mu_p=10^4$)")
    ax.plot(x, DP["mfm_sig1e4_D_bin"], "-.", lw=1.15, color="0.40", label=r"AP-MFM ($\sigma/\mu_p=10^4$)")
    ax.plot(x_taub, [1.0, 1.0, D2_w, D2_w, 1.0, 1.0], color="k", ls="--", lw=1.25, label="Exact Taub")
    ax.set_xlim(0.22, 0.78)
    ax.set_ylim(0.55, 6.25)
    ax.set_xlabel(r"Position $x$", labelpad=-1)
    ax.set_ylabel(r"Lab rest-mass density $D(x)$")
    ax.legend(ncol=2, loc="upper center", fontsize=6.6, columnspacing=0.75, handlelength=1.4, frameon=False)

    # Bottom-Left: Normalized compute cost vs optical depth
    ax = axes[1, 0]
    cats = np.arange(4)
    c_ref = float(DP["nrpic_comp_s"][0])
    c_pbgk = DP["pbgk_comp_s"] / c_ref
    c_mfm = DP["mfm_comp_s"] / c_ref
    c_mc = DP["nrpic_comp_s"] / c_ref

    ax.plot(cats, c_pbgk, "o-", color=cz.PAL["red"], ms=5.2, lw=1.6, label="Cell-BGK")
    ax.plot(cats, c_mfm, "s--", color=cz.PAL["orange"], ms=4.8, lw=1.45, label="AP-MFM")
    ax.plot(cats[:3], c_mc[:3], "^:", color=cz.PAL["blue"], ms=5.2, lw=1.45, label="MC PIC")
    ax.plot(cats[2:], c_mc[2:], ":", color=cz.PAL["blue"], lw=1.35)
    ax.plot([cats[3]], [c_mc[3]], "^", color=cz.PAL["blue"], mfc="white", ms=5.8, mew=1.3,
            label="MC (projected)")
    ax.annotate("", xy=(3.0, c_pbgk[3] * 1.45), xytext=(3.0, c_mc[3] * 0.72),
                arrowprops=dict(arrowstyle="<->", color="0.35", lw=1.0))
    speedup = float(c_mc[3] / c_pbgk[3])
    ax.text(2.88, np.sqrt(c_pbgk[3] * c_mc[3]), rf"{speedup:.0f}$\times$ faster",
            ha="right", va="center", fontsize=7.8, color="0.20")

    ax.set_yscale("log")
    ax.set_xticks(cats)
    ax.set_xticklabels([r"$0$", r"$2$", r"$15$", r"$10^4$"])
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.35, 3.35)
    ax.set_ylim(0.75, 420.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Dimensionless cross section $\sigma/\mu_p$", labelpad=-1)
    ax.set_ylabel(r"Normalized cost $T_{\rm step}/T_{\rm MC}(0)$")
    ax.legend(loc="upper left", fontsize=7.5, frameon=False)

    # Bottom-Right: Global energy conservation error across optical depths
    ax = axes[1, 1]
    floor = 1.0e-16
    e_pbgk = np.maximum(DP["pbgk_de"], floor)
    e_mfm = np.maximum(DP["mfm_de"], floor)
    e_mc = np.maximum(DP["nrpic_de"][:3], floor)

    ax.plot(cats, e_pbgk, "o-", color=cz.PAL["red"], ms=5.2, lw=1.6, label="Cell-BGK")
    ax.plot(cats, e_mfm, "s--", color=cz.PAL["orange"], ms=4.8, lw=1.45, label="AP-MFM")
    ax.plot(cats[:3], e_mc, "^:", color=cz.PAL["blue"], ms=5.2, lw=1.45, label="MC PIC")
    ax.axhline(floor, color="grey", lw=0.9, ls="--", alpha=0.55)
    ax.text(3.25, floor * 2.2, r"rounding floor ($\leq 10^{-16}$)",
            ha="right", va="bottom", fontsize=7.0, color="0.35")

    ax.set_yscale("log")
    ax.set_xticks(cats)
    ax.set_xticklabels([r"$0$", r"$2$", r"$15$", r"$10^4$"])
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.35, 3.35)
    ax.set_ylim(2.0e-17, 1.8e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Dimensionless cross section $\sigma/\mu_p$", labelpad=-1)
    ax.set_ylabel(r"Global energy drift $\max|\Delta E/E_0|$")
    ax.legend(loc="upper right", fontsize=7.5, frameon=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
