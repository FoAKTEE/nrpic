#!/usr/bin/env python3
"""Validation of the NRPIC initial-data tools against Wu & Most (arXiv:2611.12831).

Run with `python3 -m pytest python/tests/test_initial_data.py` or directly as a
script, which also prints the comparison table with the paper values.
"""

import os
import sys
import tempfile

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "python"))

import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
from scipy.integrate import quad  # noqa: E402

from nrpic import clumps as clm  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import oppenheimer_snyder as osn  # noqa: E402
from nrpic import sampling  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402
from nrpic.spheroid import ProlateSpheroid  # noqa: E402

# (y_c, z_c, R/M, M_0/M), paper Table I
PAPER_TABLE = [(0.900, 0.125, 16.4282, 1.019453),
               (0.819, 0.236, 9.9642, 1.030106),
               (0.605, 0.592, 5.7502, 1.035171),
               (0.500, 0.817, 5.0758, 1.023830),
               (0.283, 1.504, 4.5846, 0.961732)]


def _half_ulp(value_str):
    """Half a unit in the last printed digit of a paper number."""
    d = value_str.split(".")[1] if "." in value_str else ""
    return 0.5 * 10.0 ** (-len(d))


def _close(ours, paper_str, slack=1.0):
    return abs(ours - float(paper_str)) <= slack * _half_ulp(paper_str) + 1e-15


_MODELS = {}


def model(yc):
    if yc not in _MODELS:
        _MODELS[yc] = stc.STModel(yc)
    return _MODELS[yc]


_JEANS = {}


def jeans(**kw):
    key = tuple(sorted(kw.items()))
    if key not in _JEANS:
        _JEANS[key] = clm.JeansModel(**kw)
    return _JEANS[key]


# ----------------------------------------------------------------------------
# paper comparison (also printed in script mode)
# ----------------------------------------------------------------------------
def paper_comparison():
    rows = []
    for yc, zc, R, M0 in PAPER_TABLE:
        g = stc.st_global(yc)
        rows += [(f"y_c={yc:.3f} z_c", g["zc"], f"{zc:.3f}"),
                 (f"y_c={yc:.3f} R/M", g["R_over_M"], f"{R}"),
                 (f"y_c={yc:.3f} M_0/M", g["M0_over_M"], f"{M0:.6f}")]
    g = stc.st_global(0.5)
    rows += [("y_c=0.500 alpha_c", g["alpha_c"], "0.550442"),
             ("y_c=0.500 z_c", g["zc"], "0.816723"),
             ("y_c=0.500 E_b/M_0", g["Eb_over_M0"], "0.0232758")]
    t = stc.migration_target(0.5)
    rows += [("migration target y_c", t["yc"], "0.870743"),
             ("migration target alpha_c", t["alpha_c"], "0.859266"),
             ("migration target z_c", t["zc"], "0.163784")]
    rows += [("y_c=0.283 E_b/M_0", stc.st_global(0.283)["Eb_over_M0"], "-0.0398")]
    rows += [("y_c(z_c=0.199717) [late migration]", stc.yc_from_zc(0.199717), "0.844603")]
    rows += [("OS rbar_0/M (R_0=5M)", osn.isotropic_radius(5.0), "3.936"),
             ("OS M_rest/M (continuum)", osn.rest_mass(5.0), "1.155")]
    x, u, m, sp = sampling.sample_os(method="lattice", n_lat=124)
    rows += [("OS lattice n_lat=124 N_p", float(len(m)), "998592"),
             ("OS lattice n_lat=124 sum m_p/M", m.sum(), "1.155")]
    sph = ProlateSpheroid(0.9, 10.0)
    rows += [("prolate a/M (e=0.9, b=10M)", sph.a, "4.3589"),
             ("prolate M_rest/M", sph.rest_mass(), "1.09815")]
    rows += [("Jeans v_circ (M_env=0.76, R=30M)",
              jeans().newtonian_circular_speed()["v_circ"], "0.133215"),
             ("Jeans v_circ (M_env=0.76, y_c=0.907)",
              jeans(yc=0.907).newtonian_circular_speed()["v_circ"], "0.133215")]
    return rows


# ----------------------------------------------------------------------------
# Shapiro-Teukolsky sequence
# ----------------------------------------------------------------------------
def test_st_table_I():
    for yc, zc, R, M0 in PAPER_TABLE:
        g = stc.st_global(yc)
        assert _close(g["zc"], f"{zc:.3f}"), (yc, g["zc"], zc)
        assert _close(g["R_over_M"], f"{R}"), (yc, g["R_over_M"], R)
        assert _close(g["M0_over_M"], f"{M0:.6f}"), (yc, g["M0_over_M"], M0)


def test_st_yc05_and_migration_target():
    g = stc.st_global(0.5)
    assert _close(g["alpha_c"], "0.550442")
    assert _close(g["zc"], "0.816723")
    assert _close(g["Eb_over_M0"], "0.0232758")
    t = stc.migration_target(0.5)
    assert _close(t["yc"], "0.870743")
    assert _close(t["alpha_c"], "0.859266")
    assert _close(t["zc"], "0.163784")
    assert abs(t["Eb_over_M0"] - g["Eb_over_M0"]) < 1e-12
    assert abs(t["M0_over_M"] - g["M0_over_M"]) < 1e-11


def test_st_unbound_and_late_time_mapping():
    assert _close(stc.st_global(0.283)["Eb_over_M0"], "-0.0398")
    assert _close(stc.yc_from_zc(0.199717), "0.844603")


def test_st_binding_energy_maximum():
    mx = stc.binding_energy_maximum()
    assert 0.605 < mx["yc"] < 0.819
    for dy in (-1e-3, 1e-3):
        assert stc.eb_over_m0(mx["yc"] + dy) < mx["Eb_over_M0"]
    # Table I models: 0.900 and 0.819 on the stable side, the others beyond
    assert stc.st_global(0.605)["zc"] > mx["zc"] > stc.st_global(0.819)["zc"]


def test_st_profile_consistency():
    for yc in (0.9, 0.5, 0.283):
        md = model(yc)
        rs = md.rbar_s
        # matching to exterior isotropic Schwarzschild (value and slope)
        assert abs(md.psi(rs) - (1 + 0.5 / rs)) < 1e-13
        d = 1e-6 * rs
        slope_in = (md.psi(rs) - md.psi(rs - d)) / d
        assert abs(slope_in + 0.5 / rs ** 2) < 1e-5 * 0.5 / rs ** 2 + 1e-9
        assert abs(md.alpha(rs) - (1 - 0.5 / rs) / (1 + 0.5 / rs)) < 1e-13
        assert abs(md.rs_of(rs) - md.R) < 1e-10
        # closures: P_c / rho_c = zeta, rho = W rho_0, alpha W = E_0
        assert abs(md.P_c / md.rho_c - (1 - yc) / 3) < 1e-15
        r = np.linspace(0, rs, 101)[:-1]
        assert np.allclose(md.rho(r), md.W(r) * md.rho0(r), rtol=1e-9, atol=1e-14)
        assert np.allclose(md.alpha(r) * md.W(r), md.E0, rtol=1e-9)
        # rest mass from the isotropic-coordinate integral equals the areal one
        M0_iso = quad(lambda v: 4 * np.pi * v * v * md.psi(v) ** 6 * md.rho0(v),
                      0, rs, epsabs=0, epsrel=1e-12, limit=400)[0]
        assert abs(M0_iso / md.M0 - 1) < 1e-8, (yc, M0_iso, md.M0)
        assert abs(md.F(rs) - 1) < 1e-14 and md.F(0.0) == 0.0
        U = np.linspace(0, 1, 2001)
        assert np.max(np.abs(md.F(md.Finv(U)) - U)) < 1e-12


def test_st_hamiltonian_constraint():
    """flat Laplacian psi = -2 pi psi^5 rho on the uniform table grid (4th-order
    differences) and in the integral (Gauss) form."""
    for yc in (0.9, 0.819, 0.605, 0.5, 0.283):
        md = model(yc)
        r, u, a = stc.table_arrays(md, n_matter=4000)
        psi = 1 + u
        src = -2 * np.pi * psi ** 5 * md.rho(r)
        res = stc.radial_laplacian(r, psi) - src
        scale = np.max(np.abs(src))
        inner = r < 0.95 * md.rbar_s
        outer = (r > 1.05 * md.rbar_s) & np.isfinite(res)
        assert np.max(np.abs(res[inner])) < 1e-6 * scale, (yc, np.max(np.abs(res[inner])) / scale)
        assert np.max(np.abs(res[outer])) < 1e-6 * scale
        # integral form: rbar^2 psi' = -2 pi int_0^rbar psi^5 rho r'^2 dr'
        for f in (0.25, 0.5, 0.75, 1.0):
            R = f * md.rbar_s
            m_enc = np.interp(R, md.rbar, md.m)
            lhs = 0.5 * R * md.psi(R) * (np.sqrt(1 - 2 * m_enc / md.rs_of(R)) - 1)
            rhs = -2 * np.pi * quad(lambda v: md.psi(v) ** 5 * md.rho(v) * v * v, 0, R,
                                    epsabs=0, epsrel=1e-12, limit=400)[0]
            assert abs(lhs / rhs - 1) < 1e-6, (yc, f, lhs, rhs)


# ----------------------------------------------------------------------------
# Oppenheimer-Snyder
# ----------------------------------------------------------------------------
def test_os_slice():
    rb0 = osn.isotropic_radius(5.0)
    assert _close(rb0, "3.936")
    Mr = osn.rest_mass(5.0)
    assert _close(Mr, "1.155")
    q = quad(lambda r: 4 * np.pi * r * r * osn.rho0() * osn.psi(r) ** 6, 0, rb0,
             epsabs=0, epsrel=1e-13)[0]
    assert abs(q / Mr - 1) < 1e-12
    assert abs(osn.psi(rb0 * (1 - 1e-15)) - osn.psi(rb0 * (1 + 1e-15))) < 1e-12
    r, u, a = osn.table_arrays(5.0)
    psi = 1 + u
    src = -2 * np.pi * psi ** 5 * np.where(r <= rb0, osn.rho0(), 0.0)
    res = stc.radial_laplacian(r, psi) - src
    inner, outer = r < 0.99 * rb0, (r > 1.01 * rb0) & np.isfinite(res)
    assert np.max(np.abs(res[inner])) < 1e-6 * np.max(np.abs(src))
    assert np.max(np.abs(res[outer])) < 1e-6 * np.max(np.abs(src))


def test_os_lattice_count():
    assert sampling.os_lattice_count(124) == 998592
    x, u, m, sp = sampling.sample_os(method="lattice", n_lat=124)
    assert len(m) == 998592 and np.all(u == 0)
    assert _close(m.sum(), "1.155")
    assert abs(m.sum() / osn.rest_mass() - 1) < 5e-4
    assert np.max(np.abs(x.mean(0))) < 1e-12           # lattice symmetric about 0
    for N in (100, 1000, 10000):
        n = sampling.os_nlat_for(N)
        c = sampling.os_lattice_count(n)
        assert all(abs(sampling.os_lattice_count(k) - N) >= abs(c - N) for k in (n - 1, n + 1))


def test_os_cycloid_and_staley():
    R0 = 5.0
    tc = osn.collapse_time(R0)
    assert abs(tc - np.pi * np.sqrt(R0 ** 3 / 8)) < 1e-14
    eta = np.linspace(0, np.pi * 0.999, 50)
    tau = osn.cycloid_tau(eta, R0)
    assert np.max(np.abs(osn.eta_of_tau(tau, R0) - eta)) < 1e-9
    assert np.allclose(osn.cycloid_R(tau, R0), R0 * (1 + np.cos(eta)) / 2, rtol=1e-9)
    assert np.allclose(osn.cycloid_rho(tau, R0) / osn.rho0(R0) * (osn.cycloid_R(tau, R0) / R0) ** 3, 1)
    assert osn.staley_lower_bound(0.0, R0) == 1.0
    lb = osn.staley_lower_bound(np.linspace(0, 6, 61), R0)
    assert np.all(np.diff(lb) < 0)
    # small-tau expansion: R/R0 = 1 - M tau^2/(2 R0^3) -> alpha_LL ~ 1 - 3 M tau^2 / R0^3
    t = 0.01
    assert abs((1 - osn.staley_lower_bound(t, R0)) / (3 * t * t / R0 ** 3) - 1) < 1e-4


def test_trumpet_lapse():
    k = osn.trumpet_constants()
    assert abs(k["C"] - 1.24672) < 1e-5 and abs(k["R0"] - 1.31241) < 1e-5
    R = np.concatenate([np.linspace(k["R0"], 3, 400, endpoint=False), np.geomspace(3, 1e4, 200)])
    al = osn.trumpet_lapse(R)
    res = al ** 2 - 1 + 2 / R - k["C2"] * np.exp(al) / R ** 4
    assert np.max(np.abs(res)) < 1e-13
    assert np.all(np.diff(al) > 0) and abs(al[0]) < 1e-7
    assert abs(al[-1] - np.sqrt(1 - 2 / R[-1])) < 1e-10      # -> Schwarzschild lapse
    near = np.abs(R - k["R_crit"]) < 0.05
    assert np.max(np.abs(np.diff(np.diff(al[near])))) < 1e-4   # smooth through R_crit


# ----------------------------------------------------------------------------
# prolate spheroid
# ----------------------------------------------------------------------------
def test_spheroid_fields():
    sph = ProlateSpheroid(0.9, 10.0)
    assert _close(sph.a, "4.3589")
    assert _close(sph.rest_mass(), "1.09815")
    assert abs(sph.a ** 2 * sph.b * (2 * sph.Ja0 + sph.Jb0) - 2) < 1e-13
    # psibar -> 1 + M/(2r): the remainder is the O(r^-3) quadrupole
    Q = 0.5 * (sph.b ** 2 - sph.a ** 2) / 5
    for r in (100.0, 1000.0):
        assert abs((sph.psibar(0, 0, r) - 1 - 0.5 / r) * r ** 3 / Q - 1) < 0.05
        assert abs((sph.psibar(r, 0, 0) - 1 - 0.5 / r) * r ** 3 / (-Q / 2) - 1) < 0.05
    # flat Laplacian by second differences
    h = 1e-3
    rng = np.random.default_rng(0)
    p = rng.uniform(-12, 12, (5000, 3)) * np.array([0.5, 0.5, 1.0])
    f = sph.psibar
    lap = sum(f(*(p + h * e).T) + f(*(p - h * e).T) for e in np.eye(3)) - 6 * f(*p.T)
    lap /= h * h
    s2 = sph.s2(*p.T)
    target = 4 * np.pi * sph.rhoN
    assert np.max(np.abs(lap[s2 < 0.95] + target)) < 1e-5 * target
    assert np.max(np.abs(lap[s2 > 1.05])) < 1e-5 * target
    # continuity at the surface
    th = np.linspace(0, np.pi, 9)
    xs = np.stack([sph.a * np.sin(th), 0 * th, sph.b * np.cos(th)], axis=1)
    assert np.max(np.abs(f(*(xs * (1 - 1e-10)).T) - f(*(xs * (1 + 1e-10)).T))) < 1e-9
    # closed-form rest mass against direct quadrature in s (shells of psibar)
    M_num = quad(lambda s: 4 * np.pi * sph.a ** 2 * sph.b * s * s * 2 * sph.rhoN *
                 (sph.c0 - (sph.cR * 2 * sph.a ** 2 + sph.cz * sph.b ** 2) * s * s / 3),
                 0, 1)[0]
    assert abs(M_num / sph.rest_mass() - 1) < 1e-12


# ----------------------------------------------------------------------------
# samplers
# ----------------------------------------------------------------------------
def _ecdf_dev(samples, cdf):
    s = np.sort(samples)
    n = len(s)
    Fv = cdf(s)
    return max(np.max(np.arange(1, n + 1) / n - Fv), np.max(Fv - np.arange(n) / n))


def test_sampler_os():
    rb0, Mr = osn.isotropic_radius(), osn.rest_mass()
    F = lambda v: osn.F(v)
    for N in (100, 10000):
        x, u, m, sp = sampling.sample_os(N, "mc", seed=7)
        r = np.linalg.norm(x, axis=1)
        assert len(m) == N and np.all(r <= rb0) and np.all(u == 0) and np.all(sp == 0)
        assert abs(m.sum() / Mr - 1) < 1e-14
        assert stats.kstest(r, F).pvalue > 1e-3
        x, u, m, sp = sampling.sample_os(N, "stratified", seed=7)
        r = np.linalg.norm(x, axis=1)
        assert _ecdf_dev(r, F) <= 1.0 / N + 1e-9
    # lattice: mass-weighted cumulative distribution
    x, u, m, sp = sampling.sample_os(method="lattice", n_lat=40)
    r = np.linalg.norm(x, axis=1)
    for f in (0.5, 0.7, 0.9):
        assert abs(m[r <= f * rb0].sum() / osn.rest_mass_inside(f * rb0) - 1) < 1e-2
    assert abs(m.sum() / Mr - 1) < 2e-3
    x, u, m, sp = sampling.sample_os(N=1000, method="lattice")
    assert len(m) == sampling.os_lattice_count(sampling.os_nlat_for(1000))


def test_sampler_st_distribution():
    md = model(0.819)
    for N in (100, 10000):
        x, u, m, sp = sampling.sample_st(md, N, "mc", seed=3)
        r = np.linalg.norm(x, axis=1)
        assert abs(m.sum() / md.M0 - 1) < 1e-14 and np.all(r <= md.rbar_s)
        assert stats.kstest(r, md.F).pvalue > 1e-3
        x, u, m, sp = sampling.sample_st(md, N, "stratified", seed=3)
        r = np.linalg.norm(x, axis=1)
        assert _ecdf_dev(r, md.F) <= 1.0 / N + 1e-9
        ct = x[:, 2] / r
        assert _ecdf_dev(ct, lambda c: (c + 1) / 2) <= 1.0 / N + 1e-9
        # velocity direction cosines stratified as well
        q = u / md.psi(r)[:, None] ** 2
        qm = np.linalg.norm(q, axis=1)
        good = qm > 0
        assert np.allclose(qm, md.q(r), rtol=1e-12, atol=1e-15)
        cv = q[good, 2] / qm[good]
        assert _ecdf_dev(cv, lambda c: (c + 1) / 2) <= 1.0 / good.sum() + 1e-9


def _shell(md, f, r1, r2):
    return quad(lambda v: 4 * np.pi * v * v * md.psi(v) ** 6 * f(v), r1, r2,
                epsabs=0, epsrel=1e-11, limit=200)[0]


def test_sampler_st_moments():
    """Particle moments in proper-volume shells against the closures:
    rho_0, rho = E (sum m W / V), radial and tangential pressures
    (sum m q_r^2/W / V, sum m q_t^2/(2W) / V) and the momentum density."""
    for yc in (0.819, 0.5):
        md = model(yc)
        for method in ("mc", "stratified"):
            x, u, m, sp = sampling.sample_st(md, 20000, method, seed=11)
            r = np.linalg.norm(x, axis=1)
            nh = x / r[:, None]
            q = u / md.psi(r)[:, None] ** 2
            W = np.sqrt(1 + np.sum(q * q, axis=1))
            qr = np.sum(q * nh, axis=1)
            qt2 = np.sum(q * q, axis=1) - qr ** 2
            edges = md.Finv(np.linspace(0, 1, 9))
            edges[-1] = md.rbar_s * (1 + 1e-12)
            zmax = 0.0
            for i in range(8):
                r1, r2 = edges[i], edges[i + 1]
                sel = (r >= r1) & (r < r2)
                V = _shell(md, lambda v: 1.0, r1, r2)
                Pexp = _shell(md, md.P, r1, r2) / V
                expect = [md.M0 * (md.F(r2) - md.F(r1)) / V, _shell(md, md.rho, r1, r2) / V,
                          Pexp, Pexp]
                gs = [np.ones(sel.sum()), W[sel], qr[sel] ** 2 / W[sel], qt2[sel] / (2 * W[sel])]
                for e, g in zip(expect, gs):
                    est = np.sum(m[sel] * g) / V
                    sig = np.sqrt(np.sum((m[sel] * g) ** 2)) / V
                    zmax = max(zmax, abs(est - e) / sig)
                # momentum density ~ 0
                Sr = np.sum(m[sel] * qr[sel])
                assert abs(Sr) < 5 * np.sqrt(np.sum((m[sel] * qr[sel]) ** 2))
            assert zmax < 4.5, (yc, method, zmax)
            if method == "stratified":
                # exactly one particle per equal-mass stratum: shell masses exact
                counts = np.histogram(r, edges)[0]
                assert np.all(counts == 20000 // 8)


def test_sampler_st_perturbations():
    md = model(0.605)
    N = 20000
    x0, u0, m0, _ = sampling.sample_st(md, N, "stratified", seed=5)
    x1, u1, m1, _ = sampling.sample_st(md, N, "stratified", seed=5, vpert=0.01)
    r = np.linalg.norm(x1, axis=1)
    nh = x1 / r[:, None]
    q0 = u0 / md.psi(r)[:, None] ** 2
    q1 = u1 / md.psi(r)[:, None] ** 2
    assert np.allclose(x0, x1)
    dq = np.sum((q1 - q0) * nh, axis=1)
    assert np.allclose(dq, -0.01 * md.q(r), rtol=1e-10, atol=1e-15)
    vr = np.sum(q1 * nh, axis=1) / W_of(q1)
    vloc = md.q(r) / md.W(r)
    w = vloc > 0
    # mean radial three-velocity in units of the local speed ~ -0.01
    est = np.mean(vr[w] / vloc[w])
    assert abs(est + 0.01) < 5 * np.sqrt(1.0 / 3.0 / w.sum())
    x2, u2, m2, _ = sampling.sample_st(md, N, "stratified", seed=5, dpert=0.1)
    r2 = np.linalg.norm(x2, axis=1)
    assert np.allclose(r2 * 1.1 ** (1 / 3), np.linalg.norm(x0, axis=1))
    assert np.allclose(u2 / md.psi(r2)[:, None] ** 2, q0)


def W_of(q):
    return np.sqrt(1 + np.sum(q * q, axis=1))


def test_sampler_spheroid():
    sph = ProlateSpheroid(0.9, 10.0)
    for N in (100, 10000):
        x, u, m, sp = sampling.sample_spheroid(N, seed=2, spheroid=sph)
        assert len(m) == N and np.all(u == 0) and np.all(sph.s2(*x.T) <= 1 + 1e-12)
        assert abs(m.sum() / sph.rest_mass() - 1) < 1e-14
        n4 = N // 4
        b = x[:n4]
        assert np.allclose(x[n4:2 * n4], b * [1, 1, -1])
        assert np.allclose(x[2 * n4:3 * n4], b * [-1, -1, 1])
        assert np.allclose(x[3 * n4:], -b)
        assert np.max(np.abs(x.mean(0))) < 1e-12
        # the images share s and |z|: test the base set
        assert stats.kstest(np.sqrt(sph.s2(*b.T)), sph.F_s).pvalue > 1e-3
        assert stats.kstest(b[:, 2] / sph.b, sph.F_z).pvalue > 1e-3
    x, u, m, sp = sampling.sample_spheroid(1001, seed=1, symmetrize=False, spheroid=sph)
    assert len(m) == 1001
    try:
        sampling.sample_spheroid(1001, seed=1, spheroid=sph)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for N not divisible by 4")


# ----------------------------------------------------------------------------
# cluster with two Gaussian clumps (Jeans problem, paper lines 1335-1338)
# ----------------------------------------------------------------------------
def _random_dirs(n, seed):
    v = np.random.default_rng(seed).normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1)[:, None]


def test_jeans_psi_asymptotics():
    """(a) psi_tot -> 1 + M/(2r), M = M_env + 2 m_c = 1; outside the matter psi_tot is
    the exact point-mass superposition, its remainder the clumps' quadrupole."""
    J = jeans()
    assert abs(J.M_adm - 1.0) < 1e-15
    n = _random_dirs(500, 0)
    Q = J.m_c * J.d ** 2                       # r (psi - 1) - 1/2 -> (Q/2)(3 n_x^2 - 1)/r^2
    for r in (1e2, 1e3, 1e4):
        x = r * n
        psi = J.psi(x)
        pm = 1 + J.M_env / (2 * r) + sum(0.5 * J.m_c / np.linalg.norm(x - J.centres[k], axis=1)
                                         for k in (1, 2))
        assert np.max(np.abs(psi - pm)) < 1e-14
        dev = r * sum(J.parts(x)) - 0.5           # psi_tot - 1 without its roundoff
        assert np.max(np.abs(dev)) <= Q / r ** 2 * (1 + 10 * (J.d / r) ** 2)
        quad_ = 0.5 * Q * (3 * n[:, 0] ** 2 - 1) / r ** 2
        # O(r^-4) remainder, plus the roundoff r * eps of u_env = psi_env - 1
        assert np.max(np.abs(dev - quad_)) < 3 * Q * J.d ** 2 / r ** 4 + 1e-15 * r
    # monopole: the sphere average of psi_tot - 1 is exactly 1/(2r) outside the matter
    mu, w = np.polynomial.legendre.leggauss(64)
    for r in (40.0, 100.0, 1e3):
        pts = r * np.stack([mu, np.sqrt(1 - mu * mu), 0 * mu], axis=1)
        avg = 0.5 * np.sum(w * (J.psi(pts) - 1))
        assert abs(avg * 2 * r - 1) < 1e-12, (r, avg * 2 * r - 1)


def test_jeans_component_laplacians():
    """(b) flat Laplacian of each component equals -2 pi rho~_k on a radial grid, the
    conformal sources integrate to the conformal masses, the superposition
    satisfies Lap psi_tot = -2 pi rho~_tot in 3D, and the radial table reproduces
    u_env with the 4-point Lagrange interpolation of nrpic_cf."""
    J = jeans()
    md = J.env
    # envelope on the uniform table grid
    r, u, a = stc.table_arrays(md, n_matter=4000)
    src = -2 * np.pi * J.rho_tilde_radial(0, r)
    assert np.allclose(u, J.u_radial(0, r), rtol=0, atol=1e-15)
    res = stc.radial_laplacian(r, u) - src
    scale = np.max(np.abs(src))
    inner = r < 0.95 * md.rbar_s
    outer = (r > 1.05 * md.rbar_s) & np.isfinite(res)
    assert np.max(np.abs(res[inner])) < 1e-6 * scale
    assert np.max(np.abs(res[outer])) < 1e-6 * scale
    # Gaussian clump
    rg = np.linspace(0, 12 * J.sigma, 4801)
    ug = J.u_radial(1, rg)
    sg = -2 * np.pi * J.rho_tilde_radial(1, rg)
    rg_res = stc.radial_laplacian(rg, ug) - sg
    ok = np.isfinite(rg_res)
    assert np.max(np.abs(rg_res[ok])) < 1e-8 * np.max(np.abs(sg))
    assert abs(J.u_radial(1, 1e-9) - J.u_radial(1, 0.0)) < 1e-15
    assert abs(J.u_radial(1, 30.0) * 60.0 - J.m_c) < 1e-15
    # conformal masses: int rho~_k = M_env, m_c, m_c (Gauss: Lap u = -2 pi rho~)
    c = J.continuum()
    assert abs(c["envelope"]["conformal_mass"] / J.M_env - 1) < 1e-9
    assert abs(c["clump_A"]["conformal_mass"] / J.m_c - 1) < 1e-13
    assert abs(c["total"]["conformal_mass"] - J.M_adm) < 1e-9
    # isolated envelope: int rho0 psi_env^6 = M0 (quadrature check)
    M0 = J.shell_integral(0, lambda x, s: md.psi(s) / md.W(s))
    assert abs(M0 / md.M0 - 1) < 1e-9
    # cross terms: Gaussian overlaps in closed form, Green reciprocity with the envelope
    from scipy.special import erf
    D = 2 * J.d
    uA = lambda x, s: J.u_radial(1, J._dist(x, 1))
    uB = lambda x, s: J.u_radial(2, J._dist(x, 2))
    ue = lambda x, s: J.u_radial(0, J._dist(x, 0))
    assert abs(J.shell_integral(1, uA) / (J.m_c ** 2 / (2 * J.sigma * np.sqrt(np.pi))) - 1) < 1e-12
    assert abs(J.shell_integral(1, uB) / (J.m_c ** 2 * erf(D / (2 * J.sigma)) / (2 * D)) - 1) < 1e-12
    assert abs(J.shell_integral(0, uA) / J.shell_integral(1, ue) - 1) < 1e-9
    # 3D superposition, 4th-order differences
    rng = np.random.default_rng(1)
    p = np.concatenate([rng.normal(size=(1500, 3)) * J.sigma * 1.5 + J.centres[1],
                        rng.normal(size=(1500, 3)) * J.sigma * 1.5 + J.centres[2],
                        _random_dirs(1000, 2) * rng.uniform(0, 0.9, (1000, 1)) * md.rbar_s])
    h = 0.01
    lap = 0
    for e in np.eye(3):
        lap = lap + (-J.psi(p + 2 * h * e) + 16 * J.psi(p + h * e) - 30 * J.psi(p)
                     + 16 * J.psi(p - h * e) - J.psi(p - 2 * h * e)) / (12 * h * h)
    src3 = -2 * np.pi * J.rho_tilde(p)
    assert np.max(np.abs(lap - src3)) < 1e-6 * np.max(np.abs(src3))
    assert np.allclose(J.energy_density(p) * J.psi(p) ** 5, J.rho_tilde(p), rtol=1e-14)
    # the table with the generator's interpolation (nrpic_cf CFCubic)
    rr = rng.uniform(0, r[-1] * 0.999, 20000)
    xi = rr / (r[1] - r[0])
    i = np.clip(np.floor(xi).astype(int), 1, len(r) - 3)
    s = xi - i
    lag = (-s * (s - 1) * (s - 2) / 6 * u[i - 1] + (s + 1) * (s - 1) * (s - 2) / 2 * u[i]
           - (s + 1) * s * (s - 2) / 2 * u[i + 1] + (s + 1) * s * (s - 1) / 6 * u[i + 2])
    assert np.max(np.abs(lag - J.u_radial(0, rr))) < 1e-9


def _shell_edges(J, k, nb):
    if k == 0:
        e = J.env.Finv(np.linspace(0, 1, nb + 1))
        e[-1] = J.env.rbar_s * (1 + 1e-12)
    else:
        e = sampling.gaussian_radius_inv(np.linspace(0, 1, nb + 1), J.sigma)
        e[-1] = np.inf
    return e


def test_jeans_sampler_density():
    """(c) binned coordinate density of m W of each species, in shells about the
    component centre, against the continuum int rho~_k psi_tot; rest masses and
    velocities of the particles."""
    J = jeans()
    for method, N, mirror in (("stratified", 100000, True), ("mc", 20000, False)):
        x, u, m, sp = J.sample(N, seed=5, method=method, mirror=mirror)
        n_env, n_a, n_b = clm.split_counts(N)
        assert (n_env, n_a, n_b) == (3 * N // 5, N // 5, N // 5)
        assert [int(np.sum(sp == k)) for k in range(3)] == [n_env, n_a, n_b]
        W = J.lorentz_factor(x, u)
        psi = J.psi(x)
        q = u / psi[:, None] ** 2
        cont = J.continuum()
        zmax = 0.0
        for k in range(3):
            sel = sp == k
            r = J._dist(x[sel], k)
            g = (m * W)[sel]
            edges = _shell_edges(J, k, 8)
            counts = np.histogram(r, edges)[0]
            for i in range(8):
                b = (r >= edges[i]) & (r < edges[i + 1])
                est = g[b].sum()
                expect = J.shell_values(k, edges[i], edges[i + 1])[1]
                if method == "stratified":
                    # one particle per equal-probability stratum: fixed shell counts,
                    # the scatter is that of m W within the shell
                    assert counts[i] == sel.sum() // 8
                    sig = np.sqrt(b.sum() * g[b].var())
                    assert abs(est / expect - 1) < 2e-3
                else:
                    sig = np.sqrt(np.sum(g[b] ** 2))
                zmax = max(zmax, abs(est - expect) / sig)
            name = J.names[k]
            tol = 2e-4 if method == "stratified" else 3e-2
            assert abs(m[sel].sum() / cont[name]["rest_mass"] - 1) < tol
            assert abs(g.sum() / cont[name]["sum_mW"] - 1) < tol
            # velocities: envelope keeps the isolated |q|(r), clumps are cold at v
            if k == 0:
                # (rtol: q ~ (rbar_s - r)^(1/2) at the surface, |x| vs the drawn radius)
                assert np.allclose(np.linalg.norm(q[sel], axis=1), J.env.q(r), rtol=1e-9,
                                   atol=1e-15)
                assert np.allclose(m[sel], J.env.M0 / n_env * psi[sel] / J.env.psi(r),
                                   rtol=1e-14)
            else:
                assert np.allclose(q[sel], J.W * J.velocities[k - 1], rtol=1e-13, atol=0)
                assert np.allclose(W[sel], J.W, rtol=1e-14)
                assert np.allclose(m[sel], J.m_c / sel.sum() * psi[sel] / J.W, rtol=1e-14)
        assert zmax < 5.0, (method, zmax)
    # positions of a clump: stratified Gaussian in r and cos(theta) about its centre
    x, u, m, sp = J.sample(10000, seed=2)
    for k in (1, 2):
        d = x[sp == k] - J.centres[k]
        r = np.linalg.norm(d, axis=1)
        n = len(r)
        assert _ecdf_dev(r, lambda v: sampling.gaussian_radius_cdf(v, J.sigma)) <= 1 / n + 1e-9
        assert _ecdf_dev(d[:, 2] / r, lambda c: (c + 1) / 2) <= 1 / n + 1e-9


def test_jeans_momentum_and_spin():
    """(d) the clumps' momenta cancel; J_z = sum m (x u_y - y u_x) > 0 (paper: the
    clumps 'acquire positive angular momentum' with v_A^y < 0 at x_A = -d)."""
    J = jeans()
    assert J.centres[1, 0] < 0 and J.velocities[0, 1] < 0      # A at x < 0 moves to -y
    x, u, m, sp = J.sample(10000, seed=1)
    s = J.particle_summary(x, u, m, sp)
    pA, pB = np.array(s["clump_A"]["sum_m_u"]), np.array(s["clump_B"]["sum_m_u"])
    assert pA[1] < 0 < pB[1]
    assert np.max(np.abs(pA + pB)) < 1e-14 * abs(pA[1])          # mirrored clump B
    assert s["clump_A"]["J_z"] > 0 and s["clump_B"]["J_z"] > 0 and s["total"]["J_z"] > 0
    assert abs(s["clump_A"]["J_z"] / s["clump_B"]["J_z"] - 1) < 1e-13
    # continuum J_z of a clump: v int rho~_A psi_tot^3 (-x) d^3x
    jz = J.v * J.shell_integral(1, lambda p, r: J.psi(p) ** 3 * (-p[..., 0]))
    assert abs(s["clump_A"]["J_z"] / jz - 1) < 1e-3
    # envelope: no net angular momentum beyond sampling noise (isotropic q)
    e = sp == 0
    lz = m[e] * (x[e, 0] * u[e, 1] - x[e, 1] * u[e, 0])
    assert abs(s["envelope"]["J_z"]) < 5 * np.sqrt(np.sum(lz ** 2))
    # independently sampled clumps: momenta cancel to sampling accuracy
    x, u, m, sp = J.sample(10000, seed=1, mirror=False)
    s = J.particle_summary(x, u, m, sp)
    pA, pB = np.array(s["clump_A"]["sum_m_u"]), np.array(s["clump_B"]["sum_m_u"])
    assert np.max(np.abs(pA + pB)) < 1e-3 * abs(pA[1]) and s["total"]["J_z"] > 0


def test_jeans_circular_speed():
    """Leading-order circular speed v^2 = m_env(<d)/d + m_c/(4d) at d = 3M. The
    paper's 0.133215 is not reached with the R = 30M envelope, but is reproduced
    by the y_c = 0.907 envelope of the same mass (R = 13.31M)."""
    c = jeans().newtonian_circular_speed()
    assert abs(c["v_circ"] - 0.10272) < 1e-5 and c["v_clump_only"] == 0.1
    c = jeans(yc=0.907).newtonian_circular_speed()
    assert abs(c["v_circ"] - 0.133215) < 1e-6
    assert abs(jeans(yc=0.907).env.R - 13.3143) < 1e-4


# ----------------------------------------------------------------------------
# file formats and the command-line tool
# ----------------------------------------------------------------------------
def test_io_roundtrip():
    rng = np.random.default_rng(0)
    N = 257
    x, u, m = rng.normal(size=(N, 3)), rng.normal(size=(N, 3)), rng.random(N)
    sp = rng.integers(0, 3, N).astype(np.int32)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.nrp")
        nio.write_nrp(p, x, u, m, sp)
        assert os.path.getsize(p) == 16 + 60 * N
        with open(p, "rb") as f:
            assert f.read(8) == b"NRPIC001"
        x2, u2, m2, sp2 = nio.read_nrp(p)
        assert np.array_equal(x, x2) and np.array_equal(u, u2)
        assert np.array_equal(m, m2) and np.array_equal(sp, sp2)
        t = os.path.join(d, "t.tab")
        md = model(0.819)
        r, uu, al = stc.write_table(md, t)
        r2, u2_, a2, com = nio.read_tab(t)
        assert np.array_equal(r, r2) and np.array_equal(uu, u2_) and np.array_equal(al, a2)
        assert r2[0] == 0 and np.allclose(np.diff(r2), r2[1])
        assert np.sum(r2 <= md.rbar_s) >= 4000 and r2[-1] > md.rbar_s
        assert abs(2 * r2[-1] * u2_[-1] - 1) < 1e-12
        assert abs(a2[-1] - (1 - 0.5 / r2[-1]) / (1 + 0.5 / r2[-1])) < 1e-14


def test_make_ic_cli():
    import importlib.util
    import json
    spec = importlib.util.spec_from_file_location(
        "make_ic", os.path.join(_ROOT, "problems", "ic", "make_ic.py"))
    mk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mk)
    with tempfile.TemporaryDirectory() as d:
        runs = [["os", "--N", "1000", "--sampler", "lattice"],
                ["os", "--N", "100", "--sampler", "mc", "--seed", "2"],
                ["st", "--yc", "0.819", "--N", "1000", "--seed", "4"],
                ["st", "--yc", "0.605", "--N", "100", "--vpert", "0.01", "--sampler", "mc"],
                ["prolate", "--N", "1000"]]
        for args in runs:
            assert mk.main(args + ["--out", d, "--prefix", "run"]) == 0
            with open(os.path.join(d, "run.json")) as f:
                meta = json.load(f)
            x, u, m, sp = nio.read_nrp(os.path.join(d, "run.nrp"))
            assert meta["particles"]["N"] == len(m)
            if args[0] != "prolate":
                r, uu, al, _ = nio.read_tab(os.path.join(d, "run.tab"))
                assert abs(2 * r[-1] * uu[-1] - 1) < 1e-12
            for ext in (".nrp", ".tab", ".json"):
                if os.path.exists(os.path.join(d, "run" + ext)):
                    os.remove(os.path.join(d, "run" + ext))


def test_make_ic_jeans():
    import importlib.util
    import json
    spec = importlib.util.spec_from_file_location(
        "make_ic", os.path.join(_ROOT, "problems", "ic", "make_ic.py"))
    mk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mk)
    with tempfile.TemporaryDirectory() as d:
        assert mk.main(["jeans", "--N", "1000", "--seed", "1", "--out", d]) == 0
        stem = os.path.join(d, "jeans_N1000_s1")
        with open(stem + ".json") as f:
            meta = json.load(f)
        x, u, m, sp = nio.read_nrp(stem + ".nrp")
        assert len(m) == 1000 and [int(np.sum(sp == k)) for k in range(3)] == [600, 200, 200]
        r, uu, al, _ = nio.read_tab(stem + ".tab")
        assert abs(2 * r[-1] * uu[-1] - 0.76) < 1e-12 and r[-1] > meta["envelope"]["rbar_s"]
        comps = meta["components"]
        assert [c["type"] for c in comps] == ["table", "gaussian", "gaussian"]
        assert comps[0]["file"] == "jeans_N1000_s1.tab"
        assert comps[1]["center"] == [-3.0, 0.0, 0.0] and comps[2]["center"] == [3.0, 0.0, 0.0]
        assert comps[1]["velocity"][1] == -0.133215 and comps[2]["velocity"][1] == 0.133215
        prob = meta["athenak"]["problem"]
        assert prob["ncomp"] == 3 and prob["comp1_mass"] == 0.12 and prob["comp1_sigma"] == 0.7
        assert prob["lapse"] == "isotropic"
        assert abs(meta["envelope"]["R_areal"] - 30.0) < 1e-9
        assert abs(meta["envelope"]["M_env"] + 2 * 0.12 - meta["M_ADM"]) < 1e-15
        J = jeans()
        x2, u2, m2, sp2 = J.sample(1000, seed=1)
        # make_ic removes the net momentum of the sample by default
        ubar = (m2[:, None] * u2).sum(0) / m2.sum()
        assert meta["net_momentum_removed"]["mean_u"] == [float(v) for v in ubar]
        assert np.array_equal(x, x2) and np.array_equal(u, u2 - ubar) \
            and np.array_equal(m, m2)
        assert np.max(np.abs((m[:, None] * u).sum(0))) < 1e-15
        p0 = meta["psi_tot"]["origin"]
        assert abs(meta["lapse_isotropic"]["origin"] - (2 - p0) / p0) < 1e-15
        assert meta["particles_by_species"]["total"]["N"] == 1000
        assert mk.main(["jeans", "--N", "1000", "--env-yc", "0.907", "--out", d,
                        "--prefix", "alt", "--independent-clumps", "--sampler", "mc"]) == 0
        with open(os.path.join(d, "alt.json")) as f:
            alt = json.load(f)
        assert abs(alt["clumps"]["circular_speed_check"]["v_circ"] - 0.133215) < 1e-6
        assert alt["clump_B_mirror_of_A"] is False


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import time
    print(f"{'quantity':38s} {'this work':>16s} {'paper':>10s} {'rel. diff':>10s}")
    for name, ours, paper in paper_comparison():
        pv = float(paper)
        print(f"{name:38s} {ours:16.8f} {paper:>10s} {(ours - pv) / abs(pv):10.2e}")
    mx = stc.binding_energy_maximum()
    print(f"first E_b/M_0 maximum: y_c = {mx['yc']:.6f}, z_c = {mx['zc']:.6f}, "
          f"E_b/M_0 = {mx['Eb_over_M0']:.7f}, R/M = {mx['R_over_M']:.4f}, "
          f"M_0/M = {mx['M0_over_M']:.6f}")
    k = osn.trumpet_constants()
    print(f"1+log trumpet: C = {k['C']:.6f} M^2, R_crit = {k['R_crit']:.6f} M, "
          f"alpha_crit = {k['alpha_crit']:.6f}, R(alpha=0) = {k['R0']:.6f} M")
    print()
    failed = 0
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        t0 = time.time()
        try:
            fn()
            print(f"PASS {name} ({time.time() - t0:.1f} s)")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {name}: {exc!r}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
