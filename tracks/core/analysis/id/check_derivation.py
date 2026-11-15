#!/usr/bin/env python3
"""Symbolic check (sympy) of the slice data behind python/nrpic/expanding_ball.py
(item 1 of coord/notes/derivations_to_check.md).  Prints one line per statement and
exits with status 1 if one fails.

Lemaitre-Tolman-Bondi dust, comoving coordinates (tau, r):
    ds^2 = -dtau^2 + R'^2/(1 + 2E(r)) dr^2 + R^2 dOmega^2,   Rdot^2 = 2 m(r)/R + 2 E(r).
"""
import sys

import sympy as sp

tau, r, th, Rs = sp.symbols("tau r theta R", positive=True)
ok = True


def report(name, expr):
    global ok
    z = sp.simplify(expr)
    good = z == 0
    ok &= good
    print(("PASS  " if good else "FAIL  ") + name + ("" if good else f"   residual: {z}"))


# ---- 1. extrinsic curvature of the slices tau = const in comoving coordinates
R = sp.Function("R")(tau, r)
E = sp.Function("E")(r)
gam = sp.diag(R.diff(r) ** 2 / (1 + 2 * E), R ** 2, R ** 2 * sp.sin(th) ** 2)
Kmixed = -(gam.inv() * gam.diff(tau)) / 2          # lapse 1, shift 0: K_ij = -(1/2) d_tau gamma_ij
report("K^r_r = -Rdot'/R'", Kmixed[0, 0] + R.diff(tau).diff(r) / R.diff(r))
report("K^theta_theta = K^phi_phi = -Rdot/R",
       (Kmixed[1, 1] + R.diff(tau) / R) ** 2 + (Kmixed[2, 2] + R.diff(tau) / R) ** 2)
print("      so with v(tau, R) = Rdot along the slice: KT = -v/R, KL = -dv/dR at fixed tau")

# ---- 2. constraints on the slice, areal radius as coordinate
m = sp.Function("m")(Rs)
Es = sp.Function("E")(Rs)
v = sp.sqrt(2 * m / Rs + 2 * Es)
KT = -v / Rs
KL = -v.diff(Rs)
# Ricci scalar of dR^2/(1 + 2E) + R^2 dOmega^2, computed from the metric
x = [Rs, th, sp.Symbol("phi")]
g = sp.diag(1 / (1 + 2 * Es), Rs ** 2, Rs ** 2 * sp.sin(th) ** 2)
gi = g.inv()
Gam = [[[sum(gi[a, d] * (g[d, b].diff(x[c]) + g[d, c].diff(x[b]) - g[b, c].diff(x[d]))
             for d in range(3)) / 2 for c in range(3)] for b in range(3)] for a in range(3)]


def ricci(b, c):
    return sum(Gam[a][b][c].diff(x[a]) - Gam[a][b][a].diff(x[c])
               + sum(Gam[a][a][d] * Gam[d][b][c] - Gam[a][c][d] * Gam[d][b][a] for d in range(3))
               for a in range(3))


Rsc = sp.simplify(sum(gi[b, b] * ricci(b, b) for b in range(3)))
report("(3)R = -4 (E R)'/R^2", Rsc + 4 * (Es * Rs).diff(Rs) / Rs ** 2)
rho = m.diff(Rs) / (4 * sp.pi * Rs ** 2)
report("Hamiltonian constraint with rho = m'/(4 pi R^2)",
       Rsc + (KL + 2 * KT) ** 2 - KL ** 2 - 2 * KT ** 2 - 16 * sp.pi * rho)
# momentum constraint, radial component: D_j K^j_R - d_R K with K^i_j = diag(KL, KT, KT)
Km = sp.diag(KL, KT, KT)
div = sum(Km[j, 0].diff(x[j]) + sum(Gam[j][j][d] * Km[d, 0] - Gam[d][j][0] * Km[j, d]
                                    for d in range(3)) for j in range(3))
report("momentum constraint (S_i = 0): D_j K^j_R - d_R K = 0", div - (KL + 2 * KT).diff(Rs))
report("... equivalent to d KT/d ln R = KL - KT", Rs * KT.diff(Rs) - (KL - KT))

# ---- 3. conformally flat form: psi^4 (drbar^2 + rbar^2 dOmega^2), psi^2 rbar = R
rb = sp.Function("rbar")(Rs)
psi4 = (Rs / rb) ** 2
report("radial part: psi^4 (drbar/dR)^2 = 1/(1 + 2E) when d ln rbar/dR = 1/(R sqrt(1 + 2E))",
       (psi4 * rb.diff(Rs) ** 2).subs(rb.diff(Rs), rb / (Rs * sp.sqrt(1 + 2 * Es))) - 1 / (1 + 2 * Es))

# ---- 4. homogeneous ball and vacuum exterior
M, Rb, e0 = sp.symbols("M R_b e_0", positive=True)
H = sp.sqrt(2 * M / Rb ** 3 - 2 * e0 / Rb ** 2)
sub_in = {m: M * (Rs / Rb) ** 3, Es: -e0 * (Rs / Rb) ** 2}
report("interior: KT = -H", sp.simplify(KT.subs(sub_in).doit()) + H)
report("interior: KL = -H", sp.simplify(KL.subs(sub_in).doit()) + H)
report("interior: rho = 3M/(4 pi R_b^3)", rho.subs(sub_in).doit() - 3 * M / (4 * sp.pi * Rb ** 3))
sub_out = {m: M, Es: 0}
report("marginally bound exterior: KT = -sqrt(2M/R^3)",
       KT.subs(sub_out).doit() + sp.sqrt(2 * M / Rs ** 3))
report("marginally bound exterior: KL = +sqrt(2M/R^3)/2",
       KL.subs(sub_out).doit() - sp.sqrt(2 * M / Rs ** 3) / 2)
report("jump of KL at the surface of the marginally bound ball = 3H/2",
       (KL.subs(sub_out).doit() - KL.subs(sub_in).doit()).subs(e0, 0).subs(Rs, Rb)
       - sp.Rational(3, 2) * H.subs(e0, 0))

# ---- 5. exact evolution
R0, mm = sp.symbols("R_0 m", positive=True)
Rex = (R0 ** sp.Rational(3, 2) + sp.Rational(3, 2) * sp.sqrt(2 * mm) * tau) ** sp.Rational(2, 3)
report("E = 0: R(tau) solves Rdot^2 = 2m/R with R(0) = R_0",
       sp.simplify(Rex.diff(tau) ** 2 - 2 * mm / Rex) ** 2 + (Rex.subs(tau, 0) - R0) ** 2)
eta, Eb = sp.symbols("eta E_b", positive=True)      # E = -E_b
Rc = mm / (2 * Eb) * (1 - sp.cos(eta))
tc = mm / (2 * Eb) ** sp.Rational(3, 2) * (eta - sp.sin(eta))
report("E < 0: the cycloid solves Rdot^2 = 2m/R + 2E",
       sp.simplify((Rc.diff(eta) / tc.diff(eta)) ** 2 - 2 * mm / Rc + 2 * Eb))

sys.exit(0 if ok else 1)
