#!/usr/bin/env python3
"""S5: Lemaitre-Tolman-Bondi dust, conservation of the Misner-Sharp mass along dust
world lines (hence inside the comoving wall), the wall trajectory, the slice of constant
dust proper time in areal coordinates (KT, KL of the dust region), and the join
conditions at the wall.

Run: python3 sym/s3_ltb_wall.py
"""
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tensors import einstein_mixed, check_zero  # noqa: E402

tau, r, th, ph = sp.symbols("tau r theta phi", real=True)
X = [tau, r, th, ph]
Rf = sp.Function("R")(tau, r)
E = sp.Function("E")(r)
Rr = sp.diff(Rf, r)
g = sp.diag(-1, Rr ** 2 / (1 + 2 * E), Rf ** 2, Rf ** 2 * sp.sin(th) ** 2)
Gm, _ = einstein_mixed(g, X)
Rd, Rdd = sp.diff(Rf, tau), sp.diff(Rf, tau, 2)
check_zero(Gm[0, 1], "LTB: G^tau_r = 0 identically (E = E(r))")
check_zero(Gm[1, 0], "LTB: G^r_tau = 0 identically")
check_zero(Gm[1, 1] + (2 * Rf * Rdd + Rd ** 2 - 2 * E) / Rf ** 2,
           "LTB: G^r_r = -(2 R Rddot + Rdot^2 - 2E)/R^2")
# Misner-Sharp mass m = (R/2)(1 - g^ab d_a R d_b R)
gi = g.inv()
grad2 = sum(gi[a, b] * sp.diff(Rf, X[a]) * sp.diff(Rf, X[b]) for a in range(2) for b in range(2))
m = sp.simplify(Rf / 2 * (1 - grad2))
check_zero(m - Rf / 2 * (Rd ** 2 - 2 * E), "Misner-Sharp mass m = (R/2)(Rdot^2 - 2E)")
check_zero(sp.diff(m, tau) + Rf ** 2 * Rd / 2 * Gm[1, 1],
           "d m/d tau = -(R^2 Rdot/2) G^r_r  = -4 pi R^2 Rdot p_r")
check_zero(sp.diff(m, r) + Rf ** 2 * Rr / 2 * Gm[0, 0],
           "d m/d r = -(R^2 R_r/2) G^tau_tau = 4 pi R^2 R_r rho")
print("   => dust (p_r = 0): m = m(r) is constant along every dust world line; the mass inside")
print("      the innermost dust shell (the comoving wall) is constant, and by Birkhoff the")
print("      vacuum bubble inside is Schwarzschild with that mass, M = m(r_wall), for all tau")
print("      before shell crossing. (Also Hayward: u^a grad_a m = 4 pi R^2 (T_a^b - delta T) u^a grad_b R = 0 for dust.)")

# wall trajectory (marginally bound, E = 0): Rdot^2 = 2M/R
Mw, R0 = sp.symbols("M R_0", positive=True)
Rw = (R0 ** sp.Rational(3, 2) + sp.Rational(3, 2) * sp.sqrt(2 * Mw) * tau) ** sp.Rational(2, 3)
check_zero(sp.simplify(sp.diff(Rw, tau) ** 2 - 2 * Mw / Rw), "R_w(tau) = (R_0^(3/2) + (3/2) sqrt(2M) tau)^(2/3) solves Rdot^2 = 2M/R")
check_zero(sp.simplify(Rw.subs(tau, 0) - R0), "R_w(0) = R_0")
# bound shell (E < 0) and its parametric solution: used for tracers inside the transition
eta, A, B = sp.symbols("eta A B", positive=True)
Ec = sp.symbols("E_c", negative=True)
mc = sp.symbols("m_c", positive=True)
Rpar = mc / (-2 * Ec) * (1 - sp.cos(eta))
tpar = mc / (-2 * Ec) ** sp.Rational(3, 2) * (eta - sp.sin(eta))
check_zero(sp.simplify((sp.diff(Rpar, eta) / sp.diff(tpar, eta)) ** 2 - (2 * mc / Rpar + 2 * Ec)),
           "bound radial geodesic: R = m(1 - cos eta)/(-2E), tau = m (eta - sin eta)/(-2E)^(3/2)")

# ---------------------------------------------------------------- slice tau = const in areal coordinates
# ds^2 = -dtau^2 + (dR - v dtau)^2 + R^2 dOmega^2 (E = 0): lapse 1, shift beta^R = -v, flat 3-metric
Rs = sp.symbols("R", positive=True)
v = sp.Function("v")(tau, Rs)
gam = sp.diag(1, Rs ** 2, Rs ** 2 * sp.sin(th) ** 2)
beta_up = sp.Matrix([-v, 0, 0])
x3 = [Rs, th, ph]
from tensors import christoffel  # noqa: E402
G3 = christoffel(gam, x3)
beta_lo = gam * beta_up


def Dbeta(i, j):
    return sp.diff(beta_lo[j], x3[i]) - sum(G3[k][i][j] * beta_lo[k] for k in range(3))


Kdd = sp.Matrix(3, 3, lambda i, j: sp.Rational(1, 2) * (Dbeta(i, j) + Dbeta(j, i)))  # alpha = 1, d_t gamma = 0
check_zero(Kdd[0, 0] + sp.diff(v, Rs), "dust slice: K_RR = -dv/dR  (KL = -v')")
check_zero(Kdd[1, 1] / Rs ** 2 + v / Rs, "dust slice: K^theta_theta = -v/R  (KT = -v/R)")
check_zero(sp.diff(Rs * (-v / Rs), Rs) + sp.diff(v, Rs), "dust slice obeys KL = d(R KT)/dR")
# Hamiltonian constraint on the flat slice: 4 KL KT + 2 KT^2 = 16 pi rho with v^2 = 2 m(R)/R
mR = sp.Function("m")(Rs)
vv = sp.sqrt(2 * mR / Rs)
KLd, KTd = -sp.diff(vv, Rs), -vv / Rs
check_zero(sp.simplify(4 * KLd * KTd + 2 * KTd ** 2 - 4 * sp.diff(mR, Rs) / Rs ** 2),
           "dust slice: 4 KL KT + 2 KT^2 = 4 m'(R)/R^2 = 16 pi rho  with rho = m'/(4 pi R^2)")
# PG vacuum, m = M: KL = +v/(2R) = -KT/2
check_zero(sp.simplify(KLd.subs(mR, Mw).doit() - sp.sqrt(2 * Mw / Rs) / (2 * Rs)), "vacuum PG: KL = +sqrt(2M/R)/(2R) = -KT/2")
# homogeneous EdS: m = (4 pi/3) rho0 R^3 -> KL = KT = -H, H^2 = 8 pi rho0/3
rho0 = sp.symbols("rho_0", positive=True)
H = sp.sqrt(8 * sp.pi * rho0 / 3)
check_zero(sp.simplify(KLd.subs(mR, 4 * sp.pi * rho0 * Rs ** 3 / 3).doit() + H), "EdS: KL = -H")
check_zero(sp.simplify(KTd.subs(mR, 4 * sp.pi * rho0 * Rs ** 3 / 3).doit() + H), "EdS: KT = -H")
# Einstein-Straus matching (sharp wall at R_w): m continuous -> M = (4 pi/3) rho0 R_w^3, i.e. H^2 R_w^3 = 2M;
# KT continuous; KL jumps by -(3/2) H (= 4 pi rho0 / KT)
Rwall = sp.symbols("R_w", positive=True)
Hsub = sp.sqrt(2 * Mw / Rwall ** 3)
jump = (-Hsub) - sp.sqrt(2 * Mw / Rwall) / (2 * Rwall)
check_zero(sp.simplify(jump + sp.Rational(3, 2) * Hsub), "sharp wall: [KL] = -(3/2) H, KT continuous (= -H)")
check_zero(sp.simplify(4 * sp.pi * (3 * Hsub ** 2 / (8 * sp.pi)) / (-Hsub) - jump),
           "sharp wall: [KL] = 4 pi rho0 / KT  (jump condition from the Hamiltonian constraint)")
print("ALL S5 CHECKS PASSED")
