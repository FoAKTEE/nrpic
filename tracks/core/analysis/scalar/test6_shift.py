#!/usr/bin/env python3
"""Test 6 of the scalar field: advective terms.  The plane wave of test 1 on flat
spacetime in coordinates with a uniform shift beta; coordinate frequency omega - k.beta.

Usage: test6_shift.py --exe ATHENA   (run in the output directory)
"""
import argparse
import json
import os

import numpy as np

import common
from common import PROB, mesh_args, run_many
import test1_wave as t1

BETA = (0.3, 0.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    args = ap.parse_args()
    top = os.getcwd()
    omega = np.sqrt(t1.MASS**2 + t1.KVEC @ t1.KVEC)
    kb = t1.KVEC[0]*BETA[0] + t1.KVEC[1]*BETA[1]
    dt = 1.0/512.0
    cases, keys = [], []
    for sgn in (1, -1):
        for n in (8, 16, 32):
            keys.append((sgn, n))
            cases.append((os.path.join(top, f"s{sgn}_n{n}"), t1.INP,
                          mesh_args(n, n, 8) + [f"time/cfl_number={dt*n}", "time/tlim=1.0",
                                                "scalar_field/dump_dt=0.0625",
                                                f"problem/beta1={sgn*BETA[0]}",
                                                f"problem/beta2={sgn*BETA[1]}"]))
    wall = run_many(args.exe, cases, 6)
    res = {"omega": omega, "k_dot_beta": kb, "cases": {}}
    for (sgn, n), (rd, _, _), w in zip(keys, cases, wall):
        t, c = t1.phase_series(rd)
        om = np.polyfit(t, np.unwrap(np.angle(c)), 1)[0]
        target = omega - sgn*kb
        res["cases"][f"s{sgn}_n{n}"] = dict(
            sign=sgn, n=n, omega_meas=float(om), target=float(target),
            rel_err=float(abs(om - target)/omega), amp_loss=float(1.0 - abs(c[-1])),
            wall_s=w)
    for sgn in (1, -1):
        e = [res["cases"][f"s{sgn}_n{n}"]["rel_err"] for n in (8, 16, 32)]
        a = [res["cases"][f"s{sgn}_n{n}"]["amp_loss"] for n in (8, 16, 32)]
        res[f"order_freq_s{sgn}"] = [float(np.log2(e[0]/e[1])), float(np.log2(e[1]/e[2]))]
        res[f"order_amp_s{sgn}"] = [float(np.log2(abs(a[0])/abs(a[1]))),
                                    float(np.log2(abs(a[1])/abs(a[2])))]
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.15, top=0.95, wspace=0.34)
    nn = np.array([8, 16, 32])
    for sgn, col in ((1, fs.PAL["red"]), (-1, fs.PAL["blue"])):
        e = [res["cases"][f"s{sgn}_n{n}"]["rel_err"] for n in nn]
        a = [abs(res["cases"][f"s{sgn}_n{n}"]["amp_loss"]) for n in nn]
        lab = r"$\beta = %s(0.3, 0.2, 0)$" % ("+" if sgn > 0 else "-")
        ax[0].loglog(nn, e, "o-", color=col, ms=5, label=lab)
        ax[1].loglog(nn, a, "o-", color=col, ms=5, label=lab)
    ax[0].loglog(nn, 1e-3*(nn/8.0)**-5, **fs.GUIDE, label=r"$N^{-5}$")
    ax[1].loglog(nn, 1e-3*(nn/8.0)**-5, **fs.GUIDE, label=r"$N^{-5}$")
    for a in ax:
        a.set_xticks(nn)
        a.set_xticks([], minor=True)
        a.set_xticklabels([str(n) for n in nn])
        a.set_xlabel("cells per box side N")
        a.legend(loc="lower left", fontsize=8)
    ax[0].set_ylabel(r"$|\omega_{\rm measured}-(\omega-k\cdot\beta)|/\omega$")
    ax[1].set_ylabel("amplitude loss at t = 1")
    fs.save(fig, os.path.join(top, "fig_wave_shift"))
    plt.close(fig)


if __name__ == "__main__":
    main()
