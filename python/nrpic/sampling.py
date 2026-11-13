"""Particle samplers for the self-gravitating initial data.

Every sampler returns (x[N,3], u[N,3], m[N], species[N]) with x the isotropic
Cartesian position, u the covariant spatial four-velocity u_i, m the rest mass
and species an int32 id. For a conformally flat slice gamma_ij = psi^4 delta_ij
and an orthonormal-frame velocity q (|q|^2 = W^2 - 1), u_i = psi^2 q_i.

Equal-mass samplers draw coordinate positions with density proportional to
rho_0 psi^6 (rho_0 the rest-mass density seen by the normal observers), so
that the deposited E = sum m W delta/psi^6 reproduces the continuum energy
density.

Oppenheimer-Snyder (paper lines 905-917, App. A):
    'mc'          trial points uniform in the coordinate ball, accepted with
                  probability psi^6(r)/psi^6(0); m_p = M_rest/N.
    'lattice'     centres of the n_lat^3 cells that tile the cube
                  [-rbar_0, rbar_0]^3 (spacing h = 2 rbar_0/n_lat, centres at
                  -rbar_0 + (i + 1/2) h, so no particle sits at the origin for even
                  n_lat), kept when |x| <= rbar_0, with m_p = rho_0 psi^6(x_p) h^3.
                  n_lat = 124 gives N = 998,592.
    'stratified'  randomized stratification (as for the cluster) in rbar,
                  cos(theta), phi.
Monoenergetic cluster (paper lines 1119-1128):
    'stratified'  U_ad = (pi_d(a) + xi_ad)/N, d = rbar, cos(theta), phi,
                  cos(vartheta), varphi, independent permutations pi_d.
    'mc'          the same maps with independent uniforms (equivalent in
                  distribution to accept-reject with acceptance prop. to rho_0 psi^6).
Prolate spheroid (paper line 967): accept-reject from the uniform spheroid with
acceptance psibar/psibar(0); N/4 base points are completed by the images under
z -> -z and the pi rotation about z, (x, y) -> (-x, -y).
Isotropic Gaussian (clumps of the Jeans problem, see clumps.py): positions only,
    'stratified'  U_ad as for the cluster, d = r, cos(theta), phi, with
                  r = sigma chi_3^(-1)(U) the inverse radial CDF of the 3D Gaussian.
    'mc'          the same maps with independent uniforms.
"""

import math

import numpy as np
from scipy.stats import chi as _chi

from . import oppenheimer_snyder as osn
from .spheroid import ProlateSpheroid
from .st_cluster import STModel

__all__ = [
    "stratified_uniforms", "unit_vectors", "sample_os", "os_lattice",
    "os_lattice_count", "os_nlat_for", "sample_st", "sample_spheroid",
    "gaussian_radius_cdf", "gaussian_radius_inv", "sample_gaussian_positions",
]


def _rng(seed):
    return seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)


def stratified_uniforms(N, d, rng):
    """N x d array U_ad = (pi_d(a) + xi_ad)/N: exactly one sample in each of the
    N equal-probability strata of every column, with independent random
    permutations pi_d and offsets xi_ad ~ U[0,1)."""
    rng = _rng(rng)
    U = np.empty((N, d))
    for k in range(d):
        U[:, k] = (rng.permutation(N) + rng.random(N)) / N
    return U


def unit_vectors(u_cos, u_phi):
    """Unit vectors with cos(theta) = 2 u_cos - 1 and phi = 2 pi u_phi."""
    ct = 2.0 * np.asarray(u_cos) - 1.0
    st = np.sqrt(np.clip(1.0 - ct * ct, 0.0, None))
    ph = 2.0 * math.pi * np.asarray(u_phi)
    return np.stack([st * np.cos(ph), st * np.sin(ph), ct], axis=-1)


def _species(N, species):
    return np.full(N, species, dtype=np.int32)


# ----------------------------------------------------------------------------
# Oppenheimer-Snyder
# ----------------------------------------------------------------------------
def _lattice_ints(n_lat):
    """Cell-centre coordinates in units of h/2 (integers 2i + 1 - n_lat)."""
    return 2 * np.arange(n_lat, dtype=np.int64) + 1 - n_lat


def os_lattice_count(n_lat):
    """Number of cell centres of the n_lat-cell lattice with |x| <= rbar_0."""
    k = _lattice_ints(n_lat)
    k2 = k * k
    lim = n_lat * n_lat
    rem = lim - (k2[:, None] + k2[None, :])          # remaining budget for k_z^2
    return int(np.sum(np.searchsorted(np.sort(k2), rem, side="right")[rem >= 0]))


def os_nlat_for(N):
    """n_lat whose OS lattice count is closest to N (N ~ (pi/6) n_lat^3)."""
    n0 = max(2, int(round((6.0 * N / math.pi) ** (1.0 / 3.0))))
    cands = range(max(2, n0 - 3), n0 + 4)
    return min(cands, key=lambda n: (abs(os_lattice_count(n) - N), n))


def os_lattice(n_lat, R0=5.0, M=1.0):
    """Mass-weighted lattice: (x[N,3], m[N]) with m_p = rho_0 psi^6(x_p) h^3."""
    rb0 = osn.isotropic_radius(R0, M)
    h = 2.0 * rb0 / n_lat
    k = _lattice_ints(n_lat)
    I, J, K = np.meshgrid(k, k, k, indexing="ij")
    keep = I * I + J * J + K * K <= n_lat * n_lat         # exact integer test
    x = 0.5 * h * np.stack([I[keep], J[keep], K[keep]], axis=-1).astype(float)
    r = np.sqrt(np.sum(x * x, axis=1))
    m = osn.rho0(R0, M) * osn.psi(r, R0, M) ** 6 * h ** 3
    return x, m


def sample_os(N=None, method="mc", seed=0, R0=5.0, M=1.0, n_lat=None,
              species=0, normalize_lattice_mass=False, surface_correction=False):
    """Oppenheimer-Snyder dust at rest, u_i = 0.

    method 'mc' or 'stratified': N equal-mass particles, m_p = M_rest/N.
    method 'lattice': give n_lat, or N to pick the n_lat whose count is
    closest to N (`os_nlat_for`). The returned count is then fixed by n_lat.
    With normalize_lattice_mass the lattice masses are rescaled so that their
    sum equals the continuum M_rest exactly (off by default, as in the paper).
    """
    rb0 = osn.isotropic_radius(R0, M)
    Mrest = osn.rest_mass(R0, M)
    if method == "lattice":
        if n_lat is None:
            if N is None:
                raise ValueError("lattice sampler needs n_lat or N")
            n_lat = os_nlat_for(N)
        x, m = os_lattice(n_lat, R0, M)
        if normalize_lattice_mass and surface_correction:
            raise ValueError("choose one of normalize_lattice_mass, surface_correction")
        if normalize_lattice_mass:
            m = m * (Mrest / m.sum())
        if surface_correction:
            # The number of lattice sites inside a sphere differs from its volume in
            # cells by a fraction of order 1/n_lat (+1.2 percent at n_lat = 26), and
            # the rule m = rho_0 psi^6 h^3 inherits that as an error of the total rest
            # mass.  Put the whole correction into the outermost layer of one lattice
            # spacing, where the cells are cut by the surface: the interior keeps the
            # exact density and the total equals the continuum rest mass.
            rbar0 = osn.isotropic_radius(R0, M)
            h = 2.0 * rbar0 / n_lat
            r = np.sqrt(np.sum(x * x, axis=1))
            layer = r > rbar0 - h
            m = m.copy()
            m[layer] *= (Mrest - m[~layer].sum()) / m[layer].sum()
        n = len(m)
        return x, np.zeros((n, 3)), m, _species(n, species)
    if N is None:
        raise ValueError("N is required")
    rng = _rng(seed)
    if method == "mc":
        psi6_0 = float(osn.psi(0.0, R0, M)) ** 6
        out = np.empty((0, 3))
        while len(out) < N:
            nb = max(1024, int(1.3 * (N - len(out)) / 0.45))
            p = rng.uniform(-rb0, rb0, size=(nb, 3))
            r = np.sqrt(np.sum(p * p, axis=1))
            p = p[r <= rb0]
            r = r[r <= rb0]
            acc = rng.random(len(r)) < osn.psi(r, R0, M) ** 6 / psi6_0
            out = np.concatenate([out, p[acc]])
        x = out[:N]
    elif method == "stratified":
        U = stratified_uniforms(N, 3, rng)
        x = osn.Finv(U[:, 0], R0, M)[:, None] * unit_vectors(U[:, 1], U[:, 2])
    else:
        raise ValueError(f"unknown OS sampler {method!r}")
    return x, np.zeros((N, 3)), np.full(N, Mrest / N), _species(N, species)


# ----------------------------------------------------------------------------
# monoenergetic cluster
# ----------------------------------------------------------------------------
def sample_st(model, N, method="stratified", seed=0, vpert=0.0,
              vpert_profile="uniform", dpert=0.0, species=0):
    """Monoenergetic Shapiro-Teukolsky cluster with N equal-mass particles.

    model          STModel, or y_c (a float) to build one with M = 1.
    method         'stratified' (paper lines 1119-1128) or 'mc'.
    vpert          coherent inward radial velocity perturbation: the orthonormal
                   velocity becomes q - vpert * p(r) * |q_eq(r)| * rhat, i.e. a
                   radial three-velocity shift of -vpert * p(r) times the local
                   equilibrium speed to first order; p = 1 ('uniform') or
                   p = rbar/rbar_s ('linear').
    dpert          density perturbation by homologous compression of the
                   positions, x -> x (1 + dpert)^(-1/3), which raises the
                   coordinate number density by the factor (1 + dpert). The
                   velocities keep their equilibrium orthonormal values from the
                   unperturbed radius and are lowered with psi at the new position.
    Masses are M0/N. The particles are not altered to satisfy the constraints;
    st_cluster.PerturbedST gives the conformal factor (and lapse) that
    solves the Hamiltonian constraint for exactly this perturbed matter.
    """
    if not isinstance(model, STModel):
        model = STModel(float(model))
    rng = _rng(seed)
    if method == "stratified":
        U = stratified_uniforms(N, 5, rng)
    elif method == "mc":
        U = rng.random((N, 5))
    else:
        raise ValueError(f"unknown cluster sampler {method!r}")
    rb = model.Finv(U[:, 0])
    nhat = unit_vectors(U[:, 1], U[:, 2])
    qmag = model.q(rb)
    q = qmag[:, None] * unit_vectors(U[:, 3], U[:, 4])
    if vpert:
        if vpert_profile == "uniform":
            p = np.ones_like(rb)
        elif vpert_profile == "linear":
            p = rb / model.rbar_s
        else:
            raise ValueError(f"unknown vpert_profile {vpert_profile!r}")
        q = q - (vpert * p * qmag)[:, None] * nhat
    if dpert:
        rb = rb * (1.0 + dpert) ** (-1.0 / 3.0)
    x = rb[:, None] * nhat
    u = model.psi(rb)[:, None] ** 2 * q
    return x, u, np.full(N, model.M0 / N), _species(N, species)


# ----------------------------------------------------------------------------
# isotropic Gaussian (positions only)
# ----------------------------------------------------------------------------
def gaussian_radius_cdf(r, sigma):
    """Fraction of an isotropic 3D Gaussian of width sigma inside radius r:
    erf(t/sqrt 2) - (2/pi)^(1/2) t exp(-t^2/2), t = r/sigma."""
    return _chi.cdf(np.asarray(r, dtype=float) / sigma, 3)


def gaussian_radius_inv(U, sigma):
    """Inverse of gaussian_radius_cdf: r = sigma chi_3^(-1)(U)."""
    return sigma * _chi.ppf(np.asarray(U, dtype=float), 3)


def sample_gaussian_positions(N, sigma, centre=(0.0, 0.0, 0.0), method="stratified",
                              seed=0):
    """N positions x[N,3] of the isotropic Gaussian exp(-|x - centre|^2/(2 sigma^2)),
    with randomized stratification in r, cos(theta) and phi ('stratified', the
    construction of the cluster sampler) or independent uniforms ('mc')."""
    rng = _rng(seed)
    if method == "stratified":
        U = stratified_uniforms(N, 3, rng)
    elif method == "mc":
        U = rng.random((N, 3))
    else:
        raise ValueError(f"unknown Gaussian sampler {method!r}")
    r = gaussian_radius_inv(U[:, 0], sigma)
    return np.asarray(centre, dtype=float) + r[:, None] * unit_vectors(U[:, 1], U[:, 2])


# ----------------------------------------------------------------------------
# prolate spheroid
# ----------------------------------------------------------------------------
def sample_spheroid(N, e=0.9, b=10.0, M=1.0, seed=0, symmetrize=True,
                    species=0, spheroid=None):
    """Cold prolate spheroid at rest with coordinate density proportional to
    psibar inside (x^2+y^2)/a^2 + z^2/b^2 <= 1; m_p = M_rest/N.

    With symmetrize (default) N must be a multiple of 4: N/4 base points are
    drawn and completed by (x, y, -z), (-x, -y, z), (-x, -y, -z), so the set is
    invariant under the equatorial reflection and the pi rotation about z.
    """
    sph = spheroid if spheroid is not None else ProlateSpheroid(e, b, M)
    rng = _rng(seed)
    if symmetrize and N % 4:
        raise ValueError("symmetrized spheroid sampling needs N divisible by 4")
    nb = N // 4 if symmetrize else N
    pmax = sph.c0
    out = np.empty((0, 3))
    while len(out) < nb:
        k = max(1024, int(1.2 * (nb - len(out)) / 0.5))
        p = rng.uniform(-1.0, 1.0, size=(k, 3))
        p = p[np.sum(p * p, axis=1) <= 1.0] * np.array([sph.a, sph.a, sph.b])
        acc = rng.random(len(p)) < sph.psibar(*p.T) / pmax
        out = np.concatenate([out, p[acc]])
    base = out[:nb]
    if symmetrize:
        x = np.concatenate([base,
                            base * np.array([1.0, 1.0, -1.0]),
                            base * np.array([-1.0, -1.0, 1.0]),
                            -base])
    else:
        x = base
    return x, np.zeros((N, 3)), np.full(N, sph.rest_mass() / N), _species(N, species)
