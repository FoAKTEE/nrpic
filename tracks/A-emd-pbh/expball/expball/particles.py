"""Particle samples of the dust ball: dust at rest with respect to the normal observers of
the slice, u_i = 0, positions in the isotropic Cartesian coordinates of the code.

The rest mass in a coordinate volume is rho psi^6 d^3x (rho the rest-mass density, equal to
the energy density E for u_i = 0), so the code's deposit E = sum m W S/(psi^6 dV)
reproduces rho (docs/FORMATS.md; python/nrpic/sampling.py, module docstring).

    'stratified'  N equal masses M0/N; randomized stratification U_ad = (pi_d(a) + xi_ad)/N in
                  the rest-mass fraction (inverse radial CDF), cos(theta) and phi
                  (nrpic.sampling.stratified_uniforms, reused by path import)
    'mc'          the same maps with independent uniforms
    'lattice'     centres of the n_lat^3 cells tiling [-rbar_m, rbar_m]^3, kept inside the
                  matter, m_p = rho psi^6 h^3; with surface_correction the outermost layer
                  (one spacing) is rescaled so that the total equals the continuum rest mass
"""

import math
import os
import sys

import numpy as np

_REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "..", ".."))
if os.path.join(_REPO, "python") not in sys.path:
    sys.path.insert(0, os.path.join(_REPO, "python"))
from nrpic import io as nio  # noqa: E402
from nrpic.sampling import stratified_uniforms, unit_vectors  # noqa: E402

__all__ = ["sample", "lattice", "radius_of_mass_fraction", "write_nrp", "nlat_for"]

write_nrp = nio.write_nrp


def radius_of_mass_fraction(ball, U):
    """Isotropic radius enclosing the rest-mass fraction U (vectorized bisection to the
    last bit of the bracket [0, rbar_m])."""
    U = np.asarray(U, dtype=float)
    target = U * ball.rest_mass()
    lo = np.zeros_like(U)
    hi = np.full_like(U, ball.matter_rbar())
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        f = ball.rest_mass_inside(mid) - target
        lo = np.where(f < 0, mid, lo)
        hi = np.where(f >= 0, mid, hi)
    return 0.5 * (lo + hi)


def sample(ball, N, method="stratified", seed=1, species=0):
    """N equal-mass particles at rest: (x[N,3], u[N,3], m[N], species[N])."""
    rng = np.random.default_rng(seed)
    if method == "stratified":
        U = stratified_uniforms(N, 3, rng)
    elif method == "mc":
        U = rng.random((N, 3))
    else:
        raise ValueError(f"unknown sampler {method!r}")
    rb = radius_of_mass_fraction(ball, U[:, 0])
    x = rb[:, None] * unit_vectors(U[:, 1], U[:, 2])
    M0 = ball.rest_mass()
    return x, np.zeros((N, 3)), np.full(N, M0 / N), np.full(N, species, dtype=np.int32)


def _lattice_count(n_lat):
    k = 2 * np.arange(n_lat, dtype=np.int64) + 1 - n_lat
    k2 = np.sort(k * k)
    rem = n_lat * n_lat - (k2[:, None] + k2[None, :])
    return int(np.sum(np.searchsorted(k2, rem, side="right")[rem >= 0]))


def nlat_for(N):
    n0 = max(2, int(round((6.0 * N / math.pi) ** (1.0 / 3.0))))
    return min(range(max(2, n0 - 3), n0 + 4), key=lambda n: (abs(_lattice_count(n) - N), n))


def lattice(ball, n_lat, surface_correction=True, species=0):
    """Mass-weighted cubic lattice inside the matter (rbar <= rbar_m)."""
    rm = ball.matter_rbar()
    h = 2.0 * rm / n_lat
    k = 2 * np.arange(n_lat, dtype=np.int64) + 1 - n_lat
    I, J, K = np.meshgrid(k, k, k, indexing="ij")
    keep = I * I + J * J + K * K <= n_lat * n_lat
    x = 0.5 * h * np.stack([I[keep], J[keep], K[keep]], axis=-1).astype(float)
    r = np.sqrt(np.sum(x * x, axis=1))
    f = ball.fields(r, ("rho", "u"))
    m = f["rho"] * (1.0 + f["u"]) ** 6 * h ** 3
    pos = m > 0
    x, r, m = x[pos], r[pos], m[pos]
    if surface_correction:
        layer = r > rm - h
        M0 = ball.rest_mass()
        m = m.copy()
        m[layer] *= (M0 - m[~layer].sum()) / m[layer].sum()
    n = len(m)
    return x, np.zeros((n, 3)), m, np.full(n, species, dtype=np.int32)
