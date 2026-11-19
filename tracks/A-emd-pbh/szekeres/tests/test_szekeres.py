"""Unit tests of the Szekeres reference solution (python3 -m pytest -q tests/ from the package
directory; about a minute on one core). The LTB limit is checked against the independent
`expball` package of this track (read-only import by path)."""

import math
import os
import sys

import numpy as np
import pytest
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "sym"))
sys.path.insert(0, os.path.join(os.path.dirname(PKG), "expball"))

from szekeres import universal as U                      # noqa: E402
from szekeres.model import Szekeres, SmoothTopHat, Dipole, bump   # noqa: E402
from szekeres.confmap import ConformalMap                # noqa: E402

H = 1.0 / 16.0
PROF = (1.0, 2.4, 6.0)          # data set 2 of expball: delta_c, R1, R2 (R_b = 8)


@pytest.fixture(scope="module")
def ltb():
    return Szekeres(H, SmoothTopHat(*PROF))


@pytest.fixture(scope="module")
def szk():
    return Szekeres(H, SmoothTopHat(*PROF), Dipole(0.1, 2.4, 6.0, "twist"))


@pytest.fixture(scope="module")
def ball():
    from expball.model import Ball, SmoothTopHat as ESTH
    return Ball.from_HRb(0.5, M=1.0, profile=ESTH(*PROF))


# ------------------------------------------------------------------ universal function
def test_series_coefficients_regenerate():
    import gen_series
    l, g = gen_series.coefficients(40)
    for a, b in zip(l, U.L_COEF):
        assert abs(float(a) - b) <= 1e-18 + 1e-15 * abs(b)
    assert abs(math.exp(U.L0) - (4.5) ** (1 / 3)) < 1e-15


def test_series_matches_parametric_on_overlap():
    lam = np.concatenate([np.linspace(0.3, 0.49, 7), -np.linspace(0.3, 0.49, 7)])
    a = U.ell(lam)
    old = U.LAM_SERIES
    try:
        U.LAM_SERIES = 0.0
        b = U.ell(lam)
    finally:
        U.LAM_SERIES = old
    for x, y, tol in zip(a, b, (1e-14, 1e-13, 1e-12)):
        assert np.max(np.abs(x - y)) < tol


def test_universal_derivatives_by_differences():
    lam = np.array([-3.0, -1.0, -0.2, 0.1, 0.7, 1.5, 2.5, 3.2])
    h = 1e-5
    l0, l1, l2 = U.ell(lam)
    lp, lm = U.ell(lam + h)[0], U.ell(lam - h)[0]
    assert np.max(np.abs((lp - lm) / (2 * h) - l1) / (1 + np.abs(l1))) < 1e-8
    l1p, l1m = U.ell(lam + h)[1], U.ell(lam - h)[1]
    assert np.max(np.abs((l1p - l1m) / (2 * h) - l2) / (1 + np.abs(l2))) < 1e-7


def test_universal_satisfies_friedmann():
    # (4/9)(g + lambda g')^2 = 2/g - lambda (expanding branch) with g = exp(l)
    lam = np.array([-2.0, -0.4, 0.0, 0.3, 1.0, 2.0])
    l0, l1, _ = U.ell(lam)
    g = np.exp(l0 + U.L0)
    lhs = (4.0 / 9.0) * (g + lam * g * l1) ** 2
    assert np.max(np.abs(lhs - (2 / g - lam))) < 1e-13


# ------------------------------------------------------------------ LTB limit against expball
def test_initial_slice_matches_expball(ltb, ball):
    r = np.linspace(0.02, 7.9, 500)
    c = ball.at(r)
    f = ltb.fields(ltb.t_i, r, 0.0)
    rel = lambda a, b: np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300))   # noqa: E731
    assert rel(f["M"], c["m"]) < 1e-13
    assert np.max(np.abs(f["k"] + 2 * c["E"])) < 1e-14
    assert rel(f["rho"], c["rho"]) < 1e-12
    assert rel(f["KL"], c["KL"]) < 1e-12
    assert rel(f["KT"], c["KT"]) < 1e-12
    assert np.max(np.abs(f["R"] - r)) < 1e-13 * 8


def test_shell_evolution_matches_expball(ltb, ball):
    from expball.exact import Shells
    r = np.linspace(0.05, 7.9, 300)
    sh = Shells(ball, r)
    tau = np.linspace(0.0, 44.4, 300)
    s = ltb.shell(ltb.t_i + tau[None, :], r[:, None])
    Re = sh.R(tau)
    # P5 predicted 1e-12; measured 1.2e-12 at tau = 44.4, 0.1 per cent before the crunch of
    # the core (R/r = 0.04, ill-conditioned), below 1e-12 elsewhere (JOURNAL entry 2)
    assert np.max(np.abs(s["R"] - Re) / Re) < 2e-12
    assert np.max(np.abs(s["R"] - Re)[:, tau < 40] / Re[:, tau < 40]) < 1e-12
    # dR/dtau: expball takes sqrt(2m/R + 2E), which loses digits at turnaround; compare on H R
    Rd = s["RdR"] * s["R"]
    assert np.max(np.abs(Rd - sh.dRdtau(tau)) / (H * Re)) < 1e-7
    b = sh.bound & (ltb.radial(r)["lam_i"] > 1e-8)
    for mine, theirs in ((ltb.turnaround_time(r[b]), sh.tau_ta[b]), (ltb.crunch_time(r[b]), sh.tau_c[b]),
                         (ltb.horizon_time(r[b]), sh.tau_ah[b])):
        assert np.max(np.abs(mine - ltb.t_i - theirs) / theirs) < 1e-11


def test_shell_evolution_against_direct_integration(szk):
    # R'' = -M/R^2 from the initial slice, independent of the universal function
    for r0 in (1.0, 3.0, 4.5, 5.5, 7.0):
        c = szk.shell(szk.t_i, np.array([r0]))
        M = float(c["M"][0])
        y0 = [r0, float(c["RdR"][0]) * r0]
        tau = np.linspace(0, 40.0, 41)
        sol = solve_ivp(lambda t, y: [y[1], -M / y[0] ** 2], (0, 40.0), y0, t_eval=tau,
                        rtol=1e-12, atol=1e-14, method="DOP853")
        s = szk.shell(szk.t_i + tau, np.full_like(tau, r0))
        assert np.max(np.abs(sol.y[0] - s["R"]) / s["R"]) < 1e-9


def test_silent_universe_equations(szk):
    """Fluid scalars obey the silent equations of arXiv:1708.09143 (lines 218-223),
    kappa = 8 pi, Lambda = 0, along fixed (r, bn), by fourth-order centred differences in t."""
    r = np.array([2.0, 3.0, 3.6, 4.2, 5.0, 5.7])
    bb = np.linalg.norm(szk.dip.b(r), axis=-1)
    for sgn in (-1.0, 0.0, 0.7, 1.0):
        bn = sgn * bb
        for t in (szk.t_i, 2 * szk.t_i, 3.5 * szk.t_i):
            h = 2e-3 * szk.t_i
            f0 = szk.fields(t, r, bn)
            fp, fm = szk.fields(t + h, r, bn), szk.fields(t - h, r, bn)
            fp2, fm2 = szk.fields(t + 2 * h, r, bn), szk.fields(t - 2 * h, r, bn)
            d = {k: (8 * (fp[k] - fm[k]) - (fp2[k] - fm2[k])) / (12 * h)       # fourth order
                 for k in ("rho", "Theta", "Sigma", "W")}
            kr = 8 * math.pi * f0["rho"]
            sc = f0["Theta"] ** 2 + kr
            assert np.max(np.abs(d["rho"] + f0["rho"] * f0["Theta"]) / (f0["rho"] * np.abs(f0["Theta"]) + 1e-30)) < 1e-8
            assert np.max(np.abs(d["Theta"] - (-f0["Theta"] ** 2 / 3 - kr / 2 - 6 * f0["Sigma"] ** 2)) / sc) < 1e-9
            assert np.max(np.abs(d["Sigma"] - (-2 / 3 * f0["Theta"] * f0["Sigma"] + f0["Sigma"] ** 2 - f0["W"])) / sc) < 1e-9
            assert np.max(np.abs(d["W"] - (-f0["Theta"] * f0["W"] - kr * f0["Sigma"] / 2 - 3 * f0["Sigma"] * f0["W"]))
                          / (sc * np.sqrt(sc))) < 1e-9


def test_regular_until_core_crunch(szk):
    """P9: no shell crossing and positive density for eps = 0.1 until 0.99 of the core
    crunch."""
    tc = float(szk.crunch_time(np.array([1.0]))[0])
    r = np.linspace(2.41, 5.99, 400)
    m_dens = None
    worst = np.inf
    for t in np.linspace(szk.t_i, 0.99 * tc, 120):
        a, b = szk.margins(t, r)
        worst = min(worst, float(np.min(a)))
        m_dens = float(np.min(b))
    assert worst > 1.0
    assert m_dens > 1.0


# ------------------------------------------------------------------ conformal map
def test_confmap_ltb_limit(ltb, ball):
    cm = ConformalMap(ltb)
    r = np.linspace(0.01, 5.99, 300)
    T = cm.radial_table(r)
    assert np.max(np.abs(T["rho"] - ball.rbar_of_R(r)) / ball.rbar_of_R(r)) < 1e-10
    assert np.max(np.abs(T["C"])) == 0.0
    x = np.random.default_rng(2).uniform(-4.5, 4.5, (3000, 3))
    f = cm.fields(x)
    fe = ball.fields(np.linalg.norm(x, axis=1), ("u", "KL", "KT", "rho"))
    assert np.max(np.abs(f["psi"] - 1 - fe["u"])) < 1e-10
    assert np.max(np.abs(f["rho"] - fe["rho"])) / ltb.rho_b < 1e-10
    assert np.max(np.abs(f["KL"] - fe["KL"])) / H < 1e-10


def test_confmap_rk4_halving(szk):
    a = ConformalMap(szk, nodes=20001)
    b = ConformalMap(szk, nodes=10001)
    x = np.random.default_rng(3).uniform(-6.5, 6.5, (3000, 3))
    fa, fb = a.fields(x), b.fields(x)
    assert np.max(np.abs(fa["psi"] - fb["psi"])) < 1e-10
    assert np.max(np.abs(fa["rho"] - fb["rho"])) / szk.rho_b < 1e-9
    assert a.hyper_drift < 1e-12


def _stereo(p, q, S, P, Q):
    zr, zi = (p - P) / S, (q - Q) / S
    d = 1 + zr * zr + zi * zi
    return np.array([2 * zr / d, 2 * zi / d, (zr * zr + zi * zi - 1) / d])


def test_confmap_pullback_is_conformally_flat(szk):
    """At random (r, p, q): the flat metric of x(r, p, q) = rho O ntilde + C, times Phi^2,
    equals the Szekeres slice metric (finite differences of the map)."""
    cm = ConformalMap(szk)
    rng = np.random.default_rng(4)

    def X(r, p, q):
        T = cm.radial_table(np.array([r]))
        At = T["At"][:, 0]
        St, Pt, Qt = 1 / (2 * At[0]), -At[1] / (2 * At[0]), -At[2] / (2 * At[0])
        nt = _stereo(p, q, St, Pt, Qt)
        return T["rho"][0] * T["O"][:, :, 0] @ nt + T["C"][:, 0]

    worst = 0.0
    for _ in range(25):
        r = rng.uniform(2.6, 5.8)
        p, q = rng.uniform(-2, 2, 2)
        h = 1e-5
        J = np.stack([(X(r + h, p, q) - X(r - h, p, q)) / (2 * h),
                      (X(r, p + h, q) - X(r, p - h, q)) / (2 * h),
                      (X(r, p, q + h) - X(r, p, q - h)) / (2 * h)], axis=1)
        gflat = J.T @ J
        T = cm.radial_table(np.array([r]))
        S, P, Q = T["S"][0], T["P"][0], T["Q"][0]
        n = _stereo(p, q, S, P, Q)
        Ecal = ((p - P) ** 2 + (q - Q) ** 2) / (2 * S) + S / 2
        bn = float(szk.dip.b(np.array([r]))[0] @ n)
        f = szk.fields(szk.t_i, np.array([r]), np.array([bn]))
        g = np.diag([f["grr"][0], (f["R"][0] / Ecal) ** 2, (f["R"][0] / Ecal) ** 2])
        At = T["At"][:, 0]
        Et = At[0] * (p * p + q * q) + At[1] * p + At[2] * q + At[3]
        Phi = f["R"][0] * Et / (T["rho"][0] * Ecal)
        worst = max(worst, float(np.max(np.abs(Phi ** 2 * gflat - g)) / np.max(np.abs(g))))
    assert worst < 1e-8


def test_direction_formula_unit_and_dipolar(szk):
    cm = ConformalMap(szk)
    x = np.random.default_rng(5).uniform(-6, 6, (5000, 3))
    f = cm.fields(x)
    ins = (f["r"] > 2.5) & (f["r"] < 5.9)
    bb = np.linalg.norm(szk.dip.b(f["r"][ins]), axis=-1)
    assert np.all(np.abs(f["bn"][ins]) <= bb * (1 + 1e-12))
    assert np.max(np.abs(f["psi"][f["r"] > 6.0006] - 1.0)) < 1e-12


def test_bump_and_dipole_support():
    u = np.linspace(-0.5, 1.5, 2001)
    b = bump(u)
    assert b.max() <= 1.0 and abs(b[1000] - 1.0) < 1e-15
    assert np.all(b[(u <= 0) | (u >= 1)] == 0)
    d = Dipole(0.1, 2.4, 6.0, "twist")
    r = np.array([1.0, 2.4, 6.0, 7.0])
    assert np.all(d.b(r)[[0, 1, 2, 3]] == 0)
