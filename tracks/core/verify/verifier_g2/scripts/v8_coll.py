#!/usr/bin/env python3
"""V8: collision operator (core-v0.3), relaxation in a Minkowski box.

For each case of run core-20261115-134036-5684674 (shell_0.3, shell_2, twotemp_0.01,
twotemp_1): own snapshot reader (as v7a_point.py), first and last snapshot.
- conservation: exactly rounded sums (math.fsum) of m W and m u_i, first against last;
- theta_eq from the conserved mean energy: <W> = K1(1/th)/K2(1/th) + 3 th (own root);
- KS test of the last snapshot's W against the Maxwell-Juttner distribution
  f(W) ~ W sqrt(W^2 - 1) exp(-W/th) (own CDF by quadrature);
- pressure estimator <u^2/W>/3 against theta_eq in standard errors;
- per species (twotemp) the mean of u^2/(3W) per species.

usage: v8_coll.py RUNDIR OUTDIR
"""
import glob
import json
import math
import os
import sys

import numpy as np
from scipy import integrate, optimize, special, stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v7a_point import read_snap  # noqa: E402


def mean_W_mj(th):
    x = 1.0 / th
    return special.kve(1, x) / special.kve(2, x) + 3 * th


def theta_from_meanW(w):
    return optimize.brentq(lambda th: mean_W_mj(th) - w, 1e-4, 50.0, xtol=1e-15, rtol=1e-15)


def mj_cdf_factory(th):
    wmax = 1 + 60 * th
    grid = np.concatenate([1 + np.logspace(-12, np.log10(wmax - 1), 20000)])
    pdf = grid * np.sqrt(grid ** 2 - 1) * np.exp(-(grid - 1) / th)
    cdf = integrate.cumulative_trapezoid(pdf, grid, initial=0.0)
    cdf /= cdf[-1]
    return lambda w: np.interp(w, grid, cdf)


def main():
    rd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    res = {}
    figdata = {}
    for case in ("shell_0.3", "shell_2", "twotemp_0.01", "twotemp_1"):
        snaps = sorted(glob.glob(os.path.join(rd, case, "box.part.*.bin")))
        t0, _, r0, g0, s0, _ = read_snap(snaps[0])
        t1, _, r1, g1, s1, _ = read_snap(snaps[-1])
        m0, m1 = r0[:, 6], r1[:, 6]
        W0 = np.sqrt(1 + np.sum(r0[:, 3:6] ** 2, axis=1))
        W1 = np.sqrt(1 + np.sum(r1[:, 3:6] ** 2, axis=1))
        E0, E1 = math.fsum(m0 * W0), math.fsum(m1 * W1)
        P0 = [math.fsum(m0 * r0[:, 3 + k]) for k in range(3)]
        P1 = [math.fsum(m1 * r1[:, 3 + k]) for k in range(3)]
        meanW = E1 / math.fsum(m1)
        th = theta_from_meanW(meanW)
        cdf = mj_cdf_factory(th)
        ks = stats.kstest(W1, cdf)
        ks0 = stats.kstest(W0, cdf)
        u2 = np.sum(r1[:, 3:6] ** 2, axis=1)
        q = u2 / (3 * W1)
        z = (q.mean() - th) / (q.std(ddof=1) / np.sqrt(len(q)))
        per_species = {}
        for sp in np.unique(s1):
            sel = s1 == sp
            qs = q[sel]
            per_species[int(sp)] = {"n": int(sel.sum()), "theta_pressure": float(qs.mean()),
                                    "z": float((qs.mean() - th) / (qs.std(ddof=1) / np.sqrt(sel.sum()))),
                                    "ks_p": float(stats.kstest(W1[sel], cdf).pvalue)}
        res[case] = {"n": int(len(m1)), "t_first": t0, "t_last": t1, "n_snaps": len(snaps),
                     "masses_equal": bool(np.all(m1 == m1[0])),
                     "energy_first": E0, "energy_last": E1, "energy_rel_change": (E1 - E0) / E0,
                     "momentum_first": P0, "momentum_last": P1,
                     "momentum_change_over_energy": float(max(abs(a - b) for a, b in zip(P0, P1)) / E0),
                     "theta_eq_own": th, "ks_p_end": float(ks.pvalue), "ks_D_end": float(ks.statistic),
                     "ks_p_start": float(ks0.pvalue), "pressure_theta_end": float(q.mean()),
                     "pressure_z_end": float(z), "per_species": per_species}
        figdata[case] = (W1, th, W0)
        print(case, json.dumps({k: v for k, v in res[case].items() if k not in ("momentum_first", "momentum_last")}))
    with open(os.path.join(outdir, "v8_coll.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.4))
    for ax, (case, (W1, th, W0)) in zip(axs, figdata.items()):
        x = (W1 - 1) / th
        bins = np.linspace(0, 12, 61)
        ax.hist(x, bins=bins, density=True, histtype="step", color=fs.PAL["blue"], lw=1, label="end")
        ax.hist((W0 - 1) / th, bins=bins, density=True, histtype="step", color="grey", lw=0.8, label="start")
        g = 1 + bins * th
        pdf = g * np.sqrt(np.maximum(g ** 2 - 1, 0)) * np.exp(-(g - 1) / th)
        norm = np.trapezoid(pdf, bins) if hasattr(np, "trapezoid") else np.trapz(pdf, bins)
        ax.plot(bins, pdf / norm, **fs.GUIDE, label="MJ($\\theta_{eq}$)")
        ax.set_title(f"{case}: p={res[case]['ks_p_end']:.2f}", fontsize=7)
        ax.set_xlabel(r"$(W-1)/\theta_{\rm eq}$")
        ax.set_ylim(0, None)
    axs[0].set_ylabel("density")
    axs[0].legend(fontsize=6)
    fig.suptitle("V8: collisional relaxation in a box, run core-20261115-134036-5684674 (own reader, own MJ)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v8_coll"))


if __name__ == "__main__":
    main()
