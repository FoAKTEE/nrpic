"""Relaxation of a two-temperature start (SPEC.md section 5).

Two populations of the same particle species (same physical mass m = 1), number
densities n1, n2, Maxwell-Juttner at theta1, theta2, at rest, uniform in space. Only
collisions between the populations exchange energy between them. For isotropic elastic
scattering of equal masses the direction average of the post-collision energy of either
particle is (E_a + E_b)/2 (exact, SPEC.md section 3), so the exact initial rate is

    d e_1/dt = n1 n2 sigma < v_Mol (E_2 - E_1)/2 >_{MJ(theta1) x MJ(theta2)},

and d theta_1/dt = (d e_1/dt) / (n1 c_v(theta1)). Non-relativistic closed form
(derived in SPEC.md section 5; valid for any ratio theta1/theta2 at t = 0):

    d(T1 - T2)/dt = -(4/3) sqrt(2/pi) (n1 + n2) sigma sqrt((T1 + T2)/m) (T1 - T2).

The final equilibrium follows from energy conservation:
n1 <W>(theta1) + n2 <W>(theta2) = (n1 + n2) <W>(theta_eq).
The e-folding time of T1 - T2 is not exact beyond t = 0 (the populations leave the
Maxwell-Juttner form); `two_mj_model` integrates the model in which they keep it, as a
guide for the length of the runs, not as a pass criterion.
"""
import numpy as np
from scipy import integrate

import mj
import kinematics as kin
import rate

__all__ = ["dT_rate_nr", "de1_dt", "de1_dt_mc", "dtheta_dt", "theta_eq",
           "relaxation_time", "two_mj_model"]


def dT_rate_nr(n1, n2, sigma_tot, T1, T2, m=1.0):
    """Non-relativistic d(T1 - T2)/dt at t = 0 (T in units of m c^2 when m = 1)."""
    return -(4.0 / 3.0) * np.sqrt(2.0 / np.pi) * (n1 + n2) * sigma_tot * \
        np.sqrt((T1 + T2) / m) * (T1 - T2)


def de1_dt(n1, n2, sigma_tot, theta1, theta2, nquad=400):
    """Exact initial d e_1/dt (energy of population 1 per volume, units m = 1) by
    two-dimensional quadrature with the angular integral in closed form."""
    ua, wa = rate._speed_rule(theta1, nquad)
    ub, wb = rate._speed_rule(theta2, nquad)
    A, B = np.meshgrid(ua, ub, indexing="ij")
    WA, WB = np.sqrt(1 + A * A), np.sqrt(1 + B * B)
    ang = rate._angular_sqrt(A, B, WA, WB)          # <sqrt(g^2-1)>_mu
    # (W_B - W_A) without cancellation
    dW = (B - A) * (B + A) / (WA + WB)
    integrand = ang / (WA * WB) * 0.5 * dW
    return n1 * n2 * sigma_tot * float(np.einsum("i,j,ij->", wa, wb, integrand))


def de1_dt_mc(n1, n2, sigma_tot, theta1, theta2, npairs, rng, scatter=True):
    """Monte Carlo collision integral for d e_1/dt: independent pairs from the two
    distributions, weight v_Mol; with scatter=True the energy change is taken from the
    oracle with one random direction per pair (tests the kernel average as well),
    otherwise the exact direction average (E_b - E_a)/2. Returns (mean, standard error).
    This is a quadrature of the collision integral at t = 0, not a time evolution."""
    ua = mj.sample_u(npairs, theta1, rng)
    ub = mj.sample_u(npairs, theta2, rng)
    v = kin.vmol(ua, ub)
    Wa = kin.W_of(ua)
    if scatter:
        n = mj.isotropic_dirs(npairs, rng)
        ua2, _ = kin.scatter(ua, ub, 1.0, 1.0, n)
        a2 = np.sum(ua2 * ua2, -1)
        a1 = np.sum(ua * ua, -1)
        dE = (a2 - a1) / (kin.W_of(ua2) + Wa)
    else:
        Wb = kin.W_of(ub)
        dE = 0.5 * (np.sum(ub * ub, -1) - np.sum(ua * ua, -1)) / (Wa + Wb)
    x = v * dE
    fac = n1 * n2 * sigma_tot
    return fac * float(x.mean()), fac * float(x.std(ddof=1) / np.sqrt(npairs))


def dtheta_dt(n1, n2, sigma_tot, theta1, theta2):
    """(d theta1/dt, d theta2/dt) at t = 0 (exact)."""
    r = de1_dt(n1, n2, sigma_tot, theta1, theta2)
    return r / (n1 * mj.c_v(theta1)), -r / (n2 * mj.c_v(theta2))


def theta_eq(n1, n2, theta1, theta2):
    k = (n1 * mj.mean_kinetic(theta1) + n2 * mj.mean_kinetic(theta2)) / (n1 + n2)
    return mj.theta_from_kinetic(k)


def relaxation_time(n1, n2, sigma_tot, theta1, theta2):
    """tau = (T1 - T2) / |d(T1 - T2)/dt| at t = 0."""
    d1, d2 = dtheta_dt(n1, n2, sigma_tot, theta1, theta2)
    return (theta1 - theta2) / abs(d1 - d2)


def two_mj_model(n1, n2, sigma_tot, theta1, theta2, t_end, npts=200):
    """Temperatures if both populations stayed Maxwell-Juttner (guide only)."""
    def rhs(t, y):
        d1, d2 = dtheta_dt(n1, n2, sigma_tot, y[0], y[1])
        return [d1, d2]
    t = np.linspace(0.0, t_end, npts)
    sol = integrate.solve_ivp(rhs, (0.0, t_end), [theta1, theta2], t_eval=t,
                              rtol=1e-8, atol=1e-14 * max(theta1, theta2))
    return sol.t, sol.y
