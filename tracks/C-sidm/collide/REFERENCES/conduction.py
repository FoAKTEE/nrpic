"""Heat conduction between two reservoirs at the long and the short mean-free-path end
(SPEC.md section 6). Units c = k_B = m = 1; theta = T/m; sigma = sigma_tot.

Long mean free path (Knudsen number lambda/L >> 1): free molecular transport.
  One-sided fluxes of a Maxwell-Juttner gas through a plane (derived in SPEC.md 6.1):
      Phi_N = n theta (1 + theta) / (2 kve(2, zeta)),
      Phi_E = n theta (1 + 3 theta + 3 theta^2) / (2 kve(2, zeta)),
  limits n sqrt(theta/(2 pi)) and n/4 (number), n theta... and 3 n theta/4 (energy).
  Two half-space reservoirs (n1, theta1 | n2, theta2): net fluxes Phi(1) - Phi(2) at the
  plane while the gas is collisionless.
  Periodic box of length L, left slab [0, L/2) at (n1, theta1), right slab at
  (n2, theta2), no collisions: exact particle number and energy in the left slab per
  unit transverse area at any time (`step_collisionless`), from free streaming and the
  direction average of the periodic triangle function (SPEC.md 6.2).

Short mean free path (lambda/L << 1): Fourier conduction q = -kappa grad T.
  Chapman-Enskog conductivity of hard spheres, first approximation, non-relativistic
  (Koda & Shapiro arXiv:1101.3097 sidm1.tex lines 402-417 with b = 25 sqrt(pi)/32;
  arXiv:2010.15132 smbh.tex line 116, kappa ~ 2.1 v/sigma):
      kappa_1 = (75 sqrt(pi)/64) sqrt(theta) / sigma         (k_B = c = m = 1).
  Higher Sonine approximations raise it by about 2.5 percent for hard spheres
  [BACKGROUND: Chapman & Cowling, not re-read; TO VERIFY]. The value implied by
  Balberg et al. (astro-ph/0110561 line 394, b = 25 pi/(32 sqrt 6)) is smaller by
  sqrt(6/pi) = 1.38 (`kappa_bsi`).
  Isobaric entropy mode of wave number k (linear, derived in SPEC.md 6.3, holds
  relativistically to leading order in k lambda): decay rate Gamma = kappa k^2/(n c_p).
  Step in the periodic box at small Knudsen number: odd Fourier modes, each decaying
  with its own rate (`step_diffusive`).
"""
import numpy as np
from scipy import special, integrate

import mj
import rate

__all__ = ["phi_N", "phi_E", "phi_N_quad", "phi_E_quad", "kappa_ce_nr", "kappa_bsi",
           "chi", "mode_rate", "step_collisionless", "step_diffusive",
           "mode_collisionless"]

B_KS = 25.0 * np.sqrt(np.pi) / 32.0             # sidm1.tex line 410
B_BSI = 25.0 * np.pi / (32.0 * np.sqrt(6.0))    # SIDMGT_Xiv2.tex line 394


def phi_N(n, theta):
    z = 1.0 / np.asarray(theta, dtype=float)
    th = 1.0 / z
    return n * th * (1.0 + th) / (2.0 * special.kve(2, z))


def phi_E(n, theta):
    z = 1.0 / np.asarray(theta, dtype=float)
    th = 1.0 / z
    return n * th * (1.0 + 3.0 * th + 3.0 * th * th) / (2.0 * special.kve(2, z))


def _flux_quad(n, theta, power):
    """n int_{u_x > 0} (u_x/W) W^power MJ d^3u = n (1/4) <v W^power>... by quadrature."""
    u, w = rate._speed_rule(theta, 600)
    W = np.sqrt(1 + u * u)
    v = u / W
    # int_0^1 mu dmu / 2 over the half sphere of directions = 1/4
    return n * 0.25 * float(np.sum(w * v * W ** power))


def phi_N_quad(n, theta):
    return _flux_quad(n, theta, 0)


def phi_E_quad(n, theta):
    return _flux_quad(n, theta, 1)


def kappa_ce_nr(theta, sigma_tot, sonine=1.0):
    """First Chapman-Enskog conductivity of hard spheres (times `sonine`)."""
    return sonine * 1.5 * B_KS * np.sqrt(theta) / sigma_tot


def kappa_bsi(theta, sigma_tot):
    return 1.5 * B_BSI * np.sqrt(theta) / sigma_tot


def chi(kappa, n, theta):
    """Thermal diffusivity of the isobaric mode, kappa / (n c_p)."""
    return kappa / (n * mj.c_p(theta))


def mode_rate(kappa, n, theta, k):
    return chi(kappa, n, theta) * k * k


def _G(c, L):
    """int_0^c tri(s) ds, tri the periodic triangle min(s mod L, L - s mod L)."""
    c = np.asarray(c, dtype=float)
    k = np.floor(c / L)
    r = c - k * L
    G0 = np.where(r <= 0.5 * L, 0.5 * r * r, 0.25 * L * L - 0.5 * (L - r) ** 2)
    return k * 0.25 * L * L + G0


def _tri_avg(c, L):
    """Direction average of tri(c mu): G(c)/c (-> c/2 for small c)."""
    c = np.asarray(c, dtype=float)
    small = c < 1e-12 * L
    cs = np.where(small, 1.0, c)
    return np.where(small, 0.5 * c, _G(cs, L) / cs)


def step_collisionless(t, L, n1, theta1, n2, theta2, nquad=800):
    """Exact free-streaming evolution of the step: (N_L, E_L, K_L) per unit transverse
    area in the left slab [0, L/2) at times t (array): number, energy (rest mass
    included), kinetic energy."""
    t = np.atleast_1d(np.asarray(t, dtype=float))
    out = []
    for n, th, sgn in ((n1, theta1, -1.0), (n2, theta2, +1.0)):
        u, w = rate._speed_rule(th, nquad)
        W = np.sqrt(1 + u * u)
        v = u / W
        K = u * u / (W + 1.0)
        T = _tri_avg(v[None, :] * t[:, None], L)          # (nt, nu)
        out.append((sgn * n * (T @ w), sgn * n * (T @ (w * W)), sgn * n * (T @ (w * K))))
    NL0 = n1 * 0.5 * L
    u1, w1 = rate._speed_rule(theta1, nquad)
    W1 = np.sqrt(1 + u1 * u1)
    EL0 = NL0 * float(np.sum(w1 * W1))
    KL0 = NL0 * float(np.sum(w1 * u1 * u1 / (W1 + 1)))
    NL = NL0 + out[0][0] + out[1][0]
    EL = EL0 + out[0][1] + out[1][1]
    KL = KL0 + out[0][2] + out[1][2]
    return NL, EL, KL


def step_diffusive(t, L, X0, Xinf, chi_value, nmodes=2001):
    """Linear diffusive relaxation of a slab quantity X (number, energy) of the step:
    X(t) - X_inf = (X0 - X_inf) (8/pi^2) sum_{odd j} exp(-chi (j k1)^2 t)/j^2."""
    t = np.atleast_1d(np.asarray(t, dtype=float))
    k1 = 2.0 * np.pi / L
    j = np.arange(1, 2 * nmodes, 2, dtype=float)
    S = np.exp(-chi_value * (j[None, :] * k1) ** 2 * t[:, None]) @ (1.0 / j ** 2)
    return Xinf + (X0 - Xinf) * 8.0 / np.pi ** 2 * S


def mode_collisionless(t, k, theta, which="energy", nquad=800):
    """Collisionless (phase-mixing) evolution of the isobaric mode cos(k x): ratio of the
    mode amplitude of the energy density (or number density) at t to its value at 0.
    delta f = eps cos(kx) n [zeta (W - <W>) - 1] MJ; direction average of
    cos(k v mu t) is sin(k v t)/(k v t)."""
    t = np.atleast_1d(np.asarray(t, dtype=float))
    u, w = rate._speed_rule(theta, nquad)
    W = np.sqrt(1 + u * u)
    v = u / W
    g = (W - mj.mean_W(theta)) / theta - 1.0
    wt = w * g * (W if which == "energy" else 1.0)
    x = k * v[None, :] * t[:, None]
    sinc = np.sinc(x / np.pi)
    return (sinc @ wt) / np.sum(wt)
