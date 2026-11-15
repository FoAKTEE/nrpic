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
