"""Boltzmann entropy per particle, s = -(1/n) int f ln f d^3u, of isotropic distributions
in the space of four-velocities u (SPEC.md section 7; units c = k_B = m = 1).

Maxwell-Juttner (closed form):
    s_MJ(n, theta) = zeta (<W> - 1) + ln(4 pi kve(2, zeta) / (zeta n)),
which reduces to 3/2 + ln((2 pi theta)^(3/2)/n) for theta -> 0 (Sackur-Tetrode without
the 1 of N!). Of all distributions with the same n and <W>, MJ has the largest s: the
H-theorem test compares s(t) with s(0) (exact, `s_mixture` for a two-temperature start)
and with s_MJ(n, theta_eq).

Estimator from samples (`s_estimate`): histogram in |u| on bins of equal probability
under a reference Maxwell-Juttner distribution, f = n p_b / V_b with V_b the shell
volume, plug-in estimate plus the Miller-Madow correction (M_occupied - 1)/(2 N), and
the standard error sqrt(Var(ln(p_b/V_b))/N). Valid for isotropic distributions only.
"""
import numpy as np
from scipy import integrate, special

import mj
import rate

__all__ = ["s_mj", "s_quad", "s_mixture", "s_estimate"]


def s_mj(n, theta):
    z = 1.0 / np.asarray(theta, dtype=float)
    return mj.mean_kinetic(theta) * z + np.log(4.0 * np.pi * special.kve(2, z) / (z * n))


def s_quad(f, n, umax, args=()):
    """-(1/n) int 4 pi u^2 f ln f du for an isotropic f(u) normalized to n."""
    def g(u):
        fu = f(u, *args)
        return 0.0 if fu <= 0 else -4.0 * np.pi * u * u * fu * np.log(fu)
    val, _ = integrate.quad(g, 0.0, umax, epsabs=0.0, epsrel=1e-12, limit=500)
    return val / n


def mj_density(u, n, theta):
    """f(u) = n zeta exp(-zeta W)/(4 pi K2(zeta)) = n zeta exp(-zeta (W-1))/(4 pi kve)."""
    z = 1.0 / theta
    return n * z * np.exp(-z * mj.kinetic(u)) / (4.0 * np.pi * special.kve(2, z))


def s_mixture(n1, theta1, n2, theta2):
    """Exact entropy per particle of the two-temperature mixture."""
    f = lambda u: mj_density(u, n1, theta1) + mj_density(u, n2, theta2)
    tmax = max(theta1, theta2)
    umax = np.sqrt((1 + 60 * tmax) ** 2 - 1)
    return s_quad(f, n1 + n2, umax)


def s_estimate(u, n, theta_ref, nbins=400):
    """Histogram estimate of s from four-velocities u (shape (N,3) or |u|), number
    density n. Bins uniform in s = sqrt(zeta_ref (W - 1)) from 0 to the largest sample,
    where ln f of a Maxwell-Juttner gas is close to quadratic, so the coarse-graining
    bias (h^2/24) int f (d ln f/ds)^2 ds is of order 1e-4 for 400 bins (an equal-
    probability binning puts the whole tail into one bin and biases s by +0.02 at
    theta = 1; JOURNAL.md, outcome R6).
    Returns dict(s_plugin, s_mm, stderr, nbins_occupied)."""
    u = np.asarray(u, dtype=float)
    a = np.sqrt(np.sum(u * u, -1)) if u.ndim == 2 else np.abs(u)
    N = a.size
    s_of = lambda x: np.sqrt(mj.kinetic(x) / theta_ref)
    smax = float(s_of(a.max())) * (1.0 + 1e-9) + 1e-12
    se = np.linspace(0.0, smax, nbins + 1)
    x = theta_ref * se * se                       # W - 1 at the edges
    edges = np.sqrt(x * (x + 2.0))
    cnt, _ = np.histogram(a, bins=edges)
    V = 4.0 * np.pi / 3.0 * (edges[1:] ** 3 - edges[:-1] ** 3)
    occ = cnt > 0
    p = cnt[occ] / N
    lnf = np.log(p / V[occ])
    s_plug = -float(np.sum(p * lnf)) - np.log(n)
    mm = (np.count_nonzero(occ) - 1) / (2.0 * N)
    var = float(np.sum(p * lnf * lnf) - np.sum(p * lnf) ** 2)
    return dict(s_plugin=s_plug, s_mm=s_plug + mm, stderr=np.sqrt(var / N),
                nbins_occupied=int(np.count_nonzero(occ)))
