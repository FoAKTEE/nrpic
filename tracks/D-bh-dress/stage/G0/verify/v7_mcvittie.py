#!/usr/bin/env python3
"""Verifier check C7: the definitional drift of the area mass of the black-hole apparent
horizon in McVittie (SCOPE.md 3.3: d ln M_AH / d ln a = -12 (m H)^2), derived with sympy
from the McVittie metric itself, and the precision statement of SCOPE.md 3.3.

McVittie (G = c = 1, isotropic r, mass parameter m, scale factor a(t), H = a'/a):
  ds^2 = -[(1 - m/(2ar))/(1 + m/(2ar))]^2 dt^2 + a^2 (1 + m/(2ar))^4 (dr^2 + r^2 dOmega^2)
Steps: areal radius R = a r (1 + m/(2ar))^2; Misner-Sharp mass from
  1 - 2 M_MS/R = g^{mu nu} d_mu R d_nu R  (computed from the metric, not assumed);
apparent horizons where 1 - 2 M_MS/R = 0; the smaller root expanded in m H; then with
H^2 proportional to a^-3 (matter era, as in the scoping text) the derivative in ln a.
Numerical cross-check: the exact smaller root for m H = 0.01, 0.03, 0.1.

Usage: v7_mcvittie.py [--out DIR]
"""
import argparse
import json
import os

import sympy as sp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a_ = ap.parse_args()
    os.makedirs(a_.out, exist_ok=True)
    t, r, m = sp.symbols("t r m", positive=True)
    a = sp.Function("a", positive=True)(t)
    psi = 1 + m / (2 * a * r)
    gtt = -((1 - m / (2 * a * r)) / psi) ** 2
    grr = a ** 2 * psi ** 4
    R = a * r * psi ** 2
    # g^{mu nu} d_mu R d_nu R for the diagonal metric (t, r)
    gradR2 = sp.diff(R, t) ** 2 / gtt + sp.diff(R, r) ** 2 / grr
    H = sp.symbols("H", positive=True)
    gradR2 = sp.simplify(gradR2.subs(sp.Derivative(a, t), H * a))
    MMS = sp.simplify(R * (1 - gradR2) / 2)
    # express through R: claim M_MS = m + H^2 R^3 / 2
    claim = sp.simplify(MMS - (m + H ** 2 * R ** 3 / 2))
    res = {"MS_minus_(m+H^2R^3/2)": str(claim)}
    # horizon condition 1 - 2 m/Rh - H^2 Rh^2 = 0 in terms of Rh; expand the small root
    x, h = sp.symbols("x h", positive=True)    # x = Rh/(2m), h = m H
    eq = 1 - 1 / x - 4 * h ** 2 * x ** 2
    # series solution x = 1 + c1 h^2 + c2 h^4
    c1, c2 = sp.symbols("c1 c2")
    xs = 1 + c1 * h ** 2 + c2 * h ** 4
    ser = sp.series(eq.subs(x, xs), h, 0, 6).removeO()
    sol = sp.solve([sp.expand(ser).coeff(h, 2), sp.expand(ser).coeff(h, 4)], [c1, c2], dict=True)[0]
    xsol = xs.subs(sol)
    res["Rh_over_2m_series"] = str(sp.expand(xsol))
    # M_AH = Rh/2 = m x ; H^2 = H_i^2 (a/a_i)^-3 -> d h^2/d ln a = -3 h^2
    lnA = sp.symbols("lnA")
    hh = sp.symbols("h0", positive=True) * sp.exp(-sp.Rational(3, 2) * lnA)
    MAH = xsol.subs(h, hh)
    dlnM = sp.simplify(sp.diff(sp.log(MAH), lnA).subs(lnA, 0))
    res["dlnMAH_dlna_series"] = str(sp.series(dlnM, sp.symbols("h0", positive=True), 0, 6))
    # numerical cross-check with the exact root
    num = {}
    for hv in (0.003, 0.01, 0.03, 0.1):
        roots = sp.Poly(sp.expand((1 - 1 / x - 4 * hv ** 2 * x ** 2) * x), x).nroots()
        small = min(float(sp.re(z)) for z in roots if abs(sp.im(z)) < 1e-12 and sp.re(z) > 0)
        # d ln M/d ln a by a finite difference in ln a with h^2 ~ a^-3
        d = 1e-5
        def xr(hv2):
            rr = sp.Poly(sp.expand((1 - 1 / x - 4 * hv2 * x ** 2) * x), x).nroots()
            return min(float(sp.re(z)) for z in rr if abs(sp.im(z)) < 1e-12 and sp.re(z) > 0)
        dl = (sp.log(xr(hv ** 2 * float(sp.exp(-3 * d)))) - sp.log(xr(hv ** 2 * float(sp.exp(3 * d))))) / (2 * d)
        num[str(hv)] = {"Rh_over_2m": small, "dlnM_dlna_exact": float(dl), "-12h^2": -12 * hv ** 2}
    res["numeric"] = num
    # precision statement: 1 percent floor over one doubling
    res["k_bound_1pct_one_doubling"] = float(sp.log(1.01) / sp.log(2))
    res["k_bound_1pct_one_doubling_linear"] = 0.01 / float(sp.log(2))
    res["Delta_lnM_k1_vs_k0_one_doubling"] = float(sp.log(2))
    with open(os.path.join(a_.out, "v7_mcvittie.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
