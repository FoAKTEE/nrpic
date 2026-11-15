#!/usr/bin/env python3
"""Independent check (numpy) of the Cartesian form of the extrinsic curvature of table
format 2: momentum and Hamiltonian residuals of the bound-ball table on a patch of a
Cartesian mesh, with sixth-order centred differences, against the cell size.

Conformally flat metric psi^4 delta_ij, K^i_j = KT delta_ij + (KL - KT) n_i n_j:
    M_i = d_j K^j_i + 6 K^l_i d_l ln psi - 2 K d_i ln psi - d_i K,
    H   = -8 psi^-5 Laplace(psi) + K^2 - K^i_j K^j_i.
Evaluated in the vacuum part of the curved slice, 6.7 < r < 9 M (the region of test 0),
with `nrpic.io.Table2` giving u, KL, KT at the cell centres.  Prints the largest
residuals and the orders between successive cell sizes.
"""
import math
import sys

import numpy as np

import idlib  # noqa: F401  (path of the nrpic package)
from nrpic import expanding_ball as eb


def d1(f, ax, dx):
    s = lambda k: np.roll(f, -k, axis=ax)
    return ((s(3) - s(-3)) / 60.0 - 3.0 * (s(2) - s(-2)) / 20.0 + 3.0 * (s(1) - s(-1)) / 4.0) / dx


def d2(f, ax, dx):
    s = lambda k: np.roll(f, -k, axis=ax)
    return ((s(3) + s(-3)) / 90.0 - 3.0 * (s(2) + s(-2)) / 20.0 + 1.5 * (s(1) + s(-1))
            - 49.0 * f / 18.0) / dx ** 2


def residuals(tab, dx, lo=(4.0, 0.0, 0.0), hi=(11.0, 5.0, 5.0)):
    ax = [np.arange(math.floor(a / dx) - 4, math.ceil(b / dx) + 4) * dx + 0.5 * dx
          for a, b in zip(lo, hi)]
    X = np.stack(np.meshgrid(*ax, indexing="ij"), axis=-1)
    r = np.sqrt(np.sum(X * X, axis=-1))
    n = X / r[..., None]
    u, kl, kt, _, _ = tab(r)
    psi = 1.0 + u
    lnpsi = np.log(psi)
    K = kt[..., None, None] * np.eye(3) + (kl - kt)[..., None, None] * n[..., :, None] * n[..., None, :]
    trK = kl + 2.0 * kt
    dl = [d1(lnpsi, a, dx) for a in range(3)]
    M = []
    for i in range(3):
        m = sum(d1(K[..., j, i], j, dx) + 6.0 * K[..., j, i] * dl[j] for j in range(3))
        M.append(m - 2.0 * trK * dl[i] - d1(trK, i, dx))
    H = -8.0 * psi ** -5 * sum(d2(psi, a, dx) for a in range(3)) + trK ** 2 - (kl ** 2 + 2.0 * kt ** 2)
    Mabs = np.sqrt(sum(m * m for m in M)) / psi ** 2
    inner = np.ones(r.shape, bool)
    for a in range(3):                       # drop the wrapped margin of np.roll
        idx = [slice(None)] * 3
        idx[a] = slice(0, 4)
        inner[tuple(idx)] = False
        idx[a] = slice(-4, None)
        inner[tuple(idx)] = False
    reg = inner & (r > 6.7) & (r < 9.0)
    return float(np.abs(H[reg]).max()), float(Mabs[reg].max())


def main():
    ball = eb.Ball(M=1.0, Rb=5.0, e0=0.16, RE=10.0)
    tab = ball.table()
    out = []
    for dx in (0.5, 0.25, 0.125, 0.0625):
        h, m = residuals(tab, dx)
        out.append((dx, h, m))
        print(f"dx = {dx:6.4f}   max |H| = {h:.3e}   max |M| = {m:.3e}")
    for (a, ha, ma), (b, hb, mb) in zip(out[:-1], out[1:]):
        print(f"order {a:g} -> {b:g}:  H {math.log2(ha / hb):.2f}   M {math.log2(ma / mb):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
