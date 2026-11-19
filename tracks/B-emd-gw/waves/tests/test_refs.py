"""Checks of the references of the waves package (no simulation output needed).

    python3 -m pytest -q -p no:cacheprovider tracks/B-emd-gw/waves/tests
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wlib import refs, weylref  # noqa: E402
from gwdiag import weyl  # noqa: E402
from gwdiag.analytic import Wave, wave_adm  # noqa: E402
from gwdiag.grid import Grid  # noqa: E402


def test_flrw_mode_closed_form_vs_ode():
    t = np.linspace(0.0, 10.0, 81)
    for kn in (np.pi / 2 * np.sqrt(2.0), 2.0, 7.3):
        T, Td = refs.flrw_mode(t, kn)
        To, Tdo = refs.flrw_mode_ode(t, kn)
        assert np.max(np.abs(T - To)) < 1e-11 * max(1.0, np.max(np.abs(T)))
        assert np.max(np.abs(Td - Tdo)) < 1e-10
        assert abs(T[0]) < 1e-15 and abs(Td[0] - 1.0) < 1e-13


def test_flat_amplitudes_of_generator_formula():
    g = Grid((12, 12, 12), (1.0, 1.0, 1.0))
    kv = 2 * np.pi * np.array([1.0, 1.0, 1.0])
    ep, ex, _, _ = refs.basis(kv)
    X, Y, Z = g.mesh()
    t = 0.37
    amp, ampx, phx = 1e-6, 5e-7, 1.0
    Phi = kv[0] * X + kv[1] * Y + kv[2] * Z - np.linalg.norm(kv) * t
    h = (amp * ep[:, :, None, None, None] * np.sin(Phi)
         + ampx * ex[:, :, None, None, None] * np.sin(Phi + phx))
    P, Xa = refs.pol_amplitudes(h, g, kv)
    Pe, Xe, _, _ = refs.flat_amplitudes(t, np.linalg.norm(kv), amp, ampx, phx)
    assert abs(P - Pe) < 1e-20 and abs(Xa - Xe) < 1e-20


def _rel(a, b):
    return np.sqrt(np.mean(np.abs(a - b) ** 2)) / np.sqrt(np.mean(np.abs(b) ** 2))


def test_closed_form_flat_vs_gwdiag():
    g = Grid((16, 16, 16), (1.0, 1.0, 1.0))
    m = (1, 1, 1)
    w = Wave(m, -1j * 1e-6, -1j * 5e-7 * np.exp(1j))
    gamma, K, lin = wave_adm([w], g, t=0.21)
    kv = 2 * np.pi * np.array(m, float)
    n = kv / np.linalg.norm(kv)
    E, B = weyl.electric_magnetic(gamma, K, g, order="spectral")
    rms = lambda f: np.sqrt(np.mean(np.abs(f) ** 2))  # noqa: E731
    fwd = weyl.psi4(E, B, gamma, g, direction=n)
    cf = weylref.psi4_from_tt(lin["h"], lin["hd"], 1.0, 0.0, g, n)
    assert _rel(cf, fwd) < 1e-5
    # backward direction: zero for the forward wave (both at rounding of the forward one)
    bwd = weyl.psi4(E, B, gamma, g, direction=-n)
    cb = weylref.psi4_from_tt(lin["h"], lin["hd"], 1.0, 0.0, g, -n)
    assert rms(cb) < 1e-10 * rms(fwd) and rms(bwd) < 1e-6 * rms(fwd)


def test_closed_form_flrw_vs_gwdiag_and_inversion():
    L = 4.0
    g = Grid((16, 16, 16), (L, L, L), (0.0, 0.0, 0.0))
    kv = 2 * np.pi / L * np.array([1.0, 1.0, 0.0])
    kn = np.linalg.norm(kv)
    t = 3.1
    a, calH, _ = refs.background(t)
    P, X, Pd, Xd = refs.flrw_amplitudes(t, kn, 2e-6, 1e-6, 0.0, 1.0)
    h = refs.tensor_field(P, X, g, kv)
    hp = refs.tensor_field(Pd, Xd, g, kv)
    gamma = a ** 2 * (np.eye(3)[:, :, None, None, None] + h)
    K = -(calH / a) * gamma - 0.5 * a * hp
    E, B = weyl.electric_magnetic(gamma, K, g, order="spectral")
    n = kv / kn
    M = weylref.inversion_matrix(g, kv, a, calH)
    coeffs = []
    for s in (+1, -1):
        full = weyl.psi4(E, B, gamma, g, direction=s * n)
        cf = weylref.psi4_from_tt(h, hp, a, calH, g, s * n)
        assert _rel(cf, full) < 1e-5
        coeffs.append(full)
    c = weylref.psi4_coeffs(coeffs[0], coeffs[1], g, kv)
    Pi, Xi, Pdi, Xdi = weylref.invert(c, M)
    scale = abs(P) + abs(Pd) / kn
    for u, v in ((Pi, P), (Xi, X), (Pdi / kn, Pd / kn), (Xdi / kn, Xd / kn)):
        assert abs(u - v) < 1e-5 * scale
    assert np.linalg.cond(M) < 1e3


def test_inversion_exact_on_closed_form():
    g = Grid((8, 8, 8), (1.0, 1.0, 1.0))
    kv = 2 * np.pi * np.array([1.0, 1.0, 1.0])
    rng = np.random.default_rng(3)
    u = rng.normal(size=8)
    P, X, Pd, Xd = u[0] + 1j * u[1], u[2] + 1j * u[3], u[4] + 1j * u[5], u[6] + 1j * u[7]
    for a, calH in ((1.0, 0.0), (2.5, 0.6)):
        h = refs.tensor_field(P, X, g, kv)
        hp = refs.tensor_field(Pd, Xd, g, kv)
        n = kv / np.linalg.norm(kv)
        f = weylref.psi4_from_tt(h, hp, a, calH, g, n)
        b = weylref.psi4_from_tt(h, hp, a, calH, g, -n)
        c = weylref.psi4_coeffs(f, b, g, kv)
        M = weylref.inversion_matrix(g, kv, a, calH)
        r = weylref.invert(c, M)
        for x, y in zip(r, (P, X, Pd, Xd)):
            assert abs(x - y) < 1e-10 * (1 + abs(y))
