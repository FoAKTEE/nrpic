"""Own extraction of the curvature perturbation R^NR per lattice mode (g1verify).

TH = arXiv:2610.32592 appendix.tex:517-520 (P1 PRD_v2.tex:522-526 cites it):
  Phi_k = (a^2 X_k - 1)/2 + (1/4) sum_ij k_i k_j/k^2 (gt_ij - delta_ij)_k,
  R     = Phi - <K>/(3 <alpha> <Pi>) (phi - <phi>),
X = chi of AthenaK (chi_psi_power = -4), a^-2 = <chi> (box mean; differs from the
Friedmann a^-2 at second order).  Checked by hand against TH appendix.tex:397-402
(X = a^-2 (1 + 2 Phi - (2/3) lap E), gt_ij = delta_ij + 2 (d_i d_j - delta_ij lap/3) E):
the E parts cancel, Phi_k = Phi.

Mode convention of the code (scalar_field_noise.cpp:9-18): f(x) = sum over the hemisphere
of 2 Re[c_n exp(i k_n.(x - x0))], x0 the lower corner, cell centres (g + 1/2) dx, so the
unnormalised FFT F(n) = sum_g f(g) exp(-2 pi i n.g/N) gives
  c_n = F(n) exp(-i pi (n_x + n_y + n_z)/N) / N^3.
"""
import numpy as np
import scipy.fft as sfft

GT = ["gxx", "gxy", "gxz", "gyy", "gyz", "gzz"]
PAIRS = {"gxx": (0, 0), "gxy": (0, 1), "gxz": (0, 2), "gyy": (1, 1), "gyz": (1, 2), "gzz": (2, 2)}


def coefficients(field, nvec, workers=4):
    """c_n of a real field (array (N, N, N) in (z, y, x) order) at wave vectors nvec (m, 3)
    with n_x >= 0."""
    N = field.shape[0]
    F = sfft.rfftn(field, workers=workers)          # axes (z, y, x), x halved
    nx, ny, nz = nvec[:, 0], nvec[:, 1], nvec[:, 2]
    c = F[nz % N, ny % N, nx]
    return c * np.exp(-1j * np.pi * (nx + ny + nz) / N) / N ** 3


def means(fields):
    return {k: float(np.mean(v)) for k, v in fields.items()}


def rnr_coefficients(f, nvec, workers=4, with_parts=False):
    """R^NR_n from a dict of fields with phi, Pi, chi, K, alpha and (optional) gt_ij."""
    m = {k: float(np.mean(f[k])) for k in ("phi", "Pi", "chi", "K", "alpha")}
    n = nvec.astype(float)
    k2 = np.sum(n * n, axis=1)
    cchi = coefficients(f["chi"], nvec, workers)
    cphi = coefficients(f["phi"], nvec, workers)
    phi_part = 0.5 * cchi / m["chi"]
    gpart = np.zeros(len(nvec), dtype=complex)
    if all(g in f for g in GT):
        for g in GT:
            i, j = PAIRS[g]
            w = n[:, i] * n[:, j] / k2
            if i != j:
                w = 2.0 * w                      # gt_ij and gt_ji
            gpart += 0.25 * w * coefficients(f[g], nvec, workers)
    fac = -m["K"] / (3.0 * m["alpha"] * m["Pi"])
    R = phi_part + gpart + fac * cphi
    if with_parts:
        return R, dict(chi=phi_part, gt=gpart, phi=fac * cphi), m
    return R, m
