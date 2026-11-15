"""R1: collision rate of a Maxwell-Juttner gas (JOURNAL.md)."""
import numpy as np
import pytest

import rate


@pytest.mark.parametrize("theta", [1e-3, 0.1, 1.0, 10.0])
def test_closed_form_vs_monte_carlo(theta):
    rng = np.random.default_rng(int(1e6 * theta) + 11)
    m, se = rate.vmol_mean_mc(theta, 2_000_000, rng)
    assert abs(m - rate.vmol_mean(theta)) < 4 * se


@pytest.mark.parametrize("theta", [1e-3, 0.1, 1.0, 10.0])
def test_closed_form_vs_one_dimensional_integral(theta):
    assert abs(rate.vmol_mean_integral(theta) / rate.vmol_mean(theta) - 1) < 1e-10


@pytest.mark.parametrize("theta", [1e-3, 0.3, 3.0])
def test_closed_form_vs_two_dimensional_quadrature(theta):
    assert abs(rate.vmol_mean_two_temperatures(theta, theta) / rate.vmol_mean(theta)
               - 1) < 1e-8


def test_limits():
    th = 1e-4
    assert abs(rate.vmol_mean(th) / rate.vmol_mean_nr(th) - 1) < 1e-6
    assert abs(rate.vmol_mean(100.0) - 1.0) < 1e-3
    # a = sqrt(16/pi) of Balberg et al. as the leading coefficient
    assert abs(rate.vmol_mean(1e-8) / np.sqrt(1e-8) - np.sqrt(16 / np.pi)) < 1e-6


def test_two_temperature_rate_vs_mc():
    rng = np.random.default_rng(5)
    m, se = rate.vmol_mean_mc(0.01, 2_000_000, rng, theta_b=0.5)
    assert abs(m - rate.vmol_mean_two_temperatures(0.01, 0.5)) < 4 * se


def test_noninvariant_relative_speed_is_refuted():
    """T4 and T11 discriminate v_Mol from |v_a - v_b| (numbers quoted in TESTS.md)."""
    import mj
    import kinematics as kin
    rng = np.random.default_rng(31)
    N = 2_000_000
    ua = mj.sample_u(N, 3.0, rng); ub = mj.sample_u(N, 1.0, rng)
    dE = 0.5 * (np.sum(ub * ub, 1) - np.sum(ua * ua, 1)) / (kin.W_of(ua) + kin.W_of(ub))
    r = (rate.vrel_noninvariant_mc(ua, ub) * dE).mean() / (kin.vmol(ua, ub) * dE).mean()
    assert 1.22 < r < 1.31                       # 1.266 at seed 31
    b = np.array([0.6, 0, 0]); g2 = 1 / (1 - 0.36)
    ua = mj.sample_u_boosted(N, 1.0, b, rng); ub = mj.sample_u_boosted(N, 1.0, b, rng)
    vm = kin.vmol(ua, ub)
    assert abs(vm.mean() - rate.vmol_mean(1.0) / g2) < 4 * vm.std() / np.sqrt(N)
    assert rate.vrel_noninvariant_mc(ua, ub).mean() / vm.mean() > 1.4   # 1.48
