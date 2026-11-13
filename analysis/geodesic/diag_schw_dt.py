#!/usr/bin/env python3
"""Diagnostic figure for part A, analytic metric: the three Schwarzschild orbits.

One row per orbit (circular r = 8 M; eccentric p = 8 M, e = 0.3, inclined 30 deg; plunge,
inclined 45 deg, through the horizon to r = 1.02 M).  Columns: (1) exact trajectory projected
on the x-y plane (blue) with the black hole (r = 2M, black) and the start (blue dot); (2) position
error max(|dr|/M, |dtheta|, |dphi|) versus t for the implicit midpoint with spherical KS input
at dt = 0.08 ... 0.005 M (shades of red, light = large dt), divided by (dt/0.01 M)^2 so that a
second-order method collapses onto one curve; (3) position error at dt = 0.01 M for all
pusher / metric-input combinations; (4) |Delta E/E_0| at dt = 0.01 M (max over the records
between samples).  Colour = pusher (red midpoint, yellow Boris symmetric, green Boris
Cholesky), line style = metric input (solid spherical KS, dashed Cartesian KS).

Data: problems/schwarzschild/results/schw_histories.npz.
Output: analysis/geodesic/figs/diag_schw_dt.{pdf,png}.
"""

from __future__ import annotations

import numpy as np

from geo_common import SCHW_RESULTS
import geo_style as gs

ORBITS = [("circ", "circular"), ("ecc", "eccentric"), ("plunge", "plunge")]
DTS = [0.08, 0.04, 0.02, 0.01, 0.005]
COMBOS = [("mid", "ks"), ("mid", "cks"), ("bsym", "ks"), ("bsym", "cks"), ("bchol", "cks")]


def main():
    gs.use_style()
    import matplotlib.pyplot as plt

    h = np.load(SCHW_RESULTS / "schw_histories.npz")
    fig, axs = plt.subplots(3, 4, figsize=(gs.FULL_WIDTH, 7.8))
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.055, top=0.99, wspace=0.62, hspace=0.30)
    for row, (orbit, title) in enumerate(ORBITS):
        t = h[f"A_{orbit}__t"]
        q = h[f"A_{orbit}__xref"].astype(float)
        x = q[:, 0] * np.sin(q[:, 1]) * np.cos(q[:, 2])
        y = q[:, 0] * np.sin(q[:, 1]) * np.sin(q[:, 2])
        ax = axs[row, 0]
        gs.black_hole_disk(ax, 2.0)
        ax.plot(x, y, color=gs.COLOR["ref"], lw=1.0)
        ax.plot(x[0], y[0], "o", color=gs.COLOR["ref"], mec="k", ms=5)
        lim = 13 if orbit == "ecc" else 10.5
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect("equal")
        ax.set_xlabel(r"$x/M$", labelpad=-2)
        ax.set_ylabel(r"$y/M$")
        ax.set_title(title, fontsize=9, pad=3)

        ax = axs[row, 1]
        # circular orbit: the spherical-KS runs are exact up to round-off, so the Cartesian
        # family is shown there
        fam = "cks" if orbit == "circ" else "ks"
        for dt, col in zip(DTS, gs.shades("mid", len(DTS))):
            k = f"A--{orbit}_mid_{fam}_dt{dt:g}__dpos"
            if k in h.files:
                ax.plot(t, h[k].astype(float) / (dt / 0.01) ** 2, color=col, ls=gs.LS[fam],
                        label=rf"$\Delta t={dt:g}M$")
        ax.set_ylabel(r"$\|\delta\|_\infty\cdot(0.01M/\Delta t)^2$")
        ax.text(0.97, 0.04, f"midpoint, {'Cart.' if fam == 'cks' else 'sph.'} KS:\n5 curves coincide",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5)

        ax = axs[row, 2]
        for p, m in COMBOS:
            k = f"A--{orbit}_{p}_{m}_dt0.01__dpos"
            if k in h.files:
                ax.plot(t, h[k].astype(float), **gs.style(p, m))
        ax.set_ylabel(r"$\|\delta(r/M,\theta,\phi)\|_\infty$, $\Delta t=0.01M$")
        ax = axs[row, 3]
        for p, m in COMBOS:
            k = f"A--{orbit}_{p}_{m}_dt0.01__dE"
            if k in h.files:
                ax.plot(t[1:], np.maximum(h[k].astype(float), 1e-17), lw=1.0, **gs.style(p, m))
        ax.set_ylabel(r"$|\Delta E/E_0|$, $\Delta t=0.01M$")
        for ax in axs[row, 1:]:
            ax.set_yscale("log")
            ax.set_xlim(0, t[-1])
            ax.set_xlabel(r"$t/M$", labelpad=-2)
            if orbit != "plunge":
                ax.set_xticks([0, 400, 800])
        lo, hi = axs[row, 1].get_ylim()
        axs[row, 1].set_ylim(max(lo, 1e-10), hi * 1e2)
        lo, hi = axs[row, 2].get_ylim()
        axs[row, 2].set_ylim(max(lo, 1e-14), hi * 1e3)
        lo, hi = axs[row, 3].get_ylim()
        axs[row, 3].set_ylim(max(lo, 1e-17), hi * 1e2)
    hs = [plt.Line2D([], [], label=gs.label(p, m).replace("analytic ", ""), **gs.style(p, m))
          for p, m in COMBOS]
    axs[0, 2].legend(handles=hs, loc="upper left", fontsize=6, ncol=1, handlelength=1.8,
                     borderaxespad=0.2)
    axs[0, 2].set_ylim(axs[0, 2].get_ylim()[0], axs[0, 2].get_ylim()[1] * 1e3)
    hs = [plt.Line2D([], [], color=c, label=rf"$\Delta t={dt:g}M$")
          for dt, c in zip(DTS, gs.shades("mid", len(DTS)))]
    axs[0, 1].legend(handles=hs, loc="upper left", fontsize=6.5, ncol=1, handlelength=1.2,
                     borderaxespad=0.2)
    axs[0, 1].set_ylim(axs[0, 1].get_ylim()[0], axs[0, 1].get_ylim()[1] * 1e2)
    print("wrote", gs.save_diag(fig, "diag_schw_dt"))


if __name__ == "__main__":
    main()
