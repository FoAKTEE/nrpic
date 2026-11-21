#!/usr/bin/env python3
"""Symbolic check of the Bowen-York curvature smeared with a Gaussian (work package clump,
tracks/core/JOURNAL-clump.md, section "Derivation").

Flat conformal space, Cartesian indices. Momentum constraint with K = 0:

    d_j Abar_ij = 8 pi Stilde_i,     Stilde_i = psi^6 S_i = sum_p m_p u_i,p delta^3(x - x_p).

Momentum.  Stilde_i = P_i g(r), g = (2 pi sigma^2)^(-3/2) exp(-r^2/(2 sigma^2)).  With
    phi = erf(s)/r,  lap phi = -4 pi g,            s = r/(sqrt(2) sigma),
    chi = (r + sigma^2/r) erf(s) + sigma sqrt(2/pi) exp(-s^2),  lap chi = 2 phi,
the vector W_i = -2 P_i phi + (1/4) P_j d_i d_j chi solves lap W_i + (1/3) d_i d_j W_j
= 8 pi P_i g, and Abar_ij = d_i W_j + d_j W_i - (2/3) delta_ij d_k W_k equals

    Abar_ij = 3 Q/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
            + I4/(2 r^4)  [P_i n_j + P_j n_i + (delta_ij - 5 n_i n_j) P.n],
    Q(r)  = 4 pi int_0^r g r'^2 dr' = erf(s) - (2/sqrt pi) s exp(-s^2),
    I4(r) = 4 pi int_0^r g r'^4 dr' = 3 sigma^2 [erf(s) - (2/sqrt pi) (s + 2 s^3/3) exp(-s^2)].

Spin.  Stilde_i = (S x x)_i g/(2 sigma^2) (rigid rotation of the Gaussian with angular
momentum S).  W_i = (S x grad phi)_i, and

    Abar_ij = 3 C/r^3 [(S x n)_i n_j + (S x n)_j n_i],     C(r) = Q - (4 pi/3) r^3 g.

Every identity is checked symbolically (sympy) at a generic point; limits and series are
printed.  Run: python3 tracks/core/analysis/clump/derive_smeared_by.py
"""
import sys

import sympy as sp

x, y, z = sp.symbols("x y z", real=True)
sig = sp.symbols("sigma", positive=True)
P = sp.Matrix(sp.symbols("P1 P2 P3", real=True))
S = sp.Matrix(sp.symbols("S1 S2 S3", real=True))
X = sp.Matrix([x, y, z])
r = sp.sqrt(x * x + y * y + z * z)
s = r / (sp.sqrt(2) * sig)
n = X / r
g = (2 * sp.pi * sig**2) ** sp.Rational(-3, 2) * sp.exp(-r**2 / (2 * sig**2))
phi = sp.erf(s) / r
chi = (r + sig**2 / r) * sp.erf(s) + sig * sp.sqrt(2 / sp.pi) * sp.exp(-s**2)
Q = sp.erf(s) - 2 / sp.sqrt(sp.pi) * s * sp.exp(-s**2)
I4 = 3 * sig**2 * (sp.erf(s) - 2 / sp.sqrt(sp.pi) * (s + 2 * s**3 / 3) * sp.exp(-s**2))
C = Q - sp.Rational(4, 3) * sp.pi * r**3 * g

# a generic point with exact rational coordinates: identities are verified by exact
# substitution after symbolic differentiation (simplify on the full expressions is slow)
PT = {x: sp.Rational(3, 7), y: sp.Rational(-5, 11), z: sp.Rational(2, 3),
      sig: sp.Rational(4, 5)}
PT2 = {x: sp.Rational(-1, 9), y: sp.Rational(1, 13), z: sp.Rational(1, 5),
       sig: sp.Rational(7, 3)}
ok = True


def lap(f):
    return sum(sp.diff(f, c, 2) for c in (x, y, z))


def zero(expr, name):
    """exact check that expr vanishes at the two generic points"""
    global ok
    vals = []
    for pt in (PT, PT2):
        e = expr.subs(pt)
        e = sp.simplify(e)
        if e != 0:   # exact cancellation can hide behind erf/exp: evaluate to 60 digits
            e = sp.N(e, 60)
        vals.append(e)
    good = all(abs(sp.N(v, 60)) < sp.Float("1e-50") for v in vals)
    ok = ok and good
    print(("ok    " if good else "FAIL  ") + name
          + ("" if good else "   values " + str([sp.N(v, 8) for v in vals])))


def lichnerowicz(W):
    div = sum(sp.diff(W[k], X[k]) for k in range(3))
    return sp.Matrix(3, 3, lambda i, j: sp.diff(W[j], X[i]) + sp.diff(W[i], X[j])
                     - sp.Rational(2, 3) * (1 if i == j else 0) * div)


def divergence(A):
    return sp.Matrix([sum(sp.diff(A[i, j], X[j]) for j in range(3)) for i in range(3)])


def delta(i, j):
    return 1 if i == j else 0


print("# potentials")
zero(lap(phi) + 4 * sp.pi * g, "lap phi = -4 pi g")
zero(lap(chi) - 2 * phi, "lap chi = 2 phi")
# radial derivatives of the enclosed moments, with the radius as its own symbol
Rs = sp.Symbol("R", positive=True)
sR = Rs / (sp.sqrt(2) * sig)
gR = (2 * sp.pi * sig**2) ** sp.Rational(-3, 2) * sp.exp(-Rs**2 / (2 * sig**2))
QR = sp.erf(sR) - 2 / sp.sqrt(sp.pi) * sR * sp.exp(-sR**2)
I4R = 3 * sig**2 * (sp.erf(sR) - 2 / sp.sqrt(sp.pi) * (sR + 2 * sR**3 / 3) * sp.exp(-sR**2))
for name, e in (("dQ/dr = 4 pi r^2 g", sp.diff(QR, Rs) - 4 * sp.pi * Rs**2 * gR),
                ("dI4/dr = 4 pi r^4 g", sp.diff(I4R, Rs) - 4 * sp.pi * Rs**4 * gR)):
    good = sp.simplify(e) == 0
    ok = ok and good
    print(("ok    " if good else "FAIL  ") + name)

print("# linear momentum")
Pn = (P.T * n)[0]
W = sp.Matrix([-2 * P[i] * phi + sp.Rational(1, 4)
               * sum(P[j] * sp.diff(chi, X[i], X[j]) for j in range(3)) for i in range(3)])
divW = sum(sp.diff(W[k], X[k]) for k in range(3))
for i in range(3):
    zero(lap(W[i]) + sp.Rational(1, 3) * sp.diff(divW, X[i]) - 8 * sp.pi * P[i] * g,
         f"vector equation, component {i}")
A = lichnerowicz(W)
Acf = sp.Matrix(3, 3, lambda i, j:
                3 * Q / (2 * r**2) * (P[i] * n[j] + P[j] * n[i]
                                      - (delta(i, j) - n[i] * n[j]) * Pn)
                + I4 / (2 * r**4) * (P[i] * n[j] + P[j] * n[i]
                                     + (delta(i, j) - 5 * n[i] * n[j]) * Pn))
for i in range(3):
    for j in range(i, 3):
        zero(A[i, j] - Acf[i, j], f"(LW)_{i}{j} = closed form with Q and I4")
zero(Acf.trace(), "closed form is traceless")
dA = divergence(Acf)
for i in range(3):
    zero(dA[i] - 8 * sp.pi * P[i] * g, f"d_j Abar_{i}j = 8 pi P_{i} g")
# Abar_ij Abar_ij
a = 3 * Q / (2 * r**2) + I4 / (2 * r**4)
b = -3 * Q / (2 * r**2) + I4 / (2 * r**4)
c = 3 * Q / (2 * r**2) - 5 * I4 / (2 * r**4)
A2cf = 2 * a**2 * (P.T * P)[0] + Pn**2 * (2 * a**2 + 4 * a * b + 4 * a * c + 3 * b**2
                                           + 2 * b * c + c**2)
zero(sum(Acf[i, j] ** 2 for i in range(3) for j in range(3)) - A2cf,
     "Abar^2 = 2 a^2 P^2 + (P.n)^2 (2a^2 + 4ab + 4ac + 3b^2 + 2bc + c^2)")

print("# spin")
gradphi = sp.Matrix([sp.diff(phi, c_) for c_ in (x, y, z)])
Ws = S.cross(gradphi)
zero(sum(sp.diff(Ws[k], X[k]) for k in range(3)), "div W = 0")
src = S.cross(X) * g / (2 * sig**2)
for i in range(3):
    zero(lap(Ws[i]) - 8 * sp.pi * src[i], f"lap W_{i} = 8 pi (S x x)_{i} g/(2 sigma^2)")
As = lichnerowicz(Ws)
Sxn = S.cross(n)
Ascf = sp.Matrix(3, 3, lambda i, j: 3 * C / r**3 * (Sxn[i] * n[j] + Sxn[j] * n[i]))
for i in range(3):
    for j in range(i, 3):
        zero(As[i, j] - Ascf[i, j], f"(LW)_{i}{j} = 3 C/r^3 [(S x n)_i n_j + (S x n)_j n_i]")
dAs = divergence(Ascf)
for i in range(3):
    zero(dAs[i] - 8 * sp.pi * src[i], f"d_j Abar_{i}j = 8 pi Stilde_{i} (spin)")
A2s = 18 * C**2 / r**6 * ((S.T * S)[0] - (S.T * n)[0] ** 2)
zero(sum(Ascf[i, j] ** 2 for i in range(3) for j in range(3)) - A2s,
     "Abar^2 = 18 C^2 (S^2 - (S.n)^2)/r^6")
# total angular momentum of the source: int x cross Stilde d^3x = S (radial integral)
rr = sp.Symbol("rr", positive=True)
gr = (2 * sp.pi * sig**2) ** sp.Rational(-3, 2) * sp.exp(-rr**2 / (2 * sig**2))
Jint = sp.integrate(4 * sp.pi * rr**2 * sp.Rational(2, 3) * rr**2 * gr / (2 * sig**2),
                    (rr, 0, sp.oo))
print(("ok    " if sp.simplify(Jint - 1) == 0 else "FAIL  ")
      + "int x cross Stilde d^3x = S   (angular average of x cross (S cross x) = 2 r^2 S/3)")
ok = ok and sp.simplify(Jint - 1) == 0

print("# limits and series (t = s = r/(sqrt 2 sigma))")
t = sp.Symbol("t", positive=True)
Qt = sp.erf(t) - 2 / sp.sqrt(sp.pi) * t * sp.exp(-t**2)
I4t = 3 * (sp.erf(t) - 2 / sp.sqrt(sp.pi) * (t + 2 * t**3 / 3) * sp.exp(-t**2))
Ct = Qt - sp.Rational(4, 3) / sp.sqrt(sp.pi) * t**3 * sp.exp(-t**2)
print("Q(t)            =", sp.series(Qt, t, 0, 10))
print("I4(t)/sigma^2   =", sp.series(I4t, t, 0, 12))
print("C(t)            =", sp.series(Ct, t, 0, 12))
# series coefficients used by the code: Q = (4/sqrt pi) sum (-1)^k t^(2k+3)/(k! (2k+3)),
# I4/sigma^2 = (8/sqrt pi) sum (-1)^k t^(2k+5)/(k! (2k+5)),
# C = (8/(3 sqrt pi)) sum_{k>=1} (-1)^(k+1) k t^(2k+3)/(k! (2k+3))
K = 6
Qs = 4 / sp.sqrt(sp.pi) * sum((-1) ** k * t ** (2 * k + 3) / (sp.factorial(k) * (2 * k + 3))
                              for k in range(K))
I4s = 8 / sp.sqrt(sp.pi) * sum((-1) ** k * t ** (2 * k + 5) / (sp.factorial(k) * (2 * k + 5))
                               for k in range(K))
Cs = 8 / (3 * sp.sqrt(sp.pi)) * sum((-1) ** (k + 1) * k * t ** (2 * k + 3)
                                    / (sp.factorial(k) * (2 * k + 3)) for k in range(1, K))
for name, f, fs, order in (("Q", Qt, Qs, 2 * K + 2), ("I4", I4t, I4s, 2 * K + 4),
                           ("C", Ct, Cs, 2 * K + 2)):
    d = sp.series(f - fs, t, 0, order).removeO()
    good = sp.simplify(d) == 0
    ok = ok and good
    print(("ok    " if good else "FAIL  ") + f"power series of {name} to order t^{order - 1}")
print("r -> infinity: Q -> 1, I4 -> 3 sigma^2, C -> 1: Bowen-York plus the regular term"
      " (3 sigma^2/(2 r^4)) [P_i n_j + P_j n_i + (delta_ij - 5 n_i n_j) P.n]")
print("r -> 0: a = 3Q/(2r^2) + I4/(2r^4) -> (12 pi/5) g(0) r, b -> -(8 pi/5) g(0) r,"
      " c -> (4 pi/35) g(0) r^3/sigma^2; 3C/r^3 -> (4 pi/5) g(0) r^2/sigma^2")
g0 = (2 * sp.pi * sig**2) ** sp.Rational(-3, 2)
CR = QR - sp.Rational(4, 3) * sp.pi * Rs**3 * gR
for name, e, want in (
        ("a/r", (3 * QR / (2 * Rs**2) + I4R / (2 * Rs**4)) / Rs, sp.Rational(12, 5) * sp.pi * g0),
        ("b/r", (-3 * QR / (2 * Rs**2) + I4R / (2 * Rs**4)) / Rs, -sp.Rational(8, 5) * sp.pi * g0),
        ("c/r^3", (3 * QR / (2 * Rs**2) - 5 * I4R / (2 * Rs**4)) / Rs**3,
         sp.Rational(4, 35) * sp.pi * g0 / sig**2),
        ("3C/r^5", 3 * CR / Rs**5, sp.Rational(4, 5) * sp.pi * g0 / sig**2)):
    lim = sp.limit(e, Rs, 0)
    good = sp.simplify(lim - want) == 0
    ok = ok and good
    print(("ok    " if good else "FAIL  ")
          + f"limit r -> 0 of {name} = {sp.simplify(want / g0)} g(0)"
          + ("" if good else f"   got {sp.simplify(lim / g0)} g(0)"))
for name, e, want in (("Q", QR, 1), ("I4", I4R, 3 * sig**2), ("C", CR, 1)):
    good = sp.simplify(sp.limit(e, Rs, sp.oo) - want) == 0
    ok = ok and good
    print(("ok    " if good else "FAIL  ") + f"limit r -> infinity of {name} = {want}")

print("\nALL IDENTITIES HOLD" if ok else "\nSOME IDENTITY FAILED")
sys.exit(0 if ok else 1)
