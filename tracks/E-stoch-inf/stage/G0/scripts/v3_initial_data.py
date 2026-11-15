#!/usr/bin/env python3
"""V3 of the G0 verifier: geodesic-gauge initial data of P2 eq. (17) against the linearised
constraints, written from scratch (not the track's ic_constraint_check.py).

Metric gamma_ij = a^2 (1 - 2 Phi) delta_ij (P2 main_V2PRD.tex:180-183 with E = 0 at t*),
lapse 1 + Psi_G with Psi_G = 0 (geodesic slicing). One Fourier mode, Mpl = 1, P1 convention
eps2 = -dln eps1/dN. Linearised constraints (P1 PRD_v2.tex:378-380):
  H: dR3 + (4/3) K_b dK - 2 drho = 0,  dR3 = -4 (k/a)^2 Phi (Fourier, sign from 3-Ricci of a
     conformally flat metric), K_b = -3H, drho = Pi_b dPi + V' dphi;
  M: (2/3) i k dK - i k Pi_b dphi = 0 (Kt = 0 at t*; J_i = -Pi d_i phi).
Data (P2 main_V2PRD.tex:316-327, Bardeen potentials 251-255), with the term of delta Pi as
printed (-sqrt(2 eps1) H Psi_G, = 0 here) or as derived from the dictionary 262-308
(-sqrt(2 eps1) H Psi_B). Also derives delta Pi from the dictionary symbolically.
"""
import argparse
import json
import os

import sympy as sp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    os.makedirs(a_.out, exist_ok=True)
    t = sp.symbols("t", real=True)
    k = sp.symbols("k", positive=True)
    H = sp.Function("H")(t)
    a = sp.Function("a")(t)
    e1 = sp.Function("e1")(t)
    R = sp.Function("R")(t)
    H0, a0, E1, E2, Rv, Rd = sp.symbols("H a eps1 eps2 R Rdot", real=True)
    # background rules: Hdot = -eps1 H^2, adot = a H, eps1dot = -H eps1 eps2 (P1 sign),
    # Rddot from the MS equation (P1 PRD_v2.tex:302-304)
    def bg_sub(expr):
        rules = {
            sp.Derivative(R, (t, 2)): -(3 - E2) * H * sp.Derivative(R, t) - k**2 / a**2 * R,
        }
        expr = expr.subs(rules)
        expr = expr.subs({sp.Derivative(H, t): -e1 * H**2, sp.Derivative(a, t): a * H,
                          sp.Derivative(e1, t): -H * e1 * E2})
        expr = expr.subs({sp.Derivative(R, t): Rd})
        return sp.simplify(expr.subs({H: H0, a: a0, e1: E1, R: Rv}))

    phidot = H * sp.sqrt(2 * e1)                 # field rolls to positive phi
    PhiB = -e1 * H * a**2 / k**2 * sp.Derivative(R, t)     # Phi_B = Psi_B (comoving)
    PsiB = PhiB
    # dictionary at t* with chi_0 = 0, Psi_G = 0: chi = int (Psi_G - Psi_B) dt
    chi_dot = -PsiB                              # d chi/dt at t*, chi(t*) = 0
    # delta phi = sqrt(2 eps1)(R - Phi_NR), Phi_NR = Phi_B - H chi
    # d/dt delta phi at t*: chi = 0, d(H chi)/dt = H chi_dot
    dphi_expr = sp.sqrt(2 * e1) * (R - PhiB)       # value at t* (chi = 0)
    dphidot_dict = (sp.diff(sp.sqrt(2 * e1), t) * (R - PhiB)
                    + sp.sqrt(2 * e1) * (sp.diff(R, t) - sp.diff(PhiB, t) + H * chi_dot))
    dPi_dict = dphidot_dict - phidot * 0          # Psi_G = 0
    # printed P2 eq. (17), Psi_G = 0
    dPi_print = (sp.sqrt(2 * e1) * (sp.diff(R, t) - sp.diff(PhiB, t))
                 - E2 * sp.sqrt(e1 / 2) * H * (R - PhiB))
    dPi_corr = dPi_print - sp.sqrt(2 * e1) * H * PsiB
    dK = 3 * (sp.diff(PhiB, t) + H * PsiB)
    # V' from the background Klein-Gordon equation: phiddot + 3 H phidot + V' = 0
    phiddot = sp.diff(phidot, t)
    Vp = -phiddot - 3 * H * phidot
    Kb = -3 * H

    def ham(dPi):
        drho = phidot * dPi + Vp * dphi_expr
        return bg_sub(-4 * k**2 / a**2 * PhiB + sp.Rational(4, 3) * Kb * dK - 2 * drho)

    mom = bg_sub(sp.Rational(2, 3) * dK - phidot * dphi_expr)
    res = {
        "H_printed": str(sp.factor(ham(dPi_print))),
        "H_corrected": str(sp.simplify(ham(dPi_corr))),
        "H_dictionary": str(sp.simplify(ham(dPi_dict))),
        "M": str(sp.simplify(mom)),
        "dPi_dictionary_minus_corrected": str(sp.simplify(bg_sub(dPi_dict - dPi_corr))),
        "dPi_dictionary_minus_printed": str(sp.factor(bg_sub(dPi_dict - dPi_print))),
        "dK_minus_3eps1H(R-PhiB)": str(sp.simplify(bg_sub(dK - 3 * e1 * H * (R - PhiB)))),
    }
    res["note"] = ("printed-form residual is first order in the noise; relative to [H] it is "
                   "computed below (rel_violation_printed_at_x*), falling as eps1 (aH/k)^2/2")
    # relative size |H_printed| / [H] at t* for one mode with de Sitter mode functions
    # (eps1 = 0.0111, eps2 = -0.0221: the SR case at N*, run of v1), x = k/(aH) in [1, 64];
    # [H] = sum of the absolute values of the four terms (P1:735-745 'absolute magnitude')
    import numpy as np
    import common  # noqa: F401  (puts python/ on the path)
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    terms = [-4 * k**2 / a**2 * PhiB, sp.Rational(4, 3) * Kb * dK, -2 * phidot * dPi_corr,
             -2 * Vp * dphi_expr]
    f_terms = [sp.lambdify((H0, a0, E1, E2, Rv, Rd, k), bg_sub(tm)) for tm in terms]
    f_res = sp.lambdify((H0, a0, E1, E2, Rv, Rd, k), bg_sub(ham(dPi_print)))
    e1v, e2v, Hv, av = 0.0111, -0.0221, 1.0, 1.0
    xs = np.logspace(0, np.log10(64), 60)
    rel = []
    for x in xs:
        kk = x * av * Hv
        tau = -1.0 / ((1 - e1v) * av * Hv)
        v = np.exp(-1j * kk * tau) * (1 - 1j / (kk * tau)) / np.sqrt(2 * kk)
        dv = np.exp(-1j * kk * tau) / np.sqrt(2 * kk) * (-1j * kk * (1 - 1j / (kk * tau))
                                                         + 1j / (kk * tau**2))
        z = av * np.sqrt(2 * e1v)
        Rk = v / z
        Rdk = (dv / z - v * av * Hv / z) / av
        absH = sum(abs(f(Hv, av, e1v, e2v, Rk, Rdk, kk)) for f in f_terms)
        rel.append(abs(f_res(Hv, av, e1v, e2v, Rk, Rdk, kk)) / absH)
    rel = np.array(rel)
    res["rel_violation_printed_at_x1"] = float(rel[0])
    res["rel_violation_printed_at_x64"] = float(rel[-1])
    fs.use_style()
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.17, top=0.9)
    ax.loglog(xs, rel, color=fs.PAL["red"], label="printed P2 eq. (17)")
    ax.loglog(xs, 0.5 * e1v * xs**-2.0, **fs.GUIDE, label=r"$\varepsilon_1 (aH/k)^2/2$")
    ax.set_xlabel(r"$k/(aH)$ at $t^\ast$")
    ax.set_ylabel(r"$|\mathcal{H}|/[\mathcal{H}]$, linear")
    ax.set_title("first-order violation (corrected form: 0)", fontsize=9)
    ax.legend()
    fig.savefig(os.path.join(a_.out, "fig_v3_violation.png"))
    for k_, v in res.items():
        print(k_, ":", v)
    with open(os.path.join(a_.out, "v3.json"), "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
