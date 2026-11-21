"""Bowen-York curvature smeared with a Gaussian: the conformal, traceless extrinsic
curvature of a moving or rotating Gaussian matter clump (reference twin of
``athenak/src/pgen/nrpic/nrpic_clump_curvature.hpp``).

Conformally flat slice, gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Abar_ij, K = 0. With
particles the momentum constraint reads (flat indices)

    d_j Abar_ij = 8 pi Stilde_i,    Stilde_i = psi^6 S_i = sum_p m_p u_(i,p) delta^3(x - x_p),

the coordinate density of the covariant particle momentum, which does not depend on psi.
The equation is linear: the curvatures of clumps and of Bowen-York punctures add.

Momentum.  For Stilde_i = P_i g(r), g = (2 pi sigma^2)^(-3/2) exp(-r^2/(2 sigma^2)),

    Abar_ij = 3 Q/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
            + I4/(2 r^4)  [P_i n_j + P_j n_i + (delta_ij - 5 n_i n_j) P.n],
    Q(r)  = 4 pi int_0^r g r'^2 dr' = erf(t) - (2/sqrt pi) t exp(-t^2),
    I4(r) = 4 pi int_0^r g r'^4 dr' = 3 sigma^2 [erf(t) - (2/sqrt pi)(t + 2 t^3/3) exp(-t^2)],

t = r/(sqrt 2 sigma): the Bowen-York curvature of the enclosed momentum plus the regular
solution of Bowen and York weighted with the enclosed second moment. Far away it is the
Bowen-York curvature of P plus 3 sigma^2/(2 r^4) [..]; at the centre it vanishes linearly.
The same two lines hold for any spherical profile with its own Q and I4.

Spin.  For Stilde_i = (S x x)_i g/(2 sigma^2), the Gaussian in rigid rotation (in the
momentum density) with angular momentum S,

    Abar_ij = 3 C/r^3 [(S x n)_i n_j + (S x n)_j n_i],   C(r) = Q - (4 pi/3) r^3 g.

Derivation and symbolic check: tracks/core/analysis/clump/derive_smeared_by.py.
The Hamiltonian constraint keeps the residual H = -psi^-12 Abar_ij Abar_ij (second order
in P and S) unless psi is corrected; `second_order_mass` gives the mass that a correction
would add.

Units G = c = 1. Nothing here evolves anything: reference solutions.
"""

import math

import numpy as np
from scipy.special import erf

__all__ = ["moments", "gaussian", "abar", "abar2", "momentum_density",
           "second_order_mass", "T_SERIES"]

T_SERIES = 0.5      # below this t the power series are used (the closed forms cancel)
_NSER = 14          # terms; the first neglected one is below 1e-20 at t = 0.5
_SQPI = math.sqrt(math.pi)


def moments(t):
    """Q, I4/sigma^2 and C at t = r/(sqrt 2 sigma) (arrays of the shape of t).

    Series for t < T_SERIES:
        Q  = (4/sqrt pi) sum_k (-1)^k t^(2k+3)/(k! (2k+3)),
        I4 = (8 sigma^2/sqrt pi) sum_k (-1)^k t^(2k+5)/(k! (2k+5)),
        C  = (8/(3 sqrt pi)) sum_{k>=1} (-1)^(k+1) k t^(2k+3)/(k! (2k+3))."""
    t = np.asarray(t, dtype=float)
    small = t < T_SERIES
    ts = np.where(small, t, T_SERIES)
    t2 = ts * ts
    q = np.zeros_like(ts)
    i4 = np.zeros_like(ts)
    c = np.zeros_like(ts)
    term = np.ones_like(ts)          # (-1)^k t^(2k)/k!
    for k in range(_NSER):
        q += term / (2 * k + 3)
        i4 += term / (2 * k + 5)
        c -= k * term / (2 * k + 3)
        term = -term * t2 / (k + 1)
    q *= 4.0 / _SQPI * ts ** 3
    i4 *= 8.0 / _SQPI * ts ** 5
    c *= 8.0 / (3.0 * _SQPI) * ts ** 3
    tl = np.where(small, T_SERIES, t)
    e = np.exp(-tl * tl)
    ql = erf(tl) - 2.0 / _SQPI * tl * e
    i4l = 3.0 * (erf(tl) - 2.0 / _SQPI * (tl + 2.0 * tl ** 3 / 3.0) * e)
    cl = ql - 4.0 / (3.0 * _SQPI) * tl ** 3 * e
    return (np.where(small, q, ql), np.where(small, i4, i4l), np.where(small, c, cl))


def gaussian(r, sigma):
    """g(r) = (2 pi sigma^2)^(-3/2) exp(-r^2/(2 sigma^2)), unit integral."""
    r = np.asarray(r, dtype=float)
    return (2.0 * math.pi * sigma * sigma) ** -1.5 * np.exp(-0.5 * (r / sigma) ** 2)


def _disp(x, centre):
    d = np.asarray(x, dtype=float) - np.asarray(centre, dtype=float)
    r = np.sqrt(np.sum(d * d, axis=-1))
    rs = np.where(r > 0.0, r, 1.0)
    return d, r, d / rs[..., None]


def abar(x, centre, sigma, P=(0.0, 0.0, 0.0), S=(0.0, 0.0, 0.0)):
    """Conformal curvature Abar_ij[..., 3, 3] of one Gaussian clump at the points
    x[..., 3] (zero at the centre)."""
    P = np.asarray(P, dtype=float)
    S = np.asarray(S, dtype=float)
    d, r, n = _disp(x, centre)
    q, i4, c = moments(r / (math.sqrt(2.0) * sigma))
    rs = np.where(r > 0.0, r, 1.0)
    ca = np.where(r > 0.0, 1.5 * q / rs ** 2, 0.0)[..., None, None]
    cb = np.where(r > 0.0, 0.5 * sigma * sigma * i4 / rs ** 4, 0.0)[..., None, None]
    cs = np.where(r > 0.0, 3.0 * c / rs ** 3, 0.0)[..., None, None]
    pn = np.sum(P * n, axis=-1)[..., None, None]
    sxn = np.cross(S, n)
    eye = np.eye(3)
    nn = n[..., :, None] * n[..., None, :]
    pnn = P[:, None] * n[..., None, :] + n[..., :, None] * P[None, :]
    return (ca * (pnn - (eye - nn) * pn) + cb * (pnn + (eye - 5.0 * nn) * pn)
            + cs * (sxn[..., :, None] * n[..., None, :] + n[..., :, None] * sxn[..., None, :]))


def abar2(x, clumps):
    """Abar_ij Abar_ij of the summed curvature of clumps = [(centre, sigma, P, S), ...]."""
    a = 0.0
    for centre, sigma, P, S in clumps:
        a = a + abar(x, centre, sigma, P, S)
    return np.sum(a * a, axis=(-1, -2))


def momentum_density(x, centre, sigma, P=(0.0, 0.0, 0.0), S=(0.0, 0.0, 0.0)):
    """Stilde_i[..., 3] = [P + (S x (x - centre))/(2 sigma^2)] g, the source the curvature
    solves the momentum constraint for."""
    d, r, _ = _disp(x, centre)
    g = gaussian(r, sigma)[..., None]
    return (np.asarray(P, dtype=float)
            + np.cross(np.asarray(S, dtype=float), d) / (2.0 * sigma * sigma)) * g


def second_order_mass(sigma, P=0.0, S=0.0, psi=1.0, nr=4000, rmax=400.0):
    """(1/(16 pi)) int psi^-7 Abar^2 d^3x for one clump with |P| = P, |S| = S, P and S
    parallel or one of them zero, and a constant psi: the ADM mass that a second-order
    correction of the conformal factor adds. The radial integral runs to rmax sigma, the
    Bowen-York tail beyond it is added in closed form."""
    x, w = np.polynomial.legendre.leggauss(nr)
    # s = ln r, from 1e-4 sigma to rmax sigma
    lo, hi = math.log(1.0e-4 * sigma), math.log(rmax * sigma)
    r = np.exp(0.5 * (hi - lo) * (x + 1.0) + lo)
    wr = 0.5 * (hi - lo) * w * r
    q, i4, c = moments(r / (math.sqrt(2.0) * sigma))
    a = 1.5 * q / r ** 2 + 0.5 * sigma ** 2 * i4 / r ** 4
    b = -1.5 * q / r ** 2 + 0.5 * sigma ** 2 * i4 / r ** 4
    cc = 1.5 * q / r ** 2 - 2.5 * sigma ** 2 * i4 / r ** 4
    # angular averages: <(P.n)^2> = P^2/3, <S^2 - (S.n)^2> = 2 S^2/3
    a2p = P * P * (2.0 * a * a + (2 * a * a + 4 * a * b + 4 * a * cc + 3 * b * b
                                  + 2 * b * cc + cc * cc) / 3.0)
    a2s = 18.0 * c * c / r ** 6 * (2.0 * S * S / 3.0)
    inner = float(np.sum(wr * 4.0 * math.pi * r * r * (a2p + a2s)))
    rm = rmax * sigma
    tail = 4.0 * math.pi * (7.5 * P * P / rm + 4.0 * S * S / rm ** 3)   # Bowen-York
    return (inner + tail) / (16.0 * math.pi) * psi ** -7
