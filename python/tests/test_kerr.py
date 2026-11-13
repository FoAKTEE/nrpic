"""Checks of the Kerr reference library (nrpic.kerr, nrpic.geodesic) and of the reference data.

Run either way:
    python3 python/tests/test_kerr.py
    python3 -m pytest python/tests/test_kerr.py

(a) 3+1 fields reproduce the closed-form 4-metrics and are mutually consistent under the
    coordinate Jacobians (random points outside the horizon, 1e-11).
(b) analytic 3+1 derivatives vs 8th-order central finite differences (extended precision).
(c) one physical orbit integrated in BL, spherical KS and Cartesian KS agrees after transforming
    events (t_KS != t_BL).
(d) E, L_z, Q conserved to ~1e-11 along the reference trajectories (problems/kerr/ref/*.npz).
Plus: state transformations, quadrature periods vs. event detection, Mino-time quadrature vs ODE,
the paper's quoted numbers, and internal consistency of the reference files.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from nrpic import geodesic, kerr  # noqa: E402

try:
    import pytest

    def _skip(msg):
        pytest.skip(msg)
except ImportError:  # pragma: no cover
    class _Skip(Exception):
        pass

    def _skip(msg):
        raise _Skip(msg)

A, M = 0.9, 1.0
REF = ROOT / "problems" / "kerr" / "ref"
KS_X0 = np.array([20.0, np.pi / 2, 0.0])
KS_U0 = np.array([-0.20131797516752664, 1.4049911031746785, 2.4328])
EQ_X0, EQ_U0 = np.array([6.0, np.pi / 2, 0.0]), np.array([0.0, 0.0, 3.144275])
INC_X0, INC_U0 = np.array([8.0, np.pi / 2 - 0.35, 0.0]), np.array([0.0, 0.9, 2.9])


def _points(n=400, seed=7, rmin_off=0.01, rmax=40.0, th_margin=0.02):
    """Random BL points outside the horizon and the same events in KS and CKS."""
    rng = np.random.default_rng(seed)
    rp, _ = kerr.horizon_radii(A, M)
    r = rp + rmin_off + (rmax - rp) * rng.random(n) ** 2
    th = th_margin + (np.pi - 2 * th_margin) * rng.random(n)
    ph = rng.uniform(-np.pi, np.pi, n)
    xbl = np.stack([r, th, ph], -1)
    _, xks = kerr.convert_event(0.0, xbl, "bl", "ks", A, M)
    _, xc = kerr.convert_event(0.0, xks, "ks", "cks", A, M)
    return xbl, xks, xc


def _relmax(d, ref):
    """max over points of max|d| / max|ref| (per point)."""
    ax = tuple(range(1, d.ndim))
    return float(np.max(np.max(np.abs(d), axis=ax) / np.max(np.abs(ref), axis=ax)))


def _T(J):
    return np.swapaxes(J, -1, -2)


# ------------------------------------------------------------------------------------------- (a)

def test_adm_reproduces_4metric():
    """g_tt = -alpha^2 + beta_k beta^k, g_ti = gamma_ij beta^j, g_ij = gamma_ij vs closed forms;
    gamma^ij and g^{mu nu} are inverses."""
    for sysn, x in zip(kerr.SYSTEMS, _points()):
        m = kerr.adm(sysn, x, A, M)
        g = kerr.g4(sysn, x, A, M)
        beta_low = np.einsum("...ij,...j->...i", m.gamma, m.beta)
        gtt = -m.alpha ** 2 + np.einsum("...i,...i->...", beta_low, m.beta)
        scale = np.max(np.abs(g), axis=(-1, -2))
        assert np.max(np.abs(gtt - g[..., 0, 0]) / scale) < 1e-11, sysn
        assert np.max(np.max(np.abs(beta_low - g[..., 0, 1:]), -1) / scale) < 1e-11, sysn
        assert _relmax(m.gamma - g[..., 1:, 1:], g) < 1e-11, sysn
        eye3 = np.broadcast_to(np.eye(3), m.gamma.shape)
        assert np.max(np.abs(m.gamma @ m.gamma_inv - eye3)) < 1e-11, sysn
        gi = kerr.ginv4_from_adm(m)
        assert np.max(np.abs(gi @ g - np.eye(4))) < 1e-11, sysn


def test_metrics_consistent_under_jacobians():
    """g_BL = J^T g_KS J, g_KS = J^T g_CKS J, g_BL = J^T g_CKS J for both the closed-form metrics
    and the 3+1-assembled metrics; the two spatial Jacobians are inverses; positions round-trip."""
    xbl, xks, xc = _points()
    X = {"bl": xbl, "ks": xks, "cks": xc}
    for build in ("closed", "adm"):
        G = {s: (kerr.g4(s, X[s], A, M) if build == "closed" else kerr.g4_from_adm(kerr.adm(s, X[s], A, M)))
             for s in kerr.SYSTEMS}
        for src, dst in (("bl", "ks"), ("ks", "cks"), ("bl", "cks"), ("ks", "bl"), ("cks", "ks")):
            J = kerr.jacobian4(src, dst, X[src], A, M)  # d x_dst / d x_src
            pulled = _T(J) @ G[dst] @ J
            err = _relmax(pulled - G[src], G[src])
            assert err < 1e-11, (build, src, dst, err)
    J = kerr.jac_ks_to_cks(xks, A)
    K = kerr.jac_cks_to_ks(xc, A)
    assert np.max(np.abs(K @ J - np.eye(3))) < 1e-11
    back = kerr.cks_to_ks_position(xc, A)
    assert np.max(np.abs(back[:, :2] - xks[:, :2])) < 1e-12
    assert np.max(np.abs(np.angle(np.exp(1j * (back[:, 2] - xks[:, 2]))))) < 1e-12
    tb, xb = kerr.convert_event(1.5, xc, "cks", "bl", A, M)
    tk, _ = kerr.convert_event(1.5, xks, "ks", "bl", A, M)
    assert np.max(np.abs(tb - tk)) < 1e-12
    # delta_t, delta_phi derivatives: 2 M r / Delta, a / Delta
    r = np.linspace(1.6, 30, 50)
    h = 1e-5
    Del = r * r - 2 * M * r + A * A
    dt_fd = (kerr.delta_t(r + h, A, M) - kerr.delta_t(r - h, A, M)) / (2 * h)
    dp_fd = (kerr.delta_phi(r + h, A, M) - kerr.delta_phi(r - h, A, M)) / (2 * h)
    assert np.max(np.abs(dt_fd - 2 * M * r / Del) / (2 * M * r / Del)) < 1e-8
    assert np.max(np.abs(dp_fd - A / Del) / (A / Del)) < 1e-8


def test_state_transformations():
    """Random timelike states: round trip BL->KS->CKS->KS->BL; the transformed u_t (covariant
    4-vector law, via the 4x4 Jacobians) equals -E of the target 3+1 metric and is normalized;
    invariants identical in all systems; explicit u_r^KS = u_r^BL + (2 M r E - a L)/Delta."""
    rng = np.random.default_rng(11)
    xbl, xks, xc = _points(300, seed=3)
    u = rng.normal(size=(300, 3)) * np.array([0.5, 2.0, 2.0])
    E = kerr.energy("bl", xbl, u, A, M)
    u4 = np.concatenate([-E[:, None], u], -1)
    t0 = rng.uniform(-10, 10, 300)
    tk, xk, uk = kerr.convert_state(t0, xbl, u, "bl", "ks", A, M)
    tc, xcc, uc = kerr.convert_state(tk, xk, uk, "ks", "cks", A, M)
    tk2, xk2, uk2 = kerr.convert_state(tc, xcc, uc, "cks", "ks", A, M)
    tb2, xb2, ub2 = kerr.convert_state(tk2, xk2, uk2, "ks", "bl", A, M)
    assert np.max(np.abs(tb2 - t0)) < 1e-11
    assert np.max(np.abs(xb2[:, :2] - xbl[:, :2])) < 1e-11
    assert np.max(np.abs(np.angle(np.exp(1j * (xb2[:, 2] - xbl[:, 2]))))) < 1e-11
    assert np.max(np.abs(ub2 - u) / (1 + np.abs(u))) < 1e-11
    _, xc_direct, uc_direct = kerr.convert_state(t0, xbl, u, "bl", "cks", A, M)
    assert np.max(np.abs(uc_direct - uc)) < 1e-11 * np.max(np.abs(uc))
    # covariant transformation of the full 4-velocity: u^dst = (J^-1)^T u^src, J = d x_dst/d x_src
    for dst, xd, ud in (("ks", xk, uk), ("cks", xcc, uc)):
        J = kerr.jacobian4("bl", dst, xbl, A, M)
        u4d = np.linalg.solve(_T(J), u4[..., None])[..., 0]
        assert np.max(np.abs(u4d[:, 1:] - ud) / (1 + np.abs(ud))) < 1e-10, dst
        Ed = kerr.energy(dst, xd, ud, A, M)
        assert np.max(np.abs(-u4d[:, 0] - Ed) / (1 + np.abs(Ed))) < 1e-11, dst
        n = kerr.norm4(dst, xd, u4d[:, 0], ud, A, M)
        assert np.max(np.abs(n + 1)) < 1e-10, dst
        # normalization with the independent closed-form inverse metric too
        gi = np.linalg.inv(kerr.g4(dst, xd, A, M))
        n2 = np.einsum("...i,...ij,...j->...", u4d, gi, u4d)
        assert np.max(np.abs(n2 + 1)) < 1e-9, dst
    for (s, x, uu) in (("bl", xbl, u), ("ks", xk, uk), ("cks", xcc, uc)):
        Es, Ls, Qs = kerr.invariants(s, x, uu, A, M)
        E0, L0, Q0 = kerr.invariants("bl", xbl, u, A, M)
        assert np.max(np.abs(Es - E0) / (1 + np.abs(E0))) < 1e-11, s
        assert np.max(np.abs(Ls - L0) / (1 + np.abs(L0))) < 1e-11, s
        assert np.max(np.abs(Qs - Q0) / (1 + np.abs(Q0))) < 1e-10, s
    r = xbl[:, 0]
    Del = r * r - 2 * M * r + A * A
    assert np.max(np.abs(uk[:, 0] - (u[:, 0] + (2 * M * r * E - A * u[:, 2]) / Del))) < 1e-12 * np.max(np.abs(uk))
    assert np.array_equal(uk[:, 1:], u[:, 1:])


# ------------------------------------------------------------------------------------------- (b)

def test_derivatives_vs_finite_differences():
    """Analytic d_i alpha, d_i beta^j, d_i gamma_jk vs 8th-order central differences.

    Done in np.longdouble when it is extended precision (x86: eps = 1.1e-19), so the FD error
    (truncation ~ (h/L)^8, round-off ~ eps/h) is below 1e-13 relative; the double-precision
    analytic values are compared with the long-double ones as well.
    """
    ld = np.longdouble if np.finfo(np.longdouble).eps < 1e-18 else np.float64
    tol = 1e-11 if ld is np.longdouble else 1e-8
    c = np.array([1 / 280, -4 / 105, 1 / 5, -4 / 5, 0, 4 / 5, -1 / 5, 4 / 105, -1 / 280], dtype=ld)
    for sysn, x in zip(kerr.SYSTEMS, _points(150, seed=5, rmin_off=0.05, th_margin=0.1)):
        X = x.astype(ld)
        m = kerr.adm(sysn, X, A, M)
        m64 = kerr.adm(sysn, x, A, M)
        for name in ("dalpha", "dbeta", "dgamma"):
            an, a64 = getattr(m, name), getattr(m64, name)
            sc = np.maximum(np.max(np.abs(an).reshape(len(x), -1), 1), 1e-300)
            rel = np.max(np.abs(a64 - an).reshape(len(x), -1), 1) / sc
            assert float(np.max(rel)) < 1e-12, (sysn, name, "double vs long double", float(np.max(rel)))
        for i in range(3):
            if sysn == "cks":
                h = ld(1e-3) * np.maximum(1, np.abs(X[:, i]))
            elif i == 0:
                # BL fields have poles at r_+: scale the radial step with the distance to it
                rp, _ = kerr.horizon_radii(A, M)
                h = ld(1e-3) * (X[:, 0] - rp if sysn == "bl" else X[:, 0])
            else:
                h = np.full(len(x), ld(1e-3))
            acc = [0, 0, 0]
            for k, ck in enumerate(c):
                if ck == 0:
                    continue
                Xp = X.copy()
                Xp[:, i] += (k - 4) * h
                mm = kerr.adm(sysn, Xp, A, M, derivs=False)
                acc[0] = acc[0] + ck * mm.alpha
                acc[1] = acc[1] + ck * mm.beta
                acc[2] = acc[2] + ck * mm.gamma
            fd = (acc[0] / h, acc[1] / h[:, None], acc[2] / h[:, None, None])
            an = (m.dalpha[:, i], m.dbeta[:, i, :], m.dgamma[:, i])
            vals = (m.alpha, m.beta, m.gamma)
            for name, f, g, v in zip(("alpha", "beta", "gamma"), fd, an, vals):
                f = f.reshape(len(x), -1)
                g = g.reshape(len(x), -1)
                # scale: derivative magnitude, or field magnitude per coordinate length
                L = X[:, 0] if sysn != "cks" else kerr.cks_radius(X, A)
                sc = np.maximum(np.max(np.abs(g), 1), np.max(np.abs(v).reshape(len(x), -1), 1) / L)
                err = float(np.max(np.max(np.abs(f - g), 1) / sc))
                assert err < tol, (sysn, i, name, err)


# ------------------------------------------------------------------------------------------- (c)

def _compare_bl_ks_cks(sysn0, x0, u0, t_end, rtol=2.5e-14, n=600):
    """Integrate one orbit (defined in sysn0 at t=0) in BL, KS and CKS; compare by transforming
    events.  Returns dict of max abs differences."""
    traj = {}
    init = {}
    for s in kerr.SYSTEMS:
        t0s, xs, us = kerr.convert_state(0.0, x0, u0, sysn0, s, A, M)
        init[s] = (float(t0s), xs, us)
    # every system runs over [t0, t0 + t_end + pad]; the pad covers t_KS - t_BL = delta_t(r) changes
    for s in kerr.SYSTEMS:
        t0s, xs, us = init[s]
        traj[s] = geodesic.integrate(s, xs, us, t0s + t_end + 30.0, t0=t0s, rtol=rtol, atol=rtol,
                                     a=A, M=M, dense_output=True)
    # BL events -> KS events, compare with the KS dense output at the KS times
    tbl0 = init["bl"][0]
    tb = np.linspace(tbl0, tbl0 + t_end, n)
    xb, ub = traj["bl"].state(tb)
    tk, xk_from_bl, uk_from_bl = kerr.convert_state(tb, xb, ub, "bl", "ks", A, M)
    ks0 = init["ks"][0]
    ok = (tk >= ks0) & (tk <= ks0 + t_end)
    xk, uk = traj["ks"].state(tk[ok])
    d_bl_ks = max(np.max(np.abs(xk - xk_from_bl[ok])), np.max(np.abs(uk - uk_from_bl[ok])))
    # KS -> CKS at equal KS time
    tt = np.linspace(ks0, ks0 + t_end, n)
    xk, uk = traj["ks"].state(tt)
    _, xc_from_ks, uc_from_ks = kerr.convert_state(tt, xk, uk, "ks", "cks", A, M)
    xc, uc = traj["cks"].state(tt)
    d_ks_cks = max(np.max(np.abs(xc - xc_from_ks)), np.max(np.abs(uc - uc_from_ks)))
    return dict(bl_vs_ks=float(d_bl_ks), ks_vs_cks=float(d_ks_cks), n_bl_ks=int(ok.sum()))


def test_same_orbit_three_systems_inclined():
    """BL inclined orbit, two radial periods, integrated in BL, KS and CKS."""
    d = _compare_bl_ks_cks("bl", INC_X0, INC_U0, 430.0)
    assert d["n_bl_ks"] > 500
    assert d["bl_vs_ks"] < 1e-10 and d["ks_vs_cks"] < 1e-10, d


def test_same_orbit_three_systems_ks_passage():
    """KS e = 0.99 passage through pericenter (t_KS in [0, 230]) integrated in BL, KS and CKS.

    The orbit is near the separatrix (r3 = 1.850 vs r_p = 1.898); a perturbation of the state is
    amplified up to ~1e4 by t = 230, so free-running double-precision runs differ at ~1e-9."""
    d = _compare_bl_ks_cks("ks", KS_X0, KS_U0, 230.0)
    assert d["n_bl_ks"] > 500
    assert d["bl_vs_ks"] < 1e-8 and d["ks_vs_cks"] < 1e-8, d
    # up to just after pericenter the agreement is much tighter
    d2 = _compare_bl_ks_cks("ks", KS_X0, KS_U0, 100.0)
    assert d2["bl_vs_ks"] < 3e-11 and d2["ks_vs_cks"] < 3e-11, d2  # measured 8e-13, 6e-12


# ------------------------------------------------------------------------------------------- (d)

def _load_ref():
    js = REF / "initial_conditions.json"
    if not js.exists():
        _skip("reference data not generated (run problems/kerr/make_reference.py)")
    return json.loads(js.read_text())


def test_invariants_along_reference_trajectories():
    """E, L_z, Q along every stored reference trajectory vs the exact invariants: <= 1e-11
    (relative; absolute for the Q ~ 1e-32 of the equatorial orbit)."""
    meta = _load_ref()
    for name, om in meta["orbits"].items():
        inv = om["invariants"]
        for s, fn in om["files"].items():
            d = np.load(REF.parent / fn)
            ih = geodesic.invariant_history(s, d["x"], d["u"], A, M, ref=(inv["E"], inv["Lz"], inv["Q"]))
            for k in ("dE", "dLz", "dQ"):
                assert ih["max_abs_" + k] < 1e-11, (name, s, k, ih["max_abs_" + k])


def test_invariants_free_running():
    """Free-running DOP853 (rtol = atol = 1e-13) conserves E, L_z, Q to ~1e-12 in all systems."""
    for s in kerr.SYSTEMS:
        t0, x, u = kerr.convert_state(0.0, KS_X0, KS_U0, "ks", s, A, M)
        tr = geodesic.integrate(s, x, u, float(t0) + 230.0, t0=float(t0), rtol=1e-13, atol=1e-13)
        ih = geodesic.invariant_history(s, tr.x, tr.u, A, M)
        for k in ("dE", "dLz", "dQ"):
            assert ih["max_abs_" + k] < 1e-11, (s, k, ih["max_abs_" + k])


# ----------------------------------------------------------------------------------- extra checks

def test_paper_numbers():
    """Quoted numbers of the paper: KS passage E = 0.99738, L_z = 2.4328, Q = 1.974, r_p = 1.8983,
    e = 0.99; equatorial orbit 6.00 <= r <= 11.61; inclined orbit crosses the equator."""
    E, L, Q = kerr.invariants("ks", KS_X0, KS_U0, A, M)
    assert abs(E - 0.99738) < 5e-6 and abs(L - 2.4328) < 1e-12 and abs(Q - 1.974) < 5e-4
    op = kerr.orbit_periods(E, L, Q, A, M)
    assert abs(op["r_peri"] - 1.8983) < 5e-5
    assert abs(op["e"] - 0.99) < 5e-3
    E, L, Q = kerr.invariants("bl", EQ_X0, EQ_U0, A, M)
    op = kerr.orbit_periods(E, L, Q, A, M)
    assert abs(op["r_peri"] - 6.0) < 5e-3 and abs(op["r_apo"] - 11.61) < 5e-3
    E, L, Q = kerr.invariants("bl", INC_X0, INC_U0, A, M)
    op = kerr.orbit_periods(E, L, Q, A, M)
    assert op["theta_min"] < np.pi / 2 - 0.35 + 1e-12  # starts inside the polar range
    assert op["r_peri"] <= 8.0 + 1e-12 <= op["r_apo"]


def test_periods_vs_event_detection():
    """Quadrature T_r equals the event-detected pericenter interval (exact for the equatorial
    orbit, mean over periods for the inclined one); turning radii match the roots of R(r)."""
    E, L, Q = kerr.invariants("bl", EQ_X0, EQ_U0, A, M)
    op = kerr.orbit_periods(E, L, Q, A, M)
    tr = geodesic.integrate("bl", EQ_X0, EQ_U0, 3.2 * op["T_r"], rtol=1e-13, atol=1e-13, turning_points=True)
    tp = tr.events["peri"][0]
    tp = tp[tp > 1.0]
    assert len(tp) == 3
    assert np.max(np.abs(np.diff(np.concatenate([[0.0], tp])) - op["T_r"])) < 1e-9 * op["T_r"]
    ra = tr.events["apo"][1][:, 0]
    assert np.max(np.abs(ra - op["r_apo"])) < 1e-10
    E, L, Q = kerr.invariants("bl", INC_X0, INC_U0, A, M)
    op = kerr.orbit_periods(E, L, Q, A, M)
    nper = 12
    tr = geodesic.integrate("bl", INC_X0, INC_U0, (nper + 0.5) * op["T_r"], rtol=1e-13, atol=1e-13,
                            turning_points=True)
    tp = tr.events["peri"][0]
    tp = tp[tp > 1.0]
    assert len(tp) == nper
    # the interval oscillates with the polar motion; its mean converges to T_r like 1/N
    assert abs(tp[-1] / nper - op["T_r"]) < 1e-3 * op["T_r"]
    assert np.max(np.abs(tr.events["apo"][1][:, 0] - op["r_apo"])) < 1e-9
    thmin = np.min(tr.x[:, 1])
    assert thmin >= op["theta_min"] - 1e-9


def test_mino_quadrature_vs_ode():
    """The Mino-time quadrature solution (mpmath, first integrals only) agrees with the 3+1 ODE
    integration in KS and CKS at the pericenter and at t = 120."""
    orb = kerr.MinoOrbit.from_state("ks", 0.0, KS_X0, KS_U0, A, M, dps=25)
    trk = geodesic.integrate("ks", KS_X0, KS_U0, 125.0, rtol=2.5e-14, atol=2.5e-14, dense_output=True)
    _, xc0, uc0 = kerr.convert_state(0.0, KS_X0, KS_U0, "ks", "cks", A, M)
    trc = geodesic.integrate("cks", xc0, uc0, 125.0, rtol=2.5e-14, atol=2.5e-14, dense_output=True)
    for t in (60.0, 120.0):
        st, _ = orb.states_at_time(t, "ks", ("ks", "cks"))
        for s, tr in (("ks", trk), ("cks", trc)):
            x, u = tr.state(t)
            xe = np.array([float(v) for v in st[s][1]])
            ue = np.array([float(v) for v in st[s][2]])
            err = max(np.max(np.abs(x - xe)), np.max(np.abs(u - ue)))
            assert err < 1e-10, (t, s, err)


def test_reference_files_consistency():
    """The JSON initial states in the three systems are the same event; npz first/last samples
    equal the JSON initial/final states; the spherical and Cartesian KS references agree."""
    meta = _load_ref()
    for name, om in meta["orbits"].items():
        ini = om["initial_state"]
        nat = om["natural_system"]
        for s in kerr.SYSTEMS:
            t1, x1, u1 = kerr.convert_state(ini[nat]["t0"], np.array(ini[nat]["x"]), np.array(ini[nat]["u"]),
                                            nat, s, A, M)
            assert abs(float(t1) - ini[s]["t0"]) < 1e-12, (name, s)
            assert np.max(np.abs(x1 - np.array(ini[s]["x"]))) < 1e-13 * max(1, np.max(np.abs(x1))), (name, s)
            assert np.max(np.abs(u1 - np.array(ini[s]["u"]))) < 1e-13 * max(1, np.max(np.abs(u1))), (name, s)
            E = kerr.energy(s, np.array(ini[s]["x"]), np.array(ini[s]["u"]), A, M)
            assert abs(E + ini[s]["u_t"]) < 1e-14, (name, s)
        for s, fn in om["files"].items():
            d = np.load(REF.parent / fn)
            n = int(round(om["t_end"] / om["dt_out"]))
            assert d["t"].shape == (n + 1,) and d["t"][-1] == om["t_end"]
            assert np.max(np.abs(np.diff(d["t"]) - om["dt_out"])) < 1e-10
            # first row = exact state at t = 0 (agrees with the JSON initial state to rounding)
            assert np.max(np.abs(d["x"][0] - np.array(ini[s]["x"]))) < 1e-14 * max(1, np.max(np.abs(d["x"][0])))
            assert np.max(np.abs(d["u"][0] - np.array(ini[s]["u"]))) < 1e-14 * max(1, np.max(np.abs(d["u"][0])))
            assert np.array_equal(d["x"][-1], d["x_end"]) and np.array_equal(d["u"][-1], d["u_end"])
            assert np.array_equal(d["x_end"], np.array(om["final_state"][s]["x"]))
        if set(om["files"]) >= {"ks", "cks"}:
            dk = np.load(REF.parent / om["files"]["ks"])
            dc = np.load(REF.parent / om["files"]["cks"])
            _, xc, uc = kerr.convert_state(dk["t"], dk["x"], dk["u"], "ks", "cks", A, M)
            assert np.max(np.abs(xc - dc["x"])) < 1e-11 and np.max(np.abs(uc - dc["u"])) < 1e-11


# ------------------------------------------------------------------------------------------- main

def _run_all():
    tests = [(k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)]
    nfail = 0
    for name, fn in tests:
        t0 = time.time()
        try:
            fn()
            status = "PASS"
        except BaseException as exc:  # noqa: BLE001  (pytest.skip raises a BaseException)
            if type(exc).__name__ in ("Skipped", "_Skip"):
                status = f"SKIP ({exc})"
            else:
                status = f"FAIL: {exc!r}"
                nfail += 1
        print(f"{name:50s} {status}  [{time.time() - t0:.1f} s]", flush=True)
    print(f"{len(tests) - nfail}/{len(tests)} passed or skipped")
    return nfail


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
