#!/usr/bin/env python3
"""Diagnostic figure for part E: the inclined Kerr orbit (a = 0.9 M) with the Cartesian
Kerr-Schild metric on the AthenaK mesh, dx = 0.5, 0.25, 0.125 M, dt = 0.01 M, t = 600 M.

Top: trajectory in the x-y and x-z planes (exact reference, blue; mesh run dx = 0.5 M, red
dotted) with the MeshBlock boundaries of the dx = 0.125 M mesh (grey), the event horizon (black)
and the equatorial ergosphere (grey); final-position error versus dx (mesh: dotted, filled;
virtual lattice: open; analytic Cartesian KS at the same dt: dashed horizontal).
Bottom: position error, |Delta E/E_0| and the reconstruction error |Delta alpha| of the lapse at
the particle versus t, for the three dx (shades of red, light = coarse) and the analytic run.

Data: problems/kerr/results/{kerr_histories.npz, kerr_summary.json}.
Output: analysis/geodesic/figs/diag_kerr_mesh.{pdf,png}.
"""

from __future__ import annotations

import numpy as np

from geo_common import KERR_RESULTS, kerr, load_json
import geo_style as gs

A = 0.9
DXS = [0.5, 0.25, 0.125]


def main():
    gs.use_style()
    import matplotlib.pyplot as plt

    h = np.load(KERR_RESULTS / "kerr_histories.npz")
    S = load_json(KERR_RESULTS / "kerr_summary.json")["E"]
    t = h["E__t"]
    xref = kerr.ks_to_cks_position(h["E__xref"].astype(float), A)
    fig, axs = plt.subplots(2, 3, figsize=(gs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.075, top=0.985, wspace=0.36, hspace=0.26)
    r_plus = 1 + np.sqrt(1 - A * A)
    rho_h, rho_e = np.sqrt(r_plus ** 2 + A * A), np.sqrt(4 + A * A)

    # trajectories
    xr = h["E--inc_mid_mesh_dx0.5__x"].astype(float)
    for ax, (i, j, lab) in zip(axs[0, :2], ((0, 1, r"$y/M$"), (0, 2, r"$z/M$"))):
        for v in np.arange(-10, 10.1, 5.0):
            ax.axvline(v, color="0.85", lw=0.8, zorder=0)
        for v in (np.arange(-10, 10.1, 5.0) if j == 1 else [-5, 0, 5]):
            ax.axhline(v, color="0.85", lw=0.8, zorder=0)
        if j == 1:
            gs.black_hole_disk(ax, rho_h, rho_e)
        else:
            from matplotlib.patches import Ellipse
            ax.add_patch(Ellipse((0, 0), 2 * rho_h, 2 * r_plus, color="black", lw=0, zorder=2))
            ax.plot([-rho_e, rho_e], [0, 0], color="0.6", lw=2.5, zorder=1)
        ax.plot(xref[:, i], xref[:, j], color=gs.COLOR["ref"], lw=1.0, label="exact")
        ax.plot(xr[:, i], xr[:, j], color=gs.COLOR["mid"], ls=":", lw=1.2,
                label=r"midpoint, mesh $\Delta x=0.5M$")
        ax.plot(xref[0, i], xref[0, j], "o", color=gs.COLOR["ref"], ms=5, mec="k", mew=0.6)
        ax.set_aspect("equal")
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10) if j == 1 else ax.set_ylim(-5, 5)
        ax.set_xlabel(r"$x/M$", labelpad=-2)
        ax.set_ylabel(lab)
    hs = [plt.Line2D([], [], color=gs.COLOR["ref"], lw=1.0, label="exact"),
          plt.Line2D([], [], color=gs.COLOR["mid"], ls=":", lw=1.2, label=r"mesh, $\Delta x=0.5M$")]
    axs[0, 1].legend(handles=hs, loc="upper left", fontsize=7, ncol=1, handlelength=1.6,
                     borderaxespad=0.2)

    # final error vs dx
    ax = axs[0, 2]
    for p in ("mid", "bsym"):
        for metric, mfc in (("mesh", None), ("lat", "white")):
            c = S["dx_convergence"].get(f"{p}_{metric}")
            if c is None:
                continue
            kw = gs.style(p, "mesh") if metric == "mesh" else dict(color=gs.COLOR[p], ls="none")
            ax.plot(c["dx"], c["err"], marker=gs.MARKER[p], ms=5 if metric == "mesh" else 8,
                    mfc=mfc or gs.COLOR[p], mec=gs.COLOR[p], **kw)
        a = S["runs"].get(f"kerr_mesh/inc_{p}_cks")
        if a is not None:
            ax.axhline(a["final_pos_err"], **gs.style(p, "cks", lw=1.0))
    c = S["dx_convergence"]["mid_mesh"]
    dx = np.array([0.1, 0.6])
    e = c["err"][c["dx"].index(0.25)]
    ax.plot(dx, 0.4 * e * (dx / 0.25) ** 3, **gs.GUIDE)
    ax.text(0.33, 0.4 * e * (0.33 / 0.25) ** 3 / 4, r"$\propto\Delta x^3$", fontsize=9)
    ax.text(0.55, a["final_pos_err"] * 1.6, r"analytic Cart. KS, $\Delta t=0.01M$", fontsize=8,
            ha="right")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.1, 0.6)
    ax.set_xticks(DXS)
    ax.set_xticklabels(["0.5", "0.25", "0.125"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel(r"$\Delta x/M$", labelpad=-2)
    ax.set_ylabel(r"$\|\delta(r/M,\theta,\phi)\|_\infty$ at $t=600M$")
    ax.set_ylim(1e-6, 2e-2)
    hs = [plt.Line2D([], [], marker="o", ms=5, **gs.style("mid", "mesh"), label="midpoint, mesh"),
          plt.Line2D([], [], marker="^", ms=5, **gs.style("bsym", "mesh"), label="Boris sym., mesh"),
          plt.Line2D([], [], marker="o", ms=8, mfc="white", color="0.3", ls="none",
                     label="virtual lattice")]
    ax.legend(handles=hs, loc="upper left", fontsize=7.5)

    # histories
    cols = gs.shades("mid", 3)
    for ax, q, lab in ((axs[1, 0], "dpos", r"$\|\delta(r/M,\theta,\phi)\|_\infty$"),
                       (axs[1, 1], "dE", r"$|\Delta E/E_0|$"),
                       (axs[1, 2], "dalpha", r"$|\Delta\alpha|$ at the particle")):
        for dx, col in zip(DXS, cols):
            y = h[f"E--inc_mid_mesh_dx{dx:g}__{q}"].astype(float)
            tt = t if q == "dpos" else t[1:]
            ax.plot(tt, y, color=col, ls=":", label=rf"mesh $\Delta x={dx:g}M$")
        if q != "dalpha":
            y = h[f"E--inc_mid_cks__{q}"].astype(float)
            ax.plot(t if q == "dpos" else t[1:], y, **gs.style("mid", "cks"),
                    label="analytic Cart. KS")
        ax.set_yscale("log")
        ax.set_xlim(0, 600)
        ax.set_xlabel(r"$t/M$", labelpad=-2)
        ax.set_ylabel(lab)
    axs[1, 0].set_ylim(1e-9, 10)
    axs[1, 1].set_ylim(1e-13, 1e-3)
    axs[1, 2].set_ylim(1e-9, 1e-4)
    axs[1, 0].legend(loc="upper left", fontsize=7.5, ncol=1, handlelength=1.8)
    print("wrote", gs.save_diag(fig, "diag_kerr_mesh"))


if __name__ == "__main__":
    main()
