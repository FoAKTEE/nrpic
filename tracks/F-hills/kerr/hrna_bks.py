"""A third coordinate chart for the HRNA of tracks/F-hills/geodesic_binary/hrna.py (read-only there):
Kerr with Boyer-Lindquist time and Cartesian Kerr-Schild space, coords code COORDS_BKS = 2.

Why (kerr/JOURNAL.md entry 2): in Cartesian Kerr-Schild coordinates ('cks') the slices t = const are
tilted against the static ones by dt_KS - dt_BL = (2 M r / Delta) dr.  HRNA evaluates the pair
force at equal coordinate time, so in 'cks' a binary moving at V sees its partner displaced by
V (2M r/Delta)(n.d): a shear of first order in M/r that is not symmetric and pumps (prograde) or
drains (retrograde) the binary's energy secularly, with a runaway at the binary frequency of
arXiv:2402.02178.  The chart here keeps the spatial coordinates of 'cks' and replaces its time by
the Boyer-Lindquist time,
    t' = t_KS - F(r),   F'(r) = 2 M r / Delta,   Delta = r^2 - 2 M r + a^2,
so that at a = 0 it is exactly the Schwarzschild form 'sch' of hrna.py, and at a != 0 only the
frame-dragging part g'^{0i} = O(M a / r^2) of the shift remains.

Metric:  g'_00 = g_00,  g'_0i = g_0i + g_00 T_i,  g'_ij = g_ij + g_0i T_j + g_0j T_i + g_00 T_i T_j
         g'^00 = g^00 - 2 T_i g^0i + T_i T_j g^ij,  g'^0i = g^0i - T_j g^ij,  g'^ij = g^ij
with T_i = F'(r) d_i r (d_i r and d_i d_j r of the Kerr-Schild radius in closed form).

The equations of motion, integrator and diagnostics are those of hrna.py, unchanged: the numba
functions accel_one, rhs, integrate and energy_lz of hrna are recompiled here from their own code
objects with the module globals of hrna except `metric`, which is replaced by a dispatcher that
adds COORDS_BKS.  Nothing of hrna's text is copied.
"""
from __future__ import annotations

import math
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("NUMBA_CACHE_DIR", "/data/haiyangw/nrpic/scratch/F-hills/tmp/kerr/numba_cache")
sys.path.insert(0, os.path.join(HERE, "..", "geodesic_binary"))

import numba as nb  # noqa: E402
import numpy as np  # noqa: E402

import hrna  # noqa: E402

COORDS_BKS = 2


@nb.njit(cache=True)
def ks_r_derivs(x, a, rk, rkl):
    """r of Cartesian Kerr-Schild and its first (rk[3]) and second (rkl[3,3]) derivatives."""
    X, Y, Z = x[0], x[1], x[2]
    r = hrna.cks_r(x, a)
    D = r ** 4 + a * a * Z * Z
    N = np.empty(3)
    N[0] = r * r * X
    N[1] = r * r * Y
    N[2] = r * r * Z + a * a * Z
    for i in range(3):
        rk[i] = r * N[i] / D
    xs = (X, Y, Z)
    for k in range(3):
        dD = 4.0 * r ** 3 * rk[k] + (2.0 * a * a * Z if k == 2 else 0.0)
        for i in range(3):
            dN = 2.0 * r * rk[k] * xs[i] + (r * r if i == k else 0.0) + (a * a if (i == 2 and k == 2) else 0.0)
            rkl[i, k] = (rk[k] * N[i] + r * dN) / D - r * N[i] * dD / (D * D)
    return r


@nb.njit(cache=True)
def metric_bks(x, M, a, g, gi, dg):
    hrna.metric_cks(x, M, a, g, gi, dg)            # Kerr-Schild components, then the time change
    rk = np.empty(3)
    rkl = np.empty((3, 3))
    r = ks_r_derivs(x, a, rk, rkl)
    Dl = r * r - 2.0 * M * r + a * a
    Fp = 2.0 * M * r / Dl
    Fpp = 2.0 * M / Dl - 2.0 * M * r * (2.0 * r - 2.0 * M) / (Dl * Dl)
    T = np.empty(4)
    T[0] = 0.0
    dT = np.zeros((3, 4))                          # dT[k, i+1] = d_k T_i
    for i in range(3):
        T[i + 1] = Fp * rk[i]
        for k in range(3):
            dT[k, i + 1] = Fpp * rk[k] * rk[i] + Fp * rkl[i, k]
    G = g.copy()
    Gi = gi.copy()
    dG = dg.copy()
    # covariant metric g'_{mu nu} = g_{ab} L^a_mu L^b_nu with L^0_mu = (1, T_i), L^i_j = delta
    for mu in range(4):
        for nu in range(4):
            s = G[mu, nu]
            if mu >= 1:
                s += G[0, nu] * T[mu]
            if nu >= 1:
                s += G[mu, 0] * T[nu]
            if mu >= 1 and nu >= 1:
                s += G[0, 0] * T[mu] * T[nu]
            g[mu, nu] = s
            for k in range(3):
                d = dG[k, mu, nu]
                if mu >= 1:
                    d += dG[k, 0, nu] * T[mu] + G[0, nu] * dT[k, mu]
                if nu >= 1:
                    d += dG[k, mu, 0] * T[nu] + G[mu, 0] * dT[k, nu]
                if mu >= 1 and nu >= 1:
                    d += dG[k, 0, 0] * T[mu] * T[nu] + G[0, 0] * (dT[k, mu] * T[nu] + T[mu] * dT[k, nu])
                dg[k, mu, nu] = d
    # contravariant g'^{mu nu} = M^mu_a M^nu_b g^{ab} with M^0_a = (1, -T_i), M^i_b = delta
    for mu in range(4):
        for nu in range(4):
            s = 0.0
            for al in range(4):
                ma = (1.0 if al == 0 else -T[al]) if mu == 0 else (1.0 if al == mu else 0.0)
                if ma == 0.0:
                    continue
                for be in range(4):
                    mb = (1.0 if be == 0 else -T[be]) if nu == 0 else (1.0 if be == nu else 0.0)
                    if mb == 0.0:
                        continue
                    s += ma * mb * Gi[al, be]
            gi[mu, nu] = s


@nb.njit(cache=True)
def metric3(coords, x, M, a, g, gi, dg):
    if coords == hrna.COORDS_SCH:
        hrna.metric_sch(x, M, g, gi, dg)
    elif coords == hrna.COORDS_CKS:
        hrna.metric_cks(x, M, a, g, gi, dg)
    else:
        metric_bks(x, M, a, g, gi, dg)


@nb.njit(cache=True)
def radius3(coords, x, a):
    if coords == hrna.COORDS_SCH:
        return math.sqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2])
    return hrna.cks_r(x, a)


def _rejit(fn, glb):
    py = fn.py_func
    f = types.FunctionType(py.__code__, glb, py.__name__, py.__defaults__, py.__closure__)
    return nb.njit(cache=False)(f)


_G = dict(hrna.__dict__)
_G["metric"] = metric3
_G["radius"] = radius3
accel_one = _rejit(hrna.accel_one, _G)
_G["accel_one"] = accel_one
rhs = _rejit(hrna.rhs, _G)
_G["rhs"] = rhs
integrate = _rejit(hrna.integrate, _G)
energy_lz = _rejit(hrna.energy_lz, _G)


def coord_code(coords):
    return {"sch": hrna.COORDS_SCH, "cks": hrna.COORDS_CKS, "bks": COORDS_BKS}[coords]


def F_of_r(r, a, M=1.0):
    """t_KS - t_BL = F(r) = int 2 M r / Delta dr (constant: F = 0 at r_+ + 1, irrelevant)."""
    if a == 0.0:
        return 2.0 * M * math.log(r / (2.0 * M) - 1.0)
    rp_ = M + math.sqrt(M * M - a * a)
    rm_ = M - math.sqrt(M * M - a * a)
    return (2 * M * rp_ / (rp_ - rm_)) * math.log(r - rp_) - (2 * M * rm_ / (rp_ - rm_)) * math.log(r - rm_)


def cks_to_bks_velocity(x, v_ks, a, M=1.0):
    """dx/dt_BL from dx/dt_KS at x: dt_BL = dt_KS - F'(r) dr."""
    rk = np.empty(3)
    rkl = np.empty((3, 3))
    r = ks_r_derivs(np.asarray(x, float), a, rk, rkl)
    Fp = 2 * M * r / (r * r - 2 * M * r + a * a)
    rdot = float(rk @ v_ks)
    return np.asarray(v_ks, float) / (1.0 - Fp * rdot)


def bks_to_cks_velocity(x, v_bl, a, M=1.0):
    rk = np.empty(3)
    rkl = np.empty((3, 3))
    r = ks_r_derivs(np.asarray(x, float), a, rk, rkl)
    Fp = 2 * M * r / (r * r - 2 * M * r + a * a)
    rdot = float(rk @ v_bl)
    return np.asarray(v_bl, float) / (1.0 + Fp * rdot)
