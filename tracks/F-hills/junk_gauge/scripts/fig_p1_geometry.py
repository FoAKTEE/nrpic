#!/usr/bin/env python3
"""Figure of J4g: P1's binary from its trackers. Left: member separation and distances of the
binary's centre of mass and of the heavy hole from the grid origin. Middle: coordinate-track
quadrupole luminosity and the circular formula at the tracked separation. Right: the earliest
retarded arrival u_near(t_e) = t_e - |x_b(t_e)| at a sphere about the origin.
Reads p1_geometry.json and p1_geometry.npz. Usage: fig_p1_geometry.py <dir | ->
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
    res = json.load(open(os.path.join(d, "p1_geometry.json")))
    c = np.load(os.path.join(d, "p1_geometry.npz"))
    t = c["t"]
    tm = res["t_merge"]
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    ax[0].plot(t, c["r12"], color=fs.PAL["green"], lw=1.1, label="member separation")
    ax[0].plot(t, c["db"], color=fs.PAL["red"], lw=1.1, label=r"$|x_b|$ binary c.o.m.")
    ax[0].plot(t, c["dh"], color=fs.PAL["blue"], lw=1.1, label="heavy hole")
    ax[0].set_ylabel(r"distance from origin [$M$]")
    ax[0].legend(frameon=False, fontsize=7)
    pre = t <= tm
    ax[1].semilogy(t[pre], c["L"][pre], color=fs.PAL["blue"], lw=1.1, label=r"$L_{\rm trk}$")
    ax[1].semilogy(t[pre], c["Lc"][pre], color=fs.PAL["red"], lw=1.0, label="circular formula")
    ax[1].axhline(res["L_trk_median_2_20"], **fs.GUIDE)
    ax[1].axhline(3 * res["L_trk_median_2_20"], **fs.MASK_LINE)
    if res.get("t_L_above_3x") is not None:
        ax[1].axvline(res["t_L_above_3x"], **fs.MASK_LINE)
    ax[1].set_ylabel(r"$L$ (dashed: median 2-20 $M$)")
    ax[1].legend(frameon=False, fontsize=7)
    ax[2].plot(t, c["u_near"], color=fs.PAL["blue"], lw=1.1)
    ax[2].set_ylabel(r"$u_{\rm near}=t_e-|x_b(t_e)|$ [$M$]")
    for a in ax:
        a.axvline(tm, color="grey", lw=0.8, ls=":")
        a.set_xlabel(r"$t$ [$M$] (dotted: merger)")
        a.set_xlim(0, min(t[-1], 120))
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(d, "fig_p1_geometry")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
