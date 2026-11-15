#!/usr/bin/env python3
"""Numerical checks of python/nrpic/smeared_bowen_york.py (no simulation), test P0 of
tracks/core/JOURNAL-clump.md:

 1. trace and symmetry of Abar_ij;
 2. divergence by sixth-order central differences against 8 pi Stilde_i, momentum and
    spin, at random points inside and outside the clump;
 3. continuity of the series/closed-form switch of the moments at t = T_SERIES and the
    moments against direct quadrature;
 4. surface integrals at large radius: P_ADM = P, J_ADM = S;
 5. far field against the Bowen-York curvature of python/nrpic/bowen_york.py;
 6. sigma -> 0 limit at fixed r: Bowen-York.

Prints one line per check and exits 1 on a failure.
"""
import math
import os
import sys

import numpy as np
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
from nrpic import bowen_york as by  # noqa: E402
from nrpic import smeared_bowen_york as sby  # noqa: E402

ok = True


def report(name, err, tol):
    global ok
    good = err < tol
    ok = ok and good
    print(f"{'ok   ' if good else 'FAIL '} {name}: {err:.3e} (tolerance {tol:.0e})")


rng = np.random.default_rng(7)
centre = np.array([0.3, -0.2, 0.1])
sigma = 0.7
P = np.array([0.11, -0.05, 0.07])
S = np.array([0.02, 0.09, -0.04])

# 1. trace, symmetry
x = centre + rng.normal(size=(2000, 3)) * 2.0 * sigma
A = sby.abar(x, centre, sigma, P, S)
scale = np.abs(A).max()
report("trace", np.abs(np.trace(A, axis1=-1, axis2=-2)).max() / scale, 1e-14)
report("symmetry", np.abs(A - np.swapaxes(A, -1, -2)).max() / scale, 1e-15)

# 2. divergence, sixth-order central differences
h = 2.0e-2 * sigma
cf = np.array([-1.0 / 60.0, 3.0 / 20.0, -3.0 / 4.0, 0.0, 3.0 / 4.0, -3.0 / 20.0, 1.0 / 60.0]) / h
for label, PP, SS in (("momentum", P, 0 * S), ("spin", 0 * P, S), ("both", P, S)):
    div = np.zeros((len(x), 3))
    for j in range(3):
        for k, c in zip(range(-3, 4), cf):
            if c == 0.0:
                continue
            xs = x.copy()
            xs[:, j] += k * h
            div += c * sby.abar(xs, centre, sigma, PP, SS)[:, :, j]
    src = 8.0 * math.pi * sby.momentum_density(x, centre, sigma, PP, SS)
    report(f"d_j Abar_ij = 8 pi Stilde_i ({label})",
           np.abs(div - src).max() / np.abs(src).max(), 2e-8)

# 3. moments
t0 = sby.T_SERIES
lo = np.array(sby.moments(np.array([t0 * (1 - 1e-13)])))
hi = np.array(sby.moments(np.array([t0 * (1 + 1e-13)])))
report("series/closed-form switch of Q, I4, C", np.abs(lo / hi - 1.0).max(), 1e-11)
err = 0.0
for t in (1e-3, 0.03, 0.2, 0.49, 0.51, 1.0, 2.5, 6.0):
    q, i4, c = (float(v) for v in sby.moments(np.array(t)))
    qq = quad(lambda s: 4 / math.sqrt(math.pi) * s * s * math.exp(-s * s), 0, t,
              epsabs=0, epsrel=1e-13)[0]
    ii = quad(lambda s: 8 / math.sqrt(math.pi) * s ** 4 * math.exp(-s * s), 0, t,
              epsabs=0, epsrel=1e-13)[0]
    cc = qq - 4 / (3 * math.sqrt(math.pi)) * t ** 3 * math.exp(-t * t)
    err = max(err, abs(q / qq - 1), abs(i4 / ii - 1))
    if t < 0.4:      # C by quadrature cancels below; compare with its leading series
        cc = 8 / (3 * math.sqrt(math.pi)) * (t ** 5 / 5 - t ** 7 / 7 + t ** 9 / 18
                                             - t ** 11 / 66 + t ** 13 / 312
                                             - t ** 15 / 1800 + t ** 17 / 12240)
    err = max(err, abs(c / cc - 1))
report("moments against quadrature", err, 3e-12)

# 4. ADM momentum and angular momentum on a sphere of radius R:
#    P_i = (1/8 pi) oint Abar_ij n_j dA,  J_i = (1/8 pi) oint eps_ijk x_j Abar_kl n_l dA
mu, wm = np.polynomial.legendre.leggauss(48)
ph = (np.arange(96) + 0.5) * 2 * math.pi / 96
MU, PH = np.meshgrid(mu, ph, indexing="ij")
WW = np.repeat(wm[:, None], 96, axis=1) * 2 * math.pi / 96
nn = np.stack([np.sqrt(1 - MU ** 2) * np.cos(PH), np.sqrt(1 - MU ** 2) * np.sin(PH), MU], -1)
for R in (12.0 * sigma, 60.0 * sigma):
    xx = centre + R * nn
    AA = sby.abar(xx, centre, sigma, P, S)
    An = np.einsum("...ij,...j->...i", AA, nn)
    Padm = np.einsum("ab,abi->i", WW, An) * R * R / (8 * math.pi)
    Jadm = np.einsum("ab,abi->i", WW, np.cross(R * nn, An)) * R * R / (8 * math.pi)
    report(f"P_ADM = P on the sphere R = {R / sigma:g} sigma",
           np.abs(Padm - P).max() / np.abs(P).max(), 1e-12)
    report(f"J_ADM = S on the sphere R = {R / sigma:g} sigma",
           np.abs(Jadm - S).max() / np.abs(S).max(), 1e-12)

# 5. far field: Bowen-York plus the regular term 3 sigma^2/(2 r^4) [...]
xf = centre + 40.0 * sigma * nn.reshape(-1, 3)
Af = sby.abar(xf, centre, sigma, P, S)
Ab = by.abar(xf, centre, P, S)
d, r = xf - centre, 40.0 * sigma
n = d / r
pn = (n @ P)[:, None, None]
pnn = P[:, None] * n[:, None, :] + n[:, :, None] * P[None, :]
reg = 1.5 * sigma ** 2 / r ** 4 * (pnn + (np.eye(3) - 5 * n[:, :, None] * n[:, None, :]) * pn)
report("far field = Bowen-York + regular term (r = 40 sigma)",
       np.abs(Af - Ab - reg).max() / np.abs(Ab).max(), 1e-13)
report("far field against Bowen-York alone (expected 9.4e-4: sigma^2/r^2 term)",
       np.abs(Af - Ab).max() / np.abs(Ab).max(), 2e-3)

# 6. point limit
xs = centre + rng.normal(size=(500, 3))
As = sby.abar(xs, centre, 1.0e-3, P, S)
Ab = by.abar(xs, centre, P, S)
rr = np.sqrt(np.sum((xs - centre) ** 2, axis=1))
sel = rr > 0.3
report("sigma -> 0: Bowen-York (sigma = 1e-3, r > 0.3)",
       np.abs(As - Ab)[sel].max() / np.abs(Ab)[sel].max(), 1e-4)

# numbers quoted in the journal
print("second-order mass (1/16 pi) int Abar^2 d^3x per P^2/sigma: "
      f"{sby.second_order_mass(1.0, P=1.0):.6f}; per S^2/sigma^3: "
      f"{sby.second_order_mass(1.0, S=1.0):.6f}")
sys.exit(0 if ok else 1)
