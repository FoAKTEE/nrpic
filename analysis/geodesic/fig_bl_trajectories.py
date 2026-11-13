#!/usr/bin/env python3
"""Figure fig_bl_trajectories.pdf: the two bound Boyer-Lindquist orbits (a = 0.9 M) evolved with
the spacetime (DGREM) Boris pusher (symmetric triad, dt = 0.01 M).

Left: equatorial-eccentric orbit over 20 radial periods in the x-y plane.  Right: inclined orbit
over 18 radial periods in 3D.  x = r sin(theta) cos(phi), y = r sin(theta) sin(phi),
z = r cos(theta) with BL r, theta, phi.  Event horizon (r_+ = 1.436 M) filled black, equatorial
ergosphere (r <= 2M in the equatorial plane) grey, initial points blue with black edge.
Orbit colour: yellow = Boris, symmetric triad (geo_style.py mapping).

Data: problems/kerr/results/bl_trajectories.npz (analyze_kerr.py).
Output: paper/figures/fig_bl_trajectories.pdf (+ PNG copy in analysis/geodesic/figs).
"""

from __future__ import annotations

import numpy as np

from geo_common import KERR_RESULTS
import geo_style as gs

A = 0.9


def cart(x):
    r, th, ph = x[:, 0], x[:, 1], x[:, 2]
    return r * np.sin(th) * np.cos(ph), r * np.sin(th) * np.sin(ph), r * np.cos(th)


def main():
    gs.use_style()
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    import mpl_toolkits.mplot3d.art3d as art3d

    d = np.load(KERR_RESULTS / "bl_trajectories.npz")
    r_plus = 1 + np.sqrt(1 - A * A)
    r_ergo = 2.0
    col = gs.COLOR["bsym"]

    fig = plt.figure(figsize=(gs.FULL_WIDTH, 4.0))
    ax1 = fig.add_axes([0.075, 0.115, 0.40, 0.80])
    ax2 = fig.add_axes([0.49, 0.02, 0.46, 0.93], projection="3d")

    x = d["bl_equatorial_eccentric__x"].astype(float)
    X, Y, _ = cart(x)
    gs.black_hole_disk(ax1, r_plus, r_ergo, zorder=3)
    ax1.plot(X, Y, color=col, lw=0.6, zorder=2)
    X0, Y0, _ = cart(d["x0_ecc"][None, :])
    ax1.plot(X0, Y0, ls="none", marker="o", ms=6, color=gs.COLOR["ref"], mec="black", mew=0.8,
             zorder=5)
    ax1.set_aspect("equal")
    lim = 12.5
    ax1.set_xlim(-lim, lim)
    ax1.set_ylim(-lim, lim)
    ax1.set_xlabel(r"$x/M$", labelpad=-2)
    ax1.set_ylabel(r"$y/M$")
    ax1.set_title(r"equatorial eccentric, $20\,T_r$", fontsize=10, pad=4)

    x = d["bl_inclined__x"].astype(float)
    X, Y, Z = cart(x)
    u, v = np.meshgrid(np.linspace(0, np.pi, 40), np.linspace(0, 2 * np.pi, 60))
    ax2.plot_surface(r_plus * np.sin(u) * np.cos(v), r_plus * np.sin(u) * np.sin(v),
                     r_plus * np.cos(u), color="black", lw=0, shade=False, antialiased=False)
    ring = Circle((0, 0), r_ergo, color="0.75", lw=0)
    ax2.add_patch(ring)
    art3d.pathpatch_2d_to_3d(ring, z=0, zdir="z")
    ax2.plot(X, Y, Z, color=col, lw=0.5)
    X0, Y0, Z0 = cart(d["x0_inc"][None, :])
    ax2.plot(X0, Y0, Z0, ls="none", marker="o", ms=6, color=gs.COLOR["ref"], mec="black",
             mew=0.8, zorder=10)
    lim = 9.0
    for setl in (ax2.set_xlim, ax2.set_ylim, ax2.set_zlim):
        setl(-lim, lim)
    ax2.set_box_aspect((1, 1, 1))
    ax2.set_xlabel(r"$x/M$", labelpad=-4)
    ax2.set_ylabel(r"$y/M$", labelpad=-4)
    ax2.set_zlabel(r"$z/M$", labelpad=-5)
    ax2.tick_params(axis="both", which="major", pad=-2, labelsize=8)
    for axis in (ax2.xaxis, ax2.yaxis, ax2.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("0.8")
        axis._axinfo["grid"]["linewidth"] = 0.3
    ax2.view_init(elev=20, azim=-55)
    ax2.text2D(0.5, 0.97, r"inclined, $18\,T_r$", transform=ax2.transAxes, ha="center", va="top",
               fontsize=10)
    from matplotlib.ticker import NullLocator
    for axis in (ax2.xaxis, ax2.yaxis, ax2.zaxis):
        axis.set_minor_locator(NullLocator())
    print("wrote", gs.save_paper(fig, "fig_bl_trajectories"))


if __name__ == "__main__":
    main()
