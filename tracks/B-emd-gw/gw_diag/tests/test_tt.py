"""Unit tests of the TT projection, polarizations, helicity and energy spectra (P1, P5)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gwdiag import Grid, tt, analytic  # noqa: E402

GRID = Grid((24, 20, 18), (1.3, 1.1, 0.9), (0.1, -0.4, 0.2))   # nx != ny != nz, Lx != Ly != Lz


def rand_sym(grid, seed=0):
    rng = np.random.default_rng(seed)
    S = rng.normal(size=(3, 3) + grid.shape)
    return 0.5 * (S + np.einsum("ij...->ji...", S))


def test_projector_properties():
    S = rand_sym(GRID)
    T = tt.tt_project(S, GRID)
    TT = tt.tt_project(T, GRID)
    scale = np.abs(T).max()
    assert np.abs(TT - T).max() < 1e-12 * scale                        # idempotent
    assert np.abs(T - np.einsum("ij...->ji...", T)).max() < 1e-12 * scale
    assert np.abs(np.einsum("ii...->...", T)).max() < 1e-12 * scale    # traceless
    F = tt.tensor_rfft(T)
    k = GRID.kvec(real=True)
    div = np.einsum("a...,ab...->b...", k, F)
    assert np.abs(div).max() < 1e-10 * np.abs(F).max() * np.abs(k).max()


def test_longitudinal_and_trace_removed():
    rng = np.random.default_rng(3)
    X, Y, Z = GRID.mesh()
    # S = d_i V_j + d_j V_i + delta psi with V, psi band-limited: exactly removed
    V = analytic.random_modefield(GRID, 1.0, 5, 3, seed=4)
    W = analytic.random_modefield(GRID, 1.0, 5, 3, seed=5)
    H = V.hess() + W.hess()
    psi = analytic.random_modefield(GRID, 1.0, 5, 3, seed=6).val()
    S = 2 * H + np.eye(3)[:, :, None, None, None] * psi
    T = tt.tt_project(S, GRID)
    assert np.abs(T).max() < 1e-12 * np.abs(S).max()


def single_wave(m, ap, ax, grid=GRID):
    return [analytic.Wave(m, ap, ax)]


def test_plane_waves_recovered_exactly():
    for m in [(1, 0, 0), (0, 2, 0), (0, 0, -1), (1, 1, 0), (2, -1, 1), (-1, 1, 1)]:
        waves = single_wave(m, 0.7 + 0.2j, -0.3 + 0.5j)
        h, hd, hdd, _ = analytic.wave_fields(waves, GRID, t=0.37)
        hT = tt.tt_project(h, GRID)
        assert np.abs(hT - h).max() < 1e-12
        exp = analytic.waves_expected(waves, GRID)
        sp = tt.gw_spectrum(hT, tt.tt_project(hd, GRID), GRID)
        assert abs(sp["rho_kin_total"] / exp["rho_kin_total"] - 1) < 1e-12
        assert abs(sp["rho_grad_total"] / exp["rho_kin_total"] - 1) < 1e-12
        # polarization amplitudes along the wave's own direction
        k = analytic.lattice_k(GRID, m)
        hp, hx = tt.polarization_along(hT, k)
        X, Y, Z = GRID.mesh()
        ph = np.exp(1j * (k[0] * X + k[1] * Y + k[2] * Z - np.linalg.norm(k) * 0.37))
        assert np.abs(hp - ((0.7 + 0.2j) * ph).real).max() < 1e-12
        assert np.abs(hx - ((-0.3 + 0.5j) * ph).real).max() < 1e-12


def test_from_adm_amplitude_scaling():
    """P1(c), corrected: the O(h^2) part of tilde gamma - delta is a pure trace, removed by
    Lambda, so the relative error of h^TT and d_tau h^TT is O(A^2) (JOURNAL.md, P1 outcome)."""
    errs = []
    amps = [1e-4, 1e-3, 1e-2]
    waves0 = analytic.random_waves(GRID, 6, 1, 3, amp=1.0, seed=2)
    for A in amps:
        waves = [analytic.Wave(w.m, A * w.ap, A * w.ax) for w in waves0]
        gamma, K, ref = analytic.wave_adm(waves, GRID, t=0.2)
        hT, hdT, chib = tt.tt_from_adm(gamma, K, GRID)
        e1 = np.abs(hT - ref["h"]).max() / np.abs(ref["h"]).max()
        e2 = np.abs(hdT - ref["hd"]).max() / np.abs(ref["hd"]).max()
        errs.append(max(e1, e2))
    errs = np.array(errs)
    assert errs[-1] < 1e-3
    slope = np.polyfit(np.log10(amps), np.log10(errs), 1)[0]
    assert 1.8 < slope < 2.2, (errs, slope)


def test_hand_written_circular_waves():
    """P1(d): helicity from the rotation sense of hand-written tensors."""
    g = Grid((8, 8, 32), (1.0, 1.0, 2.0))
    X, Y, Z = g.mesh()
    k = 2 * np.pi * 3 / 2.0
    A = 1e-3
    for sgn_motion in (+1, -1):          # +1: moving along +z (phase kz - wt); -1: along -z
        t = 0.123
        ph = k * Z - sgn_motion * k * t
        h = np.zeros((3, 3) + g.shape)
        hd = np.zeros_like(h)
        h[0, 0] = A * np.cos(ph)
        h[1, 1] = -A * np.cos(ph)
        h[0, 1] = h[1, 0] = A * np.sin(ph)
        hd[0, 0] = A * np.sin(ph) * sgn_motion * k
        hd[1, 1] = -hd[0, 0]
        hd[0, 1] = hd[1, 0] = -A * np.cos(ph) * sgn_motion * k
        hel = tt.helicity_spectrum(h, hd, g)
        tot = hel["rho_plus_total"] + hel["rho_minus_total"]
        sp = tt.gw_spectrum(h, hd, g)
        assert abs(tot / (sp["rho_kin_total"] + sp["rho_grad_total"]) - 1) < 1e-12
        # pattern at z = 0: (h_xx, h_xy) = A (cos(s w t), -sin(s w t)) for s = +1:
        # clockwise about +z while moving along +z -> helicity -2;
        # s = -1: counterclockwise about +z while moving along -z -> helicity -2.
        assert hel["rho_plus_total"] < 1e-12 * tot, (sgn_motion, hel["rho_plus_total"], tot)


def test_random_superposition_spectrum_and_helicity():
    """P5 at round-off level (fields given as h directly)."""
    g = Grid((32, 32, 32), (1.0, 1.0, 1.0))
    waves = analytic.random_waves(g, 30, 1, 5, slope=-1.0, amp=1.0, frac_plus=0.8, seed=11)
    exp = analytic.waves_expected(waves, g)
    for t in (0.0, 0.31):
        h, hd, _, _ = analytic.wave_fields(waves, g, t)
        sp = tt.gw_spectrum(tt.tt_project(h, g), tt.tt_project(hd, g), g)
        tot = sp["rho_kin_total"] + sp["rho_grad_total"]
        assert abs(tot / (2 * exp["rho_kin_total"]) - 1) < 1e-12
        # per shell
        ks = exp["k"]
        edges = np.append(sp["k"] - 0.5 * sp["dk"], sp["k"][-1] + 0.5 * sp["dk"])
        ref = np.histogram(ks, edges, weights=2 * exp["rho_kin"])[0]
        got = sp["rho_kin"] + sp["rho_grad"]
        assert np.abs(got - ref).max() < 1e-12 * ref.max()
        hel = tt.helicity_spectrum(h, hd, g)
        assert abs(hel["rho_plus_total"] / exp["rho_plus_total"] - 1) < 1e-12
        assert abs(hel["rho_minus_total"] / exp["rho_minus_total"] - 1) < 1e-12
