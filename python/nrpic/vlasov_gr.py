"""Reference implementation and exact mathematical twin for the General-Relativistic
Lagrangian-Basis Vlasov (GR-LBV) method in the AthenaK NRPIC framework.

Units: G = c = 1, metric signature (-, +, +, +).
Canonical phase-space coordinates: (x^i, u_i) with covariant spatial 4-velocity u_i
and normal-observer Lorentz factor W = sqrt(1 + gamma^{ij} u_i u_j).
Rest-mass-weighted coordinate DF: f(t, x, u) = dM_0 / (d^3x d^3u), D = int f d^3u.

Every mathematical kernel here matches `athenak/src/particles/nrpic_vlasov_kernels.hpp`
to machine precision and serves for unit validation, exact quadrature cross-checks,
exact relativistic Taub/Synge shock solutions, and GRLBV001 binary IC/snapshot I/O.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import integrate, optimize, special

from . import collide as _coll
from . import kerr as _kerr
from . import oppenheimer_snyder as _osn
from . import sampling as _samp
from .st_cluster import STModel

GRLBV_MAGIC = b"GRLBV001"

BASIS_TOPHAT = 0
BASIS_GAUSS = 1

# ----------------------------------------------------------------------------
# Quadrature rules standardized to unit variance on [-sqrt(3), sqrt(3)] (Top-Hat)
# or standard normal (Gauss-Hermite)
# ----------------------------------------------------------------------------
_gl2_x, _gl2_w = np.polynomial.legendre.leggauss(2)
_gl3_x, _gl3_w = np.polynomial.legendre.leggauss(3)
_gl4_x, _gl4_w = np.polynomial.legendre.leggauss(4)
_gl6_x, _gl6_w = np.polynomial.legendre.leggauss(6)
_gh3_x, _gh3_w = np.polynomial.hermite_e.hermegauss(3)

# Standardized to mean 0, variance 1 on [-sqrt(3), sqrt(3)]
GL2_XI = _gl2_x * math.sqrt(3.0)
GL2_W = 0.5 * _gl2_w

GL3_XI = _gl3_x * math.sqrt(3.0)
GL3_W = 0.5 * _gl3_w

GH3_XI = _gh3_x
GH3_W = _gh3_w / math.sqrt(2.0 * math.pi)


def _tensor_2d(xi, w):
    x0, x1 = np.meshgrid(xi, xi, indexing="ij")
    w2 = w[:, None] * w[None, :]
    return np.stack([x0.ravel(), x1.ravel()], axis=-1), w2.ravel()


def _tensor_3d(xi, w):
    x0, x1, x2 = np.meshgrid(xi, xi, xi, indexing="ij")
    w3 = w[:, None, None] * w[None, :, None] * w[None, None, :]
    return np.stack([x0.ravel(), x1.ravel(), x2.ravel()], axis=-1), w3.ravel()


CUB_2D_GL2_XI, CUB_2D_GL2_W = _tensor_2d(GL2_XI, GL2_W)
CUB_2D_GL3_XI, CUB_2D_GL3_W = _tensor_2d(GL3_XI, GL3_W)
CUB_2D_GH3_XI, CUB_2D_GH3_W = _tensor_2d(GH3_XI, GH3_W)

CUB_3D_8_XI, CUB_3D_8_W = _tensor_3d(GL2_XI, GL2_W)
CUB_3D_27_XI, CUB_3D_27_W = _tensor_3d(GL3_XI, GL3_W)


# ----------------------------------------------------------------------------
# 3+1 Linear algebra & ADM metric helpers
# ----------------------------------------------------------------------------
@dataclass
class AdmState:
    alp: float
    beta: np.ndarray    # (3,) beta^i
    g: np.ndarray       # (3,3) gamma_{ij}
    dalp: np.ndarray    # (3,) d_k alpha
    dbeta: np.ndarray   # (3,3) d_k beta^i
    dg: np.ndarray      # (3,3,3) d_k gamma_{ij}

    @staticmethod
    def minkowski():
        return AdmState(
            alp=1.0,
            beta=np.zeros(3),
            g=np.eye(3),
            dalp=np.zeros(3),
            dbeta=np.zeros((3, 3)),
            dg=np.zeros((3, 3, 3)),
        )


def inv3_sym(g: np.ndarray):
    """Inverse and determinant of a symmetric 3x3 matrix."""
    c00 = g[1, 1] * g[2, 2] - g[1, 2] ** 2
    c01 = g[0, 2] * g[1, 2] - g[0, 1] * g[2, 2]
    c02 = g[0, 1] * g[1, 2] - g[0, 2] * g[1, 1]
    det = g[0, 0] * c00 + g[0, 1] * c01 + g[0, 2] * c02
    idet = 1.0 / det
    gi = np.empty((3, 3), dtype=np.float64)
    gi[0, 0] = c00 * idet
    gi[0, 1] = gi[1, 0] = c01 * idet
    gi[0, 2] = gi[2, 0] = c02 * idet
    gi[1, 1] = (g[0, 0] * g[2, 2] - g[0, 2] ** 2) * idet
    gi[1, 2] = gi[2, 1] = (g[0, 1] * g[0, 2] - g[0, 0] * g[1, 2]) * idet
    gi[2, 2] = (g[0, 0] * g[1, 1] - g[0, 1] ** 2) * idet
    return gi, float(det)


def chol3_safe(S: np.ndarray, tol: float = 1e-28):
    """Cholesky factor L of symmetric positive semi-definite 3x3 matrix S = L @ L.T."""
    A = 0.5 * (S + S.T)
    L = np.zeros((3, 3), dtype=np.float64)
    d0 = max(float(A[0, 0]), 0.0)
    if d0 > tol:
        L[0, 0] = math.sqrt(d0)
        L[1, 0] = A[1, 0] / L[0, 0]
        L[2, 0] = A[2, 0] / L[0, 0]
    d1 = max(float(A[1, 1] - L[1, 0] ** 2), 0.0)
    if d1 > tol:
        L[1, 1] = math.sqrt(d1)
        L[2, 1] = (A[2, 1] - L[2, 0] * L[1, 0]) / L[1, 1]
    d2 = max(float(A[2, 2] - L[2, 0] ** 2 - L[2, 1] ** 2), 0.0)
    if d2 > tol:
        L[2, 2] = math.sqrt(d2)
    return L


def chol2_safe(S2: np.ndarray, tol: float = 1e-28):
    """2D Cholesky L2 and L2^{-1} (0 on zero-variance directions) for 2x2 PSD matrix."""
    A = 0.5 * (S2 + S2.T)
    L = np.zeros((2, 2), dtype=np.float64)
    Li = np.zeros((2, 2), dtype=np.float64)
    d0 = max(float(A[0, 0]), 0.0)
    if d0 > tol:
        L[0, 0] = math.sqrt(d0)
        Li[0, 0] = 1.0 / L[0, 0]
        L[1, 0] = A[1, 0] / L[0, 0]
    d1 = max(float(A[1, 1] - L[1, 0] ** 2), 0.0)
    if d1 > tol:
        L[1, 1] = math.sqrt(d1)
        Li[1, 1] = 1.0 / L[1, 1]
        if L[0, 0] > 0.0:
            Li[1, 0] = -L[1, 0] * Li[0, 0] * Li[1, 1]
    return L, Li


def face_triad(g: np.ndarray, A_cov: np.ndarray):
    """Orthonormal right-handed face triad wrt spatial metric g_{ij}.

    Returns
    -------
    normA : float
        ||A||_gamma = sqrt(gamma^{ij} A_i A_j).
    e_up : (3, 3) ndarray
        e_up[a, i] = hat{e}_{(a)}^i, orthonormal vectors (e_up @ g @ e_up.T = I_3),
        with e_up[0, i] = gamma^{ij} A_j / normA.
    e_dn : (3, 3) ndarray
        e_dn[a, i] = e^{(a)}_i = g_{ij} e_up[a, j] (coframe covectors).
    """
    gi, det = inv3_sym(g)
    A_up = gi @ A_cov
    normA2 = max(float(np.dot(A_cov, A_up)), 0.0)
    normA = math.sqrt(normA2)
    if normA == 0.0:
        raise ValueError("Zero face area covector")
    e1 = A_up / normA
    # Pick coordinate axis least aligned with e1 (largest Euclidean residual)
    k0 = 0
    if abs(e1[1]) + 1e-10 < abs(e1[0]):
        k0 = 1
    if abs(e1[2]) + 1e-10 < abs(e1[k0]):
        k0 = 2
    v = np.zeros(3, dtype=np.float64)
    v[k0] = 1.0
    proj = float(v @ g @ e1)
    t2 = v - proj * e1
    n2 = math.sqrt(max(float(t2 @ g @ t2), 1e-300))
    e2 = t2 / n2
    # Right-handed metric-orthonormal third vector:
    # e_{(3),l} = sqrt(det) * eps_{ljk} hat{e}_{(1)}^j hat{e}_{(2)}^k,
    # hat{e}_{(3)}^i = gamma^{il} e_{(3),l}
    cross_cov = np.cross(e1, e2)
    e3 = (gi @ cross_cov) * math.sqrt(det)
    # Re-normalize e3 for machine precision
    e3 = e3 / math.sqrt(float(e3 @ g @ e3))
    e_up = np.vstack([e1, e2, e3])
    e_dn = e_up @ g
    return normA, e_up, e_dn


# ----------------------------------------------------------------------------
# Exact 1D-sliced + 2D-cubature relativistic one-sided vacuum Riemann flux
# ----------------------------------------------------------------------------
def _gl4_1d_moments(u_lo: float, b_r: float, m_perp: float, beta_F: float):
    """4-point (or 6-point) Gauss-Legendre moments of (1, u, u^2, W) * (u/W - beta_F)
    over [u_lo, b_r], divided by (b_r - u_lo) and multiplied by fraction (b_r-u_lo)/(2*sqrt(3)*s).
    Here we compute the integral over [u_lo, b_r] directly."""
    half = 0.5 * (b_r - u_lo)
    mid = 0.5 * (b_r + u_lo)
    u = mid + half * _gl6_x
    w = half * _gl6_w
    W = np.sqrt(m_perp * m_perp + u * u)
    flux = u / W - beta_F
    f0 = flux
    f1 = u * flux
    f2 = (u * u) * flux
    fE = W * flux
    return (
        float(np.dot(w, f0)),
        float(np.dot(w, f1)),
        float(np.dot(w, f2)),
        float(np.dot(w, fE)),
    )


def _antideriv_1d_moments(u_lo: float, b_r: float, m_perp: float, beta_F: float):
    """Exact antiderivative evaluation on [u_lo, b_r] for integral of
    (1, u, u^2, W) * (u/W - beta_F)."""
    def F(u):
        W = math.sqrt(m_perp * m_perp + u * u)
        ash = math.asinh(u / m_perp)
        m2 = m_perp * m_perp
        F0 = W - beta_F * u
        F1 = 0.5 * (u * W - m2 * ash) - 0.5 * beta_F * (u * u)
        F2 = (W * (u * u - 2.0 * m2)) / 3.0 - (beta_F * u * u * u) / 3.0
        FE = 0.5 * (u * u) - 0.5 * beta_F * (u * W + m2 * ash)
        return F0, F1, F2, FE

    a0, a1, a2, aE = F(u_lo)
    b0, b1, b2, bE = F(b_r)
    return b0 - a0, b1 - a1, b2 - a2, bE - aE


def _slice_tophat_1d(mu_par: float, s_par: float, m_perp: float, beta_F: float):
    """Return (I_0, I_1, I_2, I_E) for a 1D Top-Hat conditional distribution
    on [mu_par - sqrt(3)*s_par, mu_par + sqrt(3)*s_par], integrated over u > u_star."""
    if beta_F >= 1.0:
        return 0.0, 0.0, 0.0, 0.0
    has_cut = beta_F > -1.0
    u_star = (beta_F * m_perp / math.sqrt(1.0 - beta_F * beta_F)) if has_cut else -math.inf

    if s_par <= 1e-14 * max(m_perp, abs(mu_par)):
        if has_cut and mu_par <= u_star:
            return 0.0, 0.0, 0.0, 0.0
        W = math.sqrt(m_perp * m_perp + mu_par * mu_par)
        fl = mu_par / W - beta_F
        return fl, mu_par * fl, (mu_par * mu_par) * fl, W * fl

    hw = math.sqrt(3.0) * s_par
    a_r = mu_par - hw
    b_r = mu_par + hw
    u_lo = max(a_r, u_star) if has_cut else a_r
    if u_lo >= b_r:
        return 0.0, 0.0, 0.0, 0.0

    inv_width = 1.0 / (2.0 * hw)
    if (b_r - u_lo) < 0.25 * m_perp:
        j0, j1, j2, jE = _gl4_1d_moments(u_lo, b_r, m_perp, beta_F)
    else:
        j0, j1, j2, jE = _antideriv_1d_moments(u_lo, b_r, m_perp, beta_F)
    return j0 * inv_width, j1 * inv_width, j2 * inv_width, jE * inv_width


def _slice_gaussian_1d(mu_par: float, s_par: float, m_perp: float, beta_F: float):
    """1D Gaussian conditional integral on [u_star, inf) using adaptive quadrature
    when s_par > 0 (for Gaussian basis cross-checks)."""
    if beta_F >= 1.0:
        return 0.0, 0.0, 0.0, 0.0
    has_cut = beta_F > -1.0
    u_star = (beta_F * m_perp / math.sqrt(1.0 - beta_F * beta_F)) if has_cut else -math.inf
    if s_par <= 1e-14 * max(m_perp, abs(mu_par)):
        if has_cut and mu_par <= u_star:
            return 0.0, 0.0, 0.0, 0.0
        W = math.sqrt(m_perp * m_perp + mu_par * mu_par)
        fl = mu_par / W - beta_F
        return fl, mu_par * fl, (mu_par * mu_par) * fl, W * fl

    lo = max(mu_par - 12.0 * s_par, u_star) if has_cut else mu_par - 12.0 * s_par
    hi = mu_par + 12.0 * s_par
    if lo >= hi:
        return 0.0, 0.0, 0.0, 0.0
    # 16-point Gauss-Legendre in standardized z = (u - mu_par)/s_par over truncated [lo, hi]
    gl_x, gl_w = np.polynomial.legendre.leggauss(24)
    half = 0.5 * (hi - lo)
    mid = 0.5 * (hi + lo)
    u = mid + half * gl_x
    w = half * gl_w
    z = (u - mu_par) / s_par
    pdf = np.exp(-0.5 * z * z) / (math.sqrt(2.0 * math.pi) * s_par)
    W = np.sqrt(m_perp * m_perp + u * u)
    fl = (u / W - beta_F) * pdf
    return (
        float(np.dot(w, fl)),
        float(np.dot(w, u * fl)),
        float(np.dot(w, (u * u) * fl)),
        float(np.dot(w, W * fl)),
    )


def _slice_tophat_1d_vec(mu_par: np.ndarray, s_par: float, m_perp: np.ndarray, beta_F: float):
    """Vectorized 1D Top-Hat conditional moments (I_0, I_1, I_2, I_E) over arrays
    mu_par[R], m_perp[R]."""
    R = len(mu_par)
    I0 = np.zeros(R, dtype=np.float64)
    I1 = np.zeros(R, dtype=np.float64)
    I2 = np.zeros(R, dtype=np.float64)
    IE = np.zeros(R, dtype=np.float64)
    if beta_F >= 1.0:
        return I0, I1, I2, IE

    has_cut = beta_F > -1.0
    if has_cut:
        u_star = (beta_F / math.sqrt(1.0 - beta_F * beta_F)) * m_perp
    else:
        u_star = np.full(R, -math.inf)

    if s_par <= 1e-14 * max(float(np.max(m_perp)), float(np.max(np.abs(mu_par)))):
        active = (mu_par > u_star) if has_cut else np.ones(R, dtype=bool)
        if np.any(active):
            u = mu_par[active]
            W = np.sqrt(m_perp[active] ** 2 + u * u)
            fl = u / W - beta_F
            I0[active] = fl
            I1[active] = u * fl
            I2[active] = (u * u) * fl
            IE[active] = W * fl
        return I0, I1, I2, IE

    hw = math.sqrt(3.0) * s_par
    a_r = mu_par - hw
    b_r = mu_par + hw
    u_lo = np.maximum(a_r, u_star) if has_cut else a_r
    active = u_lo < b_r
    if not np.any(active):
        return I0, I1, I2, IE

    inv_w = 1.0 / (2.0 * hw)
    du = b_r - u_lo
    small = active & (du < 0.25 * m_perp)
    large = active & (~small)

    if np.any(large):
        ul = u_lo[large]
        ur = b_r[large]
        mp = m_perp[large]
        mp2 = mp * mp
        Wl = np.sqrt(mp2 + ul * ul)
        Wr = np.sqrt(mp2 + ur * ur)
        al = np.arcsinh(ul / mp)
        ar_s = np.arcsinh(ur / mp)
        I0[large] = ((Wr - beta_F * ur) - (Wl - beta_F * ul)) * inv_w
        I1[large] = (0.5 * (ur * Wr - mp2 * ar_s - beta_F * ur * ur)
                     - 0.5 * (ul * Wl - mp2 * al - beta_F * ul * ul)) * inv_w
        I2[large] = ((Wr * (ur * ur - 2.0 * mp2) - beta_F * ur ** 3)
                     - (Wl * (ul * ul - 2.0 * mp2) - beta_F * ul ** 3)) * (inv_w / 3.0)
        IE[large] = (0.5 * (ur * ur - beta_F * (ur * Wr + mp2 * ar_s))
                     - 0.5 * (ul * ul - beta_F * (ul * Wl + mp2 * al))) * inv_w

    if np.any(small):
        idx = np.where(small)[0]
        half = 0.5 * (b_r[idx] - u_lo[idx])[:, None]
        mid = 0.5 * (b_r[idx] + u_lo[idx])[:, None]
        u = mid + half * _gl6_x[None, :]
        w = half * _gl6_w[None, :] * inv_w
        mp2 = (m_perp[idx] ** 2)[:, None]
        W = np.sqrt(mp2 + u * u)
        fl = u / W - beta_F
        I0[idx] = np.sum(w * fl, axis=1)
        I1[idx] = np.sum(w * u * fl, axis=1)
        I2[idx] = np.sum(w * (u * u) * fl, axis=1)
        IE[idx] = np.sum(w * W * fl, axis=1)

    return I0, I1, I2, IE


def _slice_tophat_I0_arrays(
    w: np.ndarray, mu: np.ndarray, sp: np.ndarray, mp: np.ndarray, beta_F: float
) -> float:
    """Fast vectorized 1D Top-Hat mass-flux integral sum_q w_q I_0(mu_q, s_q, m_q; beta_F)."""
    if beta_F >= 1.0 or len(w) == 0:
        return 0.0
    has_cut = beta_F > -1.0
    u_star_fac = (beta_F / math.sqrt(max(1.0 - beta_F * beta_F, 1e-300))) if has_cut else 0.0
    cold = sp <= 1e-14 * np.maximum(mp, np.abs(mu))
    out = 0.0
    if np.any(cold):
        wc = w[cold]
        muc = mu[cold]
        mc = mp[cold]
        act = (muc > u_star_fac * mc) if has_cut else np.ones(len(wc), dtype=bool)
        if np.any(act):
            ua = muc[act]
            Wa = np.sqrt(mc[act] ** 2 + ua * ua)
            out += float(np.sum(wc[act] * (ua / Wa - beta_F)))
    warm = ~cold
    if np.any(warm):
        ww = w[warm]
        muw = mu[warm]
        spw = sp[warm]
        mw = mp[warm]
        hw = math.sqrt(3.0) * spw
        a_r = muw - hw
        b_r = muw + hw
        u_lo = np.maximum(a_r, u_star_fac * mw) if has_cut else a_r
        act = u_lo < b_r
        if np.any(act):
            ul = u_lo[act]
            ur = b_r[act]
            ma = mw[act]
            wa = ww[act]
            inv_w = 1.0 / (2.0 * hw[act])
            du = ur - ul
            small = du < 0.25 * ma
            large = ~small
            if np.any(large):
                ul_l = ul[large]
                ur_l = ur[large]
                mp2 = ma[large] ** 2
                Wl = np.sqrt(mp2 + ul_l * ul_l)
                Wr = np.sqrt(mp2 + ur_l * ur_l)
                out += float(np.sum(wa[large] * inv_w[large] * ((Wr - beta_F * ur_l) - (Wl - beta_F * ul_l))))
            if np.any(small):
                half = 0.5 * du[small][:, None]
                mid = 0.5 * (ur[small] + ul[small])[:, None]
                uq = mid + half * _gl6_x[None, :]
                wq = half * _gl6_w[None, :] * (wa[small] * inv_w[small])[:, None]
                Wq = np.sqrt((ma[small] ** 2)[:, None] + uq * uq)
                out += float(np.sum(wq * (uq / Wq - beta_F)))
    return out


def onesided_flux_tetrad(
    D_star: float,
    u_bar_tet: np.ndarray,
    Sigma_tet: np.ndarray,
    beta_F: float,
    basis_kind: int = BASIS_TOPHAT,
    n_perp: int = 3,
):
    """Exact 1D-sliced + 2D-cubature one-sided relativistic flux in the face triad.

    Returns (F_m, F_P_tet[3], F_Pi_tet[3,3], F_E) ALREADY multiplied by D_star,
    without the outer metric factor (alpha_f * ||A||_gamma).
    """
    if D_star <= 0.0 or beta_F >= 1.0:
        return 0.0, np.zeros(3), np.zeros((3, 3)), 0.0

    sig_par2 = max(float(Sigma_tet[0, 0]), 0.0)
    c = Sigma_tet[1:3, 0]
    S_pp = Sigma_tet[1:3, 1:3]
    L_p, L_pi = chol2_safe(S_pp)
    g_vec = L_pi @ c
    s_par2 = max(sig_par2 - float(np.dot(g_vec, g_vec)), 0.0)
    s_par = math.sqrt(s_par2)

    cold_perp = float(S_pp[0, 0] + S_pp[1, 1]) <= 1e-28
    if basis_kind == BASIS_TOPHAT:
        if cold_perp:
            xi_2d = np.zeros((1, 2))
            w_2d = np.array([1.0])
        elif n_perp == 3:
            xi_2d, w_2d = CUB_2D_GL3_XI, CUB_2D_GL3_W
        else:
            xi_2d, w_2d = CUB_2D_GL2_XI, CUB_2D_GL2_W

        u_perp = u_bar_tet[1:3][None, :] + xi_2d @ L_p.T
        m_perp = np.sqrt(1.0 + u_perp[:, 0] ** 2 + u_perp[:, 1] ** 2)
        mu_par = u_bar_tet[0] + xi_2d @ g_vec
        I0, I1, I2, IE = _slice_tophat_1d_vec(mu_par, s_par, m_perp, beta_F)
        wD = w_2d * D_star
        w0 = wD * I0
        w1 = wD * I1
        Fm = float(np.sum(w0))
        u1 = u_perp[:, 0]
        u2 = u_perp[:, 1]
        FP = np.array([float(np.sum(w1)), float(np.sum(w0 * u1)), float(np.sum(w0 * u2))])
        p01 = float(np.sum(w1 * u1))
        p02 = float(np.sum(w1 * u2))
        p12 = float(np.sum(w0 * u1 * u2))
        FPi = np.array([
            [float(np.sum(wD * I2)), p01, p02],
            [p01, float(np.sum(w0 * u1 * u1)), p12],
            [p02, p12, float(np.sum(w0 * u2 * u2))],
        ])
        FE = float(np.sum(wD * IE))
        return Fm, FP, FPi, FE

    # Gaussian basis
    if cold_perp:
        xi_2d = np.zeros((1, 2))
        w_2d = np.array([1.0])
    else:
        xi_2d, w_2d = CUB_2D_GH3_XI, CUB_2D_GH3_W

    Fm = 0.0
    FP = np.zeros(3, dtype=np.float64)
    FPi = np.zeros((3, 3), dtype=np.float64)
    FE = 0.0
    for eta, wr in zip(xi_2d, w_2d):
        u_perp = u_bar_tet[1:3] + L_p @ eta
        m_perp = math.sqrt(1.0 + float(u_perp[0] ** 2 + u_perp[1] ** 2))
        mu_par = float(u_bar_tet[0] + np.dot(g_vec, eta))
        I0, I1, I2, IE = _slice_gaussian_1d(mu_par, s_par, m_perp, beta_F)
        if I0 == 0.0 and I1 == 0.0 and I2 == 0.0:
            continue
        wD = wr * D_star
        Fm += wD * I0
        FP[0] += wD * I1
        FP[1] += wD * u_perp[0] * I0
        FP[2] += wD * u_perp[1] * I0
        FPi[0, 0] += wD * I2
        FPi[0, 1] += wD * u_perp[0] * I1
        FPi[1, 0] += wD * u_perp[0] * I1
        FPi[0, 2] += wD * u_perp[1] * I1
        FPi[2, 0] += wD * u_perp[1] * I1
        FPi[1, 1] += wD * (u_perp[0] * u_perp[0]) * I0
        FPi[1, 2] += wD * (u_perp[0] * u_perp[1]) * I0
        FPi[2, 1] += wD * (u_perp[0] * u_perp[1]) * I0
        FPi[2, 2] += wD * (u_perp[1] * u_perp[1]) * I0
        FE += wD * IE

    return Fm, FP, FPi, FE


def onesided_flux_coord(
    D_star: float,
    u_bar_cov: np.ndarray,
    Sigma_cov: np.ndarray,
    alpha_f: float,
    normA: float,
    e_up: np.ndarray,
    e_dn: np.ndarray,
    beta_F: float,
    basis_kind: int = BASIS_TOPHAT,
    n_perp: int = 3,
):
    """Evaluate one-sided relativistic flux and rotate back to coordinate covector indices."""
    u_tet = e_up @ u_bar_cov
    Sig_tet = e_up @ Sigma_cov @ e_up.T
    Fm, FP_tet, FPi_tet, FE = onesided_flux_tetrad(
        D_star, u_tet, Sig_tet, beta_F, basis_kind=basis_kind, n_perp=n_perp
    )
    fac = alpha_f * normA
    return (
        fac * Fm,
        fac * (e_dn.T @ FP_tet),
        fac * (e_dn.T @ FPi_tet @ e_dn),
        fac * FE,
    )


def onesided_flux_newtonian_tophat(
    rho_star: float,
    v_bar: np.ndarray,
    S_mat: np.ndarray,
    A_vec: np.ndarray,
    v_F_n: float,
):
    """Exact Hopkins (2026) Eq. (44)-(45) non-relativistic Top-Hat flux for limit tests."""
    normA = float(np.linalg.norm(A_vec))
    n_hat = A_vec / normA
    u_x = float(np.dot(v_bar, n_hat) - v_F_n)
    S_x = S_mat @ n_hat
    sig_x = math.sqrt(max(float(n_hat @ S_mat @ n_hat), 0.0))
    c_x = math.sqrt(3.0) * sig_x

    if c_x <= 1e-15:
        if u_x <= 0.0:
            return 0.0, np.zeros(3), np.zeros((3, 3))
        w_t, zeta, omega = u_x, 1.0, 0.0
    elif u_x <= -c_x:
        return 0.0, np.zeros(3), np.zeros((3, 3))
    elif u_x >= c_x:
        w_t, zeta, omega = u_x, 1.0, 0.0
    else:
        up = u_x / c_x
        w_t = 0.25 * c_x * (1.0 + up) ** 2
        zeta = 0.25 * (2.0 - up) * (1.0 + up) ** 2
        omega = (math.sqrt(3.0) / 8.0) * (1.0 - up * up) ** 2

    fac = rho_star * normA
    Fm = fac * w_t
    Fp = fac * (v_bar * w_t + S_x * zeta)
    vvS = np.outer(v_bar, v_bar) + S_mat
    cond = (np.outer(S_x, S_x) / sig_x * omega) if sig_x > 1e-15 else 0.0
    FT = fac * (vvS * w_t + (np.outer(v_bar, S_x) + np.outer(S_x, v_bar)) * zeta + cond)
    return Fm, Fp, FT


def _precompute_face_I0_side(D_vec, u_tet, Sig_tet, basis_kind: int, n_perp: int):
    """Precompute flat (w, mu_par, s_par, m_perp) arrays once per face side for fast Brent."""
    if basis_kind == BASIS_TOPHAT:
        xi_full, w_full = (CUB_2D_GL3_XI, CUB_2D_GL3_W) if n_perp == 3 else (CUB_2D_GL2_XI, CUB_2D_GL2_W)
    else:
        xi_full, w_full = CUB_2D_GH3_XI, CUB_2D_GH3_W
    w_list, mu_list, sp_list, mp_list = [], [], [], []
    for al in range(len(D_vec)):
        Da = float(D_vec[al])
        if Da <= 0.0:
            continue
        Sa = Sig_tet[al]
        sig_par2 = max(float(Sa[0, 0]), 0.0)
        c = Sa[1:3, 0]
        S_pp = Sa[1:3, 1:3]
        L_p, L_pi = chol2_safe(S_pp)
        g_vec = L_pi @ c
        s_par = math.sqrt(max(sig_par2 - float(np.dot(g_vec, g_vec)), 0.0))
        if float(S_pp[0, 0] + S_pp[1, 1]) <= 1e-28:
            up = u_tet[al, 1:3]
            mp = math.sqrt(1.0 + float(up[0] * up[0] + up[1] * up[1]))
            w_list.append(np.array([Da]))
            mu_list.append(np.array([float(u_tet[al, 0])]))
            sp_list.append(np.array([s_par]))
            mp_list.append(np.array([mp]))
        else:
            up = u_tet[al, 1:3][None, :] + xi_full @ L_p.T
            mp = np.sqrt(1.0 + up[:, 0] ** 2 + up[:, 1] ** 2)
            mu = u_tet[al, 0] + xi_full @ g_vec
            w_list.append(Da * w_full)
            mu_list.append(mu)
            sp_list.append(np.full(len(w_full), s_par))
            mp_list.append(mp)
    if not w_list:
        z = np.empty(0, dtype=np.float64)
        return z, z, z, z
    return np.concatenate(w_list), np.concatenate(mu_list), np.concatenate(sp_list), np.concatenate(mp_list)


def solve_face_beta_F(
    D_a, u_a_tet, Sig_a_tet,
    D_b, u_b_tet, Sig_b_tet,
    basis_kind: int = BASIS_TOPHAT,
    n_perp: int = 3,
):
    """Bracketed Brent root-find for the normal-observer dimensionless face speed beta_F
    in (-1, 1) enforcing sum_alpha F^{(m)}_{a->b}(beta_F) + sum_beta F^{(m)}_{b->a}(beta_F) = 0.

    Note: b->a uses reversed normal (-e_1), so u_b_par -> -u_b_par and beta_F -> -beta_F,
    and contributes negatively to the net flux from a's perspective.
    """
    tot_a = float(np.sum(D_a))
    tot_b = float(np.sum(D_b))
    if tot_a <= 0.0 and tot_b <= 0.0:
        return 0.0

    # Sign flips under reversing e_1 -> -e_1 (keep e_2, e_3 unchanged)
    flip = np.diag([-1.0, 1.0, 1.0])
    u_b_rev = np.array([-u_b_tet[:, 0], u_b_tet[:, 1], u_b_tet[:, 2]]).T
    Sig_b_rev = np.einsum("ij,bjk,kl->bil", flip, Sig_b_tet, flip)

    if basis_kind != BASIS_TOPHAT:
        def net_flux(bF: float) -> float:
            fa = 0.0
            for al in range(len(D_a)):
                if D_a[al] > 0.0:
                    fa += onesided_flux_tetrad(
                        D_a[al], u_a_tet[al], Sig_a_tet[al], bF, basis_kind=basis_kind, n_perp=n_perp
                    )[0]
            fb = 0.0
            for be in range(len(D_b)):
                if D_b[be] > 0.0:
                    fb += onesided_flux_tetrad(
                        D_b[be], u_b_rev[be], Sig_b_rev[be], -bF, basis_kind=basis_kind, n_perp=n_perp
                    )[0]
            return fa - fb
    else:
        wa, mua, spa, mpa = _precompute_face_I0_side(D_a, u_a_tet, Sig_a_tet, basis_kind, n_perp)
        wb, mub, spb, mpb = _precompute_face_I0_side(D_b, u_b_rev, Sig_b_rev, basis_kind, n_perp)

        def net_flux(bF: float) -> float:
            return _slice_tophat_I0_arrays(wa, mua, spa, mpa, bF) - _slice_tophat_I0_arrays(wb, mub, spb, mpb, -bF)

    # Try tight warm bracket around mean face velocity before falling back to full (-1, 1)
    scale_flux = max(tot_a, tot_b, 1e-300)
    lo_max, hi_max = -0.999999999, 0.999999999
    if basis_kind == BASIS_TOPHAT and (len(wa) + len(wb)) > 0:
        va = mua / np.sqrt(mpa * mpa + mua * mua) if len(wa) else np.empty(0)
        vb = -mub / np.sqrt(mpb * mpb + mub * mub) if len(wb) else np.empty(0)
        w_tot = float(np.sum(wa)) + float(np.sum(wb))
        b0 = (float(np.dot(wa, va)) + float(np.dot(wb, vb))) / max(w_tot, 1e-300)
        b0 = max(min(b0, 0.99), -0.99)
        if abs(net_flux(b0)) <= 1e-14 * scale_flux:
            return b0
        for dv in (0.04, 0.25):
            lo_t = max(lo_max, b0 - dv)
            hi_t = min(hi_max, b0 + dv)
            ft_lo, ft_hi = net_flux(lo_t), net_flux(hi_t)
            if abs(ft_lo) <= 1e-14 * scale_flux:
                return lo_t
            if abs(ft_hi) <= 1e-14 * scale_flux:
                return hi_t
            if ft_lo > 0.0 and ft_hi < 0.0:
                return float(optimize.brentq(net_flux, lo_t, hi_t, xtol=1e-12, rtol=1e-12, maxiter=120))

    flo, fhi = net_flux(lo_max), net_flux(hi_max)
    if flo <= 0.0:
        return lo_max
    if fhi >= 0.0:
        return hi_max
    return float(optimize.brentq(net_flux, lo_max, hi_max, xtol=1e-12, rtol=1e-12, maxiter=120))


# ----------------------------------------------------------------------------
# Cubature moments, stress-energy, and geodesic kick
# ----------------------------------------------------------------------------
def basis_cubature_points(u_bar: np.ndarray, Sigma: np.ndarray, n_q: int = 3):
    """Return (u_pts[Q, 3], w_q[Q]) with sum w_q = 1, mean u_bar, covariance Sigma."""
    tr = float(np.trace(Sigma))
    if tr <= 1e-26:
        return u_bar[None, :].copy(), np.array([1.0], dtype=np.float64)
    L = chol3_safe(Sigma)
    xi, w = (CUB_3D_27_XI, CUB_3D_27_W) if n_q == 3 else (CUB_3D_8_XI, CUB_3D_8_W)
    pts = u_bar[None, :] + xi @ L.T
    return pts, w


def basis_stress_energy(m_alpha: float, u_bar: np.ndarray, Sigma: np.ndarray, gi: np.ndarray, n_q: int = 3):
    """Return integrated densitized sources (E_int, P_int[3], S_int[3,3]) for one basis."""
    if m_alpha <= 0.0:
        return 0.0, np.zeros(3), np.zeros((3, 3))
    pts, w = basis_cubature_points(u_bar, Sigma, n_q=n_q)
    uup = pts @ gi.T
    W = np.sqrt(1.0 + np.sum(pts * uup, axis=1))
    E_int = m_alpha * float(np.dot(w, W))
    P_int = m_alpha * (w @ pts)
    S_int = m_alpha * np.einsum("q,qi,qj->ij", w / W, pts, pts)
    return E_int, P_int, S_int


def geodesic_kick_point(adm0: AdmState, adm1: AdmState | None, dt: float, u_in: np.ndarray,
                        tol: float = 1e-12, maxit: int = 50):
    """Implicit-midpoint momentum update at fixed spatial coordinate x_a."""
    if adm1 is None:
        alp = adm0.alp
        gi, _ = inv3_sym(adm0.g)
        dalp = adm0.dalp
        dbeta = adm0.dbeta
        dg = adm0.dg
    else:
        alp = 0.5 * (adm0.alp + adm1.alp)
        g_mid = 0.5 * (adm0.g + adm1.g)
        gi, _ = inv3_sym(g_mid)
        dalp = 0.5 * (adm0.dalp + adm1.dalp)
        dbeta = 0.5 * (adm0.dbeta + adm1.dbeta)
        dg = 0.5 * (adm0.dg + adm1.dg)

    u0 = u_in.copy()
    u1 = u_in.copy()
    for _ in range(maxit):
        ub = 0.5 * (u0 + u1)
        uup = gi @ ub
        W = math.sqrt(1.0 + float(np.dot(ub, uup)))
        # du_i/dt = -W d_i alp + u_j d_i beta^j + (alp/2W) u^l u^m d_i gamma_{lm}
        geo = np.einsum("ilm,l,m->i", dg, uup, uup)
        rhs = -W * dalp + dbeta @ ub + (0.5 * alp / W) * geo
        un = u0 + dt * rhs
        err = float(np.max(np.abs(un - u1)))
        u1 = un
        if err < tol:
            break
    return u1


def cubature_geodesic_kick(
    u_bar: np.ndarray,
    Sigma: np.ndarray,
    adm0: AdmState,
    adm1: AdmState | None,
    dt: float,
    n_q: int = 3,
    tol: float = 1e-12,
):
    """Push cubature points through the geodesic momentum equation at fixed x_a
    and reassemble (u_bar_new, Sigma_new)."""
    pts, w = basis_cubature_points(u_bar, Sigma, n_q=n_q)
    pts_new = np.empty_like(pts)
    for q in range(len(w)):
        pts_new[q] = geodesic_kick_point(adm0, adm1, dt, pts[q], tol=tol)
    u_new = w @ pts_new
    du = pts_new - u_new[None, :]
    Sig_new = np.einsum("q,qi,qj->ij", w, du, du)
    Sig_new = 0.5 * (Sig_new + Sig_new.T)
    return u_new, Sig_new


# ----------------------------------------------------------------------------
# Covariant face-rest-frame pairing cost and empty-basis assignment
# ----------------------------------------------------------------------------
def pairing_cost_matrix(
    Da, ua_tet, Siga_tet,
    Db, ub_tet, Sib_tet,
    beta_F: float,
    lam_D: float = 0.25,
    eps_tau: float = 0.04,
    eps_eb: float = 0.01,
):
    """Return cost matrix C_eb[alpha, beta] for pairing outgoing alpha on side a
    with target beta on side b, following Hopkins (2026) Eqs. (26)-(30) in the
    Lorentz-boosted face rest frame (or normal-observer tetrad when |beta_F| >= 1).
    """
    Na = len(Da)
    Nb = len(Db)
    use_boost = abs(beta_F) < 1.0 - 1e-12
    gam_F = 1.0 / math.sqrt(1.0 - beta_F * beta_F) if use_boost else 1.0

    def boost_u(u_tet):
        W = np.sqrt(1.0 + np.sum(u_tet * u_tet, axis=1))
        out = u_tet.copy()
        if use_boost:
            out[:, 0] = gam_F * (u_tet[:, 0] - beta_F * W)
        return out

    ua_b = boost_u(ua_tet)
    ub_b = boost_u(ub_tet)
    tra = np.trace(Siga_tet, axis1=1, axis2=2)
    trb = np.trace(Sib_tet, axis1=1, axis2=2)

    Da_tot = max(float(np.sum(Da)), 1e-300)
    Db_tot = max(float(np.sum(Db)), 1e-300)

    diff2 = np.sum((ua_b[:, None, :] - ub_b[None, :, :]) ** 2, axis=-1)
    ua2 = np.sum(ua_b * ua_b, axis=1)[:, None]
    ub2 = np.sum(ub_b * ub_b, axis=1)[None, :]
    uadub = np.abs(np.einsum("ai,bi->ab", ua_b, ub_b))
    denom_u = ua2 + ub2 + 2.0 * uadub + tra[:, None] + trb[None, :]
    C_u = np.where(denom_u > 0.0, diff2 / np.maximum(denom_u, 1e-300), 0.0)
    C_D = np.abs(Da[:, None] - Db[None, :]) / (Da[:, None] + Db[None, :] + 0.001 * Da_tot)
    C = C_u + lam_D * C_D

    # Empty-basis sigmoid weighting (Hopkins Eq. 29-30)
    eps_vp2 = (0.01 ** 2) * np.maximum(denom_u, 1e-300)
    term1 = diff2 / (diff2 + tra[:, None] + eps_vp2)
    term2 = eps_tau / (1.0 + Db[None, :] / (eps_eb * Db_tot))
    C_fit = np.min(term1 + term2, axis=1)  # (Na,)

    x = (C_fit - 0.5 * eps_tau) / eps_tau
    theta = np.where(x <= 0.0, 0.0, np.where(x >= 1.0, 1.0, x * x * (3.0 - 2.0 * x)))
    C_eb = C * (1.0 - theta[:, None] / (1.0 + Db[None, :] / np.maximum(Da[:, None], 1e-300)))
    return C_eb


# ----------------------------------------------------------------------------
# Intra-cell realizability repair
# ----------------------------------------------------------------------------
def realizability_repair_cell(m: np.ndarray, P: np.ndarray, Pi: np.ndarray,
                              eps_m: float = 1e-12, eps_S: float = 1e-12,
                              S_floor: float = 1e-14):
    """Enforce m_alpha > 0 and SPD Sigma_alpha within cell while conserving total
    (sum m, sum P, sum Pi) to machine precision. Operates in-place and returns drift."""
    N_b = len(m)
    m_tot = float(np.sum(m))
    if m_tot <= 0.0:
        return 0.0
    P_tot = np.sum(P, axis=0)
    u_bulk = P_tot / m_tot
    Pi_target = np.sum(Pi, axis=0)

    floor_m = max(1e-300, eps_m * m_tot / N_b)
    bad = m < floor_m
    if np.any(bad) and not np.all(bad):
        dm = np.zeros(N_b)
        dP = np.zeros((N_b, 3))
        dPi = np.zeros((N_b, 3, 3))
        dm[bad] = m[bad] - floor_m
        dP[bad] = P[bad] - floor_m * u_bulk[None, :]
        Pi_reset = floor_m * (np.outer(u_bulk, u_bulk) + S_floor * np.eye(3))
        dPi[bad] = Pi[bad] - Pi_reset[None, :, :]
        m[bad] = floor_m
        P[bad] = floor_m * u_bulk[None, :]
        Pi[bad] = Pi_reset[None, :, :]

        good = ~bad
        w = m[good] / np.sum(m[good])
        m[good] += w * np.sum(dm)
        P[good] += w[:, None] * np.sum(dP, axis=0)[None, :]
        Pi[good] += w[:, None, None] * np.sum(dPi, axis=0)[None, :, :]

    # SPD repair on Sigma_alpha
    dPi_accum = np.zeros((3, 3))
    good_idx = int(np.argmax(m))
    for al in range(N_b):
        if m[al] <= 0.0:
            continue
        ua = P[al] / m[al]
        Sig = Pi[al] / m[al] - np.outer(ua, ua)
        Sig = 0.5 * (Sig + Sig.T)
        evals, evecs = np.linalg.eigh(Sig)
        tr = float(np.sum(np.maximum(evals, 0.0)))
        lam_min = eps_S * tr / 3.0 if tr > 0.0 else 1e-30 * float(np.dot(ua, ua))
        if np.any(evals < lam_min):
            evals_fix = np.maximum(evals, lam_min)
            Sig_fix = (evecs * evals_fix[None, :]) @ evecs.T
            Sig_fix = 0.5 * (Sig_fix + Sig_fix.T)
            Pi_old = Pi[al].copy()
            Pi[al] = m[al] * (Sig_fix + np.outer(ua, ua))
            dPi_accum += Pi_old - Pi[al]
    # Note: strictly preserve total Pi if positive contribution keeps good basis SPD
    if float(np.linalg.norm(dPi_accum)) > 0.0:
        Pi_cand = Pi[good_idx] + dPi_accum
        ug = P[good_idx] / m[good_idx]
        Sig_cand = 0.5 * ((Pi_cand / m[good_idx] - np.outer(ug, ug))
                          + (Pi_cand / m[good_idx] - np.outer(ug, ug)).T)
        if np.all(np.linalg.eigvalsh(Sig_cand) >= 0.0):
            Pi[good_idx] = Pi_cand
    return float(np.linalg.norm(np.sum(Pi, axis=0) - Pi_target))


# ----------------------------------------------------------------------------
# Relativistic Maxwell-Juttner BGK collision operator & Synge-EOS HLLC
# ----------------------------------------------------------------------------
def safe_mj_theta_from_w(w: float) -> float:
    """Invert w(theta) = K_3(1/theta)/K_2(1/theta) - theta cleanly for all w >= 1."""
    if w <= 1.0 + 1e-15:
        return 0.0
    if w <= 1.0 + 1e-5:
        dw = w - 1.0
        return (-1.5 + math.sqrt(2.25 + 7.5 * dw)) / 3.75
    if w >= 1e5:
        return w / 3.0
    return float(_coll.mj_theta_from_w(w))


_SYNGE_H_ASYMP = (
    1.0, 2.5, 1.875, -1.875, 1.0546875,
    1.40625, -7.2509765625, 21.09375, -58.152008056640625, 177.978515625,
)


def synge_thermo(theta: float):
    """Return (w_mean, h_rel, c_s2, gamma_ad) for Maxwell-Juttner gas at theta = T/m."""
    theta = float(theta)
    if theta <= 0.0:
        return 1.0, 1.0, 0.0, 5.0 / 3.0
    if theta <= 0.01:
        # Horner evaluation of 10-term asymptotic expansion (< 6e-18 rel err in h, < 2.4e-15 in dh)
        h_rel = 0.0
        for c in reversed(_SYNGE_H_ASYMP):
            h_rel = h_rel * theta + c
        dh_dth = 0.0
        for k in range(len(_SYNGE_H_ASYMP) - 1, 0, -1):
            dh_dth = dh_dth * theta + k * _SYNGE_H_ASYMP[k]
        w_mean = h_rel - theta
    else:
        z = 1.0 / theta
        k2 = float(special.kve(2, z))
        k3 = float(special.kve(3, z))
        h_rel = k3 / k2
        w_mean = h_rel - theta
        dh_dth = z * z * (1.0 + 5.0 * theta * h_rel - h_rel * h_rel)
    cv = max(dh_dth - 1.0, 1.5)
    gamma_ad = 1.0 + 1.0 / cv
    cs2 = min(max(gamma_ad * theta / h_rel, 0.0), 1.0 / 3.0)
    return w_mean, h_rel, cs2, gamma_ad


def mj_bgk_relax_cell(
    m_vec: np.ndarray,
    u_bar: np.ndarray,
    Sigma: np.ndarray,
    V_a: float,
    adm: AdmState,
    sigma_over_mu: float,
    dt: float,
    n_q: int = 3,
    E_override: float | None = None,
):
    """Exact intra-cell relativistic Maxwell-Juttner BGK collision operator.

    Conserves total (m_a, P_{a,i}, E_a) to machine precision via Lorentz boost to the
    exact center-of-momentum frame and scalar dispersion-scale Newton rescaling.
    """
    m_tot = float(np.sum(m_vec))
    if m_tot <= 0.0 or sigma_over_mu <= 0.0:
        return u_bar.copy(), Sigma.copy()

    gi, detg = inv3_sym(adm.g)
    sqrt_g = math.sqrt(detg)
    L_g = chol3_safe(adm.g)           # g = L_g @ L_g.T -> coframe e^{(m)}_i = L_g[i, m]
    Li_g = np.linalg.inv(L_g)         # frame e^i_{(m)} = Li_g[m, i]

    # Accumulate cell total (E, P_cov) in coordinate frame
    E_tot = 0.0
    P_cov_tot = np.zeros(3)
    for al in range(len(m_vec)):
        if m_vec[al] > 0.0:
            Ea, Pa, _ = basis_stress_energy(m_vec[al], u_bar[al], Sigma[al], gi, n_q=n_q)
            E_tot += Ea
            P_cov_tot += Pa
    if E_override is not None:
        E_tot = float(E_override)

    P_tet = Li_g @ P_cov_tot
    P2 = float(np.dot(P_tet, P_tet))
    M_inv2 = E_tot * E_tot - P2
    if M_inv2 <= m_tot * m_tot * (1.0 + 1e-14):
        # Strictly cold zero-temperature distribution: collisions do nothing
        return u_bar.copy(), Sigma.copy()
    M_inv = math.sqrt(M_inv2)
    U0 = E_tot / M_inv
    U_cm = P_tet / M_inv

    w_com = M_inv / m_tot
    theta = safe_mj_theta_from_w(w_com)
    if theta <= 0.0:
        return u_bar.copy(), Sigma.copy()
    _, h_rel, _, _ = synge_thermo(theta)
    vmol = math.sqrt(16.0 * theta / math.pi) if theta < 1e-6 else float(_coll.mj_vmol(theta))
    rho_proper = m_tot / (V_a * sqrt_g * U0)
    nu_a = rho_proper * sigma_over_mu * vmol
    dtau_a = adm.alp * dt / U0
    eta = 1.0 - math.exp(-nu_a * dtau_a)
    if eta <= 0.0:
        return u_bar.copy(), Sigma.copy()

    # Boost every basis's cubature points to COM frame and evaluate COM moments
    u_com_mean = np.zeros_like(u_bar)
    Sig_com = np.zeros_like(Sigma)
    for al in range(len(m_vec)):
        if m_vec[al] <= 0.0:
            continue
        pts, w = basis_cubature_points(u_bar[al], Sigma[al], n_q=n_q)
        pts_tet = pts @ Li_g.T
        W = np.sqrt(1.0 + np.sum(pts_tet * pts_tet, axis=1))
        udotU = pts_tet @ U_cm
        fac = udotU / (U0 + 1.0) - W
        pts_com = pts_tet + fac[:, None] * U_cm[None, :]
        um = w @ pts_com
        du = pts_com - um[None, :]
        u_com_mean[al] = um
        Sig_com[al] = np.einsum("q,qi,qj->ij", w, du, du)

    sig_eq2_0 = theta * h_rel
    u_com_new = (1.0 - eta) * u_com_mean

    def eval_com_energy(scale_s: float):
        Et = 0.0
        S_list = np.empty_like(Sig_com)
        for al in range(len(m_vec)):
            if m_vec[al] <= 0.0:
                S_list[al] = 0.0
                continue
            S_al = (
                (1.0 - eta) * Sig_com[al]
                + eta * (scale_s * sig_eq2_0) * np.eye(3)
                + eta * (1.0 - eta) * np.outer(u_com_mean[al], u_com_mean[al])
            )
            S_list[al] = 0.5 * (S_al + S_al.T)
            pts_c, w = basis_cubature_points(u_com_new[al], S_list[al], n_q=n_q)
            W_c = np.sqrt(1.0 + np.sum(pts_c * pts_c, axis=1))
            Et += m_vec[al] * float(np.dot(w, W_c))
        return Et, S_list

    # Solve E_com(scale_s) == M_inv cleanly without failing when E_min_com > M_inv
    E_min_com, S_list_zero = eval_com_energy(0.0)
    if M_inv <= E_min_com:
        def eval_scaled(c: float):
            Et_c = 0.0
            S_sc = np.zeros_like(Sig_com)
            u_sc = c * u_com_new
            c2 = c * c
            for al in range(len(m_vec)):
                if m_vec[al] <= 0.0:
                    continue
                S_sc[al] = c2 * S_list_zero[al]
                pts_c, w = basis_cubature_points(u_sc[al], S_sc[al], n_q=n_q)
                W_c = np.sqrt(1.0 + np.sum(pts_c * pts_c, axis=1))
                Et_c += m_vec[al] * float(np.dot(w, W_c))
            return Et_c, u_sc, S_sc

        if E_min_com > m_tot * (1.0 + 1e-14):
            c_opt = float(optimize.brentq(lambda c: eval_scaled(c)[0] - M_inv,
                                          0.0, 1.0, xtol=1e-14, rtol=1e-14, maxiter=50))
            _, u_com_new, Sig_com_new = eval_scaled(c_opt)
        else:
            u_com_new = np.zeros_like(u_com_new)
            Sig_com_new = np.zeros_like(Sig_com)
    else:
        Et1, _ = eval_com_energy(1.0)
        if abs(Et1 - M_inv) > 1e-14 * M_inv:
            lo_s, hi_s = 0.0, 2.5
            while eval_com_energy(hi_s)[0] < M_inv and hi_s < 1e6:
                hi_s *= 4.0
            if eval_com_energy(hi_s)[0] >= M_inv:
                scale_opt = float(optimize.brentq(lambda s: eval_com_energy(s)[0] - M_inv,
                                                  lo_s, hi_s, xtol=1e-14, rtol=1e-14, maxiter=50))
                _, Sig_com_new = eval_com_energy(scale_opt)
            else:
                _, Sig_com_new = eval_com_energy(hi_s)
        else:
            _, Sig_com_new = eval_com_energy(1.0)

    # Boost back to coordinate basis via inverse Lorentz boost (-U_cm -> +U_cm)
    u_out = np.zeros_like(u_bar)
    Sig_out = np.zeros_like(Sigma)
    for al in range(len(m_vec)):
        if m_vec[al] <= 0.0:
            continue
        pts_c, w = basis_cubature_points(u_com_new[al], Sig_com_new[al], n_q=n_q)
        Wc = np.sqrt(1.0 + np.sum(pts_c * pts_c, axis=1))
        udotU = pts_c @ U_cm
        fac = udotU / (U0 + 1.0) + Wc
        pts_tet = pts_c + fac[:, None] * U_cm[None, :]
        pts_cov = pts_tet @ L_g
        u_out[al] = w @ pts_cov
        du = pts_cov - u_out[al][None, :]
        cov = np.einsum("q,qi,qj->ij", w, du, du)
        Sig_out[al] = 0.5 * (cov + cov.T)

    # Lock exact lab-frame total momentum P_cov_tot and total lab-frame energy E_tot
    # under finite-cubature re-sampling via mean shift + SPD dispersion scaling
    P_cur = np.sum(m_vec[:, None] * u_out, axis=0)
    u_out = u_out - ((P_cur - P_cov_tot) / m_tot)[None, :]

    def lab_energy(scale_lab: float) -> float:
        return sum(
            basis_stress_energy(m_vec[al], u_out[al], scale_lab * Sig_out[al], gi, n_q=n_q)[0]
            for al in range(len(m_vec)) if m_vec[al] > 0.0
        )

    E_min_lab = lab_energy(0.0)
    E_target = max(float(E_tot), E_min_lab)
    E_cur = lab_energy(1.0)
    if abs(E_cur - E_target) > 1e-14 * E_target:
        lo_l, hi_l = 0.25, 2.0
        while lab_energy(lo_l) > E_target and lo_l > 1e-12:
            lo_l *= 0.25
        while lab_energy(hi_l) < E_target and hi_l < 1e6:
            hi_l *= 4.0
        if lab_energy(lo_l) <= E_target <= lab_energy(hi_l):
            s_lab = float(optimize.brentq(lambda s: lab_energy(s) - E_target,
                                          lo_l, hi_l, xtol=1e-14, rtol=1e-14, maxiter=50))
            Sig_out = s_lab * Sig_out
    return u_out, Sig_out


def rel_hllc_flux_tetrad(
    D_L, u_L_tet, Sig_L_tet, m_L_vec,
    D_R, u_R_tet, Sig_R_tet, m_R_vec,
    beta_F: float,
    use_contact_beta_F: bool = False,
):
    """Single-fluid relativistic HLLC flux in face triad using cell-summed moments
    and Synge EOS (used when Delta x / lambda_MFP is non-negligible).

    Returns (FD_ale, FP_ale[3], FPi_ale[3,3], FE_ale) where FPi_ale uses the exact
    covariant third-moment Maxwell-Juttner tensor M^1_{ij} - beta_F M^0_{ij} in the
    HLLC star state.
    """
    def cell_fluid(D_vec, u_tet, Sig_tet):
        D_tot = float(np.sum(D_vec))
        if D_tot <= 0.0:
            return None
        E = 0.0
        P = np.zeros(3)
        for al in range(len(D_vec)):
            if D_vec[al] > 0.0:
                ea, pa, _ = basis_stress_energy(D_vec[al], u_tet[al], Sig_tet[al], np.eye(3))
                E += ea
                P += pa
        P2 = float(np.dot(P, P))
        Minv = math.sqrt(max(E * E - P2, D_tot * D_tot))
        U0 = E / Minv
        v = P / E
        w_com = Minv / D_tot
        if w_com <= 1.0 + 1e-12:
            theta, h_rel, cs2 = 0.0, 1.0, 0.0
        else:
            theta = safe_mj_theta_from_w(w_com)
            _, h_rel, cs2, _ = synge_thermo(theta)
        rho0 = D_tot / U0
        p_fl = rho0 * theta
        return dict(D=D_tot, E=E, P=P, v=v, U0=U0, h=h_rel, cs2=cs2, p=p_fl, rho0=rho0, theta=theta)

    L = cell_fluid(D_L, u_L_tet, Sig_L_tet)
    R = cell_fluid(D_R, u_R_tet, Sig_R_tet)
    if L is None or R is None:
        return 0.0, np.zeros(3), np.zeros((3, 3)), 0.0

    def char_speeds(st):
        vx = float(st["v"][0])
        v2 = float(np.dot(st["v"], st["v"]))
        cs2 = st["cs2"]
        s2 = max(1.0 - v2 * cs2, 1e-12)
        disc = math.sqrt(max(cs2 * (1.0 - v2) * (1.0 - v2 * cs2 - vx * vx * (1.0 - cs2)), 0.0))
        num1 = vx * (1.0 - cs2)
        lam_m = (num1 - disc) / s2
        lam_p = (num1 + disc) / s2
        return lam_m, lam_p

    lm_L, lp_L = char_speeds(L)
    lm_R, lp_R = char_speeds(R)
    S_L = min(lm_L, lm_R)
    S_R = max(lp_L, lp_R)

    def raw_flux(st):
        vx = st["v"][0]
        FD = st["D"] * vx
        FP = st["P"] * vx
        FP[0] += st["p"]
        FE = st["P"][0]
        return FD, FP, FE

    FD_L, FP_L, FE_L = raw_flux(L)
    FD_R, FP_R, FE_R = raw_flux(R)

    dS = S_R - S_L
    beta_use = beta_F
    if use_contact_beta_F:
        if dS <= 1e-12 * (1.0 + abs(S_L) + abs(S_R)):
            beta_use = 0.5 * (S_L + S_R)
        else:
            F_hll_E0 = (S_R * FE_L - S_L * FE_R + S_L * S_R * (R["E"] - L["E"])) / dS
            F_hll_Px0 = (S_R * FP_L[0] - S_L * FP_R[0] + S_L * S_R * (R["P"][0] - L["P"][0])) / dS
            U_hll_E0 = (S_R * R["E"] - S_L * L["E"] + FE_L - FE_R) / dS
            U_hll_Px0 = (S_R * R["P"][0] - S_L * L["P"][0] + FP_L[0] - FP_R[0]) / dS
            aq0 = F_hll_E0
            bq0 = -(U_hll_E0 + F_hll_Px0)
            cq0 = U_hll_Px0
            if abs(aq0) < 1e-14 * (abs(bq0) + abs(cq0) + 1e-30):
                s_st = -cq0 / bq0 if abs(bq0) > 1e-14 else 0.0
            else:
                disc0 = max(bq0 * bq0 - 4.0 * aq0 * cq0, 0.0)
                s_st = (-bq0 - math.sqrt(disc0)) / (2.0 * aq0)
            beta_use = max(S_L, min(S_R, s_st))

    if dS <= 1e-12 * (1.0 + abs(S_L) + abs(S_R)):
        S_mid = 0.5 * (S_L + S_R)
        st_pick = L if beta_use <= S_mid else R
        D_s, P_s, E_s = st_pick["D"], st_pick["P"], st_pick["E"]
        FD_s, FP_s, FE_s = (FD_L, FP_L, FE_L) if beta_use <= S_mid else (FD_R, FP_R, FE_R)
    elif beta_use <= S_L:
        D_s, P_s, E_s = L["D"], L["P"], L["E"]
        FD_s, FP_s, FE_s = FD_L, FP_L, FE_L
    elif beta_use >= S_R:
        D_s, P_s, E_s = R["D"], R["P"], R["E"]
        FD_s, FP_s, FE_s = FD_R, FP_R, FE_R
    else:
        F_hll_E = (S_R * FE_L - S_L * FE_R + S_L * S_R * (R["E"] - L["E"])) / dS
        F_hll_Px = (S_R * FP_L[0] - S_L * FP_R[0] + S_L * S_R * (R["P"][0] - L["P"][0])) / dS
        U_hll_E = (S_R * R["E"] - S_L * L["E"] + FE_L - FE_R) / dS
        U_hll_Px = (S_R * R["P"][0] - S_L * L["P"][0] + FP_L[0] - FP_R[0]) / dS

        a_q = F_hll_E
        b_q = -(U_hll_E + F_hll_Px)
        c_q = U_hll_Px
        if abs(a_q) < 1e-14 * (abs(b_q) + abs(c_q) + 1e-30):
            S_star = -c_q / b_q if abs(b_q) > 1e-14 else 0.0
        else:
            disc = max(b_q * b_q - 4.0 * a_q * c_q, 0.0)
            S_star = (-b_q - math.sqrt(disc)) / (2.0 * a_q)
        S_star = max(S_L, min(S_R, S_star))

        st = L if beta_use <= S_star else R
        S_K = S_L if beta_use <= S_star else S_R
        vxK = float(st["v"][0])
        p_s = max(F_hll_Px - S_star * F_hll_E, 0.0)
        denom = S_K - S_star
        if abs(denom) <= 1e-12 * max(dS, 1.0):
            D_s = (S_R * R["D"] - S_L * L["D"] + FD_L - FD_R) / dS
            E_s = U_hll_E
            P_s = (S_R * R["P"] - S_L * L["P"] + FP_L - FP_R) / dS
            FD_s = (S_R * FD_L - S_L * FD_R + S_L * S_R * (R["D"] - L["D"])) / dS
            FP_s = (S_R * FP_L - S_L * FP_R + S_L * S_R * (R["P"] - L["P"])) / dS
            FE_s = F_hll_E
        else:
            D_s = st["D"] * (S_K - vxK) / denom
            E_s = (st["E"] * (S_K - vxK) - st["p"] * vxK + p_s * S_star) / denom
            Px_s = (st["P"][0] * (S_K - vxK) - st["p"] + p_s) / denom
            Py_s = st["P"][1] * (S_K - vxK) / denom
            Pz_s = st["P"][2] * (S_K - vxK) / denom
            P_s = np.array([Px_s, Py_s, Pz_s])
            FD_s = D_s * S_star
            FP_s = P_s * S_star
            FP_s[0] += p_s
            FE_s = (E_s + p_s) * S_star

    if D_s <= 1e-300 or E_s <= 1e-300:
        return FD_s - beta_use * D_s, FP_s - beta_use * P_s, np.zeros((3, 3)), FE_s - beta_use * E_s

    # Covariant Maxwell-Juttner third moment M^0_{ij} and M^1_{ij} in the star state
    v_s = P_s / E_s
    v_s2 = float(np.dot(v_s, v_s))
    if v_s2 >= 1.0 - 1e-12:
        v_s = v_s * math.sqrt((1.0 - 1e-12) / v_s2)
        v_s2 = 1.0 - 1e-12
    U0_s = 1.0 / math.sqrt(1.0 - v_s2)
    U_s = U0_s * v_s
    M_inv_s = E_s / U0_s
    n_s = D_s / U0_s
    w_s = M_inv_s / D_s
    if w_s <= 1.0 + 1e-12:
        th_s, h_s = 0.0, 1.0
    else:
        th_s = safe_mj_theta_from_w(w_s)
        _, h_s, _, _ = synge_thermo(th_s)
    b3 = n_s * th_s * h_s
    a3 = n_s * (1.0 + 6.0 * th_s * h_s)
    M0_ij = (a3 * U0_s) * np.outer(U_s, U_s) + (b3 * U0_s) * np.eye(3)
    e1 = np.array([1.0, 0.0, 0.0])
    M1_ij = (
        (a3 * U_s[0]) * np.outer(U_s, U_s)
        + b3 * (U_s[0] * np.eye(3) + np.outer(U_s, e1) + np.outer(e1, U_s))
    )
    FPi_ale = M1_ij - beta_use * M0_ij
    return FD_s - beta_use * D_s, FP_s - beta_use * P_s, FPi_ale, FE_s - beta_use * E_s


# ----------------------------------------------------------------------------
# Exact Special-Relativistic Colliding-Stream / Taub Double-Shock Reference
# ----------------------------------------------------------------------------
def exact_taub_double_shock(u0: float = 1.0, rho0: float = 1.0):
    """Exact Riemann solution for two symmetric cold relativistic streams at u = +/- u0
    and coordinate rest-mass density rho0/2 (or lab rest density D_0 = 1) colliding
    head-on into a stationary shocked central slab with Maxwell-Juttner (Synge) EOS.

    Wait: in the problem where left half has D=1, u_x=+u0 and right half has D=1, u_x=-u0,
    incoming pre-shock state has proper rest density rho_1 = D_0 / W_0, specific enthalpy h_1 = 1,
    pressure p_1 = 0, Lorentz factor W_0 = sqrt(1 + u0^2), incoming speed v_0 = u0 / W_0.
    Post-shock slab is at rest (v_2 = 0) with conserved mass, momentum, energy flux across
    shock speed V_s > 0 (moving rightward into the right stream):
      [D (v - V_s)] = 0 => rho_2 V_s = D_0 (v_0 + V_s)
      [T^{xx} - T^{0x} V_s] = 0 => p_2 = D_0 W_0 v_0 (v_0 + V_s) = rho_1 u_0 (u_0 + W_0 V_s)
      [T^{0x} - T^{00} V_s] = 0 => e_2 V_s = D_0 W_0 (v_0 + V_s)
    Notice the energy and mass jump immediately give:
      e_2 / rho_2 = W_0   (specific internal energy per rest mass in the shocked slab = W_0!)
    Then theta_2 follows directly from mj_theta_from_w(W_0), pressure p_2 = rho_2 theta_2,
    and V_s satisfies: rho_2 theta_2 = rho_2 V_s v_0 => V_s = theta_2 / v_0!!
    WAIT A SECOND: check that!
      From (1): rho_2 = D_0 (v_0 + V_s) / V_s.
      From (2): p_2 = D_0 W_0 v_0 (v_0 + V_s) = rho_2 V_s W_0 v_0 = rho_2 u_0 V_s!
      Wait: p_2 = rho_2 theta_2, so theta_2 = u_0 V_s => V_s = theta_2 / u_0!
      Let's double check: T^{00}_1 = D_0 W_0, T^{0x}_1 = D_0 u_0, T^{xx}_1 = D_0 u_0 v_0,
      and T^{00}_2 = e_2 = rho_2 W_0, T^{0x}_2 = 0, T^{xx}_2 = p_2 = rho_2 theta_2.
      Flux balance across right-moving shock at speed V_s into right stream (v = -v_0):
        Mass: D_0(-v_0 - V_s) = rho_2(0 - V_s) => rho_2 = D_0 (1 + v_0/V_s)
        Momentum: T^{xx}_1 - T^{0x}_1 V_s = T^{xx}_2 - T^{0x}_2 V_s:
          Here right stream has T^{0x}_1 = -D_0 u_0, T^{xx}_1 = +D_0 u_0 v_0.
          So D_0 u_0 v_0 - (-D_0 u_0) V_s = p_2 - 0 => D_0 u_0 (v_0 + V_s) = p_2.
          Substitute D_0(v_0 + V_s) = rho_2 V_s: p_2 = rho_2 u_0 V_s => V_s = theta_2 / u_0!
        Energy: T^{0x}_1 - T^{00}_1 V_s = T^{0x}_2 - T^{00}_2 V_s:
          -D_0 u_0 - D_0 W_0 V_s = 0 - e_2 V_s => e_2 V_s = D_0 W_0 (v_0 + V_s) = rho_2 W_0 V_s
          => e_2 / rho_2 = W_0!
    """
    W0 = math.sqrt(1.0 + u0 * u0)
    v0 = u0 / W0
    theta2 = _coll.mj_theta_from_w(W0)
    V_s = theta2 / u0
    D2 = rho0 * (v0 + V_s) / V_s
    p2 = D2 * theta2
    e2 = D2 * W0
    return dict(W0=W0, v0=v0, theta2=theta2, shock_speed=V_s, D2=D2, p2=p2, e2=e2)


# ----------------------------------------------------------------------------
# 1D MFM GR-LBV Solver (exact twin of the 3D algorithm restricted to 1D)
# ----------------------------------------------------------------------------
def _cubic_spline_1d(r: float, h: float) -> float:
    q = abs(r) / h
    if q >= 2.0:
        return 0.0
    # Normalize so integral = 1 in 1D (sigma_1 = 2/(3 h))
    norm = 2.0 / (3.0 * h)
    if q < 1.0:
        return norm * (1.0 - 1.5 * q * q + 0.75 * q * q * q)
    t = 2.0 - q
    return norm * 0.25 * t * t * t


def _periodic_dx(dx: float, L: float) -> float:
    return dx - L * round(dx / L)


@dataclass
class MFM1DState:
    x: np.ndarray           # (N,) cell centers in [0, L)
    m: np.ndarray           # (N, Nb) rest mass per basis
    P: np.ndarray           # (N, Nb, 3) covariant momentum
    Pi: np.ndarray          # (N, Nb, 3, 3) second moment
    L: float
    h: np.ndarray           # (N,) smoothing length
    V: np.ndarray           # (N,) cell volume
    D: np.ndarray           # (N, Nb) coordinate density
    u_bar: np.ndarray       # (N, Nb, 3)
    Sigma: np.ndarray       # (N, Nb, 3, 3)
    grad_D: np.ndarray = None
    grad_u: np.ndarray = None
    grad_Sig: np.ndarray = None
    pairs_r: np.ndarray = None   # (N, Nb) right neighbor basis paired for each alpha
    pairs_l: np.ndarray = None   # (N, Nb) left neighbor basis paired for each alpha


def init_mfm_1d(x: np.ndarray, D_init: np.ndarray, u_init: np.ndarray, Sig_init: np.ndarray,
                L: float) -> MFM1DState:
    """Initialize 1D MFM state from per-cell density, mean u, covariance Sigma."""
    N, Nb = D_init.shape
    order = np.argsort(x % L)
    x = (x % L)[order]
    D = D_init[order].copy()
    u = u_init[order].copy()
    Sig = Sig_init[order].copy()
    # Voronoi / dual-cell volumes in 1D equal MFM V_a on ordered 1D mesh
    dx_r = np.roll(x, -1) - x
    dx_r[-1] += L
    dx_l = x - np.roll(x, 1)
    dx_l[0] += L
    V = 0.5 * (dx_r + dx_l)
    m = D * V[:, None]
    P = m[:, :, None] * u
    Pi = m[:, :, None, None] * (Sig + u[:, :, :, None] * u[:, :, None, :])
    st = MFM1DState(x=x, m=m, P=P, Pi=Pi, L=L, h=V.copy(), V=V, D=D, u_bar=u, Sigma=Sig)
    _update_1d_geometry(st)
    _cons_to_prim_1d(st)
    return st


def _update_1d_geometry(st: MFM1DState):
    """Solve h_a bar{n}_a = 1 iteratively on periodic 1D mesh (exact MFM partition)."""
    N = len(st.x)
    for a in range(N):
        h = float(st.h[a])
        for _ in range(12):
            nbar = 0.0
            for off in range(-4, 5):
                b = (a + off) % N
                dx = _periodic_dx(st.x[b] - st.x[a], st.L)
                nbar += _cubic_spline_1d(dx, h)
            h_new = 1.0 / max(nbar, 1e-300)
            if abs(h_new - h) < 1e-13 * h:
                h = h_new
                break
            h = 0.5 * (h + h_new)
        st.h[a] = h
        st.V[a] = 1.0 / nbar


def _cons_to_prim_1d(st: MFM1DState):
    N, Nb = st.m.shape
    for a in range(N):
        realizability_repair_cell(st.m[a], st.P[a], st.Pi[a])
    st.D = st.m / st.V[:, None]
    st.u_bar = st.P / st.m[:, :, None]
    st.Sigma = st.Pi / st.m[:, :, None, None] - st.u_bar[:, :, :, None] * st.u_bar[:, :, None, :]
    st.Sigma = 0.5 * (st.Sigma + np.swapaxes(st.Sigma, -1, -2))


def _compute_1d_gradients(st: MFM1DState):
    """Exact 1D MFM MLS gradients with matching + BJ + velocity-crossing + SPD limiters."""
    N, Nb = st.m.shape
    gD = np.zeros((N, Nb))
    gu = np.zeros((N, Nb, 3))
    gS = np.zeros((N, Nb, 3, 3))
    if st.pairs_r is None:
        st.pairs_r = np.broadcast_to(np.arange(Nb), (N, Nb)).copy()
        st.pairs_l = np.broadcast_to(np.arange(Nb), (N, Nb)).copy()

    for a in range(N):
        al_p = (a + 1) % N
        al_m = (a - 1) % N
        dx_p = _periodic_dx(st.x[al_p] - st.x[a], st.L)
        dx_m = _periodic_dx(st.x[al_m] - st.x[a], st.L)
        wp = _cubic_spline_1d(dx_p, st.h[a])
        wm = _cubic_spline_1d(dx_m, st.h[a])
        E = dx_p * dx_p * wp + dx_m * dx_m * wm
        invE = 1.0 / max(E, 1e-300)

        ua_bulk = np.sum(st.P[a], axis=0) / np.sum(st.m[a])
        up_bulk = np.sum(st.P[al_p], axis=0) / np.sum(st.m[al_p])
        um_bulk = np.sum(st.P[al_m], axis=0) / np.sum(st.m[al_m])

        psi_p = st.h[al_p] / (st.h[a] + st.h[al_p])
        psi_m = st.h[al_m] / (st.h[a] + st.h[al_m])
        xf_p = psi_p * dx_p
        xf_m = psi_m * dx_m

        for al in range(Nb):
            bp = int(st.pairs_r[a, al])
            bm = int(st.pairs_l[a, al])

            # Density gradient + BJ limiter
            dD_raw = invE * ((st.D[al_p, bp] - st.D[a, al]) * dx_p * wp
                             + (st.D[al_m, bm] - st.D[a, al]) * dx_m * wm)
            phi_D = 1.0
            for dx_f, val_n in ((xf_p, st.D[al_p, bp]), (xf_m, st.D[al_m, bm])):
                dval = dD_raw * dx_f
                if dval > 0.0:
                    dmax = max(st.D[a, al], val_n) - st.D[a, al]
                    phi_D = min(phi_D, dmax / dval if dval > 1e-300 else 1.0)
                elif dval < 0.0:
                    dmin = min(st.D[a, al], val_n) - st.D[a, al]
                    phi_D = min(phi_D, dmin / dval if dval < -1e-300 else 1.0)
            gD[a, al] = max(0.0, min(1.0, phi_D)) * dD_raw

            # Velocity gradient + Hopkins velocity-crossing limiter (eps_v = 0.1)
            for k in range(3):
                du_raw = invE * ((st.u_bar[al_p, bp, k] - st.u_bar[a, al, k]) * dx_p * wp
                                 + (st.u_bar[al_m, bm, k] - st.u_bar[a, al, k]) * dx_m * wm)
                phi_v = 1.0
                for dx_b, dx_f, val_n, ub_n, sig_n in (
                    (dx_p, xf_p, st.u_bar[al_p, bp, k], up_bulk[k], math.sqrt(max(st.Sigma[al_p, bp, k, k], 0.0))),
                    (dx_m, xf_m, st.u_bar[al_m, bm, k], um_bulk[k], math.sqrt(max(st.Sigma[al_m, bm, k, k], 0.0))),
                ):
                    sig_a = math.sqrt(max(st.Sigma[a, al, k, k], 0.0))
                    scale = max(abs(st.u_bar[a, al, k] - ua_bulk[k]), sig_a,
                                abs(val_n - ub_n), sig_n, 1e-12)
                    if abs(du_raw * dx_b) >= 0.1 * scale:
                        dval = du_raw * dx_f
                        if dval > 0.0:
                            dmax = max(st.u_bar[a, al, k], val_n) - st.u_bar[a, al, k]
                            phi_v = min(phi_v, dmax / dval)
                        elif dval < 0.0:
                            dmin = min(st.u_bar[a, al, k], val_n) - st.u_bar[a, al, k]
                            phi_v = min(phi_v, dmin / dval)
                gu[a, al, k] = max(0.0, min(1.0, phi_v)) * du_raw

            # Covariance gradient + shared BJ + SPD bisection limiter
            dS_raw = invE * ((st.Sigma[al_p, bp] - st.Sigma[a, al]) * dx_p * wp
                             + (st.Sigma[al_m, bm] - st.Sigma[a, al]) * dx_m * wm)
            phi_S = 1.0
            for dx_f, Sig_n in ((xf_p, st.Sigma[al_p, bp]), (xf_m, st.Sigma[al_m, bm])):
                phi_pair = 1.0
                for i in range(3):
                    for j in range(i, 3):
                        dval = dS_raw[i, j] * dx_f
                        if dval > 0.0:
                            phi_pair = min(phi_pair, (max(st.Sigma[a, al, i, j], Sig_n[i, j]) - st.Sigma[a, al, i, j]) / dval)
                        elif dval < 0.0:
                            phi_pair = min(phi_pair, (min(st.Sigma[a, al, i, j], Sig_n[i, j]) - st.Sigma[a, al, i, j]) / dval)
                phi_pair = max(0.0, min(1.0, phi_pair))
                # Bisect if reconstructed Sigma* is not SPD
                cand = st.Sigma[a, al] + phi_pair * dx_f * dS_raw
                if np.min(np.linalg.eigvalsh(0.5 * (cand + cand.T))) < 0.0:
                    lo, hi = 0.0, phi_pair
                    for _ in range(16):
                        mid = 0.5 * (lo + hi)
                        c_m = st.Sigma[a, al] + mid * dx_f * dS_raw
                        if np.min(np.linalg.eigvalsh(0.5 * (c_m + c_m.T))) >= 0.0:
                            lo = mid
                        else:
                            hi = mid
                    phi_pair = lo
                phi_S = min(phi_S, phi_pair)
            gS[a, al] = phi_S * dS_raw

    st.grad_D, st.grad_u, st.grad_Sig = gD, gu, gS


def _compute_1d_rhs(st: MFM1DState, basis_kind: int = BASIS_TOPHAT,
                    use_analytic_vF: bool = False, sigma_over_mu: float = 0.0,
                    pairing_mode: str = "eb", n_perp: int = 3):
    """Compute pairwise 1D MFM fluxes (and face velocity + pairing updates)."""
    N, Nb = st.m.shape
    _compute_1d_gradients(st)

    dm = np.zeros_like(st.m)
    dP = np.zeros_like(st.P)
    dPi = np.zeros_like(st.Pi)
    dE = np.zeros(N, dtype=np.float64)
    v_cell = np.zeros(N)
    for a in range(N):
        tot_m = float(np.sum(st.m[a]))
        vx_num = 0.0
        for al in range(Nb):
            pts, w = basis_cubature_points(st.u_bar[a, al], st.Sigma[a, al], n_q=3)
            W = np.sqrt(1.0 + np.sum(pts * pts, axis=1))
            vx_num += st.m[a, al] * float(np.dot(w, pts[:, 0] / W))
        v_cell[a] = vx_num / max(tot_m, 1e-300)

    pairs_r = np.zeros((N, Nb), dtype=np.int64)
    pairs_l = np.zeros((N, Nb), dtype=np.int64)
    max_sig = 0.0
    max_f_res = 0.0

    for a in range(N):
        b = (a + 1) % N
        dx_ab = _periodic_dx(st.x[b] - st.x[a], st.L)
        psi = st.h[b] / (st.h[a] + st.h[b])
        xf_a = psi * dx_ab
        xf_b = (psi - 1.0) * dx_ab

        Da = np.maximum(st.D[a] + xf_a * st.grad_D[a], 0.0)
        ua = st.u_bar[a] + xf_a * st.grad_u[a]
        Sa = st.Sigma[a] + xf_a * st.grad_Sig[a]

        Db = np.maximum(st.D[b] + xf_b * st.grad_D[b], 0.0)
        ub = st.u_bar[b] + xf_b * st.grad_u[b]
        Sb = st.Sigma[b] + xf_b * st.grad_Sig[b]

        # Collisionality blend weight w_c = exp(-dx / lambda_MFP)
        wc = 1.0
        if sigma_over_mu > 0.0:
            D_mean = 0.5 * (float(np.sum(Da)) + float(np.sum(Db)))
            wc = math.exp(-abs(dx_ab) * D_mean * sigma_over_mu)

        if use_analytic_vF:
            Ea, Pa = 0.0, 0.0
            for al in range(Nb):
                ea, pa, _ = basis_stress_energy(Da[al], ua[al], Sa[al], np.eye(3))
                Ea += ea; Pa += pa[0]
            for be in range(Nb):
                eb, pb, _ = basis_stress_energy(Db[be], ub[be], Sb[be], np.eye(3))
                Ea += eb; Pa += pb[0]
            beta_F = Pa / max(Ea, 1e-300)
        elif wc > 1e-6:
            beta_F = solve_face_beta_F(Da, ua, Sa, Db, ub, Sb, basis_kind=basis_kind, n_perp=n_perp)
        else:
            beta_F = 0.0

        flip = np.diag([-1.0, 1.0, 1.0])

        # Signal speed for CFL
        for al in range(Nb):
            W_a = math.sqrt(1.0 + float(np.dot(ua[al], ua[al])))
            vx_a = ua[al, 0] / W_a
            cs_eff = math.sqrt(min(3.0 * max(Sa[al, 0, 0], 0.0) / (W_a * W_a), 1.0))
            max_sig = max(max_sig, min(abs(vx_a - beta_F) + cs_eff, 2.0))

        # Basis pairing a -> b and b -> a
        if wc > 1e-6:
            if pairing_mode == "eb":
                C_ab = pairing_cost_matrix(Da, ua, Sa, Db, ub, Sb, beta_F)
                C_ba = pairing_cost_matrix(Db, ub, Sb, Da, ua, Sa, beta_F)
            elif pairing_mode == "v_only":
                diff2 = np.sum((ua[:, None, :] - ub[None, :, :]) ** 2, axis=-1)
                C_ab = diff2
                C_ba = diff2.T
            elif pairing_mode == "w2":
                tra = np.sqrt(np.maximum(np.trace(Sa, axis1=1, axis2=2), 0.0))
                trb = np.sqrt(np.maximum(np.trace(Sb, axis1=1, axis2=2), 0.0))
                C_ab = np.sum((ua[:, None, :] - ub[None, :, :]) ** 2, axis=-1) + (tra[:, None] - trb[None, :]) ** 2
                C_ba = C_ab.T
            elif pairing_mode == "always_empty":
                C_ab = pairing_cost_matrix(Da, ua, Sa, Db, ub, Sb, beta_F) * (Db[None, :] / np.maximum(Da[:, None] + Db[None, :], 1e-300))
                C_ba = pairing_cost_matrix(Db, ub, Sb, Da, ua, Sa, beta_F) * (Da[None, :] / np.maximum(Db[:, None] + Da[None, :], 1e-300))
            else:
                C_ab = pairing_cost_matrix(Da, ua, Sa, Db, ub, Sb, beta_F)
                C_ba = pairing_cost_matrix(Db, ub, Sb, Da, ua, Sa, beta_F)

            p_ab = np.argmin(C_ab, axis=1)
            p_ba = np.argmin(C_ba, axis=1)
        else:
            p_ab = np.arange(Nb, dtype=np.int64)
            p_ba = np.arange(Nb, dtype=np.int64)
        pairs_r[a] = p_ab
        pairs_l[b] = p_ba

        if wc < 1.0 - 1e-14:
            FD_c, FP_c, FPi_c, FE_c = rel_hllc_flux_tetrad(
                Da, ua, Sa, st.m[a], Db, ub, Sb, st.m[b], beta_F,
                use_contact_beta_F=(wc < 0.5),
            )
            ma_tot = max(float(np.sum(st.m[a])), 1e-300)
            mb_tot = max(float(np.sum(st.m[b])), 1e-300)
            omw = 1.0 - wc
            dE[a] -= omw * FE_c
            dE[b] += omw * FE_c
            for al in range(Nb):
                fa = st.m[a, al] / ma_tot
                dm[a, al] -= omw * fa * FD_c
                dP[a, al] -= omw * fa * FP_c
                dPi[a, al] -= omw * fa * FPi_c
            for be in range(Nb):
                fb = st.m[b, be] / mb_tot
                dm[b, be] += omw * fb * FD_c
                dP[b, be] += omw * fb * FP_c
                dPi[b, be] += omw * fb * FPi_c

        # Collisionless fluxes a -> b scaled by wc (positive leaves a, enters b)
        f_net = 0.0
        if wc > 1e-6:
            for al in range(Nb):
                be = int(p_ab[al])
                fm, fp, fpi, fe = onesided_flux_tetrad(Da[al], ua[al], Sa[al], beta_F,
                                                       basis_kind=basis_kind, n_perp=n_perp)
                f_net += fm
                dm[a, al] -= wc * fm;   dP[a, al] -= wc * fp;   dPi[a, al] -= wc * fpi
                dm[b, be] += wc * fm;   dP[b, be] += wc * fp;   dPi[b, be] += wc * fpi
                dE[a] -= wc * fe;       dE[b] += wc * fe

            # Collisionless fluxes b -> a scaled by wc (using reversed x-normal: leaves b, enters a)
            for be in range(Nb):
                al = int(p_ba[be])
                ub_rev = np.array([-ub[be, 0], ub[be, 1], ub[be, 2]])
                Sb_rev = flip @ Sb[be] @ flip
                fm, fp_rev, fpi_rev, fe_rev = onesided_flux_tetrad(
                    Db[be], ub_rev, Sb_rev, -beta_F, basis_kind=basis_kind, n_perp=n_perp
                )
                f_net -= fm
                fp = np.array([-fp_rev[0], fp_rev[1], fp_rev[2]])
                fpi = flip @ fpi_rev @ flip
                dm[b, be] -= wc * fm;   dP[b, be] -= wc * fp;   dPi[b, be] -= wc * fpi
                dm[a, al] += wc * fm;   dP[a, al] += wc * fp;   dPi[a, al] += wc * fpi
                dE[b] -= wc * fe_rev;   dE[a] += wc * fe_rev
        max_f_res = max(max_f_res, abs(f_net))

    st.pairs_r = pairs_r
    st.pairs_l = pairs_l
    return v_cell, dm, dP, dPi, dE, max_sig, max_f_res


def step_1d_mfm(
    st: MFM1DState,
    dt: float,
    basis_kind: int = BASIS_TOPHAT,
    use_analytic_vF: bool = False,
    sigma_over_mu: float = 0.0,
    pairing_mode: str = "eb",
    n_perp: int = 3,
):
    """Advance 1D MFM state by dt using SSP-RK2 + operator-split relativistic BGK."""
    x0 = st.x.copy()
    m0, P0, Pi0 = st.m.copy(), st.P.copy(), st.Pi.copy()
    E0 = np.array([
        sum(basis_stress_energy(st.m[a, al], st.u_bar[a, al], st.Sigma[a, al], np.eye(3))[0]
            for al in range(st.m.shape[1]))
        for a in range(len(st.x))
    ])

    # Stage 1
    v0, dm0, dP0, dPi0, dE0, _, max_f_res = _compute_1d_rhs(
        st, basis_kind=basis_kind, use_analytic_vF=use_analytic_vF,
        sigma_over_mu=sigma_over_mu, pairing_mode=pairing_mode, n_perp=n_perp,
    )
    st.x = (x0 + dt * v0) % st.L
    st.m = m0 + dt * dm0
    st.P = P0 + dt * dP0
    st.Pi = Pi0 + dt * dPi0
    _update_1d_geometry(st)
    _cons_to_prim_1d(st)

    # Stage 2 (SSP-RK2)
    v1, dm1, dP1, dPi1, dE1, max_sig, _ = _compute_1d_rhs(
        st, basis_kind=basis_kind, use_analytic_vF=use_analytic_vF,
        sigma_over_mu=sigma_over_mu, pairing_mode=pairing_mode, n_perp=n_perp,
    )
    st.x = (x0 + 0.5 * dt * (v0 + v1)) % st.L
    st.m = m0 + 0.5 * dt * (dm0 + dm1)
    st.P = P0 + 0.5 * dt * (dP0 + dP1)
    st.Pi = Pi0 + 0.5 * dt * (dPi0 + dPi1)
    E_cons = E0 + 0.5 * dt * (dE0 + dE1)
    _update_1d_geometry(st)
    _cons_to_prim_1d(st)

    if sigma_over_mu > 0.0:
        adm = AdmState.minkowski()
        for a in range(len(st.x)):
            u_new, S_new = mj_bgk_relax_cell(
                st.m[a], st.u_bar[a], st.Sigma[a], st.V[a], adm, sigma_over_mu, dt,
                E_override=E_cons[a],
            )
            st.u_bar[a] = u_new
            st.Sigma[a] = S_new
            st.P[a] = st.m[a, :, None] * u_new
            st.Pi[a] = st.m[a, :, None, None] * (S_new + u_new[:, :, None] * u_new[:, None, :])
        _cons_to_prim_1d(st)

    return max_sig, max_f_res


def total_invariants_1d(st: MFM1DState):
    """Return total (M_rest, P_cov[3], E_tot) over all cells and bases."""
    M_tot = float(np.sum(st.m))
    P_tot = np.sum(st.P, axis=(0, 1))
    E_tot = 0.0
    gi = np.eye(3)
    for a in range(len(st.x)):
        for al in range(st.m.shape[1]):
            ea, _, _ = basis_stress_energy(st.m[a, al], st.u_bar[a, al], st.Sigma[a, al], gi)
            E_tot += ea
    return M_tot, P_tot, E_tot


# ----------------------------------------------------------------------------
# Binary IC / Snapshot I/O (GRLBV001 format shared with AthenaK)
# ----------------------------------------------------------------------------
def write_grlbv(path: str, x: np.ndarray, m_basis: np.ndarray,
                u_bar: np.ndarray, Sigma: np.ndarray,
                species: np.ndarray | None = None, time: float = 0.0):
    """Write GRLBV001 initial data / snapshot file.

    Format (little-endian):
      8 bytes   magic b"GRLBV001"
      8 bytes   int64 N (elements)
      8 bytes   int64 N_basis
      8 bytes   float64 time
      24*N      float64 x[N, 3]
      4*N       int32   species[N]
      8*N*Nb    float64 m[N, Nb]
      24*N*Nb   float64 u_bar[N, Nb, 3]  (covariant spatial components)
      48*N*Nb   float64 Sigma_sym[N, Nb, 6]  (xx, xy, xz, yy, yz, zz)
    """
    x = np.asarray(x, dtype="<f8").reshape(-1, 3)
    N = x.shape[0]
    m_basis = np.asarray(m_basis, dtype="<f8")
    Nb = m_basis.shape[1]
    u_bar = np.asarray(u_bar, dtype="<f8").reshape(N, Nb, 3)
    Sigma = np.asarray(Sigma, dtype="<f8").reshape(N, Nb, 3, 3)
    Sig6 = np.stack([
        Sigma[:, :, 0, 0], Sigma[:, :, 0, 1], Sigma[:, :, 0, 2],
        Sigma[:, :, 1, 1], Sigma[:, :, 1, 2], Sigma[:, :, 2, 2],
    ], axis=-1).astype("<f8")
    sp = np.zeros(N, dtype="<i4") if species is None else np.asarray(species, dtype="<i4").reshape(N)
    with open(path, "wb") as f:
        f.write(GRLBV_MAGIC)
        f.write(np.array([N, Nb], dtype="<i8").tobytes())
        f.write(np.array([float(time)], dtype="<f8").tobytes())
        f.write(np.ascontiguousarray(x).tobytes())
        f.write(np.ascontiguousarray(sp).tobytes())
        f.write(np.ascontiguousarray(m_basis).tobytes())
        f.write(np.ascontiguousarray(u_bar).tobytes())
        f.write(np.ascontiguousarray(Sig6).tobytes())


def read_grlbv(path: str):
    """Read GRLBV001 file and return dict(time, x, species, m, u_bar, Sigma)."""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != GRLBV_MAGIC:
            raise ValueError(f"{path}: bad magic {magic!r}")
        N, Nb = [int(v) for v in np.frombuffer(f.read(16), dtype="<i8")]
        time = float(np.frombuffer(f.read(8), dtype="<f8")[0])
        x = np.frombuffer(f.read(24 * N), dtype="<f8").reshape(N, 3).copy()
        sp = np.frombuffer(f.read(4 * N), dtype="<i4").copy()
        m_b = np.frombuffer(f.read(8 * N * Nb), dtype="<f8").reshape(N, Nb).copy()
        u_b = np.frombuffer(f.read(24 * N * Nb), dtype="<f8").reshape(N, Nb, 3).copy()
        s6 = np.frombuffer(f.read(48 * N * Nb), dtype="<f8").reshape(N, Nb, 6)
        Sig = np.zeros((N, Nb, 3, 3), dtype=np.float64)
        Sig[:, :, 0, 0] = s6[:, :, 0]
        Sig[:, :, 0, 1] = Sig[:, :, 1, 0] = s6[:, :, 1]
        Sig[:, :, 0, 2] = Sig[:, :, 2, 0] = s6[:, :, 2]
        Sig[:, :, 1, 1] = s6[:, :, 3]
        Sig[:, :, 1, 2] = Sig[:, :, 2, 1] = s6[:, :, 4]
        Sig[:, :, 2, 2] = s6[:, :, 5]
    return dict(time=time, x=x, species=sp, m=m_b, u_bar=u_b, Sigma=Sig)


# ----------------------------------------------------------------------------
# Initial-condition generators for AthenaK GR-LBV test suites
# ----------------------------------------------------------------------------
def tile_1d_in_3d(x_1d: np.ndarray, m_1d: np.ndarray, u_1d: np.ndarray, S_1d: np.ndarray,
                  Lx: float, ny: int, nz: int, Ly: float, Lz: float,
                  x0: float = 0.0, y0: float = 0.0, z0: float = 0.0):
    """Replicate a 1D-along-x configuration onto a regular (ny x nz) transverse lattice
    for 3D AthenaK verification runs."""
    Nx, Nb = m_1d.shape
    dy, dz = Ly / ny, Lz / nz
    N = Nx * ny * nz
    x = np.empty((N, 3), dtype=np.float64)
    m = np.empty((N, Nb), dtype=np.float64)
    u = np.empty((N, Nb, 3), dtype=np.float64)
    S = np.empty((N, Nb, 3, 3), dtype=np.float64)
    idx = 0
    for k in range(nz):
        zc = z0 + (k + 0.5) * dz
        for j in range(ny):
            yc = y0 + (j + 0.5) * dy
            sl = slice(idx, idx + Nx)
            x[sl, 0] = x0 + x_1d
            x[sl, 1] = yc
            x[sl, 2] = zc
            m[sl] = m_1d * (dy * dz)
            u[sl] = u_1d
            S[sl] = S_1d
            idx += Nx
    return x, m, u, S


def make_ic_st_cluster_elements(
    yc: float = 0.819,
    N_shells: int = 16,
    seed: int = 0,
    Nb: int = 4,
    vpert: float = 0.0,
):
    """Build an ordered spherical-shell GR-LBV element representation of a
    Shapiro-Teukolsky monoenergetic cluster (hot-and-ordered start + multi-basis).

    Each element carries isotropic equilibrium covariance Sigma_{ij} = (1/3) |u_eq(r)|^2 delta_{ij}
    (split across radial/tangential sub-streams or an isotropic primary basis plus small
    free slots for streaming evolution), conserving exact total rest mass M_0.
    """
    mod = STModel(float(yc))
    rng = np.random.default_rng(seed)
    # Fibonacci sphere points per radial mass shell for low-discrepancy MFM mesh
    pts_list = []
    masses_list = []
    # Equal-mass radial strata
    r_edges = mod.Finv(np.linspace(0.0, 1.0, N_shells + 1))
    n_ang_per_shell = max(12, int(round(4.0 * math.pi * (N_shells ** 2) / 6.0 / N_shells)))
    n_ang_per_shell = 32
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for s in range(N_shells):
        # Shell center by median enclosed rest mass
        u_mid = (s + 0.5) / N_shells
        rc = float(mod.Finv(u_mid))
        m_shell = mod.M0 / N_shells
        m_el = m_shell / n_ang_per_shell
        # Random rotation per shell prevents radial alignment artifacts
        rot_phi = rng.uniform(0.0, 2.0 * math.pi)
        for k in range(n_ang_per_shell):
            y = 1.0 - 2.0 * (k + 0.5) / n_ang_per_shell
            r_xy = math.sqrt(max(1.0 - y * y, 0.0))
            th = golden * k + rot_phi
            nhat = np.array([r_xy * math.cos(th), r_xy * math.sin(th), y])
            pts_list.append(rc * nhat)
            masses_list.append(m_el)

    x = np.array(pts_list, dtype=np.float64)
    m_tot = np.array(masses_list, dtype=np.float64)
    N = len(m_tot)
    r = np.sqrt(np.sum(x * x, axis=1))
    nhat = x / np.maximum(r[:, None], 1e-30)
    psi2 = mod.psi(r) ** 2
    qmag = mod.q(r)
    umag = psi2 * qmag

    m_b = np.zeros((N, Nb), dtype=np.float64)
    u_b = np.zeros((N, Nb, 3), dtype=np.float64)
    Sig_b = np.zeros((N, Nb, 3, 3), dtype=np.float64)

    # Represent isotropic shell f(u) = delta(|u| - umag) cleanly across Nb radial/anisotropic bases,
    # or 2 opposing radial bases + (Nb-2) empty slots, OR 1 hot basis + (Nb-1) small buffer slots:
    # Here we use Nb >= 2: split into 2 opposite radial-biased hemispheres along +/- nhat when Nb >= 2
    # (exact isotropic stress: mean along nhat is +/- umag/2, variance orthogonal = umag^2/3, parallel = umag^2/12)
    # Wait: verify second moment of +/- hemisphere of isotropic shell |u|=U:
    #   <u_r^2> = U^2/3; on upper hemisphere (+nhat): <u> = (U/2) nhat, Var(u_r) = U^2/3 - U^2/4 = U^2/12!
    #   Var(u_perp) = U^2/3! And sum over both hemispheres preserves isotropy and <u_r^2> = U^2/3!
    # Plus tiny 1e-6 floor in remaining slots if Nb > 2.
    frac_rem = 1e-6 * max(Nb - 2, 0) if Nb > 2 else 0.0
    w_main = 0.5 * (1.0 - frac_rem) if Nb >= 2 else 1.0
    for a in range(N):
        nn = nhat[a]
        P_par = np.outer(nn, nn)
        P_perp = np.eye(3) - P_par
        U = umag[a]
        u_shift = -vpert * U * nn if vpert != 0.0 else np.zeros(3)
        if Nb == 1:
            m_b[a, 0] = m_tot[a]
            u_b[a, 0] = u_shift
            Sig_b[a, 0] = (U * U / 3.0) * np.eye(3)
        else:
            m_b[a, 0] = w_main * m_tot[a]
            m_b[a, 1] = w_main * m_tot[a]
            u_b[a, 0] = 0.5 * U * nn + u_shift
            u_b[a, 1] = -0.5 * U * nn + u_shift
            S_hemi = (U * U / 12.0) * P_par + (U * U / 3.0) * P_perp
            Sig_b[a, 0] = S_hemi
            Sig_b[a, 1] = S_hemi
            for al in range(2, Nb):
                m_b[a, al] = 1e-6 * m_tot[a]
                u_b[a, al] = u_shift
                Sig_b[a, al] = (U * U / 3.0) * np.eye(3)
    return x, m_b, u_b, Sig_b, mod


def make_ic_os_elements(n_lat: int = 16, R0: float = 5.0, M: float = 1.0, Nb: int = 2):
    """Ordered lattice of Oppenheimer-Snyder dust elements for GR-LBV."""
    x, m_cell = _samp.os_lattice(n_lat, R0=R0, M=M)
    # Surface mass correction so sum(m) == M_rest exactly
    rb0 = _osn.isotropic_radius(R0, M)
    Mrest = _osn.rest_mass(R0, M)
    h = 2.0 * rb0 / n_lat
    r = np.sqrt(np.sum(x * x, axis=1))
    layer = r > rb0 - h
    m_cell = m_cell.copy()
    m_cell[layer] *= (Mrest - m_cell[~layer].sum()) / m_cell[layer].sum()
    N = len(m_cell)
    m_b = np.zeros((N, Nb), dtype=np.float64)
    u_b = np.zeros((N, Nb, 3), dtype=np.float64)
    Sig_b = np.zeros((N, Nb, 3, 3), dtype=np.float64)
    m_b[:, 0] = m_cell * (1.0 - 1e-8 * (Nb - 1))
    for al in range(1, Nb):
        m_b[:, al] = m_cell * 1e-8
    Sig_b[:, :, :, :] = 1e-16 * np.eye(3)[None, None, :, :]
    return x, m_b, u_b, Sig_b


def make_ic_kerr_cloud(
    a: float = 0.9,
    M: float = 1.0,
    r0: float = 10.0,
    dr: float = 2.0,
    dz: float = 0.8,
    sigma_u: float = 0.08,
    n_r: int = 4,
    n_phi: int = 24,
    n_z: int = 3,
    Nb: int = 2,
    m_tot: float = 1e-4,
):
    """Build a warm, sheared prograde relativistic cloud in Cartesian Kerr-Schild (CKS)
    coordinates around a Kerr black hole of spin `a` and mass `M` (Suite 2)."""
    r_edges = np.linspace(r0 - dr, r0 + dr, n_r + 1)
    r_vals = 0.5 * (r_edges[:-1] + r_edges[1:])
    z_edges = np.linspace(-dz, dz, n_z + 1)
    z_vals = 0.5 * (z_edges[:-1] + z_edges[1:])
    dphi = 2.0 * math.pi / n_phi
    dr_w = (2.0 * dr) / n_r
    dz_w = (2.0 * dz) / n_z

    x_bl_list = []
    u_bl_list = []
    vol_list = []
    for rv in r_vals:
        for zv in z_vals:
            rcyl = rv
            r_bl = math.sqrt(rcyl * rcyl + zv * zv)
            th_bl = math.acos(max(min(zv / r_bl, 1.0), -1.0))
            # Prograde equatorial circular specific angular momentum in BL
            sqM = math.sqrt(M)
            sq_r = math.sqrt(r_bl)
            denom_c = (r_bl ** 0.75) * math.sqrt(max(r_bl ** 1.5 - 3.0 * M * sq_r + 2.0 * a * sqM, 1e-12))
            Lz = sqM * (r_bl * r_bl - 2.0 * a * math.sqrt(M * r_bl) + a * a) / denom_c
            for kp in range(n_phi):
                ph = (kp + 0.5) * dphi
                x_bl_list.append([r_bl, th_bl, ph])
                u_bl_list.append([0.0, 0.0, Lz * (math.sin(th_bl) ** 2)])
                vol_list.append(rcyl * dr_w * dphi * dz_w)

    x_bl = np.array(x_bl_list, dtype=np.float64)
    u_bl = np.array(u_bl_list, dtype=np.float64)
    _, x_cks, u_cks = _kerr.convert_state(0.0, x_bl, u_bl, "bl", "cks", a=a, M=M)
    adm_c = _kerr.adm("cks", x_cks, a=a, M=M, derivs=False)

    weights = np.array(vol_list, dtype=np.float64)
    m_cell = m_tot * weights / np.sum(weights)
    N = len(m_cell)
    m_b = np.zeros((N, Nb), dtype=np.float64)
    u_b = np.zeros((N, Nb, 3), dtype=np.float64)
    Sig_b = np.zeros((N, Nb, 3, 3), dtype=np.float64)

    # Isotropic warm dispersion sigma_u^2 in local Eulerian normal observer triad -> sigma_u^2 * gamma_{ij}
    m_b[:, 0] = m_cell * (1.0 - 1e-8 * (Nb - 1))
    u_b[:, 0] = u_cks
    Sig_b[:, 0] = (sigma_u * sigma_u) * adm_c.gamma
    for al in range(1, Nb):
        m_b[:, al] = m_cell * 1e-8
        u_b[:, al] = u_cks
        Sig_b[:, al] = (sigma_u * sigma_u) * adm_c.gamma
    return x_cks, m_b, u_b, Sig_b


def make_ic_cosmo_wave(
    L: float = 4.0,
    n_lat: int = 12,
    delta_rho: float = 0.25,
    u_amp: float = 0.35,
    stream_u: float = 0.0,
    sigma_u: float = 1e-4,
    Nb: int = 4,
):
    """Build a 3D periodic multi-stream / Zel'dovich relativistic wave IC on [0, L)^3
    compatible with AthenaK's `nrpic_cosmo` Einstein-Vlasov driver (Suite 5)."""
    h = L / n_lat
    c1 = (np.arange(n_lat) + 0.5) * h
    gx, gy, gz = np.meshgrid(c1, c1, c1, indexing="ij")
    x = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    N = len(x)
    V = h ** 3
    rho_crit = 3.0 / (8.0 * math.pi)
    kx = 2.0 * math.pi / L
    D_x = rho_crit * (1.0 + delta_rho * np.cos(kx * x[:, 0]))
    m_cell = D_x * V
    u_wave = u_amp * np.sin(kx * x[:, 0])

    m_b = np.zeros((N, Nb), dtype=np.float64)
    u_b = np.zeros((N, Nb, 3), dtype=np.float64)
    Sig_b = np.broadcast_to((sigma_u * sigma_u) * np.eye(3), (N, Nb, 3, 3)).copy()

    if stream_u > 0.0 and Nb >= 2:
        rem = 1e-8 * max(Nb - 2, 0)
        w = 0.5 * (1.0 - rem)
        m_b[:, 0] = w * m_cell
        m_b[:, 1] = w * m_cell
        u_b[:, 0, 0] = stream_u + u_wave
        u_b[:, 1, 0] = -stream_u + u_wave
        for al in range(2, Nb):
            m_b[:, al] = 1e-8 * m_cell
            u_b[:, al, 0] = u_wave
    else:
        rem = 1e-8 * max(Nb - 1, 0)
        m_b[:, 0] = (1.0 - rem) * m_cell
        u_b[:, 0, 0] = u_wave
        for al in range(1, Nb):
            m_b[:, al] = 1e-8 * m_cell
            # Pre-seed empty high/low momentum slots cleanly inside caustic velocity range
            u_b[:, al, 0] = (-1.0 if al % 2 == 1 else 1.0) * 0.5 * max(u_amp, 0.1) + u_wave
    return x, m_b, u_b, Sig_b


# ----------------------------------------------------------------------------
# 3D Periodic MFM Reference Solver (exact twin of AthenaK C++ GR-LBV 3D logic)
# ----------------------------------------------------------------------------
def _cubic_spline_3d(r: float, h: float) -> float:
    q = r / h
    if q >= 2.0:
        return 0.0
    norm = 1.0 / (math.pi * h * h * h)
    if q < 1.0:
        return norm * (1.0 - 1.5 * q * q + 0.75 * q * q * q)
    t = 2.0 - q
    return norm * 0.25 * t * t * t


def _periodic_vec(dx: np.ndarray, box: np.ndarray) -> np.ndarray:
    return dx - box * np.round(dx / box)


def _regularized_inv3_geom(E_a: np.ndarray, eps_cond: float = 1e-3, lam_reg: float = 1e-2) -> np.ndarray:
    A = 0.5 * (E_a + E_a.T)
    tr = float(np.trace(A))
    if tr <= 1e-300:
        return np.zeros((3, 3), dtype=np.float64)
    evals = np.linalg.eigvalsh(A)
    if evals[0] <= eps_cond * evals[2]:
        A = A + (lam_reg * tr) * np.eye(3)
    return inv3_sym(A)[0]


@dataclass
class MFM3DState:
    x: np.ndarray           # (N, 3)
    m: np.ndarray           # (N, Nb)
    P: np.ndarray           # (N, Nb, 3)
    Pi: np.ndarray          # (N, Nb, 3, 3)
    box: np.ndarray         # (3,)
    h: np.ndarray           # (N,)
    V: np.ndarray           # (N,)
    Einv: np.ndarray        # (N, 3, 3)
    D: np.ndarray           # (N, Nb)
    u_bar: np.ndarray       # (N, Nb, 3)
    Sigma: np.ndarray       # (N, Nb, 3, 3)
    pair_map: dict | None = None


def init_mfm_3d(
    x: np.ndarray, D_init: np.ndarray, u_init: np.ndarray, Sig_init: np.ndarray, box
) -> MFM3DState:
    """Initialize 3D periodic MFM state from cell coordinates and primitive fields."""
    x = np.asarray(x, dtype=np.float64).copy()
    box = np.asarray(box, dtype=np.float64)
    x = x % box[None, :]
    N, Nb = D_init.shape
    h0 = float(np.prod(box) / N) ** (1.0 / 3.0)
    h = np.full(N, h0, dtype=np.float64)
    V = np.full(N, float(np.prod(box) / N), dtype=np.float64)
    st = MFM3DState(
        x=x,
        m=np.zeros((N, Nb), dtype=np.float64),
        P=np.zeros((N, Nb, 3), dtype=np.float64),
        Pi=np.zeros((N, Nb, 3, 3), dtype=np.float64),
        box=box,
        h=h,
        V=V,
        Einv=np.zeros((N, 3, 3), dtype=np.float64),
        D=D_init.copy(),
        u_bar=u_init.copy(),
        Sigma=Sig_init.copy(),
        pair_map={},
    )
    _update_3d_geometry(st)
    st.m = D_init * st.V[:, None]
    st.P = st.m[:, :, None] * u_init
    st.Pi = st.m[:, :, None, None] * (Sig_init + u_init[:, :, :, None] * u_init[:, :, None, :])
    _cons_to_prim_3d(st)
    return st


def _update_3d_geometry(st: MFM3DState):
    N = len(st.x)
    # All-pairs periodic displacement matrix (N <= ~512 for Python reference parity)
    dx_all = _periodic_vec(st.x[None, :, :] - st.x[:, None, :], st.box[None, None, :])
    r_all = np.sqrt(np.sum(dx_all * dx_all, axis=-1))
    for a in range(N):
        h = float(st.h[a])
        ra = r_all[a]
        for _ in range(45):
            q = ra / h
            w = np.where(
                q < 1.0,
                (1.0 - 1.5 * q * q + 0.75 * q * q * q),
                np.where(q < 2.0, 0.25 * (2.0 - q) ** 3, 0.0),
            ) / (math.pi * h * h * h)
            nbar = float(np.sum(w))
            h_new = (1.0 / max(nbar, 1e-300)) ** (1.0 / 3.0)
            if abs(h_new - h) < 1e-14 * h:
                h = h_new
                break
            h = 0.2 * h + 0.8 * h_new
        st.h[a] = h
        q = ra / h
        w = np.where(
            q < 1.0,
            (1.0 - 1.5 * q * q + 0.75 * q * q * q),
            np.where(q < 2.0, 0.25 * (2.0 - q) ** 3, 0.0),
        ) / (math.pi * h * h * h)
        st.V[a] = 1.0 / max(float(np.sum(w)), 1e-300)
        E_a = np.einsum("c,ci,cj->ij", w, dx_all[a], dx_all[a])
        st.Einv[a] = _regularized_inv3_geom(E_a)


def _cons_to_prim_3d(st: MFM3DState):
    for a in range(len(st.x)):
        realizability_repair_cell(st.m[a], st.P[a], st.Pi[a])
    st.D = st.m / st.V[:, None]
    st.u_bar = st.P / st.m[:, :, None]
    st.Sigma = st.Pi / st.m[:, :, None, None] - st.u_bar[:, :, :, None] * st.u_bar[:, :, None, :]
    st.Sigma = 0.5 * (st.Sigma + np.swapaxes(st.Sigma, -1, -2))


def _compute_3d_rhs(st: MFM3DState, basis_kind: int = BASIS_TOPHAT, n_perp: int = 3):
    """Exact 3D MFM pairwise flux RHS in flat space matching AthenaK C++ logic."""
    N, Nb = st.m.shape
    dx_all = _periodic_vec(st.x[None, :, :] - st.x[:, None, :], st.box[None, None, :])
    r_all = np.sqrt(np.sum(dx_all * dx_all, axis=-1))

    # Build active symmetric neighbor lists & effective areas A_ab
    if st.pair_map is None:
        st.pair_map = {}

    u_bulk = np.sum(st.P, axis=1) / np.sum(st.m, axis=1)[:, None]
    grad_D = np.zeros((N, Nb, 3), dtype=np.float64)
    grad_u = np.zeros((N, Nb, 3, 3), dtype=np.float64)
    grad_S = np.zeros((N, Nb, 3, 3, 3), dtype=np.float64)

    for a in range(N):
        ngbs = [b for b in range(N) if b != a and r_all[a, b] < 2.0 * max(st.h[a], st.h[b])]
        if not ngbs:
            continue
        ha = st.h[a]
        # Kernel weights W(r_ba, h_a)
        rvec = np.array([r_all[a, b] for b in ngbs])
        q = rvec / ha
        w_vec = np.where(
            q < 1.0,
            (1.0 - 1.5 * q * q + 0.75 * q * q * q),
            np.where(q < 2.0, 0.25 * (2.0 - q) ** 3, 0.0),
        ) / (math.pi * ha ** 3)
        dx_ngb = np.array([dx_all[a, b] for b in ngbs])
        psi_ngb = np.array([st.h[b] / (ha + st.h[b]) for b in ngbs])
        xf_ngb = psi_ngb[:, None] * dx_ngb

        for al in range(Nb):
            dD_raw = np.zeros(3)
            du_raw = np.zeros((3, 3))
            dS_raw = np.zeros((3, 3, 3))
            m_indices = []
            for idx_n, b in enumerate(ngbs):
                if (a, b) in st.pair_map:
                    be = int(st.pair_map[(a, b)][0][al])
                else:
                    be = al
                m_indices.append(be)
                vec = st.Einv[a] @ (dx_ngb[idx_n] * w_vec[idx_n])
                dD_raw += (st.D[b, be] - st.D[a, al]) * vec
                du_raw += np.outer(st.u_bar[b, be] - st.u_bar[a, al], vec)
                dS_raw += (st.Sigma[b, be] - st.Sigma[a, al])[:, :, None] * vec[None, None, :]

            # Scalar BJ limiter for D
            d_min = min(st.D[a, al], min(st.D[b, m_indices[i]] for i, b in enumerate(ngbs))) - st.D[a, al]
            d_max = max(st.D[a, al], max(st.D[b, m_indices[i]] for i, b in enumerate(ngbs))) - st.D[a, al]
            phi_D = 1.0
            for idx_n in range(len(ngbs)):
                dval = float(np.dot(dD_raw, xf_ngb[idx_n]))
                if dval > 1e-300:
                    phi_D = min(phi_D, d_max / dval)
                elif dval < -1e-300:
                    phi_D = min(phi_D, d_min / dval)
            grad_D[a, al] = max(0.0, min(1.0, phi_D)) * dD_raw

            # Componentwise velocity-crossing BJ limiter (eps_v = 0.1)
            for k in range(3):
                phi_v = 1.0
                sig_a = math.sqrt(max(st.Sigma[a, al, k, k], 0.0))
                u_min = min(st.u_bar[a, al, k], min(st.u_bar[b, m_indices[i], k] for i, b in enumerate(ngbs))) - st.u_bar[a, al, k]
                u_max = max(st.u_bar[a, al, k], max(st.u_bar[b, m_indices[i], k] for i, b in enumerate(ngbs))) - st.u_bar[a, al, k]
                for idx_n, b in enumerate(ngbs):
                    be = m_indices[idx_n]
                    sig_b = math.sqrt(max(st.Sigma[b, be, k, k], 0.0))
                    sc = max(abs(st.u_bar[a, al, k] - u_bulk[a, k]), sig_a,
                             abs(st.u_bar[b, be, k] - u_bulk[b, k]), sig_b, 1e-12)
                    if abs(float(np.dot(du_raw[k], dx_ngb[idx_n]))) >= 0.1 * sc:
                        dval = float(np.dot(du_raw[k], xf_ngb[idx_n]))
                        if dval > 1e-300:
                            phi_v = min(phi_v, u_max / dval)
                        elif dval < -1e-300:
                            phi_v = min(phi_v, u_min / dval)
                grad_u[a, al, k] = max(0.0, min(1.0, phi_v)) * du_raw[k]

            # Covariance BJ + SPD bisection limiter
            phi_S = 1.0
            for i_c in range(3):
                for j_c in range(i_c, 3):
                    smin = min(st.Sigma[a, al, i_c, j_c], min(st.Sigma[b, m_indices[n], i_c, j_c] for n, b in enumerate(ngbs))) - st.Sigma[a, al, i_c, j_c]
                    smax = max(st.Sigma[a, al, i_c, j_c], max(st.Sigma[b, m_indices[n], i_c, j_c] for n, b in enumerate(ngbs))) - st.Sigma[a, al, i_c, j_c]
                    for idx_n in range(len(ngbs)):
                        dval = float(np.dot(dS_raw[i_c, j_c], xf_ngb[idx_n]))
                        if dval > 1e-300:
                            phi_S = min(phi_S, smax / dval)
                        elif dval < -1e-300:
                            phi_S = min(phi_S, smin / dval)
            phi_S = max(0.0, min(1.0, phi_S))
            for idx_n in range(len(ngbs)):
                cand = st.Sigma[a, al] + phi_S * np.einsum("ijk,k->ij", dS_raw, xf_ngb[idx_n])
                if np.min(np.linalg.eigvalsh(0.5 * (cand + cand.T))) < 0.0:
                    lo, hi = 0.0, phi_S
                    for _ in range(16):
                        mid = 0.5 * (lo + hi)
                        cm = st.Sigma[a, al] + mid * np.einsum("ijk,k->ij", dS_raw, xf_ngb[idx_n])
                        if np.min(np.linalg.eigvalsh(0.5 * (cm + cm.T))) >= 0.0:
                            lo = mid
                        else:
                            hi = mid
                    phi_S = lo
            grad_S[a, al] = phi_S * dS_raw

    # Cell center-of-mass velocities
    v_cell = np.zeros((N, 3), dtype=np.float64)
    for a in range(N):
        tot_m = float(np.sum(st.m[a]))
        vsum = np.zeros(3)
        for al in range(Nb):
            if st.m[a, al] > 0.0:
                pts, w = basis_cubature_points(st.u_bar[a, al], st.Sigma[a, al], n_q=3)
                W = np.sqrt(1.0 + np.sum(pts * pts, axis=1))
                vsum += st.m[a, al] * np.sum((w / W)[:, None] * pts, axis=0)
        v_cell[a] = vsum / max(tot_m, 1e-300)

    dm = np.zeros_like(st.m)
    dP = np.zeros_like(st.P)
    dPi = np.zeros_like(st.Pi)
    new_pair_map = {}
    g_eye = np.eye(3)
    flip = np.diag([-1.0, 1.0, 1.0])

    # Pairwise antisymmetric face fluxes for a < b
    for a in range(N):
        for b in range(a + 1, N):
            r_ab = float(r_all[a, b])
            if r_ab >= 2.0 * max(st.h[a], st.h[b]):
                continue
            dx_ba = dx_all[a, b]
            Wa = _cubic_spline_3d(r_ab, st.h[a])
            Wb = _cubic_spline_3d(r_ab, st.h[b])
            A_ab = st.V[a] * (st.Einv[a] @ dx_ba) * Wa + st.V[b] * (st.Einv[b] @ dx_ba) * Wb
            normA = float(np.linalg.norm(A_ab))
            if normA <= 1e-30:
                continue
            normA, e_up, e_dn = face_triad(g_eye, A_ab)

            psi = st.h[b] / (st.h[a] + st.h[b])
            xf_a = psi * dx_ba
            xf_b = (psi - 1.0) * dx_ba

            Da = np.maximum(st.D[a] + grad_D[a] @ xf_a, 0.0)
            ua = st.u_bar[a] + np.einsum("aij,j->ai", grad_u[a], xf_a)
            Sa = st.Sigma[a] + np.einsum("aijk,k->aij", grad_S[a], xf_a)

            Db = np.maximum(st.D[b] + grad_D[b] @ xf_b, 0.0)
            ub = st.u_bar[b] + np.einsum("aij,j->ai", grad_u[b], xf_b)
            Sb = st.Sigma[b] + np.einsum("aijk,k->aij", grad_S[b], xf_b)

            ua_t = ua @ e_up.T
            ub_t = ub @ e_up.T
            Sa_t = np.einsum("mi,aij,nj->amn", e_up, Sa, e_up)
            Sb_t = np.einsum("mi,aij,nj->amn", e_up, Sb, e_up)

            beta_F = solve_face_beta_F(Da, ua_t, Sa_t, Db, ub_t, Sb_t, basis_kind=basis_kind, n_perp=n_perp)
            C_ab = pairing_cost_matrix(Da, ua_t, Sa_t, Db, ub_t, Sb_t, beta_F)
            C_ba = pairing_cost_matrix(Db, ub_t, Sb_t, Da, ua_t, Sa_t, beta_F)
            p_ab = np.argmin(C_ab, axis=1)
            p_ba = np.argmin(C_ba, axis=1)
            new_pair_map[(a, b)] = (p_ab, p_ba)
            new_pair_map[(b, a)] = (p_ba, p_ab)

            for al in range(Nb):
                be = int(p_ab[al])
                fm, fp_t, fpi_t, _ = onesided_flux_tetrad(Da[al], ua_t[al], Sa_t[al], beta_F,
                                                          basis_kind=basis_kind, n_perp=n_perp)
                fm *= normA
                fp = normA * (e_dn.T @ fp_t)
                fpi = normA * (e_dn.T @ fpi_t @ e_dn)
                dm[a, al] -= fm; dP[a, al] -= fp; dPi[a, al] -= fpi
                dm[b, be] += fm; dP[b, be] += fp; dPi[b, be] += fpi

            for be in range(Nb):
                al = int(p_ba[be])
                ub_rev = np.array([-ub_t[be, 0], ub_t[be, 1], ub_t[be, 2]])
                Sb_rev = flip @ Sb_t[be] @ flip
                fm, fp_rev, fpi_rev, _ = onesided_flux_tetrad(
                    Db[be], ub_rev, Sb_rev, -beta_F, basis_kind=basis_kind, n_perp=n_perp
                )
                fp_t = np.array([-fp_rev[0], fp_rev[1], fp_rev[2]])
                fpi_t = flip @ fpi_rev @ flip
                fm *= normA
                fp = normA * (e_dn.T @ fp_t)
                fpi = normA * (e_dn.T @ fpi_t @ e_dn)
                dm[b, be] -= fm; dP[b, be] -= fp; dPi[b, be] -= fpi
                dm[a, al] += fm; dP[a, al] += fp; dPi[a, al] += fpi

    st.pair_map = new_pair_map
    return v_cell, dm, dP, dPi


def step_3d_mfm(st: MFM3DState, dt: float, basis_kind: int = BASIS_TOPHAT, n_perp: int = 3):
    """Advance 3D periodic flat-space MFM state by dt via SSP-RK2."""
    x0 = st.x.copy()
    m0, P0, Pi0 = st.m.copy(), st.P.copy(), st.Pi.copy()

    v0, dm0, dP0, dPi0 = _compute_3d_rhs(st, basis_kind=basis_kind, n_perp=n_perp)
    st.x = (x0 + dt * v0) % st.box[None, :]
    st.m = m0 + dt * dm0
    st.P = P0 + dt * dP0
    st.Pi = Pi0 + dt * dPi0
    _update_3d_geometry(st)
    _cons_to_prim_3d(st)

    v1, dm1, dP1, dPi1 = _compute_3d_rhs(st, basis_kind=basis_kind, n_perp=n_perp)
    st.x = (x0 + 0.5 * dt * (v0 + v1)) % st.box[None, :]
    st.m = m0 + 0.5 * dt * (dm0 + dm1)
    st.P = P0 + 0.5 * dt * (dP0 + dP1)
    st.Pi = Pi0 + 0.5 * dt * (dPi0 + dPi1)
    _update_3d_geometry(st)
    _cons_to_prim_3d(st)


def total_invariants_3d(st: MFM3DState):
    M_tot = float(np.sum(st.m))
    P_tot = np.sum(st.P, axis=(0, 1))
    E_tot = 0.0
    gi = np.eye(3)
    for a in range(len(st.x)):
        for al in range(st.m.shape[1]):
            ea, _, _ = basis_stress_energy(st.m[a, al], st.u_bar[a, al], st.Sigma[a, al], gi)
            E_tot += ea
    return M_tot, P_tot, E_tot
