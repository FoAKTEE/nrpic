"""Kepler orbits and the geometric conventions shared by the restricted and full models.

Frame. The centre-of-mass orbit of the binary about the large mass M lies in the x-y
plane, its angular momentum points along +z and its pericentre along +x (SKR, arXiv:
0911.1136, prp.tex:228; BKRS, arXiv:1804.02911, mnras.tex:156).

Binary orientation. The unit angular momentum of the binary's internal orbit is
l = (cos th, sin th cos vphi, sin th sin vphi) (BKRS mnras.tex:240-244, 286): th is
measured from +x, vphi from +y in the y-z plane. Coplanar prograde: th = vphi = pi/2
(l = +z); coplanar retrograde: th = pi/2, vphi = -pi/2 (l = -z).

In-plane reference. p = projection of +x onto the binary plane (normalised; +y when
l is parallel to x), q = l x p. The binary's periapsis direction is
P = cos(varpi) p + sin(varpi) q; angles grow in the binary's own sense of rotation.
For a circular binary the phase is the mean anomaly measured from p (varpi = 0).
For coplanar prograde orbits this is SKR's phase; for coplanar retrograde orbits SKR
measure the angle counter-clockwise (prp.tex:606-616), so phi_SKR = -phi_here.

Relative vector r = r2 - r1 (secondary minus primary), as in SKR prp.tex:174.
"""
import numpy as np


def orientation_basis(theta, varphi):
    """Return l, p, q, each of shape (n, 3), for arrays theta, varphi."""
    theta = np.atleast_1d(np.asarray(theta, dtype=float))
    varphi = np.broadcast_to(np.asarray(varphi, dtype=float), theta.shape)
    l = np.stack([np.cos(theta), np.sin(theta) * np.cos(varphi),
                  np.sin(theta) * np.sin(varphi)], axis=-1)
    ex = np.array([1.0, 0.0, 0.0])
    ey = np.array([0.0, 1.0, 0.0])
    p = ex[None, :] - (l @ ex)[:, None] * l
    pn = np.linalg.norm(p, axis=1)
    degenerate = pn < 1e-12
    if np.any(degenerate):
        pd = ey[None, :] - (l[degenerate] @ ey)[:, None] * l[degenerate]
        p[degenerate] = pd
        pn[degenerate] = np.linalg.norm(pd, axis=1)
    p = p / pn[:, None]
    q = np.cross(l, p)
    return l, p, q


def solve_kepler(mean_anomaly, e, tol=1e-15, maxit=60):
    """Eccentric anomaly E with E - e sin E = mean_anomaly (elliptic, 0 <= e < 1)."""
    Mm = np.mod(np.asarray(mean_anomaly, dtype=float), 2 * np.pi)
    e = np.broadcast_to(np.asarray(e, dtype=float), Mm.shape)
    E = np.where(e < 0.8, Mm, np.pi * np.ones_like(Mm))
    for _ in range(maxit):
        dE = (E - e * np.sin(E) - Mm) / (1 - e * np.cos(E))
        E = E - dE
        if np.all(np.abs(dE) < tol):
            break
    return E


def binary_relative_state(a, e, n, ell0, varpi, theta, varphi):
    """Position and velocity of r = r2 - r1 for a Kepler binary.

    a semi-major axis, e eccentricity, n mean motion (rad per time unit), ell0 mean
    anomaly at the instant wanted, varpi periapsis direction in the binary plane,
    (theta, varphi) the orientation. All broadcast to shape (n,). Returns (n, 3) each.
    """
    ell0 = np.atleast_1d(np.asarray(ell0, dtype=float))
    shp = ell0.shape
    a = np.broadcast_to(np.asarray(a, dtype=float), shp)
    e = np.broadcast_to(np.asarray(e, dtype=float), shp)
    n = np.broadcast_to(np.asarray(n, dtype=float), shp)
    varpi = np.broadcast_to(np.asarray(varpi, dtype=float), shp)
    l, p, q = orientation_basis(np.broadcast_to(theta, shp), np.broadcast_to(varphi, shp))
    P = np.cos(varpi)[:, None] * p + np.sin(varpi)[:, None] * q
    Q = np.cross(l, P)
    E = solve_kepler(ell0, e)
    se = np.sqrt(1 - e ** 2)
    cE, sE = np.cos(E), np.sin(E)
    r = (a * (cE - e))[:, None] * P + (a * se * sE)[:, None] * Q
    fac = n * a / (1 - e * cE)
    v = (-fac * sE)[:, None] * P + (fac * se * cE)[:, None] * Q
    return r, v


def conic_time_from_pericentre(rp, e, mu, r):
    """Time (>= 0) to go from pericentre to distance r on a conic of pericentre rp,
    eccentricity e and gravitational parameter mu (parabolic, elliptic, hyperbolic)."""
    rp, e, mu, r = np.broadcast_arrays(*[np.asarray(z, dtype=float) for z in (rp, e, mu, r)])
    t = np.empty(rp.shape)
    par = np.abs(e - 1) < 1e-12
    ell = (e < 1) & ~par
    hyp = (e > 1) & ~par
    if np.any(par):
        tau = np.sqrt(r[par] / rp[par] - 1)
        t[par] = np.sqrt(2 * rp[par] ** 3 / mu[par]) * (tau + tau ** 3 / 3)
    if np.any(ell):
        ao = rp[ell] / (1 - e[ell])
        cosE = np.clip((1 - r[ell] / ao) / e[ell], -1, 1)
        E = np.arccos(cosE)
        t[ell] = np.sqrt(ao ** 3 / mu[ell]) * (E - e[ell] * np.sin(E))
    if np.any(hyp):
        ao = rp[hyp] / (e[hyp] - 1)
        coshH = (1 + r[hyp] / ao) / e[hyp]
        H = np.arccosh(np.maximum(coshH, 1.0))
        t[hyp] = np.sqrt(ao ** 3 / mu[hyp]) * (e[hyp] * np.sinh(H) - H)
    return t


def conic_state(rp, e, mu, r, incoming=True):
    """Relative position and velocity (n, 3) at distance r on the conic in the x-y plane
    with pericentre along +x and angular momentum along +z; incoming means before the
    pericentre (true anomaly < 0)."""
    rp, e, mu, r = np.broadcast_arrays(*[np.atleast_1d(np.asarray(z, dtype=float))
                                         for z in (rp, e, mu, r)])
    p = rp * (1 + e)
    cosf = np.clip((p / r - 1) / e, -1, 1)
    f = np.arccos(cosf) * (-1 if incoming else 1)
    rhat = np.stack([np.cos(f), np.sin(f), np.zeros_like(f)], axis=-1)
    that = np.stack([-np.sin(f), np.cos(f), np.zeros_like(f)], axis=-1)
    vfac = np.sqrt(mu / p)
    vr = vfac * e * np.sin(f)
    vt = vfac * (1 + e * np.cos(f))
    return r[:, None] * rhat, vr[:, None] * rhat + vt[:, None] * that, f


def fibonacci_sphere(n):
    """n nearly equal-area points on the unit sphere (Fibonacci lattice); returns the
    orientation angles (theta from +x, varphi from +y in the y-z plane)."""
    k = np.arange(n) + 0.5
    cth = 1 - 2 * k / n
    golden = np.pi * (3 - np.sqrt(5))
    az = golden * k
    theta = np.arccos(cth)
    varphi = np.mod(az, 2 * np.pi)
    return theta, varphi
