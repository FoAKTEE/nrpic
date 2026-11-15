"""R7: Maxwell-Juttner moments and sampler (JOURNAL.md)."""
import numpy as np
import pytest
from scipy import integrate, stats

import mj
import rate


def quad_moment(theta, fun):
    z = 1.0 / theta
    num = integrate.quad(lambda u: fun(u) * mj.speed_pdf(u, theta), 0, np.inf,
                         epsabs=0, epsrel=1e-13, limit=400)[0]
    return num


@pytest.mark.parametrize("theta", [1e-6, 1e-3, 0.05, 0.3, 1.0, 10.0, 1e3])
def test_normalization_and_identities(theta):
    # quadrature over the s-variable rule (independent of the Bessel forms)
    u, w = rate._speed_rule(theta, 600)
    assert abs(w.sum() - 1.0) < 1e-13
    W = np.sqrt(1 + u * u)
    assert abs(np.sum(w * u * u / W) / (3 * theta) - 1.0) < 1e-11       # p = n T
    kin = np.sum(w * u * u / (W + 1))
    assert abs(kin / mj.mean_kinetic(theta) - 1.0) < 1e-11
    var = np.sum(w * (W - 1 - kin) ** 2) - 0.0
    assert abs(var / (theta * theta * mj.c_v(theta)) - 1.0) < 1e-9


@pytest.mark.parametrize("theta", [0.06, 0.3, 1.0, 10.0])
def test_bessel_forms_match_quadrature(theta):
    m = mj._s_moments(theta)
    assert abs(theta * m[1] / m[0] / mj.mean_kinetic_bessel(theta) - 1) < 1e-11
    assert abs((m[2] / m[0] - (m[1] / m[0]) ** 2) / mj.c_v_bessel(theta) - 1) < 1e-9


def test_limits():
    assert abs(mj.c_v(1e-7) - 1.5) < 1e-5
    assert abs(mj.c_v(1e7) - 3.0) < 1e-5
    assert abs(mj.mean_kinetic(1e-6) / 1.5e-6 - 1) < 1e-5
    assert abs(mj.enthalpy(1e6) / 4e6 - 1) < 1e-5


@pytest.mark.parametrize("theta", [1e-5, 0.1, 2.0])
def test_inversion(theta):
    k = mj.mean_kinetic(theta)
    assert abs(mj.theta_from_kinetic(k) / theta - 1) < 1e-12


@pytest.mark.parametrize("theta", [1e-3, 1.0, 100.0])
def test_sampler_ks(theta):
    rng = np.random.default_rng(7)
    smp = mj.Sampler(theta)
    u = mj.sample_u(200000, theta, rng, smp)
    a = np.sqrt(np.sum(u * u, -1))
    # exact CDF by quadrature at a few points vs table
    for q in (0.1, 0.5, 0.9):
        uq = smp.u_of_q(q)
        exact = integrate.quad(lambda x: mj.speed_pdf(x, theta), 0, uq, epsabs=0,
                               epsrel=1e-12, limit=400)[0]
        assert abs(exact - q) < 1e-9
    p = stats.kstest(a, smp.cdf_u).pvalue
    assert p > 1e-3
    # isotropy: mean direction ~ 0
    assert np.all(np.abs(u.mean(0)) < 5 * a.std() / np.sqrt(len(a)) + 5 * a.mean() /
                  np.sqrt(len(a)))


def test_boosted_sampler_moments():
    """Drifting gas: lab-frame density ratio and mean momentum. For a fixed lab volume,
    the four-velocity of the mean flow is the boost: <u_x> per particle equals
    gamma beta h/... ; test the invariant check N^mu: n_lab = gamma n_rest is a statement
    about densities, so check instead T^0x/T^00 = (e+p) gamma^2 beta / (gamma^2 (e+p) - p)."""
    rng = np.random.default_rng(3)
    theta, beta = 0.5, 0.6
    u = mj.sample_u_boosted(400000, theta, np.array([beta, 0, 0]), rng)
    W = np.sqrt(1 + np.sum(u * u, -1))
    T00 = W.mean()                     # per particle in lab volume (sum E)/N
    T0x = u[:, 0].mean()
    g2 = 1.0 / (1 - beta ** 2)
    # rest-frame energy and pressure per rest-frame particle
    e = mj.mean_W(theta)
    p = theta
    # per lab-frame particle: divide rest quantities by gamma (n_lab = gamma n_rest)
    g = np.sqrt(g2)
    T00_exp = (g2 * (e + p) - p) / g
    T0x_exp = g2 * (e + p) * beta / g
    assert abs(T00 / T00_exp - 1) < 4 * W.std() / T00 / np.sqrt(len(W))
    assert abs(T0x / T0x_exp - 1) < 4 * u[:, 0].std() / abs(T0x) / np.sqrt(len(W))
