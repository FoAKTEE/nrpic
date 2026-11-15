#!/usr/bin/env python3
"""Checks the mode files of the ladder (written by core's make_case.py) against Track E's
own reference tracks/E-stoch-inf/spec/ref/ms_reference.py (independent background and
Bunch-Davies integration, E-pre-1): for a set of shells, R_k and dR_k/dN at N* in Planck
units, converted to the units of the code (R H*^(3/2), d/dtau = d/dN at N*, k = |n| a*H*).

    modefile_check.py --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "spec", "ref")))
import ms_reference as MS  # noqa: E402

import ladder_lib as LL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    mdl = MS.model_quadratic()
    bg = MS.Background(mdl, mdl["dNstar"] + 0.5)
    hs = bg.Hstar
    res = dict(H_star_planck=hs, H_star_case_json=LL.H_STAR_PLANCK,
               phi_star_code=bg.state(bg.Nstar)[0] / np.sqrt(8 * np.pi), phi0_input=LL.PHI0,
               pi_star_code=bg.state(bg.Nstar)[1] / np.sqrt(8 * np.pi), pi0_input=LL.PI0,
               files={})
    for name, kstart, pick in (("modes_n64.txt", 1e30, [1, 2, 3, 9, 27, 64]),
                               ("modes_n4096.txt", 100.0, [1, 2, 16, 256, 1024, 2048, 4096])):
        n2f, r, dr = LL.read_modefile(os.path.join(HERE, "..", "inputs", name))
        rows = []
        for n2 in pick:
            i = int(np.nonzero(n2f == n2)[0][0])
            k = np.sqrt(n2) * bg.aH(bg.Nstar)
            g = lambda N: k / bg.aH(N) - kstart
            from scipy.optimize import brentq
            ni = 0.0 if g(0.0) < 0 else brentq(g, 0.0, bg.Nstar)
            r0, rn0 = MS.bd_initial(bg, k, ni)
            from scipy.integrate import solve_ivp
            s = solve_ivp(MS.ms_rhs(bg, k, False), (ni, bg.Nstar),
                          [r0.real, r0.imag, rn0.real, rn0.imag], method="DOP853",
                          rtol=1e-12, atol=1e-30)
            rr = (s.y[0, -1] + 1j * s.y[1, -1]) * hs**1.5
            dd = (s.y[2, -1] + 1j * s.y[3, -1]) * hs**1.5
            rows.append(dict(n2=n2, rel_R=float(abs(r[i] / rr - 1)),
                             rel_dR=float(abs(dr[i] / dd - 1)),
                             rel_modulus_R=float(abs(abs(r[i]) / abs(rr) - 1))))
        res["files"][name] = rows
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "modefile_check.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
