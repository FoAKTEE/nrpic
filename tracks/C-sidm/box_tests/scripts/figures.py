#!/usr/bin/env python3
"""Final figure of T1/T2 from the processor run directory (cleaner layout than the
figures written during the run; same numbers, recomputed by t1t2.analyse).

    python3 figures.py T2_RUN_DIR [--tag cpu]
"""
import argparse
import json
import os
import sys

import numpy as np

import boxlib as bl
import t1t2

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("t2dir")
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    out = bl.outdir()
    res = {}
    for th in t1t2.THETAS:
        for var in ("plain", "sub"):
            for seed in t1t2.SEEDS:
                name = f"T2_th{th}_{var}_s{seed}"
                rd = os.path.join(a.t2dir, name)
                meta = json.load(open(os.path.join(rd, "box.json")))
                r = t1t2.analyse(rd, meta, 200)
                r.update(theta=th, var=var, seed=seed)
                res[name] = r
    fs.use_style()
    cols = {"0.001": fs.PAL["blue"], "0.1": fs.PAL["red"], "1.0": fs.PAL["yellow"],
            "10.0": fs.PAL["green"]}
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.6))
    ax1 = fig.add_axes([0.09, 0.57, 0.38, 0.38])
    ax2 = fig.add_axes([0.59, 0.57, 0.38, 0.38])
    ax3 = fig.add_axes([0.09, 0.08, 0.38, 0.38])
    ax4 = fig.add_axes([0.59, 0.08, 0.38, 0.38])
    for name, r in res.items():
        c = cols[r["theta"]]
        x = np.log10(float(r["theta"])) + (-0.15 if r["var"] == "plain" else 0.15) + \
            (0.05 if r["seed"] == 2 else -0.05)
        mk = "o" if r["var"] == "plain" else "s"
        mf = c if r["seed"] == 1 else "none"
        if r["seed"] == 1:
            s = np.array(r["series"]["sumP"])
            ax1.plot(np.arange(1, s.size + 1), s, ls="-" if r["var"] == "plain" else "--",
                     color=c, lw=0.7, label=rf"$\theta={r['theta']}$, {r['var']}")
        ax2.errorbar(x, 1e3 * (r["ratio_b"] - 1),
                     yerr=1e3 * r["sumP_per_step_se"] / r["expected_per_step"],
                     fmt=mk, color=c, mfc=mf, ms=4)
        ax2.plot(x, 1e3 * (r["ratio_b_nominal"] - 1), "x", color="k", ms=3)
        ax3.plot(x, r["T2a_z"], mk, color=c, mfc=mf, ms=4)
        ax3.plot(x, r["T2b_z"], "^", color=c, mfc=mf, ms=4)
        ax4.plot(x, np.log10(max(r["T1_max_relE"], 1e-30)), mk, color=c, mfc=mf, ms=4)
        ax4.plot(x, np.log10(max(r["T1_max_relP"], 1e-30)), "v", color=c, mfc=mf, ms=4)
        ax4.plot(x, np.log10(1e-14 * np.sqrt(r["collisions"] / 200 + 1)), "_", color="k", ms=8)
    ax1.axhline(1, **fs.GUIDE)
    ax1.set_xlabel("step", labelpad=-2); ax1.set_ylabel(r"$\Sigma P$ per step / expected")
    ax1.set_ylim(0.993, 1.012)
    ax1.legend(loc="upper center", fontsize=7, ncol=2)
    for ax in (ax2, ax3, ax4):
        ax.set_xticks([-3, -1, 0, 1])
        ax.set_xticklabels(["$10^{-3}$", "0.1", "1", "10"])
        ax.set_xlabel(r"$\theta$ (o plain, s sub-cycled; filled seed 1)", labelpad=-2)
    ax2.axhspan(-5, 5, color="grey", alpha=0.15)
    ax2.axhline(0, **fs.GUIDE)
    ax2.set_ylabel(r"$10^3(\overline{\Sigma P}/{\rm expected}-1)$; x: nominal $\theta$")
    ax3.axhspan(-4, 4, color="grey", alpha=0.15)
    ax3.axhline(0, **fs.GUIDE)
    ax3.set_ylabel(r"$z$: (a) o/s accepted vs $\Sigma P$; (b) $\triangle$ rate")
    ax4.set_ylabel(r"$\log_{10}\max$ per step: o/s $|dE|$, $\nabla$ $|dP_i|$ / $\Sigma MW$")
    ax4.set_ylim(-22, -11)
    fs.save(fig, os.path.join(out, f"t1t2_summary_{a.tag}"))
    plt.close(fig)
    print("written", os.path.join(out, f"t1t2_summary_{a.tag}.png"))


if __name__ == "__main__":
    sys.exit(main())
