"""Electric and magnetic parts of the Weyl tensor and the Weyl scalar Psi_4 on a periodic
mesh, from the 3+1 variables gamma_ij, K_ij (layout: grid.py).

Conventions (README.md, section "Conventions"):

* K_ij = -(1/2 alpha)(d_t - L_beta) gamma_ij (AthenaK sign).
* E_ij = TF[R_ij + K K_ij - K_ik K^k_j] - 4 pi TF[S_ij]   (S_ij optional, the spatial stress),
  the trace-free part taken with gamma; in vacuum the trace vanishes by the Hamiltonian
  constraint.
* B_ij = sym(eps_i^kl D_k K_lj),  eps_ijk = sqrt(gamma) [ijk].
* For a propagation direction u, the triad (u, v, w) with v, w the theta-hat and phi-hat of
  u, orthonormalized with gamma in the order w, u, v (the order of
  athenak/src/z4c/z4c_calculate_weyl_scalars.cpp), mbar = (v - i w)/sqrt(2) and
      Psi_4 = -(E_ij - i B_ij) mbar^i mbar^j.
  For a linear wave moving along +u in TT gauge this is Psi_4 = d_t^2 h_+ - i d_t^2 h_x
  in the basis of tt.pol_basis(u), and a wave moving along -u gives zero; the same
  combination is what AthenaK writes as (weyl_rpsi4 + i weyl_ipsi4)/r with u the radial
  direction about the origin (derivation in JOURNAL.md, checked numerically on AthenaK
  output in scripts/validate_athenak.py).

Derivatives: periodic centred finite differences of order 2, 4, 6 (the stencils of
athenak/src/utils/finite_diff.hpp for nghost = 2, 3, 4) or spectral ('spectral').
Memory: about 60 full-size float64 arrays (64^3: 130 MB, 128^3: 1 GB).
"""
import numpy as np

from .grid import axis_of
from .tt import inv3, det3

FD1 = {2: [(1, 1 / 2)],
       4: [(1, 2 / 3), (2, -1 / 12)],
       6: [(1, 3 / 4), (2, -3 / 20), (3, 1 / 60)]}
FD2 = {2: (-2.0, [(1, 1.0)]),
       4: (-5 / 2, [(1, 4 / 3), (2, -1 / 12)]),
       6: (-49 / 18, [(1, 3 / 2), (2, -3 / 20), (3, 1 / 90)])}
SYM = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


class Deriv:
    """Periodic derivative operators on a Grid; order in {2, 4, 6, 'spectral'}."""

    def __init__(self, grid, order=4):
        self.g = grid
        self.order = order
        if order == "spectral":
            self.k = grid.kvec(real=True)

    def d1(self, f, a):
        if self.order == "spectral":
            # the mean is removed first: it does not contribute to a derivative, and an
            # array 1 + h with h << 1 would otherwise put its FFT round-off into every mode
            F = np.fft.rfftn(f - f.mean(), axes=(-3, -2, -1))
            F *= 1j * self.k[a]
            # the Nyquist mode of an odd derivative is not representable for a real field
            F[..., self.g.nyquist_mask(real=True)] = 0.0
            return np.fft.irfftn(F, s=self.g.shape, axes=(-3, -2, -1))
        ax = axis_of(a)
        out = np.zeros_like(f)
        for s, c in FD1[self.order]:
            out += c * (np.roll(f, -s, axis=ax) - np.roll(f, s, axis=ax))
        return out / self.g.dx[a]

    def d2(self, f, a, b):
        if self.order == "spectral":
            F = np.fft.rfftn(f - f.mean(), axes=(-3, -2, -1))
            F *= -self.k[a] * self.k[b]
            if a != b:
                F[..., self.g.nyquist_mask(real=True)] = 0.0
            return np.fft.irfftn(F, s=self.g.shape, axes=(-3, -2, -1))
        if a != b:
            return self.d1(self.d1(f, a), b)
        ax = axis_of(a)
        c0, cs = FD2[self.order]
        out = c0 * f
        for s, c in cs:
            out = out + c * (np.roll(f, -s, axis=ax) + np.roll(f, s, axis=ax))
        return out / self.g.dx[a] ** 2


def trace_free(X, g, ginv):
    tr = np.einsum("ab...,ab...->...", ginv, X)
    return X - g * tr / 3.0, tr


def ricci(gamma, D):
    """Ricci tensor R_ij of gamma_ij, its Christoffel symbols and inverse metric.
    R_ij = 1/2 g^kl (d_k d_j g_il + d_i d_l g_kj - d_i d_j g_kl - d_k d_l g_ij)
           + g^kl (G^m_il G_mkj - G^m_ij G_mkl)."""
    ginv, detg = inv3(gamma)
    dg = np.empty((3, 3, 3) + gamma.shape[2:])          # dg[c, a, b] = d_c g_ab
    for c in range(3):
        for a, b in SYM:
            dg[c, a, b] = D.d1(gamma[a, b], c)
            dg[c, b, a] = dg[c, a, b]
    # Christoffel of the first kind G_kij = 1/2 (d_i g_kj + d_j g_ki - d_k g_ij)
    G1 = 0.5 * (np.einsum("ikj...->kij...", dg) + np.einsum("jki...->kij...", dg) - dg)
    G2 = np.einsum("km...,mij...->kij...", ginv, G1)    # G^k_ij
    # second derivatives dd[(c,d)][(a,b)] = d_c d_d g_ab
    dd = {}
    for c, d in SYM:
        for a, b in SYM:
            dd[(c, d, a, b)] = D.d2(gamma[a, b], c, d)

    def DD(c, d, a, b):
        c, d = min(c, d), max(c, d)
        a, b = min(a, b), max(a, b)
        return dd[(c, d, a, b)]

    # quadratic part g^kl (G^m_il G_mkj - G^m_ij G_mkl), as full tensors
    T = np.einsum("kl...,mkj...->mlj...", ginv, G1)            # g^kl G_mkj
    Q = np.einsum("mil...,mlj...->ij...", G2, T)
    trG = np.einsum("kl...,mkl...->m...", ginv, G1)            # g^kl G_mkl
    Q -= np.einsum("mij...,m...->ij...", G2, trG)
    R = np.zeros_like(gamma)
    for i, j in SYM:
        acc = Q[i, j].copy()
        for k in range(3):
            for l in range(3):
                acc += 0.5 * ginv[k, l] * (DD(k, j, i, l) + DD(i, l, k, j)
                                           - DD(i, j, k, l) - DD(k, l, i, j))
        R[i, j] = acc
        R[j, i] = acc
    return R, G2, ginv, detg


def levi_civita():
    e = np.zeros((3, 3, 3))
    e[0, 1, 2] = e[1, 2, 0] = e[2, 0, 1] = 1.0
    e[0, 2, 1] = e[2, 1, 0] = e[1, 0, 2] = -1.0
    return e


def electric_magnetic(gamma, K, grid, order=4, S=None, return_all=False):
    """E_ij and B_ij (symmetric, trace-free) from gamma_ij, K_ij; S_ij optional (the
    spatial stress of the matter, same layout). Returns (E, B) or, with return_all, a dict
    with E, B, R (Ricci), the Hamiltonian-constraint residual of vacuum and the
    antisymmetric part of eps D K (the momentum constraint up to a factor)."""
    D = Deriv(grid, order)
    R, G2, ginv, detg = ricci(gamma, D)
    Kud = np.einsum("ik...,kj...->ij...", ginv, K)          # K^i_j
    trK = np.einsum("ii...->...", Kud)
    KK = np.einsum("ik...,kj...->ij...", K, Kud)            # K_ik K^k_j
    Eraw = R + trK * K - KK
    if S is not None:
        Eraw = Eraw - 8.0 * np.pi * 0.5 * S
    E, trE = trace_free(Eraw, gamma, ginv)
    # D_k K_lj = d_k K_lj - G^m_kl K_mj - G^m_kj K_lm
    dK = np.empty((3, 3, 3) + gamma.shape[2:])
    for k in range(3):
        for a, b in SYM:
            dK[k, a, b] = D.d1(K[a, b], k)
            dK[k, b, a] = dK[k, a, b]
    DK = (dK - np.einsum("mkl...,mj...->klj...", G2, K)
          - np.einsum("mkj...,lm...->klj...", G2, K))
    eps_up = levi_civita()[:, :, :, None, None, None] / np.sqrt(detg)   # eps^mkl
    eps_dud = np.einsum("im...,mkl...->ikl...", gamma, eps_up)          # eps_i^kl
    C = np.einsum("ikl...,klj...->ij...", eps_dud, DK)
    B = 0.5 * (C + np.einsum("ij...->ji...", C))
    if not return_all:
        return E, B
    return {"E": E, "B": B, "R": R, "trE_vacuum": trE, "antisym": 0.5 * (C - np.einsum(
        "ij...->ji...", C)), "trK": trK}


# ----------------------------------------------------------------------------------------
# tetrad and Psi_4

def _theta_phi_hat(u):
    """theta-hat and phi-hat of the (coordinate) direction field u (3, ...)."""
    n = np.sqrt((u ** 2).sum(axis=0))
    uz = np.clip(u[2] / n, -1, 1)
    th = np.arccos(uz)
    ph = np.arctan2(u[1], u[0])
    v = np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])
    w = np.array([-np.sin(ph), np.cos(ph), np.zeros_like(ph)])
    return v, w


def _dot(g, a, b):
    return np.einsum("ab...,a...,b...->...", g, a, b)


def triad(gamma, grid, direction=None, origin=(0.0, 0.0, 0.0)):
    """Orthonormal triad (u, v, w) w.r.t. gamma at every cell.

    direction = (nx, ny, nz): a fixed propagation direction (for plane waves on the torus);
    direction = None: radial about origin, built exactly as AthenaK does
    (z4c_calculate_weyl_scalars.cpp: u = x, v = (x z, y z, -(x^2 + y^2)), w = (-y, x, 0),
    x shifted by 1e-8 on the z axis), for comparison with its weyl output."""
    shp = gamma.shape[2:]
    if direction is not None:
        nh = np.asarray(direction, float)
        nh = nh / np.linalg.norm(nh)
        u = np.broadcast_to(nh.reshape(3, 1, 1, 1), (3,) + shp).copy()
        v, w = _theta_phi_hat(u)
    else:
        X, Y, Z = grid.mesh()
        X = X - origin[0]
        Y = Y - origin[1]
        Z = Z - origin[2]
        X = np.where(X ** 2 + Y ** 2 < 1e-10, X + 1e-8, X)
        u = np.array([X, Y, Z])
        v = np.array([X * Z, Y * Z, -X ** 2 - Y ** 2])
        w = np.array([-Y, X, np.zeros_like(X)])
    w = w / np.sqrt(_dot(gamma, w, w))
    u = u - _dot(gamma, w, u) * w
    u = u / np.sqrt(_dot(gamma, u, u))
    v = v - _dot(gamma, w, v) * w - _dot(gamma, u, v) * u
    v = v / np.sqrt(_dot(gamma, v, v))
    return u, v, w


def psi4(E, B, gamma, grid, direction=None, origin=(0.0, 0.0, 0.0)):
    """Psi_4 = -(E_ij - i B_ij) mbar^i mbar^j, mbar = (v - i w)/sqrt(2), triad from triad()."""
    u, v, w = triad(gamma, grid, direction, origin)
    mb = (v - 1j * w) / np.sqrt(2.0)
    Q = E - 1j * B
    return -np.einsum("ab...,a...,b...->...", Q, mb, mb)


def psi0_like(E, B, gamma, grid, direction):
    """The incoming-radiation partner: Psi_4 for the reversed direction, -(E - iB) m m with
    m = conj(mbar) of the triad of -direction. Zero for a wave moving along +direction."""
    return psi4(E, B, gamma, grid, direction=-np.asarray(direction, float))
