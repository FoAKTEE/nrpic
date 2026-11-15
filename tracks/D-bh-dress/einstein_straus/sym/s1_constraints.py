#!/usr/bin/env python3
"""S1: spherically symmetric constraints in the variables KT, KL; Misner-Sharp mass;
conformally flat form; time-symmetric (puncture) region; throat.

Run: python3 sym/s1_constraints.py   (prints [OK]/[FAIL] per identity; exits nonzero on FAIL)
"""
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tensors import ricci_scalar, covdiv_mixed, check_zero, christoffel  # noqa: E402

l, th, ph = sp.symbols("l theta phi", real=True)
x = [l, th, ph]
R = sp.Function("R")(l)
KL = sp.Function("K_L")(l)
KT = sp.Function("K_T")(l)
rho = sp.Function("rho")(l)
Sl = sp.Function("S_l")(l)        # radial momentum density (covariant, proper-length basis)

# ---------------------------------------------------------------- 3-metric dl^2 + R^2 dOmega^2
g = sp.diag(1, R ** 2, R ** 2 * sp.sin(th) ** 2)
Rs3, Ric, G = ricci_scalar(g, x)
Rp, Rpp = sp.diff(R, l), sp.diff(R, l, 2)
check_zero(Rs3 - 2 * (1 - Rp ** 2 - 2 * R * Rpp) / R ** 2,
           "3-Ricci scalar of dl^2 + R^2 dOmega^2 = (2/R^2)(1 - R'^2 - 2 R R'')")

Km = sp.diag(KL, KT, KT)                       # K^i_j
K = KL + 2 * KT
KK = KL ** 2 + 2 * KT ** 2                     # K^i_j K^j_i
Ham = Rs3 + K ** 2 - KK - 16 * sp.pi * rho     # Hamiltonian constraint (= 0)
check_zero(K ** 2 - KK - (4 * KL * KT + 2 * KT ** 2), "K^2 - K_ij K^ij = 4 KL KT + 2 KT^2")

div = covdiv_mixed(Km, G, x)                   # D_j K^j_i
Mom = [sp.simplify(div[i] - sp.diff(K, x[i])) for i in range(3)]   # D_j K^j_i - D_i K
check_zero(Mom[1], "momentum constraint, theta component vanishes identically")
check_zero(Mom[2], "momentum constraint, phi component vanishes identically")
check_zero(Mom[0] - (2 * (KL - KT) * Rp / R - 2 * sp.diff(KT, l)),
           "momentum constraint, radial: D_j K^j_l - D_l K = 2[(KL - KT) R'/R - KT']")
MomEq = Mom[0] - 8 * sp.pi * Sl                # = 0
print("   => vacuum or S_i = 0:  dKT/dl = (KL - KT) R'/R,  i.e. dKT/dlnR = KL - KT,"
      "  KL = d(R KT)/dR")

# ---------------------------------------------------------------- Misner-Sharp mass
# m = (R/2)(1 - g^{ab} d_a R d_b R) with d_n R = Lie_n R = -R KT  (K_ij = -(1/2) Lie_n gamma_ij)
m = R / 2 * (1 - Rp ** 2 + R ** 2 * KT ** 2)
dm = sp.diff(m, l)
# claim: dm/dl = 4 pi R^2 (rho R' - S_l R KT) + (R^2 R'/4) Ham - (R^3 KT/2)... find the exact
# linear combination with undetermined multipliers and check it is identically satisfied
a1, a2 = sp.symbols("a1 a2")
target = 4 * sp.pi * R ** 2 * (rho * Rp - Sl * R * KT)
expr = sp.expand(dm - target - a1 * Ham - a2 * MomEq)
# solve for a1, a2 from coefficients of R'' and KT'
sol = sp.solve([sp.expand(expr).coeff(Rpp), sp.expand(expr).coeff(sp.diff(KT, l))], [a1, a2], dict=True)[0]
print("   multipliers:", sol)
check_zero(expr.subs(sol), "dm/dl = 4 pi R^2 (rho R' - S_l R KT) + a1 Ham + a2 Mom (identity)")
check_zero(sol[a1] - R ** 2 * Rp / 4, "a1 = R^2 R'/4")
check_zero(sol[a2] + R ** 3 * KT / 2, "a2 = -R^3 KT/2")
print("   => with S_l = 0: dm/dR = 4 pi R^2 rho (where R' != 0); vacuum: m constant;"
      "  and (dR/dl)^2 = 1 - 2m/R + R^2 KT^2 (definition of m)")

# ---------------------------------------------------------------- conformally flat form
rb = sp.symbols("rbar", positive=True)
psi = sp.Function("psi")(rb)
gc = sp.diag(psi ** 4, psi ** 4 * rb ** 2, psi ** 4 * rb ** 2 * sp.sin(th) ** 2)
Rs3c, _, Gc = ricci_scalar(gc, [rb, th, ph])
check_zero(Rs3c + 8 * psi ** -5 * (sp.diff(psi, rb, 2) + 2 * sp.diff(psi, rb) / rb),
           "conformally flat: (3)R = -8 psi^-5 Laplacian(psi)")
# areal radius and proper length
Rc = psi ** 2 * rb
dl_drb = psi ** 2
W = sp.diff(Rc, rb) / dl_drb                   # dR/dl
check_zero(W - (1 + 2 * rb * sp.diff(psi, rb) / psi), "dR/dl = 1 + 2 dln psi/dln rbar")
print("   => d ln R / d ln rbar = dR/dl =: W(R), so ln rbar = int dR/(R W(R)) on the sheet"
      " where R grows outward")
# the momentum constraint in rbar: d KT/d rbar = (KL - KT) d ln R/d rbar
KLc, KTc = sp.Function("K_L")(rb), sp.Function("K_T")(rb)
Kmc = sp.diag(KLc, KTc, KTc)
divc = covdiv_mixed(Kmc, Gc, [rb, th, ph])
Momc = sp.simplify(divc[0] - sp.diff(KLc + 2 * KTc, rb))
check_zero(Momc - 2 * ((KLc - KTc) * sp.diff(sp.log(Rc), rb) - sp.diff(KTc, rb)),
           "momentum constraint in rbar: 2[(KL - KT)(1/rbar + 2 psi'/psi) - KT']")

# ---------------------------------------------------------------- time-symmetric vacuum region
a, b, M = sp.symbols("a b M", positive=True)
psi0 = a + b / rb
check_zero(sp.diff(psi0, rb, 2) + 2 * sp.diff(psi0, rb) / rb, "psi = a + b/rbar is harmonic")
R0 = psi0 ** 2 * rb
W0 = sp.simplify(sp.diff(R0, rb) / psi0 ** 2)
mMS = sp.simplify(R0 / 2 * (1 - W0 ** 2))
check_zero(mMS - 2 * a * b, "Misner-Sharp mass of psi = a + b/rbar (K = 0) is 2ab")
rth = sp.solve(sp.diff(R0, rb), rb)
print("   stationary points of R(rbar):", rth)
rth = [r for r in rth if sp.simplify(r - b / a) == 0][0]
check_zero(R0.subs(rb, rth) - 4 * a * b, "throat at rbar = b/a with R = 4ab = 2M")
# inversion symmetry rbar -> (b/a)^2 / rbar maps R to itself
check_zero(sp.simplify(R0.subs(rb, (b / a) ** 2 / rb) - R0), "inversion rbar -> (b/a)^2/rbar is an isometry of R")
# puncture form psi = 1 + u0 + m_p/(2 rbar): a = 1 + u0, b = m_p/2  =>  M = m_p (1 + u0)
u0, mp = sp.symbols("u0 m_p")
check_zero((2 * a * b).subs({a: 1 + u0, b: mp / 2}) - mp * (1 + u0),
           "puncture parameters: M = m_p (1 + u(0)), throat rbar = m_p/(2(1 + u(0)))")
# isotropic Schwarzschild for comparison: a = 1, b = M/2
r_iso = sp.symbols("r", positive=True)
Riso = (1 + M / (2 * r_iso)) ** 2 * r_iso
# check dlnR/dlnr = sqrt(1 - 2M/R) for r > M/2
expr_iso = sp.simplify(sp.diff(sp.log(Riso), r_iso) * r_iso - sp.sqrt(1 - 2 * M / Riso))
num = [expr_iso.subs({M: 1, r_iso: v}).evalf() for v in (0.6, 1.0, 3.0, 10.0)]
print("   isotropic: d ln R/d ln r - sqrt(1 - 2M/R) at r = 0.6, 1, 3, 10 M:", num)
assert max(abs(float(v)) for v in num) < 1e-14
print("[OK] isotropic Schwarzschild obeys d ln R/d ln r = W = sqrt(1 - 2M/R) on the outer sheet")
print("ALL S1 CHECKS PASSED")
