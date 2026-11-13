#!/usr/bin/env python3
"""Diagnostic figure for part A, mesh metric: circular and eccentric Schwarzschild orbits with
the Cartesian Kerr-Schild metric stored on the AthenaK mesh (dt = 0.01 M).

One row per orbit.  Columns: (1) exact trajectory projected on the x-y plane (blue), mesh run
dx = 0.5 M (red dotted), black hole (r = 2M) and the MeshBlock boundaries of the dx = 0.125 M
mesh (grey); (2) position error max(|dr|/M, |dtheta|, |dphi|) versus t for dx = 0.5, 0.25,
0.125 M (shades of red, light = coarse), midpoint, and the analytic Cartesian KS run at the same
dt (red dashed); (3) |Delta E/E_0| versus t, same runs; (4) |Delta alpha| of the lapse
reconstructed at the particle.

Data: problems/schwarzschild/results/schw_histories.npz.
Output: analysis/geodesic/figs/diag_schw_mesh.{pdf,png}.
"""

from __future__ import annotations

import numpy as np

from geo_common import SCHW_RESULTS, kerr
import geo_style as gs

DXS = [0.5, 0.25, 0.125]
BLOCKS = {"circ": (np.arange(-10, 10.1, 5.0), np.arange(-10, 10.1, 5.0)),
          "ecc": (np.arange(-12, 12.1, 6.0), np.arange(-12, 12.1, 6.0))}


def main():
    gs.use_style()
    import matplotlib.pyplot as plt

    h = np.load(SCHW_RESULTS / "schw_histories.npz")
    fig, axs = plt.subplots(2, 4, figsize=(gs.FULL_WIDTH, 5.2))
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.085, top=0.985, wspace=0.62, hspace=0.30)
    for row, (orbit, title) in enumerate((("circ", "circular"), ("ecc", "eccentric"))):
        t = h[f"A_{orbit}__t"]
        xr = kerr.ks_to_cks_position(h[f"A_{orbit}__xref"].astype(float), 0.0)
        ax = axs[row, 0]
        bx, by = BLOCKS[orbit]
        for v in bx:
            ax.axvline(v, color="0.85", lw=0.8, zorder=0)
        for v in by:
            ax.axhline(v, color="0.85", lw=0.8, zorder=0)
        gs.black_hole_disk(ax, 2.0)
        ax.plot(xr[:, 0], xr[:, 1], color=gs.COLOR["ref"], lw=1.0)
        k = f"Am--{orbit}_mid_mesh_dx0.5__x"
        if k in h.files:
            x = h[k].astype(float)
            ax.plot(x[:, 0], x[:, 1], color=gs.COLOR["mid"], ls=":", lw=1.2)
        ax.plot(xr[0, 0], xr[0, 1], "o", color=gs.COLOR["ref"], mec="k", ms=5)
        lim = bx[-1]
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect("equal")
        ax.set_xlabel(r"$x/M$", labelpad=-2)
        ax.set_ylabel(r"$y/M$")
        ax.set_title(title, fontsize=9, pad=3)
        for col_i, q, lab in ((1, "dpos", r"$\|\delta(r/M,\theta,\phi)\|_\infty$"),
                              (2, "dE", r"$|\Delta E/E_0|$"),
                              (3, "dalpha", r"$|\Delta\alpha|$ at the particle")):
            ax = axs[row, col_i]
            for dx, col in zip(DXS, gs.shades("mid", 3)):
                k = f"Am--{orbit}_mid_mesh_dx{dx:g}__{q}"
                if k in h.files:
                    ax.plot(t if q == "dpos" else t[1:], h[k].astype(float), color=col, ls=":",
                            label=rf"$\Delta x={dx:g}M$")
            k = f"A--{orbit}_mid_cks_dt0.01__{q}"
            if q != "dalpha" and k in h.files:
                ax.plot(t if q == "dpos" else t[1:], np.maximum(h[k].astype(float), 1e-17),
                        label="analytic", **gs.style("mid", "cks"))
            ax.set_yscale("log")
            ax.set_xlim(0, t[-1])
            ax.set_xticks([0, 400, 800])
            ax.set_xlabel(r"$t/M$", labelpad=-2)
            ax.set_ylabel(lab)
        axs[row, 1].set_ylim(1e-8, 1e3)
        axs[row, 2].set_ylim(1e-16, 1e-1)
        axs[row, 3].set_ylim(1e-9, 1e-3)
        axs[row, 1].legend(loc="upper left", fontsize=6.5, ncol=1, handlelength=1.6,
                           borderaxespad=0.2)
    print("wrote", gs.save_diag(fig, "diag_schw_mesh"))


if __name__ == "__main__":
    main()
