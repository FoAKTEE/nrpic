"""First post-Newtonian (Einstein-Infeld-Hoffmann) N-body reference for the Hills passages.

Reference calculation of track F-hills (package eih, wave 3a): ordinary differential
equations for point masses, all bodies free (the large black hole moves). Decision 0010:
an exact or semi-analytic reference solution outside athenak/src, not a simulation code.

Equations (G = c = 1; c2inv = 1/c^2 multiplies every post-Newtonian term, so c2inv = 0 is
Newton). Acceleration of body a, x_ab = x_a - x_b, n_ab = x_ab / r_ab:

  a_a = - sum_{b!=a} m_b x_ab / r_ab^3
        + c2inv sum_{b!=a} (m_b x_ab / r_ab^3) [ 4 m_b/r_ab + 5 m_a/r_ab
              + sum_{c!=a,b} ( m_c/r_bc + 4 m_c/r_ac - (1/2) (m_c/r_bc^3) (x_ab . x_bc) )
              - v_a^2 + 4 v_a.v_b - 2 v_b^2 + (3/2) (v_b . n_ab)^2 ]
        - c2inv (7/2) sum_{b!=a} (m_b/r_ab) sum_{c!=a,b} m_c x_bc / r_bc^3
        + c2inv sum_{b!=a} (m_b / r_ab^3) [x_ab . (4 v_a - 3 v_b)] (v_a - v_b)

Source, read at the locator: Will, arXiv:1312.1289v3, PN-NbodyDraft.tex lines 338-355
(Eq. eq:EIH). The same equation, written differently, is 2404.16270 appendix.tex lines
117-124 (Eq. eab.1) and 2604.27429 template.tex lines 100-120 (Eq. eq:EIH); the three
agree term by term (README, section "Equations").

Conserved quantities to 1PN accuracy (Will, PN-NbodyDraft.tex lines 357-380, Eqs.
energy2 and momentum):

  E = (1/2) sum_a m_a (v_a^2 - sum_{b!=a} m_b/r_ab)
      + c2inv sum_a m_a [ (3/8) v_a^4 + (3/2) v_a^2 sum_{b!=a} m_b/r_ab
                          + (1/2) sum_{b!=a} sum_{c!=a} m_b m_c/(r_ab r_ac)
                          - (1/4) sum_{b!=a} (m_b/r_ab) (7 v_a.v_b + (v_a.n_ab)(v_b.n_ab)) ]
  P = sum_a m_a v_a + (c2inv/2) sum_a m_a v_a (v_a^2 - sum_{b!=a} m_b/r_ab)
      - (c2inv/2) sum_a sum_{b!=a} (m_a m_b/r_ab) (v_a.n_ab) n_ab

Derived here (not from a source; tested numerically in tests/test_eih.py):
  canonical momenta of the Lagrangian whose energy function is E above,
      p_a = m_a v_a [1 + c2inv (v_a^2/2 + 3 sum_{b!=a} m_b/r_ab)]
            - (c2inv/2) sum_{b!=a} (m_a m_b/r_ab) (7 v_b + n_ab (n_ab.v_b)),
  with sum_a p_a = P identically; angular momentum J = sum_a x_a x p_a;
  centre of mass G = sum_a m_a x_a [1 + c2inv (v_a^2/2 - (1/2) sum_{b!=a} m_b/r_ab)]
  (the general form of Will's truncated Eq. at PN-NbodyDraft.tex lines 545-547), dG/dt = P.

Body order of the Hills problems: [M, m1, m2] (as tracks/F-hills/newton3). The drivers below
take newton3's HillsSetup and initial states and return newton3's outcome codes, so that the
three references (newton3, geodesic_binary/hrna.py, this module) are driven alike.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from scipy.integrate._ivp import dop853_coefficients as _c

HERE = os.path.dirname(os.path.abspath(__file__))
NEWTON3 = os.path.join(HERE, "..", "newton3")
if NEWTON3 not in sys.path:
    sys.path.insert(0, NEWTON3)
from hills3.threebody import (_stack, initial_state_arrays, member_energies,  # noqa: E402
                              classify, _energies_in_units, OUTCOME_NAMES)
from hills3.orbits import conic_time_from_pericentre  # noqa: E402

# extra outcome flags of this module (bit field 'flag'): the 1PN prediction is not
# controlled for these encounters
FLAG_DEEP = 1        # a member came closer to M than r_trust (harmonic coordinate distance)
FLAG_MERGE = 2       # the members came closer than r12_stop (they would merge)
FLAG_STOPPED = 4     # integration stopped early (r_stop or r12_stop reached)
FLAG_FAILED = 8      # step-size underflow or step limit


# ------------------------------------------------------------------------------------------
# pairwise geometry
# ------------------------------------------------------------------------------------------
def _pairs(x):
    """x (..., N, 3) -> X[..., a, b, :] = x_a - x_b, r[..., a, b] (diagonal set to inf)."""
    X = x[..., :, None, :] - x[..., None, :, :]
    r = np.sqrt(np.sum(X * X, axis=-1))
    N = x.shape[-2]
    eye = np.eye(N, dtype=bool)
    r = np.where(eye, np.inf, r)
    return X, r


def accel(x, v, m, c2inv=1.0):
    """EIH accelerations. x, v (..., N, 3); m (..., N) or (N,). Returns (..., N, 3)."""
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    N = x.shape[-2]
    m = np.broadcast_to(np.asarray(m, dtype=float), x.shape[:-1])
    X, r = _pairs(x)                       # X[a,b] = x_a - x_b
    ir = 1.0 / r                           # 0 on the diagonal
    ir3 = ir ** 3
    mb = m[..., None, :]                   # m_b broadcast over a
    # Newtonian part: -sum_b m_b X_ab / r_ab^3
    aN = -np.sum((mb * ir3)[..., None] * X, axis=-2)
    if c2inv == 0.0:
        return aN
    v2 = np.sum(v * v, axis=-1)                                   # (..., N)
    vv = np.einsum("...ak,...bk->...ab", v, v)                    # v_a . v_b
    # Newtonian accelerations g_b (for the terms with the acceleration of b)
    # potential sums U_a = sum_{b!=a} m_b / r_ab
    U = np.sum(mb * ir, axis=-1)                                  # (..., N)
    pn = np.zeros_like(x)
    for a in range(N):
        for b in range(N):
            if b == a:
                continue
            Xab = X[..., a, b, :]
            rab = r[..., a, b]
            nab = Xab / rab[..., None]
            vbn = np.sum(v[..., b, :] * nab, axis=-1)
            br = (4.0 * m[..., b] / rab + 5.0 * m[..., a] / rab
                  - v2[..., a] + 4.0 * vv[..., a, b] - 2.0 * v2[..., b] + 1.5 * vbn ** 2)
            third = np.zeros_like(rab)
            vec7 = np.zeros_like(Xab)
            for c in range(N):
                if c == a or c == b:
                    continue
                Xbc = X[..., b, c, :]
                rbc = r[..., b, c]
                rac = r[..., a, c]
                third = third + (m[..., c] / rbc + 4.0 * m[..., c] / rac
                                 - 0.5 * m[..., c] / rbc ** 3 * np.sum(Xab * Xbc, axis=-1))
                vec7 = vec7 + (m[..., c] / rbc ** 3)[..., None] * Xbc
            br = br + third
            pn[..., a, :] += (m[..., b] / rab ** 3 * br)[..., None] * Xab
            pn[..., a, :] += -3.5 * (m[..., b] / rab)[..., None] * vec7
            w = np.sum(Xab * (4.0 * v[..., a, :] - 3.0 * v[..., b, :]), axis=-1)
            pn[..., a, :] += (m[..., b] / rab ** 3 * w)[..., None] * (v[..., a, :] - v[..., b, :])
    del U
    return aN + c2inv * pn


def energy(x, v, m, c2inv=1.0):
    """1PN conserved energy (Will 1312.1289 Eq. energy2), without the rest masses."""
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    m = np.broadcast_to(np.asarray(m, dtype=float), x.shape[:-1])
    X, r = _pairs(x)
    ir = 1.0 / r
    mb = m[..., None, :]
    U = np.sum(mb * ir, axis=-1)
    v2 = np.sum(v * v, axis=-1)
    EN = 0.5 * np.sum(m * (v2 - U), axis=-1)
    if c2inv == 0.0:
        return EN
    n = X * ir[..., None]
    van = np.einsum("...abk,...ak->...ab", n, v)                  # v_a . n_ab
    vbn = np.einsum("...abk,...bk->...ab", n, v)                  # v_b . n_ab
    vv = np.einsum("...ak,...bk->...ab", v, v)
    t = (0.375 * v2 ** 2 + 1.5 * v2 * U + 0.5 * U ** 2
         - 0.25 * np.sum(mb * ir * (7.0 * vv + van * vbn), axis=-1))
    return EN + c2inv * np.sum(m * t, axis=-1)


def momentum(x, v, m, c2inv=1.0):
    """1PN conserved linear momentum (Will 1312.1289 Eq. momentum)."""
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    m = np.broadcast_to(np.asarray(m, dtype=float), x.shape[:-1])
    X, r = _pairs(x)
    ir = 1.0 / r
    mb = m[..., None, :]
    U = np.sum(mb * ir, axis=-1)
    v2 = np.sum(v * v, axis=-1)
    P = np.sum(m[..., None] * v, axis=-2)
    if c2inv == 0.0:
        return P
    n = X * ir[..., None]
    van = np.einsum("...abk,...ak->...ab", n, v)
    P = P + 0.5 * c2inv * np.sum((m * (v2 - U))[..., None] * v, axis=-2)
    P = P - 0.5 * c2inv * np.sum((m[..., :, None] * mb * ir * van)[..., None] * n, axis=(-3, -2))
    return P


def canonical_momenta(x, v, m, c2inv=1.0):
    """p_a = dL/dv_a of the EIH Lagrangian (module docstring; derived, tested)."""
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    m = np.broadcast_to(np.asarray(m, dtype=float), x.shape[:-1])
    X, r = _pairs(x)
    ir = 1.0 / r
    mb = m[..., None, :]
    U = np.sum(mb * ir, axis=-1)
    v2 = np.sum(v * v, axis=-1)
    p = m[..., None] * v
    if c2inv == 0.0:
        return p
    n = X * ir[..., None]
    vbn = np.einsum("...abk,...bk->...ab", n, v)                  # n_ab . v_b
    p = p + c2inv * (m * (0.5 * v2 + 3.0 * U))[..., None] * v
    w = (m[..., :, None] * mb * ir)                               # m_a m_b / r_ab
    term = 7.0 * np.einsum("...ab,...bk->...ak", w, v) + np.sum((w * vbn)[..., None] * n, axis=-2)
    return p - 0.5 * c2inv * term


def angular_momentum(x, v, m, c2inv=1.0):
    return np.sum(np.cross(np.asarray(x, float), canonical_momenta(x, v, m, c2inv)), axis=-2)


def centre_of_mass(x, v, m, c2inv=1.0):
    """G = sum_a m_a x_a [1 + c2inv (v_a^2/2 - U_a/2)] and the 1PN mass M* = sum of the
    weights (module docstring)."""
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    m = np.broadcast_to(np.asarray(m, dtype=float), x.shape[:-1])
    _, r = _pairs(x)
    U = np.sum(m[..., None, :] / r, axis=-1)
    w = m * (1.0 + c2inv * (0.5 * np.sum(v * v, axis=-1) - 0.5 * U))
    return np.sum(w[..., None] * x, axis=-2), np.sum(w, axis=-1)


def velocities_from_momenta(x, p, m, c2inv=1.0, tol=1e-15, maxit=200):
    """Invert canonical_momenta for v (fixed point; start v = p/m)."""
    x = np.asarray(x, dtype=float)
    p = np.asarray(p, dtype=float)
    m = np.broadcast_to(np.asarray(m, dtype=float), x.shape[:-1])
    v = p / m[..., None]
    _, r = _pairs(x)
    U = np.sum(m[..., None, :] / r, axis=-1)
    for _ in range(maxit):
        dp = canonical_momenta(x, v, m, c2inv) - p
        # divide by the diagonal of d p_a / d v_a (direction along v): m_a (1 + 3U + 3/2 v^2)
        diag = m * (1.0 + c2inv * (3.0 * U + 1.5 * np.sum(v * v, axis=-1)))
        vn = v - dp / diag[..., None]
        if np.max(np.abs(vn - v)) < tol * max(1.0, np.max(np.abs(v))):
            return vn
        v = vn
    raise RuntimeError("velocities_from_momenta did not converge")


# ------------------------------------------------------------------------------------------
# test-mass limit (2404.16270 appendix.tex lines 182-188, Eqs. EIH1 and EIH2)
# ------------------------------------------------------------------------------------------
def testmass_E_L(r, vr, vphi, M=1.0):
    """1PN energy and angular momentum per unit mass of a test body about a fixed M."""
    v2 = vr * vr + vphi * vphi
    E = 0.5 * v2 - M / r + 0.375 * v2 * v2 + 0.5 * M / r * (3.0 * v2 + M / r)
    L = r * vphi * (1.0 + 0.5 * v2 + 3.0 * M / r)
    return E, L


def testmass_state(E, L, r, M=1.0, incoming=True):
    """(v_r, v_phi) of a test body at radius r with 1PN energy E and angular momentum L
    (inverse of testmass_E_L; None where no real solution)."""
    from scipy.optimize import brentq

    def resid(vphi, v2):
        return r * vphi * (1.0 + 0.5 * v2 + 3.0 * M / r) - L
    # v2 from E: (3/8) v2^2 + (1/2 + 3M/2r) v2 + (M^2/2r^2 - M/r - E) = 0
    bq = 0.5 + 1.5 * M / r
    cq = 0.5 * M * M / (r * r) - M / r - E
    disc = bq * bq - 1.5 * cq
    if disc < 0:
        return None
    v2 = (-bq + math.sqrt(disc)) / 0.75
    if v2 < 0:
        return None
    vphi = L / (r * (1.0 + 0.5 * v2 + 3.0 * M / r))
    if vphi * vphi > v2:
        return None
    vr = math.sqrt(v2 - vphi * vphi)
    return (-vr if incoming else vr), vphi


# ------------------------------------------------------------------------------------------
# vectorised DOP853 with per-trajectory stop (after newton3/hills3/integrate.py)
# ------------------------------------------------------------------------------------------
N_STAGES = _c.N_STAGES
_A = np.array(_c.A[:N_STAGES, :N_STAGES])
_B = np.array(_c.B)
_C = np.array(_c.C[:N_STAGES])
_E3 = np.array(_c.E3)
_E5 = np.array(_c.E5)


def integrate_many(rhs, t0, y0, t_end, h0, rtol=1e-11, atol=1e-14, max_steps=3_000_000,
                   monitor=None, stop=None):
    """As newton3's integrate_many, plus stop(t, y, idx) -> bool (n,): trajectories for
    which it returns True after an accepted step are finished there. Returns
    (y_end, t_reached, n_accepted, ok, stopped)."""
    y = np.array(y0, dtype=float, copy=True)
    N, d = y.shape
    t = np.broadcast_to(np.asarray(t0, dtype=float), (N,)).copy()
    t_end = np.broadcast_to(np.asarray(t_end, dtype=float), (N,)).copy()
    h = np.broadcast_to(np.asarray(h0, dtype=float), (N,)).copy()
    nacc = np.zeros(N, dtype=np.int64)
    ok = np.ones(N, dtype=bool)
    stopped = np.zeros(N, dtype=bool)
    idx_all = np.arange(N)
    f = rhs(t, y, idx_all)
    act = idx_all[t < t_end]
    it = 0
    while act.size:
        it += 1
        if it > max_steps:
            ok[act] = False
            break
        n = act.size
        ta, ya, fa = t[act], y[act], f[act]
        ha = np.minimum(h[act], t_end[act] - ta)
        K = np.empty((N_STAGES + 1, n, d))
        K[0] = fa
        for s in range(1, N_STAGES):
            dy = np.tensordot(_A[s, :s], K[:s], axes=(0, 0)) * ha[:, None]
            K[s] = rhs(ta + _C[s] * ha, ya + dy, act)
        y_new = ya + ha[:, None] * np.tensordot(_B, K[:N_STAGES], axes=(0, 0))
        t_new = ta + ha
        f_new = rhs(t_new, y_new, act)
        K[N_STAGES] = f_new
        scale = atol + np.maximum(np.abs(ya), np.abs(y_new)) * rtol
        e5 = np.sum((np.tensordot(_E5, K, axes=(0, 0)) / scale) ** 2, axis=1)
        e3 = np.sum((np.tensordot(_E3, K, axes=(0, 0)) / scale) ** 2, axis=1)
        denom = e5 + 0.01 * e3
        with np.errstate(divide="ignore", invalid="ignore"):
            err = np.where(denom > 0, np.abs(ha) * e5 / np.sqrt(denom * d), 0.0)
            fac = np.where(err > 0, 0.9 * err ** (-1.0 / 8.0), 10.0)
        bad = ~np.isfinite(err)
        err[bad] = 1e300
        fac[bad] = 0.2
        acc = err <= 1.0
        ia = act[acc]
        y[ia] = y_new[acc]
        t[ia] = t_new[acc]
        f[ia] = f_new[acc]
        nacc[ia] += 1
        h[act] = np.where(acc, ha * np.minimum(10.0, fac), ha * np.maximum(0.2, np.minimum(fac, 1.0)))
        if ia.size:
            if monitor is not None:
                monitor(t[ia], y[ia], ia)
            if stop is not None:
                st = stop(t[ia], y[ia], ia)
                stopped[ia[st]] = True
        done = (t[act] >= t_end[act] - 1e-14 * np.maximum(np.abs(t_end[act]), 1.0)) | stopped[act]
        tiny = h[act] <= 1e-14 * np.maximum(np.abs(t[act]), 1.0)
        if np.any(tiny & ~done):
            ok[act[tiny & ~done]] = False
        act = act[~(done | tiny)]
    return y, t, nacc, ok, stopped


def rhs_factory(masses, c2inv=1.0):
    """rhs(t, y, idx) for y = (x (N*3), v (N*3)); masses (n, N)."""
    masses = np.asarray(masses, dtype=float)
    N = masses.shape[1]

    def rhs(t, y, idx):
        x = y[:, :3 * N].reshape(-1, N, 3)
        v = y[:, 3 * N:].reshape(-1, N, 3)
        out = np.empty_like(y)
        out[:, :3 * N] = y[:, 3 * N:]
        out[:, 3 * N:] = accel(x, v, masses[idx], c2inv).reshape(-1, 3 * N)
        return out
    return rhs


# ------------------------------------------------------------------------------------------
# drivers with newton3's interface
# ------------------------------------------------------------------------------------------
def evolve_states(masses, x, v, t0, t_end, c2inv=1.0, rtol=1e-11, atol=1e-14, h_scale=None,
                  r_trust=6.0, r_stop=1.0, r12_stop=None, record_every=0):
    """EIH evolution of three-body states x, v (n, 3, 3), bodies [M, m1, m2], masses (n, 3),
    from t0 to t_end (n,). Classification at the end with newton3's member_energies and
    classify (Newtonian Jacobi energies; module docstring of newton3/hills3/threebody.py).

    Stops a trajectory early when a member comes closer to M than r_stop (harmonic
    coordinate distance, in units of M) or the members closer than r12_stop (default
    2 (m1 + m2)); flags (bit field 'flag'): FLAG_DEEP if a member came closer than r_trust,
    FLAG_MERGE, FLAG_STOPPED, FLAG_FAILED. Returns a dict like newton3.evolve_states plus
    flag, t_reached, E1PN_err, P1PN_err, J1PN_err (relative changes of the 1PN integrals),
    EN_err (change of the Newtonian energy, for comparison), rMmin (n, 2), r12min,
    eps_max = max M/r of the members over the run."""
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    n = x.shape[0]
    masses = np.broadcast_to(np.asarray(masses, dtype=float), (n, 3)).copy()
    t0 = np.broadcast_to(np.asarray(t0, dtype=float), (n,))
    t_end = np.broadcast_to(np.asarray(t_end, dtype=float), (n,))
    if r12_stop is None:
        r12_stop = 2.0 * (masses[:, 1] + masses[:, 2])
    r12_stop = np.broadcast_to(np.asarray(r12_stop, dtype=float), (n,))
    Mh = masses[:, 0]
    y0 = np.concatenate([x.reshape(n, 9), v.reshape(n, 9)], axis=1)
    E0 = energy(x, v, masses, c2inv)
    EN0 = energy(x, v, masses, 0.0)
    P0 = momentum(x, v, masses, c2inv)
    J0 = angular_momentum(x, v, masses, c2inv)
    scaleE = 0.5 * np.sum(masses * np.sum(v * v, axis=-1), axis=-1)       # kinetic scale
    scaleP = np.sum(masses * np.linalg.norm(v, axis=-1), axis=-1)
    scaleJ = np.sum(masses * np.linalg.norm(np.cross(x, v), axis=-1), axis=-1)
    r12min = np.linalg.norm(x[:, 2] - x[:, 1], axis=1)
    rMmin = np.stack([np.linalg.norm(x[:, 1] - x[:, 0], axis=1),
                      np.linalg.norm(x[:, 2] - x[:, 0], axis=1)], axis=1)
    rec = [] if record_every else None
    counter = [0]

    def monitor(t, y, idx):
        xx = y[:, :9].reshape(-1, 3, 3)
        np.minimum.at(r12min, idx, np.linalg.norm(xx[:, 2] - xx[:, 1], axis=1))
        np.minimum.at(rMmin[:, 0], idx, np.linalg.norm(xx[:, 1] - xx[:, 0], axis=1))
        np.minimum.at(rMmin[:, 1], idx, np.linalg.norm(xx[:, 2] - xx[:, 0], axis=1))
        if rec is not None:
            counter[0] += 1
            if counter[0] % record_every == 0:
                rec.append((t.copy(), idx.copy(), y.copy()))

    def stop(t, y, idx):
        xx = y[:, :9].reshape(-1, 3, 3)
        r1 = np.linalg.norm(xx[:, 1] - xx[:, 0], axis=1)
        r2 = np.linalg.norm(xx[:, 2] - xx[:, 0], axis=1)
        r12 = np.linalg.norm(xx[:, 2] - xx[:, 1], axis=1)
        return (np.minimum(r1, r2) < r_stop * Mh[idx]) | (r12 < r12_stop[idx])

    if h_scale is None:
        r12 = np.linalg.norm(x[:, 2] - x[:, 1], axis=1)
        h_scale = 2 * np.pi * np.sqrt(r12 ** 3 / (masses[:, 1] + masses[:, 2]))
    y, t_reached, nacc, ok, stopped = integrate_many(
        rhs_factory(masses, c2inv), t0, y0, t_end, 1e-3 * h_scale, rtol=rtol, atol=atol,
        monitor=monitor, stop=stop)
    xe = y[:, :9].reshape(n, 3, 3)
    ve = y[:, 9:].reshape(n, 3, 3)
    en = member_energies(xe, ve, masses, 1.0)
    outcome, outcome_M = classify(en, xe, ve, masses, 1.0)
    flag = np.zeros(n, dtype=int)
    flag[np.min(rMmin, axis=1) < r_trust * Mh] |= FLAG_DEEP
    flag[r12min < r12_stop] |= FLAG_MERGE
    flag[stopped] |= FLAG_STOPPED
    flag[~ok] |= FLAG_FAILED
    res = dict(outcome=outcome, outcome_M=outcome_M, _en=en, flag=flag, t_reached=t_reached,
               r12min=r12min, rMmin=rMmin, eps_max=Mh / np.min(rMmin, axis=1),
               E1PN_err=(energy(xe, ve, masses, c2inv) - E0) / scaleE,
               EN_err=(energy(xe, ve, masses, 0.0) - EN0) / scaleE,
               P1PN_err=np.linalg.norm(momentum(xe, ve, masses, c2inv) - P0, axis=1) / scaleP,
               J1PN_err=np.linalg.norm(angular_momentum(xe, ve, masses, c2inv) - J0, axis=1) / scaleJ,
               nacc=nacc, ok=ok, x_end=xe, v_end=ve)
    for k in ("a1", "e1", "a2", "e2", "a12", "e12", "a_in", "e_in", "rp_in", "inner"):
        res[k] = en[k]
    if rec is not None:
        res["record"] = rec
    return res


def vinf_out(res, masses):
    """Speed at infinity of the outer member relative to the barycentre of (M, inner member),
    from its Newtonian Jacobi energy at the end (NaN if bound or the binary survived)."""
    en = res["_en"]
    M = masses[:, 0]
    inner = en["inner"]
    mc = np.where(inner == 1, masses[:, 1], masses[:, 2])
    me = np.where(inner == 1, masses[:, 2], masses[:, 1])
    mu_out = me * (M + mc) / masses.sum(axis=1)
    with np.errstate(invalid="ignore"):
        return np.where(en["E_out"] > 0, np.sqrt(2 * en["E_out"] / mu_out), np.nan)


def scatter(setups, r0=None, k0=4.0, k_end=30.0, t_end=None, c2inv=1.0, rtol=1e-11,
            atol=1e-14, **kw):
    """EIH counterpart of newton3.threebody.scatter: the same HillsSetup list and the same
    initial data (the binary on the Newtonian conic about M + m at r0 = k0 r_t, barycentric
    positions and velocities), integrated with the EIH equations to the time at which the
    Newtonian conic would be at k_end r_t outbound. Energies in newton3's unit
    (G m1 m2 / a)(M/m)^(1/3), Newtonian Jacobi definitions (as newton3)."""
    P = _stack(setups)
    n = P["M"].size
    if r0 is None:
        r0 = k0 * P["r_t"]
    x, v, t0 = initial_state_arrays(P, r0)
    masses = np.stack([P["M"], P["m1"], P["m2"]], axis=1)
    mu = P["G"] * (P["M"] + P["m"])
    if t_end is None:
        t_end = conic_time_from_pericentre(P["rp"], P["e_orb"], mu, k_end * P["r_t"])
    t_end = np.broadcast_to(np.asarray(t_end, dtype=float), (n,))
    unit = P["G"] * P["m1"] * P["m2"] / P["a"] * (P["M"] / P["m"]) ** (1.0 / 3.0)
    res = evolve_states(masses, x, v, t0, t_end, c2inv=c2inv, rtol=rtol, atol=atol,
                        h_scale=np.minimum(2 * np.pi / np.sqrt(P["G"] * P["m"] / P["a"] ** 3),
                                           np.abs(t0)), **kw)
    res.update(_energies_in_units(res, masses, P["G"], unit, x, v))
    res["vinf"] = vinf_out(res, masses)
    res["a12"] = res["a12"] / P["a"]
    res.update(t0=t0, t_end=t_end, x0=x, v0=v, masses=masses)
    return res


def puncture_masses_positions_momenta(path):
    """Read an nrpic_cf input (members first, M last, as three_punctures/inputs) and return
    masses, positions, momenta in the order [M, m1, m2]."""
    from hills3.threebody import parse_problem_block
    with open(path) as fh:
        blk = parse_problem_block(fh.read())
    order = [2, 0, 1]
    return blk["masses"][order], blk["positions"][order], blk["momenta"][order]


def run_encounter(law="eih", M=1.0, m1=0.05, m2=0.05, a=3.0, rp=8.0, phase=0.0, sense=1,
                  k0=4.0, k_end=30.0, c2inv=1.0, **kw):
    """One coplanar encounter with the parameter names of newton3/geodesic_binary
    (law: 'eih' or 'newton' (= c2inv 0); phase: newton3's effective phase). Returns the
    scatter() dict for that encounter with scalars."""
    from hills3.threebody import HillsSetup
    s = HillsSetup(M=M, m1=m1, m2=m2, a=a, rp=rp, phase=phase,
                   theta=np.pi / 2, varphi=(np.pi / 2 if sense > 0 else -np.pi / 2))
    res = scatter([s], k0=k0, k_end=k_end, c2inv=(0.0 if law == "newton" else c2inv), **kw)
    out = {}
    for k, val in res.items():
        if isinstance(val, np.ndarray) and val.shape[:1] == (1,):
            out[k] = val[0].item() if val[0].ndim == 0 else val[0]
        elif k != "_en":
            out[k] = val
    out["outcome_name"] = OUTCOME_NAMES[int(out["outcome"])]
    return out
