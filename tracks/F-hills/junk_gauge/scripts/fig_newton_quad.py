#!/usr/bin/env python3
"""Figure of the J4 reference: Newtonian quadrupole luminosity and its cumulative energy for P1's
track, with the separations. Reads newton_quad.json and newton_quad_track.npz.
Usage: fig_newton_quad.py <dir | ->
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def main():
    d = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    res = json.load(open(os.path.join(d, "newton_quad.json")))
    c = np.load(os.path.join(d, "newton_quad_track.npz"))
    t = c["t"]
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    ax[0].semilogy(t, c["L"], color=fs.PAL["blue"], lw=1.1)
    ax[0].axhline(res["L_circular_binary_formula"], **fs.GUIDE)
    if res["t_L_above_2x"] is not None:
        ax[0].axvline(res["t_L_above_2x"], **fs.MASK_LINE)
    ax[0].set_ylabel(r"$L_{\rm quad}$ (dashed: circular binary)")
    ax[1].semilogy(t, np.maximum(c["E"], 1e-12), color=fs.PAL["blue"], lw=1.1)
    ax[1].set_ylabel(r"$\int_0^t L_{\rm quad}\,dt$ [$M$]")
    ax[2].plot(t, c["rcm"], color=fs.PAL["red"], lw=1.1, label="binary c.o.m. to heavy hole")
    ax[2].plot(t, c["r12"], color=fs.PAL["green"], lw=1.1, label="member separation")
    ax[2].set_ylabel(r"distance [$M$]")
    ax[2].legend(frameon=False, fontsize=7)
    for a in ax:
        a.set_xlabel(r"$t$ [$M$] (Newtonian, bare masses)")
        a.set_xlim(0, t[-1])
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(d, "fig_newton_quad")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
