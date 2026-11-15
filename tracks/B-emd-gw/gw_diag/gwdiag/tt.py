"""Transverse-traceless projection in Fourier space on a periodic mesh, polarization and
helicity amplitudes, and the energy density spectrum of the waves.

Definitions (see README.md, section "Conventions", for the gauge assumptions):

* Lambda projector:  Lambda_ij,lm(k) = P_il P_jm - 1/2 P_ij P_lm,  P_ij = delta_ij - k_i k_j/k^2.
  It removes the trace and every longitudinal piece k_(i V_j), so Lambda S is the flat-space
  TT part of S. On a flat torus it equals York's covariant TT decomposition with respect to
  delta_ij (arXiv:2111.09163, Eqs. (decom), (LL), (veceq), source prd_v1.tex lines 163-175):
  for gamma_ij = a^2 (delta_ij + O(eps)) the two differ at O(eps^2).
* Metric perturbation: h_ij = tilde gamma_ij - delta_ij with tilde gamma_ij = gamma_ij /
  det(gamma)^(1/3) (the Z4c conformal metric). The conformal factor removes the homogeneous
  expansion, so no scale factor is needed; h^TT = Lambda h.
* Time derivative along the normal (proper time of the Eulerian observers), with the
  AthenaK sign K_ij = -(1/2 alpha)(d_t - L_beta) gamma_ij:
      d_tau h^TT_ij = -2 Lambda(tilde A)_ij,  tilde A_ij = chi (K_ij - gamma_ij K/3),
  correct to first order in the perturbation (shift terms are longitudinal at that order).
* Energy densities (G = 1 by default, c = 1):
      rho_kin  = <d_tau h^TT_ij d_tau h^TT_ij> / (64 pi G)
               = <K^TT_ab K_TT^ab> M_pl^2/2  (rho_K of arXiv:2111.09163, Eq. (rhoK), line 260),
      rho_grad = chi_bar <d_k h^TT_ij d_k h^TT_ij> / (64 pi G)   (proper gradients),
      rho_GW   = rho_kin + rho_grad; for freely propagating waves averaged over a period
                 rho_kin = rho_grad and rho_GW = <d_tau h d_tau h>/(32 pi G) (Isaacson);
                 the paper states rho_K = rho_Isaacson/2 (footnote, line 272).
* Spectrum: shells in |k| of width dk; the shell sums add up to the volume average.
"""
import numpy as np

from .grid import Grid

FOURPI = 4.0 * np.pi
AX = (-3, -2, -1)


def rfft(f):
    return np.fft.rfftn(f, axes=AX)


def irfft(F, grid):
    return np.fft.irfftn(F, s=grid.shape, axes=AX)


def _khat(grid):
    k = grid.kvec(real=True)
    kk = np.sqrt((k ** 2).sum(axis=0))
    with np.errstate(invalid="ignore", divide="ignore"):
        kh = np.where(kk > 0, k / np.where(kk > 0, kk, 1.0), 0.0)
    return k, kk, kh


def lambda_apply(F, kh):
    """Apply Lambda(khat) to a full (3, 3, ...) tensor of Fourier coefficients."""
    P = np.eye(3)[:, :, None, None, None] - kh[:, None] * kh[None, :]
    PF = np.einsum("ac...,cb...->ab...", P, F)
    PFP = np.einsum("ac...,cb...->ab...", PF, P)
    tr = np.einsum("aa...->...", PF)
    return PFP - 0.5 * P * tr


def tensor_rfft(S):
    """rfftn of the six independent components of a symmetric (3, 3, nz, ny, nx) array."""
    F = None
    for a in range(3):
        for b in range(a, 3):
            Fab = rfft(S[a, b])
            if F is None:
                F = np.empty((3, 3) + Fab.shape, dtype=complex)
            F[a, b] = Fab
            F[b, a] = Fab
    return F


def tt_project_fourier(S, grid, k0="zero", nyquist="zero"):
    """Fourier coefficients (3, 3, nz, ny, nx//2+1) of Lambda S.

    k0      'zero' sets the k = 0 mode to zero (default); 'traceless' keeps the traceless
            part of the homogeneous mode (a Bianchi-I-like shear, transverse to every k).
    nyquist 'zero' (default) removes the Nyquist planes, on which k and -k coincide and the
            projector of a real field is not defined; 'keep' projects them with k as given.
    """
    F = tensor_rfft(S)
    k, kk, kh = _khat(grid)
    T = lambda_apply(F, kh)
    if k0 == "zero":
        T[:, :, 0, 0, 0] = 0.0
    elif k0 == "traceless":
        F0 = F[:, :, 0, 0, 0]
        T[:, :, 0, 0, 0] = F0 - np.eye(3) * np.trace(F0) / 3.0
    else:
        raise ValueError(k0)
    if nyquist == "zero":
        T[:, :, grid.nyquist_mask(real=True)] = 0.0
    elif nyquist != "keep":
        raise ValueError(nyquist)
    return T


def tt_project(S, grid, **kw):
    """Lambda S in real space, a symmetric (3, 3, nz, ny, nx) array."""
    T = tt_project_fourier(S, grid, **kw)
    out = np.empty((3, 3) + grid.shape)
    for a in range(3):
        for b in range(a, 3):
            out[a, b] = irfft(T[a, b], grid)
            out[b, a] = out[a, b]
    return out


# ----------------------------------------------------------------------------------------
# 3+1 variables -> h, d_tau h

def det3(g):
    return (g[0, 0] * (g[1, 1] * g[2, 2] - g[1, 2] * g[2, 1])
            - g[0, 1] * (g[1, 0] * g[2, 2] - g[1, 2] * g[2, 0])
            + g[0, 2] * (g[1, 0] * g[2, 1] - g[1, 1] * g[2, 0]))


def inv3(g):
    d = det3(g)
    inv = np.empty_like(g)
    inv[0, 0] = g[1, 1] * g[2, 2] - g[1, 2] * g[2, 1]
    inv[0, 1] = g[0, 2] * g[2, 1] - g[0, 1] * g[2, 2]
    inv[0, 2] = g[0, 1] * g[1, 2] - g[0, 2] * g[1, 1]
    inv[1, 1] = g[0, 0] * g[2, 2] - g[0, 2] * g[2, 0]
    inv[1, 2] = g[0, 2] * g[1, 0] - g[0, 0] * g[1, 2]
    inv[2, 2] = g[0, 0] * g[1, 1] - g[0, 1] * g[1, 0]
    inv[1, 0] = inv[0, 1]
    inv[2, 0] = inv[0, 2]
    inv[2, 1] = inv[1, 2]
    return inv / d, d


def conformal_from_adm(gamma, K):
    """chi = det(gamma)^(-1/3), tilde gamma = chi gamma, tilde A = chi (K - gamma trK/3)."""
    ginv, d = inv3(gamma)
    chi = d ** (-1.0 / 3.0)
    trK = np.einsum("ab...,ab...->...", ginv, K)
    gt = chi * gamma
    At = chi * (K - gamma * trK / 3.0)
    return chi, gt, At, trK


def h_and_hdot(gt, At):
    """(h, d_tau h) before projection: h = tilde gamma - delta, d_tau h = -2 tilde A."""
    h = gt - np.eye(3)[:, :, None, None, None]
    return h, -2.0 * At


def tt_from_conformal(gt, At, grid, **kw):
    """h^TT and d_tau h^TT from the conformal metric and the conformal trace-free
    extrinsic curvature (the Z4c variables, or conformal_from_adm)."""
    h, hd = h_and_hdot(gt, At)
    return tt_project(h, grid, **kw), tt_project(hd, grid, **kw)


def tt_from_adm(gamma, K, grid, **kw):
    """h^TT, d_tau h^TT and the mean conformal factor from gamma_ij, K_ij."""
    chi, gt, At, _ = conformal_from_adm(gamma, K)
    hTT, hdTT = tt_from_conformal(gt, At, grid, **kw)
    return hTT, hdTT, float(np.mean(chi))


# ----------------------------------------------------------------------------------------
# energies and spectra

def _shell_sum(P, grid, dk=None):
    """Sum a Fourier-space density P (rfft half space, weights included) into |k| shells."""
    edges, dk = grid.wavenumber_bins(dk)
    k = grid.kvec(real=True)
    kk = np.sqrt((k ** 2).sum(axis=0))
    idx = np.digitize(kk.ravel(), edges) - 1
    w = grid.rfft_weights().ravel()
    nb = len(edges) - 1
    s = np.bincount(idx, weights=P.ravel(), minlength=nb + 1)[:nb]
    cnt = np.bincount(idx, weights=w, minlength=nb + 1)[:nb]
    kc = 0.5 * (edges[1:] + edges[:-1])
    return kc, s, cnt, dk


def power_tensor(F, grid):
    """Weighted sum over components |F_ij(k)|^2 / N^2 on the rfft half space: the
    contribution of each mode to the volume average <f_ij f_ij>."""
    P = np.zeros(F.shape[2:])
    for a in range(3):
        for b in range(3):
            P += np.abs(F[a, b]) ** 2
    return P * grid.rfft_weights() / grid.ncell ** 2


def gw_spectrum(hTT, hdTT, grid, G=1.0, chi_bar=1.0, dk=None, lapse=1.0):
    """Energy density spectrum of the waves.

    hTT, hdTT: TT metric perturbation and its proper-time derivative, (3, 3, nz, ny, nx).
    chi_bar converts coordinate to proper gradients (chi = a^-2 for gamma = a^2 delta);
    lapse divides hdTT if it is a coordinate-time derivative (pass the mean lapse).
    Returns dict: k (shell centres), dk, counts (number of modes), the shell sums
    rho_kin, rho_grad (they add up to the volume averages), the totals, and
    drho_dlnk = (rho_kin + rho_grad) k/dk.
    """
    Fh = tensor_rfft(hTT)
    Fd = tensor_rfft(hdTT) / lapse
    k = grid.kvec(real=True)
    kk2 = (k ** 2).sum(axis=0)
    Pk = power_tensor(Fd, grid) / (16 * FOURPI * G)
    Pg = chi_bar * kk2 * power_tensor(Fh, grid) / (16 * FOURPI * G)
    kc, sk, cnt, dk = _shell_sum(Pk, grid, dk)
    _, sg, _, _ = _shell_sum(Pg, grid, dk)
    return {"k": kc, "dk": dk, "counts": cnt, "rho_kin": sk, "rho_grad": sg,
            "rho_kin_total": float(sk.sum()), "rho_grad_total": float(sg.sum()),
            "drho_dlnk": (sk + sg) * kc / dk}


def rho_kin_field(At_TT, G=1.0):
    """Local rho_K(x) = (1/16 pi G) Lambda(tilde A)_ij Lambda(tilde A)_ij (indices with
    delta, i.e. tilde gamma = delta at this order)."""
    return np.einsum("ab...,ab...->...", At_TT, At_TT) / (4 * FOURPI * G)


# ----------------------------------------------------------------------------------------
# polarizations

def pol_basis(kh):
    """(e_plus, e_cross, u, v) for unit vectors kh (3, ...): u = theta-hat, v = phi-hat of
    the direction kh (theta from +z, phi from +x towards +y); at kh = +-z the basis is
    u = (+-1, 0, 0), v = (0, 1, 0). e_plus = u u - v v, e_cross = u v + v u. (u, v, kh)
    is right-handed."""
    kz = np.clip(kh[2], -1.0, 1.0)
    th = np.arccos(kz)
    ph = np.arctan2(kh[1], kh[0])
    u = np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])
    v = np.array([-np.sin(ph), np.cos(ph), np.zeros_like(ph)])
    ep = u[:, None] * u[None, :] - v[:, None] * v[None, :]
    ex = u[:, None] * v[None, :] + v[:, None] * u[None, :]
    return ep, ex, u, v


def polarization_fourier(hTT, grid):
    """Fourier amplitudes h_+(k), h_x(k) = (1/2) e^{+,x}_ij hhat_ij on the rfft half space,
    normalized so that a mode h_ij = A e^+_ij cos(k.x) gives |h_+(k)| = A/2 (FFT / N)."""
    F = tensor_rfft(hTT) / grid.ncell
    _, kk, kh = _khat(grid)
    ep, ex, _, _ = pol_basis(kh)
    hp = 0.5 * np.einsum("ab...,ab...->...", ep, F)
    hx = 0.5 * np.einsum("ab...,ab...->...", ex, F)
    return hp, hx


def polarization_along(hTT, nhat):
    """Real-space h_+, h_x for waves along one direction nhat (coordinate unit vector),
    in the basis of pol_basis(nhat)."""
    nh = np.asarray(nhat, float)
    nh = nh / np.linalg.norm(nh)
    ep, ex, _, _ = pol_basis(nh.reshape(3, 1, 1, 1))
    hp = 0.5 * np.einsum("ab...,ab...->...", ep, hTT)
    hx = 0.5 * np.einsum("ab...,ab...->...", ex, hTT)
    return hp, hx


def helicity_spectrum(hTT, hdTT, grid, G=1.0, chi_bar=1.0, dk=None):
    """Energy density of the waves of physical helicity +2 and -2, per |k| shell, for free
    waves with omega = sqrt(chi_bar) |k| (proper frequency of a mode of coordinate
    wavenumber k; flat background or sub-horizon modes in FLRW).

    Each Fourier mode is split into the parts moving along +k and along -k,
    a_fwd = (hhat + i hdhat/omega)/2, a_bwd = (hhat - i hdhat/omega)/2 (a mode
    exp(i(k.x - omega t)) is purely forward), and each part into the helicity basis
    e^(+-2) = (e_plus +- i e_cross)/sqrt(2) of pol_basis(k), with amplitudes
    a_(+-2) = (a_+ -+ i a_x)/sqrt(2). A forward part with label +2 has physical helicity +2
    (its pattern turns counterclockwise about its direction of motion, with the time
    dependence exp(-i omega t)); a backward part with label +2 turns clockwise about k while
    moving along -k, so it has physical helicity +2 as well. The split only removes the
    interference of the two parts: since |hdhat|^2 + omega^2 |hhat|^2
    = 2 omega^2 (|a_fwd|^2 + |a_bwd|^2) mode by mode, the two helicity energies add up
    exactly to rho_kin + rho_grad of gw_spectrum and do not oscillate in time."""
    Fh = tensor_rfft(hTT) / grid.ncell
    Fd = tensor_rfft(hdTT) / grid.ncell
    _, kk, kh = _khat(grid)
    om = np.sqrt(chi_bar) * kk
    with np.errstate(invalid="ignore", divide="ignore"):
        inv = np.where(om > 0, 1.0 / np.where(om > 0, om, 1.0), 0.0)
    ep, ex, _, _ = pol_basis(kh)
    w = grid.rfft_weights()
    Pplus = np.zeros(kk.shape)
    Pminus = np.zeros(kk.shape)
    for sgn in (+1, -1):
        A = 0.5 * (Fh + sgn * 1j * Fd * inv)
        ap = 0.5 * np.einsum("ab...,ab...->...", ep, A)
        ax = 0.5 * np.einsum("ab...,ab...->...", ex, A)
        Pplus += np.abs(ap - 1j * ax) ** 2 / 2.0        # |a_(+2)|^2
        Pminus += np.abs(ap + 1j * ax) ** 2 / 2.0       # |a_(-2)|^2
    # |a_ij|^2 = 2 sum_lam |a_lam|^2; energy per mode (1/64 pi G) 2 omega^2 |a_ij|^2
    fac = 4.0 * om ** 2 * w / (16 * FOURPI * G)
    kc, sp, _, dk = _shell_sum(fac * Pplus, grid, dk)
    _, sm, _, _ = _shell_sum(fac * Pminus, grid, dk)
    return {"k": kc, "dk": dk, "rho_plus": sp, "rho_minus": sm,
            "rho_plus_total": float(sp.sum()), "rho_minus_total": float(sm.sum())}
