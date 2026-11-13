#!/usr/bin/env python3
"""Diagnostic figure for part D: the same Kerr-Schild passage input (dt = 0.01 M, t = 230 M) on
the GPU executable and on the serial CPU executable.

Left: trajectory near pericentre in the x-y plane of Cartesian KS (GPU red/green solid, CPU
orange dashed).  Middle: max |x_CPU - x_GPU| and |u_CPU - u_GPU| (max over components and over
the records in 0.4 M bins) versus t, for implicit midpoint with analytic spherical KS input (red)
and Boris (Cholesky triad) with the Hermite lattice (green); solid = position, dashed =
momentum.  Right: |Delta E/E_0| of the GPU (method colour) and CPU (orange) runs.

Data: problems/kerr/results/kerr_histories.npz (analyze_kerr.py).
Output: analysis/geodesic/figs/diag_cpu_gpu.{pdf,png}.
"""

from __future__ import annotations

import numpy as np

from geo_common import KERR_RESULTS, kerr
import geo_style as gs

A = 0.9
RUNSEL = [("mid", "ks"), ("bchol", "lat")]


def main():
    gs.use_style()
    import matplotlib.pyplot as plt

    h = np.load(KERR_RESULTS / "kerr_histories.npz")
    t = h["C__t"]
    fig, axs = plt.subplots(1, 3, figsize=(gs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.15, top=0.97, wspace=0.38)

    # trajectory near pericentre (from the run directories if present, else the reference)
    ax = axs[0]
    r_plus = 1 + np.sqrt(1 - A * A)
    gs.black_hole_disk(ax, np.sqrt(r_plus ** 2 + A * A), np.sqrt(4 + A * A))
    for p, m in RUNSEL:
        for exe, ls, col in (("gpu", "-", gs.COLOR[p]), ("cpu", "--", gs.COLOR["cpu"])):
            x = h[f"D--{p}_{m}_dt0.01__x_{exe}"].astype(float)     # every 0.1 M
            xc = kerr.ks_to_cks_position(x, A) if m == "ks" else x
            ax.plot(xc[:, 0], xc[:, 1], ls=ls, color=col, lw=1.2 if exe == "gpu" else 1.0)
    ax.set_aspect("equal")
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-4.5, 4.5)
    ax.set_xlabel(r"$x/M$", labelpad=-2)
    ax.set_ylabel(r"$y/M$")
    hs = [plt.Line2D([], [], color=gs.COLOR["mid"], label="GPU, midpoint"),
          plt.Line2D([], [], color=gs.COLOR["bchol"], label="GPU, Boris Chol."),
          plt.Line2D([], [], color=gs.COLOR["cpu"], ls="--", lw=1.0, label="CPU")]
    ax.legend(handles=hs, loc="lower left", fontsize=7, handlelength=1.6, borderaxespad=0.2)

    ax = axs[1]
    for p, m in RUNSEL:
        k = f"D--{p}_{m}_dt0.01"
        dx = np.maximum(h[f"{k}__dx"].astype(float), 1e-20)
        du = np.maximum(h[f"{k}__du"].astype(float), 1e-20)
        ax.plot(t[1:], dx, color=gs.COLOR[p], ls="-", label=f"{gs.PUSHER_NAME[p]}: position")
        ax.plot(t[1:], du, color=gs.COLOR[p], ls="--", lw=1.0, label=f"{gs.PUSHER_NAME[p]}: momentum")
    ax.set_yscale("log")
    ax.set_xlim(0, 230)
    ax.set_ylim(1e-19, 1e-2)
    ax.set_xlabel(r"$t/M$", labelpad=-2)
    ax.set_ylabel(r"$\max|{\rm CPU}-{\rm GPU}|$")
    ax.legend(loc="upper left", fontsize=7, ncol=1, handlelength=1.8)

    ax = axs[2]
    for p, m in RUNSEL:
        k = f"D--{p}_{m}_dt0.01"
        ax.plot(t[1:], h[f"{k}__dE_gpu"].astype(float), color=gs.COLOR[p], ls=gs.LS[m],
                label=f"{gs.PUSHER_NAME[p]}, GPU")
        ax.plot(t[1:], h[f"{k}__dE_cpu"].astype(float), color=gs.COLOR["cpu"], ls=(0, (2, 3)),
                lw=1.2, label=f"{gs.PUSHER_NAME[p]}, CPU")
    ax.set_yscale("log")
    ax.set_xlim(0, 230)
    ax.set_ylim(1e-14, 1e0)
    ax.set_xlabel(r"$t/M$", labelpad=-2)
    ax.set_ylabel(r"$|\Delta E/E_0|$ (max per $0.4M$)")
    ax.legend(loc="upper left", fontsize=7, ncol=1, handlelength=1.8)
    print("wrote", gs.save_diag(fig, "diag_cpu_gpu"))


if __name__ == "__main__":
    main()
