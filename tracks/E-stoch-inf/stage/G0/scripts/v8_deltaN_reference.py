#!/usr/bin/env python3
"""V8 of the G0 verifier: two numbers behind acceptance A8 (SPEC.md 7.2).

(a) Lattice sum against the continuum: the variance of a field with dimensionless spectrum
    Delta(k) on an L-periodic lattice with modes 1 <= |n| <= 64 is
    sum_n 2 pi^2 Delta(k_n) / (k_n^3 L^3) = sum_n Delta / (4 pi |n|^3), the continuum is
    int_dk^64dk Delta dk/k. Computed for Delta = const and for the SR spectrum at N_f of my
    run V2 (power-law fit of v2.json). Claim: 1.0805 (quadratic case).
(b) Separate-universe excess at coarse-graining sigma: a massless de Sitter mode
    dphi_k = H/sqrt(2k^3) (1 + i k tau) e^(-i k tau) is kicked into the gradient-free system at
    k|tau| = sigma and then evolves by dphi'' + 3 dphi' = 0 (e-folds), ending at
    dphi + dphi'/3. Ratio of its power to the true late-time power H^2/(2k^3):
    |1 - i sigma ... | evaluated numerically against the closed form 1 + sigma^2/3 + sigma^4/9.
    Claim: Langevin with sigma = 1 overestimates the variance by 42-45 percent.
Writes v8.json and fig_v8.png.
"""
import argparse
import json
import os

import numpy as np

import common
from common import save_json


def lattice_ratio(delta_of_q, qmax2=4096):
    m = int(np.floor(np.sqrt(qmax2)))
    r = np.arange(-m, m + 1)
    nx, ny, nz = np.meshgrid(r, r, r, indexing="ij")
    q2 = nx**2 + ny**2 + nz**2
    sel = (q2 >= 1) & (q2 <= qmax2)
    q = np.sqrt(q2[sel].astype(float))
    lat = np.sum(delta_of_q(q) / (4 * np.pi * q**3))
    qq = np.logspace(0, np.log10(np.sqrt(qmax2)), 20001)
    cont = np.trapezoid(delta_of_q(qq) / qq, qq)
    return lat / cont, lat, cont


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--v2", required=True, help="v2.json of my run V2")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    out = {}
    r0 = lattice_ratio(lambda q: np.ones_like(q))
    out["lattice_over_continuum_flat"] = r0[0]
    v2 = json.load(open(a.v2))
    qs = np.array([r["k_over_dk"] for r in v2["SR"]])
    P = np.array([r["full_Nf"] for r in v2["SR"]])
    c = np.polyfit(np.log(qs), np.log(P), 2)
    r1 = lattice_ratio(lambda q: np.exp(np.polyval(c, np.log(q))))
    out["lattice_over_continuum_SR_Nf"] = r1[0]
    out["SR_fit_coeffs_lnP_vs_lnq"] = c.tolist()
    # (b) separate-universe excess
    sig = np.logspace(-2, np.log10(3.0), 200)

    def excess(s):
        # x = k tau = -s; dphi ~ (1 + i x) e^{-i x}; d/dN = -tau d/dtau = -x d/dx
        x = -s
        f = (1 + 1j * x) * np.exp(-1j * x)
        dfdx = (1j) * np.exp(-1j * x) + (1 + 1j * x) * (-1j) * np.exp(-1j * x)
        dfdN = -x * dfdx
        return np.abs(f + dfdN / 3.0) ** 2
    ex = np.array([excess(s) for s in sig])
    closed = 1 + sig**2 / 3 + sig**4 / 9
    out["excess_sigma1"] = float(excess(1.0) - 1)
    out["max_abs_numeric_minus_closed"] = float(np.max(np.abs(ex - closed)))
    out["excess_sigma0.1"] = float(excess(0.1) - 1)
    out["excess_sigma0.01"] = float(excess(0.01) - 1)
    for k, v in out.items():
        print(k, v)
    save_json(os.path.join(a.out, "v8.json"), out)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.9, wspace=0.42)
    ax[0].loglog(sig, ex - 1, color=fs.PAL["red"], label="numerical")
    ax[0].loglog(sig, closed - 1, **fs.GUIDE, label=r"$\sigma^2/3+\sigma^4/9$")
    ax[0].axvline(1.0, **fs.MASK_LINE)
    ax[0].axhspan(0.42, 0.45, color=fs.PAL["blue"], alpha=0.2, label="claim 42-45 %")
    ax[0].set_xlabel(r"$\sigma$")
    ax[0].set_ylabel("variance excess")
    ax[0].set_title("massless de Sitter, gradient-free after the kick", fontsize=9)
    ax[0].legend()
    qq = np.logspace(0, np.log10(64), 100)
    ax[1].loglog(qs, P, "o", color=fs.PAL["red"], label="V2 full MS at $N_f$ (SR)")
    ax[1].loglog(qq, np.exp(np.polyval(c, np.log(qq))), **fs.GUIDE, label="fit")
    ax[1].set_xlabel(r"$k/dk$")
    ax[1].set_ylabel(r"$\Delta_\mathcal{R}$")
    ax[1].set_title("lattice/continuum = %.4f (flat: %.4f)" % (r1[0], r0[0]), fontsize=9)
    ax[1].legend()
    fig.savefig(os.path.join(a.out, "fig_v8.png"))


if __name__ == "__main__":
    main()
