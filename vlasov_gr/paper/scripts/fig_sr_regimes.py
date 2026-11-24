#!/usr/bin/env python3
"""Publication figure: special-relativistic convergence and colliding-beam regimes."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
D1 = np.load(os.path.join(PAPER_DIR, "data/suite1_sr_flat.npz"))
DH = np.load(os.path.join(PAPER_DIR, "data/hybrid_speed_accuracy.npz"))
OUT_DIR = os.path.join(PAPER_DIR, "figures")


def main():
    cz.use_style()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.18, top=0.92, wspace=0.27)

    # Left panel: 3D warm-wave convergence + two-stream and free-streaming accuracy summary
    ax = axes[0]
    h = D1["s1b_h"]
    err = D1["s1b_l1_D"]
    p_fit = float(D1["s1b_p_fit"])
    ax.loglog(h, err, "o-", color=cz.PAL["red"], ms=4.5, lw=1.5,
              label=rf"Warm wave $L_1(D)$ (slope {p_fit:.2f})")
    ref_line = err[0] * (h / h[0]) ** 2
    ax.loglog(h, ref_line, label=r"$\propto h^2$ scaling", **cz.GUIDE)

    # Add collisionless colliding-beam L1 errors at x=1/150 effective resolution
    xb = DH["beam_xb_cent"]
    ex0 = DH["beam_exact_colless_D_bin"]
    l1_mfm0 = float(np.mean(np.abs(DH["beam_mfm_sig0_D_bin"] - ex0)) / np.mean(ex0))
    l1_hyb0 = float(np.mean(np.abs(DH["beam_hybrid_sig0_D_bin"] - ex0)) / np.mean(ex0))
    h_1d = 1.0 / 150.0

    ax.set_xticks([1.0 / 16.0, 1.0 / 12.0, 1.0 / 8.0])
    ax.set_xticklabels(["1/16", "1/12", "1/8"])
    cz.no_minor_labels(ax, "x")
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Element spacing $h$")
    ax.set_ylabel(r"$L_1(D - D_{\rm ref})$")
    ax.legend(loc="upper left", fontsize=8.0, frameon=False)

    sep_cov = float(D1["s1a_sep_cov"][-1])
    sep_von = float(D1["s1a_sep_von"][-1])
    note_txt = (
        rf"$|u|=3$ sep.: $C^{{eb}}$ {sep_cov:.2f}, $v$-only {sep_von:.2f}" "\n"
        rf"$\sigma=0$ beam $L_1$: SCP {l1_hyb0:.3f}, MFM {l1_mfm0:.3f}"
    )
    ax.text(0.97, 0.06, note_txt, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.6)

    # Right panel: 3D colliding beams across collisionality regimes
    ax = axes[1]
    ax.plot(xb, ex0, ":", lw=1.2, color="0.25", label=r"Exact $\sigma/\mu_p=0$")
    ax.plot(xb, DH["beam_mfm_sig0_D_bin"], "--", lw=1.1, color=cz.PAL["blue"], alpha=0.65,
            label=r"MFM $\sigma/\mu_p=0$")
    ax.plot(xb, DH["beam_hybrid_sig0_D_bin"], "-", lw=1.5, color=cz.PAL["blue"],
            label=r"SCP $\sigma/\mu_p=0$")
    ax.plot(DH["beam_hybrid_sig2_xs"], DH["beam_hybrid_sig2_Ds"], ".", ms=2.0, color=cz.PAL["orange"],
            label=r"AP-MFM $\sigma/\mu_p=2$")
    ax.plot(DH["beam_hybrid_sig15_xs"], DH["beam_hybrid_sig15_Ds"], ".", ms=2.0, color=cz.PAL["green"],
            label=r"AP-MFM $\sigma/\mu_p=15$")
    ax.plot(DH["beam_hybrid_sig1e4_xs"], DH["beam_hybrid_sig1e4_Ds"], "-", lw=1.4, color=cz.PAL["red"],
            label=r"AP-MFM $\sigma/\mu_p=10^4$")

    Vs = float(DH["beam_taub_Vs"])
    D2 = float(DH["beam_taub_D2"])
    x_sh = [0.5 - Vs * 0.55, 0.5 + Vs * 0.55]
    ax.plot([0.26, x_sh[0], x_sh[0], x_sh[1], x_sh[1], 0.74], [1.0, 1.0, D2, D2, 1.0, 1.0],
            color="k", ls="--", lw=1.2, label="Exact Taub")
    ax.set_xlim(0.26, 0.74)
    ax.set_ylim(0.45, 5.95)
    ax.set_xlabel(r"Position $x$")
    ax.set_ylabel(r"Lab rest-mass density $D(x)$")
    ax.legend(ncol=2, loc="upper center", fontsize=6.9, columnspacing=0.8, handlelength=1.4, frameon=False)

    os.makedirs(OUT_DIR, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT_DIR, f"fig_sr_regimes.{ext}"), dpi=300)
    print(f"Saved fig_sr_regimes in {OUT_DIR} (h_1d={h_1d:.4f})")


if __name__ == "__main__":
    main()
