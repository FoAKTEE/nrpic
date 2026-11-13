#!/usr/bin/env python3
"""Where the mesh-metric invariant errors come from: per-particle |dE/E| and |dL_z/L_z| at
t = 1000 M versus the smallest Kerr-Schild radius the particle reached, for the analytic
metric, the production mesh (dx = 0.25 M around the cluster, 0.125 M inside |x_i| < 4 M)
and the same mesh with every dx doubled (a = 0.9 M, N = 1e4, midpoint).  Binned medians
and the ratio coarse/production give the convergence order of the mesh-metric error.

Figure: figs/mesh_resolution.{pdf,png}
Numbers: results/mesh_resolution.json
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt

import ct_common as C
from nrpic import figstyle as fs

A = 0.9
SERIES = [("ana_a0.9_mid", 2, "analytic", fs.PAL["blue"]),
          ("mesh_a0.9_n10000_mid", None, r"mesh, $\Delta x$", fs.PAL["red"]),
          ("mesh_a0.9_n10000_mid_dx2", None, r"mesh, $2\Delta x$", fs.PAL["yellow"])]
EDGES = np.array([2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.5])


def per_particle(name, sp):
    h = C.invariant_history(name)
    sel = np.ones(len(h["tag"]), bool) if sp is None else (h["species"] == sp)
    last = np.nonzero(h["alive"].any(1))[0][-1]
    eE = np.abs(h["E"][last, sel] / h["E0"][sel] - 1)
    eL = np.abs(h["L"][last, sel] / h["L0"][sel] - 1)
    rmin = np.nanmin(h["r"][:, sel], 0)
    tag = h["tag"][sel] - (1100 if sp == 2 else 0)
    return dict(eE=eE, eL=eL, rmin=rmin, tag=tag)


def binned_median(x, y):
    k = np.digitize(x, EDGES) - 1
    med = np.full(len(EDGES) - 1, np.nan)
    for i in range(len(EDGES) - 1):
        v = y[(k == i) & np.isfinite(y)]
        if len(v) >= 5:
            med[i] = np.median(v)
    return med


def main():
    fs.use_style()
    data = {}
    for name, sp, lab, col in SERIES:
        if C.exists(name):
            data[name] = per_particle(name, sp)
    if "mesh_a0.9_n10000_mid" not in data:
        return
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.86, wspace=0.25)
    xc = 0.5 * (EDGES[1:] + EDGES[:-1])
    res = {"edges": EDGES.tolist()}
    for j, (key, ylab) in enumerate((("eE", r"$|\Delta E/E|$ at $t = 1000\,M$"),
                                     ("eL", r"$|\Delta L_z/L_z|$ at $t = 1000\,M$"))):
        ax = axes[j]
        for name, sp, lab, col in SERIES:
            if name not in data:
                continue
            d = data[name]
            ax.scatter(d["rmin"], np.maximum(d[key], 1e-16), s=0.6, lw=0, color=col,
                       alpha=0.5, rasterized=True)
            med = binned_median(d["rmin"], d[key])
            ax.semilogy(xc, med, color=col, marker="o", ms=3, label=lab)
            res.setdefault(name, {})[key + "_median"] = med.tolist()
        ax.set_yscale("log")
        ax.set_xlabel(r"smallest Kerr-Schild radius reached, $r_\mathrm{min}/M$")
        ax.set_ylabel(ylab)
        ax.axvline(4.0, **fs.MASK_LINE)
        ax.set_xlim(2.5, 11)
    if "mesh_a0.9_n10000_mid_dx2" in data:
        for key in ("eE", "eL"):
            f = np.array(res["mesh_a0.9_n10000_mid"][key + "_median"])
            c = np.array(res["mesh_a0.9_n10000_mid_dx2"][key + "_median"])
            res["order_" + key] = (np.log2(c / f)).tolist()
            # per particle (same tags in both runs)
            df, dcs = data["mesh_a0.9_n10000_mid"], data["mesh_a0.9_n10000_mid_dx2"]
            o = np.argsort(dcs["tag"])
            ratio = dcs[key][o][np.searchsorted(dcs["tag"][o], df["tag"])] / df[key]
            res["order_" + key + "_per_particle_median"] = float(np.nanmedian(np.log2(ratio)))
            res["median_all_" + key] = [float(np.nanmedian(df[key])),
                                        float(np.nanmedian(dcs[key]))]
    res["median_all_analytic_eE"] = (float(np.nanmedian(data["ana_a0.9_mid"]["eE"]))
                                     if "ana_a0.9_mid" in data else None)
    h0, l0 = axes[0].get_legend_handles_labels()
    fig.legend(h0, l0, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.54, 1.0))
    fs.save(fig, os.path.join(C.FIGS, "mesh_resolution"))
    plt.close(fig)
    with open(os.path.join(C.HERE, "results", "mesh_resolution.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items()}, indent=None)[:3000])


if __name__ == "__main__":
    main()
