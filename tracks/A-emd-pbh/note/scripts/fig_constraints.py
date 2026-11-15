"""Constraint residuals of the expanding-ball initial data against mesh spacing (note v0).

Reads only registered outputs of expball's G1 test (offline finite differences of the
Hamiltonian H and momentum M constraints on octant meshes of N^3 cells over [0, L]^3):
  run A-emd-pbh-20261115-130402-f5566fb (lead's rerun), convergence.json, N = 32-256;
  run A-emd-pbh-20261115-122117-aa1c84d, convergence.json, smoothed top hat to N = 512.
L2 norms with fourth-order differences ("4"); region "smooth" leaves out cells closer than
0.1 R_b to a radius where the data are not smooth, "all" keeps every cell.
The flat ball has H = 0 identically (rounding level), so it appears in the M panel only.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from czstyle import use_style, save, PAL  # noqa: E402
import common  # noqa: E402

STEM = "fig_constraints"
CURVES = [  # (model, region, label, colour, marker)
    ("smooth_tophat", "smooth", "smoothed top hat", PAL["blue"], "o"),
    ("tophat", "smooth", "top hat, smooth cells", PAL["green"], "s"),
    ("flat_taper", "all", "flat ball, tapered edge", PAL["orange"], "^"),
    ("tophat", "all", "top hat, all cells", "0.5", "x"),
]


def series(models, models512, model, region, q):
    m = models[model]
    N = [int(n) for n in m["N"]]
    h = list(m["h"])
    y = [m["norms"][str(n)]["4"][region][q] for n in N]
    if model in models512:
        m5 = models512[model]
        for n, hh in zip(m5["N"], m5["h"]):
            if int(n) in N:      # the two runs agree on their common meshes
                a = m["norms"][str(n)]["4"][region][q]
                b = m5["norms"][str(n)]["4"][region][q]
                assert abs(a - b) <= 1e-12 * max(abs(a), 1e-300), (model, n, a, b)
            else:
                N.append(int(n))
                h.append(hh)
                y.append(m5["norms"][str(n)]["4"][region][q])
    return np.array(N), np.array(h), np.array(y)


def main():
    out = common.out_dir("figures")
    models = common.load_json("convergence", "convergence.json")["models"]
    models512 = common.load_json("convergence512", "convergence.json")["models"]

    use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.6), sharex=True)
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.18, top=0.95, wspace=0.30)
    orders = {}
    for ax, q, name in ((axs[0], "H_L2", r"$\|\mathcal{H}\|_2$"), (axs[1], "M_L2", r"$\|\mathcal{M}\|_2$")):
        for model, region, lab, col, mk in CURVES:
            if model.startswith("flat") and q.startswith("H"):
                continue
            N, h, y = series(models, models512, model, region, q)
            ax.plot(h, y, color=col, marker=mk, ms=4, label=lab)
            orders[f"{model}/{region}/{q}"] = list(np.log2(y[:-1] / y[1:]))
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(r"cell spacing $h/M$")
        ax.set_ylabel(name)
    # slope guides through the smoothed top hat
    for ax, q in ((axs[0], "H_L2"), (axs[1], "M_L2")):
        N, h, y = series(models, models512, "smooth_tophat", "smooth", q)
        g = np.array([0.1, h.max()])
        ax.plot(g, 0.3 * y[0] * (g / h[0]) ** 4, color="k", lw=1.0, ls="--")
        ax.plot(g, 3.0 * y[0] * (g / h[0]) ** 2, color="k", lw=1.0, ls=":")
    axs[0].text(0.05, 0.92, r"(a) dashed $h^4$, dotted $h^2$", transform=axs[0].transAxes, fontsize=8.5)
    axs[1].text(0.05, 0.92, "(b)", transform=axs[1].transAxes, fontsize=8.5)
    axs[1].legend(loc="upper left", bbox_to_anchor=(0.0, 0.89), fontsize=7, handlelength=1.2)
    save(fig, os.path.join(out, STEM))
    plt.close(fig)
    common.report_checks(STEM)
    for k, v in orders.items():
        print(f"{STEM}: order {k}: " + ", ".join(f"{x:.2f}" for x in v))


if __name__ == "__main__":
    main()
