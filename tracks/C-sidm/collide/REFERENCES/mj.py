"""Maxwell-Juttner distribution of one particle species: moments, inversion, sampler.

Units c = k_B = 1 and particle mass m = 1 unless stated: theta = T/m, zeta = 1/theta,
u = p/m the spatial four-velocity, W = sqrt(1 + u^2) = E/m. The distribution of u in the
rest frame of the gas, normalized to one,

    MJ(u) d^3u = zeta exp(-zeta W) / (4 pi K2(zeta)) d^3u,

so that the speed distribution is p(u) du = zeta u^2 exp(-zeta W) / K2(zeta) du.
Bessel functions are used in their exponentially scaled form kve(nu, z) = K_nu(z) e^z,
so every formula below holds from theta = 1e-8 to theta = 1e8 without overflow.

Closed forms (SPEC.md section 2; checked against quadrature in tests/test_mj.py):
    <W>      = K1/K2 + 3 theta = K3/K2 - theta        mean energy per particle / m
    h        = K3/K2                                    enthalpy per particle / m
    <u^2/W>  = 3 theta                                  pressure p = n T
    c_v      = d<W>/dtheta = 3 + zeta^2 (K0 K2 - K1^2 - K1 K2 / zeta) / K2^2
    c_p      = c_v + 1
    T d(ln MJ)/dT = zeta (W - <W>)                      (fixed u)
"""
import numpy as np
from scipy import special, integrate, optimize

__all__ = ["mean_W", "enthalpy", "c_v", "c_p", "var_W", "mean_W2", "theta_from_mean_W",
           "speed_pdf", "Sampler", "sample_u", "sample_u_boosted", "isotropic_dirs",
           "kinetic"]


def _k(nu, z):
    return special.kve(nu, z)


def kinetic(u):
    """W - 1 = u^2 / (W + 1), without cancellation for small u (u: (..., 3) or |u|)."""
    u = np.asarray(u, dtype=float)
    u2 = np.sum(u * u, axis=-1) if u.ndim and u.shape[-1] == 3 else u * u
    return u2 / (np.sqrt(1.0 + u2) + 1.0)


THETA_SWITCH = 0.05   # below: moments by quadrature (the Bessel forms cancel)


def _s_moments(theta):
    """M_k = int_0^inf s^(2k) g(s) ds, k = 0, 1, 2, with the density of s = sqrt(zeta
    (W - 1)) g(s) = s^2 sqrt(2 + theta s^2) (1 + theta s^2) exp(-s^2) (up to a constant):
    <W - 1> = theta M1/M0, c_v = Var(s^2) = M2/M0 - (M1/M0)^2."""
    g = lambda s, k: s ** (2 * k + 2) * np.sqrt(2.0 + theta * s * s) * \
        (1.0 + theta * s * s) * np.exp(-s * s)
    m = [integrate.quad(g, 0.0, 12.0, args=(k,), epsabs=0.0, epsrel=2e-14,
                        limit=200)[0] for k in range(3)]
    return m


def _vec(fun, theta):
    th = np.asarray(theta, dtype=float)
    out = np.vectorize(fun, otypes=[float])(th)
    return out if out.ndim else float(out)


def mean_kinetic_bessel(theta):
    """<W> - 1 = K1/K2 + 3 theta - 1 (closed form; cancels for small theta)."""
    z = 1.0 / np.asarray(theta, dtype=float)
    return _k(1, z) / _k(2, z) + 3.0 / z - 1.0


def c_v_bessel(theta):
    """c_v = 3 + zeta^2 (K0 K2 - K1^2 - K1 K2 / zeta) / K2^2 (closed form)."""
    z = 1.0 / np.asarray(theta, dtype=float)
    k0, k1, k2 = _k(0, z), _k(1, z), _k(2, z)
    return 3.0 + z * z * (k0 * k2 - k1 * k1 - k1 * k2 / z) / (k2 * k2)


def mean_kinetic(theta):
    """<W> - 1, accurate for every theta."""
    def f(t):
        if t >= THETA_SWITCH:
            return float(mean_kinetic_bessel(t))
        m = _s_moments(t)
        return t * m[1] / m[0]
    return _vec(f, theta)


def mean_W(theta):
    """<W> = K1(zeta)/K2(zeta) + 3 theta."""
    return 1.0 + mean_kinetic(theta)


def enthalpy(theta):
    """h/m = K3/K2 = <W> + theta."""
    return mean_W(theta) + np.asarray(theta, dtype=float)


def c_v(theta):
    """Heat capacity per particle at constant volume, d<W>/dtheta (k_B = 1)."""
    def f(t):
        if t >= THETA_SWITCH:
            return float(c_v_bessel(t))
        m = _s_moments(t)
        return m[2] / m[0] - (m[1] / m[0]) ** 2
    return _vec(f, theta)


def c_p(theta):
    return c_v(theta) + 1.0


def var_W(theta):
    """Var(W) = theta^2 c_v (fluctuation formula)."""
    theta = np.asarray(theta, dtype=float)
    return theta * theta * c_v(theta)


def mean_W2(theta):
    return var_W(theta) + mean_W(theta) ** 2


def theta_from_kinetic(kbar, lo=1e-10, hi=1e10):
    """Invert <W - 1>(theta) = kbar (> 0); pass the kinetic part, not <W>, so that small
    temperatures keep their digits."""
    kin = float(kbar)
    if kin <= 0:
        raise ValueError("mean kinetic energy must be positive")
    f = lambda lt: np.log(mean_kinetic(np.exp(lt))) - np.log(kin)
    lt = optimize.brentq(f, np.log(lo), np.log(hi), xtol=1e-14, rtol=1e-15, maxiter=500)
    return float(np.exp(lt))


def theta_from_mean_W(wbar, lo=1e-10, hi=1e10):
    """Invert <W>(theta) = wbar (wbar > 1)."""
    return theta_from_kinetic(float(wbar) - 1.0, lo, hi)


def speed_pdf(u, theta):
    """p(u) = zeta u^2 exp(-zeta (W - 1)) / kve(2, zeta)."""
    u = np.asarray(u, dtype=float)
    z = 1.0 / theta
    return z * u * u * np.exp(-z * kinetic(u)) / _k(2, z)


class Sampler:
    """Inverse-CDF sampler of |u| for one theta.

    Variable s with y = zeta (W - 1) = s^2 (scaled kinetic energy): the density in s is
    proportional to s sqrt(W^2 - 1) W exp(-s^2), smooth at s = 0 in every regime.
    The CDF is tabulated on 2e5 points of s in [0, 9] by cumulative Simpson integration
    (relative tail below e^-81) and inverted by linear interpolation; the error of a
    sampled |u| is below 1e-9 relative (tests/test_mj.py)."""

    def __init__(self, theta, npts=200001, smax=9.0):
        self.theta = float(theta)
        s = np.linspace(0.0, smax, npts)
        y = s * s
        w = 1.0 + y * self.theta
        dens = s * np.sqrt(np.maximum(w * w - 1.0, 0.0)) * w * np.exp(-y)
        cdf = integrate.cumulative_simpson(dens, x=s, initial=0.0)
        cdf = np.maximum.accumulate(cdf)
        self.norm = cdf[-1]
        self.cdf = cdf / cdf[-1]
        self.s = s

    def u_of_q(self, q):
        s = np.interp(q, self.cdf, self.s)
        x = s * s * self.theta                 # W - 1
        return np.sqrt(x * (x + 2.0))

    def cdf_u(self, u):
        """CDF of |u| from the table (for Kolmogorov-Smirnov tests)."""
        x = kinetic(np.asarray(u, dtype=float))
        s = np.sqrt(x / self.theta)
        return np.interp(s, self.s, self.cdf)


def isotropic_dirs(n, rng):
    """n isotropic unit vectors (cos uniform, phi uniform)."""
    mu = rng.uniform(-1.0, 1.0, n)
    ph = rng.uniform(0.0, 2.0 * np.pi, n)
    st = np.sqrt(1.0 - mu * mu)
    return np.stack([st * np.cos(ph), st * np.sin(ph), mu], axis=-1)


def sample_u(n, theta, rng, sampler=None):
    """n spatial four-velocities of a Maxwell-Juttner gas at rest, shape (n, 3)."""
    smp = sampler if sampler is not None else Sampler(theta)
    mag = smp.u_of_q(rng.uniform(0.0, 1.0, n))
    return mag[:, None] * isotropic_dirs(n, rng)


def boost(u, beta_vec):
    """Lorentz boost of four-velocities u (n,3) by the velocity beta_vec (3,) of the
    rest frame of u relative to the new frame (pure boost, no rotation)."""
    b = np.asarray(beta_vec, dtype=float)
    b2 = float(b @ b)
    if b2 == 0.0:
        return np.array(u, dtype=float)
    g = 1.0 / np.sqrt(1.0 - b2)
    W = np.sqrt(1.0 + np.sum(u * u, axis=-1))
    bu = u @ b
    coef = g * g / (g + 1.0) * bu + g * W
    return u + coef[:, None] * b[None, :]


def sample_u_boosted(n, theta, beta_vec, rng, sampler=None):
    """n four-velocities of a Maxwell-Juttner gas drifting with velocity beta_vec, as
    counted in a fixed volume of the frame in which it drifts.

    Rest-frame samples are boosted and accepted with probability (1 + beta.v_rest) /
    (1 + |beta|): the number of particles per volume of the drifting frame is
    proportional to E_lab / E_rest = gamma (1 + beta.v_rest) (d^3p/E is invariant)."""
    b = np.asarray(beta_vec, dtype=float)
    bm = np.sqrt(b @ b)
    out = []
    have = 0
    smp = sampler if sampler is not None else Sampler(theta)
    while have < n:
        m = int(1.2 * (n - have)) + 16
        u = sample_u(m, theta, rng, smp)
        W = np.sqrt(1.0 + np.sum(u * u, axis=-1))
        v_par = (u @ b) / W
        acc = rng.uniform(0.0, 1.0, m) < (1.0 + v_par) / (1.0 + bm) if bm > 0 else \
            np.ones(m, bool)
        ub = boost(u[acc], b)
        out.append(ub)
        have += ub.shape[0]
    return np.concatenate(out)[:n]
