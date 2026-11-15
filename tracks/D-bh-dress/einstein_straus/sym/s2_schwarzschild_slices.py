#!/usr/bin/env python3
"""S2, S3: slices t = T(R) of Schwarzschild in static coordinates; the family
KT = -f(R) sqrt(2M/R^3); lapse and shift of the stationary slicing; null expansions and
the anti-trapping condition; the outgoing Painleve-Gullstrand slice.

Run: python3 sym/s2_schwarzschild_slices.py
"""
import os
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tensors import christoffel, check_zero  # noqa: E402

t, R, th, ph = sp.symbols("t R theta phi", real=True)
M = sp.symbols("M", positive=True)
X = [t, R, th, ph]
F = 1 - 2 * M / R
g4 = sp.diag(-F, 1 / F, R ** 2, R ** 2 * sp.sin(th) ** 2)
G4 = christoffel(g4, X)

T = sp.Function("T")(R)
Tp = sp.diff(T, R)
# slice t - T(R) = 0; future-pointing unit normal n_mu = -N d_mu(t - T)
gRR = 1 / F - F * Tp ** 2                       # induced metric component (dl/dR)^2
N = 1 / sp.sqrt(gRR)
n_lo = sp.Matrix([-N, N * Tp, 0, 0])
g4i = g4.inv()
n_up = sp.simplify(g4i * n_lo)
check_zero(sp.simplify((n_lo.T * n_up)[0] + 1), "n is unit timelike")
print("   n^t =", sp.simplify(n_up[0]), "(> 0 where gRR > 0 and F > 0: future pointing)")


def nabla_n(a, b):
    """nabla_a n_b"""
    return sp.diff(n_lo[b], X[a]) - sum(G4[c][a][b] * n_lo[c] for c in range(4))


# K_ab = -h_a^c h_b^d nabla_c n_d (code convention K_ij = -(1/2) Lie_n gamma_ij).
# Tangent basis of the slice: e_R = d_R + T' d_t, e_theta, e_phi.
eR = sp.Matrix([Tp, 1, 0, 0])
eth = sp.Matrix([0, 0, 1, 0])
KRR = -sum(eR[a] * eR[b] * nabla_n(a, b) for a in range(4) for b in range(4))
Kthth = -nabla_n(2, 2)
KL = sp.simplify(KRR / gRR)                      # K^R_R (mixed, along the slice)
KT = sp.simplify(Kthth / R ** 2)
print("   KT =", KT)
# (S2a) Misner-Sharp relation for every T(R)
Rprime2 = 1 / gRR                               # (dR/dl)^2
check_zero(sp.simplify(Rprime2 - (1 - 2 * M / R + R ** 2 * KT ** 2)),
           "(dR/dl)^2 = 1 - 2M/R + R^2 KT^2 for every slice t = T(R)")
# (S2b) momentum constraint KL = d(R KT)/dR for every T(R)
check_zero(sp.simplify(KL - sp.diff(R * KT, R)), "KL = d(R KT)/dR for every slice t = T(R)")

# (S2c) the f family: solve KT = -f sqrt(2M/R^3) for T'
f = sp.Function("f")(R)
s = sp.symbols("s")                             # s = T'
KT_s = sp.simplify(KT.subs(Tp, s))
sol = sp.solve(sp.Eq(KT_s ** 2, f ** 2 * 2 * M / R ** 3), s)
print("   T'(R) for KT^2 = f^2 2M/R^3:", [sp.simplify(z) for z in sol])
Wf = sp.sqrt(1 - 2 * M * (1 - f ** 2) / R)
for z in sol:
    cand = sp.simplify(z - f * sp.sqrt(2 * M / R) / (F * Wf))
    if cand == 0:
        print("[OK] T'(R) = f sqrt(2M/R) / ((1 - 2M/R) W),  W = sqrt(1 - 2M(1 - f^2)/R)")
        Tp_f = z
        break
else:
    # check numerically which root matches
    Tp_f = f * sp.sqrt(2 * M / R) / (F * Wf)
    val = sp.simplify(KT.subs(Tp, Tp_f) + f * sp.sqrt(2 * M / R ** 3))
    num = [val.subs({M: 1, R: r, f: q}).evalf() for r, q in ((3, 0.3), (7, 0.8), (20, 1.0))]
    print("   KT(T'_f) + f sqrt(2M/R^3) at sample points:", num)
    assert max(abs(complex(v)) for v in num) < 1e-14
    print("[OK] T'(R) = f sqrt(2M/R) / ((1 - 2M/R) W) gives KT = -f sqrt(2M/R^3) (R > 2M)")
# T' is singular at R = 2M unless f = 0 there: the slice crosses R = 2M only through the
# bifurcation sphere (f = 0) in these coordinates, or through a horizon (f != 0).
# (S2d) lapse of the stationary slicing (xi = d_t): alpha = -n . xi = N
xi = sp.Matrix([1, 0, 0, 0])
alpha = sp.simplify(-(n_lo.T * xi)[0])
check_zero(sp.simplify(alpha ** 2 - Rprime2), "stationary slicing: alpha^2 = (dR/dl)^2 = W^2")
# shift: beta = xi - alpha n ; radial component along R
beta_up = sp.simplify(xi - alpha * n_up)
# the shift is tangent to the slice: beta = beta^R e_R with beta^R the R component
check_zero(sp.simplify(beta_up[0] - beta_up[1] * Tp), "beta is tangent to the slice")
check_zero(sp.simplify(beta_up[1] - alpha * R * KT), "beta^R = alpha R KT (areal radius frozen)")
print("   => in the isotropic radius beta^rbar = beta^R (rbar/(R W)) = rbar KT")

# ---------------------------------------------------------------- null expansions (S3)
# outgoing k = n + s, ingoing l = n - s, s the unit outward normal of the sphere in the slice
sR = sp.Matrix([Tp, 1, 0, 0]) / sp.sqrt(gRR)    # unit tangent along increasing R
k = n_up + sR
lv = n_up - sR
th_k = sp.simplify(2 * k[1] / R)                # theta = (2/R) k^mu d_mu R
th_l = sp.simplify(2 * lv[1] / R)
Rp = 1 / sp.sqrt(gRR)                          # dR/dl (dl = sqrt(gRR) dR)
# Lie_n R = n^R must equal -R KT (definition of KT through K_ij = -(1/2) Lie_n gamma_ij)
nR_plus = sp.simplify(n_up[1] + R * KT)
samples = [{M: 1, R: 3, Tp: 0.4}, {M: 1, R: 7.5, Tp: -0.9}, {M: 2, R: 30, Tp: 0.05}]


def check_num(expr, label):
    vals = [complex(sp.N(expr.subs(sv))) for sv in samples]
    ok = max(abs(v) for v in vals) < 1e-13
    print(f"[{'OK' if ok else 'FAIL'}] {label} (numerically at {len(samples)} points with R > 2M,"
          f" spacelike slice; symbolic form differs by sqrt branches only)" + ("" if ok else f" {vals}"))
    if not ok:
        raise AssertionError(label)


check_num(nR_plus, "Lie_n R = n^R = -R KT")
check_num(th_k - 2 / R * (Rp - R * KT), "theta_+ = (2/R)(R' - R KT)")
check_num(th_l - 2 / R * (-Rp - R * KT), "theta_- = (2/R)(-R' - R KT)")
check_num(th_k * th_l + 4 / R ** 2 * (1 - 2 * M / R), "theta_+ theta_- = -(4/R^2)(1 - 2M/R)")
check_num(th_k + th_l + 4 * KT, "theta_+ + theta_- = -4 KT")
print("   => anti-trapped (both > 0) iff R < 2M and KT < 0; trapped iff R < 2M and KT > 0;"
      " marginal at R = 2M")

# ---------------------------------------------------------------- general m: product rule
mm = sp.symbols("m", positive=True)
Rpr, KTs, Rs = sp.symbols("Rp KT Rs", real=True)
pe =sp.expand((2 / Rs) ** 2 * (Rs ** 2 * KTs ** 2 - Rpr ** 2)).subs(Rpr ** 2, 1 - 2 * mm / Rs + Rs ** 2 * KTs ** 2)
check_zero(sp.simplify(pe + 4 / Rs ** 2 * (1 - 2 * mm / Rs)),
           "with matter: theta_+ theta_- = -(4/R^2)(1 - 2m/R), m the Misner-Sharp mass")

# ---------------------------------------------------------------- the throat of the f family
fs = sp.symbols("f_th", real=True)
Rth = sp.solve(sp.Eq(1 - 2 * M * (1 - fs ** 2) / R, 0), R)
print("   throat of the f family (W = 0): R_th =", Rth, "= 2M only if f(R_th) = 0")
# outgoing PG (f = 1 everywhere): W = 1, no throat, the slice reaches R = 0
print("   f = 1 everywhere (outgoing PG): W = 1, R runs from 0 to infinity; for R < 2M,"
      " KT < 0 -> anti-trapped (white-hole region); the slice ends at R = 0")
Kretsch = 48 * M ** 2 / R ** 6
print("   Kretschmann scalar 48 M^2/R^6 diverges at R = 0: the outgoing PG slice is singular")
print("ALL S2/S3 CHECKS PASSED")
