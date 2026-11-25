#!/usr/bin/env python3
"""Remade PRX figure: Near-extremal Kerr (a = 0.999 M) ergospheric zoom-whirl and pusher accuracy."""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

HERE = Path(__file__).resolve().parent
PAPER_DIR = HERE.parent
D999 = np.load(PAPER_DIR / "data" / "physics_kerr_a0999_e0999.npz")
DZW = np.load(PAPER_DIR / "data" / "compare_orig_vs_best_orbits.npz")
OUT = PAPER_DIR / "figures" / "fig_kerr_strong_orbits"


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
    a999 = float(D999["a999"])
    rp = 1.0 + np.sqrt(1.0 - a999 * a999)
    r_hor_eq = np.sqrt(rp * rp + a999 * a999)
    r_erg_eq = np.sqrt(4.0 + a999 * a999)
    ph = np.linspace(0.0, 2.0 * np.pi, 240)

    fig = plt.figure(figsize=(8.0, 6.0))
    gs = fig.add_gridspec(2, 2, left=0.085, right=0.925, bottom=0.085, top=0.955,
                          wspace=0.38, hspace=0.29)

    # Top-Left (3D): Inclined ergosphere-diving bound zoom-whirl rosette (t = 450 M)
    ax3 = fig.add_subplot(gs[0, 0], projection="3d")
    Xh, Yh, Zh = cks_surface(lambda th: np.full_like(th, rp), a999)
    Xe, Ye, Ze = cks_surface(lambda th: 1.0 + np.sqrt(np.maximum(1.0 - (a999 * np.cos(th))**2, 0.0)), a999)
    ax3.plot_surface(Xh, Yh, Zh, color="0.12", alpha=0.96, shade=True, linewidth=0)
    ax3.plot_surface(Xe, Ye, Ze, color=cz.PAL["orange"], alpha=0.16, linewidth=0.15)

    xzw, tzw = D999["x_zw"], D999["t_zw"]
    pts3d = xzw.reshape(-1, 1, 3)
    segs3d = np.concatenate([pts3d[:-1], pts3d[1:]], axis=1)
    lc3d = Line3DCollection(segs3d, cmap="viridis", norm=plt.Normalize(0.0, float(tzw[-1])),
                            linewidth=1.1, alpha=0.92)
    lc3d.set_array(tzw[:-1])
    ax3.add_collection3d(lc3d)
    ax3.scatter([xzw[0, 0]], [xzw[0, 1]], [xzw[0, 2]], color=cz.PAL["green"], s=18, edgecolor="k", lw=0.5, zorder=10)
    ax3.scatter([xzw[-1, 0]], [xzw[-1, 1]], [xzw[-1, 2]], color=cz.PAL["red"], s=20, marker="s", edgecolor="k", lw=0.5, zorder=10)
    ax3.set_xlim(-9.6, 9.6)
    ax3.set_ylim(-9.6, 9.6)
    ax3.set_zlim(-6.8, 6.8)
    ax3.set_xticks([-8, -4, 0, 4, 8])
    ax3.set_yticks([-8, -4, 0, 4, 8])
    ax3.set_zticks([-6, -3, 0, 3, 6])
    ax3.set_box_aspect((1.0, 1.0, 0.72))
    ax3.view_init(elev=22, azim=38)
    ax3.set_xlabel(r"$x\,[M]$", labelpad=1, fontsize=8.2)
    ax3.set_ylabel(r"$y\,[M]$", labelpad=1, fontsize=8.2)
    ax3.set_zlabel(r"$z\,[M]$", labelpad=0, fontsize=8.2)
    ax3.tick_params(labelsize=7.0, pad=0)
    ax3.text2D(0.02, 0.99,
               r"Ergosphere rosette ($a=0.999M$, GL4, $t=450M$)" "\n"
               rf"$\mathcal{{E}}_{{\rm geo}}={float(D999['E0_3d']):.4f},\;L_z={float(D999['L0_3d']):.2f},\;Q={float(D999['Q0_3d']):.2f}$",
               transform=ax3.transAxes, ha="left", va="top", fontsize=6.5)

    # Top-Right (2D): Coarse-step zoom-whirl pusher comparison (dt = 0.10 M vs 0.02 M ref)
    ax = fig.add_subplot(gs[0, 1])
    ax.fill(r_hor_eq * np.cos(ph), r_hor_eq * np.sin(ph), color="0.12", zorder=2, label=r"Horizon $r_+$")
    ax.plot(r_erg_eq * np.cos(ph), r_erg_eq * np.sin(ph), color=cz.PAL["orange"], ls=":", lw=1.05, zorder=2,
            label="Ergosphere")
    zr, zg, zm, zb = DZW["zw_ref_xyz"], DZW["zw_gl4_xyz"], DZW["zw_mid_xyz"], DZW["zw_bor_xyz"]
    gl4_dx = float(DZW["zw_gl4_dx"])
    gl4_exp = int(np.floor(np.log10(gl4_dx)))
    gl4_mant = gl4_dx / (10.0 ** gl4_exp)
    ax.plot(zr[:, 0], zr[:, 1], color="0.25", lw=2.0, zorder=3, label=r"Ref. ($\Delta t=0.02M$)")
    ax.plot(zg[:, 0], zg[:, 1], color=cz.PAL["red"], lw=1.35, ls="-", zorder=6,
            label=rf"GL4 (${gl4_mant:.1f}\times 10^{{{gl4_exp}}}M$)")
    ax.plot(zm[:, 0], zm[:, 1], color=cz.PAL["blue"], lw=1.35, ls="--", zorder=5,
            label=rf"Midpoint (${float(DZW['zw_mid_dx']):.2f}M$)")
    ax.plot(zb[:, 0], zb[:, 1], color=cz.PAL["green"], lw=1.35, ls="-.", zorder=4,
            label=rf"Boris (${float(DZW['zw_bor_dx']):.2f}M$)")
    ax.plot([zr[-1, 0]], [zr[-1, 1]], "o", color="0.15", ms=4.2, zorder=8)
    ax.plot([zm[-1, 0]], [zm[-1, 1]], "s", color=cz.PAL["blue"], mec="k", mew=0.4, ms=4.2, zorder=8)
    ax.plot([zb[-1, 0]], [zb[-1, 1]], "^", color=cz.PAL["green"], mec="k", mew=0.4, ms=4.6, zorder=8)
    ax.set_xlim(-14.0, 14.0)
    ax.set_ylim(-17.5, 13.5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.97, 0.96, "Bound zoom-whirl\n" r"($a=0.999M$, $t=450M$)",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.0, color="0.18")
    ax.legend(loc="lower center", ncol=2, fontsize=5.1, frameon=False,
              labelspacing=0.16, columnspacing=0.45, handlelength=1.15, handletextpad=0.35)

    # Bottom-Left: Position error |x - x_exact|(t) & radius r(t) on e=0.999 four-whirl passage
    ax = fig.add_subplot(gs[1, 0])
    h_bl = []
    h_bl.append(ax.semilogy(D999["t_mid"], np.maximum(D999["mid_dx"], 1.0e-12), color=cz.PAL["blue"],
                            lw=1.35, ls="--", label=r"Midpoint $|\Delta\mathbf{x}|$")[0])
    h_bl.append(ax.semilogy(D999["t_bor"], np.maximum(D999["bor_dx"], 1.0e-12), color=cz.PAL["green"],
                            lw=1.35, ls="-.", label=r"Spacetime Boris $|\Delta\mathbf{x}|$")[0])
    h_bl.append(ax.semilogy(D999["t_gl4"], np.maximum(D999["gl4_dx"], 1.0e-12), color=cz.PAL["red"],
                            lw=1.55, ls="-", label=r"GL4 $|\Delta\mathbf{x}|$")[0])
    ax.set_xlim(0.0, 220.0)
    ax.set_ylim(2.0e-11, 5.0e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Position error $|\mathbf{x}-\mathbf{x}_{\rm ref}|\,[M]$")

    ax2 = ax.twinx()
    h_bl.append(ax2.plot(D999["t_dop"], D999["r_dop"], color="0.45", lw=1.15, ls=":",
                         label=r"$r(t)$ (right axis)")[0])
    ax2.axhline(r_erg_eq, color=cz.PAL["orange"], lw=0.9, ls=":", alpha=0.85)
    ax2.text(216.0, r_erg_eq + 0.55, r"$r_{\rm ergo}=2M$", ha="right", va="bottom",
             fontsize=6.6, color=cz.PAL["orange"])
    ax2.set_ylim(0.0, 31.0)
    ax2.set_ylabel(r"Kerr--Schild radius $r\,[M]$", color="0.35")
    ax2.tick_params(which="both", direction="in")
    ax.legend(handles=h_bl, loc="lower right", bbox_to_anchor=(0.98, 0.16), fontsize=6.4, frameon=False)

    # Bottom-Right: Energy & Carter drifts on the e = 0.999 four-whirl encounter (dt = 0.02 M)
    ax = fig.add_subplot(gs[1, 1])
    ax.semilogy(D999["t_mid"], np.maximum(D999["mid_dE"], 1.0e-16), color=cz.PAL["blue"], ls="--", lw=1.4,
                label=r"Midpoint $|\Delta\mathcal{E}_{\rm geo}/\mathcal{E}_0|$")
    ax.semilogy(D999["t_mid"], np.maximum(D999["mid_dQ"], 1.0e-16), color=cz.PAL["blue"], ls=":", lw=1.25,
                label=r"Midpoint $|\Delta Q/Q_0|$")
    ax.semilogy(D999["t_bor"], np.maximum(D999["bor_dE"], 1.0e-16), color=cz.PAL["green"], ls="-.", lw=1.35,
                label=r"Boris $|\Delta\mathcal{E}_{\rm geo}/\mathcal{E}_0|$")
    ax.semilogy(D999["t_gl4"], np.maximum(D999["gl4_dE"], 1.0e-16), color=cz.PAL["red"], ls="-", lw=1.6,
                label=r"GL4 $|\Delta\mathcal{E}_{\rm geo}/\mathcal{E}_0|$")
    ax.semilogy(D999["t_gl4"], np.maximum(D999["gl4_dQ"], 1.0e-16), color=cz.PAL["orange"], ls="--", lw=1.4,
                label=r"GL4 $|\Delta Q/Q_0|$")
    ax.axvline(92.0, color="0.55", lw=0.8, ls=":")
    ax.text(84.0, 1.0e-4, "Pericenter\n" r"($r_p=1.35M$, $4.05$ turns)", ha="right", va="bottom",
            fontsize=5.9, color="0.30")
    ax.set_xlim(0.0, 220.0)
    ax.set_ylim(5.0e-17, 6.0e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$", labelpad=-1)
    ax.set_ylabel("Relative invariant drift")
    ax.legend(loc="upper right", ncol=2, fontsize=5.5, frameon=False,
              labelspacing=0.18, columnspacing=0.65)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
