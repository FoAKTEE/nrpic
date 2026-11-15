"""Collision rate of a Maxwell-Juttner gas for a constant total cross-section.

Per-particle collision rate in the rest frame of the gas (SPEC.md section 2):

    Gamma = n sigma_tot <v_Mol> = rho_0 (sigma/m) <v_Mol>,      rho_0 = n m,

with the thermal average of the Moller speed

    <v_Mol>(theta) = 4 K3(2 zeta) / (zeta K2(zeta)^2),          zeta = 1/theta,

obtained from the one-dimensional form of the thermal average of sigma v_Mol (Gondolo &
Gelmini 1991, their eq. 3.8 [BACKGROUND, not re-read]) for constant sigma with
int_a^inf x^2 K1 = a^2 K2(a) and int_a^inf x^4 K1 = a^4 K2(a) + 2 a^3 K3(a). The
derivation is in SPEC.md; tests/test_rate.py checks it against a direct Monte Carlo
average over sampled pairs, which does not use the one-dimensional form.

Limits: non-relativistic <v_Mol> = (4/sqrt(pi)) sqrt(theta) (1 - 25 theta/16 + ...),
i.e. Gamma = a rho sigma v with a = sqrt(16/pi), v = sqrt(T/m) (Balberg, Shapiro &
Inagaki, astro-ph/0110561, SIDMGT_Xiv2.tex lines 309-323); ultra-relativistic
<v_Mol> -> 1 (= c).

The number of collision events per unit volume and time is R = n^2 sigma <v_Mol> / 2
(each event involves two particles of the same species).
"""
import numpy as np
from scipy import special, integrate

import mj
import kinematics as kin

__all__ = ["vmol_mean", "vmol_mean_integral", "vmol_mean_nr", "rate_per_particle",
           "events_per_volume_time", "vmol_mean_mc", "vmol_mean_two_temperatures"]


def vmol_mean(theta):
    """<v_Mol> = 4 K3(2 zeta)/(zeta K2(zeta)^2); exponential scaling cancels exactly."""
    z = 1.0 / np.asarray(theta, dtype=float)
    return 4.0 * special.kve(3, 2.0 * z) / (z * special.kve(2, z) ** 2)


def vmol_mean_nr(theta):
    """First two terms of the non-relativistic expansion."""
    theta = np.asarray(theta, dtype=float)
    return 4.0 / np.sqrt(np.pi) * np.sqrt(theta) * (1.0 - 25.0 * theta / 16.0)


def vmol_mean_integral(theta):
    """The one-dimensional thermal average evaluated by quadrature (no closed form):
    <v> = (1 / (4 zeta^4 K2(zeta)^2)) int_{2 zeta}^inf (x^4 - 4 zeta^2 x^2) K1(x) dx."""
    z = 1.0 / float(theta)
    # scaled: K1(x) = kve(1,x) e^-x, K2(z)^2 = kve(2,z)^2 e^-2z; substitute x = 2z + y
    f = lambda y: ((2 * z + y) ** 4 - 4 * z * z * (2 * z + y) ** 2) * \
        special.kve(1, 2 * z + y) * np.exp(-y)
    val, _ = integrate.quad(f, 0.0, np.inf, epsabs=0.0, epsrel=1e-13, limit=400)
    return val / (4.0 * z ** 4 * special.kve(2, z) ** 2)


def rate_per_particle(rho0, sigma_per_mass, theta):
    """Gamma = rho_0 (sigma/m) <v_Mol> (rest frame of the gas)."""
    return rho0 * sigma_per_mass * vmol_mean(theta)


def events_per_volume_time(n, sigma_tot, theta):
    """R = n^2 sigma <v_Mol> / 2 (rest frame)."""
    return 0.5 * n * n * sigma_tot * vmol_mean(theta)


def vmol_mean_mc(theta, npairs, rng, theta_b=None):
    """Direct Monte Carlo average of v_Mol over independent pairs (a at theta, b at
    theta_b, default theta). Returns (mean, standard error)."""
    tb = theta if theta_b is None else theta_b
    ua = mj.sample_u(npairs, theta, rng)
    ub = mj.sample_u(npairs, tb, rng)
    v = kin.vmol(ua, ub)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(npairs))


def vmol_mean_two_temperatures(theta_a, theta_b):
    """<v_Mol> between two Maxwell-Juttner populations at rest (theta_a, theta_b), by a
    two-dimensional quadrature over |u_a|, |u_b| with the angular integral in closed form:
    (1/2) int_{-1}^{1} sqrt(g^2-1) dmu = [F(g+) - F(g-)] / (2 a b), F(g) = (g sqrt(g^2-1)
    - acosh g)/2, g+- = W_a W_b +- a b."""
    sa, sb = mj.Sampler(theta_a), mj.Sampler(theta_b)
    qa, wa = _speed_rule(theta_a)
    qb, wb = _speed_rule(theta_b)
    A, B = np.meshgrid(qa, qb, indexing="ij")
    WA, WB = np.sqrt(1 + A * A), np.sqrt(1 + B * B)
    ang = _angular_sqrt(A, B, WA, WB)
    integrand = ang / (WA * WB)
    return float(np.einsum("i,j,ij->", wa, wb, integrand))


def _angular_sqrt(a, b, Wa, Wb):
    """(1/2) int_{-1}^{1} sqrt(g^2 - 1) dmu, g = Wa Wb - a b mu, robust for small a b."""
    gm1_plus = kin.gamma_rel_m1(np.stack([a, 0 * a, 0 * a], -1),
                                np.stack([-b, 0 * b, 0 * b], -1))
    gm1_minus = kin.gamma_rel_m1(np.stack([a, 0 * a, 0 * a], -1),
                                 np.stack([b, 0 * b, 0 * b], -1))

    def F(gm1):
        g = gm1 + 1.0
        sq = np.sqrt(gm1 * (gm1 + 2.0))
        return 0.5 * (g * sq - np.arcsinh(sq))
    ab = a * b
    out = (F(gm1_plus) - F(gm1_minus)) / (2.0 * np.where(ab > 0, ab, 1.0))
    # small ab: the integrand is nearly constant, sqrt(g0^2 - 1) with g0 = Wa Wb
    g0m1 = kin.gamma_rel_m1(np.stack([a, 0 * a, 0 * a], -1),
                            np.stack([0 * b, b, 0 * b], -1))
    small = ab < 1e-6 * np.sqrt(np.maximum(g0m1 * (g0m1 + 2.0), 1e-300))
    return np.where(small, np.sqrt(g0m1 * (g0m1 + 2.0)), out)


def _speed_rule(theta, n=400):
    """Quadrature nodes and weights in |u| for the Maxwell-Juttner speed distribution:
    Gauss-Legendre in s on [0, 9] with u(s) from y = s^2 = zeta (W - 1)."""
    x, w = np.polynomial.legendre.leggauss(n)
    s = 4.5 * (x + 1.0)
    ws = 4.5 * w
    y = s * s
    W = 1.0 + y * theta
    u = np.sqrt(np.maximum(W * W - 1.0, 0.0))
    dens = s * u * W * np.exp(-y)
    norm = np.sum(ws * dens)
    return u, ws * dens / norm
