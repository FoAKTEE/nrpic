#!/usr/bin/env python3
"""Zoom on the T4 window of the T3-T5 runs: theta_1 - theta_2 over [0, 0.25 tau_rel]
with the exact initial slope and the quadratic fit over [0, 0.15 tau_rel] (the fit of
collide/analysis/an_box.py relax, repeated here only to draw it).

    python3 t4zoom.py T345_RUN_DIR [--tag cpu]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

import boxlib as bl
import mj

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def theta_of(u):
    return float(mj.theta_from_kinetic(float(bl.snap.kinetic_flat(u).mean())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    out = bl.outdir()
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    axes = {"0.001": fig.add_axes([0.08, 0.15, 0.38, 0.78]),
            "1.0": fig.add_axes([0.59, 0.15, 0.38, 0.78])}
    summ = {}
    for adir in sorted(glob.glob(os.path.join(a.rundir, "T345_th*_A"))):
        base = os.path.basename(adir)[:-2]
        th2 = base.split("_")[1][2:]
        seed = int(base[-1])
        res = json.load(open(os.path.join(a.rundir, "analysis", f"relax_{base}.json")))
        meta = json.load(open(os.path.join(a.rundir, base + "_ic", "box.json")))
        n1 = meta["n_pop1"]
        t, D = [], []
        for f in bl.snapshots(adir):
            s = bl.snap.read_snapshot(f)
            p = s["tag"] < n1
            t.append(s["time"]); D.append(theta_of(s["u"][p]) - theta_of(s["u"][~p]))
        t, D = np.array(t), np.array(D)
        tau = res["tau_rel"]
        w = t <= 0.15 * tau * (1 + 1e-9)
        A = np.vstack([np.ones(w.sum()), t[w], t[w] ** 2]).T
        coef = np.linalg.lstsq(A, D[w], rcond=None)[0]
        ax = axes[th2]
        c = fs.PAL["red"] if seed == 1 else fs.PAL["yellow"]
        x = t / tau
        ax.plot(x, D / D[0], "o", ms=3, color=c, label=f"seed {seed}: ratio {res['T4_ratio']:.4f}")
        xx = np.linspace(0, 0.15, 50)
        ax.plot(xx, (coef[0] + coef[1] * xx * tau + coef[2] * (xx * tau) ** 2) / D[0],
                color=c, lw=1.0)
        ax.plot(xx, 1 + res["slope_exact"] * xx * tau / D[0], **fs.GUIDE)
        summ[base] = dict(ratio=res["T4_ratio"], se_rel=res["T4_slope_se"] / abs(res["slope_exact"]),
                          fit_coef=coef.tolist())
    for th2, ax in axes.items():
        ax.axvspan(0, 0.15, color="grey", alpha=0.08)
        ax.set_xlabel(r"$t/\tau_{\rm rel}$")
        ax.set_ylabel(r"$(\theta_1-\theta_2)/(\theta_1-\theta_2)_0$")
        ax.set_title(rf"$\theta_2={th2}$ (dashed: exact initial slope)", fontsize=9)
        ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(out, f"t4_zoom_{a.tag}"))
    plt.close(fig)
    bl.save_json(os.path.join(out, f"t4zoom_{a.tag}.json"), summ)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    sys.exit(main())
