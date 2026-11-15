#!/usr/bin/env python3
"""Test T4 of E-pre-1: do the geodesic-gauge initial data of arXiv:2502.06783 eq. (17)
satisfy the linearised constraints of the same paper, eq. (9)?

Symbolic check (sympy) at the start time t* of the simulation, geodesic gauge
(Psi_G = B_G = 0) with chi_0 = E_0 = 0, for one Fourier mode with amplitudes R, Rdot of
the comoving curvature perturbation. Background relations (Mpl = M, Launay signs):
  phidot = sqrt(2 eps1) H M (field rolling towards positive phi),
  Hdot = -eps1 H^2,  eps1dot = -H eps1 eps2,
  V' = (-3 + eps1 + eps2/2) H phidot          (thesis 2610.32592, chap_SIGR line 358),
  Rddot = -H (3 - eps2) Rdot - (k/a)^2 R      (Mukhanov-Sasaki, 2512.14649 eq. 7).
Fields at t* (2502.06783 eqs. 14-17):
  Phi = Phi_B = -eps1 H a^2 k^-2 Rdot, Psi_B = Phi_B (no window),
  dphi = sqrt(2 eps1) M (R - Phi_B), dX = 2 Phi_B, dK = 3 (Phi_B' + H Psi_B),
  dPi (paper) = sqrt(2 eps1) M (Rdot - Phi_B') - eps2 sqrt(eps1/2) H M (R - Phi_B),
  dPi (re-derived here) = dPi (paper) - sqrt(2 eps1) M H Psi_B.
Linear constraints (2502.06783 eq. 9), Laplacian -> -(k/a)^2:
  Ham = 4 Lap Phi - 4 H kappa - 2 M^-2 drho,  drho = phidot dPi + V' dphi  (Psi = 0),
  Mom = kappa - (3/2) M^-2 phidot dphi      (chi = 0),  kappa = dK.
Writes the simplified residuals to --out/ic_check.json.
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
    R, Rd, k, a, H, e1, e2, M = sp.symbols("R Rdot k a H eps1 eps2 M", positive=True)
    phid = sp.sqrt(2 * e1) * H * M
    Hd = -e1 * H**2
    e1d = -H * e1 * e2
    ad = a * H
    Vp = (-3 + e1 + e2 / 2) * H * phid
    Rdd = -H * (3 - e2) * Rd - (k / a) ** 2 * R
    # time derivative of an expression in (R, Rd, a, H, e1) along the background and MS
    def ddt(expr):
        return (sp.diff(expr, R) * Rd + sp.diff(expr, Rd) * Rdd + sp.diff(expr, a) * ad
                + sp.diff(expr, H) * Hd + sp.diff(expr, e1) * e1d)
    PhiB = -e1 * H * a**2 / k**2 * Rd
    PsiB = PhiB
    PhiBd = ddt(PhiB)
    dphi = sp.sqrt(2 * e1) * M * (R - PhiB)
    dK_paper = 3 * (PhiBd + H * PsiB)
    dK_mom = 3 * e1 * H * (R - PhiB)
    dPi_paper = sp.sqrt(2 * e1) * M * (Rd - PhiBd) - e2 * sp.sqrt(e1 / 2) * H * M * (R - PhiB)
    dPi_new = dPi_paper - sp.sqrt(2 * e1) * M * H * PsiB
    out = {}
    lap = -(k / a) ** 2
    for name, dPi in (("dPi_paper", dPi_paper), ("dPi_rederived", dPi_new)):
        drho = phid * dPi + Vp * dphi
        ham = 4 * lap * PhiB - 4 * H * dK_paper - 2 / M**2 * drho
        out["Ham_residual_with_" + name] = str(sp.simplify(sp.expand(ham)))
    mom = dK_paper - sp.Rational(3, 2) / M**2 * phid * dphi
    out["Mom_residual"] = str(sp.simplify(sp.expand(mom)))
    out["dK_paper_minus_dK_from_momentum_constraint"] = str(sp.simplify(sp.expand(dK_paper - dK_mom)))
    out["PhiB_dot"] = str(sp.simplify(sp.expand(PhiBd)))
    with open(os.path.join(a_.out, "ic_check.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
