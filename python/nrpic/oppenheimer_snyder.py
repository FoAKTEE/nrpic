"""Oppenheimer-Snyder dust ball (Wu & Most, Sec. IV B and App. A).

Time-symmetric slice in isotropic Cartesian coordinates (Staley et al. 2012):

    rbar_0 = (R_0/2) (1 - M/R_0 + sqrt(1 - 2M/R_0))                     (os-isotropic-radius)
    psi^2  = (1 + sqrt(1 - 2M/R_0)) rbar_0 R_0^2 / (2 rbar_0^3 + M r^2), r <= rbar_0  (os-psi-interior)
    psi^2  = (1 + M/(2r))^2,                                           r >  rbar_0  (os-psi-exterior)

with uniform rest-mass (= energy) density rho_0 = 3M/(4 pi R_0^3), unit lapse,
zero shift and K_ij = 0. Writing psi = c (1 + r^2/a^2)^(-1/2), a^2 = 2 rbar_0^3/M,
c^2 = (1 + sqrt(1 - 2M/R_0)) R_0^2 / (2 rbar_0^2), the rest mass inside r is

    M_rest(<r) = 4 pi rho_0 c^6 a^3 [theta/8 - sin(4 theta)/32],  theta = arctan(r/a).

Cycloid (proper time tau along the dust worldlines, 0 <= eta < pi):

    R/R_0 = (1 + cos eta)/2,  tau = sqrt(R_0^3/(8M)) (eta + sin eta),
    rho/rho_0 = (2/(1 + cos eta))^3,

and the Staley et al. lower bound for 1+log slicing with initially unit lapse:
alpha_c >= alpha_LL(tau_c) = 1 + 6 ln[R(tau_c)/R_0].

Stationary 1+log trumpet of Schwarzschild (Hannam et al. 2008), as a function
of the areal radius R. For a stationary slice with the Killing time as
evolution vector, alpha^2 = 1 - 2M/R + (n^R)^2, K = -R^(-2) d(R^2 n^R)/dR and
beta^R = -alpha n^R. The stationary 1+log condition
0 = d_t alpha = beta^R d_R alpha - 2 alpha K integrates to R^2 n^R = C e^(alpha/2), so

    alpha^2 = 1 - 2M/R + C^2 e^alpha / R^4.

Regularity at the critical point (where both partial derivatives of
F = alpha^2 - 1 + 2M/R - C^2 e^alpha/R^4 vanish) gives alpha_crit = M/(4 R_crit),
with u = M/R_crit the positive root of u^2 + 24 u - 16 = 0, and
C^2 = 2 alpha_crit R_crit^4 exp(-alpha_crit). Numerically R_crit = 1.540569 M,
alpha_crit = 0.162278, C = 1.246725 M^2, and alpha = 0 at R_0 = 1.312408 M.
The trumpet takes the smaller root of F(., R) for R < R_crit and the larger one
for R > R_crit (F is convex in alpha on [0, 1] for R >= R_0). This is the
stationary solution of d_t alpha = beta^i d_i alpha - 2 alpha K (1+log with the
advection term), the variant used in moving-puncture codes.
"""

import math

import numpy as np
from scipy.optimize import brentq

__all__ = [
    "isotropic_radius", "rho0", "psi", "rest_mass_inside", "rest_mass",
    "F", "Finv", "eta_of_tau", "cycloid_R", "cycloid_tau", "cycloid_rho",
    "collapse_time", "staley_lower_bound", "trumpet_constants",
    "trumpet_lapse", "table_arrays", "write_table", "summary",
]


def isotropic_radius(R0=5.0, M=1.0):
    """Isotropic radius of the surface, Eq. os-isotropic-radius."""
    return 0.5 * R0 * (1.0 - M / R0 + math.sqrt(1.0 - 2.0 * M / R0))


def rho0(R0=5.0, M=1.0):
    """Initial uniform rest-mass density 3M/(4 pi R_0^3)."""
    return 3.0 * M / (4.0 * math.pi * R0 ** 3)


def _ac(R0, M):
    rb0 = isotropic_radius(R0, M)
    a2 = 2.0 * rb0 ** 3 / M
    c2 = (1.0 + math.sqrt(1.0 - 2.0 * M / R0)) * R0 ** 2 / (2.0 * rb0 ** 2)
    return rb0, math.sqrt(a2), math.sqrt(c2)


def psi(r, R0=5.0, M=1.0):
    """Conformal factor at isotropic radius r (Eqs. os-psi-interior/exterior)."""
    r = np.abs(np.asarray(r, dtype=float))
    rb0 = isotropic_radius(R0, M)
    s = math.sqrt(1.0 - 2.0 * M / R0)
    inner = np.sqrt((1.0 + s) * rb0 * R0 ** 2 / (2.0 * rb0 ** 3 + M * r * r))
    outer = 1.0 + M / (2.0 * np.where(r > rb0, r, 1.0))
    return np.where(r <= rb0, inner, outer)


def rest_mass_inside(r, R0=5.0, M=1.0):
    """Rest mass inside isotropic radius r: int rho_0 psi^6 d^3x (closed form)."""
    rb0, a, c = _ac(R0, M)
    r = np.minimum(np.abs(np.asarray(r, dtype=float)), rb0)
    th = np.arctan(r / a)
    return 4.0 * math.pi * rho0(R0, M) * c ** 6 * a ** 3 * (th / 8.0 - np.sin(4.0 * th) / 32.0)


def rest_mass(R0=5.0, M=1.0):
    """Total rest mass M_rest = int_{r<=rbar_0} rho_0 psi^6 d^3x."""
    return float(rest_mass_inside(isotropic_radius(R0, M), R0, M))


def F(r, R0=5.0, M=1.0):
    """Cumulative rest-mass fraction inside isotropic radius r."""
    return rest_mass_inside(r, R0, M) / rest_mass(R0, M)


def Finv(U, R0=5.0, M=1.0, iters=60):
    """Inverse of F by vectorised bisection on [0, rbar_0]."""
    U = np.asarray(U, dtype=float)
    lo = np.zeros_like(U)
    hi = np.full_like(U, isotropic_radius(R0, M))
    Mr = rest_mass(R0, M)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        below = rest_mass_inside(mid, R0, M) / Mr < U
        lo = np.where(below, mid, lo)
        hi = np.where(below, hi, mid)
    return 0.5 * (lo + hi)


# ----------------------------------------------------------------------------
# cycloid and Staley bound
# ----------------------------------------------------------------------------
def collapse_time(R0=5.0, M=1.0):
    """Proper time to the singularity, pi sqrt(R_0^3/(8M))."""
    return math.pi * math.sqrt(R0 ** 3 / (8.0 * M))


def cycloid_tau(eta, R0=5.0, M=1.0):
    return math.sqrt(R0 ** 3 / (8.0 * M)) * (np.asarray(eta, float) + np.sin(eta))


def eta_of_tau(tau, R0=5.0, M=1.0, iters=64):
    """Conformal time eta in [0, pi] with tau(eta) = tau (bisection; tau is
    clipped to [0, tau_coll])."""
    T = np.clip(np.asarray(tau, dtype=float) / math.sqrt(R0 ** 3 / (8.0 * M)), 0.0, math.pi)
    lo = np.zeros_like(T)
    hi = np.full_like(T, math.pi)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        below = mid + np.sin(mid) < T
        lo = np.where(below, mid, lo)
        hi = np.where(below, hi, mid)
    return 0.5 * (lo + hi)


def cycloid_R(tau, R0=5.0, M=1.0):
    """Surface areal radius R(tau) (Eq. os-cycloid-radius)."""
    return R0 * 0.5 * (1.0 + np.cos(eta_of_tau(tau, R0, M)))


def cycloid_rho(tau, R0=5.0, M=1.0):
    """Uniform interior rest-mass density rho(tau) (Eq. os-cycloid-time-density)."""
    eta = eta_of_tau(tau, R0, M)
    return rho0(R0, M) * (2.0 / (1.0 + np.cos(eta))) ** 3


def staley_lower_bound(tau_c, R0=5.0, M=1.0):
    """alpha_LL = 1 + 6 ln[R(tau_c)/R_0] (Eq. os-staley-lapse)."""
    with np.errstate(divide="ignore"):
        return 1.0 + 6.0 * np.log(cycloid_R(tau_c, R0, M) / R0)


# ----------------------------------------------------------------------------
# stationary 1+log trumpet
# ----------------------------------------------------------------------------
def trumpet_constants(M=1.0):
    """Return dict(C, C2, R_crit, alpha_crit, R0) of the 1+log trumpet."""
    u = -12.0 + math.sqrt(160.0)
    Rc = M / u
    ac = u / 4.0
    C2 = 2.0 * ac * Rc ** 4 * math.exp(-ac)
    R0 = brentq(lambda R: R ** 4 - 2.0 * M * R ** 3 + C2, 0.5 * M, Rc, xtol=1e-15)
    return dict(C=math.sqrt(C2), C2=C2, R_crit=Rc, alpha_crit=ac, R0=R0)


def trumpet_lapse(R, M=1.0, iters=64):
    """Lapse of the stationary 1+log trumpet at areal radius R (NaN for R < R_0)."""
    R = np.asarray(R, dtype=float)
    k = trumpet_constants(M)
    kk = k["C2"] / R ** 4
    f = 1.0 - 2.0 * M / R

    def bisect(fun, lo, hi):
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            neg = fun(mid) < 0
            lo, hi = np.where(neg, mid, lo), np.where(neg, hi, mid)
        return 0.5 * (lo + hi)

    zero = np.zeros_like(R)
    one = np.ones_like(R)
    # minimum of F(., R): 2 alpha = kk e^alpha (increasing function of alpha)
    amin = bisect(lambda a: 2.0 * a - kk * np.exp(a), zero, one)
    Ffun = lambda a: a * a - kk * np.exp(a) - f
    # upper root (F increasing on [amin, 1]); lower root (F decreasing on [0, amin])
    up = bisect(Ffun, amin, one)
    lowr = bisect(lambda a: -Ffun(a), zero, amin)
    a = np.where(R >= k["R_crit"], up, lowr)
    a = np.where(Ffun(amin) >= 0, amin, a)          # at the critical point
    return np.where(R >= k["R0"], a, np.nan)


# ----------------------------------------------------------------------------
# radial table
# ----------------------------------------------------------------------------
def table_arrays(R0=5.0, M=1.0, n_matter=4000, rmax_factor=1.5):
    """Uniform (r, u = psi - 1, alpha = 1) table, dr = rbar_0/n_matter."""
    rb0 = isotropic_radius(R0, M)
    dr = rb0 / n_matter
    n = int(math.ceil(rmax_factor * n_matter)) + 1
    r = dr * np.arange(n)
    return r, psi(r, R0, M) - 1.0, np.ones_like(r)


def summary(R0=5.0, M=1.0):
    k = trumpet_constants(M)
    return dict(model="oppenheimer_snyder", M_ADM=M, R0_areal=R0,
                rbar0=isotropic_radius(R0, M), rho0=rho0(R0, M),
                M_rest=rest_mass(R0, M), psi_c=float(psi(0.0, R0, M)),
                psi_s=1.0 + M / (2.0 * isotropic_radius(R0, M)),
                tau_collapse=collapse_time(R0, M), lapse_initial=1.0,
                trumpet_C=k["C"], trumpet_R0=k["R0"])


def write_table(path, R0=5.0, M=1.0, n_matter=4000, rmax_factor=1.5):
    """Write the `.tab` table. The alpha column is the initial lapse, 1; the
    generator must not switch to the Schwarzschild lapse outside the table."""
    from . import io as nio
    r, u, a = table_arrays(R0, M, n_matter, rmax_factor)
    hdr = ["Oppenheimer-Snyder time-symmetric slice (Staley et al. isotropic form)",
           "columns: r (isotropic)  u = psi - 1  alpha = 1 (initial lapse is unity everywhere;",
           "  do not use the tabulated-lapse vacuum continuation for this model)"]
    hdr += [f"{kk} = {v!r}" for kk, v in summary(R0, M).items()]
    nio.write_tab(path, r, u, a, header=hdr)
    return r, u, a
