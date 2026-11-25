#!/usr/bin/env python3
"""Remade PRX figure: Binary black hole formation and inspiral inside a relativistic cluster."""
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
DL = np.load(PAPER_DIR / "data" / "physics_jeans_live.npz")
D3 = np.load(PAPER_DIR / "data" / "physics_jeans_3d.npz")
OUT = PAPER_DIR / "figures" / "fig_binary_cluster"


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 5.95))
    fig.subplots_adjust(left=0.095, right=0.905, bottom=0.085, top=0.955, wspace=0.45, hspace=0.31)

    t_l = float(D3["s11_t"])
    xyz = D3["s11_xyz"]
    sp = D3["s11_sp"]
    co_t = D3["co_t"]
    co0 = D3["co0_xyz"]
    co1 = D3["co1_xyz"]
    m_t = co_t <= t_l + 1e-6

    # Top-Left: Equatorial (x, y) spiral inspiral at t = 55 M
    ax = axes[0, 0]
    env, cA, cB = sp == 0, sp == 1, sp == 2
    ax.scatter(xyz[env, 0], xyz[env, 1], s=0.9, c="0.65", alpha=0.38, lw=0, rasterized=True, label="Envelope")
    ax.scatter(xyz[cA, 0], xyz[cA, 1], s=1.4, c=cz.PAL["blue"], alpha=0.58, lw=0, rasterized=True, label="Clump A")
    ax.scatter(xyz[cB, 0], xyz[cB, 1], s=1.4, c=cz.PAL["red"], alpha=0.58, lw=0, rasterized=True, label="Clump B")
    ax.plot(co0[m_t, 0], co0[m_t, 1], color=cz.PAL["blue"], lw=1.45, zorder=4)
    ax.plot(co1[m_t, 0], co1[m_t, 1], color=cz.PAL["red"], lw=1.45, zorder=4)
    ax.plot(D3["s11_hx0_xy"], D3["s11_hy0_xy"], color="k", lw=1.2, zorder=6)
    ax.plot(D3["s11_hx1_xy"], D3["s11_hy1_xy"], color="k", lw=1.2, zorder=6)
    ax.text(0.04, 0.95, rf"Equatorial $(x, y)$ at $t={t_l:.0f}\,M$" "\n" rf"($N_{{\rm live}}={len(xyz)}$)",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.3, color="0.18")
    ax.set_xlim(-11.5, 11.5)
    ax.set_ylim(-11.5, 11.5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.legend(loc="lower right", fontsize=6.6, markerscale=3.0, frameon=False)

    # Top-Right: Meridional (x, z) anatomy highlighting vertical BH drift vs QMC symmetry
    ax = axes[0, 1]
    ax.scatter(xyz[env, 0], xyz[env, 2], s=0.9, c="0.65", alpha=0.36, lw=0, rasterized=True)
    ax.scatter(xyz[cA, 0], xyz[cA, 2], s=1.4, c=cz.PAL["blue"], alpha=0.58, lw=0, rasterized=True)
    ax.scatter(xyz[cB, 0], xyz[cB, 2], s=1.4, c=cz.PAL["red"], alpha=0.58, lw=0, rasterized=True)
    ax.axhline(0.0, color="0.35", lw=0.85, ls="--", alpha=0.70, label="Midplane $z=0$")
    ax.plot(co0[m_t, 0], co0[m_t, 2], color=cz.PAL["blue"], lw=1.45, zorder=4, label="BH 0 (MC)")
    ax.plot(co1[m_t, 0], co1[m_t, 2], color=cz.PAL["red"], lw=1.45, zorder=4, label="BH 1 (MC)")
    ax.plot(D3["s11_hx0_xz"], D3["s11_hz0_xz"], color="k", lw=1.2, zorder=6)
    ax.plot(D3["s11_hx1_xz"], D3["s11_hz1_xz"], color="k", lw=1.2, zorder=6)
    zb0 = float(co0[np.argmin(np.abs(co_t - t_l)), 2])
    ax.text(0.04, 0.95, rf"Meridional $(x, z)$ at $t={t_l:.0f}\,M$" "\n" rf"MC kick $z_{{\rm BH,0}}={zb0:+.2f}\,M$",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.3, color="0.18")
    ax.set_xlim(-11.5, 11.5)
    ax.set_ylim(-7.0, 7.0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$z\,[M]$")
    ax.legend(loc="lower right", fontsize=6.6, frameon=False)

    # Bottom-Left: Binary separation d_AB(t) and vertical kick |z_BH|(t)
    ax = axes[1, 0]
    tc = DL["co_t"]
    sep = np.linalg.norm(DL["co0_xyz"] - DL["co1_xyz"], axis=1)
    h_sep = [ax.plot(tc, sep, color=cz.PAL["blue"], lw=1.55, label=r"MC+Mid $d_{AB}$")[0]]
    if "q_co_t" in DL and len(DL["q_co_t"]):
        qsep = np.linalg.norm(DL["q_co0_xyz"] - DL["q_co1_xyz"], axis=1)
        h_sep.append(ax.plot(DL["q_co_t"], qsep, color="0.12", lw=1.55, ls="--", zorder=5,
                             label=r"QMC+GL4 $d_{AB}$")[0])
    ax.set_xlim(0.0, max(36.0, float(tc[-1]) * 1.02))
    ax.set_ylim(0.0, 6.8)
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Binary separation $d_{AB}\,[M]$", color=cz.PAL["blue"])
    ax.tick_params(axis="y", labelcolor=cz.PAL["blue"])

    ax2 = ax.twinx()
    h_sep.append(ax2.plot(tc, np.abs(DL["co0_xyz"][:, 2]), color=cz.PAL["red"], lw=1.4, ls="-", label=r"MC kick $|z_0|$")[0])
    h_sep.append(ax2.plot(tc, np.abs(DL["co1_xyz"][:, 2]), color=cz.PAL["orange"], lw=1.4, ls="--", label=r"MC kick $|z_1|$")[0])
    if "q_co0_xyz" in DL and len(DL["q_co0_xyz"]):
        h_sep.append(ax2.plot(DL["q_co_t"], np.abs(DL["q_co0_xyz"][:, 2]), color=cz.PAL["green"], lw=1.6, ls="-",
                              label=r"QMC $|z_0|$")[0])
    ax2.set_ylim(-0.02, 0.85)
    ax2.set_ylabel(r"Vertical kick $|z_{\rm BH}|\,[M]$", color=cz.PAL["red"])
    ax2.tick_params(axis="y", labelcolor=cz.PAL["red"])
    ax2.tick_params(which="both", direction="in")
    ax.legend(handles=h_sep, loc="center left", bbox_to_anchor=(0.02, 0.56), fontsize=6.4, frameon=False)

    # Bottom-Right: Individual AH masses M_AH(t), excised fraction, and alpha_min
    ax = axes[1, 1]
    lines = []
    if len(DL["ah0_t"]):
        lines.append(ax.plot(DL["ah0_t"], DL["ah0_M"], color=cz.PAL["blue"], lw=1.55, label=r"MC $M_{\rm AH,0}$")[0])
    if len(DL["ah1_t"]):
        lines.append(ax.plot(DL["ah1_t"], DL["ah1_M"], color=cz.PAL["red"], lw=1.45, ls="--", label=r"MC $M_{\rm AH,1}$")[0])
    if "q_ah0_t" in DL and len(DL["q_ah0_t"]):
        lines.append(ax.plot(DL["q_ah0_t"], DL["q_ah0_M"], color=cz.PAL["orange"], lw=1.7, ls="-", zorder=6,
                             label=r"QMC $M_{\rm AH,0}$")[0])
    if "q_ah1_t" in DL and len(DL["q_ah1_t"]):
        lines.append(ax.plot(DL["q_ah1_t"], DL["q_ah1_M"], color="0.12", lw=1.5, ls=":", zorder=6,
                             label=r"QMC $M_{\rm AH,1}$")[0])
    ax.axhline(0.1321, color="grey", lw=0.9, ls=":", alpha=0.75)
    ax.text(float(tc[-1]) * 0.98, 0.1338, r"initial clump $m_A=0.132M$",
            ha="right", va="bottom", fontsize=6.5, color="0.32")
    ax.set_xlim(0.0, max(36.0, float(tc[-1]) * 1.02))
    ax.set_ylim(0.088, 0.212)
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Horizon mass $M_{\rm AH}\,[M]$")

    axr = ax.twinx()
    lines.append(axr.plot(DL["nh_t"], DL["nh_mexc"], color=cz.PAL["green"], lw=1.35, ls="-", label=r"$M_{\rm exc}/M_0$")[0])
    lines.append(axr.plot(DL["nh_t"], DL["nh_amin"], color="0.35", lw=1.25, ls=":", label=r"$\alpha_{\min}$")[0])
    axr.set_ylim(-0.04, 1.15)
    axr.set_ylabel(r"$M_{\rm exc}/M_0,\;\alpha_{\min}$", color="0.25")
    axr.tick_params(which="both", direction="in")
    ax.legend(handles=lines, loc="upper left", ncol=2, columnspacing=0.55, fontsize=6.0, frameon=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
