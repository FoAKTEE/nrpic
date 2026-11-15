"""Unit tests of the expanding-ball package (run: python3 -m pytest -q tests/)."""

import math
import os
import sys

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import hyp2f1

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
from expball import exact, mesh, model as M, particles, table  # noqa: E402

TH = dict(delta_c=1.0, R1=2.4, R2=6.0)


@pytest.fixture(scope="module")
def balls():
    return dict(flat=M.Ball.from_HRb(0.5),
                tophat=M.Ball.from_HRb(0.5, profile=M.TopHat(**TH)),
                smooth=M.Ball.from_HRb(0.5, profile=M.SmoothTopHat(**TH)),
                taper=M.Ball.from_HRb(0.5, edge_width=0.8))


# ------------------------------------------------------------------ F, y(Delta)
def test_Fm1_matches_hyp2f1():
    y = np.array([-3.0, -0.6, -0.4999, -0.1, 1e-6, 0.3, 0.4999, 0.5, 0.9])
    assert np.allclose(M.Fm1(y), hyp2f1(0.5, 1.5, 2.5, y) - 1, rtol=1e-13, atol=1e-16)


def test_y_of_Delta_inverse_and_linear_limit():
    D = np.array([-0.5, -1e-3, 1e-9, 1e-4, 0.1, 1.0, 3.0, 4.4])
    y = M.y_of_Delta(D)
    assert np.allclose(1 + M.Fm1(y), np.sqrt(1 + D), rtol=1e-14)
    assert abs(M.y_of_Delta(np.array([1e-8]))[0] / 1e-8 - 5 / 3) < 1e-6


# ------------------------------------------------------------------ the slice
def test_flat_ball(balls):
    b = balls["flat"]
    assert b.H * b.Rb == pytest.approx(0.5) and b.M == pytest.approx(1.0)
    R = np.array([0.0, 1.0, 7.9, 8.0, 8.1, 20.0])
    c = b.at(R)
    assert np.allclose(c["v"][:4], b.H * R[:4]) and np.allclose(c["KL"][:4], -b.H)
    assert np.allclose(c["KT"][:4], -b.H)
    v = np.sqrt(2 * b.M / R[4:])
    assert np.allclose(c["KL"][4:], v / (2 * R[4:])) and np.allclose(c["KT"][4:], -v / R[4:])
    assert np.all(c["E"] == 0) and np.allclose(b.G(R), 0)
    assert np.allclose(4 * c["KL"] * c["KT"] + 2 * c["KT"] ** 2, 16 * math.pi * c["rho"])


@pytest.mark.parametrize("name", ["tophat", "smooth"])
def test_simultaneous_bang_time(balls, name):
    b = balls[name]
    R = np.array([0.5, 2.0, 2.39, 3.0, 4.5, 5.9])
    c = b.at(R)
    t = exact.t_expanding(R, c["m"], c["E"])
    assert np.allclose(t, b.t_i, rtol=1e-13)
    for Ri, m, E in zip(R, c["m"], c["E"]):     # independent: quadrature of dR/v
        tq = quad(lambda r: 1 / math.sqrt(2 * m / r + 2 * E), 0, Ri, epsabs=0, epsrel=1e-13)[0]
        assert tq == pytest.approx(b.t_i, rel=1e-10)


@pytest.mark.parametrize("name", ["tophat", "smooth", "taper"])
def test_derivatives_match_finite_differences(balls, name):
    b = balls[name]
    R = np.array([0.7, 1.9, 3.3, 4.2, 5.5, 7.5, 8.3, 11.0])
    hh = 1e-3
    st = np.array([1, -8, 0, 8, -1]) / 12.0
    def fd(key):
        return sum(c * b.at(R + k * hh)[key] for c, k in zip(st, (-2, -1, 0, 1, 2))) / hh
    c = b.at(R)
    for key, dkey in (("m", "dm"), ("E", "dE"), ("v", "dv")):
        assert np.allclose(fd(key), c[dkey], rtol=1e-8, atol=1e-12), key


@pytest.mark.parametrize("name", ["tophat", "smooth", "taper", "flat"])
def test_radial_constraints(balls, name):
    """3R = -4 (R E)'/R^2, Hamiltonian and momentum (dKT/dR = (KL - KT)/R) in areal form."""
    b = balls[name]
    R = np.array([0.7, 1.9, 3.3, 4.2, 5.5, 7.5, 8.3, 11.0])
    hh = 1e-3
    st = np.array([1, -8, 0, 8, -1]) / 12.0
    def fd(fun):
        return sum(c * fun(R + k * hh) for c, k in zip(st, (-2, -1, 0, 1, 2))) / hh
    c = b.at(R)
    Ric = -4 * fd(lambda r: r * b.at(r)["E"]) / R ** 2
    Ham = Ric + 4 * c["KL"] * c["KT"] + 2 * c["KT"] ** 2 - 16 * math.pi * c["rho"]
    Mom = fd(lambda r: b.at(r)["KT"]) - (c["KL"] - c["KT"]) / R
    assert np.max(np.abs(Ham)) < 1e-9 * 6 * b.H ** 2
    assert np.max(np.abs(Mom)) < 1e-9 * b.H / b.Rb


def test_conformal_map_tophat_closed_form(balls):
    b = balls["tophat"]
    R = np.linspace(0.01, 2.4, 9)
    c = b.at(R)
    a2 = -2 * c["E"] / R ** 2
    s = np.sqrt(1 - a2 * R ** 2)
    s1 = math.sqrt(1 - a2[0] * 2.4 ** 2)
    assert np.allclose(b.G(R) - b.G(np.array([2.4])), np.log((1 + s) / (1 + s1)), atol=1e-14)
    rb = b.rbar_of_R(R)
    assert np.allclose(b.R_of_rbar(rb), R, rtol=1e-14)
    assert np.allclose(b.G(np.array([6.0, 7.0, 9.0])), 0)


@pytest.mark.parametrize("name", ["tophat", "smooth", "taper"])
def test_interpolant_accuracy(balls, name):
    b = balls[name]
    I = b.radial()
    x = np.random.default_rng(3).uniform(1e-3, I.rbar_max, 400)
    ex = b.slice_at_rbar(x)
    ip = I(x)
    for k in ("u", "KL", "KT", "rho", "betar", "R"):
        assert np.max(np.abs(ip[k] - ex[k])) <= 1e-12 * np.max(np.abs(ex[k])), k


def test_no_antitrapped_surface(balls):
    for b in balls.values():
        q, _ = b.max_compactness()
        assert q < 1
    assert balls["flat"].max_compactness()[0] == pytest.approx(0.25, rel=1e-3)


# ------------------------------------------------------------------ table format 2
def test_lagrange4_exact_for_cubics():
    r = np.arange(40) * 0.1
    p = 1.0 - 2 * r + 0.5 * r ** 2 - 0.3 * r ** 3
    x = np.linspace(0, 3.7, 77)
    assert np.allclose(table.lagrange4(p, 0.1, x), 1.0 - 2 * x + 0.5 * x ** 2 - 0.3 * x ** 3,
                       atol=1e-12)


@pytest.mark.parametrize("name", ["smooth", "flat"])
def test_table_roundtrip_and_exterior(balls, name, tmp_path):
    b = balls[name]
    p = str(tmp_path / "t.tab")
    table.write_format2(p, b, drbar=0.002, rbar_max=12.0, header=dict(model=name))
    T = table.Format2Table(p)
    assert T.hdr["format"] == "2" and T.hdr["exterior"] == "pg"
    r = np.array([12.5, 20.0, 100.0])
    t = T(r)
    f = b.fields(r, ("u", "KL", "KT", "betar"))
    for k in ("u", "KL", "KT", "betar"):
        assert np.allclose(t[k], f[k], rtol=1e-13, atol=1e-16), k
    x = np.random.default_rng(5).uniform(0.01, 7.9, 200)
    x = x[np.min(np.abs(x[:, None] - b.rbar_edges()[None, :]), axis=1) > 0.01]
    t = T(x)
    f = b.fields(x, ("u", "KL", "KT"))
    assert np.max(np.abs(t["KL"] - f["KL"])) < 1e-8 * b.H


# ------------------------------------------------------------------ particles
@pytest.mark.parametrize("name", ["smooth", "flat"])
def test_stratified_sample(balls, name):
    b = balls[name]
    x, u, m, sp = particles.sample(b, 20000, "stratified", seed=2)
    assert np.all(u == 0) and m.sum() == pytest.approx(b.rest_mass(), rel=1e-13)
    r = np.sqrt((x * x).sum(1))
    F = b.rest_mass_inside(np.sort(r)) / b.rest_mass()
    ks = np.max(np.abs(F - (np.arange(len(r)) + 0.5) / len(r)))
    assert ks < 2e-4          # stratified in the mass fraction: one particle per stratum


def test_lattice_sample(balls):
    b = balls["smooth"]
    x, u, m, sp = particles.lattice(b, 40)
    assert m.sum() == pytest.approx(b.rest_mass(), rel=1e-12)
    x2, _, m2, _ = particles.lattice(b, 40, surface_correction=False)
    assert abs(m2.sum() / b.rest_mass() - 1) < 0.05


# ------------------------------------------------------------------ exact solution
@pytest.mark.parametrize("name", ["tophat", "smooth", "flat", "taper"])
def test_shell_evolution(balls, name):
    b = balls[name]
    Ri = np.array([0.3, 2.0, 2.6, 4.0, 5.9, 7.0, b.R_out])
    sh = exact.Shells(b, Ri)
    assert np.allclose(sh.R(np.array(0.0)), Ri, rtol=1e-12)
    tau = np.linspace(0.5, 40.0, 7)
    hh = 1e-4
    dR = (sh.R(tau + hh) - sh.R(tau - hh)) / (2 * hh)
    assert np.allclose(dR, sh.dRdtau(tau), rtol=1e-6, atol=1e-10)
    # shells whose crunch lies beyond 1e4 t_i (E -> 0 at the edge of the core) are skipped:
    # there the horizon time differs from the crunch time by less than double precision
    b_ = sh.bound & (sh.tau_c < 1e4 * b.t_i)
    if np.any(b_):
        Rta = np.array([sh.R(np.array(t))[k, ...] for k, t in enumerate(sh.tau_ta)])[b_]
        assert np.allclose(Rta, sh.R_max[b_], rtol=1e-10)
        Rah = np.array([sh.R(np.array(t))[k, ...] for k, t in enumerate(sh.tau_ah)])[b_]
        assert np.allclose(Rah, 2 * sh.m[b_], rtol=1e-8)
        assert np.allclose(sh.tau_ah_cycloid()[b_], sh.tau_ah[b_], rtol=1e-9)
    if name == "flat":
        assert np.allclose(sh.R(tau)[:-1], Ri[:-1, None] * (1 + 1.5 * b.H * tau) ** (2 / 3),
                           rtol=1e-12)


# ------------------------------------------------------------------ mesh and deposit
def test_residual_order_quick(balls):
    b = balls["smooth"]
    src = mesh.radial_source(b)
    reg = {"in": lambda r: r < 7.0}
    e = [mesh.residuals(src, N, 10.0, orders=(4,), regions=reg, norm=6 * b.H ** 2)[4]["in"]
         for N in (32, 64)]
    # smoke test only (pre-asymptotic at these N; the measured orders are those of the
    # registered convergence run): H drops by > 10, M by > 2^2.5
    assert e[0]["H_L2"] / e[1]["H_L2"] > 10 and e[0]["M_L2"] / e[1]["M_L2"] > 2 ** 2.5


def test_general_form_agrees(balls):
    b = balls["smooth"]
    src = mesh.radial_source(b)
    Hg, Mg, rb = mesh.residuals_general(src, 20, 10.0, order=4, norm=6 * b.H ** 2)
    Hs = mesh.residuals(src, 20, 10.0, orders=(4,), regions={"in": lambda r: r < 7.0},
                        norm=6 * b.H ** 2)[4]["in"]
    c = rb < 7.0
    # different discretizations of the same operator: same size of truncation error
    assert 0.2 < np.sqrt(np.mean(Hg[c] ** 2)) / Hs["H_L2"] < 5


def test_cic_conserves_mass():
    rng = np.random.default_rng(0)
    x = rng.uniform(-0.9, 0.9, (1000, 3))
    m = rng.random(1000)
    d = mesh.deposit_cic(x, m, 16, 1.0)
    assert d.sum() == pytest.approx(m.sum(), rel=1e-13)
