#!/usr/bin/env python3
"""Publication figure: Relativistic Cell-BGK vs AP-MFM vs MC PIC optical-depth crossover."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA = np.load(os.path.join(PAPER_DIR, "data/pbgk_crossover.npz"))
OUT_DIR = os.path.join(PAPER_DIR, "figures")


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.095, top=0.955, wspace=0.28, hspace=0.33)

    x = DATA["xb_cent"]
    D2_w = float(DATA["warm_taub_D2"])
    e2_w = float(DATA["warm_taub_e2"])
    Vs_w = float(DATA["warm_taub_Vs"])
    t_end = 0.65
    x_lo = 0.5 - Vs_w * t_end
    x_hi = 0.5 + Vs_w * t_end
    x_taub = np.array([0.22, x_lo, x_lo, x_hi, x_hi, 0.78])

    # Top-Left: Lab density D(x) across four orders of magnitude in sigma/mu_p
    ax = axes[0, 0]
    ax.plot(x, DATA["pbgk_sig0_D_bin"], "-", lw=1.5, color=cz.PAL["blue"],
            label=r"Cell-BGK ($\sigma/\mu_p=0$)")
    ax.plot(x, DATA["mfm_sig0_D_bin"], ":", lw=1.3, color=cz.PAL["blue"],
            label=r"AP-MFM ($\sigma/\mu_p=0$)")
    ax.plot(x, DATA["pbgk_sig2_D_bin"], "-", lw=1.4, color=cz.PAL["orange"],
            label=r"Cell-BGK ($\sigma/\mu_p=2$)")
    ax.plot(x, DATA["pbgk_sig15_D_bin"], "-", lw=1.4, color=cz.PAL["green"],
            label=r"Cell-BGK ($\sigma/\mu_p=15$)")
    ax.plot(x, DATA["pbgk_sig1e4_D_bin"], "-", lw=1.6, color=cz.PAL["red"],
            label=r"Cell-BGK ($\sigma/\mu_p=10^4$)")
    ax.plot(x, DATA["mfm_sig1e4_D_bin"], "-.", lw=1.1, color="0.40",
            label=r"AP-MFM ($\sigma/\mu_p=10^4$)")
    ax.plot(x_taub, [1.0, 1.0, D2_w, D2_w, 1.0, 1.0],
            color="k", ls="--", lw=1.2, label="Exact Taub")
    ax.set_xlim(0.22, 0.78)
    ax.set_ylim(0.55, 5.75)
    ax.set_xlabel(r"Position $x$")
    ax.set_ylabel(r"Lab rest-mass density $D(x)$")
    ax.legend(ncol=2, loc="upper center", fontsize=6.4, columnspacing=0.7, handlelength=1.4, frameon=False)

    # Top-Right: Energy density e(x) at transitional (15) and hydrodynamic (10^4) coupling
    ax = axes[0, 1]
    ax.plot(x, DATA["pbgk_sig15_e_bin"], "-", lw=1.4, color=cz.PAL["green"],
            label=r"Cell-BGK ($\sigma/\mu_p=15$)")
    ax.plot(x, DATA["mfm_sig15_e_bin"], "--", lw=1.2, color=cz.PAL["orange"],
            label=r"AP-MFM ($\sigma/\mu_p=15$)")
    ax.plot(x, DATA["nrpic_sig15_e_bin"], ":", lw=1.3, color=cz.PAL["blue"],
            label=r"MC PIC ($\sigma/\mu_p=15$)")
    ax.plot(x, DATA["pbgk_sig1e4_e_bin"], "-", lw=1.6, color=cz.PAL["red"],
            label=r"Cell-BGK ($\sigma/\mu_p=10^4$)")
    ax.plot(x, DATA["mfm_sig1e4_e_bin"], "-.", lw=1.1, color="0.40",
            label=r"AP-MFM ($\sigma/\mu_p=10^4$)")
    e1_w = 1.166190378969  # warm upstream energy per rest mass sqrt(1 + 0.6^2 + 3*0.03^2)
    ax.plot(x_taub, [e1_w, e1_w, e2_w, e2_w, e1_w, e1_w],
            color="k", ls="--", lw=1.2, label="Exact Taub")
    ax.set_xlim(0.22, 0.78)
    ax.set_ylim(0.75, 6.45)
    ax.set_xlabel(r"Position $x$")
    ax.set_ylabel(r"Normal energy density $E(x)$")
    ax.legend(ncol=2, loc="upper center", fontsize=6.4, columnspacing=0.7, handlelength=1.4, frameon=False)

    # Bottom-Left: Normalized compute cost vs optical depth
    ax = axes[1, 0]
    cats = np.arange(4)
    c_ref = float(DATA["nrpic_comp_s"][0])
    c_pbgk = DATA["pbgk_comp_s"] / c_ref
    c_mfm = DATA["mfm_comp_s"] / c_ref
    c_mc = DATA["nrpic_comp_s"] / c_ref

    ax.plot(cats, c_pbgk, "o-", color=cz.PAL["red"], ms=5.0, lw=1.6, label="Cell-BGK")
    ax.plot(cats, c_mfm, "s--", color=cz.PAL["orange"], ms=4.8, lw=1.4, label="AP-MFM")
    ax.plot(cats[:3], c_mc[:3], "^:", color=cz.PAL["blue"], ms=5.2, lw=1.4, label="MC PIC")
    ax.plot(cats[2:], c_mc[2:], ":", color=cz.PAL["blue"], lw=1.3)
    ax.plot([cats[3]], [c_mc[3]], "^", color=cz.PAL["blue"], mfc="white", ms=5.6, mew=1.3,
            label="MC (projected)")
    ax.annotate("", xy=(3.0, c_pbgk[3] * 1.45), xytext=(3.0, c_mc[3] * 0.72),
                arrowprops=dict(arrowstyle="<->", color="0.35", lw=1.0))
    speedup = float(c_mc[3] / c_pbgk[3])
    ax.text(2.88, np.sqrt(c_pbgk[3] * c_mc[3]), rf"{speedup:.0f}$\times$ faster",
            ha="right", va="center", fontsize=7.8, color="0.2")

    ax.set_yscale("log")
    ax.set_xticks(cats)
    ax.set_xticklabels([r"$0$", r"$2$", r"$15$", r"$10^4$"])
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.35, 3.35)
    ax.set_ylim(0.75, 420.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Dimensionless cross section $\sigma/\mu_p$")
    ax.set_ylabel(r"Relative compute cost $T_{\rm comp}/T_{\rm MC}(0)$")
    ax.legend(loc="upper left", fontsize=7.2, frameon=False)

    # Bottom-Right: Global energy conservation error across optical depths
    ax = axes[1, 1]
    floor = 1.0e-16
    e_pbgk = np.maximum(DATA["pbgk_de"], floor)
    e_mfm = np.maximum(DATA["mfm_de"], floor)
    e_mc = np.maximum(DATA["nrpic_de"][:3], floor)

    ax.plot(cats, e_pbgk, "o-", color=cz.PAL["red"], ms=5.0, lw=1.6, label="Cell-BGK")
    ax.plot(cats, e_mfm, "s--", color=cz.PAL["orange"], ms=4.8, lw=1.4, label="AP-MFM")
    ax.plot(cats[:3], e_mc, "^:", color=cz.PAL["blue"], ms=5.2, lw=1.4, label="MC PIC")
    ax.axhline(floor, color="grey", lw=0.9, ls="--", alpha=0.55)
    ax.text(3.25, floor * 0.72, r"machine floor ($\leq 10^{-16}$)",
            ha="right", va="top", fontsize=6.9, color="0.35")

    ax.set_yscale("log")
    ax.set_xticks(cats)
    ax.set_xticklabels([r"$0$", r"$2$", r"$15$", r"$10^4$"])
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.35, 3.35)
    ax.set_ylim(1.2e-17, 1.8e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Dimensionless cross section $\sigma/\mu_p$")
    ax.set_ylabel(r"Global energy drift $\max|\Delta E/E_0|$")
    ax.legend(loc="upper right", fontsize=7.2, frameon=False)

    os.makedirs(OUT_DIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT_DIR, f"fig_pbgk_crossover.{ext}"), dpi=300)
    print(f"Saved fig_pbgk_crossover in {OUT_DIR} (speedup={speedup:.1f}x)")


if __name__ == "__main__":
    main()
