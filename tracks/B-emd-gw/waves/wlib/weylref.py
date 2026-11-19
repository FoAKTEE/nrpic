"""Closed-form Weyl scalar of a tensor mode on a flat FLRW slice, and its inversion.

Fields of the slice (lapse alpha = a, zero shift, t conformal time; flat space: a = 1,
calH = 0):
    gamma_ij = a^2 (delta_ij + h_ij),   K_ij = -(calH/a) gamma_ij - (a/2) h'_ij,
with h transverse-traceless. To first order in h (derivation in ../JOURNAL.md, entry
"Derivation of the closed form", and the check against gw_diag's full evaluation in
tests/test_refs.py), in coordinate components
    E_ij = [R_ij + K K_ij - K_ik K^k_j]^TF = (1/2)(-lap h_ij + calH h'_ij),
    B_ij = sym(eps_i^kl D_k K_lj)           = -(1/2) sym(eps_ikl d_k h'_lj),
and Psi_4 = -(E - iB)_ij mbar^i mbar^j with the triad of gw_diag (weyl.triad, fixed
direction, orthonormal with respect to gamma = a^2 delta, so each mbar carries 1/a).
The matter term -4 pi S_ij^TF vanishes for dust at rest.
"""
import numpy as np

from . import HERE  # noqa: F401
from gwdiag import weyl
from gwdiag.analytic import EPS3

from .refs import mode_coeff, tensor_field


def _spectral(grid):
    return weyl.Deriv(grid, order="spectral")


def em_from_tt(h, hp, calH, grid):
    """E_ij, B_ij (coordinate components) of the closed form, spectral derivatives."""
    D = _spectral(grid)
    lap = np.zeros_like(h)
    for a in range(3):
        for b in range(a, 3):
            lap[a, b] = sum(D.d2(h[a, b], c, c) for c in range(3))
            lap[b, a] = lap[a, b]
    E = 0.5 * (-lap + calH * hp)
    dhp = np.empty((3,) + h.shape)
    for c in range(3):
        for a in range(3):
            for b in range(a, 3):
                dhp[c, a, b] = D.d1(hp[a, b], c)
                dhp[c, b, a] = dhp[c, a, b]
    C = -0.5 * np.einsum("ikl,klj...->ij...", EPS3, dhp)
    B = 0.5 * (C + np.einsum("ij...->ji...", C))
    return E, B


def psi4_from_tt(h, hp, a, calH, grid, direction):
    """Psi_4 along a fixed direction from the TT fields h, h' (closed form)."""
    E, B = em_from_tt(h, hp, calH, grid)
    gam = (a ** 2) * np.broadcast_to(np.eye(3)[:, :, None, None, None], h.shape).copy()
    return weyl.psi4(E, B, gam, grid, direction=direction)


def psi4_coeffs(p4_fwd, p4_bwd, grid, kvec):
    """The eight real numbers (Re, Im of the coefficients at +k and -k of Psi_4 along +n
    and along -n), n = khat."""
    kv = np.asarray(kvec, float)
    out = []
    for f in (p4_fwd, p4_bwd):
        for s in (+1, -1):
            c = mode_coeff(f, grid, s * kv)
            out += [c.real, c.imag]
    return np.array(out)


def inversion_matrix(grid, kvec, a, calH):
    """8 x 8 matrix M with psi4_coeffs = M u, u = (Re P, Im P, Re X, Im X, Re P', Im P',
    Re X', Im X'), built by applying the closed form to unit amplitudes."""
    kv = np.asarray(kvec, float)
    n = kv / np.linalg.norm(kv)
    M = np.empty((8, 8))
    for j in range(8):
        u = np.zeros(8)
        u[j] = 1.0
        P, X = u[0] + 1j * u[1], u[2] + 1j * u[3]
        Pd, Xd = u[4] + 1j * u[5], u[6] + 1j * u[7]
        h = tensor_field(P, X, grid, kv)
        hp = tensor_field(Pd, Xd, grid, kv)
        f = psi4_from_tt(h, hp, a, calH, grid, n)
        b = psi4_from_tt(h, hp, a, calH, grid, -n)
        M[:, j] = psi4_coeffs(f, b, grid, kv)
    return M


def invert(coeffs, M):
    """(P, X, P', X') implied by measured Psi_4 coefficients."""
    u = np.linalg.solve(M, coeffs)
    return u[0] + 1j * u[1], u[2] + 1j * u[3], u[4] + 1j * u[5], u[6] + 1j * u[7]
