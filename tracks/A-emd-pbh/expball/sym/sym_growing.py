#!/usr/bin/env python3
"""Checks of the growing-mode parametrisation and of the exact shell solution
(DERIVATION.md, sections 4 and 5), with sympy and mpmath.

(i)   t(R; m, E) = int_0^R dR'/sqrt(2m/R' + 2E) = (2/3) R^(3/2) (2m)^(-1/2) F(y),
      F = 2F1(1/2, 3/2; 5/2; y), y = -E R/m   (both signs of E).
(ii)  For E < 0 the same as the cycloid t = m (-2E)^(-3/2) (eta - sin eta),
      R = m (-2E)^(-1) (1 - cos eta), on the expanding branch.
(iii) F(1) = 3 pi/4 (turnaround); t_ta = pi m (-2E)^(-3/2).
(iv)  Simultaneous bang time at t_i = 2/(3H) with m = (H^2/2) R^3 (1 + Delta):
      F(y) = sqrt(1 + Delta); t_ta/t_i = 3 pi/(4 sqrt(1+Delta) y^(3/2)).
(v)   Linear limit: y = (5/3) Delta + O(Delta^2), v/(H R) = 1 - Delta/3 + O(Delta^2)
      (the growing mode); Delta_i (t_c/t_i)^(2/3) -> (3/20)(12 pi)^(2/3) = 1.686 as Delta -> 0.
(vi)  R = 2m on the collapsing branch at cos(eta_AH) = 1 + 4E.

Run: python3 sym_growing.py  (exit status 0 when every check passes)
"""

import sys

import mpmath as mp
import sympy as sp

mp.mp.dps = 30
PASS = []


def check(name, ok, info=""):
    PASS.append(bool(ok))
    print(f"[{'ok' if ok else 'FAIL'}] {name}" + (f"  ({info})" if info else ""))


def F(y):
    return mp.hyp2f1(0.5, 1.5, 2.5, y)


def t_hyp(R, m, E):
    return mp.mpf(2) / 3 * R ** 1.5 / mp.sqrt(2 * m) * F(-E * R / m)


def t_quad(R, m, E):
    # substitution R' = R s^2 removes the end-point singularity
    return mp.quad(lambda s: 2 * s * R / mp.sqrt(2 * m / (R * s * s) + 2 * E), [0, 1])


def main():
    # (i) integral representation, several shells, both signs of E
    worst = 0
    for (R, m, E) in [(1, 0.3, -0.1), (2, 0.5, -0.12), (3, 0.2, 0.05), (1, 1, -0.4999),
                      (5, 0.01, -1e-4), (4, 2, 0.3)]:
        R, m, E = mp.mpf(R), mp.mpf(m), mp.mpf(E)
        if 2 * m / R + 2 * E <= 0:
            continue
        a, b = t_hyp(R, m, E), t_quad(R, m, E)
        worst = max(worst, abs(a / b - 1))
    check("(i) t(R; m, E) = (2/3) R^1.5 (2m)^-0.5 2F1(1/2,3/2;5/2;-ER/m)", worst < 1e-20,
          f"max rel. diff {mp.nstr(worst, 3)}")
    # symbolic series in y to order 6 against term-by-term integration
    y, s = sp.symbols("y s")
    ser_int = sp.integrate(sp.series(sp.sqrt(s) / sp.sqrt(1 - y * s), y, 0, 7).removeO(),
                           (s, 0, 1))
    ser_hyp = sp.Rational(2, 3) * sum(sp.rf(sp.Rational(1, 2), k) * sp.rf(sp.Rational(3, 2), k)
                                      / (sp.rf(sp.Rational(5, 2), k) * sp.factorial(k)) * y ** k
                                      for k in range(7))
    check("(i) series in y to order 6: int_0^1 s^1/2 (1 - y s)^-1/2 ds = (2/3) F(y)",
          sp.simplify(sp.expand(ser_int - ser_hyp)) == 0)
    # (ii) cycloid
    worst = 0
    for (m, E) in [(1, -0.1), (0.3, -0.02), (2, -0.45)]:
        m, E = mp.mpf(m), mp.mpf(E)
        A = m / (-2 * E)
        T0 = m / (-2 * E) ** 1.5
        for eta in [0.1, 1.0, 2.0, 3.0]:
            R = A * (1 - mp.cos(eta))
            t = T0 * (eta - mp.sin(eta))
            worst = max(worst, abs(t_hyp(R, m, E) / t - 1))
    check("(ii) cycloid = hypergeometric form on the expanding branch", worst < 1e-20,
          f"max rel. diff {mp.nstr(worst, 3)}")
    # (iii) turnaround
    Fs = sp.hyper([sp.Rational(1, 2), sp.Rational(3, 2)], [sp.Rational(5, 2)], 1)
    F1 = sp.simplify(sp.hyperexpand(Fs))
    check("(iii) F(1) = 3 pi/4", sp.simplify(F1 - 3 * sp.pi / 4) == 0, f"F(1) = {F1}")
    m, E = mp.mpf("0.7"), mp.mpf("-0.05")
    Rmax = m / (-E)
    check("(iii) t(R_max) = pi m (-2E)^-1.5",
          abs(t_hyp(Rmax, m, E) / (mp.pi * m / (-2 * E) ** 1.5) - 1) < 1e-20)
    # (iv) simultaneous bang time
    H, Rr, D, Y = sp.symbols("H R Delta y", positive=True)
    msym = H ** 2 * Rr ** 3 * (1 + D) / 2
    pref = sp.Rational(2, 3) * Rr ** sp.Rational(3, 2) / sp.sqrt(2 * msym)
    check("(iv) t = t_i = 2/(3H)  <=>  F(y) = sqrt(1+Delta)",
          sp.simplify(sp.Rational(2, 3) / H / pref - sp.sqrt(1 + D)) == 0)
    Esym = -Y * msym / Rr
    tta = sp.pi * msym / (-2 * Esym) ** sp.Rational(3, 2)
    check("(iv) t_ta/t_i = 3 pi/(4 sqrt(1+Delta) y^1.5)",
          sp.simplify(tta / (sp.Rational(2, 3) / H) - 3 * sp.pi / (4 * sp.sqrt(1 + D) * Y ** sp.Rational(3, 2))) == 0)
    # (v) linear limit by series inversion of F(y) = sqrt(1+Delta)
    eps = sp.symbols("epsilon")
    Fser = sum(sp.rf(sp.Rational(1, 2), k) * sp.rf(sp.Rational(3, 2), k)
               / (sp.rf(sp.Rational(5, 2), k) * sp.factorial(k)) * eps ** k for k in range(4))
    a1, a2 = sp.symbols("a1 a2")
    yser = a1 * D + a2 * D ** 2
    eq = sp.series(Fser.subs(eps, yser) - sp.sqrt(1 + D), D, 0, 3).removeO()
    sol = sp.solve([eq.coeff(D, 1), eq.coeff(D, 2)], [a1, a2], dict=True)[0]
    check("(v) y = (5/3) Delta + O(Delta^2)", sol[a1] == sp.Rational(5, 3),
          f"y = {sol[a1]} Delta + {sol[a2]} Delta^2")
    h = sp.sqrt((1 + D) * (1 - yser.subs(sol)))
    hs = sp.series(h, D, 0, 2).removeO()
    check("(v) v/(HR) = sqrt((1+Delta)(1-y)) = 1 - Delta/3 + O(Delta^2)",
          sp.simplify(hs - (1 - D / 3)) == 0, f"{hs}")
    # Delta_i (t_c/t_i)^(2/3) for decreasing Delta_i
    target = mp.mpf(3) / 20 * (12 * mp.pi) ** (mp.mpf(2) / 3)
    vals = []
    for Di in [mp.mpf("1e-2"), mp.mpf("1e-3"), mp.mpf("1e-4")]:
        yy = mp.findroot(lambda q: F(q) - mp.sqrt(1 + Di), 5 * Di / 3)
        tc = 3 * mp.pi / (2 * mp.sqrt(1 + Di) * yy ** 1.5)
        vals.append(Di * tc ** (mp.mpf(2) / 3))
    check("(v) Delta_i (t_c/t_i)^(2/3) -> (3/20)(12 pi)^(2/3) = 1.6865 (linear collapse threshold)",
          abs(vals[-1] / target - 1) < 1e-3,
          f"{[mp.nstr(v, 8) for v in vals]} -> {mp.nstr(target, 8)}")
    # (vi) apparent horizon on the collapsing branch
    eta, Es, ms = sp.symbols("eta E m")
    Rcyc = ms / (-2 * Es) * (1 - sp.cos(eta))
    check("(vi) R = 2m  <=>  cos(eta) = 1 + 4E",
          sp.simplify((Rcyc - 2 * ms).subs(sp.cos(eta), 1 + 4 * Es)) == 0)
    print(f"{sum(PASS)}/{len(PASS)} checks passed")
    return 0 if all(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
