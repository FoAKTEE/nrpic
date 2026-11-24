#!/usr/bin/env python3
"""Publication figure: Prolate e=0.9 spindle collapse (10^5 QMC+GL4 vs MC+Midpoint)."""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LogNorm

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
D = np.load(os.path.join(PAPER_DIR, "data/physics_prolate.npz"))
OUT = os.path.join(PAPER_DIR, "figures/fig_physics_prolate_spindle")

HALF = D["half"]
BAR = (5.0, 5.0, 2.0, 1.0)
ON_AXIS = 0.25
DASH = (0, (4.0, 1.8))


def draw_scale_bar(ax, half, length):
    x1 = 0.90 * half
    y = -0.87 * half
    ax.plot([x1 - length, x1], [y, y], color="white", lw=1.6, solid_capstyle="butt", zorder=6)
    ax.text(
        x1 - 0.5 * length,
        y + 0.045 * half,
        f"{length:g} M",
        color="white",
        ha="center",
        va="bottom",
        fontsize=7.2,
        zorder=6,
    )


def main():
    cz.use_style()
    W = 7.2
    fig = plt.figure(figsize=(W, 4.65))

    # Top row: 4 meridional curvature + matter-density contour slices + shared right colorbar
    left_t, gap_t, cb_w, cb_pad, right_t = 0.42, 0.08, 0.12, 0.06, 0.44
    P = (W - left_t - right_t - 3 * gap_t - cb_w - cb_pad) / 4.0
    bot, hb, gap_rows = 0.44, 1.82, 0.52
    y_top = bot + hb + gap_rows

    im_ref = None
    norm = LogNorm(vmin=1e-4, vmax=2e2)
    cmap = cz.CMAP["dens"]

    for j in range(4):
        L = float(HALF[j])
        ax = cz.inch_axes(fig, left_t + j * (P + gap_t), y_top, P, P)
        I_abs = np.clip(np.abs(D[f"s{j}_I"]), 1e-4, 2e2)
        E_img = D[f"s{j}_E"]
        t = float(D[f"s{j}_t"])

        im_ref = ax.imshow(
            I_abs,
            origin="lower",
            extent=(-L, L, -L, L),
            cmap=cmap,
            norm=norm,
            interpolation="nearest",
            rasterized=True,
        )
        lvls = [4e-4] if j == 0 else [3e-3, 3e-2]
        xs = np.linspace(-L, L, E_img.shape[1])
        zs = np.linspace(-L, L, E_img.shape[0])
        ax.contour(xs, zs, E_img, levels=lvls, colors=["#7CE8FF"], linewidths=0.8, alpha=0.9)

        if j in (1, 2):
            k = int(np.argmin(np.abs(D["hyb_c_t"] - t)))
            xz_peak = float(D["hyb_c_Ix"][k])
            zz_peak = abs(float(D["hyb_c_Iz"][k]))
            ax.plot([xz_peak, xz_peak], [zz_peak, -zz_peak], ls="none", marker="o",
                    ms=5.8, mfc="none", mec="white", mew=1.0, zorder=5)
            if j == 1:
                ax.annotate(
                    r"max $|I|$",
                    xy=(xz_peak + 0.3, zz_peak),
                    xytext=(2.1, zz_peak + 0.8),
                    color="white",
                    fontsize=7.0,
                    ha="left",
                    va="center",
                    arrowprops=dict(arrowstyle="-", color="white", lw=0.7, shrinkA=0, shrinkB=0),
                )

        if j == 3:
            ax.plot(D["ah_sec_x"], D["ah_sec_z"], color="white", lw=1.15, zorder=5)
            ax.text(0.95, 0.94, "apparent\nhorizon", transform=ax.transAxes,
                    ha="right", va="top", color="white", fontsize=6.8, linespacing=1.0)

        ax.text(0.05, 0.94, rf"$t={t:g}\,M$", transform=ax.transAxes,
                ha="left", va="top", color="white", fontsize=7.6)
        draw_scale_bar(ax, L, BAR[j])
        ax.set_xlim(-L, L)
        ax.set_ylim(-L, L)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.minorticks_off()
        ax.set_xlabel(r"$x$", labelpad=2)
        if j == 0:
            ax.set_ylabel(r"$z$", labelpad=4)

    cax = cz.inch_axes(fig, left_t + 4 * P + 3 * gap_t + cb_pad, y_top, cb_w, P)
    cb = fig.colorbar(im_ref, cax=cax)
    cb.set_label(r"$M^4 |I|$", labelpad=3, fontsize=8.0)
    cb.set_ticks([1e-4, 1e-2, 1.0, 1e2])
    cb.ax.minorticks_off()
    cb.ax.tick_params(labelsize=7.0)

    # Bottom row: 3 physics time-series columns with generous inter-panel spacing
    left_b, gap_b, right_b = 0.62, 0.66, 0.10
    w = (W - left_b - right_b - 2 * gap_b) / 3.0
    hs = (hb - 0.08) / 2.0

    a_I = cz.inch_axes(fig, left_b, bot + hs + 0.08, w, hs)
    a_z = cz.inch_axes(fig, left_b, bot, w, hs)
    a_l = cz.inch_axes(fig, left_b + w + gap_b, bot, w, hb)
    a_h = cz.inch_axes(fig, left_b + 2 * (w + gap_b), bot, w, hb)

    t_ah = float(D["ah_first_t"])

    # Bottom-left top: peak Kretschmann scalar M^4 I_max
    a_I.plot(D["mid_c_t"], D["mid_c_I"], color="0.52", lw=1.0, ls="--", label="MC+Mid")
    a_I.plot(D["hyb_c_t"], D["hyb_c_I"], color=cz.PAL["red"], lw=1.35, label="QMC+GL4")
    a_I.set_yscale("log")
    a_I.set_ylim(1e-3, 3e3)
    a_I.set_yticks([1e-2, 1.0, 1e2])
    a_I.yaxis.set_minor_locator(mticker.LogLocator(numticks=20))
    cz.no_minor_labels(a_I, "y")
    a_I.set_ylabel(r"$M^4 I_{\max}$")
    a_I.legend(loc="lower right", fontsize=6.4, frameon=False, handlelength=1.4)

    # Bottom-left bottom: axial curvature max |z|, matter edge, AH polar radius
    on = (np.hypot(D["hyb_c_Ix"], D["hyb_c_Iy"]) < ON_AXIS) & (D["hyb_c_t"] <= 35.0)
    a_z.plot(D["hyb_c_t"][on], np.abs(D["hyb_c_Iz"][on]), ls="none", marker="o",
             ms=1.8, mew=0, color=cz.PAL["red"], label="curv peak")
    ok_z = np.isfinite(D["zenv_z"]) & (D["zenv_t"] <= 34.0)
    a_z.plot(D["zenv_t"][ok_z], D["zenv_z"][ok_z], color=cz.PAL["blue"], lw=1.1, ls="--", label="core edge")
    a_z.plot(D["hyb_ah_tf"], D["hyb_ah_rp"], color="k", lw=1.15, label="AH pole")
    a_z.set_ylim(0, 11.2)
    a_z.set_yticks([0, 5, 10])
    a_z.set_ylabel(r"$|z|/M$")
    a_z.legend(loc="upper right", fontsize=6.1, frameon=False, handlelength=1.3, labelspacing=0.2)

    # Bottom-middle: minimum lapse & live mass fraction
    a_l.axhline(0.05, ls=":", color="k", lw=0.9)
    a_l.plot(D["mid_h_t"], D["mid_h_amin"], color="0.52", lw=1.0, ls="--", label=r"$\alpha_{\min}$ MC+Mid")
    a_l.plot(D["hyb_h_t"], D["hyb_h_amin"], color=cz.PAL["blue"], lw=1.35, label=r"$\alpha_{\min}$ QMC+GL4")
    a_l.plot(D["hyb_h_t"], D["hyb_h_mfrac"], color=cz.PAL["red"], lw=1.35, ls="-.", label=r"$M_{\rm live}/M_0$")
    a_l.set_ylim(0, 1.15)
    a_l.set_yticks([0.0, 0.5, 1.0])
    a_l.set_ylabel(r"$\alpha_{\min},\; M_{\rm live}/M_0$", labelpad=4)
    a_l.legend(loc="lower left", bbox_to_anchor=(0.02, 0.08), fontsize=6.0, frameon=False, handlelength=1.3, labelspacing=0.22)

    # Bottom-right: apparent horizon irreducible mass
    a_h.axhline(1.0, color="0.4", lw=0.9, ls=":")
    ok_h = np.isfinite(D["hyb_ah_M"])
    ok_m = np.isfinite(D["mid_ah_M"])
    a_h.plot(D["mid_ah_t"][ok_m], D["mid_ah_M"][ok_m], color="0.52", lw=1.05, ls="--", label="MC+Mid")
    a_h.plot(D["hyb_ah_t"][ok_h], D["hyb_ah_M"][ok_h], color=cz.PAL["red"], lw=1.4, label="QMC+GL4")
    a_h.set_xlim(30.0, 45.0)
    a_h.set_xticks([30, 35, 40, 45])
    a_h.set_ylim(0.93, 1.045)
    a_h.set_yticks([0.94, 0.98, 1.02])
    a_h.set_ylabel(r"$M_{\rm AH}/M$", labelpad=4)
    a_h.legend(loc="lower right", fontsize=6.4, frameon=False, handlelength=1.4)

    for ax in (a_I, a_z, a_l):
        ax.set_xlim(0, 45)
        ax.set_xticks([0, 10, 20, 30, 40])
    for ax in (a_I, a_z, a_l, a_h):
        ax.axvline(t_ah, ls=DASH, zorder=1, color="k", lw=0.9)
    a_I.xaxis.set_major_formatter(mticker.NullFormatter())
    for ax in (a_z, a_l, a_h):
        ax.set_xlabel(r"$t/M$", labelpad=2)
    for ax in (a_I, a_z):
        ax.yaxis.set_label_coords(-0.46 / w, 0.5)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {OUT}.{{pdf,png}}")


if __name__ == "__main__":
    main()
