"""Exact references for test particles around a Schwarzschild black hole of mass M in
Cartesian Kerr-Schild coordinates (the coordinates of `nrpic_geodesic`, `metric = mesh` or
`kerr_schild` with spin 0). Reference solutions only (decision 0010).

Metric (G = c = 1, q = 2M/r, n^i = x^i/r):
    alpha = (1 + q)^(-1/2),  beta^i = q/(1 + q) n^i,  gamma_ij = delta_ij + q n_i n_j.
A geodesic has conserved E = -u_t = alpha W - beta^i u_i and L = |x x u| (u_i covariant);
radial motion: (dr/dtau)^2 = E^2 - V(r), V = (1 - q)(1 + L^2/r^2). Kerr-Schild time
t = t_S + 2M ln|r/2M - 1|, so along the orbit
    ingoing:  dt/dr = -[E^2 (1 + q) + q^2 (1 + L^2/r^2)] / (s (q s + E)),  s = sqrt(E^2 - V)
    outgoing: dt/dr = [E/s + q]/(1 - q)
(the ingoing form is the regular rewriting of [q - E/s]/(1 - q); it is finite at r = 2M).
Every time is a one-dimensional quadrature; a turning point is integrated through the
substitution r = r_t -+ w^2.
"""
import math

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq


def ks_metric(x, M=1.0):
    x = np.atleast_2d(np.asarray(x, float))
    r = np.linalg.norm(x, axis=1)
    n = x / r[:, None]
    q = 2.0 * M / r
    alpha = 1.0 / np.sqrt(1.0 + q)
    beta = (q / (1.0 + q))[:, None] * n
    gam = np.eye(3)[None, :, :] + q[:, None, None] * n[:, :, None] * n[:, None, :]
    return alpha, beta, gam, r, n


def invariants(x, u, M=1.0):
    """E, L, u_r (covariant radial component n^i u_i), r of particles at x with u_i."""
    x = np.atleast_2d(np.asarray(x, float))
    u = np.atleast_2d(np.asarray(u, float))
    alpha, beta, gam, r, n = ks_metric(x, M)
    gi = np.linalg.inv(gam)
    W = np.sqrt(1.0 + np.einsum("pi,pij,pj->p", u, gi, u))
    E = alpha * W - np.einsum("pi,pi->p", beta, u)
    L = np.linalg.norm(np.cross(x, u), axis=1)
    ur = np.einsum("pi,pi->p", n, u)
    return E, L, ur, r


def alpha_ks(r, M=1.0):
    return 1.0 / np.sqrt(1.0 + 2.0 * M / np.asarray(r, float))


def r_of_alpha(alpha, M=1.0):
    """Radius where the Kerr-Schild lapse equals alpha (alpha < 1)."""
    return 2.0 * M / (1.0 / alpha ** 2 - 1.0)


def _s2(r, E, L, M):
    q = 2.0 * M / r
    return E * E - (1.0 - q) * (1.0 + L * L / (r * r))


def turning_points(E, L, M=1.0):
    """Real positive roots of E^2 - V(r): (E^2 - 1) r^3 + 2M r^2 - L^2 r + 2M L^2 = 0."""
    c = [E * E - 1.0, 2.0 * M, -L * L, 2.0 * M * L * L]
    if abs(c[0]) < 1e-15:
        c = c[1:]
    rt = np.roots(c)
    rt = np.real(rt[(np.abs(np.imag(rt)) < 1e-9) & (np.real(rt) > 0)])
    return np.sort(rt)


def _s2_fact(r, E, L, M, roots):
    """E^2 - V(r) = P(r)/r^3 with P(r) = (E^2-1) r^3 + 2M r^2 - L^2 r + 2M L^2, written as a
    product over the known turning points so that no cancellation occurs near them."""
    a = E * E - 1.0
    if len(roots) == 2 and a < 0:
        ra, rp = max(roots), min(roots)
        r3 = 2.0 * M / (1.0 - E * E) - ra - rp
        return (-a) * (ra - r) * (r - rp) * (r - r3) / r ** 3
    if len(roots) == 1:
        rt = roots[0]
        q1 = 2.0 * M + a * rt
        q0 = -L * L + rt * q1
        return (r - rt) * (a * r * r + q1 * r + q0) / r ** 3
    return _s2(r, E, L, M)


def _dt_in(r, s, E, L, M):
    q = 2.0 * M / r
    return (E * E * (1.0 + q) + q * q * (1.0 + L * L / (r * r))) / (s * (q * s + E))


def _dt_out(r, s, E, L, M):
    q = 2.0 * M / r
    return (E / s + q) / (1.0 - q)


def _dtau(r, s, E, L, M):
    return 1.0 / s


def _leg(f, r_hi, r_lo, E, L, M, top_turn, bottom_turn, roots=()):
    """Integral of f(r, s) over [r_lo, r_hi], s = (E^2 - V)^(1/2) from the factored form;
    a turning point at an end is integrated through r = r_t -+ w^2 (integrand times 2w)."""
    if r_hi <= r_lo:
        return 0.0
    sf = lambda r: math.sqrt(max(_s2_fact(r, E, L, M, roots), 0.0))
    if top_turn and bottom_turn:
        mid = 0.5 * (r_hi + r_lo)
        return (_leg(f, r_hi, mid, E, L, M, True, False, roots)
                + _leg(f, mid, r_lo, E, L, M, False, True, roots))
    if top_turn or bottom_turn:
        W = math.sqrt(r_hi - r_lo)
        sign, base = (-1.0, r_hi) if top_turn else (1.0, r_lo)

        def g(w):
            w = max(w, 1e-12 * W)
            r = base + sign * w * w
            return 2.0 * w * f(r, sf(r), E, L, M)
        return quad(g, 0.0, W, epsabs=0.0, epsrel=1e-10, limit=400)[0]
    return quad(lambda r: f(r, sf(r), E, L, M), r_lo, r_hi, epsabs=0.0, epsrel=1e-10,
                limit=400)[0]


def _ds2dr(r, E, L, M, h=1e-7):
    return (_s2(r + h, E, L, M) - _s2(r - h, E, L, M)) / (2 * h)


class Orbit:
    """Exact orbit of a test particle that starts at r0 with E, L and radial velocity
    sign `sgn` (-1 ingoing, +1 outgoing, 0 at a turning point: then r0 is the apocentre
    if E^2 - V decreases inward, the pericentre otherwise). Times are Kerr-Schild."""

    def __init__(self, r0, E, L, ur, M=1.0):
        self.r0, self.E, self.L, self.M = float(r0), float(E), float(L), float(M)
        tp = turning_points(self.E, self.L, self.M)
        self.at_turn = abs(_s2(self.r0, self.E, self.L, self.M)) < 1e-9
        if self.at_turn:
            # put the start exactly on the turning point (E changes by rounding only)
            self.E = math.sqrt((1.0 - 2.0 * self.M / self.r0)
                               * (1.0 + self.L ** 2 / self.r0 ** 2))
            sgn = -1 if _ds2dr(self.r0, self.E, self.L, self.M) < 0 else +1   # apocentre: E^2 - V grows inward
        else:
            sgn = -1 if ur < 0 else +1
        if sgn > 0:
            raise NotImplementedError("outgoing starts are not used in these tests")
        below = tp[tp < self.r0 * (1 - 1e-9)]
        below = below[below > 2.0 * self.M]
        self.captured = below.size == 0
        self.rp = None
        if not self.captured:
            rp = float(below.max())
            f = lambda r: _s2(r, self.E, self.L, self.M)
            lo, hi = rp * (1 - 1e-6), rp * (1 + 1e-6)
            if f(lo) * f(hi) < 0:
                rp = brentq(f, lo, hi, xtol=1e-15, rtol=1e-15)
            self.rp = rp
        if not self.captured:
            above = tp[tp > self.rp * (1 + 1e-9)]
            self.ra = float(above.min())          # apocentre (= r0 when starting there)
            if self.at_turn and abs(self.ra - self.r0) < 1e-6 * self.r0:
                self.ra = self.r0
        if self.captured:
            self.roots = (self.r0,) if self.at_turn else ()
        else:
            self.roots = (self.ra, self.rp)

    def t_in(self, r):
        """Kerr-Schild time of the first inward passage through r (r < r0)."""
        if not self.captured and r < self.rp:
            return math.nan
        bottom = (not self.captured) and abs(r - self.rp) < 1e-12
        return _leg(_dt_in, self.r0, r, self.E, self.L, self.M, self.at_turn, bottom, self.roots)

    def tau_in(self, r):
        if not self.captured and r < self.rp:
            return math.nan
        bottom = (not self.captured) and abs(r - self.rp) < 1e-12
        return _leg(_dtau, self.r0, r, self.E, self.L, self.M, self.at_turn, bottom, self.roots)

    def crossings(self, rs, t_end):
        """Inward and outward passage times through the sphere rs up to t_end."""
        if self.captured:
            return ([self.t_in(rs)] if rs < self.r0 else []), []
        if not (self.rp < rs < self.ra):
            return [], []
        if not self.at_turn or abs(self.r0 - self.ra) > 1e-9 * self.ra:
            raise NotImplementedError("bound orbits must start at their apocentre")
        T_in = _leg(_dt_in, self.ra, self.rp, self.E, self.L, self.M, True, True, self.roots)
        T_out = _leg(_dt_out, self.ra, self.rp, self.E, self.L, self.M, True, True, self.roots)
        a_in = _leg(_dt_in, self.ra, rs, self.E, self.L, self.M, True, False, self.roots)
        a_out = _leg(_dt_out, rs, self.rp, self.E, self.L, self.M, False, True, self.roots)
        P = T_in + T_out
        ins, outs = [], []
        k = 0
        while k * P + a_in <= t_end:
            ins.append(k * P + a_in)
            if k * P + T_in + a_out <= t_end:
                outs.append(k * P + T_in + a_out)
            k += 1
        return ins, outs

    def period(self):
        if self.captured:
            return math.nan
        return (_leg(_dt_in, self.ra, self.rp, self.E, self.L, self.M, True, True, self.roots)
                + _leg(_dt_out, self.ra, self.rp, self.E, self.L, self.M, True, True, self.roots))


def static_u(x, M=1.0):
    """Covariant u_i of a particle at rest relative to the static observer (u^r = 0,
    no angular motion): u_r = q/sqrt(1 - q) along n."""
    x = np.atleast_2d(np.asarray(x, float))
    r = np.linalg.norm(x, axis=1)
    q = 2.0 * M / r
    return (q / np.sqrt(1.0 - q))[:, None] * x / r[:, None]


def radial_u_for_energy(x, E, M=1.0):
    """Covariant u_i of an ingoing radial geodesic with energy E at x (Kerr-Schild):
    solves g^tt E^2 - 2 g^tr E u_r + g^rr u_r^2 = -1 with g^tt = -(1+q), g^tr = q,
    g^rr = 1 - q, ingoing root."""
    x = np.atleast_2d(np.asarray(x, float))
    r = np.linalg.norm(x, axis=1)
    q = 2.0 * M / r
    E = np.broadcast_to(np.asarray(E, float), r.shape)
    a, b, c = 1.0 - q, -2.0 * q * E, 1.0 - (1.0 + q) * E * E
    disc = np.sqrt(b * b - 4 * a * c)
    roots = np.stack([(-b - disc) / (2 * a), (-b + disc) / (2 * a)], axis=1)
    # ingoing: u^r = g^rt u_t + g^rr u_r = -q E + (1 - q) u_r < 0
    urup = -q[:, None] * E[:, None] + (1 - q)[:, None] * roots
    pick = np.where(urup[:, 0] < 0, roots[:, 0], roots[:, 1])
    return pick[:, None] * x / r[:, None]
