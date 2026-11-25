#!/usr/bin/env python3
"""Remade PRX figure: Massive-particle gravitational back-reaction on a spinning black hole."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
D = np.load(PAPER_DIR / "data" / "physics_bh_massive_backreaction.npz")
OUT = PAPER_DIR / "figures" / "fig_bh_backreaction"
TLIM = 80.0

CASES = [
    ("q000", r"$q = 0.00$", cz.PAL["blue"],   "--"),
    ("q002", r"$q = 0.02$", cz.PAL["green"],  "-"),
    ("q005", r"$q = 0.05$", cz.PAL["orange"], "-"),
    ("q010", r"$q = 0.10$", cz.PAL["red"],    "-"),
]


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.05))
    fig.subplots_adjust(left=0.09, right=0.895, bottom=0.085, top=0.955, wspace=0.42, hspace=0.30)

    # Top-Left: Smooth lapse slice (pale exterior, deep core) + plunge & BH recoil trajectories
    ax = axes[0, 0]
    edges = D["alpha_edges"]
    grid = D["alpha_grid"]
    cmap = cz.truncate_cmap("magma_r", 0.05, 0.94)
    im = ax.pcolormesh(edges, edges, grid, cmap=cmap, vmin=0.05, vmax=0.90,
                       shading="auto", rasterized=True)

    for case, lbl, col, ls in CASES:
        px = D[f"{case}_p_xyz"]
        bx = D[f"{case}_bh_xyz"]
        ax.plot(px[:, 0], px[:, 1], color=col, ls=ls, lw=1.65, label=lbl, zorder=4)
        ax.plot(bx[:, 0], bx[:, 1], color=col, ls="-", lw=1.25, alpha=0.92, zorder=5)

    t_sl = float(D["alpha_t"])
    px_sl, py_sl = D["alpha_p_xy"]
    bx_sl, by_sl = D["alpha_bh_xy"]
    ax.plot([px_sl], [py_sl], "o", color=cz.PAL["red"], mec="k", mew=0.9, ms=5.2, zorder=6)
    if len(D["alpha_hx"]):
        ax.plot(D["alpha_hx"], D["alpha_hy"], color="white", lw=1.3, zorder=6)
    ax.plot([bx_sl], [by_sl], "+", color="white", mew=1.2, ms=5.5, zorder=6)

    ax.text(0.04, 0.96, rf"$\alpha(x,y)$ at $t={t_sl:.1f}\,M$ ($q=0.10$)",
            transform=ax.transAxes, ha="left", va="top", color="white", fontsize=7.6)
    ax.set_xlim(-4.4, 4.4)
    ax.set_ylim(-4.4, 4.4)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.legend(loc="lower center", ncol=2, columnspacing=0.8, fontsize=7.2,
              frameon=False, labelcolor="white")
    cax = make_axes_locatable(ax).append_axes("right", size="4.5%", pad=0.04)
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label(r"Lapse $\alpha$", fontsize=8.4, labelpad=2)
    cbar.ax.tick_params(labelsize=7.6)

    # Top-Right: Relative orbital separation r_rel(t) and BH recoil |x_BH(t)|
    ax = axes[0, 1]
    ax2 = ax.twinx()
    ax2.tick_params(which="both", direction="in")
    handles = []
    max_r, max_rec = 3.8, 1e-4
    for case, lbl, col, ls in CASES:
        tp = D[f"{case}_p_t"]
        rr = D[f"{case}_r_rel"]
        tb = D[f"{case}_bh_t"]
        rbh = D[f"{case}_r_bh"]
        max_r = max(max_r, float(np.max(rr)))
        max_rec = max(max_rec, float(np.max(rbh)))
        h, = ax.plot(tp, rr, color=col, ls=ls if case == "q000" else "-", lw=1.55, label=lbl)
        handles.append(h)
        ax2.plot(tb, rbh, color=col, ls=":", lw=1.45)
    ax.set_xlim(0.0, TLIM)
    ax.set_ylim(0.0, max_r * 1.20)
    ax2.set_ylim(-0.02 * max_rec, max_rec * 1.25)
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Separation $r_{\rm rel}\,[M]$ (solid/dashed)")
    ax2.set_ylabel(r"BH recoil $|\mathbf{x}_{\rm BH}|\,[M]$ (dotted)", fontsize=8.8)
    ax.legend(handles=handles, loc="upper left", ncol=2, columnspacing=0.8, fontsize=7.2, frameon=False)

    # Bottom-Left: Quadrupolar waveform r Re Psi_4^{22} at R_ext = 14 M
    ax = axes[1, 0]
    t_cut = 25.0
    gw_pos, gw_neg = 1e-7, 1e-7
    for case, lbl, col, ls in CASES:
        gt = D[f"{case}_gw_t"]
        gre = D[f"{case}_gw_re"]
        msk = gt >= t_cut
        gw_pos = max(gw_pos, float(np.max(gre[msk])))
        gw_neg = max(gw_neg, float(-np.min(gre[msk])))
        ax.plot(gt[msk], gre[msk] * 1.0e4, color=col, ls=ls, lw=1.45, label=lbl)
    ax.axhline(0.0, color="0.65", lw=0.7, ls="-", zorder=1)
    ax.set_xlim(t_cut, TLIM)
    ax.set_ylim(-1.22 * gw_neg * 1.0e4, 1.32 * gw_pos * 1.0e4)
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^4\,r\,\mathrm{Re}\,\Psi_4^{22}\;[M^{-1}]$")
    ax.text(0.04, 0.94, r"$R_{\rm ext} = 14\,M$", transform=ax.transAxes, ha="left", va="top", fontsize=7.8)
    ax.legend(loc="upper right", ncol=2, columnspacing=0.8, fontsize=7.2, frameon=False)

    # Bottom-Right: Dynamical FastFlow horizon mass M_AH(t) & spin chi_AH(t)
    ax = axes[1, 1]
    axr = ax.twinx()
    axr.tick_params(which="both", direction="in")
    ah_M_all, ah_c_all, h_ah = [], [], []
    for case, lbl, col, ls in CASES:
        at = D[f"{case}_ah_t"]
        aM = D[f"{case}_ah_M"]
        ac = D[f"{case}_ah_chi"]
        ah_M_all.append(aM)
        ah_c_all.append(ac)
        h, = ax.plot(at, aM, color=col, ls=ls if case == "q000" else "-", lw=1.55, label=lbl)
        h_ah.append(h)
        axr.plot(at, ac, color=col, ls=":", lw=1.45)
    m_lo = min(float(np.min(a)) for a in ah_M_all)
    m_hi = max(float(np.max(a)) for a in ah_M_all)
    c_lo = min(float(np.min(a)) for a in ah_c_all)
    c_hi = max(float(np.max(a)) for a in ah_c_all)
    ax.set_xlim(0.0, TLIM)
    ax.set_ylim(m_lo - 0.12 * (m_hi - m_lo), m_hi + 0.45 * (m_hi - m_lo))
    axr.set_ylim(c_lo - 0.30 * (c_hi - c_lo), c_hi + 0.40 * (c_hi - c_lo))
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Horizon mass $M_{\rm AH}\,[M]$ (solid)")
    axr.set_ylabel(r"Dimensionless spin $\chi_{\rm AH}$ (dotted)", fontsize=8.8)
    ax.legend(handles=h_ah, loc="upper left", ncol=2, columnspacing=0.8, fontsize=7.2, frameon=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
