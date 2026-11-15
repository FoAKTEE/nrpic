"""Restricted parabolic three-body problem of Sari, Kobayashi & Rossi (SKR, arXiv:0911.1136).

Equations (SKR prp.tex:223-259; BKRS arXiv:1804.02911 mnras.tex:149-164): the relative
vector eta = (M/m)^(1/3) r / r_p of the binary members obeys

    eta'' = (r_p/r_m)^3 [ -eta + 3 (eta . rhat_m) rhat_m ] - eta / |eta|^3,

with time in units of sqrt(r_p^3 / G M), rhat_m = (cos f, sin f, 0),
r_p/r_m = (1 + cos f)/2 and f(t) from t = (sqrt 2 / 3) tan(f/2) (3 + tan^2(f/2))
(SKR prp.tex:251), inverted here in closed form, tan(f/2) = 2 sinh(asinh(3t/(2 sqrt 2))/3). The equations contain no
parameter: D = r_p / r_t enters only through the initial data (binary separation 1/D,
mean motion D^(3/2) in these units).

Energy of the secondary after disruption, in units of (G m1 m2 / a)(M/m)^(1/3)
(SKR prp.tex:350-357, BKRS mnras.tex:181-188):

    E2 = (1/D) [ (1+cos f)^2/4 (x cos f + y sin f) + (-sin f x' + (1+cos f) y') / sqrt 2 ].

E1 = -E2 (SKR prp.tex:347). The primary is ejected when E2 < 0.
"""
import numpy as np
from .integrate import integrate_many
from .orbits import binary_relative_state

SQRT2 = np.sqrt(2.0)
HILL_FACTOR = 3.0 ** (-1.0 / 3.0)


def tau_of_t(t):
    """tan(f/2) on the unit parabola as a function of time (exact inversion)."""
    # tau^3 + 3 tau = 2 s with s = 3 t / (2 sqrt 2); tau = 2 sinh(asinh(s) / 3)
    t = np.asarray(t, dtype=float)
    return 2.0 * np.sinh(np.arcsinh(3.0 * t / (2.0 * SQRT2)) / 3.0)


def t_of_tau(tau):
    return SQRT2 * (tau + tau ** 3 / 3.0)


def geometry(t):
    """w = r_p/r_m, cos f, sin f at time t."""
    tau = tau_of_t(t)
    w = 1.0 / (1.0 + tau * tau)
    return w, (1.0 - tau * tau) * w, 2.0 * tau * w


def make_rhs(self_gravity=True):
    def rhs(t, y, idx):
        w, cf, sf = geometry(t)
        k = w ** 3
        x, yy, z = y[:, 0], y[:, 1], y[:, 2]
        out = np.empty_like(y)
        out[:, :3] = y[:, 3:]
        rr = x * cf + yy * sf
        ax = k * (-x + 3.0 * rr * cf)
        ay = k * (-yy + 3.0 * rr * sf)
        az = -k * z
        if self_gravity:
            r2 = x * x + yy * yy + z * z
            ir3 = r2 ** -1.5
            ax -= x * ir3
            ay -= yy * ir3
            az -= z * ir3
        out[:, 3], out[:, 4], out[:, 5] = ax, ay, az
        return out
    return rhs


def energy_bracket(t, y):
    """The bracket of SKR prp.tex:356; E2 = bracket / D in units (G m1 m2/a)(M/m)^(1/3)."""
    w, cf, sf = geometry(t)
    opc = 2.0 * w  # 1 + cos f
    x, yy, vx, vy = y[:, 0], y[:, 1], y[:, 3], y[:, 4]
    return opc ** 2 / 4.0 * (x * cf + yy * sf) + (-sf * vx + opc * vy) / SQRT2


def initial_conditions(D, theta, varphi, phase, e_b=0.0, varpi=0.0, k0=10.0):
    """Start at r_m = k0 r_t on the incoming branch. Returns t0 (n,), y0 (n, 6).

    phase is the effective mean anomaly at the pericentre time (SKR prp.tex:606):
    the mean anomaly at the start is phase + n t0 with t0 < 0.
    """
    D = np.atleast_1d(np.asarray(D, dtype=float))
    shp = np.broadcast_shapes(D.shape, np.shape(theta), np.shape(varphi), np.shape(phase),
                              np.shape(e_b), np.shape(varpi))
    D = np.broadcast_to(D, shp).ravel()
    th = np.broadcast_to(theta, shp).ravel()
    vp = np.broadcast_to(varphi, shp).ravel()
    ph = np.broadcast_to(phase, shp).ravel()
    eb = np.broadcast_to(e_b, shp).ravel()
    vw = np.broadcast_to(varpi, shp).ravel()
    tau0 = -np.sqrt(k0 / D - 1.0)
    t0 = t_of_tau(tau0)
    a = 1.0 / D
    n = D ** 1.5
    r, v = binary_relative_state(a, eb, n, ph + n * t0, vw, th, vp)
    return t0, np.concatenate([r, v], axis=1)


def run(D, theta, varphi, phase, e_b=0.0, varpi=0.0, k0=10.0, k_end=30.0, rtol=1e-10,
        atol=1e-13, self_gravity=True):
    """Integrate the restricted problem from k0 r_t (incoming) to k_end r_t (outgoing).

    Returns a dict of arrays (one entry per trajectory):
      E2        energy of the secondary, units (G m1 m2/a)(M/m)^(1/3) (meaningful when
                disrupted; E1 = -E2)
      disrupted relative two-body energy > 0 at the end
      survived  bound, apocentre < half the Hill radius at the end
      ambiguous bound but wider than that (outcome not settled at k_end)
      rmin      minimum member separation over accepted steps, units of a
      af, ef    semi-major axis (units of a) and eccentricity of survivors
      ok        integrator finished
    """
    D = np.atleast_1d(np.asarray(D, dtype=float))
    shp = np.broadcast_shapes(D.shape, np.shape(theta), np.shape(varphi), np.shape(phase),
                              np.shape(e_b), np.shape(varpi))
    Dflat = np.broadcast_to(D, shp).ravel()
    t0, y0 = initial_conditions(Dflat, theta, varphi, phase, e_b, varpi, k0)
    t_end = t_of_tau(np.sqrt(k_end / Dflat - 1.0))
    rmin = np.linalg.norm(y0[:, :3], axis=1)

    def monitor(t, y, idx):
        r = np.sqrt(np.sum(y[:, :3] ** 2, axis=1))
        np.minimum.at(rmin, idx, r)

    h0 = 1e-3 * 2 * np.pi / Dflat ** 1.5
    y, nacc, ok = integrate_many(make_rhs(self_gravity), t0, y0, t_end, h0, rtol=rtol,
                                 atol=atol, monitor=monitor)
    E2 = energy_bracket(t_end, y) / Dflat
    r = np.linalg.norm(y[:, :3], axis=1)
    v2 = np.sum(y[:, 3:] ** 2, axis=1)
    eps = 0.5 * v2 - 1.0 / r
    hvec = np.cross(y[:, :3], y[:, 3:])
    h2 = np.sum(hvec ** 2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        af = np.where(eps < 0, -0.5 / eps, np.inf)
        ef = np.sqrt(np.maximum(1.0 + 2.0 * eps * h2, 0.0))
    rH = (k_end / Dflat) * HILL_FACTOR
    bound = eps < 0
    survived = bound & (af * (1 + ef) < 0.5 * rH)
    return dict(E2=E2.reshape(shp), disrupted=(~bound).reshape(shp),
                survived=survived.reshape(shp),
                ambiguous=(bound & ~survived).reshape(shp),
                rmin=(rmin * Dflat).reshape(shp), af=(af * Dflat).reshape(shp),
                ef=ef.reshape(shp), nacc=nacc.reshape(shp), ok=ok.reshape(shp),
                y_end=y.reshape(shp + (6,)), t_end=t_end.reshape(shp))


def coplanar_phase(phase_skr, prograde):
    """Convert SKR's coplanar phase (angle counter-clockwise from +x) to this module's
    (theta, varphi, phase): prograde l = +z, retrograde l = -z with phase = -phi_SKR."""
    th = np.pi / 2
    if prograde:
        return th, np.pi / 2, phase_skr
    return th, -np.pi / 2, -np.asarray(phase_skr)
