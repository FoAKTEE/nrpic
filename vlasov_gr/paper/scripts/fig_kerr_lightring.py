#!/usr/bin/env python3
"""Remade PRX figure: Kerr a=0.90M null geodesics, photon-shell stability, and light-ring separatrix."""
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
D = np.load(PAPER_DIR / "data" / "physics_kerr_a090_lightring.npz")
DC = np.load(PAPER_DIR / "data" / "compare_orig_vs_best_orbits.npz")
OUT = PAPER_DIR / "figures" / "fig_kerr_lightring"


def cks_surface(r_func, a, nth=28, nph=40):
    th = np.linspace(0.0, np.pi, nth)
    ph = np.linspace(0.0, 2.0 * np.pi, nph)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    rr = r_func(TH)
    X = np.sqrt(rr**2 + a**2) * np.sin(TH) * np.cos(PH)
    Y = np.sqrt(rr**2 + a**2) * np.sin(TH) * np.sin(PH)
    Z = rr * np.cos(TH)
    return X, Y, Z


def main():
    cz.use_style()
    a = float(D["a_spin"])
    rp = float(D["rp_bh"])
    r_php = float(D["r_ph_pro"])
    r_phr = float(D["r_ph_ret"])
    om_ph = 1.0 / (r_php**1.5 + a)
    ph = np.linspace(0.0, 2.0 * np.pi, 240)

    r_hor_eq = np.sqrt(rp**2 + a**2)
    r_php_c = np.sqrt(r_php**2 + a**2)
    r_phr_c = np.sqrt(r_phr**2 + a**2)
    r_erg_eq = np.sqrt(4.0 + a**2)

    fig = plt.figure(figsize=(8.0, 6.0))
    gs = fig.add_gridspec(2, 2, left=0.085, right=0.970, bottom=0.085, top=0.945,
                          wspace=0.28, hspace=0.33)

    # Top-Left (3D): Inclined spherical photon shell (r_sph=2.20M): GL4 vs Midpoint plunge
    ax3 = fig.add_subplot(gs[0, 0], projection="3d")
    Xh, Yh, Zh = cks_surface(lambda th: np.full_like(th, rp), a)
    ax3.plot_surface(Xh, Yh, Zh, color="0.16", alpha=0.65, shade=True, linewidth=0)
    ax3.plot(r_php_c * np.cos(ph), r_php_c * np.sin(ph), np.zeros_like(ph), color=cz.PAL["orange"], lw=1.0, zorder=8)
    g33, m33 = DC["lr33_gl4_xyz"], DC["lr33_mid_xyz"]
    ax3.plot(g33[:, 0], g33[:, 1], g33[:, 2], color=cz.PAL["red"], lw=1.15, alpha=0.92,
             label=rf"GL4 shell ($t={float(DC['lr33_gl4_tend']):.1f}M$)")
    ax3.plot(m33[:, 0], m33[:, 1], m33[:, 2], color=cz.PAL["blue"], lw=1.3, ls="--",
             label=rf"Midpoint plunge ($t={float(DC['lr33_mid_tend']):.1f}M$)")
    ax3.scatter([m33[-1, 0]], [m33[-1, 1]], [m33[-1, 2]], marker="X", c=cz.PAL["blue"],
                edgecolors="k", linewidths=0.5, s=36, zorder=10)
    ax3.set_xlim(-2.35, 2.35)
    ax3.set_ylim(-2.35, 2.35)
    ax3.set_zlim(-2.35, 2.35)
    ax3.set_box_aspect((1.0, 1.0, 0.90))
    ax3.set_xticks([-2, 0, 2])
    ax3.set_yticks([-2, 0, 2])
    ax3.set_zticks([-2, 0, 2])
    ax3.tick_params(labelsize=7.0, pad=1)
    ax3.set_xlabel(r"$x\,[M]$", fontsize=8.2, labelpad=1)
    ax3.set_ylabel(r"$y\,[M]$", fontsize=8.2, labelpad=1)
    ax3.set_zlabel(r"$z\,[M]$", fontsize=8.2, labelpad=0)
    ax3.view_init(elev=22, azim=-50)
    ax3.text2D(0.02, 0.99, r"3D photon shell ($a=0.9M$, $r_{\rm sph}=2.20M$)",
               transform=ax3.transAxes, ha="left", va="top", fontsize=7.0)
    ax3.legend(loc="upper right", bbox_to_anchor=(1.04, 0.92), fontsize=6.4, frameon=False)

    # Top-Right (2D): Equatorial prograde light-ring separatrix + (dxi/xi_c+ = +1e-6) divergence
    ax = fig.add_subplot(gs[0, 1])
    ax.fill(r_hor_eq * np.cos(ph), r_hor_eq * np.sin(ph), color="0.12", zorder=5, label=r"Horizon $r_+$")
    ax.plot(r_php_c * np.cos(ph), r_php_c * np.sin(ph), color=cz.PAL["orange"], ls="--", lw=1.2, zorder=4,
            label=rf"Prograde $r_{{\rm ph}}^+={r_php:.2f}M$")
    ax.plot(r_erg_eq * np.cos(ph), r_erg_eq * np.sin(ph), color="0.50", ls=":", lw=0.95, zorder=3,
            label=r"Ergosphere ($2M$)")
    ax.plot(r_phr_c * np.cos(ph), r_phr_c * np.sin(ph), color="0.45", ls="-.", lw=0.9, zorder=3,
            label=rf"Retrograde $r_{{\rm ph}}^-={r_phr:.2f}M$")

    # Critical escape/fall-in rays + solver comparison at delta xi / xi_c+ = +1e-6
    dop21, gl21, mid21 = DC["lr21_dop_xyz"], DC["lr21_gl4_xyz"], DC["lr21_mid_xyz"]
    ax.plot(dop21[:, 0], dop21[:, 1], color="0.20", lw=2.0, zorder=3, label="8th-order ref. (escape)")
    ax.plot(gl21[:, 0], gl21[:, 1], color=cz.PAL["red"], lw=1.35, ls="-", zorder=6, label=r"GL4 ($\Delta t=0.05M$, escape)")
    ax.plot(mid21[:, 0], mid21[:, 1], color=cz.PAL["blue"], lw=1.35, ls="--", zorder=5, label=r"Midpoint (false plunge)")
    ax.plot([mid21[-1, 0]], [mid21[-1, 1]], "X", color=cz.PAL["blue"], mec="k", mew=0.45, ms=5.5, zorder=7)
    ax.plot(D["ray_37_x"][:, 0], D["ray_37_x"][:, 1], color=cz.PAL["green"], lw=1.0, ls=":", zorder=2,
            label="Retro. critical ray")
    ax.set_xlim(-9.8, 8.8)
    ax.set_ylim(-6.8, 11.8)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.04, 0.04, "Separatrix\n" r"($\delta\xi/\xi_c^+ = +10^{-6}$)",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=6.6, color="0.18")
    ax.legend(loc="upper right", fontsize=5.8, frameon=False, labelspacing=0.17)

    # Bottom-Left: Orbit winding number N_turns vs |dxi / xi_c+| across 8 decades
    ax = fig.add_subplot(gs[1, 0])
    deltas = D["deltas"]
    neg = deltas < 0.0
    pos = deltas > 0.0
    ax.semilogx(np.abs(deltas[neg]), D["dop_turns"][neg], color=cz.PAL["blue"], lw=1.6, ls="-",
                label="8th-order ref. (fall-in)")
    ax.semilogx(np.abs(deltas[pos]), D["dop_turns"][pos], color=cz.PAL["red"], lw=1.6, ls="-",
                label="8th-order ref. (escape)")

    for mask, dfate, col_m, tag_l in [(neg, 1, cz.PAL["blue"], "fall-in"), (pos, 0, cz.PAL["red"], "escape")]:
        ok_g = D["gl4_dt05_fates"][mask] == dfate
        d_sub = np.abs(deltas[mask])
        t_g = D["gl4_dt05_turns"][mask]
        if np.any(ok_g):
            ax.semilogx(d_sub[ok_g], t_g[ok_g], "o", color=col_m, mfc="none", ms=5.0, mew=1.0, zorder=5,
                        label=r"GL4 ($\Delta t=0.05M$)" if tag_l == "fall-in" else None)
        ok_m = D["mid_dt05_fates"][mask] == dfate
        bad_m = ~ok_m
        t_m = D["mid_dt05_turns"][mask]
        if np.any(ok_m):
            ax.semilogx(d_sub[ok_m], t_m[ok_m], "s", color=cz.PAL["orange"] if tag_l == "fall-in" else cz.PAL["green"],
                        ms=3.6, zorder=4, label=r"Midpoint ($\Delta t=0.05M$)" if tag_l == "fall-in" else None)
        if np.any(bad_m):
            ax.semilogx(d_sub[bad_m], t_m[bad_m], "x", color="k", ms=6.2, mew=1.5, zorder=8,
                        label="Midpoint false capture" if tag_l == "escape" else None)

    ax.invert_xaxis()
    ax.set_xlim(2.0e-1, 1.5e-9)
    ax.set_ylim(0.2, 8.6)
    ax.set_xlabel(r"Impact-parameter offset $|\delta\xi/\xi_c^+|$", labelpad=-1)
    ax.set_ylabel(r"Orbit number $N_{\rm turns} = |\Delta\phi|/(2\pi)$")
    ax.text(0.04, 0.95, rf"Slope $\approx {float(D['turns_per_dec']):.3f}$ turns/dec",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.0, color="0.20")
    ax.legend(loc="lower right", fontsize=5.8, frameon=False)

    # Bottom-Right: Perched light-ring Lyapunov divergence & hold turns
    ax = fig.add_subplot(gs[1, 1])
    curves = [
        ("mid_dt10", cz.PAL["orange"], ":",  1.35, r"Midpoint $\Delta t=0.10M$"),
        ("mid_dt05", cz.PAL["green"],  "-.", 1.25, r"Midpoint $\Delta t=0.05M$"),
        ("mid_dt02", cz.PAL["blue"],   "--", 1.25, r"Midpoint $\Delta t=0.02M$"),
        ("gl4_dt10", cz.PAL["red"],    ":",  1.35, r"GL4 $\Delta t=0.10M$"),
        ("gl4_dt05", cz.PAL["red"],    "--", 1.35, r"GL4 $\Delta t=0.05M$"),
        ("gl4_dt02", cz.PAL["red"],    "-",  1.65, r"GL4 $\Delta t=0.02M$"),
    ]
    for lbl, col, ls, lw, desc in curves:
        nh = float(D[f"{lbl}_nh"])
        ax.semilogy(D[f"{lbl}_p32_t"], np.maximum(D[f"{lbl}_p32_dev"], 1.0e-15),
                    color=col, ls=ls, lw=lw, label=rf"{desc} ($N_{{\rm hold}}={nh:.2f}$)")

    tg = np.linspace(35.0, 155.0, 100)
    lam = float(D["lam_ph_pro"])
    ax.semilogy(tg, 1.0e-12 * np.exp(lam * (tg - 35.0)), color="0.30", ls="-", lw=1.0, alpha=0.65,
                label=rf"Exact $\propto e^{{\lambda t}}$ ($\lambda={lam:.4f}\,M^{{-1}}$)")

    ax.set_xlim(0.0, 200.0)
    ax.set_ylim(1.0e-15, 3.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Light-ring offset $|r(t) - r_{\rm ph}^+|\,[M]$")
    ax.legend(loc="lower right", fontsize=5.6, frameon=False)

    ax_top = ax.twiny()
    ax_top.set_xlim(0.0, 200.0 * om_ph / (2.0 * np.pi))
    ax_top.set_xlabel(r"Light-ring orbits $\Omega_{\rm ph}^+ t/(2\pi)$", fontsize=8.0, labelpad=3)
    ax_top.tick_params(labelsize=7.2, direction="in")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
