#!/usr/bin/env python3
"""Test T6 of the Newtonian mode: a moving, rotating ball on an isolated domain. No
exact solution; the conservation laws and the consistency of the second-moment columns
are checked for a configuration without symmetry (problems/newton/README.md).

    analyze_conservation.py --ic STEM.json --run RUNDIR --out DIR [--name spin]

Writes DIR/<name>.png and DIR/<name>.json: drift of the centre of mass from uniform
motion, of the momentum, of the angular momentum about the centre of mass and of the
energy; for each of the six components of the second moment the mismatch between the
centred time difference of one column and the next column.
"""
import argparse
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "python")))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402

COMP = ("xx", "xy", "xz", "yy", "yz", "zz")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ic", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="spin")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    meta = json.load(open(a.ic))
    gm, rad = meta["mass"], meta["radius"]
    h = nw.read_newton_hst(glob.glob(os.path.join(a.run, "*.newton.hst"))[0])
    t = h["time"]
    mass = h["mass"][0]
    vscale = np.sqrt(gm/rad)
    X = np.stack([h["X_%s" % c] for c in "xyz"], axis=1)
    P = np.stack([h["P_%s" % c] for c in "xyz"], axis=1)
    L = np.stack([h["L_%s" % c] for c in "xyz"], axis=1)
    V0 = P[0]/mass
    dX = X - X[0] - t[:, None]*V0
    dP = (P - P[0])/(mass*vscale)
    Lc = L - mass*np.cross(X, P/mass)                 # about the centre of mass
    dL = (Lc - Lc[0])/np.linalg.norm(Lc[0])
    e = h["K"] + h["W"]
    de = (e - e[0])/abs(e[0])

    res = dict(rundir=a.run, steps=int(len(t) - 1), t_end=float(t[-1]),
               mass_change=float(abs(h["mass"][-1] - mass)/mass),
               com_drift_end=float(np.linalg.norm(dX[-1])/rad),
               com_drift_max=float(np.max(np.linalg.norm(dX, axis=1))/rad),
               momentum_drift_max=float(np.max(np.linalg.norm(dP, axis=1))),
               angular_momentum_initial=Lc[0].tolist(),
               angular_momentum_drift_max=float(np.max(np.linalg.norm(dL, axis=1))),
               energy0=float(e[0]), energy_rel_end=float(de[-1]),
               energy_rel_max=float(np.max(np.abs(de))),
               mg_cycles_mean=float(np.mean(h["mg_cycles"][1:])), columns={})
    for c in COMP:
        fdI = (h["I_" + c][2:] - h["I_" + c][:-2])/(t[2:] - t[:-2])
        fddI = (h["dI_" + c][2:] - h["dI_" + c][:-2])/(t[2:] - t[:-2])
        q3 = np.diff(h["d2I_" + c])/np.diff(t)
        res["columns"][c] = dict(
            dI=float(np.max(np.abs(fdI - h["dI_" + c][1:-1]))/np.max(np.abs(h["dI_" + c]))),
            d2I=float(np.max(np.abs(fddI - h["d2I_" + c][1:-1]))
                      / np.max(np.abs(h["d2I_" + c]))),
            d3I=float(np.max(np.abs(q3 - h["d3I_" + c][1:]))
                      / np.max(np.abs(h["d3I_" + c]))))

    cols = fs.series_colors(3)
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.09, top=0.97, wspace=0.40,
                        hspace=0.27)
    ax = axs[0, 0]
    for k, c in enumerate("xyz"):
        ax.plot(t, 1e4*dX[:, k]/rad, color=cols[k], label=c)
    ax.set_ylabel(r"$(X - X_0 - Vt)/R$  [$10^{-4}$]")
    ax.legend(loc="upper left", ncol=3, fontsize=8)
    ax = axs[0, 1]
    for k, c in enumerate("xyz"):
        ax.plot(t, 1e4*dP[:, k], color=cols[k], label=r"$P_%s$" % c)
        ax.plot(t, 1e4*dL[:, k], "--", color=cols[k], label=r"$L_%s$" % c)
    ax.set_ylabel(r"change of $P$, $L$  [$10^{-4}$]")
    ax.legend(loc="lower left", ncol=3, fontsize=7, columnspacing=0.8)
    ax = axs[0, 2]
    ax.plot(t, 1e3*de, color=fs.PAL["red"])
    ax.set_ylabel(r"$(E-E_0)/|E_0|$  [$10^{-3}$]")
    q0 = nw.quadrupole(h, 0)
    q2 = nw.quadrupole(h, 2)
    q3 = nw.quadrupole(h, 3)
    cs = fs.series_colors(6, "viridis")
    idx = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
    for ax, q, tt, lab in ((axs[1, 0], q0, t, r"$Q_{ij}$"),
                           (axs[1, 1], q2, t, r"$d^2Q_{ij}/dt^2$"),
                           (axs[1, 2], q3[1:], h["time_d3I"][1:], r"$d^3Q_{ij}/dt^3$")):
        for (i, j), cc, c in zip(idx, cs, COMP):
            ax.plot(tt, q[:, i, j], color=cc, lw=1.0, label=c)
        ax.set_ylabel(lab)
    axs[1, 0].legend(loc="upper left", ncol=3, fontsize=7, columnspacing=0.8)
    for ax in axs.ravel():
        ax.set_xlabel(r"$t$", labelpad=-1)
        ax.set_xlim(0, t[-1])
    fig.savefig(os.path.join(a.out, a.name + ".png"), dpi=200)
    with open(os.path.join(a.out, a.name + ".json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
