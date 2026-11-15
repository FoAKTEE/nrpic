#!/usr/bin/env python3
"""3+1 checks on the slice tau = const of the dust ball (DERIVATION.md, section 3), sympy.

(c) Extrinsic curvature from the (tau, R) metric, code sign
    K_ij = -(1/(2 alpha)) (d_tau gamma_ij - D_i beta_j - D_j beta_i), alpha = 1, beta^R = -v,
    gamma_RR = 1/(1+2E) with E advected: K^R_R = -dv/dR, K^theta_theta = -v/R. Dropping
    d_tau gamma_RR (a static-metric shortcut) gives K^R_R = -v' + v E'/(1+2E), which is wrong.
(d) Hamiltonian and momentum constraints in areal coordinates for arbitrary m(R), E(R).
(d') Homogeneous ball and vacuum exterior, as in coord/notes/derivations_to_check.md item 1.
(e) Conformally flat form and the Cartesian assembly of table format 2: at two generic
    points the Cartesian constraints equal the radial ones.
(f) Null expansions theta_pm = (2/R)(v pm sqrt(1+2E)); theta_+ theta_- = (4/R^2)(2m/R - 1);
    g^ab d_a R d_b R = 1 - 2m/R.

Run: python3 sym_slice.py  (exit status 0 when every check passes)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from geom import christoffel, ricci  # noqa: E402

PASS = []


def check(name, expr):
    e = sp.simplify(expr)
    ok = (e == 0)
    PASS.append(ok)
    print(f"[{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f": remainder {e}"))
    return ok


th, ph = sp.symbols("theta phi", positive=True)
tau, R = sp.symbols("tau R", positive=True)


def part_c():
    m = sp.Function("m")(tau, R)
    E = sp.Function("E")(tau, R)
    v = sp.sqrt(2 * m / R + 2 * E)
    f = 1 + 2 * E
    X = [R, th, ph]
    gam = sp.diag(1 / f, R ** 2, R ** 2 * sp.sin(th) ** 2)
    gi, Gam = christoffel(gam, X)
    beta_up = sp.Matrix([-v, 0, 0])
    beta_dn = gam * beta_up
    Dbeta = sp.zeros(3, 3)
    for i in range(3):
        for j in range(3):
            Dbeta[i, j] = sp.diff(beta_dn[j], X[i]) - sum(Gam[k][i][j] * beta_dn[k]
                                                          for k in range(3))
    adv = {sp.diff(E, tau): -v * sp.diff(E, R), sp.diff(m, tau): -v * sp.diff(m, R)}
    dtgam = gam.applyfunc(lambda x: sp.diff(x, tau).xreplace(adv))
    K = -(dtgam - Dbeta - Dbeta.T) / 2
    Kmix = gi * K
    dvdR = sp.diff(v, R)        # total derivative along the slice: m and E depend on R
    check("(c) K^R_R = -dv/dR (E and m depend on R at fixed tau)", Kmix[0, 0] + dvdR)
    check("(c) K^theta_theta = -v/R", Kmix[1, 1] + v / R)
    check("(c) K^phi_phi = -v/R", Kmix[2, 2] + v / R)
    check("(c) K^R_theta = 0", Kmix[0, 1])
    Knaive = gi * (-(-Dbeta - Dbeta.T) / 2)
    wrong = -dvdR + v * sp.diff(E, R) / f
    check("(c) the static shortcut (d_tau gamma dropped) gives -v' + v E'/(1+2E) instead",
          Knaive[0, 0] - wrong)
    print("    difference shortcut - correct =", sp.simplify(Knaive[0, 0] - Kmix[0, 0]))


def slice_constraints(m, E, X):
    """Hamiltonian and momentum residuals for the slice data built from m(R), E(R)."""
    v = sp.sqrt(2 * m / R + 2 * E)
    f = 1 + 2 * E
    gam = sp.diag(1 / f, R ** 2, R ** 2 * sp.sin(th) ** 2)
    gi, Gam, Ric, Rs = ricci(gam, X)
    KL = -sp.diff(v, R)
    KT = -v / R
    Kmix = sp.diag(KL, KT, KT)
    trK = KL + 2 * KT
    KK = sum(Kmix[i, j] * Kmix[j, i] for i in range(3) for j in range(3))
    rho = sp.diff(m, R) / (4 * sp.pi * R ** 2)
    Ham = Rs + trK ** 2 - KK - 16 * sp.pi * rho
    Mom = []
    for i in range(3):
        s = 0
        for j in range(3):
            s += sp.diff(Kmix[j, i], X[j])
            for k in range(3):
                s += Gam[j][j][k] * Kmix[k, i] - Gam[k][j][i] * Kmix[j, k]
        Mom.append(s - sp.diff(trK, X[i]))
    return Ham, Mom, Rs, KL, KT


def part_d():
    X = [R, th, ph]
    m = sp.Function("m")(R)
    E = sp.Function("E")(R)
    Ham, Mom, Rs, KL, KT = slice_constraints(m, E, X)
    check("(d) 3R = -4 (R E)'/R^2", Rs + 4 * sp.diff(R * E, R) / R ** 2)
    check("(d) Hamiltonian constraint, arbitrary m(R), E(R)", Ham)
    for i in range(3):
        check(f"(d) momentum constraint, component {i}", Mom[i])
    # homogeneous marginally bound ball and vacuum exterior
    H, M = sp.symbols("H M", positive=True)
    Ham, Mom, Rs, KL, KT = slice_constraints(H ** 2 * R ** 3 / 2, sp.Integer(0), X)
    check("(d') ball: KL = -H", KL + H)
    check("(d') ball: KT = -H", KT + H)
    check("(d') ball: K^2 - K_ij K^ij = 6 H^2 = 16 pi rho", Ham)
    Ham, Mom, Rs, KL, KT = slice_constraints(M, sp.Integer(0), X)
    v = sp.sqrt(2 * M / R)
    check("(d') vacuum: KL = +v/(2R)", KL - v / (2 * R))
    check("(d') vacuum: KT = -v/R", KT + v / R)
    check("(d') vacuum: Hamiltonian constraint", Ham)
    check("(d') vacuum: momentum constraint (radial)", Mom[0])


def part_e():
    # conformal map: R = psi^2 rbar with d rbar/dR = rbar/(R sqrt(1+2E))
    rb = sp.symbols("rbar", positive=True)
    Rf = sp.Function("Rf")(rb)
    E = sp.Function("E")(rb)
    dRdrb = Rf * sp.sqrt(1 + 2 * E) / rb
    psi4 = (Rf / rb) ** 2
    check("(e) dR^2/(1+2E) = psi^4 drbar^2 with psi^2 = R/rbar", dRdrb ** 2 / (1 + 2 * E) - psi4)
    check("(e) R^2 dOmega^2 = psi^4 rbar^2 dOmega^2", Rf ** 2 - psi4 * rb ** 2)
    # Cartesian assembly at two generic points with rational unit vectors
    x, y, z = sp.symbols("x y z", real=True)
    r0 = sp.symbols("r0", positive=True)
    p0, p1, p2, l0, l1, k0, k1 = sp.symbols("p0 p1 p2 l0 l1 k0 k1", real=True)
    rr = sp.sqrt(x ** 2 + y ** 2 + z ** 2)
    s = rr - r0
    psi = p0 + p1 * s + p2 * s ** 2 / 2
    KL = l0 + l1 * s
    KT = k0 + k1 * s
    Xc = [x, y, z]
    n = [x / rr, y / rr, z / rr]
    gam = sp.eye(3) * psi ** 4
    Kdn = sp.Matrix(3, 3, lambda i, j: psi ** 4 * (KT * (1 if i == j else 0)
                                                    + (KL - KT) * n[i] * n[j]))
    gi, Gam, Ric, Rs = ricci(gam, Xc, simp=lambda e: e)
    Kmix = gi * Kdn
    trK = sum(Kmix[i, i] for i in range(3))
    KK = sum(Kmix[i, j] * Kmix[j, i] for i in range(3) for j in range(3))
    Ham = Rs + trK ** 2 - KK
    Mom = []
    for i in range(3):
        sm = 0
        for j in range(3):
            sm += sp.diff(Kmix[j, i], Xc[j])
            for k in range(3):
                sm += Gam[j][j][k] * Kmix[k, i] - Gam[k][j][i] * Kmix[j, k]
        Mom.append(sm - sp.diff(trK, Xc[i]))
    # radial forms (rbar the radius): 3R = -8 psi^-5 (psi'' + 2 psi'/rbar)
    Ham_rad = -8 / p0 ** 5 * (p2 + 2 * p1 / r0) + 4 * l0 * k0 + 2 * k0 ** 2
    Mrad = 2 * ((1 / r0 + 2 * p1 / p0) * (l0 - k0) - k1)
    for pt in [(2, 3, 6, 7), (1, 4, 8, 9)]:
        sub = {x: sp.Rational(pt[0], pt[3]) * r0, y: sp.Rational(pt[1], pt[3]) * r0,
               z: sp.Rational(pt[2], pt[3]) * r0}
        nv = [sp.Rational(c, pt[3]) for c in pt[:3]]
        check(f"(e) Cartesian Hamiltonian = radial form at n = {pt[:3]}/{pt[3]}",
              Ham.subs(sub) - Ham_rad)
        for i in range(3):
            check(f"(e) Cartesian momentum_{i} = n_i x radial form at n = {pt[:3]}/{pt[3]}",
                  Mom[i].subs(sub) - nv[i] * Mrad)
        # K^i_j n^j = KL n^i, trace = KL + 2 KT
        Kn = Kmix.subs(sub) * sp.Matrix(nv)
        check(f"(e) K^i_j n^j = KL n^i at n = {pt[:3]}/{pt[3]}",
              sum((Kn[i] - l0 * nv[i]) ** 2 for i in range(3)))
        check(f"(e) trace K = KL + 2 KT at n = {pt[:3]}/{pt[3]}", trK.subs(sub) - l0 - 2 * k0)
    # areal form of the momentum constraint: dKT/dR = (KL - KT)/R, with R = psi^2 rbar
    # => dKT/drbar = (KL - KT) (1/rbar + 2 psi'/psi): Mrad = 0 is exactly that.


def part_f():
    m = sp.Function("m")(R)
    E = sp.Function("E")(R)
    v = sp.sqrt(2 * m / R + 2 * E)
    f = 1 + 2 * E
    sqrtg = R ** 2 * sp.sin(th) / sp.sqrt(f)
    sR = sp.sqrt(f)
    divs = sp.diff(sqrtg * sR, R) / sqrtg
    KT = -v / R
    KL = -sp.diff(v, R)
    trK = KL + 2 * KT
    Kss = KL
    thp = divs - trK + Kss
    thm = -divs - trK + Kss
    check("(f) theta_+ = (2/R)(v + sqrt(1+2E))", thp - 2 * (v + sp.sqrt(f)) / R)
    check("(f) theta_- = (2/R)(v - sqrt(1+2E))", thm - 2 * (v - sp.sqrt(f)) / R)
    check("(f) theta_+ theta_- = (4/R^2)(2m/R - 1)", thp * thm - 4 * (2 * m / R - 1) / R ** 2)
    # invariant g^ab d_a R d_b R from the 4-metric of the (tau, R) form
    mt = sp.Function("m")(tau, R)
    Et = sp.Function("E")(tau, R)
    vt = sp.sqrt(2 * mt / R + 2 * Et)
    ft = 1 + 2 * Et
    g = sp.Matrix([[-1 + vt ** 2 / ft, -vt / ft], [-vt / ft, 1 / ft]])
    gi = sp.simplify(g.inv())
    check("(f) g^RR = 1 - 2m/R (Misner-Sharp mass)", gi[1, 1] - (1 - 2 * mt / R))
    # flat FLRW sanity check of the sign convention: K_ij = -H gamma_ij
    Hs = sp.symbols("H", positive=True)
    check("(f) FLRW: theta_- = 2(HR - 1)/R, anti-trapped beyond the Hubble radius",
          (-2 / R + 2 * Hs) - 2 * (Hs * R - 1) / R)


if __name__ == "__main__":
    part_c()
    part_d()
    part_f()
    part_e()
    print(f"{sum(PASS)}/{len(PASS)} checks passed")
    sys.exit(0 if all(PASS) else 1)
