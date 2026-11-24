#!/usr/bin/env python3
"""Seed spread of the one-patch moments (Ito and Stratonovich readings of P0's printed SDE)
and the moments figure with clipped axes (the Stratonovich reading has rare explosive paths
whose spikes hide the curves in the first version of fig_p0_moments.png).

Usage: python onepatch_seeds.py --out DIR [--nseed 6]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onepatch as op  # noqa: E402
import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def halfwidth(x):
    x = x[np.isfinite(x)]
    lo, hi = np.percentile(x, [15.865, 84.135])
    return 0.5*(hi - lo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nseed", type=int, default=6)
    ap.add_argument("--npath", type=int, default=50000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    N, phi, pi = op.fixed_step("euler", 0.01)
    H, e1, e2 = op.bg_quantities(N, phi, pi)
    res = {}
    series = {}
    for reading in ("ito", "strat"):
        rows = []
        for s in range(a.nseed):
            seed = 7 + s
            t, A, D, ok = op.langevin(H, e1, e2, 0.01, 200, 600, a.npath, seed, reading=reading)
            r = dict(seed=seed, alive=float(ok[-1].mean()))
            for nb in (4.0, 5.0, 6.0):
                j = int(np.argmin(abs(t - nb)))
                ma, sa, k3a, _ = op.moments(A[j] - 1)
                mn, sn, k3n, _ = op.moments(D[j])
                r[str(nb)] = dict(std_a=sa, std_n=sn, skew_a=k3a, mean_n=mn,
                                  hw_a=halfwidth(A[j] - 1), hw_n=halfwidth(D[j]))
            sel = np.where((t >= 4.5) & (t <= 6.0))[0]
            r["median_skew_a"] = float(np.median([op.moments(A[j] - 1)[2] for j in sel]))
            rows.append(r)
            if s == 0:
                series[reading] = (t, np.array([op.moments(A[j] - 1)[1] for j in range(len(t))]),
                                   np.array([op.moments(D[j])[1] for j in range(len(t))]),
                                   np.array([op.moments(A[j] - 1)[2] for j in range(len(t))]),
                                   np.array([halfwidth(A[j] - 1) for j in range(len(t))]))
        summ = {}
        for nb in ("4.0", "5.0", "6.0"):
            for q in ("std_a", "std_n", "skew_a", "mean_n", "hw_a", "hw_n"):
                v = np.array([r[nb][q] for r in rows])
                summ[f"{q}@{nb}"] = [float(v.mean()), float(v.std(ddof=1))]
        v = np.array([r["median_skew_a"] for r in rows])
        summ["median_skew_a"] = [float(v.mean()), float(v.std(ddof=1))]
        res[reading] = dict(rows=rows, mean_sd=summ)
        print(reading, json.dumps(summ), flush=True)

    figstyle.use_style()
    ro_t = np.array([3, 4, 5, 6.0])
    ro_a = np.array([0.0068, 0.117, 0.133, 0.122])
    ro_n = np.array([0.0016, 0.042, 0.150, 0.188])
    fig, axs = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.8))
    for reading, lab, c in (("ito", r"Ito reading", figstyle.SERIES[0]),
                            ("strat", r"Stratonovich reading", figstyle.SERIES[1])):
        t, sa, sn, k3, hw = series[reading]
        axs[0].plot(t, sa, color=c, label=lab + " (std)")
        axs[0].plot(t, hw, color=c, ls="--", lw=1, label=lab + " (68% half-width)")
        axs[1].plot(t, sn, color=c)
        axs[2].plot(t, k3, color=c, lw=1)
    axs[0].plot(ro_t, ro_a, "ko", ms=4, label="P0 Fig. 3, read off")
    axs[1].plot(ro_t, ro_n, "ko", ms=4)
    axs[2].axhline(1.1, color="k", ls=":", lw=1, label="P0 Fig. 2, read off")
    axs[0].set_ylim(0, 0.25)
    axs[2].set_ylim(-0.5, 4)
    axs[0].set_ylabel(r"width of $\alpha-\alpha_b$")
    axs[1].set_ylabel(r"std of $\mathcal{N}-\mathcal{N}_b$")
    axs[2].set_ylabel(r"skewness of $\alpha$")
    for ax in axs:
        ax.set_xlabel(r"$\mathcal{N}_b$")
        ax.set_xlim(2, 6)
    axs[0].legend(fontsize=5.5, loc="upper left")
    axs[2].legend(fontsize=6, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_p0_moments_clipped.png"), dpi=150)
    plt.close(fig)

    with open(os.path.join(a.out, "onepatch_seeds.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)


if __name__ == "__main__":
    main()
