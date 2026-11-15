"""Tests of fslib.gauge on exact data (T0 of JOURNAL.md, prediction P7).

Pure-gauge Minkowski space in random spatial coordinates (gw_diag analytic.gauge_mode,
slicing off): tilde gamma = det(J)^(-2/3) J^T J exactly, h_T = 0, so Lambda h - G must be
third order in the amplitude while Lambda h is second order. With the slicing on, the
residual Lambda[-d f d f] stays second order (G does not remove the slicing part).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from gwdiag import tt, analytic  # noqa: E402
from gwdiag.grid import Grid  # noqa: E402
from fslib import gauge  # noqa: E402


def conformal_h(gamma):
    ginv, d = tt.inv3(gamma)
    return d ** (-1.0 / 3.0) * gamma - np.eye(3)[:, :, None, None, None]


def rms(x):
    return float(np.sqrt(np.mean(np.einsum("ab...,ab...->...", x, x))))


def residuals(eps, slicing=False, n=32, seed=3, pad=True):
    g = Grid((n, n, n), (4.0, 4.0, 4.0), (0.0, 0.0, 0.0))
    gamma, K, alpha, beta = analytic.gauge_mode(g, eps, seed=seed, slicing=slicing)
    h = conformal_h(gamma)
    Lh = tt.tt_project(h, g)
    G = gauge.gauge_piece(h, g, pad=pad)
    return rms(Lh), rms(Lh - G), rms(G)


def test_inverse_of_longitudinal_part():
    rng = np.random.default_rng(1)
    g = Grid((16, 16, 16), (4.0, 4.0, 4.0), (0.0, 0.0, 0.0))
    h = rng.normal(size=(3, 3) + g.shape)
    h = 0.5 * (h + np.einsum("ab...->ba...", h))
    X = gauge.xi_hat_from_h(h, g)
    D = gauge.longitudinal_from_xi_hat(X, g)
    target = tt.tensor_rfft(gauge.nonTT_traceless(h, g))
    m = ~g.nyquist_mask(real=True)
    m[0, 0, 0] = False
    err = np.abs(D[:, :, m] - target[:, :, m]).max() / np.abs(target[:, :, m]).max()
    assert err < 1e-12, err


def test_pure_spatial_gauge_is_removed_at_second_order():
    eps = np.array([4e-3, 2e-3, 1e-3, 5e-4])
    r = np.array([residuals(e) for e in eps])
    s_raw = np.polyfit(np.log(eps), np.log(r[:, 0]), 1)[0]
    s_res = np.polyfit(np.log(eps), np.log(r[:, 1]), 1)[0]
    assert abs(s_raw - 2.0) < 0.05, s_raw
    assert abs(s_res - 3.0) < 0.1, s_res
    assert np.all(r[:, 1] < 0.05 * r[:, 0])


def test_slicing_part_is_not_removed():
    eps = np.array([2e-3, 1e-3, 5e-4])
    r = np.array([residuals(e, slicing=True) for e in eps])
    s_res = np.polyfit(np.log(eps), np.log(r[:, 1]), 1)[0]
    assert abs(s_res - 2.0) < 0.1, s_res


def _A_target_at(points, coefs, ks, phases):
    """Symmetric traceless field sum_n c_n sin(k_n.x + p_n) at the given points (3, ...)."""
    A = np.zeros((3, 3) + points.shape[1:])
    for c, k, p in zip(coefs, ks, phases):
        A += c[:, :, None, None, None] * np.sin(np.einsum("a,a...->...", k, points) + p)
    return A


def residual_A(eps_xi, amp_A=1e-4, n=32, seed=7):
    g = Grid((n, n, n), (4.0, 4.0, 4.0), (0.0, 0.0, 0.0))
    rng = np.random.default_rng(seed)
    L = 4.0
    xis = [analytic.random_modefield(g, eps_xi * L / (2 * np.pi), 3, 2, seed + 10 * a + 1) for a in range(3)]
    xi = np.array([x.val() for x in xis])
    J = np.eye(3)[:, :, None, None, None] + np.array([x.grad() for x in xis])
    X = np.array(g.mesh())
    ks, coefs, ph = [], [], []
    for _ in range(4):
        m = rng.integers(-2, 3, size=3)
        while not m.any():
            m = rng.integers(-2, 3, size=3)
        ks.append(2 * np.pi * m / L)
        c = rng.normal(size=(3, 3))
        c = 0.5 * (c + c.T)
        c -= np.eye(3) * np.trace(c) / 3
        coefs.append(amp_A * c / np.abs(c).max())
        ph.append(rng.uniform(0, 2 * np.pi))
    A_T_disp = _A_target_at(X + xi, coefs, ks, ph)                 # A_T(x' + xi)
    A_T = _A_target_at(X, coefs, ks, ph)                           # A_T(x')
    detJ = tt.det3(J)
    Ap = detJ ** (-2.0 / 3.0) * np.einsum("ki...,kl...,lj...->ij...", J, A_T_disp, J)
    gamma = np.einsum("mi...,mj...->ij...", J, J)
    ginv, d = tt.inv3(gamma)
    h = d ** (-1.0 / 3.0) * gamma - np.eye(3)[:, :, None, None, None]
    LA = tt.tt_project(Ap, g)
    LAT = tt.tt_project(A_T, g)
    GA = gauge.gauge_piece_A(h, Ap, g)
    return rms(LA - LAT), rms(LA - GA - LAT)


def test_gauge_piece_of_A():
    eps = np.array([4e-3, 2e-3, 1e-3, 5e-4])
    r = np.array([residual_A(e) for e in eps])
    s_raw = np.polyfit(np.log(eps), np.log(r[:, 0]), 1)[0]
    s_res = np.polyfit(np.log(eps), np.log(r[:, 1]), 1)[0]
    assert abs(s_raw - 1.0) < 0.05, s_raw
    assert abs(s_res - 2.0) < 0.1, s_res
    assert np.all(r[:, 1] < 0.05 * r[:, 0])


def test_total_piece_with_homogeneous_anisotropy():
    """Target metric with a homogeneous traceless part h0 and a TT wave, both of the size of
    the coordinate gradients: G alone leaves an error first order in xi times h_T; G_tot
    (with the cross terms) leaves third order."""
    g = Grid((32, 32, 32), (4.0, 4.0, 4.0), (0.0, 0.0, 0.0))
    L = 4.0
    out = []
    for e in (2e-3, 1e-3, 5e-4):
        xis = [analytic.random_modefield(g, e * L / (2 * np.pi), 3, 2, 21 + 10 * a) for a in range(3)]
        xi = np.array([x.val() for x in xis])
        J = np.eye(3)[:, :, None, None, None] + np.array([x.grad() for x in xis])
        h0 = e * np.diag([1.0, 0.7, -1.7])[:, :, None, None, None]
        waves = [analytic.Wave((1, 1, 0), 0.5 * e, 0.0), analytic.Wave((0, 1, 2), 0.0, 0.3 * e)]
        X = np.array(g.mesh())
        # wave evaluated at the displaced points x' + xi: shift the mesh analytically
        hw_disp = np.zeros((3, 3) + g.shape)
        for w in waves:
            k = analytic.lattice_k(g, w.m)
            ep, ex, _, _ = tt.pol_basis((k / np.linalg.norm(k)).reshape(3, 1, 1, 1))
            ph = np.einsum("a,a...->...", k, X + xi)
            hw_disp += (w.ap.real * ep + w.ax.real * ex) * np.cos(ph)
        hw = np.zeros((3, 3) + g.shape)
        for w in waves:
            k = analytic.lattice_k(g, w.m)
            ep, ex, _, _ = tt.pol_basis((k / np.linalg.norm(k)).reshape(3, 1, 1, 1))
            hw += (w.ap.real * ep + w.ax.real * ex) * np.cos(np.einsum("a,a...->...", k, X))
        gT = np.eye(3)[:, :, None, None, None] + h0 + hw_disp
        gp = tt.det3(J) ** (-2.0 / 3.0) * np.einsum("ki...,kl...,lj...->ij...", J, gT, J)
        h = conformal_h(gp)
        Lh = tt.tt_project(h, g)
        target = tt.tt_project(hw, g)
        e_G = rms(Lh - gauge.gauge_piece(h, g) - target)
        e_T = rms(Lh - gauge.gauge_piece_total(h, g) - target)
        out.append((e, e_G, e_T))
    out = np.array(out)
    sG = np.polyfit(np.log(out[:, 0]), np.log(out[:, 1]), 1)[0]
    sT = np.polyfit(np.log(out[:, 0]), np.log(out[:, 2]), 1)[0]
    assert abs(sG - 2.0) < 0.1, sG           # G alone: xi * h_T, both ~ e
    assert abs(sT - 3.0) < 0.15, sT          # G_tot: third order
    assert np.all(out[:, 2] < 0.05 * out[:, 1])


def test_tt_wave_survives_the_correction():
    g = Grid((32, 32, 32), (4.0, 4.0, 4.0), (0.0, 0.0, 0.0))
    waves = [analytic.Wave((1, 1, 0), 1e-6, 0.0), analytic.Wave((0, 1, 2), 0.0, 5e-7)]
    gamma_w = analytic.wave_adm(waves, g)[0]
    hw = conformal_h(gamma_w)
    # wave in pure-gauge coordinates: gamma' = J^T gamma_w(x' + xi) J; to the order kept
    # here (xi ~ 1e-3, wave ~ 1e-6) the shift of the argument is a 1e-9 correction
    gp, _, _, _ = analytic.gauge_mode(g, 1e-3, seed=5, slicing=False)
    J = np.eye(3)[:, :, None, None, None] + 0.0
    # J^T gamma_w J with J from gp: gp = J^T J; build J explicitly from the same seed
    L = 4.0
    xis = [analytic.random_modefield(g, 1e-3 * L / (2 * np.pi), 3, 2, 5 + 10 * a + 1) for a in range(3)]
    J = J + np.array([x.grad() for x in xis])
    gamma = np.einsum("mi...,mn...,nj...->ij...", J, gamma_w, J)
    assert np.allclose(np.einsum("mi...,mj...->ij...", J, J), gp)
    h = conformal_h(gamma)
    Lh = tt.tt_project(h, g)
    G = gauge.gauge_piece(h, g)
    hTT_w = tt.tt_project(hw, g)
    err_raw = rms(Lh - hTT_w)
    err_cor = rms(Lh - G - hTT_w)
    assert err_cor < 0.01 * err_raw, (err_raw, err_cor)
    assert err_cor < 5e-3 * rms(hTT_w), (err_cor, rms(hTT_w))
