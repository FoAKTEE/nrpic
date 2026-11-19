"""Figure: the code's Newtonian mode against exact references (note v1, G1).

(a) Plane-wave pancake (delta = 0.05, box of one length unit, one particle per cell):
largest sheet error against the exact Zel'dovich continuum, in units of the displacement,
at a = 2, 5, 10, 15 for n = 16, 32, 64 cells (filled), the prediction of linear theory with
the force of the seven-point Laplacian (lines, hypothesis H1 of newton_tests), and the
spectral particle-mesh reference at n = 32, 64 (open). (b) Isolated homogeneous ellipsoid
(benchmark of arXiv:2605.04487): relative error of the first crossing time and of the
quadrupole energy to the first crossing against the ellipsoid ODE, N = 32, 64, 128 cells,
with guides of slope -2 and -1. Sources: pancake.json of run B-20261115-173904-a7297e3 (runs
B-20261115-165349-81a17bc, -163556-ad5637f, -163653-f6324ea; particle mesh
B-emd-gw-20261115-115239-69ab1db), ellipsoid.json of run B-20261115-174405-af11300 (runs
B-20261115-163613-790095f, -163615-7bc8b30, -163617-085c093).
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402

STEM = "fig_newton"
A_CHECK = (2, 5, 10, 15)
COL = {16: cz.PAL["yellow"], 32: cz.PAL["red"], 64: cz.PAL["blue"]}


def main():
    out = common.out_dir("figures")
    cz.use_style()
    p = common.load_json("nw_pancake", "pancake.json")
    e = common.load_json("nw_ellipsoid", "ellipsoid.json")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(3.4, 5.0))
    fig.subplots_adjust(left=0.20, right=0.965, top=0.985, bottom=0.09, hspace=0.36)

    for n in (16, 32, 64):
        r = p[f"P1_athenak_n{n}"]
        a = np.array([r[f"a_rec_{k}"] for k in A_CHECK])
        meas = np.array([r[f"ex_cont_a{k}"] for k in A_CHECK])
        pred = np.array([r[f"ex_h1_pred_a{k}"] for k in A_CHECK])
        a1.semilogy(a, meas, "o", color=COL[n], ms=4.5, label=f"{n} cells")
        a1.semilogy(a, pred, "-", color=COL[n], lw=1.0)
        if n in (32, 64):
            q = p[f"P1_athenak_minus_pm_n{n}"]
            pm = np.array([q[f"pm_ex_cont_a{k}"] for k in A_CHECK])
            a1.semilogy(a, pm, "s", color=COL[n], ms=4.5, mfc="none")
    leg = a1.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.2)
    a1.add_artist(leg)
    h1, = a1.semilogy([], [], "k-", lw=1.0)
    h2, = a1.semilogy([], [], "ks", ms=4.5, mfc="none")
    a1.legend([h1, h2], ["seven-point force, linear theory", "spectral particle mesh"],
              frameon=False, loc="lower right", fontsize=7, handlelength=1.6)
    a1.set_xlabel(r"scale factor $a$")
    a1.set_ylabel("error over displacement")
    a1.set_xlim(0, 17)
    a1.set_ylim(1e-5, 2e-1)
    a1.text(0.96, 0.95, "(a)", transform=a1.transAxes, ha="right", va="top")

    conv = e["N1_convergence"]
    nn = np.array([32, 64, 128])
    tx = np.array(conv["t_x"]["values"])
    E = np.array(conv["E_raw"]["values"])
    tx0, E0 = conv["t_x_ode_nominal"], conv["E_ode_nominal"]
    a2.loglog(nn, np.abs(tx / tx0 - 1), "o-", color=cz.PAL["blue"], ms=4.5, lw=1.0,
              label="first crossing time")
    a2.loglog(nn, np.abs(E / E0 - 1), "s-", color=cz.PAL["red"], ms=4.5, lw=1.0,
              label="energy to the first crossing")
    x = np.array([28, 145])
    a2.loglog(x, abs(tx[0] / tx0 - 1) * (x / 32.0) ** -2, **cz.GUIDE, label=r"$\propto N^{-2}$, $N^{-1}$")
    a2.loglog(x, abs(E[0] / E0 - 1) * (x / 32.0) ** -1, **cz.GUIDE)
    a2.set_xlabel(r"cells per box side $N$")
    a2.set_ylabel("relative error against the ODE")
    a2.set_xlim(26, 160)
    a2.set_xticks([32, 64, 128])
    a2.set_xticklabels(["32", "64", "128"])
    a2.xaxis.set_minor_formatter(plt.NullFormatter())
    a2.set_ylim(1e-4, 1.5)
    a2.legend(frameon=False, loc="lower left", fontsize=7, handlelength=1.8)
    a2.text(0.96, 0.95, "(b)", transform=a2.transAxes, ha="right", va="top")
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
