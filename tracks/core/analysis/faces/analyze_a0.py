#!/usr/bin/env python3
"""Test a0 of the package faces: the constraint monitor at t = 0 next to an outflow face
for the extrapolation orders 2, 3, 4 of the ghost cells.

    analyze_a0.py <run directory of plan a0_t0> [--out results/a0.json] [--fig figs/a0_monitor]

Per case: |H| and |M_x| along the line nearest the x axis in the last cells before the
+x face (layer 0 is the boundary cell), their largest value per layer of cells over
the whole mesh, and the largest difference between orders four cells or more from every
face.  Stencil prediction of the journal (entry 1): boundary-cell error of the second
derivative -1.117 f'' (order 2), 1.011 f''' dx (order 3), 0.917 f'''' dx^2 (order 4).
"""

import argparse
import json
import os

import numpy as np

import flib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def layers(d, var, nlay=6):
    x, y, z, dv, v = d.flat(var)
    h = dv ** (1.0 / 3.0)
    dface = d.L - np.maximum(np.maximum(np.abs(x), np.abs(y)), np.abs(z))
    lay = np.floor(dface / h + 1e-9).astype(int)
    out = []
    for n in range(nlay):
        m = lay == n
        out.append(float(np.abs(v[m]).max()) if m.any() else float("nan"))
    m = lay >= 4
    return out, float(np.abs(v[m]).max())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("rundir")
    p.add_argument("--out", default=os.path.join(flib._HERE, "results", "a0.json"))
    p.add_argument("--fig", default=os.path.join(flib._HERE, "figs", "a0_monitor"))
    a = p.parse_args()
    cases = ["ball_e2", "ball_e3", "ball_e4", "ball64_e2", "ball64_e4",
             "punc_e2", "punc_e3", "punc_e4", "boost_e2", "boost_e3", "boost_e4"]
    res = {}
    dumps = {}
    for c in cases:
        f = flib.dumps(os.path.join(a.rundir, c), "con")
        if not f:
            continue
        d = flib.Dump(f[0])
        dumps[c] = d
        r = {}
        for var in ("con_H", "con_Mx"):
            xl, vl, hl = flib.axis_line(d, var)
            r[var + "_line_last6"] = [float(q) for q in vl[-6:][::-1]]
            r[var + "_line_x_last6"] = [float(q) for q in xl[-6:][::-1]]
            lay, deep = layers(d, var)
            r[var + "_layer_max"] = lay
            r[var + "_deep_max"] = deep
        res[c] = r
    # differences between orders four or more cells from every face
    for fam in ("ball", "punc", "boost"):
        if fam + "_e2" not in dumps:
            continue
        for o in ("e3", "e4"):
            x, y, z, dv, va, vb = flib.difference(dumps[fam + "_e2"], dumps[fam + "_" + o],
                                                  "con_H")
            h = dv ** (1.0 / 3.0)
            L = dumps[fam + "_e2"].L
            dface = L - np.maximum(np.maximum(np.abs(x), np.abs(y)), np.abs(z))
            m = np.floor(dface / h + 1e-9) >= 4
            res[f"{fam}_e2_minus_{o}_deep_max"] = float(np.abs(va - vb)[m].max())
    # stencil prediction for the puncture at the face centre (journal entry 1)
    r_b = 15.5
    res["prediction"] = {"punc_e2_boundary_cell_H": 8 * 1.117 / r_b ** 3,
                         "ratio_e3": 1.011 * 3 / r_b / 1.117,
                         "ratio_e4": 0.917 * 12 / r_b ** 2 / 1.117,
                         "layer1_over_layer0": 0.117 / 1.117,
                         "layer2_over_layer0": 0.011 / 1.117}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.085, top=0.94, wspace=0.28,
                        hspace=0.08)
    col = {"e2": fs.PAL["red"], "e3": fs.PAL["yellow"], "e4": fs.PAL["blue"]}
    for j, fam in enumerate(("ball", "punc", "boost")):
        for i, var in enumerate(("con_H", "con_Mx")):
            ax = axs[i, j]
            for o in ("e2", "e3", "e4"):
                c = f"{fam}_{o}"
                if c not in res:
                    continue
                lay = np.array(res[c][var + "_layer_max"])
                ax.semilogy(np.arange(len(lay)), np.maximum(lay, 1e-18), "o-",
                            color=col[o], label=f"order {o[1]}")
            if fam == "ball" and "ball64_e2" in res:
                lay = np.array(res["ball64_e2"][var + "_layer_max"])
                ax.semilogy(np.arange(len(lay)), np.maximum(lay, 1e-18), "s--",
                            color=col["e2"], mfc="none", label="order 2, cells 1/2")
            if fam == "punc" and var == "con_H":
                pr = res["prediction"]
                y0 = pr["punc_e2_boundary_cell_H"]
                ax.semilogy([0, 1, 2], [y0, y0 * pr["layer1_over_layer0"],
                                        y0 * pr["layer2_over_layer0"]], "k--", lw=1.0,
                            label="stencil, order 2")
            if i == 0:
                ax.set_title({"ball": "expanding ball", "punc": "vacuum puncture",
                              "boost": "boosted puncture"}[fam])
            else:
                ax.set_xlabel("layer of cells from the face", labelpad=-2)
            if j == 0:
                ax.set_ylabel({"con_H": r"max $|H|$ at $t=0$",
                               "con_Mx": r"max $|M_x|$ at $t=0$"}[var])
            if i == 0 and j == 1:
                ax.legend(fontsize=8)
            if i == 0 and j == 0:
                ax.legend(fontsize=8)
    fs.save(fig, a.fig)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
