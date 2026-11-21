#!/usr/bin/env python3
"""Test c0 of the package faces: the constraint monitor next to an outflow face after one
step, the fall-off ghost fill (plan c0_step1) against the stock fill (plan a0b_step1).

    analyze_c0.py <run directory of c0> <run directory of a0b> [--out results/c0.json]
                  [--fig figs/c0_monitor]

Per case and order: the largest |H| and |M_x| per layer of cells from the faces (layer 0
is the boundary cell), and the values on the line nearest the +x axis.  Prediction of
the journal (entry 6): the falloff fill lowers the boundary-cell |H| of the vacuum
puncture by 1.25 m/r (1 - 3m/r)/(1 - 3.75 m/r) = 0.086 at r = 15.5 at every order, and
|M_x| of the boosted puncture by 1/3.
"""

import argparse
import json
import os

import numpy as np

import flib
from analyze_a0 import layers

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def one(rundir, case):
    f = flib.dumps(os.path.join(rundir, case), "con")
    if not f:
        return None
    d = flib.Dump(f[-1])
    r = {"time": d.time}
    for var in ("con_H", "con_Mx"):
        xl, vl, hl = flib.axis_line(d, var)
        r[var + "_line_last6"] = [float(q) for q in vl[-6:][::-1]]
        lay, deep = layers(d, var)
        r[var + "_layer_max"] = lay
        r[var + "_deep_max"] = deep
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("c0dir")
    p.add_argument("a0bdir")
    p.add_argument("--out", default=os.path.join(flib._HERE, "results", "c0.json"))
    p.add_argument("--fig", default=os.path.join(flib._HERE, "figs", "c0_monitor"))
    a = p.parse_args()
    res = {"stock": {}, "falloff": {}}
    for fam in ("punc", "boost"):
        for o in ("2", "4"):
            s = one(a.a0bdir, f"{fam}_e{o}")
            g = one(a.c0dir, f"{fam}_g{o}")
            if s is not None:
                res["stock"][f"{fam}_{o}"] = s
            if g is not None:
                res["falloff"][f"{fam}_{o}"] = g
    m, r = 1.0, 15.5
    res["prediction"] = {"H_ratio": 1.25 * m / r * (1 - 3 * m / r) / (1 - 3.75 * m / r),
                         "Mx_ratio_boost": 1.0 / 3.0}
    ratios = {}
    for k in res["falloff"]:
        if k in res["stock"]:
            for var in ("con_H", "con_Mx"):
                ratios[f"{k}.{var}.cell0"] = (abs(res["falloff"][k][var + "_line_last6"][0]) /
                                             abs(res["stock"][k][var + "_line_last6"][0]))
                ratios[f"{k}.{var}.layer0max"] = (res["falloff"][k][var + "_layer_max"][0] /
                                                 res["stock"][k][var + "_layer_max"][0])
    res["ratios"] = ratios
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH * 0.75, 4.8), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.985, bottom=0.1, top=0.93, wspace=0.3,
                        hspace=0.08)
    col = {"2": fs.PAL["red"], "4": fs.PAL["blue"]}
    for j, fam in enumerate(("punc", "boost")):
        for i, var in enumerate(("con_H", "con_Mx")):
            ax = axs[i, j]
            for o in ("2", "4"):
                k = f"{fam}_{o}"
                for kind, ls, mk in (("stock", "--", "s"), ("falloff", "-", "o")):
                    if k not in res[kind]:
                        continue
                    lay = np.array(res[kind][k][var + "_layer_max"])
                    ax.semilogy(np.arange(len(lay)), np.maximum(lay, 1e-18), ls,
                                marker=mk, color=col[o], mfc="none" if kind == "stock" else None,
                                label=f"order {o}, {kind}")
                if var == "con_H" and fam == "punc" and k in res["stock"]:
                    y0 = res["stock"][k][var + "_layer_max"][0] * res["prediction"]["H_ratio"]
                    ax.plot([0], [y0], "k*", ms=8, label="prediction" if o == "2" else None)
            if i == 0:
                ax.set_title({"punc": "vacuum puncture", "boost": "boosted puncture"}[fam] +
                             ", one step", fontsize=10)
            else:
                ax.set_xlabel("layer of cells from the face", labelpad=-2)
            if j == 0:
                ax.set_ylabel({"con_H": r"max $|H|$", "con_Mx": r"max $|M_x|$"}[var])
    axs[0, 0].legend(fontsize=7)
    fs.save(fig, a.fig)
    print(json.dumps(ratios, indent=1))


if __name__ == "__main__":
    main()
