#!/usr/bin/env python3
"""Lead check L-N (independent of langevin/sdn/exact.py): the first two moments of the
number of e-folds for the benchmark V2 of the langevin package (quadratic potential,
m = Mpl, phi_in = phi_UV = sqrt(42), phi_end = sqrt(2), reflecting wall at phi_UV;
arXiv:2206.11234 v2 demonstration.tex lines 18-55), from the iterated integrals of the
backward Fokker-Planck equation, derived here:

  overdamped slow roll, Mpl = 1, v = V/(24 pi^2): drift -v'/v, diffusion coefficient v,
  backward operator L = v d^2/dphi^2 - (v'/v) d/dphi.
  L <N> = -1, L <N^2> = -2 <N>, with f(phi_end) = 0 and f'(phi_UV) = 0, give
  g_1(x) = d<N>/dx = int_x^UV dy (1/v(y)) exp(1/v(y) - 1/v(x)),
  g_2(x) = d<N^2>/dx = 2 int_x^UV dy (<N>(y)/v(y)) exp(1/v(y) - 1/v(x)),
  and <N>(phi) = int_end^phi g_1, <N^2>(phi) = int_end^phi g_2.

Quadrature on a fine grid (cumulative Simpson in y from UV downwards, trapezoid in x),
refined twice to estimate the error. Writes lead_dn.json and fig_lead_dn.png.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.integrate import cumulative_trapezoid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "python"))
from nrpic import figstyle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

M = 1.0
PHI_IN = PHI_UV = np.sqrt(42.0)
PHI_END = np.sqrt(2.0)


def v(p):
    return 0.5 * M**2 * p**2 / (24 * np.pi**2)


def moments(n):
    x = np.linspace(PHI_END, PHI_UV, n)
    iv = 1.0 / v(x)
    # h1(x) = int_x^UV e^{1/v(y)}/v(y) dy, computed as e^{-1/v(x)} times it, stably:
    # integrate from UV downwards the function e^{1/v(y) - 1/v(UV)}/v(y), then rescale.
    ref = iv[-1]
    w1 = np.exp(iv - ref) * iv
    c1 = cumulative_trapezoid(w1[::-1], -x[::-1], initial=0.0)[::-1]   # int_x^UV
    g1 = c1 * np.exp(ref - iv)
    N1 = cumulative_trapezoid(g1, x, initial=0.0)
    w2 = 2.0 * np.exp(iv - ref) * iv * N1
    c2 = cumulative_trapezoid(w2[::-1], -x[::-1], initial=0.0)[::-1]
    g2 = c2 * np.exp(ref - iv)
    N2 = cumulative_trapezoid(g2, x, initial=0.0)
    return x, N1, N2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for n in (20001, 80001, 320001):
        x, N1, N2 = moments(n)
        mean = N1[-1]
        var = N2[-1] - mean**2
        rows.append((n, mean, var))
        print(n, mean, var, flush=True)
    (n0, m0, v0), (n1, m1, v1), (n2, m2, v2) = rows
    # Richardson with order 2 (trapezoid)
    mean_r = m2 + (m2 - m1) / 3.0
    var_r = v2 + (v2 - v1) / 3.0
    res = dict(grid=[r[0] for r in rows], mean=[r[1] for r in rows], var=[r[2] for r in rows],
               mean_richardson=mean_r, var_richardson=var_r,
               mean_err_est=abs(m2 - m1) / 3.0, var_err_est=abs(v2 - v1) / 3.0,
               classical=(PHI_IN**2 - PHI_END**2) / 4.0,
               helper_claim=dict(mean=9.38603, var=4.521540,
                                 source="langevin/JOURNAL.md entry 7, run E-stoch-inf-20261115-125658-e3eaef3"))
    res["rel_diff_mean"] = (mean_r - 9.38603) / 9.38603
    res["rel_diff_var"] = (var_r - 4.521540) / 4.521540
    with open(os.path.join(a.out, "lead_dn.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    figstyle.use_style()
    x, N1, N2 = moments(80001)
    fig, ax = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.0))
    ax[0].plot(x, N1, color=figstyle.PAL["blue"], label=r"$\langle\mathcal{N}\rangle$")
    ax[0].plot(x, (x**2 - PHI_END**2) / 4, **figstyle.GUIDE, label="classical")
    ax[0].set_xlabel(r"$\phi/M_\mathrm{Pl}$")
    ax[0].set_ylabel(r"$\langle\mathcal{N}\rangle$")
    ax[0].legend(frameon=False)
    ax[1].plot(x, N2 - N1**2, color=figstyle.PAL["red"])
    ax[1].axhline(4.521540, **figstyle.MASK_LINE)
    ax[1].set_xlabel(r"$\phi/M_\mathrm{Pl}$")
    ax[1].set_ylabel(r"$\mathrm{var}\,\mathcal{N}$")
    fig.tight_layout()
    figstyle.save(fig, os.path.join(a.out, "fig_lead_dn"))
    plt.close(fig)


if __name__ == "__main__":
    main()
