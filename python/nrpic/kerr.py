"""Kerr spacetime reference functions: 3+1 fields, coordinate maps, invariants, orbit quadratures.

Independent Python reference implementation used to validate the NRPIC particle pushers.

Coordinate systems (string keys used everywhere in this module):

``'bl'``  Boyer-Lindquist ``(t, r, theta, phi)``.
``'ks'``  spherical Kerr-Schild (ingoing Kerr) ``(t, r, theta, phi)``, with
          ``g = g_flat + (2 M r / Sigma) l l`` and ``l = dt + dr - a sin^2(theta) dphi``.
``'cks'`` Cartesian Kerr-Schild ``(t, x, y, z)``, with
          ``x + i y = (r + i a) e^{i phi} sin(theta)``, ``z = r cos(theta)`` (``phi`` the KS azimuth),
          ``g = eta + 2 H l l``, ``H = M r^3 / (r^4 + a^2 z^2)``,
          ``l = (1, (r x + a y)/(r^2 + a^2), (r y - a x)/(r^2 + a^2), z / r)``.

``r`` and ``theta`` are the same in all three systems.  BL and KS are related by
``t_KS = t_BL + delta_t(r)``, ``phi_KS = phi_BL + delta_phi(r)`` with
``delta_t' = 2 M r / Delta`` and ``delta_phi' = a / Delta``.  The integration constants are fixed
here as (``r_pm = M +- sqrt(M^2 - a^2)``)::

    delta_t(r)   = 2 M / (r_+ - r_-) * [ r_+ ln((r - r_+)/M) - r_- ln((r - r_-)/M) ]
    delta_phi(r) = a / (r_+ - r_-) * ln((r - r_+)/(r - r_-))        (-> 0 as r -> infinity)

Signature ``(-,+,+,+)``, geometrized units.  Spatial positions are arrays ``(..., 3)`` and the
particle momentum is the covariant spatial four-velocity ``u_i`` (per unit rest mass), also
``(..., 3)``.  All numpy functions broadcast over leading dimensions and preserve the floating
dtype of the input (``np.longdouble`` works, which the tests use for finite differences).

3+1 field derivatives are analytic closed forms (no finite differencing); the test-suite checks
them against 8th-order central differences evaluated in extended precision.

The orbit quadratures (turning points, periods, the Mino-time solution ``MinoOrbit``) use mpmath
at a configurable working precision (default 30 digits).
"""

from __future__ import annotations

import math
from typing import NamedTuple

import mpmath as mp
import numpy as np

A_DEFAULT = 0.9
M_DEFAULT = 1.0
SYSTEMS = ("bl", "ks", "cks")

__all__ = [
    "A_DEFAULT", "M_DEFAULT", "SYSTEMS", "ADM", "horizon_radii",
    "adm_bl", "adm_ks", "adm_cks", "adm", "g4_bl", "g4_ks", "g4_cks", "g4",
    "g4_from_adm", "ginv4_from_adm", "delta_t", "delta_phi", "cks_radius",
    "ks_to_cks_position", "cks_to_ks_position", "jac_ks_to_cks", "jac_cks_to_ks",
    "jacobian4", "convert_event", "convert_state", "lorentz_factor", "energy", "carter_q",
    "invariants", "norm4", "dr_dt", "dtheta_dt", "radial_roots", "polar_roots", "orbit_periods",
    "MinoOrbit", "convert_state_mp",
]


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------

class ADM(NamedTuple):
    """3+1 fields at a point (arrays broadcast over leading dims ``...``).

    alpha     (...)          lapse
    beta      (..., 3)       shift beta^i
    gamma     (..., 3, 3)    spatial metric gamma_ij
    gamma_inv (..., 3, 3)    inverse spatial metric gamma^ij (closed form)
    dalpha    (..., 3)       [i]       = d_i alpha
    dbeta     (..., 3, 3)    [i, j]    = d_i beta^j
    dgamma    (..., 3, 3, 3) [i, j, k] = d_i gamma_jk
    The derivative fields are ``None`` when called with ``derivs=False``.
    """

    alpha: np.ndarray
    beta: np.ndarray
    gamma: np.ndarray
    gamma_inv: np.ndarray
    dalpha: np.ndarray | None
    dbeta: np.ndarray | None
    dgamma: np.ndarray | None


def _asfloat(x):
    x = np.asarray(x)
    if not np.issubdtype(x.dtype, np.floating):
        x = x.astype(float)
    return x


def _vec3(a, b, c):
    a, b, c = np.broadcast_arrays(a, b, c)
    return np.stack([a, b, c], axis=-1)


def _sym33(xx, xy, xz, yy, yz, zz):
    xx, xy, xz, yy, yz, zz = np.broadcast_arrays(xx, xy, xz, yy, yz, zz)
    return np.stack([np.stack([xx, xy, xz], -1),
                     np.stack([xy, yy, yz], -1),
                     np.stack([xz, yz, zz], -1)], -2)


def _mat33(rows):
    """rows: 3x3 nested list of broadcastable arrays -> (..., 3, 3) with [i, j] = rows[i][j]."""
    flat = np.broadcast_arrays(*[e for row in rows for e in row])
    return np.stack([np.stack(flat[3 * i:3 * i + 3], -1) for i in range(3)], -2)


def horizon_radii(a=A_DEFAULT, M=M_DEFAULT):
    """Return (r_+, r_-), the outer and inner horizon radii."""
    d = math.sqrt(M * M - a * a)
    return M + d, M - d


# ---------------------------------------------------------------------------------------------
# 3+1 metrics with analytic first derivatives
# ---------------------------------------------------------------------------------------------

def adm_bl(x, a=A_DEFAULT, M=M_DEFAULT, derivs=True):
    """3+1 fields of Kerr in Boyer-Lindquist coordinates; x = (r, theta, phi).

    alpha^2 = Sigma Delta / A, beta^phi = -2 M a r / A, gamma = diag(Sigma/Delta, Sigma,
    A sin^2 / Sigma), A = (r^2 + a^2)^2 - a^2 Delta sin^2.  Valid for r > r_+.
    """
    x = _asfloat(x)
    r, th = x[..., 0], x[..., 1]
    s, c = np.sin(th), np.cos(th)
    s2, c2, sc = s * s, c * c, s * c
    a2, r2 = a * a, r * r
    zero = np.zeros_like(r)
    Sig = r2 + a2 * c2
    Del = r2 - 2 * M * r + a2
    rpa = r2 + a2
    A = rpa * rpa - a2 * Del * s2
    alpha = np.sqrt(Sig * Del / A)
    bph = -2 * M * a * r / A
    beta = _vec3(zero, zero, bph)
    grr, gpp = Sig / Del, A * s2 / Sig
    gamma = _sym33(grr, zero, zero, Sig, zero, gpp)
    gamma_inv = _sym33(Del / Sig, zero, zero, 1 / Sig, zero, Sig / (A * s2))
    if not derivs:
        return ADM(alpha, beta, gamma, gamma_inv, None, None, None)
    Sr, Sth = 2 * r, -2 * a2 * sc
    Dr = 2 * r - 2 * M
    Ar = 4 * r * rpa - a2 * Dr * s2
    Ath = -2 * a2 * Del * sc
    al_r = 0.5 * alpha * (Sr / Sig + Dr / Del - Ar / A)
    al_th = 0.5 * alpha * (Sth / Sig - Ath / A)
    dalpha = _vec3(al_r, al_th, zero)
    bph_r = -2 * M * a / A + 2 * M * a * r * Ar / (A * A)
    bph_th = 2 * M * a * r * Ath / (A * A)
    dbeta = _mat33([[zero, zero, bph_r], [zero, zero, bph_th], [zero, zero, zero]])
    grr_r = Sr / Del - Sig * Dr / (Del * Del)
    grr_th = Sth / Del
    gpp_r = s2 * (Ar / Sig - A * Sr / (Sig * Sig))
    gpp_th = (Ath * s2 + 2 * A * sc) / Sig - A * s2 * Sth / (Sig * Sig)
    dg_r = _sym33(grr_r, zero, zero, Sr, zero, gpp_r)
    dg_th = _sym33(grr_th, zero, zero, Sth, zero, gpp_th)
    dgamma = np.stack([dg_r, dg_th, np.zeros_like(dg_r)], axis=-3)
    return ADM(alpha, beta, gamma, gamma_inv, dalpha, dbeta, dgamma)


def adm_ks(x, a=A_DEFAULT, M=M_DEFAULT, derivs=True):
    """3+1 fields of Kerr in spherical Kerr-Schild coordinates; x = (r, theta, phi).

    With z = 2 M r / Sigma: alpha = (1+z)^(-1/2), beta^r = z/(1+z), beta^theta = beta^phi = 0,
    gamma_rr = 1+z, gamma_thth = Sigma, gamma_rph = -a (1+z) sin^2,
    gamma_phph = sin^2 [Sigma + a^2 (1+z) sin^2].  Closed-form inverse:
    gamma^rr = 1/(1+z) + a^2 sin^2/Sigma, gamma^rph = a/Sigma, gamma^thth = 1/Sigma,
    gamma^phph = 1/(Sigma sin^2).  Regular for r > 0 off the ring.
    """
    x = _asfloat(x)
    r, th = x[..., 0], x[..., 1]
    s, c = np.sin(th), np.cos(th)
    s2, c2, sc = s * s, c * c, s * c
    a2, r2 = a * a, r * r
    zero = np.zeros_like(r)
    Sig = r2 + a2 * c2
    z = 2 * M * r / Sig
    opz = 1 + z
    alpha = 1 / np.sqrt(opz)
    beta = _vec3(z / opz, zero, zero)
    grr, grp, gpp = opz, -a * opz * s2, s2 * Sig + a2 * opz * s2 * s2
    gamma = _sym33(grr, zero, grp, Sig, zero, gpp)
    gamma_inv = _sym33(1 / opz + a2 * s2 / Sig, zero, a / Sig, 1 / Sig, zero, 1 / (Sig * s2))
    if not derivs:
        return ADM(alpha, beta, gamma, gamma_inv, None, None, None)
    Sr, Sth = 2 * r, -2 * a2 * sc
    zr = 2 * M * (a2 * c2 - r2) / (Sig * Sig)
    zth = 4 * M * r * a2 * sc / (Sig * Sig)
    f = -0.5 * opz ** -1.5
    dalpha = _vec3(f * zr, f * zth, zero)
    dbeta = _mat33([[zr / opz ** 2, zero, zero], [zth / opz ** 2, zero, zero], [zero, zero, zero]])
    grp_r = -a * zr * s2
    grp_th = -a * zth * s2 - 2 * a * opz * sc
    gpp_r = s2 * Sr + a2 * zr * s2 * s2
    gpp_th = 2 * sc * Sig + s2 * Sth + a2 * zth * s2 * s2 + 4 * a2 * opz * s2 * sc
    dg_r = _sym33(zr, zero, grp_r, Sr, zero, gpp_r)
    dg_th = _sym33(zth, zero, grp_th, Sth, zero, gpp_th)
    dgamma = np.stack([dg_r, dg_th, np.zeros_like(dg_r)], axis=-3)
    return ADM(alpha, beta, gamma, gamma_inv, dalpha, dbeta, dgamma)


def cks_radius(x, a=A_DEFAULT):
    """Kerr-Schild r from Cartesian KS (x, y, z): positive root of
    r^4 - (x^2 + y^2 + z^2 - a^2) r^2 - a^2 z^2 = 0 (cancellation-free form)."""
    x = _asfloat(x)
    X, Y, Z = x[..., 0], x[..., 1], x[..., 2]
    w = X * X + Y * Y + Z * Z - a * a
    disc = np.sqrt(w * w + 4 * a * a * Z * Z)
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = np.where(w >= 0, 0.5 * (w + disc), 2 * a * a * Z * Z / (disc - w))
    return np.sqrt(r2)


def _cks_r_grad(X, Y, Z, r, a):
    D4 = r ** 4 + a * a * Z * Z
    r3 = r ** 3
    return r3 * X / D4, r3 * Y / D4, r * (r * r + a * a) * Z / D4, D4


def adm_cks(x, a=A_DEFAULT, M=M_DEFAULT, derivs=True):
    """3+1 fields of Kerr in Cartesian Kerr-Schild coordinates; x = (x, y, z).

    alpha = (1+2H)^(-1/2), beta^i = 2 H l_i / (1+2H), gamma_ij = delta_ij + 2 H l_i l_j,
    gamma^ij = delta^ij - 2 H l_i l_j / (1+2H) (because delta^ij l_i l_j = 1).
    Derivatives use dr/dx = r^3 x / (r^4 + a^2 z^2), dr/dy = r^3 y / (...),
    dr/dz = r (r^2 + a^2) z / (...).
    """
    x = _asfloat(x)
    X, Y, Z = x[..., 0], x[..., 1], x[..., 2]
    a2 = a * a
    r = cks_radius(x, a)
    r2 = r * r
    q = r2 + a2
    D4 = r2 * r2 + a2 * Z * Z
    H = M * r2 * r / D4
    l = _vec3((r * X + a * Y) / q, (r * Y - a * X) / q, Z / r)
    opH = 1 + 2 * H
    alpha = 1 / np.sqrt(opH)
    beta = (2 * H / opH)[..., None] * l
    ll = l[..., :, None] * l[..., None, :]
    eye = np.eye(3, dtype=x.dtype)
    gamma = eye + (2 * H)[..., None, None] * ll
    gamma_inv = eye - (2 * H / opH)[..., None, None] * ll
    if not derivs:
        return ADM(alpha, beta, gamma, gamma_inv, None, None, None)
    rx, ry, rz, _ = _cks_r_grad(X, Y, Z, r, a)
    t1 = 3 * a2 * Z * Z - r2 * r2
    cH = M * r2 / (D4 * D4)
    dH = _vec3(cH * t1 * rx, cH * t1 * ry, cH * (t1 * rz - 2 * a2 * Z * r))
    lx, ly = l[..., 0], l[..., 1]
    zero = np.zeros_like(r)
    one = np.ones_like(r)
    grad_r = (rx, ry, rz)
    dl_rows = []
    for i, ri in enumerate(grad_r):
        dix = (one if i == 0 else zero)
        diy = (one if i == 1 else zero)
        diz = (one if i == 2 else zero)
        dlx = (ri * X + r * dix + a * diy) / q - 2 * r * ri * lx / q
        dly = (ri * Y + r * diy - a * dix) / q - 2 * r * ri * ly / q
        dlz = diz / r - Z * ri / r2
        dl_rows.append([dlx, dly, dlz])
    dl = _mat33(dl_rows)  # [i, j] = d_i l_j
    dalpha = -(opH ** -1.5)[..., None] * dH
    dbeta = (2 / opH ** 2)[..., None, None] * dH[..., :, None] * l[..., None, :] \
        + (2 * H / opH)[..., None, None] * dl
    dgamma = 2 * dH[..., :, None, None] * ll[..., None, :, :] \
        + (2 * H)[..., None, None, None] * (dl[..., :, :, None] * l[..., None, None, :]
                                            + l[..., None, :, None] * dl[..., :, None, :])
    return ADM(alpha, beta, gamma, gamma_inv, dalpha, dbeta, dgamma)


_ADM_FUNCS = {"bl": adm_bl, "ks": adm_ks, "cks": adm_cks}


def adm(system, x, a=A_DEFAULT, M=M_DEFAULT, derivs=True):
    """Dispatch to adm_bl / adm_ks / adm_cks by system key."""
    return _ADM_FUNCS[system](x, a, M, derivs)


# ---------------------------------------------------------------------------------------------
# independent closed-form 4-metrics (used only for validation)
# ---------------------------------------------------------------------------------------------

def _empty44(r):
    return np.zeros(r.shape + (4, 4), dtype=r.dtype)


def g4_bl(x, a=A_DEFAULT, M=M_DEFAULT):
    """Textbook Boyer-Lindquist 4-metric g_{mu nu}, x = (r, theta, phi); shape (..., 4, 4)."""
    x = _asfloat(x)
    r, th = x[..., 0], x[..., 1]
    s2, c2 = np.sin(th) ** 2, np.cos(th) ** 2
    Sig = r * r + a * a * c2
    Del = r * r - 2 * M * r + a * a
    g = _empty44(r)
    g[..., 0, 0] = -(1 - 2 * M * r / Sig)
    g[..., 0, 3] = g[..., 3, 0] = -2 * M * a * r * s2 / Sig
    g[..., 1, 1] = Sig / Del
    g[..., 2, 2] = Sig
    g[..., 3, 3] = (r * r + a * a + 2 * M * a * a * r * s2 / Sig) * s2
    return g


def g4_ks(x, a=A_DEFAULT, M=M_DEFAULT):
    """Spherical KS 4-metric built as g_flat + (2 M r / Sigma) l l, where g_flat is Minkowski in
    the oblate-spheroidal chart: -dt^2 + dr^2 - 2 a sin^2 dr dphi + Sigma dth^2
    + (r^2 + a^2) sin^2 dphi^2, and l = (1, 1, 0, -a sin^2)."""
    x = _asfloat(x)
    r, th = x[..., 0], x[..., 1]
    s2, c2 = np.sin(th) ** 2, np.cos(th) ** 2
    Sig = r * r + a * a * c2
    eta = _empty44(r)
    eta[..., 0, 0] = -1
    eta[..., 1, 1] = 1
    eta[..., 1, 3] = eta[..., 3, 1] = -a * s2
    eta[..., 2, 2] = Sig
    eta[..., 3, 3] = (r * r + a * a) * s2
    zero, one = np.zeros_like(r), np.ones_like(r)
    l = np.stack(np.broadcast_arrays(one, one, zero, -a * s2), -1)
    return eta + (2 * M * r / Sig)[..., None, None] * l[..., :, None] * l[..., None, :]


def g4_cks(x, a=A_DEFAULT, M=M_DEFAULT):
    """Cartesian KS 4-metric eta + 2 H l l; x = (x, y, z)."""
    x = _asfloat(x)
    X, Y, Z = x[..., 0], x[..., 1], x[..., 2]
    r = cks_radius(x, a)
    q = r * r + a * a
    H = M * r ** 3 / (r ** 4 + a * a * Z * Z)
    one = np.ones_like(r)
    l = np.stack(np.broadcast_arrays(one, (r * X + a * Y) / q, (r * Y - a * X) / q, Z / r), -1)
    eta = np.diag(np.array([-1.0, 1.0, 1.0, 1.0], dtype=x.dtype))
    return eta + (2 * H)[..., None, None] * l[..., :, None] * l[..., None, :]


_G4_FUNCS = {"bl": g4_bl, "ks": g4_ks, "cks": g4_cks}


def g4(system, x, a=A_DEFAULT, M=M_DEFAULT):
    """Closed-form 4-metric of the given system (independent of the 3+1 functions)."""
    return _G4_FUNCS[system](x, a, M)


def g4_from_adm(m: ADM):
    """Assemble g_{mu nu} from 3+1 fields: g_tt = -alpha^2 + beta_k beta^k, g_ti = gamma_ij beta^j."""
    beta_low = np.einsum("...ij,...j->...i", m.gamma, m.beta)
    g = np.zeros(m.alpha.shape + (4, 4), dtype=m.alpha.dtype)
    g[..., 0, 0] = -m.alpha ** 2 + np.einsum("...i,...i->...", beta_low, m.beta)
    g[..., 0, 1:] = beta_low
    g[..., 1:, 0] = beta_low
    g[..., 1:, 1:] = m.gamma
    return g


def ginv4_from_adm(m: ADM):
    """g^{mu nu} from 3+1 fields: g^tt = -1/alpha^2, g^ti = beta^i/alpha^2,
    g^ij = gamma^ij - beta^i beta^j / alpha^2."""
    ia2 = 1 / m.alpha ** 2
    g = np.zeros(m.alpha.shape + (4, 4), dtype=m.alpha.dtype)
    g[..., 0, 0] = -ia2
    g[..., 0, 1:] = ia2[..., None] * m.beta
    g[..., 1:, 0] = ia2[..., None] * m.beta
    g[..., 1:, 1:] = m.gamma_inv - ia2[..., None, None] * m.beta[..., :, None] * m.beta[..., None, :]
    return g


# ---------------------------------------------------------------------------------------------
# coordinate transformations
# ---------------------------------------------------------------------------------------------

def delta_t(r, a=A_DEFAULT, M=M_DEFAULT):
    """t_KS - t_BL as a function of r (> r_+); derivative 2 M r / Delta."""
    rp, rm = horizon_radii(a, M)
    r = _asfloat(r)
    return 2 * M / (rp - rm) * (rp * np.log((r - rp) / M) - rm * np.log((r - rm) / M))


def delta_phi(r, a=A_DEFAULT, M=M_DEFAULT):
    """phi_KS - phi_BL as a function of r (> r_+); derivative a / Delta; -> 0 at infinity."""
    rp, rm = horizon_radii(a, M)
    r = _asfloat(r)
    return a / (rp - rm) * np.log((r - rp) / (r - rm))


def ks_to_cks_position(x, a=A_DEFAULT):
    """(r, theta, phi_KS) -> Cartesian KS (x, y, z)."""
    x = _asfloat(x)
    r, th, ph = x[..., 0], x[..., 1], x[..., 2]
    s, c = np.sin(th), np.cos(th)
    cp, sp = np.cos(ph), np.sin(ph)
    return _vec3((r * cp - a * sp) * s, (r * sp + a * cp) * s, r * c)


def cks_to_ks_position(x, a=A_DEFAULT):
    """Cartesian KS (x, y, z) -> (r, theta, phi_KS); phi in (-pi - atan(a/r), pi - atan(a/r)]."""
    x = _asfloat(x)
    X, Y, Z = x[..., 0], x[..., 1], x[..., 2]
    r = cks_radius(x, a)
    rho = np.sqrt(X * X + Y * Y)
    th = np.arctan2(rho / np.sqrt(r * r + a * a), Z / r)
    ph = np.arctan2(Y, X) - np.arctan2(a, r)
    return _vec3(r, th, ph)


def jac_ks_to_cks(x, a=A_DEFAULT):
    """J[i, j] = d x_CKS^i / d q^j at spherical KS point q = (r, theta, phi)."""
    x = _asfloat(x)
    r, th, ph = x[..., 0], x[..., 1], x[..., 2]
    s, c = np.sin(th), np.cos(th)
    cp, sp = np.cos(ph), np.sin(ph)
    X = (r * cp - a * sp) * s
    Y = (r * sp + a * cp) * s
    zero = np.zeros_like(r)
    return _mat33([[cp * s, (r * cp - a * sp) * c, -Y],
                   [sp * s, (r * sp + a * cp) * c, X],
                   [c, -r * s, zero]])


def jac_cks_to_ks(x, a=A_DEFAULT):
    """K[i, j] = d q^i / d x_CKS^j at Cartesian KS point x, q = (r, theta, phi_KS) (closed form)."""
    x = _asfloat(x)
    X, Y, Z = x[..., 0], x[..., 1], x[..., 2]
    r = cks_radius(x, a)
    rx, ry, rz, _ = _cks_r_grad(X, Y, Z, r, a)
    q = r * r + a * a
    rho2 = X * X + Y * Y
    s = np.sqrt(rho2 / q)
    zero = np.zeros_like(r)
    # theta = arccos(Z / r):  d theta = -(1/sin) (dZ / r - Z dr / r^2)
    thx = Z * rx / (r * r * s)
    thy = Z * ry / (r * r * s)
    thz = -(1 / r - Z * rz / (r * r)) / s
    # phi = atan2(Y, X) - atan2(a, r)
    phx = -Y / rho2 + a * rx / q
    phy = X / rho2 + a * ry / q
    phz = a * rz / q
    return _mat33([[rx, ry, rz], [thx, thy, thz], [phx, phy, phz]])


def jacobian4(src, dst, x_src, a=A_DEFAULT, M=M_DEFAULT):
    """4x4 Jacobian d x_dst^mu / d x_src^nu at the source-system spatial position x_src.

    Only adjacent pairs are implemented directly ('bl'<->'ks', 'ks'<->'cks'); others are chained.
    """
    x_src = _asfloat(x_src)
    shape = x_src.shape[:-1]

    def eye4():
        return np.broadcast_to(np.eye(4, dtype=x_src.dtype), shape + (4, 4)).copy()

    if src == dst:
        return eye4()
    if (src, dst) in (("bl", "ks"), ("ks", "bl")):
        r = x_src[..., 0]
        Del = r * r - 2 * M * r + a * a
        sgn = 1.0 if src == "bl" else -1.0
        J = eye4()
        J[..., 0, 1] = sgn * 2 * M * r / Del
        J[..., 3, 1] = sgn * a / Del
        return J
    if (src, dst) == ("ks", "cks"):
        J = eye4()
        J[..., 1:, 1:] = jac_ks_to_cks(x_src, a)
        return J
    if (src, dst) == ("cks", "ks"):
        J = eye4()
        J[..., 1:, 1:] = jac_cks_to_ks(x_src, a)
        return J
    # chain through 'ks'
    _, x_mid = convert_event(0.0, x_src, src, "ks", a, M)
    return jacobian4("ks", dst, x_mid, a, M) @ jacobian4(src, "ks", x_src, a, M)


def convert_event(t, x, src, dst, a=A_DEFAULT, M=M_DEFAULT):
    """Convert an event (t, x^i) from system src to system dst.  Returns (t_dst, x_dst).

    BL <-> KS shifts t by delta_t(r) and phi by delta_phi(r); KS <-> CKS is purely spatial.
    Angles are not wrapped when going BL <-> KS (phi stays continuous along a trajectory).
    """
    t = np.asarray(t, dtype=float) if not isinstance(t, np.ndarray) else t
    x = _asfloat(x)
    if src == dst:
        return t, x.copy()
    path = {("bl", "ks"): ["ks"], ("ks", "bl"): ["bl"], ("ks", "cks"): ["cks"],
            ("cks", "ks"): ["ks"], ("bl", "cks"): ["ks", "cks"], ("cks", "bl"): ["ks", "bl"]}
    cur = src
    for nxt in path[(src, dst)]:
        if (cur, nxt) == ("bl", "ks"):
            r = x[..., 0]
            x = x.copy()
            x[..., 2] = x[..., 2] + delta_phi(r, a, M)
            t = t + delta_t(r, a, M)
        elif (cur, nxt) == ("ks", "bl"):
            r = x[..., 0]
            x = x.copy()
            x[..., 2] = x[..., 2] - delta_phi(r, a, M)
            t = t - delta_t(r, a, M)
        elif (cur, nxt) == ("ks", "cks"):
            x = ks_to_cks_position(x, a)
        elif (cur, nxt) == ("cks", "ks"):
            x = cks_to_ks_position(x, a)
        cur = nxt
    return t, x


def convert_state(t, x, u, src, dst, a=A_DEFAULT, M=M_DEFAULT, u_t=None):
    """Convert a particle state (t, x^i, u_i) between coordinate systems.

    The covariant four-velocity transforms as u^dst_mu = u^src_nu d x_src^nu / d x_dst^mu.
    u_t (= -E) is identical in the three systems; it is computed from the source 3+1 metric
    unless given.  BL -> KS:  u_r^KS = u_r^BL + (2 M r E - a L_z) / Delta, all other components
    unchanged.  KS <-> CKS: u_cks = (d q / d x_cks)^T u_ks and u_ks = (d x_cks / d q)^T u_cks.

    Returns (t_dst, x_dst, u_dst).
    """
    x = _asfloat(x)
    u = _asfloat(u)
    if u_t is None:
        u_t = -energy(src, x, u, a, M)
    t_dst, x_dst = convert_event(t, x, src, dst, a, M)
    if src == dst:
        return t_dst, x_dst, u.copy()
    # Build u in 'ks' first
    if src == "ks":
        u_ks, x_ks = u, x
    elif src == "bl":
        r = x[..., 0]
        Del = r * r - 2 * M * r + a * a
        u_ks = u.copy()
        u_ks[..., 0] = u[..., 0] - (2 * M * r / Del) * u_t - (a / Del) * u[..., 2]
        _, x_ks = convert_event(t, x, "bl", "ks", a, M)
    else:  # cks
        _, x_ks = convert_event(t, x, "cks", "ks", a, M)
        J = jac_ks_to_cks(x_ks, a)
        u_ks = np.einsum("...ij,...i->...j", J, u)
    if dst == "ks":
        return t_dst, x_dst, u_ks
    if dst == "bl":
        r = x_ks[..., 0]
        Del = r * r - 2 * M * r + a * a
        u_bl = u_ks.copy()
        u_bl[..., 0] = u_ks[..., 0] + (2 * M * r / Del) * u_t + (a / Del) * u_ks[..., 2]
        return t_dst, x_dst, u_bl
    K = jac_cks_to_ks(x_dst, a)
    u_cks = np.einsum("...ij,...i->...j", K, u_ks)
    return t_dst, x_dst, u_cks


# ---------------------------------------------------------------------------------------------
# invariants
# ---------------------------------------------------------------------------------------------

def lorentz_factor(m: ADM, u):
    """W = sqrt(1 + gamma^ij u_i u_j)."""
    return np.sqrt(1 + np.einsum("...i,...ij,...j->...", u, m.gamma_inv, u))


def energy(system, x, u, a=A_DEFAULT, M=M_DEFAULT):
    """E = -u_t = alpha W - beta^i u_i."""
    u = _asfloat(u)
    m = adm(system, x, a, M, derivs=False)
    return m.alpha * lorentz_factor(m, u) - np.einsum("...i,...i->...", m.beta, u)


def carter_q(E, Lz, theta, u_theta, a=A_DEFAULT):
    """Q = u_theta^2 + cos^2(theta) [a^2 (1 - E^2) + Lz^2 / sin^2(theta)]."""
    c2 = np.cos(theta) ** 2
    s2 = np.sin(theta) ** 2
    return u_theta ** 2 + c2 * (a * a * (1 - E * E) + Lz * Lz / s2)


def invariants(system, x, u, a=A_DEFAULT, M=M_DEFAULT):
    """Return (E, L_z, Q) for state(s) in any system.

    E from the 3+1 fields of that system; L_z = u_phi (CKS: x u_y - y u_x);
    u_theta and theta are taken from the spherical KS (= BL) representation.
    """
    x = _asfloat(x)
    u = _asfloat(u)
    E = energy(system, x, u, a, M)
    if system == "cks":
        xs = cks_to_ks_position(x, a)
        J = jac_ks_to_cks(xs, a)
        us = np.einsum("...ij,...i->...j", J, u)
        th, uth, Lz = xs[..., 1], us[..., 1], us[..., 2]
    else:
        th, uth, Lz = x[..., 1], u[..., 1], u[..., 2]
    return E, Lz, carter_q(E, Lz, th, uth, a)


def norm4(system, x, u_t, u, a=A_DEFAULT, M=M_DEFAULT):
    """g^{mu nu} u_mu u_nu with an independently supplied u_t (should be -1)."""
    m = adm(system, x, a, M, derivs=False)
    gi = ginv4_from_adm(m)
    u4 = np.concatenate([np.asarray(u_t, dtype=float)[..., None], _asfloat(u)], axis=-1)
    return np.einsum("...i,...ij,...j->...", u4, gi, u4)


def dr_dt(system, x, xdot, a=A_DEFAULT):
    """Coordinate-time derivative of the (common) radius r given dx^i/dt in any system."""
    x = _asfloat(x)
    if system in ("bl", "ks"):
        return xdot[..., 0]
    r = cks_radius(x, a)
    rx, ry, rz, _ = _cks_r_grad(x[..., 0], x[..., 1], x[..., 2], r, a)
    return rx * xdot[..., 0] + ry * xdot[..., 1] + rz * xdot[..., 2]


def dtheta_dt(system, x, xdot, a=A_DEFAULT):
    """Coordinate-time derivative of theta given dx^i/dt in any system."""
    x = _asfloat(x)
    if system in ("bl", "ks"):
        return xdot[..., 1]
    K = jac_cks_to_ks(x, a)
    return np.einsum("...j,...j->...", K[..., 1, :], xdot)


# ---------------------------------------------------------------------------------------------
# bound-orbit quadratures (mpmath)
# ---------------------------------------------------------------------------------------------
#
# Mino time lambda, d tau = Sigma d lambda:
#   (dr/dlambda)^2 = R(r)     = [E (r^2 + a^2) - a L]^2 - Delta [r^2 + (L - a E)^2 + Q]
#   (dth/dlambda)^2 = Theta   = Q - cos^2 th [a^2 (1 - E^2) + L^2 / sin^2 th]
#   dt/dlambda   = T_r(r) + T_th(th),  T_r = (r^2+a^2) P / Delta,  T_th = a L - a^2 E sin^2 th
#   dphi/dlambda = P_r(r) + P_th(th),  P_r = a P / Delta,          P_th = L / sin^2 th - a E
#   P = E (r^2 + a^2) - a L.
# Bound orbit: R = (1 - E^2)(r1 - r)(r - r2)(r - r3)(r - r4), r1 >= r2 >= r3 >= r4, r in [r2, r1].
# Singularity-free phases: r = p / (1 + e cos chi_r),  cos th = sqrt(z_-) cos chi_th, with
#   dchi_r/dlambda  = sqrt(1-E^2) p sqrt((1 - r3/r)(1 - r4/r)) / sqrt(1 - e^2)
#   dchi_th/dlambda = sqrt(beta (z_+ - z_- cos^2 chi_th)),  beta = a^2 (1 - E^2),
# where z_+- are the roots of beta z^2 - (Q + beta + L^2) z + Q (z = cos^2 th).
# Every integrand is a smooth even 2 pi-periodic function of its phase.

def _mpf(v):
    if isinstance(v, mp.mpf):
        return v
    if isinstance(v, (np.ndarray, np.generic)):
        v = float(v)
    return mp.mpf(v)


def radial_roots(E, Lz, Q, a=A_DEFAULT, M=M_DEFAULT, dps=30):
    """Roots r1 >= r2 >= r3 >= r4 of R(r) (mpmath mpf, real parts).  For a bound orbit
    r1 = apocenter and r2 = pericenter."""
    with mp.workdps(dps):
        E, Lz, Q, a, M = map(_mpf, (E, Lz, Q, a, M))
        co = [E * E - 1, 2 * M, a * a * (E * E - 1) - Lz * Lz - Q,
              2 * M * ((Lz - a * E) ** 2 + Q), -a * a * Q]
        rts = mp.polyroots(co, maxsteps=500, extraprec=4 * dps)
        if max(abs(mp.im(z)) for z in rts) > mp.mpf(10) ** (-dps // 2):
            raise ValueError("R(r) has complex roots: not a bound orbit with four turning points")
        return tuple(sorted((mp.re(z) for z in rts), reverse=True))


def polar_roots(E, Lz, Q, a=A_DEFAULT, dps=30):
    """(z_-, beta z_+) for z = cos^2 theta; z_- = cos^2 theta_min.  beta z_+ is returned instead
    of z_+ so that a -> 0 or E -> 1 stays finite."""
    with mp.workdps(dps):
        E, Lz, Q, a = map(_mpf, (E, Lz, Q, a))
        beta = a * a * (1 - E * E)
        B = Q + beta + Lz * Lz
        sq = mp.sqrt(B * B - 4 * beta * Q)
        return 2 * Q / (B + sq), (B + sq) / 2


class MinoOrbit:
    """Bound Kerr geodesic solved by quadrature in Mino time, to arbitrary precision.

    Independent of the 3+1 equations of motion: it uses only the first integrals E, L_z, Q.
    Construct with ``MinoOrbit.from_state(system, t0, x0, u0, a, M, dps)``.  Coordinate times
    in BL and KS are both available; positions/momenta can be returned in any system.
    """

    def __init__(self, E, Lz, Q, chi_r0, chi_th0, t0_bl=0, phi0_bl=0, a=A_DEFAULT, M=M_DEFAULT,
                 dps=30):
        self.dps = dps
        with mp.workdps(dps):
            self.E, self.L, self.Q, self.a, self.M = map(_mpf, (E, Lz, Q, a, M))
            self.r1, self.r2, self.r3, self.r4 = radial_roots(self.E, self.L, self.Q, self.a,
                                                              self.M, dps)
            if not (self.E < 1 and self.r2 > self.r3):
                raise ValueError("not a bound orbit")
            self.p = 2 * self.r1 * self.r2 / (self.r1 + self.r2)
            self.e = (self.r1 - self.r2) / (self.r1 + self.r2)
            self.zm, self.bzp = polar_roots(self.E, self.L, self.Q, self.a, dps)
            self.beta = self.a ** 2 * (1 - self.E ** 2)
            self.chi_r0, self.chi_th0 = _mpf(chi_r0), _mpf(chi_th0)
            self.t0, self.phi0 = _mpf(t0_bl), _mpf(phi0_bl)
            self._cr = mp.sqrt(1 - self.E ** 2) * self.p / mp.sqrt(1 - self.e ** 2)
            g = {
                "lr": lambda c: 1 / self._Fr(c),
                "tr": lambda c: self._Tr(self._r(c)) / self._Fr(c),
                "pr": lambda c: self._Pr(self._r(c)) / self._Fr(c),
                "lth": lambda c: 1 / self._Fth(c),
                "tth": lambda c: self._Tth(c) / self._Fth(c),
                "pth": lambda c: self._Pth(c) / self._Fth(c),
            }
            self._g = g
            self._I = {k: 2 * self._quad(f, mp.pi) for k, f in g.items()}
            self._G0 = {k: self._G(k, self.chi_r0 if k.endswith("r") else self.chi_th0)
                        for k in g}

    # ---- construction from a state ---------------------------------------------------------
    @classmethod
    def from_state(cls, system, t0, x0, u0, a=A_DEFAULT, M=M_DEFAULT, dps=30):
        """Build from a (double or mpf) state in 'bl', 'ks' or 'cks'.  The state is converted to
        BL in mpmath; E follows from u.u = -1 there."""
        with mp.workdps(dps + 10):
            a_, M_ = _mpf(a), _mpf(M)
            t, x, u, E = _mp_state_to_bl(system, t0, x0, u0, a_, M_)
            r, th, ph = x
            ur, uth, L = u
            Q = uth ** 2 + mp.cos(th) ** 2 * (a_ ** 2 * (1 - E ** 2) + L ** 2 / mp.sin(th) ** 2)
            r1, r2, r3, r4 = radial_roots(E, L, Q, a_, M_, dps + 10)
            p = 2 * r1 * r2 / (r1 + r2)
            e = (r1 - r2) / (r1 + r2)
            Del = r * r - 2 * M_ * r + a_ * a_
            cosx = (p / r - 1) / e
            sinx = Del * ur * (p / r) * mp.sqrt(1 - e * e) / (
                p * e * mp.sqrt(1 - E * E) * mp.sqrt((r - r3) * (r - r4)))
            chi_r0 = mp.atan2(sinx, cosx)
            zm, bzp = polar_roots(E, L, Q, a_, dps + 10)
            if zm == 0:
                chi_th0 = mp.mpf(0)
            else:
                beta = a_ ** 2 * (1 - E ** 2)
                c = mp.cos(th)
                cosy = c / mp.sqrt(zm)
                siny = uth * mp.sin(th) / (mp.sqrt(zm) * mp.sqrt(bzp - beta * c * c))
                chi_th0 = mp.atan2(siny, cosy)
        return cls(E, L, Q, chi_r0, chi_th0, t, ph, a_, M_, dps)

    # ---- elementary functions ----------------------------------------------------------------
    def _r(self, chi):
        return self.p / (1 + self.e * mp.cos(chi))

    def _Fr(self, chi):
        r = self._r(chi)
        return self._cr * mp.sqrt((1 - self.r3 / r) * (1 - self.r4 / r))

    def _Fth(self, chi):
        return mp.sqrt(self.bzp - self.beta * self.zm * mp.cos(chi) ** 2)

    def _Del(self, r):
        return r * r - 2 * self.M * r + self.a ** 2

    def _P(self, r):
        return self.E * (r * r + self.a ** 2) - self.a * self.L

    def _Tr(self, r):
        return (r * r + self.a ** 2) * self._P(r) / self._Del(r)

    def _Pr(self, r):
        return self.a * self._P(r) / self._Del(r)

    def _s2(self, chi):
        return 1 - self.zm * mp.cos(chi) ** 2

    def _Tth(self, chi):
        return self.a * self.L - self.a ** 2 * self.E * self._s2(chi)

    def _Pth(self, chi):
        return self.L / self._s2(chi) - self.a * self.E

    @staticmethod
    def _quad(f, y):
        if y == 0:
            return mp.mpf(0)
        return mp.quad(f, [0, y / 2, y])

    def _G(self, key, chi):
        """Integral of g_key from 0 to chi (uses periodicity and evenness)."""
        twopi = 2 * mp.pi
        n = mp.floor(chi / twopi)
        rem = chi - n * twopi
        I = self._I[key]
        if rem <= mp.pi:
            part = self._quad(self._g[key], rem)
        else:
            part = I - self._quad(self._g[key], twopi - rem)
        return (n * I if n != 0 else 0) + part

    def _chi_of_lambda(self, which, lam, guess=None):
        """Phase chi_r ('r') or chi_th ('th') at Mino time lam (safeguarded Newton)."""
        key = "l" + which
        F = self._Fr if which == "r" else self._Fth
        target = lam + self._G0[key]
        I = self._I[key]
        twopi = 2 * mp.pi
        n = mp.floor(target / I)
        lo, hi = n * twopi, (n + 1) * twopi
        chi = guess if guess is not None and lo <= guess <= hi else lo + twopi * (target - n * I) / I
        tol = mp.mpf(10) ** (-(self.dps - 3))
        for _ in range(200):
            f = self._G(key, chi) - target
            if f > 0:
                hi = chi
            else:
                lo = chi
            step = f * F(chi)
            new = chi - step
            if not (lo < new < hi):
                new = (lo + hi) / 2
            if abs(new - chi) < tol * (1 + abs(chi)):
                return new
            chi = new
        raise RuntimeError("chi(lambda) did not converge")

    # ---- public API --------------------------------------------------------------------------
    def periods(self):
        """Mino-time periods and coordinate-time periods (dict of mpf).

        Lambda_r, Lambda_th: Mino periods.  Gamma = <dt/dlambda> (Mino-time average).
        T_r = Gamma Lambda_r, T_th = Gamma Lambda_th: mean coordinate-time periods (identical
        for BL and KS time).  Omega_phi = <dphi/dlambda>/Gamma.  T_th is meaningless when Q = 0.
        """
        with mp.workdps(self.dps):
            Lr, Lth = self._I["lr"], self._I["lth"]
            Gamma = self._I["tr"] / Lr + self._I["tth"] / Lth
            Ups_phi = self._I["pr"] / Lr + self._I["pth"] / Lth
            return dict(Lambda_r=Lr, Lambda_th=Lth, Gamma=Gamma, T_r=Gamma * Lr, T_th=Gamma * Lth,
                        Omega_r=2 * mp.pi / (Gamma * Lr), Omega_th=2 * mp.pi / (Gamma * Lth),
                        Omega_phi=Ups_phi / Gamma)

    def at_lambda(self, lam, guess=None, need_phi=True):
        """BL state at Mino time lam measured from the initial event.  Returns a dict of mpf."""
        with mp.workdps(self.dps):
            lam = _mpf(lam)
            gr, gth = (guess or (None, None))
            cr = self._chi_of_lambda("r", lam, gr)
            cth = self._chi_of_lambda("th", lam, gth)
            r = self._r(cr)
            t = self.t0 + (self._G("tr", cr) - self._G0["tr"]) + (self._G("tth", cth) - self._G0["tth"])
            out = dict(lam=lam, chi_r=cr, chi_th=cth, t_bl=t, r=r)
            Del = self._Del(r)
            drdl = self.p * self.e * mp.sin(cr) / (1 + self.e * mp.cos(cr)) ** 2 * self._Fr(cr)
            out["dr_dlam"] = drdl
            out["dtbl_dlam"] = self._Tr(r) + self._Tth(cth)
            cos_th = mp.sqrt(self.zm) * mp.cos(cth)
            sin_th = mp.sqrt(self._s2(cth))
            out["theta"] = mp.atan2(sin_th, cos_th)
            out["u_r"] = drdl / Del
            out["u_th"] = mp.sqrt(self.zm) * mp.sin(cth) * self._Fth(cth) / sin_th
            out["u_ph"] = self.L
            out["u_t"] = -self.E
            if need_phi:
                out["phi_bl"] = self.phi0 + (self._G("pr", cr) - self._G0["pr"]) + \
                    (self._G("pth", cth) - self._G0["pth"])
            return out

    def _time_and_rate(self, st, system):
        if system == "bl":
            return st["t_bl"], st["dtbl_dlam"]
        r = st["r"]
        tks = st["t_bl"] + _mp_delta_t(r, self.a, self.M)
        return tks, st["dtbl_dlam"] + 2 * self.M * r / self._Del(r) * st["dr_dlam"]

    def lambda_at_time(self, t, system="bl", guess=None):
        """Mino time at which the coordinate time of `system` equals t (Newton on lambda)."""
        with mp.workdps(self.dps):
            t = _mpf(t)
            Gamma = self._I["tr"] / self._I["lr"] + self._I["tth"] / self._I["lth"]
            lam = _mpf(guess) if guess is not None else (t - self.t0) / Gamma
            tol = mp.mpf(10) ** (-(self.dps - 4))
            ph = None
            lo = hi = None  # bracket: t_sys(lo) < t < t_sys(hi); t_sys is increasing in lambda
            for _ in range(200):
                st = self.at_lambda(lam, ph, need_phi=False)
                ph = (st["chi_r"], st["chi_th"])
                ts, rate = self._time_and_rate(st, system)
                f = ts - t
                if f == 0:
                    return lam
                if f < 0:
                    lo = lam
                else:
                    hi = lam
                new = lam - f / rate
                if lo is not None and hi is not None and not (lo < new < hi):
                    new = (lo + hi) / 2
                if abs(new - lam) < tol * (1 + abs(lam)):
                    return new
                lam = new
            raise RuntimeError("lambda(t) did not converge")

    def state_at_time(self, t, system="bl", guess=None):
        """State at coordinate time t of `system` ('bl', 'ks' or 'cks').

        Returns (t, x, u, lam) with x, u as tuples of mpf in that system.
        """
        states, lam = self.states_at_time(t, system, (system,), guess)
        tt, x, u = states[system]
        return tt, x, u, lam

    def states_at_time(self, t, time_system="bl", systems=("bl",), guess=None):
        """State at coordinate time t of `time_system`, returned in each of `systems`.

        Returns ({system: (t_sys, x, u)}, lam) with mpf tuples.
        """
        with mp.workdps(self.dps):
            lam = self.lambda_at_time(t, time_system, guess)
            st = self.at_lambda(lam)
            x_bl = (st["r"], st["theta"], st["phi_bl"])
            u_bl = (st["u_r"], st["u_th"], st["u_ph"])
            out = {s: _mp_bl_to_system(s, st["t_bl"], x_bl, u_bl, self.E, self.a, self.M)
                   for s in systems}
            return out, lam

    def time_at_lambda(self, lam, system="bl"):
        """Coordinate time of `system` at Mino time lam."""
        with mp.workdps(self.dps):
            st = self.at_lambda(_mpf(lam), need_phi=False)
            return self._time_and_rate(st, system)[0]

    def pericenter_lambdas(self, lam_max):
        """Mino times of pericenter passages (chi_r = 2 pi k) in [0, lam_max]."""
        with mp.workdps(self.dps):
            k0 = mp.ceil(self.chi_r0 / (2 * mp.pi))
            out = []
            k = k0
            while True:
                lam = self._G("lr", 2 * mp.pi * k) - self._G0["lr"]
                if lam > lam_max:
                    return out
                if lam >= 0:
                    out.append(lam)
                k += 1


# ---- mpmath coordinate helpers --------------------------------------------------------------

def _mp_horizons(a, M):
    d = mp.sqrt(M * M - a * a)
    return M + d, M - d


def _mp_delta_t(r, a, M):
    rp, rm = _mp_horizons(a, M)
    return 2 * M / (rp - rm) * (rp * mp.log((r - rp) / M) - rm * mp.log((r - rm) / M))


def _mp_delta_phi(r, a, M):
    rp, rm = _mp_horizons(a, M)
    return a / (rp - rm) * mp.log((r - rp) / (r - rm))


def _mp_jac_ks_to_cks(r, th, ph, a):
    s, c, cp, sp = mp.sin(th), mp.cos(th), mp.cos(ph), mp.sin(ph)
    X = (r * cp - a * sp) * s
    Y = (r * sp + a * cp) * s
    return mp.matrix([[cp * s, (r * cp - a * sp) * c, -Y],
                      [sp * s, (r * sp + a * cp) * c, X],
                      [c, -r * s, 0]])


def _mp_energy_ks(r, th, u, a, M):
    s, c = mp.sin(th), mp.cos(th)
    Sig = r * r + a * a * c * c
    z = 2 * M * r / Sig
    ur, uth, uph = u
    W = mp.sqrt(1 + (1 / (1 + z) + a * a * s * s / Sig) * ur * ur + 2 * a / Sig * ur * uph
                + uth * uth / Sig + uph * uph / (Sig * s * s))
    return W / mp.sqrt(1 + z) - z / (1 + z) * ur


def _mp_state_to_bl(system, t, x, u, a, M):
    """Convert a state to BL in mpmath.  Returns (t, (r, th, ph), (u_r, u_th, u_ph), E)."""
    t = _mpf(t)
    x = [_mpf(v) for v in x]
    u = [_mpf(v) for v in u]
    if system == "bl":
        r, th, ph = x
        s, c = mp.sin(th), mp.cos(th)
        Sig = r * r + a * a * c * c
        Del = r * r - 2 * M * r + a * a
        A = (r * r + a * a) ** 2 - a * a * Del * s * s
        W = mp.sqrt(1 + Del / Sig * u[0] ** 2 + u[1] ** 2 / Sig + Sig / (A * s * s) * u[2] ** 2)
        E = mp.sqrt(Sig * Del / A) * W + 2 * M * a * r / A * u[2]
        return t, (r, th, ph), tuple(u), E
    if system == "cks":
        X, Y, Z = x
        w = X * X + Y * Y + Z * Z - a * a
        r = mp.sqrt((w + mp.sqrt(w * w + 4 * a * a * Z * Z)) / 2)
        th = mp.atan2(mp.sqrt(X * X + Y * Y) / mp.sqrt(r * r + a * a), Z / r)
        ph = mp.atan2(Y, X) - mp.atan2(a, r)
        J = _mp_jac_ks_to_cks(r, th, ph, a)
        uc = mp.matrix(u)
        uk = J.T * uc
        x = [r, th, ph]
        u = [uk[0], uk[1], uk[2]]
    # now spherical KS
    r, th, ph = x
    E = _mp_energy_ks(r, th, u, a, M)
    Del = r * r - 2 * M * r + a * a
    ur_bl = u[0] - (2 * M * r * E - a * u[2]) / Del
    return t - _mp_delta_t(r, a, M), (r, th, ph - _mp_delta_phi(r, a, M)), (ur_bl, u[1], u[2]), E


def _mp_bl_to_system(system, t, x, u, E, a, M):
    """Convert a BL state (mpf) to 'bl', 'ks' or 'cks'.  Returns (t, x, u) tuples of mpf."""
    if system == "bl":
        return t, tuple(x), tuple(u)
    r, th, ph = x
    Del = r * r - 2 * M * r + a * a
    tk = t + _mp_delta_t(r, a, M)
    phk = ph + _mp_delta_phi(r, a, M)
    uk = (u[0] + (2 * M * r * E - a * u[2]) / Del, u[1], u[2])
    if system == "ks":
        return tk, (r, th, phk), uk
    J = _mp_jac_ks_to_cks(r, th, phk, a)
    uc = mp.lu_solve(J.T, mp.matrix(uk))
    s, c, cp, sp = mp.sin(th), mp.cos(th), mp.cos(phk), mp.sin(phk)
    X = (r * cp - a * sp) * s
    Y = (r * sp + a * cp) * s
    return tk, (X, Y, r * c), (uc[0], uc[1], uc[2])


def convert_state_mp(t, x, u, src, dst, a=A_DEFAULT, M=M_DEFAULT, dps=30):
    """mpmath version of convert_state (inputs may be floats).  Returns (t, x, u, E) with
    mpf tuples; E = -u_t computed in the source system."""
    with mp.workdps(dps):
        a_, M_ = _mpf(a), _mpf(M)
        tb, xb, ub, E = _mp_state_to_bl(src, t, x, u, a_, M_)
        tt, xx, uu = _mp_bl_to_system(dst, tb, xb, ub, E, a_, M_)
        return tt, xx, uu, E


def orbit_periods(E, Lz, Q, a=A_DEFAULT, M=M_DEFAULT, dps=30):
    """Turning points and periods of a bound orbit with invariants (E, Lz, Q).

    Returns a dict of floats: r_apo, r_peri, r3, r4, p, e, theta_min (None if Q == 0),
    Lambda_r, Lambda_th, Gamma, T_r, T_th, Omega_r, Omega_th, Omega_phi.
    T_r and T_th are the Mino-averaged coordinate-time periods Gamma Lambda (exact for equatorial
    orbits; for inclined orbits the time between successive pericenters oscillates about T_r).
    """
    orb = MinoOrbit(E, Lz, Q, 0, 0, 0, 0, a, M, dps)
    per = orb.periods()
    with mp.workdps(dps):
        thmin = None if orb.zm == 0 else float(mp.acos(mp.sqrt(orb.zm)))
    out = dict(r_apo=float(orb.r1), r_peri=float(orb.r2), r3=float(orb.r3), r4=float(orb.r4),
               p=float(orb.p), e=float(orb.e), theta_min=thmin)
    for k, v in per.items():
        out[k] = float(v)
    if orb.zm == 0:
        out["T_th"] = out["Lambda_th"] = out["Omega_th"] = None
    return out
