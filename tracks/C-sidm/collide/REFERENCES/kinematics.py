"""Kinematics oracle of the collision kernel (SPEC.md sections 3 and 4).

Everything acts on spatial four-velocities u = p/m in an orthonormal frame (c = 1),
vectorized over leading axes: u has shape (..., 3), masses broadcast.

scatter(ua, ub, ma, mb, nhat)
    Isotropic elastic scattering of one pair in its centre-of-momentum (CM) frame.
    nhat is the direction of particle a's momentum after the collision, expressed in the
    axes of the CM frame reached from the given frame by the pure boost with velocity
    P/E (no rotation). The momentum of b follows from momentum conservation,
    p_b' = P - p_a'; the energies from the mass shells. Exact to rounding: the pair's
    four-momentum is conserved to a few ulps of the pair energy.

gamma_rel_m1(ua, ub)
    gamma_rel - 1 = -u_a.u_b - 1 without cancellation, from
    gamma_rel - 1 = 2 sinh^2(d_eta/2) + |u_a||u_b| (1 - cos psi), with
    sinh(d_eta) = (a - b)(a + b)/(a W_b + b W_a), a = |u_a|, b = |u_b|.

vmol(ua, ub)
    Moller relative speed sqrt(gamma_rel^2 - 1)/(W_a W_b) (0 <= vmol < 2).

The mpmath twins (mp_scatter, mp_vmol) evaluate the textbook formulas (s = E^2 - |P|^2,
boost with beta) at 60 digits; they share no algebra with the double-precision path and
are the reference of tests/test_kinematics.py and of the test vectors for the code.
"""
import json
import numpy as np

try:
    import mpmath as mp
except ImportError:          # the oracle itself does not need mpmath
    mp = None

__all__ = ["W_of", "gamma_rel_m1", "vmol", "scatter", "cholesky_triad", "to_frame",
           "from_frame", "scatter_metric", "nanbu_update", "pair_probability",
           "mp_scatter", "mp_vmol", "make_test_vectors"]


def W_of(u):
    u = np.asarray(u, dtype=float)
    return np.sqrt(1.0 + np.sum(u * u, axis=-1))


def _norm(u):
    return np.sqrt(np.sum(u * u, axis=-1))


def gamma_rel_m1(ua, ub):
    """gamma_rel - 1 between two four-velocities (shape (..., 3)), without cancellation.

    Branch 1, used where r = D_par/A <= 1/2: from D = u_a - u_b and S = u_a + u_b only,
        gamma_rel - 1 = (D_perp + 4 D_par / A) / (2 (1 - D_par / A)),
    e = S/|S|, D_par = (D.e)^2, D_perp = |D x e|^2, A = (W_a + W_b)^2 (exact identity
    from 2(gamma_rel - 1) = |D|^2 - (W_a - W_b)^2 and (W_a + W_b)^2 - |S|^2 = 2(gamma_rel
    + 1); at S = 0 it equals |D|^2/2 for any e).
    Branch 2, where r > 1/2: 2 sinh^2(d_eta/2) + |u_a||u_b| (1 - cos psi), with
    sinh(d_eta) = (a - b)(a + b)/(a W_b + b W_a). r > 1/2 implies |D|^2 > 2 + (a + b)^2/2,
    so either a/b lies outside [0.17, 5.8] (no cancellation in a - b) or the angle term
    ab (1 - cos psi) dominates."""
    ua = np.asarray(ua, dtype=float)
    ub = np.asarray(ub, dtype=float)
    ua, ub = np.broadcast_arrays(ua, ub)
    a, b = _norm(ua), _norm(ub)
    Wa, Wb = np.sqrt(1.0 + a * a), np.sqrt(1.0 + b * b)
    with np.errstate(invalid="ignore", divide="ignore"):
        # branch 1: co-moving
        D = ua - ub
        S = ua + ub
        sn = _norm(S)
        e = S / np.where(sn > 0, sn, 1.0)[..., None]
        dpar = np.sum(D * e, axis=-1)
        Dpar = dpar * dpar
        cr = np.cross(D, e)
        Dperp = np.sum(cr * cr, axis=-1)
        A = (Wa + Wb) ** 2
        r = Dpar / A
        g_co = (Dperp + 4.0 * r) / (2.0 * (1.0 - r))
        g_co = np.where(sn > 0, g_co, 0.5 * np.sum(D * D, axis=-1))
        # branch 2: opposed or orthogonal
        den = a * Wb + b * Wa
        Sh = np.where(den > 0, (a - b) * (a + b) / np.where(den > 0, den, 1.0), 0.0)
        t1 = Sh * Sh / (np.sqrt(1.0 + Sh * Sh) + 1.0)
        ah = np.where(a[..., None] > 0, ua / np.where(a > 0, a, 1.0)[..., None], 0.0)
        bh = np.where(b[..., None] > 0, ub / np.where(b > 0, b, 1.0)[..., None], 0.0)
        d = ah - bh
        g_op = t1 + a * b * 0.5 * np.sum(d * d, axis=-1)
    return np.where(r <= 0.5, g_co, g_op)


def vmol(ua, ub):
    """Moller relative speed of two particles with four-velocities ua, ub."""
    g1 = gamma_rel_m1(ua, ub)
    return np.sqrt(g1 * (g1 + 2.0)) / (W_of(ua) * W_of(ub))


def scatter(ua, ub, ma, mb, nhat):
    """Post-collision four-velocities (ua', ub') for the CM direction nhat of a."""
    ua = np.asarray(ua, dtype=float)
    ub = np.asarray(ub, dtype=float)
    ma = np.asarray(ma, dtype=float)
    mb = np.asarray(mb, dtype=float)
    nhat = np.asarray(nhat, dtype=float)
    g1 = gamma_rel_m1(ua, ub)                      # gamma_rel - 1 >= 0
    Wa, Wb = W_of(ua), W_of(ub)
    pa, pb = ma[..., None] * ua, mb[..., None] * ub
    P = pa + pb
    E = ma * Wa + mb * Wb
    s = (ma + mb) ** 2 + 2.0 * ma * mb * g1        # invariant mass squared
    rs = np.sqrt(s)
    pstar = ma * mb * np.sqrt(g1 * (g1 + 2.0)) / rs    # |p*| in the CM frame
    Ea_star = np.sqrt(ma * ma + pstar * pstar)
    psa = pstar[..., None] * nhat                  # p_a' in the CM frame
    coef = np.sum(psa * P, axis=-1) / (rs * (E + rs)) + Ea_star / rs
    pa_new = psa + coef[..., None] * P
    pb_new = P - pa_new
    return pa_new / ma[..., None], pb_new / mb[..., None]


# ---------------------------------------------------------------------------------------
# curved spacetime: triad of the normal observer at the collision cell

def cholesky_triad(gamma):
    """Lower-triangular L with gamma_ij = (L L^T)_ij, L_ii > 0 (shape (..., 3, 3)).
    Orthonormal-frame components of a covariant spatial vector: u_hat = L^-1 u; back:
    u = L u_hat. Then gamma^ij u_i u_j = |u_hat|^2 exactly in exact arithmetic."""
    return np.linalg.cholesky(np.asarray(gamma, dtype=float))


def to_frame(u_cov, L):
    return np.linalg.solve(L, np.asarray(u_cov, dtype=float)[..., None])[..., 0]


def from_frame(u_hat, L):
    return np.einsum("...ij,...j->...i", L, np.asarray(u_hat, dtype=float))


def scatter_metric(ua_cov, ub_cov, gamma, nhat, ma=1.0, mb=1.0):
    """Scatter two particles given by covariant u_i in a cell with spatial metric gamma
    (one metric for both): map to the triad, scatter, map back."""
    L = cholesky_triad(gamma)
    a = to_frame(ua_cov, L)
    b = to_frame(ub_cov, L)
    a2, b2 = scatter(a, b, ma, mb, nhat)
    return from_frame(a2, L), from_frame(b2, L)


# ---------------------------------------------------------------------------------------
# unequal weights (SPEC.md section 4.3)

def nanbu_update(wa, wb, r):
    """Which members of a colliding pair adopt their post-collision momenta under the
    Nanbu-Yonemura rule: the lighter always, the heavier iff r < w_min / w_max
    (r uniform in (0,1); one draw for the pair)."""
    wa = np.asarray(wa, dtype=float)
    wb = np.asarray(wb, dtype=float)
    wmax = np.maximum(wa, wb)
    return r < wb / wmax, r < wa / wmax


def pair_probability(n_cell, sigma_per_mass, m_max, vm, alpha, dt, sqrt_gamma, dvol):
    """Collision probability of one tested pair (SPEC.md eq. P):
    P = (N - 1) (sigma/m) M_max v_Mol alpha dt / (sqrt(gamma) dV_coord)."""
    return (n_cell - 1) * sigma_per_mass * m_max * vm * alpha * dt / (sqrt_gamma * dvol)


# ---------------------------------------------------------------------------------------
# 60-digit reference (textbook formulas)

def _mpv(x):
    return [mp.mpf(float(c)) for c in x]


def mp_vmol(ua, ub):
    mp.mp.dps = 60
    a, b = _mpv(ua), _mpv(ub)
    Wa = mp.sqrt(1 + sum(c * c for c in a))
    Wb = mp.sqrt(1 + sum(c * c for c in b))
    g = Wa * Wb - sum(x * y for x, y in zip(a, b))
    return mp.sqrt(g * g - 1) / (Wa * Wb)


def mp_scatter(ua, ub, ma, mb, nhat):
    """Textbook evaluation at 60 digits for one pair; returns two lists of mpf."""
    mp.mp.dps = 60
    a, b, n = _mpv(ua), _mpv(ub), _mpv(nhat)
    ma, mb = mp.mpf(float(ma)), mp.mpf(float(mb))
    pa = [ma * c for c in a]
    pb = [mb * c for c in b]
    Ea = mp.sqrt(ma * ma + sum(c * c for c in pa))
    Eb = mp.sqrt(mb * mb + sum(c * c for c in pb))
    P = [x + y for x, y in zip(pa, pb)]
    E = Ea + Eb
    s = E * E - sum(c * c for c in P)
    rs = mp.sqrt(s)
    pst = mp.sqrt((s - (ma + mb) ** 2) * (s - (ma - mb) ** 2) / (4 * s))
    Est = (s + ma * ma - mb * mb) / (2 * rs)
    beta = [c / E for c in P]
    b2 = sum(c * c for c in beta)
    g = 1 / mp.sqrt(1 - b2)
    psa = [pst * c for c in n]
    bp = sum(x * y for x, y in zip(beta, psa))
    if b2 > 0:
        pa_new = [psa[i] + ((g - 1) * bp / b2 + g * Est) * beta[i] for i in range(3)]
    else:
        pa_new = psa
    pb_new = [P[i] - pa_new[i] for i in range(3)]
    return [c / ma for c in pa_new], [c / mb for c in pb_new]


def make_test_vectors(path, n_random=200, seed=20261115):
    """Write JSON test vectors for the kernel of the code: inputs (u_a, u_b, m_a, m_b,
    nhat) as doubles (hex strings, exact), expected outputs (60-digit reference rounded
    to double). Cases: hand-picked edge cases plus n_random random pairs spanning
    theta 1e-8..1e6 and bulk Lorentz factors up to 1e4."""
    rng = np.random.default_rng(seed)
    cases = []

    def add(ua, ub, ma, mb, nh, label):
        ua = np.asarray(ua, float); ub = np.asarray(ub, float)
        nh = np.asarray(nh, float); nh = nh / np.sqrt(nh @ nh)
        ra, rb = mp_scatter(ua, ub, ma, mb, nh)
        cases.append(dict(label=label,
                          ua=[float(x).hex() for x in ua], ub=[float(x).hex() for x in ub],
                          ma=float(ma).hex(), mb=float(mb).hex(),
                          nhat=[float(x).hex() for x in nh],
                          ua_out=[float(x) for x in ra], ub_out=[float(x) for x in rb],
                          vmol=float(mp_vmol(ua, ub))))

    add([0, 0, 0], [1e-4, 0, 0], 1, 1, [0, 1, 0], "nr_head_on_at_rest")
    add([3e-5, -1e-5, 2e-5], [-2e-5, 4e-5, 1e-5], 1, 1, [0.3, -0.5, 0.8], "nr_generic")
    add([1e-8, 0, 0], [-1e-8, 0, 0], 1, 1, [0, 0, 1], "nr_tiny_relative_speed")
    add([1e3, 0, 0], [-1e3, 0, 0], 1, 1, [0, 1, 0], "ur_head_on")
    add([1e4, 1e4 * 1e-6, 0], [1e4, -1e4 * 1e-6, 0], 1, 1, [0, 1, 0],
        "ur_collinear_small_angle")
    add([1e6, 0, 0], [1.000001e6, 0, 0], 1, 1, [0.6, 0.8, 0], "ur_collinear_close")
    add([0.5, 0.2, -0.1], [0.5, 0.2, -0.1], 1, 1, [0, 0, 1], "identical_velocities")
    add([0.3, 0, 0], [0, 0.4, 0], 1, 3, [1, 1, 1], "unequal_physical_masses")
    add([2.0, -1.0, 0.5], [-0.7, 0.1, 1.3], 1, 1, [-0.2, 0.9, 0.1], "mildly_relativistic")
    for i in range(n_random):
        th = 10.0 ** rng.uniform(-8, 6)
        gb = 10.0 ** rng.uniform(0, 4)
        ub_ = np.sqrt(gb * gb - 1.0)
        bulk = ub_ * _unit(rng)
        ua = bulk + np.sqrt(th) * rng.normal(size=3) * (1.0 + np.sqrt(th))
        ubv = bulk + np.sqrt(th) * rng.normal(size=3) * (1.0 + np.sqrt(th))
        add(ua, ubv, 1, 1, _unit(rng), f"random_{i:03d}")
    with open(path, "w") as fh:
        json.dump(dict(description=__doc__.split("\n")[0], generator="kinematics.py",
                       convention="nhat = direction of a's momentum after the collision "
                                  "in the CM axes reached by the pure boost P/E",
                       cases=cases), fh, indent=1)
    return len(cases)


def _unit(rng):
    v = rng.normal(size=3)
    return v / np.sqrt(v @ v)
