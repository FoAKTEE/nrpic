"""Low-discrepancy quasi-Monte Carlo (Sobol), antipodal, octant-symmetric, and
Lebedev/icosahedral spherical-shell particle samplers for GR-Vlasov and NRPIC.

These samplers eliminate O(N^{-1/2}) Monte Carlo shot noise in initial density
and momentum-stress moments:
- `qmc_antipodal` / `qmc`: Scrambled Sobol sequence paired with 6D phase-space
  antipodes (-x, -u), giving exact zero COM and dipole moments (< 1e-15).
- `qmc_lebedev`: Scrambled Sobol + antipodal spatial nodes with Halton-SO(3)
  rotated S^2 cubature shells (Q in {6, 12, 14, 26}) matching the C++
  `SphericalCubatureRule`, yielding exact local stress-tensor isotropy and zero
  local dipole at each spatial site.
- `qmc_octant`: Scrambled Sobol in the positive octant reflected across all 8
  sign combinations (+-x, +-y, +-z) for cold spheres (OS) and spheroids (Prolate),
  giving exact COM = 0 and diagonal quadrupole moments.
"""

import math
import warnings

import numpy as np
from scipy.stats import qmc

from . import oppenheimer_snyder as osn
from .spheroid import ProlateSpheroid
from .st_cluster import STModel

__all__ = [
    "sobol_uniforms",
    "lebedev_unit_vectors",
    "halton_so3",
    "sample_qmc_unit_vectors",
    "sample_qmc_os",
    "sample_qmc_st",
    "sample_qmc_gaussian_positions",
    "sample_qmc_spheroid",
]


def _seed_int(seed):
    if isinstance(seed, np.random.Generator):
        return int(seed.integers(0, 2**31 - 1))
    return int(seed) if seed is not None else 0


def sobol_uniforms(n, d, seed=0, scramble=True):
    """Draw n points in (0, 1)^d from a scrambled digital Sobol sequence.

    Clips away from exact 0/1 boundaries for safe inverse-CDF evaluation.
    """
    if n <= 0:
        return np.empty((0, d), dtype=float)
    eng = qmc.Sobol(d=d, scramble=scramble, seed=_seed_int(seed))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        u = eng.random(n)
    return np.clip(u, 1e-12, 1.0 - 1e-12)


def _stratify_col0(u):
    """Map column 0 to exact cell midpoints (rank + 0.5)/n for arbitrary non-2^k n."""
    if len(u) == 0:
        return u
    out = u.copy()
    rank = np.argsort(np.argsort(u[:, 0]))
    out[:, 0] = (rank + 0.5) / float(len(u))
    return out


def _unit_vectors_from_u(u_cos, u_phi):
    ct = 2.0 * np.asarray(u_cos, dtype=float) - 1.0
    st = np.sqrt(np.clip(1.0 - ct * ct, 0.0, None))
    ph = 2.0 * math.pi * np.asarray(u_phi, dtype=float)
    return np.stack([st * np.cos(ph), st * np.sin(ph), ct], axis=-1)


def lebedev_unit_vectors(q=14):
    """Normalized unit directions dir[q, 3] and weights w[q] (sum w = 1) on S^2.

    Matches `nrpic::vlasov::SphericalCubatureRule` in `vlasov_math.hpp` for
    q in {6, 12, 14, 26}:
      - 6 : octahedron (exact through l = 3)
      - 12: regular icosahedron (equal weights, exact through l = 5)
      - 14: Lebedev-Laikov 14-point O_h rule (exact through l = 5)
      - 26: Lebedev-Laikov 26-point O_h rule (exact through l = 7)
    """
    q = int(q)
    if q == 6:
        dirs = []
        for d in range(3):
            for s in (-1.0, 1.0):
                v = [0.0, 0.0, 0.0]
                v[d] = s
                dirs.append(v)
        return np.array(dirs, dtype=float), np.full(6, 1.0 / 6.0)
    if q == 12:
        phi = 0.5 * (1.0 + math.sqrt(5.0))
        inv = 1.0 / math.sqrt(1.0 + phi * phi)
        a, b = inv, phi * inv
        dirs = []
        for s1 in (-1.0, 1.0):
            for s2 in (-1.0, 1.0):
                dirs.append([0.0, s1 * a, s2 * b])
                dirs.append([s2 * b, 0.0, s1 * a])
                dirs.append([s1 * a, s2 * b, 0.0])
        return np.array(dirs, dtype=float), np.full(12, 1.0 / 12.0)
    if q == 14:
        s3 = 1.0 / math.sqrt(3.0)
        dirs, w = [], []
        for d in range(3):
            for s in (-1.0, 1.0):
                v = [0.0, 0.0, 0.0]
                v[d] = s
                dirs.append(v)
                w.append(1.0 / 15.0)
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                for sz in (-1.0, 1.0):
                    dirs.append([sx * s3, sy * s3, sz * s3])
                    w.append(3.0 / 40.0)
        return np.array(dirs, dtype=float), np.array(w, dtype=float)
    if q == 26:
        s2 = 1.0 / math.sqrt(2.0)
        s3 = 1.0 / math.sqrt(3.0)
        dirs, w = [], []
        for d in range(3):
            for s in (-1.0, 1.0):
                v = [0.0, 0.0, 0.0]
                v[d] = s
                dirs.append(v)
                w.append(1.0 / 21.0)
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                dirs.append([sx * s2, sy * s2, 0.0]); w.append(4.0 / 105.0)
                dirs.append([sx * s2, 0.0, sy * s2]); w.append(4.0 / 105.0)
                dirs.append([0.0, sx * s2, sy * s2]); w.append(4.0 / 105.0)
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                for sz in (-1.0, 1.0):
                    dirs.append([sx * s3, sy * s3, sz * s3])
                    w.append(9.0 / 280.0)
        return np.array(dirs, dtype=float), np.array(w, dtype=float)
    raise ValueError(f"unsupported lebedev_q={q}; expected 6, 12, 14, or 26")


def _halton_base(index, base):
    f, r, i = 1.0, 0.0, int(index)
    while i > 0:
        f /= base
        r += f * (i % base)
        i //= base
    return r


def halton_so3(idx):
    """Shoemake uniform SO(3) rotation matrix driven by base-(2, 3, 5) Halton sequence."""
    u1 = _halton_base(idx + 1, 2)
    u2 = _halton_base(idx + 1, 3)
    u3 = _halton_base(idx + 1, 5)
    s1 = math.sqrt(max(1.0 - u1, 0.0))
    s2 = math.sqrt(max(u1, 0.0))
    a1 = 2.0 * math.pi * u2
    a2 = 2.0 * math.pi * u3
    qx, qy, qz, qw = s1 * math.sin(a1), s1 * math.cos(a1), s2 * math.sin(a2), s2 * math.cos(a2)
    xx, yy, zz = qx * qx, qy * qy, qz * qz
    xy, xz, xw = qx * qy, qx * qz, qx * qw
    yz, yw, zw = qy * qz, qy * qw, qz * qw
    return np.array([
        [1.0 - 2.0 * (yy + zz), 2.0 * (xy - zw),       2.0 * (xz + yw)],
        [2.0 * (xy + zw),       1.0 - 2.0 * (xx + zz), 2.0 * (yz - xw)],
        [2.0 * (xz - yw),       2.0 * (yz + xw),       1.0 - 2.0 * (xx + yy)],
    ], dtype=float)


def sample_qmc_unit_vectors(n, seed=0, antipodal=True):
    """Draw n QMC unit vectors on S^2, optionally antipodally paired for zero dipole."""
    if n <= 0:
        return np.empty((0, 3), dtype=float)
    if antipodal and n >= 2:
        half = (n + 1) // 2
        u = sobol_uniforms(half, 2, seed=seed)
        v = _unit_vectors_from_u(u[:, 0], u[:, 1])
        return np.concatenate([v, -v[: n - half]], axis=0)
    u = sobol_uniforms(n, 2, seed=seed)
    return _unit_vectors_from_u(u[:, 0], u[:, 1])


def _octant_reflect(x_pos):
    """Reflect positive-octant coordinates across all 8 sign choices (+-x, +-y, +-z)."""
    signs = np.array(
        [[sx, sy, sz] for sx in (1.0, -1.0) for sy in (1.0, -1.0) for sz in (1.0, -1.0)],
        dtype=float,
    )
    return (x_pos[:, None, :] * signs[None, :, :]).reshape(-1, 3)


def _oh_cyclic_octant_reflect(x_pos):
    """Reflect positive-octant points across 8 octants x 3 cyclic axis permutations (24x).

    Guarantees zero COM, zero off-diagonal quadrupole, and exact Q_xx == Q_yy == Q_zz.
    """
    c0 = x_pos
    c1 = x_pos[:, [1, 2, 0]]
    c2 = x_pos[:, [2, 0, 1]]
    return _octant_reflect(np.concatenate([c0, c1, c2], axis=0))


def _xy_octant_reflect(x_pos):
    """Reflect positive-octant points across x<->y swap and all 8 octants (16x).

    Preserves spheroidal z-axisymmetry while enforcing exact COM=0, Q_xy=Q_xz=Q_yz=0,
    and Q_xx == Q_yy.
    """
    return _octant_reflect(np.concatenate([x_pos, x_pos[:, [1, 0, 2]]], axis=0))


def sample_qmc_os(N=None, mode="qmc_octant", seed=0, R0=5.0, M=1.0, species=0):
    """QMC Oppenheimer-Snyder cold dust sphere samplers ('qmc_octant', 'qmc_antipodal')."""
    if N is None:
        raise ValueError("N is required for QMC OS sampling")
    Mrest = osn.rest_mass(R0, M)
    if mode in ("qmc", "qmc_antipodal"):
        half = (N + 1) // 2
        u = _stratify_col0(sobol_uniforms(half, 3, seed=seed))
        r = osn.Finv(u[:, 0], R0, M)
        v = _unit_vectors_from_u(u[:, 1], u[:, 2])
        x_base = r[:, None] * v
        x = np.concatenate([x_base, -x_base[: N - half]], axis=0)
    elif mode == "qmc_octant":
        n_base24 = N // 24
        if n_base24 > 0:
            u = _stratify_col0(sobol_uniforms(n_base24, 3, seed=seed))
            r = osn.Finv(u[:, 0], R0, M)
            ct = u[:, 1]
            st = np.sqrt(np.clip(1.0 - ct * ct, 0.0, None))
            ph = 0.5 * math.pi * u[:, 2]
            xp = r[:, None] * np.stack([st * np.cos(ph), st * np.sin(ph), ct], axis=-1)
            x = _oh_cyclic_octant_reflect(xp)
        else:
            n_base = N // 8
            u = _stratify_col0(sobol_uniforms(n_base, 3, seed=seed))
            r = osn.Finv(u[:, 0], R0, M)
            ct = u[:, 1]
            st = np.sqrt(np.clip(1.0 - ct * ct, 0.0, None))
            ph = 0.5 * math.pi * u[:, 2]
            xp = r[:, None] * np.stack([st * np.cos(ph), st * np.sin(ph), ct], axis=-1)
            x = _octant_reflect(xp)
        rem = N - len(x)
        if rem >= 8:
            xr, _, _, _ = sample_qmc_os(rem - rem % 8, mode="qmc_octant",
                                        seed=_seed_int(seed) + 733, R0=R0, M=M)
            # Small 8-fold tail without 24-fold permutation only if N % 24 >= 8
            x = np.concatenate([x, xr], axis=0)
            rem = N - len(x)
        if rem > 0:
            x_rem, _, _, _ = sample_qmc_os(rem, mode="qmc_antipodal",
                                           seed=_seed_int(seed) + 997, R0=R0, M=M)
            x = np.concatenate([x, x_rem], axis=0)
    else:
        raise ValueError(f"unknown QMC OS mode {mode!r}")
    return (x, np.zeros((N, 3), dtype=float), np.full(N, Mrest / N, dtype=float),
            np.full(N, species, dtype=np.int32))


def sample_qmc_st(model, N, seed=0, mode="qmc_lebedev", lebedev_q=14,
                  vpert=0.0, vpert_profile="uniform", dpert=0.0, species=0):
    """QMC Shapiro-Teukolsky monoenergetic cluster sampler.

    mode = 'qmc_antipodal' (or 'qmc'):
        Pairs N//2 5D Sobol phase-space samples with their exact (-x, -u) antipodes.
    mode = 'qmc_lebedev':
        Places a Halton-SO(3) rotated S^2 cubature shell of q points at each spatial
        node (with antipodal spatial pairing for even site counts), guaranteeing exact
        local zero dipole and exact local velocity stress-tensor isotropy. Any remainder
        particles mod q use 'qmc_antipodal' with seed+997.
    """
    if not isinstance(model, STModel):
        model = STModel(float(model))
    base_seed = _seed_int(seed)

    def _apply_pert(rb_arr, nhat_arr, q_arr):
        if vpert:
            if vpert_profile == "uniform":
                p = np.ones_like(rb_arr)
            elif vpert_profile == "linear":
                p = rb_arr / model.rbar_s
            else:
                raise ValueError(f"unknown vpert_profile {vpert_profile!r}")
            q_arr = q_arr - (vpert * p * model.q(rb_arr))[:, None] * nhat_arr
        if dpert:
            rb_arr = rb_arr * (1.0 + dpert) ** (-1.0 / 3.0)
        return rb_arr, q_arr

    if mode in ("qmc", "qmc_antipodal"):
        # 4-tuple phase-space pairing (x, u), (-x, -u), (x, -u), (-x, u) zeroes COM, P, and J
        n_quad = N // 4
        rem = N - 4 * n_quad
        u = sobol_uniforms(n_quad + rem, 5, seed=base_seed)
        u[:n_quad] = _stratify_col0(u[:n_quad])
        rb_b = model.Finv(u[:n_quad, 0])
        nh_b = _unit_vectors_from_u(u[:n_quad, 1], u[:n_quad, 2])
        q_b = model.q(rb_b)[:, None] * _unit_vectors_from_u(u[:n_quad, 3], u[:n_quad, 4])
        rb = np.concatenate([rb_b, rb_b, rb_b, rb_b], axis=0)
        nh = np.concatenate([nh_b, -nh_b, nh_b, -nh_b], axis=0)
        q = np.concatenate([q_b, -q_b, -q_b, q_b], axis=0)
        if rem >= 2:
            rb_p = model.Finv(u[n_quad:n_quad + 1, 0])
            nh_p = _unit_vectors_from_u(u[n_quad:n_quad + 1, 1], u[n_quad:n_quad + 1, 2])
            q_p = model.q(rb_p)[:, None] * _unit_vectors_from_u(u[n_quad:n_quad + 1, 3], u[n_quad:n_quad + 1, 4])
            rb = np.concatenate([rb, rb_p, rb_p], axis=0)
            nh = np.concatenate([nh, nh_p, -nh_p], axis=0)
            q = np.concatenate([q, q_p, -q_p], axis=0)
            rem -= 2
            off = n_quad + 1
        else:
            off = n_quad
        if rem > 0:
            rb_r = model.Finv(u[off:off + rem, 0])
            nh_r = _unit_vectors_from_u(u[off:off + rem, 1], u[off:off + rem, 2])
            q_r = model.q(rb_r)[:, None] * _unit_vectors_from_u(u[off:off + rem, 3], u[off:off + rem, 4])
            rb = np.concatenate([rb, rb_r], axis=0)
            nh = np.concatenate([nh, nh_r], axis=0)
            q = np.concatenate([q, q_r], axis=0)
        rb, q = _apply_pert(rb, nh, q)
        x = rb[:, None] * nh
        u_cov = model.psi(rb)[:, None] ** 2 * q
        m = np.full(N, model.M0 / N, dtype=float)
        return x, u_cov, m, np.full(N, species, dtype=np.int32)

    if mode == "qmc_lebedev":
        dirs, w_s2 = lebedev_unit_vectors(lebedev_q)
        q_shell = len(dirs)
        n_sites = N // q_shell
        if n_sites == 0:
            return sample_qmc_st(model, N, seed=base_seed, mode="qmc_antipodal",
                                 vpert=vpert, vpert_profile=vpert_profile,
                                 dpert=dpert, species=species)
        rem = N - n_sites * q_shell
        half_s = (n_sites + 1) // 2
        u_pos = _stratify_col0(sobol_uniforms(half_s, 3, seed=base_seed))
        rb_h = model.Finv(u_pos[:, 0])
        nh_h = _unit_vectors_from_u(u_pos[:, 1], u_pos[:, 2])
        n_anti = n_sites - half_s
        rb_sites = np.concatenate([rb_h, rb_h[:n_anti]], axis=0)
        nh_sites = np.concatenate([nh_h, -nh_h[:n_anti]], axis=0)

        rots = np.stack([halton_so3(a) for a in range(n_sites)], axis=0)  # [n_sites, 3, 3]
        shell_dirs = np.einsum("aij,qj->aqi", rots, dirs).reshape(-1, 3)

        rb_main = np.repeat(rb_sites, q_shell)
        nh_main = np.repeat(nh_sites, q_shell, axis=0)
        q_main = model.q(rb_main)[:, None] * shell_dirs
        rb_main, q_main = _apply_pert(rb_main, nh_main, q_main)
        x_main = rb_main[:, None] * nh_main
        u_main = model.psi(rb_main)[:, None] ** 2 * q_main

        m_site = model.M0 * (q_shell / float(N))
        m_main = np.tile(m_site * w_s2, n_sites)
        if rem > 0:
            x_r, u_r, m_r, _ = sample_qmc_st(
                model, rem, seed=base_seed + 997, mode="qmc_antipodal",
                vpert=vpert, vpert_profile=vpert_profile, dpert=dpert, species=species)
            # Re-weight remainder so total rest mass equals model.M0 identically
            m_r = np.full(rem, model.M0 / float(N), dtype=float)
            x = np.concatenate([x_main, x_r], axis=0)
            u_cov = np.concatenate([u_main, u_r], axis=0)
            m = np.concatenate([m_main, m_r], axis=0)
        else:
            x, u_cov, m = x_main, u_main, m_main
        return x, u_cov, m, np.full(N, species, dtype=np.int32)

    raise ValueError(f"unknown QMC ST mode {mode!r}")


def sample_qmc_gaussian_positions(N, sigma, centre=(0.0, 0.0, 0.0), seed=0, octant_sym=True):
    """Draw N 3D isotropic Gaussian positions via scrambled Sobol with octant reflection."""
    from scipy.stats import chi as _chi

    if octant_sym and N >= 8:
        n_base = N // 8
        u = _stratify_col0(sobol_uniforms(n_base, 3, seed=seed))
        r = sigma * _chi.ppf(u[:, 0], 3)
        ct = u[:, 1]
        st = np.sqrt(np.clip(1.0 - ct * ct, 0.0, None))
        ph = 0.5 * math.pi * u[:, 2]
        xp = r[:, None] * np.stack([st * np.cos(ph), st * np.sin(ph), ct], axis=-1)
        dx = _octant_reflect(xp)
        rem = N - len(dx)
        if rem > 0:
            half = (rem + 1) // 2
            ur = sobol_uniforms(half, 3, seed=_seed_int(seed) + 997)
            rr = sigma * _chi.ppf(ur[:, 0], 3)
            vr = _unit_vectors_from_u(ur[:, 1], ur[:, 2])
            dr = np.concatenate([rr[:, None] * vr, -(rr[:, None] * vr)[: rem - half]], axis=0)
            dx = np.concatenate([dx, dr], axis=0)
    else:
        half = (N + 1) // 2
        u = sobol_uniforms(half, 3, seed=seed)
        r = sigma * _chi.ppf(u[:, 0], 3)
        v = _unit_vectors_from_u(u[:, 1], u[:, 2])
        d_half = r[:, None] * v
        dx = np.concatenate([d_half, -d_half[: N - half]], axis=0)
    return np.asarray(centre, dtype=float) + dx


def sample_qmc_spheroid(N, e=0.9, b=10.0, M=1.0, seed=0, octant_sym=True,
                        species=0, spheroid=None):
    """Octant-symmetric QMC sampler for a homogeneous prolate spheroid.

    Draws base samples in the positive octant via Sobol accept-reject against
    psibar/c0 inside the unit ball mapped to (a, a, b), and reflects across
    x<->y swap + all 8 octants (when octant_sym=True and N % 16 == 0) or all 8
    octants (when N % 8 == 0), guaranteeing exact COM=0, Q_xy=Q_xz=Q_yz=0, and
    (for 16-fold) exact Q_xx == Q_yy.
    """
    sph = spheroid if spheroid is not None else ProlateSpheroid(e, b, M)
    base_seed = _seed_int(seed)
    sym_mult = (16 if (octant_sym and N >= 16 and N % 16 == 0)
                else (8 if (octant_sym and N >= 8 and N % 8 == 0)
                      else (4 if N % 4 == 0 else 1)))
    n_base = N // sym_mult
    pmax = sph.c0
    eng = qmc.Sobol(d=4, scramble=True, seed=base_seed)
    acc_pts = []
    tot = 0
    while tot < n_base:
        u = eng.random(max(2048, n_base * 4))
        rad = np.cbrt(u[:, 0])
        if sym_mult >= 8:
            ct = u[:, 1]
            ph = 0.5 * math.pi * u[:, 2]
        elif sym_mult == 4:
            ct = u[:, 1]
            ph = math.pi * u[:, 2]
        else:
            ct = 2.0 * u[:, 1] - 1.0
            ph = 2.0 * math.pi * u[:, 2]
        st = np.sqrt(np.clip(1.0 - ct * ct, 0.0, None))
        px = sph.a * rad * st * np.cos(ph)
        py = sph.a * rad * st * np.sin(ph)
        pz = sph.b * rad * ct
        p = np.stack([px, py, pz], axis=-1)
        keep = u[:, 3] < (sph.psibar(px, py, pz) / pmax)
        p_keep = p[keep]
        if len(p_keep):
            acc_pts.append(p_keep)
            tot += len(p_keep)
    base = np.concatenate(acc_pts, axis=0)[:n_base]
    if sym_mult == 16:
        x = _xy_octant_reflect(base)
    elif sym_mult == 8:
        x = _octant_reflect(base)
    elif sym_mult == 4:
        x = np.concatenate([
            base,
            base * np.array([1.0, 1.0, -1.0]),
            base * np.array([-1.0, -1.0, 1.0]),
            -base,
        ])
    else:
        x = base
    return (x, np.zeros((N, 3), dtype=float), np.full(N, sph.rest_mass() / N, dtype=float),
            np.full(N, species, dtype=np.int32))
