#!/usr/bin/env python3
"""V4 of the G0 verifier: normalisation of a Gaussian draw with a QFT spectrum.

P2 (2502.06783 v3) main_V2PRD.tex:835-884: <f(x)^2> = int d^3k/(2pi)^3 |f_k|^2 (backward
normalisation), s_k = N^(-3/2) RFFTN{Delta}, IRFFTN unnormalised, dk = 2 pi/(N dx) (P2:393).
Printed prefactors: line 880 = dk^(3/2), line 881 = (dk/sqrt(2 pi))^(3/2). Expected correct
prefactor L^(-3/2) = (dk/2pi)^(3/2), since the discrete form of the integral is
sum_k |f_k|^2 / L^3. Measures <f^2> / (sum |f_k|^2 / L^3) for the three prefactors with
L = 3 (dk is not 1, so no factor hides), N = 32, scale-invariant |f_k|^2 = k^-3 on
1 <= |n| <= 8, 64 seeds. Writes v4.json and fig_v4_norm.png.
"""
import argparse
import os

import numpy as np

import common
from common import save_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=64)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    N, L = 32, 3.0
    dk = 2 * np.pi / L
    n = np.fft.fftfreq(N, 1.0 / N)
    nz = np.fft.rfftfreq(N, 1.0 / N)
    nx, ny, nzz = np.meshgrid(n, n, nz, indexing="ij")
    q = np.sqrt(nx**2 + ny**2 + nzz**2)
    k = q * dk
    band = (q >= 1) & (q <= 8)
    fk = np.zeros_like(k)
    fk[band] = k[band] ** -1.5
    # sum over the full lattice (both hemispheres): weight 2 for 0 < nz < N/2
    w = np.where((nzz == 0) | (nzz == N // 2), 1.0, 2.0)
    expected = np.sum(w * fk**2) / L**3
    pref = {"L^-3/2 (claimed correct)": L**-1.5, "dk^3/2 (P2:880)": dk**1.5,
            "(dk/sqrt(2pi))^3/2 (P2:881)": (dk / np.sqrt(2 * np.pi)) ** 1.5}
    rng = np.random.default_rng(20261115)
    var = {kk: [] for kk in pref}
    shells = np.arange(1, 9)
    shell_meas = {kk: np.zeros(len(shells)) for kk in pref}
    for s in range(a.seeds):
        D = rng.standard_normal((N, N, N))
        sk = np.fft.rfftn(D) / N**1.5
        base = np.fft.irfftn(fk * sk, s=(N, N, N), axes=(0, 1, 2)) * N**3      # unnormalised IRFFTN
        for kk, c in pref.items():
            f = c * base
            var[kk].append(np.mean(f**2))
            # shell power: |FFT of f|^2 / N^6 * L^3 vs |f_k|^2 at the shell
            Fk = np.fft.rfftn(f)
            for j, sh in enumerate(shells):
                m = band & (np.rint(q) == sh)
                shell_meas[kk][j] += np.mean(np.abs(Fk[m]) ** 2 / N**6 * L**3 / fk[m] ** 2) / a.seeds
    out = {"expected_sum_over_L3": expected, "N": N, "L": L, "seeds": a.seeds}
    for kk in pref:
        v = np.array(var[kk])
        out[kk] = dict(ratio=float(v.mean() / expected),
                       ratio_err=float(v.std(ddof=1) / np.sqrt(len(v)) / expected),
                       shell_ratio=shell_meas[kk].tolist())
        print(kk, out[kk]["ratio"], "+-", out[kk]["ratio_err"])
    out["predicted"] = {"L^-3/2 (claimed correct)": 1.0, "dk^3/2 (P2:880)": (2 * np.pi) ** 3,
                        "(dk/sqrt(2pi))^3/2 (P2:881)": (2 * np.pi) ** 1.5}
    save_json(os.path.join(a.out, "v4.json"), out)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(4.0, 3.2))
    fig.subplots_adjust(left=0.18, right=0.96, bottom=0.16, top=0.9)
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["yellow"]]
    for c, kk in zip(cols, pref):
        ax.semilogy(shells, shell_meas[kk], "o-", color=c, label=kk)
        ax.axhline(out["predicted"][kk], color=c, ls="--", lw=1.0)
    ax.set_xlabel(r"shell $|n|$")
    ax.set_ylabel(r"measured / QFT power")
    ax.set_title("draw normalisation, 64 seeds, $N=32$, $L=3$", fontsize=9)
    ax.legend(fontsize=7, loc="center right")
    fig.savefig(os.path.join(a.out, "fig_v4_norm.png"))


if __name__ == "__main__":
    main()
