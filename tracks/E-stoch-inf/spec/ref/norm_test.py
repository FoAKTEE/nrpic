#!/usr/bin/env python3
"""Test T3 of E-pre-1: normalisation of the Gaussian random draw with a given spectrum.

The appendix "Randomness with a power spectrum" of arXiv:2502.06783 (and of the thesis
arXiv:2610.32592, appendix app:random) builds a real field from the QFT amplitude f_k
(<f(x)^2> = int d^3k/(2pi)^3 |f_k|^2) as  f(x) = PREFACTOR * IRFFTN{ f_k s_k },
s_k = N^(-3/2) RFFTN{white noise}, with RFFTN/IRFFTN unnormalised (RFFTN{IRFFTN} = N^3).
This script draws such fields for three prefactors,
   L^(-3/2) = (dk / 2pi)^(3/2)   (derived in SPEC.md section 5),
   dk^(3/2)                      (first line of the papers' "final strategy"),
   (dk / sqrt(2 pi))^(3/2)       (second line of the papers' "final strategy"),
and measures the shell-averaged dimensionless spectrum Delta = k^3 P(k) / (2 pi^2),
P(k) = |FT f|^2 / L^3 with FT f = (L/N)^3 RFFTN{f}, against the input k^3 |f_k|^2/(2 pi^2).

Usage: python3 norm_test.py --out DIR [--n 64] [--seeds 8]
"""
import argparse
import json
import os

import numpy as np


def draw(n, L, fk_of_k, prefactor, rng):
    dk = 2 * np.pi / L
    kx = np.fft.fftfreq(n, d=1.0 / n) * dk
    kz = np.fft.rfftfreq(n, d=1.0 / n) * dk
    K = np.sqrt(kx[:, None, None] ** 2 + kx[None, :, None] ** 2 + kz[None, None, :] ** 2)
    white = rng.standard_normal((n, n, n))
    s = np.fft.rfftn(white) / n**1.5                 # N^(-3/2) RFFTN
    fk = np.zeros_like(K)
    fk[K > 0] = fk_of_k(K[K > 0])
    IRFFTN = lambda a: np.fft.irfftn(a, s=(n, n, n)) * n**3   # unnormalised inverse
    return prefactor * IRFFTN(fk * s), K


def shell_delta(f, K, L, n, edges):
    F = np.fft.rfftn(f) * (L / n) ** 3                # continuum Fourier transform
    P = np.abs(F) ** 2 / L**3
    D = K**3 * P / (2 * np.pi**2)
    out, cnt = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (K >= lo) & (K < hi)
        out.append(D[m].mean())
        cnt.append(int(m.sum()))
    return np.array(out), np.array(cnt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--seeds", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    n = a.n
    L = 2 * np.pi * 7.0                               # arbitrary box, dk = 1/7
    dk = 2 * np.pi / L
    A = 1.3e-3                                        # Delta_in = A^2 / (2 pi^2), flat
    fk_of_k = lambda k: A * k**-1.5
    Delta_in = A**2 / (2 * np.pi**2)
    pref = {"L^-3/2": L**-1.5, "dk^3/2": dk**1.5, "(dk/sqrt(2pi))^3/2": (dk / np.sqrt(2 * np.pi))**1.5}
    edges = dk * np.array([0.5, 1.5, 2.5, 3.5, 5, 7, 10, 14, 20, 28, 32])
    res = {"n": n, "L": L, "dk": dk, "Delta_in": Delta_in, "edges_over_dk": (edges / dk).tolist(),
           "seeds": a.seeds}
    ratios = {}
    for name, p in pref.items():
        rs = []
        for seed in range(a.seeds):
            rng = np.random.default_rng(12345 + seed)
            f, K = draw(n, L, fk_of_k, p, rng)
            D, cnt = shell_delta(f, K, L, n, edges)
            rs.append(D / Delta_in)
        rs = np.array(rs)
        ratios[name] = rs
        res[name] = {"mean_ratio_per_shell": rs.mean(0).tolist(),
                     "std_of_mean_per_shell": (rs.std(0, ddof=1) / np.sqrt(a.seeds)).tolist(),
                     "overall_mean_ratio": float(rs.mean())}
    res["modes_per_shell_halfspace"] = cnt.tolist()
    # expected ratios for the papers' prefactors relative to L^-3/2, in power
    res["expected_power_ratio"] = {k: float((p / pref["L^-3/2"]) ** 2) for k, p in pref.items()}
    np.savez_compressed(os.path.join(a.out, "norm_test.npz"), edges=edges / dk,
                        **{k.replace("/", "_"): v for k, v in ratios.items()})
    with open(os.path.join(a.out, "norm_test.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: (v["overall_mean_ratio"] if isinstance(v, dict) and "overall_mean_ratio" in v else v)
                      for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    main()
