#!/usr/bin/env python3
"""Test c0b of the package faces: |M_x| and |H| of the boosted puncture next to an outflow
face after one step, Sommerfeld against the non-wave condition, for the stock and the
fall-off ghost fill.

    analyze_c0b.py <c0b dir> <c0 dir> <a0b dir> [--out results/c0b.json] [--fig figs/c0b]

Prediction (journal entry 7): with nonwave the boundary-cell |M_x| falls below 0.2 of the
Sommerfeld value of the same ghost fill and order.
"""

import argparse
import json
import os

import numpy as np

import flib
from analyze_c0 import one

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("c0bdir")
    p.add_argument("c0dir")
    p.add_argument("a0bdir")
    p.add_argument("--out", default=os.path.join(flib._HERE, "results", "c0b.json"))
    p.add_argument("--fig", default=os.path.join(flib._HERE, "figs", "c0b_boost"))
    a = p.parse_args()
    pairs = {  # label: (Sommerfeld run dir, case), (nonwave run dir, case)
        "stock ghosts, order 2": ((a.a0bdir, "boost_e2"), (a.c0bdir, "boost_e2nw")),
        "falloff ghosts, order 2": ((a.c0dir, "boost_g2"), (a.c0bdir, "boost_g2nw")),
        "falloff ghosts, order 4": ((a.c0dir, "boost_g4"), (a.c0bdir, "boost_g4nw")),
    }
    res = {}
    for lab, ((d1, c1), (d2, c2)) in pairs.items():
        s, n = one(d1, c1), one(d2, c2)
        if s is None or n is None:
            continue
        res[lab] = {"sommerfeld": s, "nonwave": n,
                    "ratio_Mx_cell0": abs(n["con_Mx_line_last6"][0]) /
                    abs(s["con_Mx_line_last6"][0]),
                    "ratio_Mx_layer0max": n["con_Mx_layer_max"][0] / s["con_Mx_layer_max"][0],
                    "ratio_H_cell0": abs(n["con_H_line_last6"][0]) /
                    abs(s["con_H_line_last6"][0])}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    for lab, r in res.items():
        print(lab, "Mx cell0 %.2e -> %.2e (ratio %.3f), layer0 max ratio %.3f, H ratio %.3f" % (
            r["sommerfeld"]["con_Mx_line_last6"][0], r["nonwave"]["con_Mx_line_last6"][0],
            r["ratio_Mx_cell0"], r["ratio_Mx_layer0max"], r["ratio_H_cell0"]))
        for k in ("sommerfeld", "nonwave"):
            print("   ", k, "Mx layers", ["%.2e" % q for q in r[k]["con_Mx_layer_max"]],
                  "H layers", ["%.2e" % q for q in r[k]["con_H_layer_max"]])

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH * 0.75, 2.8))
    fig.subplots_adjust(left=0.11, right=0.985, bottom=0.17, top=0.9, wspace=0.32)
    cols = [fs.PAL["red"], fs.PAL["green"], fs.PAL["blue"]]
    for (lab, r), c in zip(res.items(), cols):
        for i, var in enumerate(("con_Mx", "con_H")):
            for k, ls, mk in (("sommerfeld", "--", "s"), ("nonwave", "-", "o")):
                lay = np.array(r[k][var + "_layer_max"])
                axs[i].semilogy(np.arange(len(lay)), np.maximum(lay, 1e-18), ls, marker=mk,
                                color=c, mfc="none" if k == "sommerfeld" else None,
                                label=f"{lab}, {k}" if i == 0 else None)
    for ax, var in zip(axs, (r"max $|M_x|$", r"max $|H|$")):
        ax.set_xlabel("layer of cells from the face", labelpad=-1)
        ax.set_ylabel(var)
    axs[0].set_title("boosted puncture, one step", fontsize=10)
    axs[0].legend(fontsize=6, loc="lower left")
    fs.save(fig, a.fig)


if __name__ == "__main__":
    main()
