#!/usr/bin/env python3
"""Lead's independent closed-form check of D-pre-3 numbers (secondary_infall), written
without reading secondary_infall/common.py or shells.py.

Newtonian, G = M = 1, EdS with H_i = eps at t_i = 2/(3 eps). A shell at initial radius r
moves with the Hubble flow v = eps r and encloses mu(r) = 1 + eps^2 r^3 / 2 (seed plus
uniform dust of density 3 eps^2 / (8 pi)). Its energy is E = v^2/2 - mu/r = -1/r. Radial
Kepler orbit r(eta) = A (1 - cos eta), t(eta) = t0 + B (eta - sin eta), A = mu r / 2,
B = mu (r/2)^(3/2). Turnaround at eta = pi, arrival at the centre at eta = 2 pi.
Prints M_ta(a) and M_c(a) (mass of the shells that reached r = 0) at a/a_i = 2, 4, 8, 100,
1000 and the coefficient (M_ta - 1)/(a/a_i). Figure: lead_infall_recheck.png.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/python")
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle  # noqa: E402


def times(r, eps):
    ti = 2.0 / (3.0 * eps)
    mu = 1.0 + 0.5 * eps ** 2 * r ** 3
    A = 0.5 * mu * r
    B = mu * (0.5 * r) ** 1.5
    c = 1.0 - r / A            # cos eta_i
    eta_i = np.arccos(c)       # outgoing branch, 0 < eta_i < pi
    t0 = ti - B * (eta_i - np.sin(eta_i))
    return mu, t0 + B * np.pi, t0 + B * 2.0 * np.pi


def mass_at(a, eps, which):
    ti = 2.0 / (3.0 * eps)
    t = ti * a ** 1.5
    k = 1 if which == "ta" else 2
    f = lambda lr: times(np.exp(lr), eps)[k] - t
    lo, hi = np.log(1e-6 / eps ** (2 / 3)), np.log(1e6 / eps ** (2 / 3))
    lr = brentq(f, lo, hi, xtol=1e-14, rtol=1e-14)
    return times(np.exp(lr), eps)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    res = {}
    for eps in (0.003, 0.01, 0.03, 0.1):
        row = {}
        for a in (2, 4, 8, 100, 1000):
            mta = mass_at(a, eps, "ta")
            mc = mass_at(a, eps, "c")
            row[str(a)] = dict(M_ta=mta, M_c=mc, coef=(mta - 1) / a)
        res[str(eps)] = row
    res["coef_limit_(4/(3pi))^(2/3)"] = (4 / (3 * np.pi)) ** (2 / 3)
    figstyle.use_style()
    fig, ax = plt.subplots(figsize=(5.5, 4))
    aa = np.geomspace(1.05, 1000, 80)
    eps = 0.01
    ax.plot(aa, [(mass_at(x, eps, "ta") - 1) / x for x in aa], label=r"$(M_{\rm ta}-M)/(M a/a_i)$")
    ax.plot(aa, [(mass_at(x, eps, "c") - 1) / x for x in aa], label=r"$(M_{\rm c}-M)/(M a/a_i)$")
    ax.axhline(res["coef_limit_(4/(3pi))^(2/3)"], color="k", ls="--", lw=0.8, label=r"$(4/3\pi)^{2/3}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel("coefficient")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(a_.out, "lead_infall_recheck.png"), dpi=150)
    with open(os.path.join(a_.out, "lead_infall_recheck.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
