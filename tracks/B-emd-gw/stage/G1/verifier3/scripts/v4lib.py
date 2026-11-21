"""verifier3, V4: second-order spatial-gauge piece of the flat TT projection (my own
derivation, JOURNAL entry 12; written without reading first_source/fslib/gauge.py).

Layout as in diag.py: vectors v[a, i, j, k], tensors T[a, b, i, j, k], axis a = direction a.
Old (zero-shift) coordinates X, new (Gamma-driver) coordinates x, X = x + zeta(x).
- plain metric perturbation h = gamma/a^2 - delta:
    G  = Lambda[L_zeta h_old + dzeta dzeta^T]           (one-sided)
       = Lambda[L_zeta hbar]                            (symmetric, hbar = (h_old + h_new)/2)
- conformal metric ht = det(gamma)^(-1/3) gamma - delta (density of weight -2/3):
    Gt = Lambda[L_zeta ht_old + dzeta dzeta^T - (2/3) div(zeta) (ht_old + dzeta + dzeta^T)]
       = Lambda[L_zeta htbar - (2/3) div(zeta) htbar]
  with (L_zeta h)_ij = zeta^k d_k h_ij + h_kj d_i zeta^k + h_ik d_j zeta^k and
  (dzeta dzeta^T)_ij = d_i zeta^k d_j zeta^k. Then Lambda h_new = Lambda h_old + G + O(3).
"""
import numpy as np

import diag


def grad_vec(zeta, grid):
    """dz[c, k] = d_c zeta^k (spectral)."""
    return np.array([diag.dspec(zeta, grid, c) for c in range(3)])


def grad_ten(h, grid):
    """dh[c, i, j] = d_c h_ij (spectral)."""
    return np.array([diag.dspec(h, grid, c) for c in range(3)])


def lie_tensor(h, zeta, grid, dz=None):
    dz = grad_vec(zeta, grid) if dz is None else dz
    dh = grad_ten(h, grid)
    t1 = np.einsum("k...,kij...->ij...", zeta, dh)
    t2 = np.einsum("kj...,ik...->ij...", h, dz)
    t3 = np.einsum("ik...,jk...->ij...", h, dz)
    return t1 + t2 + t3


def gauge_piece(zeta, grid, h_old=None, h_new=None, conformal=True, form="one", project=True):
    """second-order change of Lambda(h) from old to new coordinates (see module doc).
    form 'one' needs h_old; 'sym' needs h_old and h_new. Returns Lambda[...] (or the field
    before projection with project=False)."""
    dz = grad_vec(zeta, grid)
    divz = np.einsum("kk...->...", dz)
    if form == "one":
        h = h_old
        F = lie_tensor(h, zeta, grid, dz) + np.einsum("ik...,jk...->ij...", dz, dz)
        if conformal:
            sdz = dz + np.swapaxes(dz, 0, 1)
            F = F - (2.0 / 3.0) * divz * (h + sdz)
    elif form == "sym":
        hb = 0.5 * (h_old + h_new)
        F = lie_tensor(hb, zeta, grid, dz)
        if conformal:
            F = F - (2.0 / 3.0) * divz * hb
    else:
        raise ValueError(form)
    return diag.tt_project(F, grid) if project else F


def zeta_from_difference(D, grid, conformal=True):
    """first-order displacement from D = h_new - h_old = 2 d_(i zeta_j) [- (2/3) div zeta delta]."""
    kx, ky, kz = grid.kvecs(real=False)
    kk = [kx, ky, kz]
    k2 = kx ** 2 + ky ** 2 + kz ** 2
    mask = k2 > 0
    for a, n in enumerate(grid.n):
        if n % 2 == 0:
            mask &= ~np.isclose(np.abs(kk[a]), np.pi / grid.h[a])
    with np.errstate(invalid="ignore", divide="ignore"):
        inv = np.where(mask, 1.0 / np.where(k2 > 0, k2, 1.0), 0.0)
    Dk = np.fft.fftn(D, axes=(-3, -2, -1))
    kD = [sum(kk[j] * Dk[i, j] for j in range(3)) for i in range(3)]
    kkD = sum(kk[i] * kD[i] for i in range(3))
    if conformal:
        kz_ = -0.75j * kkD * inv
        zk = [(-1j * kD[i] - (1.0 / 3.0) * kk[i] * kz_) * inv for i in range(3)]
    else:
        kz_ = -0.5j * kkD * inv
        zk = [(-1j * kD[i] - kk[i] * kz_) * inv for i in range(3)]
    return np.array([np.real(np.fft.ifftn(z, axes=(-3, -2, -1))) for z in zk])


def conformal(gam):
    _, det = diag.inv3(gam)
    return gam / np.cbrt(det)
