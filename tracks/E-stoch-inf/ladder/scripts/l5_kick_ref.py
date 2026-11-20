#!/usr/bin/env python3
"""Reference for the single-kick test L5 (../JOURNAL.md entry 14): the first-order momentum
constraint of ONE step of the kick of one shell on a homogeneous background, on the root
mesh of the code, for the two projectors of the anisotropic kick.

Kick of a step (coord/INTERFACES/scalar_field.md 7.3, linear order, alpha_b = 1):
    dK = -eps1 I dt,   dA_ij = eps1 (delta_ij I/3 - T_ij) dt,   T_ij = p_i p_j / p^2 I
with p = q (the symbol of the sixth-order centred first difference, `noise_projector =
stencil`) or p = n (`continuum`).  The linear momentum constraint of the discrete
evolution (`Z4c::ADMConstraints`, sixth-order first differences, symbol i q_j) is
    M_i = D_j dA_ij - (2/3) D_i dK = i eps1 dt [q_i - q_j p_i p_j / p^2] I_n   per mode,
and the magnitude of P1 (scalar_field_2.md section 3), at the same order,
    [M_i] = |D_j dA_ij| + (2/3)|D_i dK|,   [M] = sqrt(sum_i [M_i]^2).
eps1 dt and the complex shell factor cancel in rms|M| / <[M]>.  Amplitudes alpha_n: Track
E's Philox twin (noise/ref/philox_ref.py), seed 20261115, dof 0, epoch 0, as in the run.

    l5_kick_ref.py [--nmesh 64] [--n2 5] [--out JSON]

Prints the ratio for both projectors (the continuum one is the size of the first-order
momentum violation the kick itself makes; the stencil one is rounding), and the relative
mismatch between the second-difference symbol and the square of the first-difference
symbol per axis (the size of the first-order constraint violation the discrete
evolution makes once the kicked fields evolve).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "noise", "ref")))
from philox_ref import mode_alpha  # noqa: E402

SEED = 20261115


def q_symbol(theta):
    """h times the symbol of the sixth-order centred first difference (finite_diff.hpp)."""
    return 1.5 * np.sin(theta) - 0.3 * np.sin(2 * theta) + np.sin(3 * theta) / 30.0


def k2_symbol(theta):
    """h^2 times minus the symbol of the sixth-order centred second difference."""
    return -(-49.0 / 18.0 + 3.0 * np.cos(theta) - 0.3 * np.cos(2 * theta)
             + (2.0 / 90.0) * np.cos(3 * theta))


def shell_modes(n2):
    m = int(np.ceil(np.sqrt(n2)))
    r = np.arange(-m, m + 1)
    nz, ny, nx = np.meshgrid(r, r, r, indexing="ij")
    n = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=1)
    hemi = (n[:, 0] > 0) | ((n[:, 0] == 0) & (n[:, 1] > 0)) | \
        ((n[:, 0] == 0) & (n[:, 1] == 0) & (n[:, 2] > 0))
    return n[hemi & ((n * n).sum(axis=1) == n2)]


def field(nmesh, n, coef):
    """sum over modes of 2 Re[coef_n exp(i n.x)] on the cell centres of [0, 2 pi)^3,
    arrays [z, y, x]; coef has shape (modes,) or (modes, 3)."""
    h = 2 * np.pi / nmesh
    x = (np.arange(nmesh) + 0.5) * h
    out = np.zeros((nmesh, nmesh, nmesh) + coef.shape[1:])
    for j, nn in enumerate(n):
        ph = np.exp(1j * (nn[0] * x[None, None, :] + nn[1] * x[None, :, None]
                          + nn[2] * x[:, None, None]))
        if coef.ndim == 1:
            out += 2 * np.real(coef[j] * ph)
        else:
            out += 2 * np.real(coef[j][None, None, None, :] * ph[..., None])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmesh", type=int, default=64)
    ap.add_argument("--n2", type=int, default=5)
    ap.add_argument("--out")
    a = ap.parse_args()
    n = shell_modes(a.n2)
    h = 2 * np.pi / a.nmesh
    th = n * h
    q = q_symbol(th) / h                               # (modes, 3)
    alpha = mode_alpha(SEED, 0, 0, n)
    res = dict(nmesh=a.nmesh, n2=a.n2, modes=int(n.shape[0]), vectors=n.tolist())
    for name, p in (("stencil", q), ("continuum", n.astype(float))):
        pp = (p * p).sum(axis=1)
        qp = (q * p).sum(axis=1)
        # per mode (I_n = alpha_n): D_j dA_ij and (2/3) D_i dK, without eps1 dt
        da = 1j * (q / 3.0 - p * (qp / pp)[:, None])            # i q_j (delta_ij/3 - p_i p_j/p^2)
        dk = 1j * (2.0 / 3.0) * q                               # -(2/3) i q_i (-1)
        resid = da + dk                                         # M_i per unit I_n
        per_mode = np.linalg.norm(resid, axis=1) / np.linalg.norm(q, axis=1)
        m_f = field(a.nmesh, n, resid * alpha[:, None])
        da_f = field(a.nmesh, n, da * alpha[:, None])
        dk_f = field(a.nmesh, n, dk * alpha[:, None])
        mag = np.sqrt(((np.abs(da_f) + np.abs(dk_f))**2).sum(axis=-1))
        ratio = float(np.sqrt(np.mean((m_f**2).sum(axis=-1))) / mag.mean())
        res[name] = dict(per_mode_rel_residual_max=float(per_mode.max()),
                         rms_M_over_mean_magnitude=ratio)
    mism = np.abs(q * q * h * h - k2_symbol(th)) / np.maximum(k2_symbol(th), 1e-300)
    res["second_vs_first_squared_rel_mismatch_max"] = float(mism[n != 0].max())
    print(json.dumps(res, indent=1))
    if a.out:
        with open(a.out, "w") as fp:
            json.dump(res, fp, indent=1)


if __name__ == "__main__":
    main()
