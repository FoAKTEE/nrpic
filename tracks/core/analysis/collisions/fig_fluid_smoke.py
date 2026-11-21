#!/usr/bin/env python3
"""Figure of the fluid smoke run (stock TOV star of dyn_grmhd on Z4c, deck
problems/tests/fluid_tov_z4c.athinput): maximum rest-mass density, minimum lapse,
relative change of the rest mass, and the constraint norms against time.

  fig_fluid_smoke.py RUNDIR [OUT.png]

Reads tov.mhd.hst, tov.user.hst, tov.z4c.user.hst of the run directory; writes the
figure (default RUNDIR/fig_fluid_smoke.png) and prints the numbers quoted in
tracks/core/interfaces/collisions.md section 12.
"""
import os
import sys

import numpy as np

import common


def hst(path):
    with open(path) as fp:
        lines = fp.readlines()
    names = []
    for ln in lines:
        if ln.startswith("#") and "[1]=" in ln:
            names = [t.split("=")[1] for t in ln[1:].split()]
    data = np.loadtxt([ln for ln in lines if not ln.startswith("#")], ndmin=2)
    return {n: data[:, i] for i, n in enumerate(names)}


def main():
    rd = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(rd, "fig_fluid_smoke.png")
    m = hst(os.path.join(rd, "tov.mhd.hst"))
    u = hst(os.path.join(rd, "tov.user.hst"))
    z = hst(os.path.join(rd, "tov.z4c.user.hst"))
    dm = m["mass"]/m["mass"][0] - 1.0
    print(f"rest mass {m['mass'][0]:.9f} -> {m['mass'][-1]:.9f} (relative {dm[-1]:+.2e})")
    print(f"rho_max {u['rho-max'][0]:.4e} -> {u['rho-max'][-1]:.4e} "
          f"({u['rho-max'][-1]/u['rho-max'][0] - 1.0:+.3f})")
    print(f"alpha_min {u['alpha-min'][0]:.4f} -> {u['alpha-min'][-1]:.4f}")
    print(f"H-norm2 {z['H-norm2'][0]:.3e} -> {z['H-norm2'][-1]:.3e}, "
          f"M-norm2 {z['M-norm2'][0]:.3e} -> {z['M-norm2'][-1]:.3e}")
    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(9.0, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.95, wspace=0.38)
    axs[0].plot(u["time"], u["rho-max"]/u["rho-max"][0], color=fs.PAL["red"], lw=1.0,
                label=r"$\rho_{\max}/\rho_{\max}(0)$")
    axs[0].plot(u["time"], u["alpha-min"]/u["alpha-min"][0], color=fs.PAL["blue"], lw=1.0,
                label=r"$\alpha_{\min}/\alpha_{\min}(0)$")
    axs[0].axhline(1.0, **fs.GUIDE)
    axs[0].set_xlabel(r"$t$")
    axs[0].legend(fontsize=7)
    axs[1].plot(m["time"], dm, color="k", lw=1.0)
    axs[1].set_xlabel(r"$t$")
    axs[1].set_ylabel(r"$\Delta M_0/M_0$")
    axs[2].semilogy(z["time"], z["H-norm2"], color=fs.PAL["red"], lw=1.0, label=r"$\|H\|_2$")
    axs[2].semilogy(z["time"], z["M-norm2"], color=fs.PAL["blue"], lw=1.0, label=r"$\|M\|_2$")
    axs[2].set_xlabel(r"$t$")
    axs[2].legend(fontsize=7)
    fig.savefig(out, dpi=200)
    print(out)


if __name__ == "__main__":
    main()
