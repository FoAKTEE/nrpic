#!/usr/bin/env python3
"""(a) Per-particle conservation of E, L_z and Q, evaluated with the exact Kerr metric
on every particle snapshot, for the bound-family runs: analytic vs mesh metric, midpoint
vs Boris pushers.

Figures: figs/invariants_time.{pdf,png}  (median and 99th percentile vs time)
         figs/invariants_hist.{pdf,png}  (distributions at t = 1000 M)
Numbers: results/invariants.json
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt

import ct_common as C
from nrpic import figstyle as fs

SPINS = (0.0, 0.9)
# (run name pattern, species selection for combined analytic files, label, colour)
SERIES = [
    ("ana_a{a}_mid", 2, "analytic, midpoint", fs.PAL["blue"]),
    ("mesh_a{a}_n10000_mid", None, "mesh, midpoint", fs.PAL["red"]),
    ("ana_a{a}_boris", 2, "analytic, Boris", fs.PAL["yellow"]),
    ("mesh_a{a}_n10000_boris", None, "mesh, Boris", fs.PAL["green"]),
    ("ana_a{a}_bchol", 2, "analytic, Boris Cholesky", fs.PAL["orange"]),
]
EXTRA = [("mesh_a{a}_n1000_mid", None), ("mesh_a{a}_n100_mid", None),
         ("ana_a{a}_mid", 0), ("ana_a{a}_mid", 1)]
KEYS = [("E", r"$|\Delta E/E|$"), ("L", r"$|\Delta L_z/L_z|$"), ("Q", r"$|\Delta Q/Q|$")]


def load(name, species):
    h = C.invariant_history(name)
    if species is not None:
        sel = h["species"] == species
        h = {k: (v[..., sel] if (isinstance(v, np.ndarray) and v.ndim >= 1
                                 and v.shape[-1] == len(sel)) else v)
             for k, v in h.items() if k != "x"}
    return h


def stats(h):
    out = {}
    last = np.nonzero(h["alive"].any(1))[0][-1]
    for k, _ in KEYS:
        e = C.rel_err(h, k)
        allv = e[np.isfinite(e)]
        fin = e[last][np.isfinite(e[last])]
        out[k] = dict(median_final=float(np.median(fin)),
                      p90_final=float(np.percentile(fin, 90)),
                      p99_final=float(np.percentile(fin, 99)),
                      max_final=float(fin.max()),
                      max_all=float(allv.max()),
                      median_all=float(np.median(allv)))
    out["n_start"] = int(h["alive"][0].sum())
    out["n_end"] = int(h["alive"][last].sum())
    out["t_end"] = float(h["t"][last])
    rr = h["r"][np.isfinite(h["r"])]
    out["r_min"] = float(rr.min())
    out["r_max"] = float(rr.max())
    return out


def main():
    fs.use_style()
    os.makedirs(C.FIGS, exist_ok=True)
    os.makedirs(os.path.join(C.HERE, "results"), exist_ok=True)
    res = {}

    # ---- time series -------------------------------------------------------------------
    fig, axes = plt.subplots(3, 2, figsize=(8.0, 7.2), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.07, top=0.93, hspace=0.06,
                        wspace=0.22)
    hists = {}
    for j, a in enumerate(SPINS):
        for pat, sp, lab, col in SERIES:
            name = pat.format(a=a)
            if not C.exists(name):
                continue
            h = load(name, sp)
            hists[(a, lab)] = h
            key = name + ("" if sp is None else f"_species{sp}")
            res[key] = stats(h)
            t = h["t"] / C.T_ORB[a]
            for i, (k, _) in enumerate(KEYS):
                e = C.rel_err(h, k)
                with np.errstate(all="ignore"):
                    med = np.nanmedian(e, axis=1)
                    p99 = np.nanpercentile(e, 99, axis=1)
                ax = axes[i, j]
                ax.semilogy(t[1:], med[1:], color=col, ls="-", label=lab if i == 0 else None)
                ax.semilogy(t[1:], p99[1:], color=col, ls="--")
        for pat, sp in EXTRA:
            name = pat.format(a=a)
            if C.exists(name):
                key = name + ("" if sp is None else f"_species{sp}")
                res[key] = stats(load(name, sp))
        axes[0, j].set_title(f"$a = {a}\\,M$")
        axes[-1, j].set_xlabel("$t / T_\\mathrm{orb}$")
    for i, (k, lab) in enumerate(KEYS):
        axes[i, 0].set_ylabel(lab)
    for ax in axes.ravel():
        ax.set_xlim(0, C.TLIM / C.T_ORB[0.9])
    # line-style key
    axes[0, 0].plot([], [], color="k", ls="-", label="median")
    axes[0, 0].plot([], [], color="k", ls="--", label="99th percentile")
    h0, l0 = axes[0, 0].get_legend_handles_labels()
    fig.legend(h0, l0, loc="upper center", ncol=4, fontsize=8, frameon=False,
               bbox_to_anchor=(0.54, 1.0))
    fs.save(fig, os.path.join(C.FIGS, "invariants_time"))
    plt.close(fig)

    # ---- distributions at the final snapshot -------------------------------------------
    fig, axes = plt.subplots(3, 2, figsize=(8.0, 7.2), sharey="row")
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.07, top=0.93, hspace=0.32,
                        wspace=0.06)
    bins = np.linspace(-14, -2, 97)
    for j, a in enumerate(SPINS):
        for pat, sp, lab, col in SERIES:
            if (a, lab) not in hists:
                continue
            h = hists[(a, lab)]
            last = np.nonzero(h["alive"].any(1))[0][-1]
            for i, (k, xl) in enumerate(KEYS):
                e = C.rel_err(h, k)[last]
                e = e[np.isfinite(e)]
                v = np.log10(np.maximum(e, 1e-16))
                axes[i, j].hist(v, bins=bins, histtype="step", color=col, lw=1.5,
                                label=lab if (i == 0) else None)
        axes[0, j].set_title(f"$a = {a}\\,M$, $t = {C.TLIM:.0f}\\,M$")
        for i, (k, xl) in enumerate(KEYS):
            axes[i, j].set_xlabel(r"$\log_{10}$ " + xl, labelpad=-1)
    for i in range(3):
        axes[i, 0].set_ylabel("particles per bin")
    h0, l0 = axes[0, 0].get_legend_handles_labels()
    fig.legend(h0, l0, loc="upper center", ncol=5, fontsize=8, frameon=False,
               bbox_to_anchor=(0.54, 1.0))
    fs.save(fig, os.path.join(C.FIGS, "invariants_hist"))
    plt.close(fig)

    with open(os.path.join(C.HERE, "results", "invariants.json"), "w") as f:
        json.dump(res, f, indent=1)
    for k, v in res.items():
        print(f"{k:32s} n={v['n_start']}->{v['n_end']} r=[{v['r_min']:.2f},{v['r_max']:.1f}] "
              + "  ".join(f"{q}: med {v[q]['median_final']:.1e} p99 {v[q]['p99_final']:.1e} "
                          f"max {v[q]['max_all']:.1e}" for q, _ in KEYS))


if __name__ == "__main__":
    main()
