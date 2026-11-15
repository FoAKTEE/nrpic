#!/usr/bin/env python3
"""T1 of collide/TESTS.md over a run of 1e4 steps.

    python3 t1long.py [--steps 10000] [--exe PATH] [--tag cpu]

twotemp box (theta_1 = 0.3, theta_2 = 0.1), 1e5 particles, 16^3 cells, sigma = 4,
dt = 0.01 (~1e3 collisions per step, ~1e7 in the run), seeds (1, 1) and (2, 2), snapshots
every 1000 steps. Criteria (TESTS.md, fixed in wave 1): per step |dE|/sum_MW and
|dP_i|/sum_MW below 1e-14 sqrt(n_coll + 1); relative drift of sum M W over the run below
1e-11; n_trunc = 0. sum M W is taken from the exactly rounded sums of the snapshots and
from coll.hst sum_MW (nrpic.hst sum_mW is 0 without deposit, JOURNAL S0).
"""
import argparse
import os
import sys

import numpy as np

import boxlib as bl

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    out = bl.outdir()
    dt, sig = 0.01, 4.0
    jobs = []
    for seed in (1, 2):
        rd = os.path.join(out, f"T1long_s{seed}")
        bl.make_box(rd, "twotemp", n=100000, theta=0.3, sigma=sig, seed=seed)
        jobs.append((rd, bl.mesh_overrides(16) + [
            f"particles/dt={dt!r}", f"time/nlim={a.steps}", f"particles/coll_sigma={sig!r}",
            f"particles/snap_dt={1000 * dt * (1 - 1e-9)!r}", f"job/rng_seed={seed}",
            "particles/hist_dcycle=100"], dict(exe=a.exe)))
    rr = bl.run_many(jobs, 2)
    res = {}
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax1 = fig.add_axes([0.08, 0.15, 0.40, 0.78])
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    for (rd, _, _), r0 in zip(jobs, rr):
        name = os.path.basename(rd)
        if r0["rc"]:
            res[name] = dict(rc=r0["rc"], failed=True)
            continue
        h = bl.coll_history(rd)
        files = bl.snapshots(rd)
        E, P, cyc = [], [], []
        for f in files:
            s = bl.snap.read_snapshot(f)
            E.append(bl.fsum_cols((s["m"] * bl.W(s["u"]))[:, None])[0])
            P.append(bl.fsum_cols(s["m"][:, None] * s["u"]))
            cyc.append(s["cycle"])
        E, P = np.array(E), np.array(P)
        smw = h["sum_MW"]
        nc = h["n_coll"]
        bound = 1e-14 * np.sqrt(nc + 1)
        relE = np.abs(h["dE"]) / smw
        relP = np.max(np.abs(np.stack([h["dP1"], h["dP2"], h["dP3"]])), 0) / smw
        r = dict(rc=0, wall=r0["wall"], steps=int(h["ncycle"][-1]), collisions=float(nc.sum()),
                 n_trunc=float(h["n_trunc"].sum()), max_nsub=float(h["max_nsub"].max()),
                 max_P=float(h["max_P"].max()), n_snap=len(files), snap_cycles=cyc,
                 exact_drift_max=float(np.max(np.abs(E / E[0] - 1))),
                 exact_dP_max=float(np.max(np.abs(P - P[0])) / E[0]),
                 hst_drift_max=float(np.max(np.abs(smw / smw[0] - 1))),
                 T1_max_relE=float(relE.max()), T1_max_relP=float(relP.max()),
                 T1_max_over_bound=float(max((relE / bound).max(), (relP / bound).max())))
        r["pass"] = bool(r["exact_drift_max"] < 1e-11 and r["hst_drift_max"] < 1e-11 and
                         r["T1_max_over_bound"] < 1 and r["n_trunc"] == 0 and
                         r["steps"] == a.steps)
        res[name] = r
        ls = "-" if name.endswith("1") else "--"
        ax1.plot(h["ncycle"], smw / smw[0] - 1, ls=ls, color=fs.PAL["red"], lw=0.8,
                 label=f"coll.hst sum_MW, {name}")
        ax1.plot(np.array(cyc), E / E[0] - 1, "o", color=fs.PAL["blue"], ms=3,
                 mfc="none" if ls == "--" else fs.PAL["blue"], label=f"exact sum, {name}")
        ax2.semilogy(h["ncycle"], np.maximum(relE, 1e-30), ls=ls, color=fs.PAL["red"], lw=0.5,
                     label=f"|dE|/sum_MW, {name}")
        ax2.semilogy(h["ncycle"], bound, ls=":", color="k", lw=0.8)
    ax1.axhspan(-1e-11, 1e-11, color="grey", alpha=0.15)
    ym = max([2e-14] + [1.5 * max(v["exact_drift_max"], v["hst_drift_max"])
                        for v in res.values() if not v.get("failed")])
    ax1.set_ylim(-ym, ym)
    ax1.set_xlabel("step"); ax1.set_ylabel(r"$\Sigma MW/\Sigma MW(0) - 1$")
    ax1.legend(loc="lower left", fontsize=7)
    ax2.set_ylim(1e-22, 1e-10)
    ax2.set_xlabel("step"); ax2.set_ylabel(r"per step (dotted: $10^{-14}\sqrt{n+1}$)")
    ax2.legend(loc="center right", fontsize=7)
    fs.save(fig, os.path.join(out, f"t1_long_{a.tag}"))
    plt.close(fig)
    res["pass"] = bool(all(v.get("pass") for v in res.values()))
    bl.save_json(os.path.join(out, f"t1long_{a.tag}.json"), res)
    import json
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    sys.exit(main())
