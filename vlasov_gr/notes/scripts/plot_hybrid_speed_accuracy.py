#!/usr/bin/env python3
"""Diagnostic 2x2 summary for internal engineering notes (with B200 timings)."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

REPO_ROOT = "/home/schmidt/ssci-haiyangw/nrpic"
DH = np.load(os.path.join(REPO_ROOT, "vlasov_gr/paper/data/hybrid_speed_accuracy.npz"))
OUT_PNG = os.path.join(REPO_ROOT, "vlasov_gr/notes/figs/diag_hybrid_speed_accuracy.png")


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.6))
    fig.subplots_adjust(left=0.095, right=0.98, bottom=0.085, top=0.935, wspace=0.28, hspace=0.35)

    # Top-Left: Suite 1D collisionless vs exact & collisional Taub
    ax = axes[0, 0]
    xb = DH["s1d_xb_cent"]
    ex0 = DH["s1d_exact_colless_D_bin"]
    ax.plot(xb, ex0, ":", color="0.25", lw=1.2, label=r"Exact $\sigma=0$")
    ax.plot(xb, DH["s1d_mfm_sig0_D_bin"], "--", color=cz.PAL["orange"], lw=1.2,
            label=rf"MFM $\sigma=0$ ({float(DH['s1d_mfm_sig0_wall_s']):.2f}s)")
    ax.plot(xb, DH["s1d_hybrid_sig0_D_bin"], "-", color=cz.PAL["blue"], lw=1.5,
            label=rf"Hybrid SCP $\sigma=0$ ({float(DH['s1d_hybrid_sig0_wall_s']):.2f}s)")
    ax.plot(DH["s1d_hybrid_sig1e4_xs"], DH["s1d_hybrid_sig1e4_Ds"], "-", color=cz.PAL["red"], lw=1.4,
            label=rf"Hybrid AP $\sigma=10^4$ ({float(DH['s1d_hybrid_sig1e4_wall_s']):.2f}s)")
    Vs = float(DH["s1d_taub_Vs"]); D2 = float(DH["s1d_taub_D2"])
    x_sh = [0.5 - Vs * 0.55, 0.5 + Vs * 0.55]
    ax.plot([0.26, x_sh[0], x_sh[0], x_sh[1], x_sh[1], 0.74], [1.0, 1.0, D2, D2, 1.0, 1.0],
            color="k", ls="--", lw=1.2, label="Exact Taub")
    ax.set_xlim(0.26, 0.74)
    ax.set_ylim(0.45, 5.75)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$D(x)$")
    ax.set_title("Suite 1D: Automatic SCP / AP switching")
    ax.legend(loc="upper center", ncol=2, fontsize=6.9, columnspacing=0.8)

    # Top-Right: Suite 2 B200 Wall & Compute Runtime Comparison
    ax = axes[0, 1]
    labels = ["Base\nMFM", "Opt MFM\nn18", "MC 10k", "Hybrid\nn14/q14", "Hybrid\nn18/q14"]
    wall_vals = [
        float(DH["base_mfm_s2_n18_wall_s"]),
        float(DH["s2_opt_n18_wall_s"]),
        float(DH["s2_mc10k_wall_s"]),
        float(DH["s2_hyb_n14_q14_wall_s"]),
        float(DH["s2_hyb_n18_q14_wall_s"]),
    ]
    comp_vals = [
        np.nan,
        float(DH["s2_opt_n18_comp_s"]),
        float(DH["s2_mc10k_comp_s"]),
        float(DH["s2_hyb_n14_q14_comp_s"]),
        float(DH["s2_hyb_n18_q14_comp_s"]),
    ]
    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, wall_vals, width=0.55,
                  color=["0.5", cz.PAL["orange"], cz.PAL["blue"], cz.PAL["green"], cz.PAL["red"]],
                  alpha=0.88)
    ax.set_yscale("log")
    ax.set_ylim(0.3, 140.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=7.8)
    ax.set_ylabel("B200 runtime [s]")
    ax.set_title(r"Suite 2 Kerr $a=0.9M$ runtime ($t=30M$)")
    for i, b in enumerate(bars):
        sp = wall_vals[0] / wall_vals[i]
        c_txt = f"\n({comp_vals[i]:.2f}s)" if np.isfinite(comp_vals[i]) else ""
        lbl_t = f"{wall_vals[i]:.2f}s\n({sp:.1f}x){c_txt}" if i > 0 else f"{wall_vals[i]:.1f}s"
        ax.text(b.get_x() + b.get_width() / 2.0, wall_vals[i] * 1.12, lbl_t,
                ha="center", va="bottom", fontsize=6.6)

    # Bottom-Left: Suite 2 Pareto Error vs Wall Speedup
    ax = axes[1, 0]
    t_b = wall_vals[0]
    ax.loglog([1.0], [float(DH["s2_opt_n18_l1_hist"])], "D", color="0.4", ms=6, label="Base MFM")
    opt_k = ("s2_opt_n10", "s2_opt_n14", "s2_opt_n18")
    ax.loglog([t_b / float(DH[f"{k}_comp_s"]) for k in opt_k],
              [float(DH[f"{k}_l1_hist"]) for k in opt_k],
              "s-", color=cz.PAL["orange"], ms=5, label="Opt MFM (compute ratio)")
    ax.loglog([t_b / float(DH["s2_mc10k_comp_s"])], [float(DH["s2_mc10k_l1_hist"])],
              "P", color=cz.PAL["blue"], ms=7, label="NRPIC MC 10k")
    hyb_k = ("s2_hyb_n10_q14", "s2_hyb_n14_q14", "s2_hyb_n18_q8", "s2_hyb_n18_q14")
    ax.loglog([t_b / float(DH[f"{k}_comp_s"]) for k in hyb_k],
              [float(DH[f"{k}_l1_hist"]) for k in hyb_k],
              "o-", color=cz.PAL["red"], ms=5.5, label="Hybrid SCP-AP")
    ax.set_xlabel(r"Compute speedup over baseline MFM ($\times$)")
    ax.set_ylabel(r"Normalized PDF $L_1$ error vs MC $10^5$")
    ax.set_title("Suite 2 speed-accuracy Pareto frontier")
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.legend(loc="lower left", fontsize=7.2)

    # Bottom-Right: B200 50-cycle Strong Scaling
    ax = axes[1, 1]
    ax.loglog(DH["sc_mfm_N"], DH["sc_mfm_comp_s"], "s-", color=cz.PAL["orange"], ms=5, label="Opt MFM")
    ax.loglog(DH["sc_hyb_N"], DH["sc_hyb_comp_s"], "o-", color=cz.PAL["red"], ms=5, label="Hybrid SCP-AP (q=14)")
    ax.loglog(DH["sc_mc_N"], DH["sc_mc_comp_s"], "^--", color=cz.PAL["blue"], ms=4.5, label="NRPIC MC")
    ax.set_xlabel(r"Active elements / packets $N_{\rm eff}$")
    ax.set_ylabel("50-cycle B200 compute time [s]")
    ax.set_title("B200 strong scaling (Kerr cloud)")
    ax.set_ylim(3.0e-3, 1.8)
    cz.no_minor_labels(ax, "x")
    cz.no_minor_labels(ax, "y")
    ax.legend(loc="upper left", fontsize=7.2)

    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    fig.savefig(OUT_PNG, dpi=300)
    print(f"Saved diagnostic figure: {OUT_PNG}")


if __name__ == "__main__":
    main()
