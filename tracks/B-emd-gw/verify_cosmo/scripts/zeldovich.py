"""Exact Newtonian plane-symmetric reference for the single plane wave (verify_cosmo).

Equations (those of cosmo/newton/pm.py, H0 = 1, a = (1 + tau/2)^2, tau conformal time):

    dx/dtau = p / a,   dp/dtau = -(3/2) d_x lap^-1 delta_N .

In plane symmetry, before any two sheets cross, the force on a sheet is
(3/2) s with s = x - Qt, where Qt = Q + X_cm - L/2 is fixed in time (Q = mass to the
left of the sheet, own mass counted half, over the mean density; X_cm the centre of
mass, which moves only with the total momentum). So each sheet obeys the linear growth
equation d/dtau (a ds/dtau) = (3/2) s exactly, with the solution

    s(a) = A a + B a^(-3/2),    A = 0.6 s0 + 0.4 v0,  B = 0.4 (s0 - v0),

for s0 = s(a = 1) and v0 = a ds/dtau at a = 1 (Zel'dovich, with both modes; exact up to
the first crossing).

Data of cosmo/ic/make_east.py --ratios 1,0,0 (and pm.east_particles with ratios
(1, 0, 0)): at a = 1 the Eulerian density is rho0 (1 + d sin k x) and the velocity
dx/dtau = (d/k) cos k x. Then Q(x) = x + (d/k)(1 - cos k x), X_cm = L/2 - d/k, so
s0 = (d/k) cos k x0 = v0: a pure growing mode. For the fluid element that starts at
x0 (continuum):

    x(x0, a)   = x0 + (a - 1) (d/k) cos k x0,
    v(x0, a)   = dx/dtau = a^(1/2) (d/k) cos k x0,
    rho / rho0 = (1 + d sin k x0) / (1 - (a - 1) d sin k x0)   (Lagrangian density),

first crossing at x0 = L/4 when a = 1 + 1/d. The discrete sheets of a lattice follow
the same law with the mass coordinate of the sheets (sheet_solution below).

Derivation in tracks/B-emd-gw/verify_cosmo/JOURNAL.md (entry "Reference solution").
"""
import numpy as np


def scale_factor(tau):
    return (1.0 + 0.5*tau)**2


def drift_integral(tau):
    """Integral of d tau / a from 0 to tau (H0 = 1)."""
    return 2.0*(1.0 - 1.0/(1.0 + 0.5*tau))


def continuum(x0, a, d, L):
    """Position, velocity dx/dtau and Lagrangian density rho/rho0 of the fluid element
    that starts at x0 (a = 1), for the plane wave of amplitude d in a box of side L."""
    k = 2.0*np.pi/L
    x0 = np.asarray(x0, dtype=float)
    s0 = (d/k)*np.cos(k*x0)
    S = np.sin(k*x0)
    x = x0 + (a - 1.0)*s0
    v = np.sqrt(a)*s0
    rho = (1.0 + d*S)/(1.0 - (a - 1.0)*d*S)
    return x, v, rho


def a_cross_continuum(d):
    return 1.0 + 1.0/d


def eulerian_density(xgrid, a, d, L, nfine=200001):
    """Continuum density rho/rho0 at the Eulerian points xgrid (before crossing), by
    inverting x(x0, a) on a fine grid of x0 (monotone before the crossing)."""
    x0 = np.linspace(0.0, L, nfine, endpoint=False)
    x, _, rho = continuum(x0, a, d, L)
    # unwrap: x(x0) increases monotonically from x(0) to x(0) + L
    order = np.argsort(np.mod(x, L))
    xs = np.mod(x, L)[order]
    rs = rho[order]
    xs = np.concatenate([xs[-1:] - L, xs, xs[:1] + L])
    rs = np.concatenate([rs[-1:], rs, rs[:1]])
    return np.interp(np.mod(xgrid, L), xs, rs)


def sheet_solution(x0, v0, m, L, tau):
    """Exact solution for discrete sheets (1-D arrays: positions in [0, L) at tau = 0,
    velocities dx/dtau at tau = 0, masses) at the conformal times tau (array). Valid
    until the first crossing. Returns x (ntau, nsheet), unwrapped, and v = dx/dtau."""
    x0 = np.asarray(x0, float)
    v0 = np.asarray(v0, float)
    m = np.asarray(m, float)
    order = np.argsort(x0)
    xs, vs, ms = x0[order], v0[order], m[order]
    M = ms.sum()
    Q = (np.cumsum(ms) - 0.5*ms)/M*L
    xcm0 = (ms*xs).sum()/M
    P = (ms*vs).sum()/M
    s0 = xs - Q - xcm0 + 0.5*L
    w0 = vs - P
    A = 0.6*s0 + 0.4*w0
    B = 0.4*(s0 - w0)
    tau = np.atleast_1d(np.asarray(tau, float))
    a = scale_factor(tau)[:, None]
    xcm = xcm0 + P*drift_integral(tau)[:, None]
    x = Q[None, :] + xcm - 0.5*L + A[None, :]*a + B[None, :]*a**-1.5
    v = P/a + np.sqrt(a)*(A[None, :] - 1.5*B[None, :]*a**-2.5)
    inv = np.empty_like(order)
    inv[order] = np.arange(len(order))
    return x[:, inv], v[:, inv]


def first_crossing_a(x_of_a, a):
    """First scale factor at which neighbouring sheets (in the order of their initial
    positions) swap, from positions x_of_a (na, nsheet, unwrapped, sheets ordered by
    initial position), with linear interpolation between records; nan if none."""
    gap = np.diff(x_of_a, axis=1)
    neg = (gap <= 0.0).any(axis=1)
    if not neg.any():
        return np.nan
    i = int(np.argmax(neg))
    if i == 0:
        return float(a[0])
    j = int(np.argmin(gap[i]))
    g0, g1 = gap[i - 1, j], gap[i, j]
    return float(a[i - 1] + (a[i] - a[i - 1])*g0/(g0 - g1))
