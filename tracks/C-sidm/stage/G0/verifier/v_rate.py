#!/usr/bin/env python3
"""V6: mean Moller speed of a Maxwell-Juttner gas, by my own Monte Carlo.

Sampler (not REFERENCES/mj.py): kinetic energy K = W - 1 has density
    p(K) ~ (1 + K) sqrt(K (K + 2)) exp(-K/theta).
Since (1 + K) sqrt(2 + K) <= sqrt(2) (1 + K)^2, propose from
    g(K) ~ K^{1/2} (1 + 2K + K^2) exp(-K/theta)
(a mixture of Gamma(3/2), Gamma(5/2), Gamma(7/2) with scale theta) and accept with
probability sqrt((2 + K)/2)/(1 + K). Directions isotropic. Pairs independent.
Checked moment: <W> = K1(z)/K2(z) + 3 theta (z = 1/theta) [BACKGROUND].
Claim under test (collide/SPEC.md section 2): <v_Mol> = 4 K3(2z)/(z K2(z)^2).
Output (argv[1]): v_rate.json, fig_v6_rate.{png,pdf}.
"""
import json
import os
import sys

import numpy as np
from scipy.special import kve, gamma as G

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 5))
sys.path.insert(0, os.path.join(ROOT, "python"))


def sample_K(theta, n, rng):
    w = np.array([G(1.5) * theta ** 1.5, 2 * G(2.5) * theta ** 2.5, G(3.5) * theta ** 3.5])
    w /= w.sum()
    out = np.empty(0)
    while out.size < n:
        m = int(1.3 * (n - out.size)) + 100
        comp = rng.choice(3, size=m, p=w)
        K = rng.gamma(1.5 + comp, theta)
        acc = rng.random(m) < np.sqrt((2 + K) / 2) / (1 + K)
        out = np.concatenate([out, K[acc]])
    return out[:n]


def sample_u(theta, n, rng):
    K = sample_K(theta, n, rng)
    q = np.sqrt(K * (K + 2))
    mu = rng.uniform(-1, 1, n)
    ph = rng.uniform(0, 2 * np.pi, n)
    s = np.sqrt(1 - mu * mu)
    return np.stack([q * s * np.cos(ph), q * s * np.sin(ph), q * mu], axis=1), 1 + K


def vmol_closed(theta):
    z = 1 / theta
    # exponentially scaled Bessel functions: K3(2z) e^{2z} / (K2(z) e^z)^2
    return 4 * kve(3, 2 * z) / (z * kve(2, z) ** 2)


def main(out):
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261115)
    n = 2_000_000
    rows = []
    for theta in (0.001, 0.01, 0.1, 0.3, 1.0, 3.0, 10.0):
        ua, Wa = sample_u(theta, n, rng)
        ub, Wb = sample_u(theta, n, rng)
        g = Wa * Wb - np.sum(ua * ub, axis=1)
        # g - 1 without cancellation: g - 1 = (|ua - ub|^2 - (Wa - Wb)^2)/2
        d2 = np.sum((ua - ub) ** 2, axis=1)
        dW = (np.sum(ua * ua, axis=1) - np.sum(ub * ub, axis=1)) / (Wa + Wb)
        g1 = 0.5 * (d2 - dW * dW)
        v = np.sqrt(g1 * (g1 + 2)) / (Wa * Wb)
        z = 1 / theta
        Wmean = kve(1, z) / kve(2, z) + 3 * theta
        rows.append(dict(theta=theta, mc=float(v.mean()), se=float(v.std() / np.sqrt(n)),
                         closed=float(vmol_closed(theta)),
                         pull=float((v.mean() - vmol_closed(theta)) / (v.std() / np.sqrt(n))),
                         W_mc=float(Wa.mean()), W_exact=float(Wmean),
                         W_pull=float((Wa.mean() - Wmean) / (Wa.std() / np.sqrt(n))),
                         nonrel=float(np.sqrt(16 * theta / np.pi))))
    ths = np.logspace(-4, 3, 200)
    lim = dict(small=float(vmol_closed(1e-5) / np.sqrt(16e-5 / np.pi)),
               large=float(vmol_closed(1e4)))
    res = dict(rows=rows, limits=lim)
    with open(os.path.join(out, "v_rate.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.95, wspace=0.3)
    ax = axs[0]
    ax.plot(ths, vmol_closed(ths), color=fs.PAL["blue"], label="closed form (SPEC eq. R)")
    ax.plot(ths, np.sqrt(16 * ths / np.pi), **fs.GUIDE, label=r"$\sqrt{16\theta/\pi}$")
    ax.plot([r["theta"] for r in rows], [r["mc"] for r in rows], "o", color=fs.PAL["red"],
            label="own Monte Carlo")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-2, 2)
    ax.set_xlabel(r"$\theta = T/m$")
    ax.set_ylabel(r"$\langle v_{\rm Mol}\rangle$")
    ax.legend(loc="lower right")
    ax = axs[1]
    ax.plot([r["theta"] for r in rows], [r["pull"] for r in rows], "o-", color=fs.PAL["red"],
            label=r"$\langle v_{\rm Mol}\rangle$")
    ax.plot([r["theta"] for r in rows], [r["W_pull"] for r in rows], "s--", color=fs.PAL["yellow"],
            label=r"$\langle W\rangle$ (sampler check)")
    ax.axhspan(-3, 3, color="grey", alpha=0.15)
    ax.set_xscale("log")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("(MC - exact) / standard error")
    ax.legend(loc="upper left")
    ax.set_ylim(-6, 6)
    fs.save(fig, os.path.join(out, "fig_v6_rate"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NRPIC_RUN_DIR", "."))
