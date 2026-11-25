#!/usr/bin/env python3
"""Remade PRX figure: End-to-end validation comparing baseline second-order NRPIC against the high-order solver."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
DO = np.load(PAPER_DIR / "data" / "compare_nrpic_orig_vs_best.npz")
DB = np.load(PAPER_DIR / "data" / "compare_orig_vs_best_backreaction.npz")
OUT = PAPER_DIR / "figures" / "fig_baseline_vs_highorder"
TLIM = 80.0


def fmt_gain(g: float) -> str:
    if g >= 1.0e4:
        exp = int(np.floor(np.log10(g)))
        mant = g / (10.0 ** exp)
        if exp >= 10:
            return rf"${mant:.0f}\!\times\!10^{{{exp}}}\times$"
        return rf"${mant:.1f}\!\times\!10^{{{exp}}}\times$"
    if g >= 100.0:
        return rf"${g:.0f}\times$"
    return rf"${g:.1f}\times$"


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.05))
    fig.subplots_adjust(left=0.095, right=0.92, bottom=0.095, top=0.955, wspace=0.52, hspace=0.35)

    # Top-Left: Spinning BH + massive particle ladder equatorial orbits
    ax = axes[0, 0]
    ax.fill(DB["bh_ah_hx"], DB["bh_ah_hy"], color="0.16", alpha=0.86, zorder=2)
    bh_qs = [
        ("q002", cz.PAL["green"]),
        ("q005", cz.PAL["orange"]),
        ("q010", cz.PAL["red"]),
    ]
    for qtag, col in bh_qs:
        for meth, ls, lw, zo in [("orig", "--", 1.45, 4), ("best", "-", 1.70, 5)]:
            px = DB[f"bh_{meth}_{qtag}_p_xy"]
            bx = DB[f"bh_{meth}_{qtag}_bh_xy"]
            ax.plot(px[:, 0], px[:, 1], color=col, ls=ls, lw=lw, zorder=zo)
            ax.plot(bx[:, 0], bx[:, 1], color=col, ls=ls, lw=1.1, alpha=0.84, zorder=zo)
    ax.plot([3.5], [0.0], "o", color="k", ms=4.5, zorder=7)
    ax.set_xlim(-3.3, 4.6)
    ax.set_ylim(-3.3, 4.6)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.04, 0.96, r"Spinning BH $+ \,m_p=q M_0$" "\n(inner: recoiling BH)",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.2, color="0.18")
    h_tl = [
        Line2D([], [], color=cz.PAL["green"], lw=1.6, label=r"$q=0.02$"),
        Line2D([], [], color=cz.PAL["orange"], lw=1.6, label=r"$q=0.05$"),
        Line2D([], [], color=cz.PAL["red"], lw=1.6, label=r"$q=0.10$"),
        Line2D([], [], color="0.15", lw=1.6, ls="-", label="High-order"),
        Line2D([], [], color="0.15", lw=1.45, ls="--", label="Baseline NRPIC"),
    ]
    ax.legend(handles=h_tl, loc="lower left", ncol=2, columnspacing=0.65, fontsize=6.4, frameon=False)

    # Top-Right: Proper-volume filter energy drift & M_AH(t) at q = 0.05
    ax = axes[0, 1]
    ax2 = ax.twinx()
    ax2.tick_params(which="both", direction="in")
    floor = 1.0e-16
    styles_tr = [
        ("orig", "Baseline NRPIC",                  cz.PAL["blue"],  "--", 1.55),
        ("best", r"High-order ($s_{\rm m}=1$)",     cz.PAL["red"],   "-",  1.65),
        ("fast", r"High-order ($s_{\rm m}=2$)",     cz.PAL["green"], "-.", 1.55),
    ]
    h_tr = []
    for tag, lbl, col, ls, lw in styles_tr:
        ft = DO[f"{tag}_filt_t"]
        fd = np.maximum(DO[f"{tag}_filt_drift"], floor)
        h_tr.append(ax.semilogy(ft, fd, color=col, ls=ls, lw=lw, label=lbl, zorder=4)[0])
        ax2.plot(DO[f"{tag}_ah_t"], DO[f"{tag}_ah_M"], color=col, ls=ls, lw=1.25, alpha=0.88, zorder=3)
    ax.axhline(floor, color="grey", lw=0.85, ls=":", alpha=0.6)
    ax.set_xlim(0.0, TLIM)
    ax.set_ylim(2.0e-17, 1.0e1)
    cz.no_minor_labels(ax, "y")
    ax2.set_ylim(0.930, 1.032)
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Filter drift $|I_E^{\rm filt}/I_E - 1|$", labelpad=2)
    ax2.set_ylabel(r"Horizon mass $M_{\rm AH}\,[M]$ (mid curves)", fontsize=8.5)
    ax.text(0.97, 0.24, r"Right axis: $M_{\rm AH}(t)$",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.0, color="0.25")
    ax.legend(handles=h_tr, loc="upper right", fontsize=6.6, frameon=False, labelspacing=0.20)

    # Bottom-Left: Cross-suite error & conservation comparison bars
    ax = axes[1, 0]
    cats = [
        ("Kerr\n" r"$\Delta\mathcal{E}_{\rm geo}$", float(DO["acc_kerr999_dE_orig"]),  float(DO["acc_kerr999_dE_best"])),
        ("Light\n" r"$\Delta N_{\rm t}$",          float(DO["acc_lr_dN_orig"]),      float(DO["acc_lr_dN_best"])),
        ("6-Lvl\n" r"$\Delta\mathcal{E}_{\rm med}$", float(DO["acc_m4_med_dE_orig"]), float(DO["acc_m4_med_dE_best"])),
        ("OS\n" r"$\Delta\alpha_c$",               float(DO["acc_os_alphac_orig"]),  float(DO["acc_os_alphac_best"])),
        ("ST\n" r"$|\mathbf{P}|$",                 float(DO["acc_st_mom_orig"]),     float(DO["acc_st_mom_best"])),
        ("BH\n" r"$\Delta I_E$",                   float(DO["orig_filt_max"]),       max(float(DO["best_filt_max"]), 1e-16)),
    ]
    x = np.arange(len(cats), dtype=np.float64)
    w = 0.34
    v_orig = np.array([c[1] for c in cats])
    v_best = np.array([c[2] for c in cats])
    ax.bar(x - 0.5 * w, v_orig, width=w, color=cz.PAL["blue"], edgecolor="k", lw=0.6,
           label="Baseline NRPIC", bottom=1e-17, log=True)
    ax.bar(x + 0.5 * w, v_best, width=w, color=cz.PAL["red"], edgecolor="k", lw=0.6,
           label="High-order solver", bottom=1e-17, log=True)
    y_mults = [3.0, 2.5, 3.0, 3.0, 2.8, 12.0]
    for xi, vo, vb, ym in zip(x, v_orig, v_best, y_mults):
        top = max(vo, vb)
        gain = vo / max(vb, 1e-30)
        ax.text(xi, top * ym, fmt_gain(gain), ha="center", va="bottom",
                fontsize=6.1, weight="bold", color=cz.PAL["red"])
    ax.set_xticks(x)
    ax.set_xticklabels([c[0] for c in cats], fontsize=6.4)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.55, 5.65)
    ax.set_ylim(1.0e-17, 1.5e4)
    cz.no_minor_labels(ax, "y")
    ax.set_ylabel("Relative error or drift")
    ax.legend(loc="upper center", ncol=2, columnspacing=0.8, fontsize=6.8, frameon=False)

    # Bottom-Right: Strictly dimensionless multi-suite speedup ratios
    ax = axes[1, 1]
    spds = [
        (r"BH $q{=}0.05$ ($s_{\rm m}{=}1$)", float(DO["orig_wall"]) / float(DO["best_wall"])),
        (r"BH $q{=}0.05$ ($s_{\rm m}{=}2$)", float(DO["orig_wall"]) / float(DO["fast_wall"])),
        (r"OS $10^4$ (7-Lvl)",               float(DO["spd_os10k_orig"]) / float(DO["spd_os10k_best"])),
        (r"OS $10^5$ (7-Lvl)",               float(DO["spd_os100k_orig"]) / float(DO["spd_os100k_best"])),
        (r"ST $10^4$ (9-Lvl)",               float(DO["spd_st10k_orig"]) / float(DO["spd_st10k_best"])),
        (r"6-Lvl Kerr SMR",                  float(DO["spd_m4_orig"]) / float(DO["spd_m4_best"])),
    ]
    y = np.arange(len(spds), dtype=np.float64)[::-1]
    ratios = [r for _, r in spds]
    cols_br = [cz.PAL["orange"], cz.PAL["green"], cz.PAL["blue"], "#008B8B", "#8E24AA", cz.PAL["red"]]
    ax.barh(y, ratios, height=0.56, color=cols_br, edgecolor="k", lw=0.65)
    ax.axvline(1.0, **cz.GUIDE)
    for yi, sp in zip(y, ratios):
        ax.text(sp + 0.08, yi, rf"${sp:.2f}\times$", va="center", ha="left", fontsize=7.2, weight="bold", color="0.15")
    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in spds], fontsize=7.0)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlim(0.0, 4.15)
    ax.set_ylim(-0.55, len(spds) + 0.05)
    ax.set_xlabel(r"Dimensionless speedup ratio ($T_{\rm base} / T$)", labelpad=1)
    ax.text(1.06, len(spds) - 0.25, r"Baseline $1\times$", fontsize=6.8, color="0.35", ha="left", va="center")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
