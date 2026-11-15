#!/usr/bin/env python3
"""Reference solution for the oblate-collapse row of the ladder (row 3), written for the
core lead who implements the oblate case in athenak/src/pgen/nrpic/nrpic_cf.cpp and
python/nrpic/spheroid.py (this package may not write either; see README.md, Requests).

Homogeneous spheroid with equatorial semi-axis a (x, y) and polar semi-axis b (z),
auxiliary density rho_N = 3M/(8 pi a^2 b) (Newtonian source mass M/2, G = 1), as for the
prolate case (python/nrpic/spheroid.py, module docstring). Its potential is

    Phi_N = -pi rho_N a^2 b [ I(lam) - (x^2 + y^2) J_a(lam) - z^2 J_b(lam) ],
    I = int_lam^inf du/D,  J_a = int du/((a^2+u) D),  J_b = int du/((b^2+u) D),
    D(u) = (a^2 + u) sqrt(b^2 + u),

lam = 0 inside and the positive root of (x^2+y^2)/(a^2+lam) + z^2/(b^2+lam) = 1 outside.
Substituting s = sqrt(b^2 + u), w = sqrt(b^2 + lam), c^2 = |a^2 - b^2|:

  oblate (a > b):   I   = (2/c) atan(c/w)
                    J_a = atan(c/w)/c^3 - w/(c^2 (w^2 + c^2))
                    J_b = (2/c^2) (1/w - atan(c/w)/c)
  prolate (a < b):  atan -> atanh, c^2 -> -c^2 (the formulas of spheroid.py)

The conformal factor of the time-symmetric conformally flat data is psibar = 1 - Phi_N
(ADM mass M); the particles at rest have coordinate rest-mass density 2 rho_N psibar.

Checks run by `python3 oblate_reference.py` (each prints PASS/FAIL):
  1. I, J_a, J_b against adaptive quadrature of the defining integrals (inside and
     outside, several aspect ratios);
  2. inside: a^2 b (2 J_a + J_b) = 2 (Poisson equation, nabla^2 Phi_N = 4 pi rho_N);
  3. finite-difference Laplacian of Phi_N: 4 pi rho_N inside, 0 outside;
  4. Phi_N continuous across the surface and -> -(M/2)/r far away;
  5. the limit a -> b (sphere) and the prolate formulas of spheroid.py at a < b by
     analytic continuation (same quadrature).
"""
import math
import os
import sys

import numpy as np
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))


def lam_outside(R2, z2, a, b):
    """Positive root of R2/(a^2+l) + z2/(b^2+l) = 1 (0 inside)."""
    A, B = a * a, b * b
    # l^2 + l (A + B - R2 - z2) + (A B - R2 B - z2 A) = 0
    p = A + B - R2 - z2
    q = A * B - R2 * B - z2 * A
    l = 0.5 * (-p + np.sqrt(p * p - 4.0 * q))
    inside = R2 / A + z2 / B <= 1.0
    return np.where(inside, 0.0, l)


def IJ_oblate(lam, a, b):
    c = math.sqrt(a * a - b * b)
    w = np.sqrt(b * b + lam)
    t = np.arctan(c / w)
    I = 2.0 / c * t
    Ja = t / c ** 3 - w / (c * c * (w * w + c * c))
    Jb = 2.0 / (c * c) * (1.0 / w - t / c)
    return I, Ja, Jb


def IJ_quad(lam, a, b):
    D = lambda u: (a * a + u) * math.sqrt(b * b + u)
    I = quad(lambda u: 1.0 / D(u), lam, np.inf, epsabs=0, epsrel=1e-13, limit=400)[0]
    Ja = quad(lambda u: 1.0 / ((a * a + u) * D(u)), lam, np.inf, epsabs=0, epsrel=1e-13, limit=400)[0]
    Jb = quad(lambda u: 1.0 / ((b * b + u) * D(u)), lam, np.inf, epsabs=0, epsrel=1e-13, limit=400)[0]
    return I, Ja, Jb


def phi_N(x, y, z, a, b, M=1.0, IJ=IJ_oblate):
    rho = 3.0 * M / (8.0 * math.pi * a * a * b)
    R2, z2 = x * x + y * y, z * z
    lam = lam_outside(R2, z2, a, b)
    I, Ja, Jb = IJ(lam, a, b)
    return -math.pi * rho * a * a * b * (I - R2 * Ja - z2 * Jb), rho


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    return ok


def main():
    allok = True
    # oblate counterparts of the paper's prolate case: e = 0.9, a = 10 M, b = a sqrt(1-e^2)
    cases = [(10.0, 10.0 * math.sqrt(1 - 0.81)), (10.0, 7.0), (5.0, 4.9)]
    # 1. closed form against quadrature
    worst = 0.0
    for a, b in cases:
        for lam in (0.0, 0.3, 5.0, 80.0, 1e4):
            cf = IJ_oblate(np.array(lam), a, b)
            qd = IJ_quad(lam, a, b)
            worst = max(worst, max(abs(float(u) / v - 1.0) for u, v in zip(cf, qd)))
    allok &= check("closed form vs quadrature", worst < 1e-10, f"largest relative difference {worst:.2e}")
    # 2. Poisson identity inside
    worst = max(abs(a * a * b * (2 * IJ_oblate(np.array(0.0), a, b)[1] + IJ_oblate(np.array(0.0), a, b)[2]) - 2.0)
                for a, b in cases)
    allok &= check("a^2 b (2 J_a + J_b) = 2 inside", worst < 1e-12, f"{worst:.2e}")
    # 3. finite-difference Laplacian
    a, b = cases[0]
    h = 1e-3
    pts = [(1.0, 0.5, 0.3), (3.0, -2.0, 1.0), (0.0, 0.0, 0.0), (12.0, 3.0, 1.0), (2.0, 1.0, 6.0), (15.0, 0.0, 15.0)]
    res = []
    for p in pts:
        p = np.array(p, float)
        f0, rho = phi_N(*p, a, b)
        lap = 0.0
        for k in range(3):
            e = np.zeros(3)
            e[k] = h
            lap += (phi_N(*(p + e), a, b)[0] - 2 * f0 + phi_N(*(p - e), a, b)[0]) / h ** 2
        inside = (p[0] ** 2 + p[1] ** 2) / a ** 2 + p[2] ** 2 / b ** 2 < 1
        res.append(abs(lap - (4 * math.pi * rho if inside else 0.0)) / (4 * math.pi * rho))
    allok &= check("FD Laplacian = 4 pi rho_N inside, 0 outside", max(res) < 1e-5,
                   f"largest relative residual {max(res):.2e} at points {pts}")
    # 4. continuity at the surface and the far field
    eps = 1e-9
    worst = 0.0
    for th in np.linspace(0.05, math.pi / 2, 7):
        xs, zs = a * math.sin(th), b * math.cos(th)
        fin = phi_N(xs * (1 - eps), 0.0, zs * (1 - eps), a, b)[0]
        fout = phi_N(xs * (1 + eps), 0.0, zs * (1 + eps), a, b)[0]
        worst = max(worst, abs(fin - fout))
    allok &= check("Phi_N continuous across the surface", worst < 1e-7, f"largest jump {worst:.2e}")
    r = 1e5
    far = [phi_N(r * math.sin(t), 0.0, r * math.cos(t), a, b)[0] * r for t in (0.1, 0.8, 1.5)]
    allok &= check("Phi_N r -> -M/2 far away", max(abs(v + 0.5) for v in far) < 1e-6,
                   f"{far}")
    # 5. sphere limit and the prolate side (spheroid.py) through the quadrature
    a, b = 5.0, 5.0 * (1 - 1e-6)
    I, Ja, Jb = IJ_oblate(np.array(0.0), a, b)
    allok &= check("sphere limit inside: I = 2/a, J_a = J_b = 2/(3 a^3)",
                   abs(I * a / 2 - 1) < 1e-5 and abs(Ja * 1.5 * a ** 3 - 1) < 1e-5 and abs(Jb * 1.5 * a ** 3 - 1) < 1e-5,
                   f"I a/2 = {I * a / 2:.8f}, 3 a^3 J_a/2 = {1.5 * Ja * a ** 3:.8f}, 3 a^3 J_b/2 = {1.5 * Jb * a ** 3:.8f}")
    try:
        from nrpic import spheroid as sp
        a, b = 10.0 * math.sqrt(1 - 0.81), 10.0
        c = math.sqrt(b * b - a * a)
        worst = 0.0
        for lam in (0.0, 2.0, 50.0):
            ref = sp._IJ(np.array([math.sqrt(b * b + lam)]), c)
            qd = IJ_quad(lam, a, b)
            worst = max(worst, max(abs(float(np.ravel(u)[0]) / v - 1.0) for u, v in zip(ref, qd)))
        allok &= check("quadrature reproduces spheroid.py (prolate side)", worst < 1e-10,
                       f"largest relative difference {worst:.2e}")
    except Exception as err:  # the private helper may change
        print(f"SKIP  prolate comparison: {err}")
    print("ALL PASS" if allok else "SOME CHECKS FAILED")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
