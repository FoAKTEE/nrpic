#!/usr/bin/env python3
"""V5 of the G0 verifier: core's stochastic sources (athenak/src/scalar_field/
scalar_field_noise.cpp of release core-v0.3) against the sources of P1 (PRD_v2.tex:297-310,
370-375), by symbolic algebra written here.

Checks, in code units G = c = 1 (Mpl^2 = 1/(8 pi)), alpha_b = 1:
 C1 eps1 = 4 pi Pi_b^2/H^2 (cpp:487) equals phidot^2/(2 H^2 Mpl^2).
 C2 eps2 = 6 + 2 V'/(H Pi_b) - 2 eps1 (cpp:488) equals -dln eps1/dN on the Friedmann background.
 C3 window derivatives w1, w2 (cpp:524-542) equal the first two time derivatives of
    W = (1 + tanh[s ln(sigma a H/k)])/2, with Hdot = -eps1 H^2, eps1dot = -H eps1 eps2.
 C4 shell factor (cpp:543): S_R = R w2 + (2 Rdot + (3 - eps2) H R) w1 (P1:302-304).
 C5 the kicks (cpp:548-550, 727-745; rhs.cpp:151): dPi = (Pi_b/H) I, dK = -eps1 I,
    dAt_ij = eps1 (delta_ij/3 - qh_i qh_j/qh^2) I leave the linearised Hamiltonian and momentum
    constraints unchanged, with qh the symbol of the sixth-order centred first difference
    (coefficients of athenak/src/utils/finite_diff.hpp NGHOST = 4: 3/4, -3/20, 1/60), and P1's
    prefactors: S_Pi/S_R = Mpl sqrt(2 eps1) for phidot > 0, S_K/S_R = -eps1, S_At/S_R = eps1 P_ij.
 Figure: momentum-constraint residual of one kick with the stencil projector (core's default)
 and with the continuum projector, against k dx along (1,1,1) and (1,2,0).
Writes v5.json and fig_v5_projector.png.
"""
import argparse
import json
import os

import numpy as np
import sympy as sp

import common


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a_ = ap.parse_args()
    os.makedirs(a_.out, exist_ok=True)
    res = {}
    t = sp.symbols("t", real=True)
    s, sig, k = sp.symbols("s sigma k", positive=True)
    H = sp.Function("H")(t)
    a = sp.Function("a")(t)
    e1 = sp.Function("e1")(t)
    E1, E2, Hs, As = sp.symbols("eps1 eps2 H a", positive=True)
    rules = {sp.Derivative(H, t): -e1 * H**2, sp.Derivative(a, t): a * H,
             sp.Derivative(e1, t): -H * e1 * E2}

    def D(e):
        """time derivative on the background, first-order rules applied at once"""
        return sp.diff(e, t).subs(rules)

    def sub(e):
        return e.subs({H: Hs, a: As, e1: E1})

    # C1
    Pi, Mpl2 = sp.symbols("Pi_b Mpl2", positive=True)
    res["C1"] = str(sp.simplify((4 * sp.pi * Pi**2 / Hs**2 - Pi**2 / (2 * Hs**2 * Mpl2))
                                .subs(Mpl2, 1 / (8 * sp.pi))))
    # C2: background with phidot = Pi (alpha = 1), Pidot = -3 H Pi - V', Hdot = -4 pi Pi^2
    phi = sp.Function("phi")(t)
    V = sp.Function("V")
    P = sp.Function("P")(t)
    Hf = sp.Function("Hf")(t)
    eps1_expr = 4 * sp.pi * P**2 / Hf**2
    dln = sp.diff(sp.log(eps1_expr), t) / Hf
    dln = dln.subs({sp.Derivative(P, t): -3 * Hf * P - sp.Derivative(V(phi), phi),
                    sp.Derivative(Hf, t): -4 * sp.pi * P**2})
    core_eps2 = 6 + 2 * sp.Derivative(V(phi), phi) / (Hf * P) - 2 * eps1_expr
    res["C2"] = str(sp.simplify(core_eps2 + dln))
    # C3
    W = (1 + sp.tanh(s * sp.log(sig * a * H / k))) / 2
    x = s * sp.log(sig * As * Hs / k)
    sech2 = 1 / sp.cosh(x) ** 2
    dlnks = Hs * (1 - E1)
    d2lnks = Hs**2 * E1 * (E2 - 1 + E1)
    w1 = sp.Rational(1, 2) * s * sech2 * dlnks
    w2 = sp.Rational(1, 2) * sech2 * (s * d2lnks - 2 * s**2 * sp.tanh(x) * dlnks**2)
    Wd = sub(D(W))
    Wdd = sub(D(D(W)))
    res["C3_w1"] = str(sp.simplify((Wd - w1).rewrite(sp.exp)))
    res["C3_w2"] = str(sp.simplify((Wdd - w2).rewrite(sp.exp)))
    # numeric spot check of C3 at random points (guards against a simplify artefact)
    f1 = sp.lambdify((s, sig, k, E1, E2, Hs, As), Wd - w1)
    f2 = sp.lambdify((s, sig, k, E1, E2, Hs, As), Wdd - w2)
    rng = np.random.default_rng(1)
    worst = 0.0
    for _ in range(200):
        pt = (5.0, 1.0, rng.uniform(0.3, 3), rng.uniform(1e-3, 0.3), rng.uniform(-1, 6),
              rng.uniform(0.5, 2), rng.uniform(0.5, 2))
        worst = max(worst, abs(f1(*pt)), abs(f2(*pt)))
    res["C3_numeric_max_abs"] = worst
    # C4: S_R as the source of L[W R] = W L[R] + S_R, L = d2 + (3 - eps2) H d + k^2/a^2
    Rf = sp.Function("R")(t)
    Wf = sp.Function("W")(t)
    L = lambda X: sp.diff(X, t, 2) + (3 - E2) * Hs * sp.diff(X, t) + k**2 / As**2 * X
    SR = sp.expand(L(Wf * Rf) - Wf * L(Rf))
    core_SR = (Rf * sp.diff(Wf, t, 2)
               + (2 * sp.diff(Rf, t) + (3 - E2) * Hs * Rf) * sp.diff(Wf, t))
    res["C4"] = str(sp.simplify(SR - core_SR))
    # C5: linearised constraints in G = 1 units: H = R3 + 2/3 K^2 - A.A - 16 pi rho,
    # M_i = d_j At_ij - 2/3 d_i K - 8 pi J_i; kicks change only Pi, K, At (rho += Pi_b dPi)
    I = sp.symbols("I", real=True)
    dPi = Pi / Hs * I
    dK = -E1 * I
    dH = sp.Rational(4, 3) * (-3 * Hs) * dK - 16 * sp.pi * Pi * dPi
    res["C5_H"] = str(sp.simplify(dH.subs(E1, 4 * sp.pi * Pi**2 / Hs**2)))
    kh = sp.symbols("kh", real=True)
    qsym = sp.Rational(3, 2) * sp.sin(kh) - sp.Rational(3, 10) * sp.sin(2 * kh) \
        + sp.Rational(1, 30) * sp.sin(3 * kh)
    # symbol of the stencil -1/60, 3/20, -3/4, 0, 3/4, -3/20, 1/60: sum c_m exp(i m kh) / i
    c = {1: sp.Rational(3, 4), 2: -sp.Rational(3, 20), 3: sp.Rational(1, 60)}
    stencil = sum(cm * (sp.exp(sp.I * m * kh) - sp.exp(-sp.I * m * kh)) for m, cm in c.items()) / sp.I
    res["C5_stencil_symbol_minus_core"] = str(sp.simplify((stencil - qsym).rewrite(sp.sin)))
    q1, q2, q3 = sp.symbols("q1 q2 q3", real=True)
    qv = sp.Matrix([q1, q2, q3])
    q2s = q1**2 + q2**2 + q3**2
    Pij = sp.eye(3) / 3 - qv * qv.T / q2s
    dM = [sp.simplify(sum(sp.I * qv[j] * E1 * Pij[i, j] * I for j in range(3))
                      - sp.Rational(2, 3) * sp.I * qv[i] * dK) for i in range(3)]
    res["C5_M_stencil_projector"] = str(dM)
    res["C5_trace_Tzz"] = str(sp.simplify(sum(Pij[i, i] for i in range(3))))
    # P1 prefactors in code units: S_Pi/S_R = Pi_b/H = sqrt(2 eps1) Mpl for Pi_b > 0
    res["C5_SPi_vs_P1"] = str(sp.simplify((Pi / Hs - sp.sqrt(2 * 4 * sp.pi * Pi**2 / Hs**2)
                                           * sp.sqrt(1 / (8 * sp.pi)))))
    for kk, v in res.items():
        print(kk, ":", v)

    # figure: residual of the discrete momentum constraint for one kick, per unit eps1 I,
    # relative to |qh| |dK|: stencil projector 0; continuum projector |qh - k (qh.k)/k^2|/|qh|
    def qh(x):
        return 1.5 * np.sin(x) - 0.3 * np.sin(2 * x) + np.sin(3 * x) / 30.0
    xs = np.linspace(0.01, np.pi / 2, 200)
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.17, top=0.9)
    curves = {}
    for d, col in (((1, 1, 1), fs.PAL["red"]), ((1, 2, 0), fs.PAL["blue"]),
                   ((1, 2, 3), fs.PAL["yellow"])):
        n = np.array(d, float) / np.linalg.norm(d)
        r = []
        for x in xs:
            kv = x * n
            qv_ = qh(kv)
            res_v = qv_ - kv * np.dot(qv_, kv) / np.dot(kv, kv)
            r.append(np.linalg.norm(res_v) / np.linalg.norm(qv_))
        curves[str(d)] = r
        ax.semilogy(xs / np.pi, np.maximum(r, 1e-17), color=col, label="continuum, %s" % (d,))
    ax.axhline(1e-16, **fs.GUIDE, label="stencil (core default): 0")
    ax.axvline(0.25, **fs.MASK_LINE)
    ax.set_xlabel(r"$|k|\,dx/\pi$ ($k_{\max}dx=\pi/2$)")
    ax.set_ylabel(r"$|\delta\mathcal{M}|/(|q_h|\,|\delta K|)$")
    ax.set_title("momentum constraint after one kick", fontsize=9)
    ax.legend(fontsize=7)
    fig.savefig(os.path.join(a_.out, "fig_v5_projector.png"))
    res["continuum_projector_residual_at_kmax_111"] = curves["(1, 1, 1)"][-1]
    res["continuum_projector_residual_at_kmax_120"] = curves["(1, 2, 0)"][-1]
    with open(os.path.join(a_.out, "v5.json"), "w") as fh:
        json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
