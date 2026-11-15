"""R4 (relaxation), R5 (conduction), R6 (entropy) (JOURNAL.md)."""
import numpy as np
import pytest
from scipy import integrate

import mj
import rate
import relax
import conduction as cd
import entropy as en


# ---------------------------------------------------------------- R4
def test_nr_closed_form_vs_quadrature_and_mc():
    n1, n2, sig = 0.6, 0.4, 1.0
    t1, t2 = 2e-4, 0.5e-4
    exact_nr = cd_nr = relax.dT_rate_nr(n1, n2, sig, t1, t2)
    d1, d2 = relax.dtheta_dt(n1, n2, sig, t1, t2)
    # quadrature (relativistic formula) at theta ~ 1e-4: relativistic corrections O(theta)
    assert abs((d1 - d2) / exact_nr - 1) < 2e-3
    # Monte Carlo collision integral with oracle scattering
    rng = np.random.default_rng(9)
    m, se = relax.de1_dt_mc(n1, n2, sig, t1, t2, 2_000_000, rng, scatter=True)
    q = relax.de1_dt(n1, n2, sig, t1, t2)
    assert abs(m - q) < 4 * se


def test_relativistic_quadrature_vs_mc():
    n1, n2, sig = 0.5, 0.5, 1.0
    rng = np.random.default_rng(10)
    for t1, t2 in ((1.0, 0.5), (3.0, 0.1)):
        q = relax.de1_dt(n1, n2, sig, t1, t2)
        m, se = relax.de1_dt_mc(n1, n2, sig, t1, t2, 2_000_000, rng, scatter=True)
        assert abs(m - q) < 4 * se, (t1, t2, m, q, se)
        m2, se2 = relax.de1_dt_mc(n1, n2, sig, t1, t2, 2_000_000, rng, scatter=False)
        assert abs(m2 - q) < 4 * se2


def test_equilibrium_temperature():
    th = relax.theta_eq(0.5, 0.5, 1.0, 0.1)
    k = 0.5 * (mj.mean_kinetic(1.0) + mj.mean_kinetic(0.1))
    assert abs(mj.mean_kinetic(th) / k - 1) < 1e-12
    # NR: arithmetic mean
    assert abs(relax.theta_eq(0.5, 0.5, 2e-6, 1e-6) / 1.5e-6 - 1) < 1e-5


# ---------------------------------------------------------------- R5
@pytest.mark.parametrize("theta", [1e-4, 0.1, 1.0, 30.0])
def test_one_sided_fluxes(theta):
    assert abs(cd.phi_N(1.0, theta) / cd.phi_N_quad(1.0, theta) - 1) < 1e-9
    assert abs(cd.phi_E(1.0, theta) / cd.phi_E_quad(1.0, theta) - 1) < 1e-9


def test_flux_limits():
    th = 1e-6
    assert abs(cd.phi_N(1.0, th) / np.sqrt(th / (2 * np.pi)) - 1) < 1e-5
    assert abs(cd.phi_N(1.0, 1e6) / 0.25 - 1) < 1e-5
    assert abs(cd.phi_E(1.0, 1e6) / (0.75 * 1e6) - 1) < 1e-5
    # NR kinetic energy flux: 2 T per crossing particle
    kin_flux = cd.phi_E(1.0, th) - cd.phi_N(1.0, th)
    assert abs(kin_flux / (2 * th * cd.phi_N(1.0, th)) - 1) < 1e-4


@pytest.mark.parametrize("theta1,theta2", [(0.02, 0.01), (2.0, 1.0)])
def test_step_collisionless(theta1, theta2):
    L = 1.0
    n1, n2 = 1.0 / theta1, 1.0 / theta2          # equal pressure n theta = 1
    t = np.array([0.0, 1e-6, 2e-6])
    NL, EL, KL = cd.step_collisionless(t, L, n1, theta1, n2, theta2)
    sN = (NL[2] - NL[1]) / 1e-6
    sE = (EL[2] - EL[1]) / 1e-6
    assert abs(sN / (-2 * (cd.phi_N(n1, theta1) - cd.phi_N(n2, theta2))) - 1) < 1e-4
    assert abs(sE / (-2 * (cd.phi_E(n1, theta1) - cd.phi_E(n2, theta2))) - 1) < 1e-4
    # late time: phase mixing to the box average (the triangle average tends to L/4)
    vtyp = rate.vmol_mean(theta2)
    tl = np.array([2000.0 * L / vtyp])
    NLl, ELl, _ = cd.step_collisionless(tl, L, n1, theta1, n2, theta2)
    assert abs(NLl[0] / (0.25 * L * (n1 + n2)) - 1) < 1e-3
    E1 = n1 * mj.mean_W(theta1); E2 = n2 * mj.mean_W(theta2)
    assert abs(ELl[0] / (0.25 * L * (E1 + E2)) - 1) < 1e-3


def test_step_diffusive_initial_value():
    t = np.array([0.0])
    X = cd.step_diffusive(t, 1.0, 3.0, 1.0, 1.0)
    assert abs(X[0] - 3.0) < 2e-3        # truncated series at t = 0


def test_kappa_values():
    # 75 sqrt(pi)/64 = 2.077 (Koda & Shapiro, 2010.15132's 2.1)
    assert abs(cd.kappa_ce_nr(1.0, 1.0) - 75 * np.sqrt(np.pi) / 64) < 1e-14
    assert abs(cd.kappa_ce_nr(1.0, 1.0) / cd.kappa_bsi(1.0, 1.0) - np.sqrt(6 / np.pi)) \
        < 1e-14


def test_mode_collisionless_starts_at_one():
    r = cd.mode_collisionless(np.array([0.0, 1e3]), 2 * np.pi, 0.01)
    assert abs(r[0] - 1) < 1e-12
    assert abs(r[1]) < 1e-2


# ---------------------------------------------------------------- R6
@pytest.mark.parametrize("theta", [1e-3, 0.2, 1.0, 20.0])
def test_entropy_closed_form(theta):
    n = 2.0
    umax = np.sqrt((1 + 70 * theta) ** 2 - 1)
    sq = en.s_quad(lambda u: en.mj_density(u, n, theta), n, umax)
    assert abs(sq - en.s_mj(n, theta)) < 1e-9 * max(1.0, abs(sq))


def test_sackur_tetrode():
    th, n = 1e-7, 3.0
    st = 1.5 + np.log((2 * np.pi * th) ** 1.5 / n)
    assert abs(en.s_mj(n, th) - st) < 1e-5


def test_mixture_below_equilibrium():
    n1 = n2 = 0.5
    t1, t2 = 1.0, 0.1
    s0 = en.s_mixture(n1, t1, n2, t2)
    teq = relax.theta_eq(n1, n2, t1, t2)
    assert s0 < en.s_mj(1.0, teq)


@pytest.mark.parametrize("theta", [0.01, 1.0])
def test_estimator_unbiased(theta):
    rng = np.random.default_rng(12)
    u = mj.sample_u(1_000_000, theta, rng)
    r = en.s_estimate(u, 1.0, theta, nbins=400)
    assert abs(r["s_mm"] - en.s_mj(1.0, theta)) < 4 * r["stderr"]
