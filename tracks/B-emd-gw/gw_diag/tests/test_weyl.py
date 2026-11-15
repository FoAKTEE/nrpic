"""Unit tests of E_ij, B_ij and Psi_4 (P2, P3, P4 at a single resolution)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gwdiag import Grid, tt, weyl, analytic  # noqa: E402

GRID = Grid((20, 16, 24), (1.25, 1.0, 1.5), (0.0, 0.0, 0.0))


def rel(a, b):
    return np.abs(a - b).max() / np.abs(b).max()


def test_derivative_orders():
    g = Grid((32, 24, 16), (1.0, 0.75, 0.5))
    X, Y, Z = g.mesh()
    kx, ky, kz = 2 * np.pi * 2 / 1.0, 2 * np.pi / 0.75, 2 * np.pi / 0.5
    f = np.sin(kx * X + ky * Y - kz * Z)
    fx = kx * np.cos(kx * X + ky * Y - kz * Z)
    fyz = ky * kz * np.sin(kx * X + ky * Y - kz * Z)
    D = weyl.Deriv(g, "spectral")
    assert rel(D.d1(f, 0), fx) < 1e-12
    assert rel(D.d2(f, 1, 2), fyz) < 1e-12
    for p in (2, 4, 6):
        D = weyl.Deriv(g, p)
        e1 = rel(D.d1(f, 0), fx)
        D2 = weyl.Deriv(Grid((64, 48, 32), g.L), p)
        X2, Y2, Z2 = D2.g.mesh()
        e2 = rel(D2.d1(np.sin(kx * X2 + ky * Y2 - kz * Z2), 0),
                 kx * np.cos(kx * X2 + ky * Y2 - kz * Z2))
        assert abs(np.log2(e1 / e2) - p) < 0.3, (p, e1, e2)


def test_wave_E_B_psi4_spectral():
    A = 1e-8
    for m in [(0, 0, 2), (1, 0, 0), (1, 1, 1), (-1, 2, 0)]:
        waves = [analytic.Wave(m, A * (0.6 - 0.3j), A * (0.2 + 0.7j))]
        gamma, K, ref = analytic.wave_adm(waves, GRID, t=0.1)
        E, B = weyl.electric_magnetic(gamma, K, GRID, order="spectral")
        assert rel(E, ref["E_lin"]) < 1e-6
        assert rel(B, ref["B_lin"]) < 1e-6
        k = analytic.lattice_k(GRID, m)
        p4 = weyl.psi4(E, B, gamma, GRID, direction=k)
        hp, hx = tt.polarization_along(ref["hdd"], k)       # d_t^2 h_+, d_t^2 h_x
        assert rel(p4, hp - 1j * hx) < 1e-6
        p0 = weyl.psi0_like(E, B, gamma, GRID, direction=k)
        assert np.abs(p0).max() < 1e-6 * np.abs(p4).max()


def test_gauge_mode_weyl_converges_and_tt_quadratic():
    errs = {}
    for n in (16, 32):
        g = Grid((n, n, n), (1.0, 1.0, 1.0))
        gamma, K, alpha, beta = analytic.gauge_mode(g, 1e-3, seed=3)
        E, B = weyl.electric_magnetic(gamma, K, g, order=4)
        errs[n] = max(np.abs(E).max(), np.abs(B).max())
    assert abs(np.log2(errs[16] / errs[32]) - 4) < 0.5, errs
    g = Grid((16, 16, 16), (1.0, 1.0, 1.0))
    r = []
    for eps in (1e-4, 1e-3):
        gamma, K, alpha, beta = analytic.gauge_mode(g, eps, seed=3)
        hT, hdT, _ = tt.tt_from_adm(gamma, K, g)
        r.append(max(np.abs(hT).max(), np.abs(hdT).max()))
    assert abs(np.log10(r[1] / r[0]) - 2) < 0.1, r


def test_scalar_mode():
    g = Grid((24, 24, 24), (1.0, 1.0, 1.0))
    out = []
    for eps in (1e-5, 1e-4):
        gamma, K, ref = analytic.scalar_mode(g, eps, seed=5)
        E, B = weyl.electric_magnetic(gamma, K, g, order="spectral")
        LE = tt.tt_project(E, g)
        hT, hdT, _ = tt.tt_from_adm(gamma, K, g)
        out.append((np.abs(B).max(), np.abs(LE).max(), np.abs(hT).max(), rel(E, ref["E_lin"]),
                    np.abs(ref["E_lin"]).max()))
    for i in range(3):
        assert abs(np.log10(out[1][i] / out[0][i]) - 2) < 0.15, (i, out)
    assert out[0][3] < 1e-3            # E = E_lin to O(eps)
