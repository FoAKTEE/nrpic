#!/usr/bin/env python3
"""Fresh verifier, part 3: six of the seventeen misprints listed in repro/equations/ERRATA.md,
rederived with my own sympy code from the papers' definitions (not from the package's
scripts). Items: E1 (P0:249 linear momentum constraint prefactor), E3 (P0:138 trace-free
operator with delta_ij), E6 (P0:371 delta N), E7 (P0:911 Hddot), E8 (P1:267 V'), E10 (P0:530,
P1:108 Friedmann line in e-folds).

For each item: the printed form and my derived form as expressions; a residual (derived minus
printed) that must be identically zero if the print were right; a numerical instance.

Usage: python errata.py --out DIR
"""
import argparse
import json
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def e7():
    """Hddot with eps_{i+1} = -H^-1 d_t ln eps_i, eps_0 = H (P0:919)."""
    t = sp.symbols("t")
    H = sp.Function("H")(t)
    e1 = -sp.diff(H, t)/H**2
    e2 = -sp.diff(sp.log(e1), t)/H
    Hdd = sp.diff(H, t, 2)
    # express Hddot via e1, e2: solve symbolically by substitution on a test function
    E1, E2, h = sp.symbols("eps1 eps2 H", positive=True)
    printed = 2*E1*(1 - E2/2)*h**3
    derived = E1*(2*E1 + E2)*h**3
    # check derived identity on a generic H(t) = polynomial with exp
    Ht = sp.exp(-t**2/7) + 2 + sp.sin(t)/5
    sub = {H: Ht}
    lhs = Hdd.subs(sub).doit()
    e1v = e1.subs(sub).doit()
    e2v = e2.subs(sub).doit()
    rhs_der = (e1v*(2*e1v + e2v)*Ht**3)
    rhs_pr = (2*e1v*(1 - e2v/2)*Ht**3)
    vals = []
    for tv in (0.3, 1.1, 2.0):
        vals.append((float(lhs.subs(t, tv)), float(rhs_der.subs(t, tv)), float(rhs_pr.subs(t, tv))))
    ok_der = all(abs(a - b) < 1e-12*max(1, abs(a)) for a, b, _ in vals)
    ok_pr = all(abs(a - c) < 1e-12*max(1, abs(a)) for a, _, c in vals)
    return dict(item="E7", locator="P0:911", printed=str(printed), derived=str(derived),
                residual=str(sp.simplify(derived - printed)), derived_holds=ok_der,
                printed_holds=ok_pr, instance=vals)


def e8():
    """V'(phi_b) from Klein-Gordon and the definitions eps1 = phidot^2/(2 M^2 H^2),
    eps2 = -dln eps1/(H dt)."""
    t = sp.symbols("t")
    M = sp.symbols("M", positive=True)
    phi = sp.Function("phi")(t)
    H = sp.Function("H")(t)
    e1 = sp.diff(phi, t)**2/(2*M**2*H**2)
    e2 = -sp.diff(sp.log(e1), t)/H
    Vp = -3*H*sp.diff(phi, t) - sp.diff(phi, t, 2)       # Klein-Gordon
    derived = (-3 + e1 + e2/2)*H*sp.diff(phi, t)
    printed = (-3 + e1 + e2/2)*H/sp.diff(phi, t)
    # Hdot = -eps1 H^2 is the Friedmann-Raychaudhuri relation; impose it
    rel = {sp.diff(H, t): -e1*H**2}
    r_der = sp.simplify((derived - Vp).subs(rel))
    r_pr = sp.simplify((printed - Vp).subs(rel))
    return dict(item="E8", locator="P1:267 (and P0:914)", printed="(-3+eps1+eps2/2) H phidot^-1",
                derived="(-3+eps1+eps2/2) H phidot", residual_derived=str(r_der),
                residual_printed=str(r_pr), derived_holds=(r_der == 0), printed_holds=(r_pr == 0))


def e10():
    """Friedmann equation in e-folds: 3 M^2 H^2 = phidot^2/2 + V with phidot = H pi."""
    H, V, M, p = sp.symbols("H V M pi", positive=True)
    fried = sp.Eq(3*M**2*H**2, H**2*p**2/2 + V)
    sol = sp.solve(fried, H**2)[0]
    printed = V/(1 - p**2/(6*M**2))
    derived = V/(3*M**2*(1 - p**2/(6*M**2)))
    return dict(item="E10", locator="P0:530, P0:710, P1:108", solved=str(sp.simplify(sol)),
                printed=str(printed), derived=str(derived),
                derived_holds=sp.simplify(sol - derived) == 0,
                printed_holds=sp.simplify(sol - printed) == 0,
                printed_over_solved=str(sp.simplify(printed/sol)))


def e6():
    """delta N = (1/6) delta ln det(gamma) for gamma_ij = a^2[(1-2Phi) delta_ij + 2 E_,ij]
    (P0:178-181), plane wave E ~ exp(i k x): E_,ij -> -k_i k_j E."""
    Phi, E, k, eps = sp.symbols("Phi E k epsilon")
    kv = sp.Matrix([k, 0, 0])
    g = sp.eye(3)*(1 - 2*eps*Phi) + 2*eps*(-kv*kv.T)*E       # a^2 factored out
    dN = sp.series(sp.log(g.det())/6, eps, 0, 2).removeO().coeff(eps)
    printed = Phi + k**2*E/3
    return dict(item="E6", locator="P0:371", derived=str(sp.simplify(dN)), printed=str(printed),
                derived_equals_minus_printed=sp.simplify(dN + printed) == 0,
                printed_holds=sp.simplify(dN - printed) == 0)


def e3():
    """Trace of alpha_|i|j - (1/3) alpha^|k_|k X_ij with gamma_ij = a^2 delta_ij (background):
    with X = delta the trace is (1 - 1/a^2) D^2 alpha, with X = gamma it is zero."""
    x, y, z, a = sp.symbols("x y z a", positive=True)
    X = (x, y, z)
    al = sp.Function("alpha")(x, y, z)
    g = a**2*sp.eye(3)
    gi = g.inv()
    # Christoffels vanish for constant a on the slice
    DD = sp.Matrix(3, 3, lambda i, j: sp.diff(al, X[i], X[j]))
    lap = sum(gi[i, j]*DD[i, j] for i in range(3) for j in range(3))
    tr_delta = sp.simplify(sum(gi[i, j]*(DD[i, j] - lap/3*sp.eye(3)[i, j])
                               for i in range(3) for j in range(3)))
    tr_gamma = sp.simplify(sum(gi[i, j]*(DD[i, j] - lap/3*g[i, j])
                               for i in range(3) for j in range(3)))
    return dict(item="E3", locator="P0:138 (also P0:656, P1:346 per the list)",
                trace_with_delta=str(tr_delta), trace_with_gamma=str(tr_gamma),
                printed_tracefree=(tr_delta == 0), corrected_tracefree=(tr_gamma == 0))


def e1():
    """Linear momentum constraint from the full ADM one, D_j K^j_i - D_i K = M^-2 J_i with
    J_i = -(phidot/alpha) d_i dphi (P0:150-160), K_ij = -(1/2 alpha)(dt gamma_ij + D_i beta_j +
    D_j beta_i) (P0:122), metric P0:178-181 with plane waves along x. Compare the linear part
    with -2 d_x[Delta chi + kappa - (3/2) M^-2 phidot dphi] (printed prefactor, P0:249) and with
    -(2/3) d_x[...] (claimed)."""
    t, x, y, z, eps, M = sp.symbols("t x y z epsilon M", real=True)
    a = sp.Function("a")(t)
    ab = sp.Function("alpha_b")(t)
    Phi = sp.Function("Phi")(t, x)
    Psi = sp.Function("Psi")(t, x)
    B = sp.Function("B")(t, x)
    E = sp.Function("E")(t, x)
    phib = sp.Function("phi_b")(t)
    dphi = sp.Function("dphi")(t, x)
    X = (x, y, z)
    gam = a**2*((1 - 2*eps*Phi)*sp.eye(3))
    gam[0, 0] += a**2*2*eps*sp.diff(E, x, 2)
    alpha = ab*(1 + eps*Psi)
    beta_low = sp.Matrix([-a**2*eps*sp.diff(B, x), 0, 0])
    gi = gam.inv()

    def lin(e):
        return e.subs(eps, 0) + eps*sp.diff(e, eps).subs(eps, 0)
    gi = gi.applyfunc(lin)
    Gam = [[[lin(sum(gi[k, l]*(sp.diff(gam[l, i], X[j]) + sp.diff(gam[l, j], X[i]) -
                                sp.diff(gam[i, j], X[l]))/2 for l in range(3)))
             for j in range(3)] for i in range(3)] for k in range(3)]
    Db = sp.Matrix(3, 3, lambda i, j: sp.diff(beta_low[j], X[i]) -
                   sum(Gam[k][i][j]*beta_low[k] for k in range(3)))
    Kl = sp.Matrix(3, 3, lambda i, j: lin(-(sp.diff(gam[i, j], t) + Db[i, j] + Db[j, i])/(2*alpha)))
    Kmix = (gi*Kl).applyfunc(lin)              # K^i_j
    K = lin(sum(Kmix[i, i] for i in range(3)))
    # D_j K^j_i for a mixed tensor
    i = 0
    div = sum(sp.diff(Kmix[j, i], X[j]) for j in range(3))
    div += sum(Gam[j][j][k]*Kmix[k, i] for j in range(3) for k in range(3))
    div -= sum(Gam[k][j][i]*Kmix[j, k] for j in range(3) for k in range(3))
    phidot = sp.diff(phib, t)
    J = -(phidot/ab)*eps*sp.diff(dphi, x)
    lhs = lin(div - sp.diff(K, x))
    first = sp.simplify(lhs.coeff(eps))
    Jfirst = J.coeff(eps)
    chi = -(a**2/ab)*(B - sp.diff(E, t))
    Delta = lambda f: sp.diff(f, x, 2)/a**2   # noqa: E731
    H = sp.diff(a, t)/(a*ab)
    kappa = 3*(sp.diff(Phi, t)/ab + H*Psi) - Delta(chi)
    bracket = Delta(chi) + kappa
    # the constraint: first - M^-2 Jfirst = 0. Test which prefactor c gives
    # first - M^-2 Jfirst == c d_x[bracket - (3/2) M^-2 phidot/ab dphi]
    target = sp.diff(bracket - sp.Rational(3, 2)/M**2*phidot/ab*dphi, x)
    resid23 = sp.simplify(sp.expand(first - Jfirst/M**2 - sp.Rational(-2, 3)*target))
    resid2 = sp.simplify(sp.expand(first - Jfirst/M**2 - (-2)*target))
    return dict(item="E1", locator="P0:249 (also P1:610 per the list)",
                residual_with_minus_2_over_3=str(resid23), residual_with_minus_2=str(resid2),
                derived_prefactor_minus_2_over_3=(resid23 == 0),
                printed_prefactor_minus_2_holds=(resid2 == 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = []
    for f in (e7, e8, e10, e6, e3, e1):
        r = f()
        res.append(r)
        print(json.dumps(r, default=str), flush=True)
    with open(os.path.join(a.out, "errata.json"), "w") as fo:
        json.dump(res, fo, indent=1, default=str)
    # figure: derived form holds / printed form holds per item
    figstyle.use_style()
    fig, ax = plt.subplots(figsize=(figstyle.COLUMN_WIDTH, 2.2))
    items = [r["item"] for r in res]
    der = [bool(r.get("derived_holds", r.get("derived_equals_minus_printed",
                                             r.get("corrected_tracefree",
                                                   r.get("derived_prefactor_minus_2_over_3")))))
           for r in res]
    pr = [bool(r.get("printed_holds", r.get("printed_tracefree",
                                            r.get("printed_prefactor_minus_2_holds")))) for r in res]
    for j, (d, p) in enumerate(zip(der, pr)):
        ax.scatter([j], [1], marker="o" if d else "x", s=60, color=figstyle.SERIES[0])
        ax.scatter([j], [0], marker="o" if p else "x", s=60, color=figstyle.SERIES[1])
    ax.set_xticks(range(len(items)))
    ax.set_xticklabels(items)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["printed form", "my derivation"])
    ax.set_ylim(-0.6, 1.6)
    ax.set_title("o: identity holds, x: fails", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_errata.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
