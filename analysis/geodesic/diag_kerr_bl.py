#!/usr/bin/env python3
"""Diagnostic figure for part B: the Boyer-Lindquist orbits (a = 0.9 M), equatorial eccentric
(top row, t_end = 4550 M) and inclined (bottom row, t_end = 3850 M).

Columns: (1) trajectory of the Boris (symmetric triad, dt = 0.01 M) run in the x-y plane
(eccentric) or x-z plane (inclined) of BL pseudo-Cartesian coordinates (yellow), with the exact
solution sampled every 10 M (blue dots), the event horizon (black) and the equatorial ergosphere
(grey); (2) position error max(|dr|/M, |dtheta|, |dphi|) against the reference trajectory every
10 M; (3) |Delta E/E_0|; (4) |Delta L_z/L_z0| (eccentric) or |Delta Q/Q_0| (inclined), max over
10 M bins.  Colour = pusher (red midpoint, yellow Boris symmetric, green Boris Cholesky); light
shade dt = 0.02 M, dark shade dt = 0.01 M; all solid (analytic BL metric).  Blue circle: start,
blue square: exact final position.

Data: problems/kerr/results/{kerr_histories.npz, bl_trajectories.npz}.
Output: analysis/geodesic/figs/diag_kerr_bl.{pdf,png}.
"""

from __future__ import annotations

import numpy as np

from geo_common import KERR_RESULTS
import geo_style as gs

A = 0.9
RUNS_ = [("mid", 0.02), ("mid", 0.01), ("bsym", 0.02), ("bsym", 0.01), ("bchol", 0.01)]


def cart(q):
    r, th, ph = q[:, 0], q[:, 1], q[:, 2]
    return r * np.sin(th) * np.cos(ph), r * np.sin(th) * np.sin(ph), r * np.cos(th)


def color(p, dt):
    sh = gs.shades(p, 5)
    return sh[1] if dt > 0.015 else sh[3]


def main():
    gs.use_style()
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse

    h = np.load(KERR_RESULTS / "kerr_histories.npz")
    tj = np.load(KERR_RESULTS / "bl_trajectories.npz")
    r_plus = 1 + np.sqrt(1 - A * A)
    fig, axs = plt.subplots(2, 4, figsize=(gs.FULL_WIDTH, 5.4))
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.08, top=0.955, wspace=0.62, hspace=0.36)
    for row, (key, tag, short, title) in enumerate((
            ("bl_equatorial_eccentric", "B_ecc", "ecc", "equatorial eccentric"),
            ("bl_inclined", "B_inc", "inc", "inclined"))):
        t = h[f"{tag}__t"]
        ax = axs[row, 0]
        X, Y, Z = cart(tj[f"{key}__x"].astype(float))
        Xr, Yr, Zr = cart(h[f"{tag}__xref"].astype(float))
        if row == 0:
            gs.black_hole_disk(ax, r_plus, 2.0, zorder=3)
            ax.plot(X, Y, color=gs.COLOR["bsym"], lw=0.4, zorder=2)
            ax.plot(Xr[0], Yr[0], "o", color=gs.COLOR["ref"], mec="k", ms=5, zorder=4)
            ax.plot(Xr[-1], Yr[-1], "s", color=gs.COLOR["ref"], mec="k", ms=5, zorder=4)
            ax.set_ylabel(r"$y/M$")
            lim = 12.5
        else:
            ax.add_patch(Ellipse((0, 0), 2 * r_plus, 2 * r_plus, color="black", lw=0, zorder=3))
            ax.plot([-2, 2], [0, 0], color="0.6", lw=2.5, zorder=2)
            ax.plot(X, Z, color=gs.COLOR["bsym"], lw=0.4, zorder=2)
            ax.plot(Xr[0], Zr[0], "o", color=gs.COLOR["ref"], mec="k", ms=5, zorder=4)
            ax.plot(Xr[-1], Zr[-1], "s", color=gs.COLOR["ref"], mec="k", ms=5, zorder=4)
            ax.set_ylabel(r"$z/M$")
            lim = 9.5
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect("equal")
        ax.set_xlabel(r"$x/M$", labelpad=-2)
        ax.set_title(title, fontsize=9, pad=3)
        q4 = "dLz" if row == 0 else "dQ"
        for col_i, q, lab in ((1, "dpos", r"$\|\delta(r/M,\theta,\phi)\|_\infty$"),
                              (2, "dE", r"$|\Delta E/E_0|$"),
                              (3, q4, r"$|\Delta L_z/L_{z,0}|$" if row == 0 else r"$|\Delta Q/Q_0|$")):
            ax = axs[row, col_i]
            for p, dt in RUNS_:
                k = f"B--{short}_{p}_dt{dt:g}__{q}"
                if k not in h.files:
                    continue
                y = np.maximum(h[k].astype(float), 1e-18)
                ax.plot(t if q == "dpos" else t[1:], y, color=color(p, dt), lw=1.0,
                        label=rf"{gs.PUSHER_NAME[p]}, $\Delta t={dt:g}M$")
            ax.set_yscale("log")
            ax.set_xlim(0, t[-1])
            ax.set_xlabel(r"$t/M$", labelpad=-2)
            ax.set_ylabel(lab)
            lo, hi = ax.get_ylim()
            ax.set_ylim(max(lo, 1e-14 if q != "dpos" else 1e-11), hi * 1e3)
        axs[row, 1].set_ylim(1e-11, 1e1)
    axs[0, 1].legend(loc="upper left", fontsize=6.5, ncol=1, handlelength=1.4, borderaxespad=0.2)
    axs[1, 2].text(0.97, 0.96, "Boris sym. = Chol.\n(diagonal BL metric)",
                   fontsize=7, ha="right", va="top", transform=axs[1, 2].transAxes)
    axs[0, 3].text(0.97, 0.96, "midpoint: $L_z$ cyclic,\nconserved to round-off", fontsize=7,
                   ha="right", va="top", transform=axs[0, 3].transAxes, color=gs.COLOR["mid"])
    print("wrote", gs.save_diag(fig, "diag_kerr_bl"))


if __name__ == "__main__":
    main()
