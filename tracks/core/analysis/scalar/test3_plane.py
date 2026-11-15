#!/usr/bin/env python3
"""Test 3 of the scalar field: a plane perturbation started from data that satisfy the
constraints, convergence of the constraints with resolution (JOURNAL-scalar.md, P3).

Meshes N x N x 8 with N = 16, 32, 64, Courant factor 0.25, to t = 0.5; control runs
(Pi = pi0 everywhere, momentum constraint violated at first order) with N = 16, 32.

Usage: test3_plane.py --exe ATHENA   (run in the output directory)
"""
import argparse
import json
import os

import numpy as np

import common
from common import PROB, mesh_args, run_many
from nrpic import scalar_field as sfr

INP = os.path.join(PROB, "plane.athinput")
NS = [16, 32, 64]
TIMES = [0.0, 0.125, 0.25, 0.375, 0.5]


def at_times(h, key):
    return np.array([h[key][np.argmin(np.abs(h["time"] - t))] for t in TIMES])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    top = os.getcwd()
    cases, keys = [], []
    for n in NS:
        keys.append(("data", n))
        cases.append((os.path.join(top, f"n{n}"), INP,
                      mesh_args(n, n, 8) + [f"mesh/x3max={8.0/n!r}"]))
    for n in NS[:2]:
        keys.append(("control", n))
        cases.append((os.path.join(top, f"control_n{n}"), INP,
                      mesh_args(n, n, 8) + [f"mesh/x3max={8.0/n!r}", "problem/control=true"]))
    wall = run_many(args.exe, cases, args.workers)
    hist = {k: sfr.read_history(os.path.join(c[0], "pl.sf.hst")) for k, c in zip(keys, cases)}
    summary = {"exe": os.path.abspath(args.exe), "times": TIMES, "cases": {}}
    for k, w in zip(keys, wall):
        h = hist[k]
        summary["cases"][f"{k[0]}_n{k[1]}"] = dict(
            H_rms=at_times(h, "H_rms").tolist(), H_max=at_times(h, "H_max").tolist(),
            M_rms=at_times(h, "M_rms").tolist(), M_max=at_times(h, "M_max").tolist(),
            H_norm=at_times(h, "H_norm").tolist(), rms_phi=at_times(h, "rms_phi").tolist(),
            K=at_times(h, "K").tolist(), steps=int(h["cycle"][-1]), wall_s=w)
    for q in ("H_rms", "M_rms", "H_max", "M_max"):
        v = np.array([summary["cases"][f"data_n{n}"][q] for n in NS])
        summary[f"order_{q}"] = dict(n16_32=np.log2(v[0]/v[1]).tolist(),
                                     n32_64=np.log2(v[1]/v[2]).tolist())
        vc = np.array([summary["cases"][f"control_n{n}"][q] for n in NS[:2]])
        summary[f"control_order_{q}"] = np.log2(vc[0]/vc[1]).tolist()
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    cols = {16: fs.PAL["yellow"], 32: fs.PAL["red"], 64: fs.PAL["blue"]}
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.14, top=0.95, wspace=0.28)
    for n in NS:
        h = hist[("data", n)]
        ax[0].semilogy(h["time"], h["H_rms"]/h["H_norm"], color=cols[n], label=f"N = {n}")
        ax[1].semilogy(h["time"], h["M_rms"], color=cols[n], label=f"N = {n}")
    for n in NS[:2]:
        h = hist[("control", n)]
        ax[1].semilogy(h["time"], h["M_rms"], color=cols[n], ls=":",
                       label=f"control, N = {n}")
        ax[0].semilogy(h["time"], h["H_rms"]/h["H_norm"], color=cols[n], ls=":")
    ax[0].set_xlabel("conformal time")
    ax[0].set_ylabel(r"rms $H$ / $\langle[H]\rangle$")
    ax[0].legend(loc="lower right")
    ax[1].set_xlabel("conformal time")
    ax[1].set_ylabel(r"rms $|M|$")
    ax[1].legend(loc="lower center", fontsize=7, ncol=2)
    fs.save(fig, os.path.join(top, "fig_plane_constraints"))
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.14, top=0.95, wspace=0.28)
    nn = np.array(NS, dtype=float)
    for ti, t in enumerate(TIMES[::2]):
        i = 2*ti
        hv = np.array([summary["cases"][f"data_n{n}"]["H_rms"][i] for n in NS])
        mv = np.array([summary["cases"][f"data_n{n}"]["M_rms"][i] for n in NS])
        ax[0].loglog(nn, hv, "o-", color=fs.SERIES[ti], ms=5, label=f"t = {t}")
        ax[1].loglog(nn, mv, "o-", color=fs.SERIES[ti], ms=5, label=f"t = {t}")
    for a, v0 in ((ax[0], summary["cases"]["data_n16"]["H_rms"][0]),
                  (ax[1], summary["cases"]["data_n16"]["M_rms"][0])):
        a.loglog(nn, v0*(nn/16.0)**-6, **fs.GUIDE, label=r"$N^{-6}$")
        a.loglog(nn, v0*(nn/16.0)**-4, color="k", lw=1.0, ls=":", label=r"$N^{-4}$")
        a.set_xticks(NS)
        a.set_xticks([], minor=True)
        a.set_xticklabels([str(n) for n in NS])
        a.set_xlabel("cells per box side N")
        a.legend(loc="lower left", fontsize=8)
    ax[0].set_ylabel(r"rms $H$")
    ax[1].set_ylabel(r"rms $|M|$")
    fs.save(fig, os.path.join(top, "fig_plane_convergence"))
    plt.close(fig)


if __name__ == "__main__":
    main()
