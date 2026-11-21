#!/usr/bin/env python3
"""Horizon proxy of the package faces (tests b2, c3): apparent-horizon mass of the vacuum
puncture with the outflow faces at 16 M (inputs/punc_h*.athinput), stock conditions
against the new options.

    analyze_proxy.py --stock <dir> --case name=<dir> [--case ...]
                     [--out results/proxy.json] [--fig figs/proxy]

Each directory holds punc.horizon_summary_0.txt (columns 1:iter 2:time 3:mass ...).
Measures (journal entries 4 and 6): the largest |M - M_stock| for t <= 11 (nothing from
the faces has reached the hole); the largest excursion of M from its value at t = 12
over 12 <= t <= 40, for every run, and its ratio to the stock one.
"""

import argparse
import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import flib  # noqa: F401,E402  (puts python/ on the path)
from nrpic import figstyle as fs  # noqa: E402


def load(d):
    a = np.loadtxt(os.path.join(d, "punc.horizon_summary_0.txt"), comments="#")
    t, m = a[:, 1], a[:, 2]
    k = np.isfinite(m)
    t, m = t[k], m[k]
    _, idx = np.unique(t, return_index=True)
    return t[idx], m[idx]


def excursion(t, m):
    k12 = int(np.argmin(np.abs(t - 12.0)))
    q = (t >= 12.0) & (t <= 40.0)
    return float(np.abs(m[q] - m[k12]).max()), float(t[q].max())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stock", required=True)
    p.add_argument("--case", action="append", default=[])
    p.add_argument("--out", default=os.path.join(flib._HERE, "results", "proxy.json"))
    p.add_argument("--fig", default=os.path.join(flib._HERE, "figs", "proxy"))
    a = p.parse_args()
    ts, ms = load(a.stock)
    exs, tend = excursion(ts, ms)
    res = {"stock": {"excursion_12_40": exs, "t_end": tend, "M_12": float(ms[np.argmin(np.abs(ts - 12.0))]),
                     "M_end": float(ms[-1])}}
    runs = {}
    for c in a.case:
        n, d = c.split("=", 1)
        t, m = load(d)
        runs[n] = (t, m)
        ex, te = excursion(t, m)
        common = np.intersect1d(np.round(t, 6), np.round(ts, 6))
        dm = np.array([m[np.argmin(np.abs(t - q))] - ms[np.argmin(np.abs(ts - q))]
                       for q in common])
        res[n] = {"excursion_12_40": ex, "t_end": te, "ratio_to_stock": ex / exs,
                  "max_dM_t_le_11": float(np.abs(dm[common <= 11.0]).max()),
                  "max_dM_t_le_20": float(np.abs(dm[common <= 20.0]).max()),
                  "max_dM_all": float(np.abs(dm).max()),
                  "dM_end": float(dm[-1]), "M_end": float(m[-1]),
                  "t": [float(q) for q in common], "dM": [float(q) for q in dm]}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    for n, r in res.items():
        print(n, {k: v for k, v in r.items() if k not in ("t", "dM")})

    fs.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH * 0.7, 4.6), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.1, top=0.97, hspace=0.06)
    cols = [fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"]]
    axs[0].plot(ts, ms - 1.0, color=fs.PAL["red"], lw=1.2, label="stock (linear ghosts, Sommerfeld)")
    for (n, (t, m)), c in zip(runs.items(), cols):
        axs[0].plot(t, m - 1.0, color=c, lw=1.2, ls="--", label=n)
        axs[1].semilogy(res[n]["t"], np.maximum(np.abs(res[n]["dM"]), 1e-12), color=c, lw=1.2,
                        label=n)
    axs[1].axvline(11.0, color="0.6", lw=0.8)
    axs[0].set_ylabel(r"$M_{\rm AH}/m - 1$")
    axs[0].legend(fontsize=8, loc="lower left")
    axs[1].set_ylabel(r"$|M_{\rm AH} - M_{\rm AH}^{\rm stock}|$")
    axs[1].set_xlabel(r"$t/m$")
    fs.save(fig, a.fig)


if __name__ == "__main__":
    main()
