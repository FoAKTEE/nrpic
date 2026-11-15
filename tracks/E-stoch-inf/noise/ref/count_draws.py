#!/usr/bin/env python3
"""T-N1: modes, draws per step and evaluation cost at the resolutions of the specification.

    python3 count_draws.py --out DIR [--theta 0.025]

Configurations (sources in NOISE_SPEC.md, section 5):
  - production of arXiv:2512.14649: N = 256, k_max = N k_min / 4 (n_max = 64), sigma = 1,
    L k_sigma* = 2 pi (PRD_v2.tex lines 510-512, 519), N_f - N* ~ 8 (quadratic) and ~ 10
    (inflection) e-folds (Table I, lines 419-420);
  - its convergence series: N = 32, 64, 128, 256 with k_max / dk = 8 (line 756);
  - the unit test of NOISE_SPEC.md section 8: N = 64, nmax2 = 256; N = 32 and 64, nmax2 = 64.
Time stepping: de Sitter proxy k_sigma = sigma k_min exp(Ne) and Delta Ne = 2 pi theta /
(N sigma) per step (line 721); theta = 0.025 is the Courant factor of arXiv:2502.06783
(line 492), not stated in 2512.14649.
Draw cost: Normal2 0.133 ns on one A100, 66.8 ns on one core (rng.md section 8, runs
core-20261115-115230-f0258ce and core-20261115-115134-f0258ce).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from noise_ref import Lattice                             # noqa: E402

NS_CARD, NS_CORE = 0.133, 66.8


def per_step_counts(q, N, theta, sigma, Ntot, s=5.0):
    """Draws per step: Heaviside window with fresh draws (modes crossing in the step) and
    tanh window (modes with Delta W >= 1e-16, i.e. those a stateless frozen generator or
    a Markov generator must draw in that step)."""
    dNe = 2 * np.pi * theta / (N * sigma)
    nsteps = int(np.ceil(Ntot / dNe))
    qs = np.sort(q)
    lnq = np.log(qs)
    t = np.arange(nsteps + 1) * dNe                 # e-folds since the start
    lnks = np.log(sigma) + t                        # ln(k_sigma / k_min)
    # Heaviside: modes with ln q in (lnks_n, lnks_{n+1}]
    cum = np.searchsorted(lnq, lnks, side="right")
    heavi = np.diff(cum)
    # tanh: Delta W >= 1e-16 <=> |s ln(k_sigma/k)| below about 18.4 at one end (bound)
    # count exactly on a subsample of steps
    stride = max(1, nsteps // 400)
    tsub = np.arange(0, nsteps, stride)
    tanh_cnt = np.empty(tsub.size, dtype=np.int64)
    for i, n in enumerate(tsub):
        w0 = 0.5 * (1 + np.tanh(s * (lnks[n] - lnq)))
        w1 = 0.5 * (1 + np.tanh(s * (lnks[n + 1] - lnq)))
        tanh_cnt[i] = int(np.count_nonzero((w1 - w0) >= 1e-16))
    return dict(dNe=dNe, nsteps=nsteps, t=t, heavi=heavi, tsub=tsub, tanh=tanh_cnt)


def eval_cost(lat, b):
    """Complex multiply-adds per evaluation of one component on the whole mesh:
    separable partial sums per MeshBlock of b^3 cells over the half-space modes,
    (N/b)^3 (M b + P b^2 + X b^3) with M modes, P distinct (n_x, n_y), X distinct n_x
    (the formula of E-pre-2, codebase/ref/synth.py:synth_ops, recomputed here), and one
    complex FFT of N^3 points (5 N^3 log2 N^3 real flops / 8 per multiply-add)."""
    N = lat.N
    M = lat.M
    P = len(np.unique(lat.n[:, :2], axis=0))
    X = len(np.unique(lat.n[:, 0]))
    nblocks = (N // b)**3
    sep = nblocks * (M * b + P * b**2 + X * b**3)
    fft = 5 * N**3 * np.log2(float(N**3)) / 8.0
    return float(sep), float(fft)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--theta", type=float, default=0.025)
    a = ap.parse_args()
    configs = [
        ("2512.14649 production", 256, 4096, [8.0, 10.0]),
        ("2512.14649 convergence N=32", 32, 64, []),
        ("2512.14649 convergence N=64", 64, 64, []),
        ("2512.14649 convergence N=128", 128, 64, []),
        ("2512.14649 convergence N=256", 256, 64, []),
        ("unit test base", 64, 256, []),
        ("unit test resolution N=32", 32, 64, []),
    ]
    table = []
    series = {}
    for name, N, nmax2, ntots in configs:
        lat = Lattice(N, 1.0, nmax2)
        row = dict(config=name, N=N, nmax2=nmax2, hemisphere_modes=int(lat.M),
                   estimate_2pi_over_3_nmax3=float(2 * np.pi / 3 * nmax2**1.5),
                   normal2_calls_per_set=int(lat.M),
                   card_seconds_per_set=lat.M * NS_CARD * 1e-9,
                   core_seconds_per_set=lat.M * NS_CORE * 1e-9)
        for b in (32, 64, 128):
            if N % b == 0 and b <= N:
                sep, fft = eval_cost(lat, b)
                row[f"separable_cmadd_per_eval_b{b}"] = sep
                row["fft_cmadd_equiv_per_eval"] = fft
        for Ntot in ntots:
            c = per_step_counts(lat.q, N, a.theta, 1.0, Ntot)
            key = f"{name} Ntot={Ntot:g}"
            row[f"steps_Ntot{Ntot:g}"] = c["nsteps"]
            row[f"heaviside_max_per_step_Ntot{Ntot:g}"] = int(c["heavi"].max())
            row[f"heaviside_mean_per_step_while_crossing_Ntot{Ntot:g}"] = float(
                c["heavi"][c["t"][1:] <= np.log(np.sqrt(nmax2)) + 1e-12].mean())
            row[f"tanh_max_per_step_Ntot{Ntot:g}"] = int(c["tanh"].max())
            row[f"total_draws_markov_tanh_Ntot{Ntot:g}"] = float(
                np.interp(np.arange(c["nsteps"]), c["tsub"], c["tanh"]).sum())
            series[key] = c
        table.append(row)
    with open(os.path.join(a.out, "count_draws.json"), "w") as f:
        json.dump(dict(theta=a.theta, table=table), f, indent=1)
    p = table[0]
    summ = (f"N=256 nmax=64: {p['hemisphere_modes']} hemisphere modes "
            f"(estimate {p['estimate_2pi_over_3_nmax3']:.0f}); steps 8 e-folds "
            f"{p['steps_Ntot8']}, 10 e-folds {p['steps_Ntot10']} at theta {a.theta}; "
            f"Heaviside max {p['heaviside_max_per_step_Ntot8']} per step; tanh max "
            f"{p['tanh_max_per_step_Ntot8']} per step; one set of draws "
            f"{p['card_seconds_per_set']:.2e} s card, {p['core_seconds_per_set']:.2e} s core; "
            f"N=32 nmax=8: {table[1]['hemisphere_modes']} modes")
    with open(os.path.join(a.out, "summary.txt"), "w") as f:
        f.write(summ + "\n")
    print(summ)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    c = series["2512.14649 production Ntot=8"]
    x = c["t"][1:]
    h = c["heavi"].astype(float)
    ax[0].semilogy(x[h > 0], h[h > 0], ".", ms=2, color=fs.PAL["blue"],
                   label="Heaviside, fresh draws")
    ax[0].semilogy(c["t"][c["tsub"]], c["tanh"], "-", color=fs.PAL["red"],
                   label=r"tanh ($s=5$), $\Delta W\geq10^{-16}$")
    ax[0].axhline(p["hemisphere_modes"], **fs.GUIDE, label="all modes")
    ax[0].axvline(np.log(64), **fs.MASK_LINE)
    ax[0].set_xlabel(r"e-folds since start, $\ln(k_\sigma/k_{\min})$")
    ax[0].set_ylabel("normal pairs per step")
    ax[0].set_title(r"$N=256$, $n_{\max}=64$, $\theta=0.025$", fontsize=10)
    ax[0].legend(loc="upper center", bbox_to_anchor=(0.55, 0.84), fontsize=8)
    Ns = [r["N"] for r in table[1:5]]
    sep = [r.get("separable_cmadd_per_eval_b32", np.nan) for r in table[1:5]]
    fft = [r["fft_cmadd_equiv_per_eval"] for r in table[1:5]]
    sepP = table[0]["separable_cmadd_per_eval_b128"]
    fftP = table[0]["fft_cmadd_equiv_per_eval"]
    ax[1].loglog(Ns, sep, "o-", color=fs.PAL["blue"], label=r"partial sums, $n_{\max}=8$, $b=32$")
    ax[1].loglog(Ns, fft, "s-", color=fs.PAL["red"], label="FFT")
    ax[1].loglog([256], [sepP], "o", mfc="none", color=fs.PAL["blue"], ms=8,
                 label=r"partial sums, $n_{\max}=64$, $b=128$")
    from matplotlib.ticker import NullFormatter
    ax[1].set_xticks([32, 64, 128, 256])
    ax[1].set_xticklabels(["32", "64", "128", "256"])
    ax[1].xaxis.set_minor_formatter(NullFormatter())
    ax[1].set_xlabel(r"$N$")
    ax[1].set_ylabel("complex multiply-adds per field")
    ax[1].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_count_draws"))


if __name__ == "__main__":
    main()
