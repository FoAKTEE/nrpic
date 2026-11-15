"""Unit tests of the newton3 package (prediction P0 in ../JOURNAL.md).

Run: cd tracks/F-hills/newton3 && OMP_NUM_THREADS=1 python3 -m pytest -q tests
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hills3 import restricted as R  # noqa: E402
from hills3 import threebody as T  # noqa: E402
from hills3.integrate import integrate_many  # noqa: E402
from hills3.orbits import orientation_basis  # noqa: E402

SQ2 = np.sqrt(2.0)


# ---- the free solutions of SKR prp.tex:274-307, as functions of the true anomaly f
def _free(f):
    c, s = np.cos(f), np.sin(f)
    th = np.tan(f / 2)
    z = np.zeros_like(f)
    return {
        "omega": (-s / (1 + c), c / (1 + c), z),
        "peri_time": (-s, 1 + c, z),
        "peri_dist": (2 - c, -c * th, z),
        "ecc": ((8 + 12 * c) * th ** 4,
                (35 * s - 2 * np.sin(2 * f) + 3 * np.sin(3 * f)) / (1 + c) ** 2, z),
        "rot_apsidal": (z, z, 2 * s / (1 + c)),
        "rot_latus": (z, z, 2 * c / (1 + c)),
    }


def _free_state(f, name, h=1e-6):
    pos = np.array(_free(np.array([f]))[name])[:, 0]
    dp = (np.array(_free(np.array([f + h]))[name])[:, 0]
          - np.array(_free(np.array([f - h]))[name])[:, 0]) / (2 * h)
    fdot = SQ2 * (1 + np.cos(f)) ** 2 / 4  # SKR prp.tex:259
    return np.concatenate([pos, dp * fdot])


def test_tau_inversion():
    t = np.concatenate([-np.logspace(-8, 9, 50), [0.0], np.logspace(-8, 9, 50)])
    tau = R.tau_of_t(t)
    assert np.allclose(R.t_of_tau(tau), t, rtol=1e-12, atol=1e-20)


def test_free_solutions_solve_tidal_equations():
    f0, f1 = -2.0, 2.0
    t0 = R.t_of_tau(np.tan(f0 / 2))
    t1 = R.t_of_tau(np.tan(f1 / 2))
    names = list(_free(np.zeros(1)).keys())
    y0 = np.array([_free_state(f0, nm) for nm in names])
    y1 = np.array([_free_state(f1, nm) for nm in names])
    y, nacc, ok = integrate_many(R.make_rhs(self_gravity=False), np.full(6, t0), y0,
                                 np.full(6, t1), np.full(6, 1e-3), rtol=1e-12, atol=1e-14)
    assert ok.all()
    scale = np.maximum(np.abs(y1).max(axis=1), 1.0)
    err = np.abs(y - y1).max(axis=1) / scale
    assert np.all(err < 1e-8), dict(zip(names, err))


def test_energy_bracket_of_free_solutions():
    """bracket = 20 B for the eccentricity solution (SKR prp.tex:397-401), 0 otherwise."""
    for f in (-2.5, -1.0, 0.3, 1.7):
        t = R.t_of_tau(np.tan(f / 2))
        for nm in _free(np.zeros(1)):
            br = R.energy_bracket(np.array([t]), _free_state(f, nm)[None, :])[0]
            want = 20.0 if nm == "ecc" else 0.0
            assert abs(br - want) < 1e-6 * max(1.0, abs(want)), (nm, f, br)


def test_kepler_two_body():
    """integrate_many on an e = 0.6 Kepler orbit over 20 periods: at rtol 1e-13 the
    return error is below 1e-8, and at rtol 1e-11 it is within a factor 2 of SciPy's
    DOP853 (journal entry 2: 1e-8 at rtol 1e-11 was too optimistic for both codes)."""
    from scipy.integrate import solve_ivp

    def rhs(t, y, idx):
        r3 = np.sum(y[:, :2] ** 2, axis=1) ** 1.5
        return np.concatenate([y[:, 2:], -y[:, :2] / r3[:, None]], axis=1)
    e = 0.6
    y0 = np.array([[1 - e, 0.0, 0.0, np.sqrt((1 + e) / (1 - e))]])
    y, nacc, ok = integrate_many(rhs, 0.0, y0, 20 * 2 * np.pi, 1e-3, rtol=1e-13, atol=1e-14)
    assert ok.all()
    assert np.max(np.abs(y - y0)) < 1e-8
    y, nacc, ok = integrate_many(rhs, 0.0, y0, 20 * 2 * np.pi, 1e-3, rtol=1e-11, atol=1e-14)
    s = solve_ivp(lambda t, z: rhs(t, z[None, :], None)[0], (0, 40 * np.pi), y0[0],
                  method="DOP853", rtol=1e-11, atol=1e-14)
    mine, ref = np.max(np.abs(y - y0)), np.max(np.abs(s.y[:, -1] - y0[0]))
    assert 0.5 < mine / ref < 2.0, (mine, ref)


def test_initial_state_properties():
    rng = np.random.default_rng(1)
    for _ in range(5):
        s = T.HillsSetup(M=10 ** rng.uniform(1, 6), m1=rng.uniform(0.2, 1), m2=rng.uniform(0.2, 1),
                         a=rng.uniform(0.5, 2), e_b=rng.uniform(0, 0.8), D=rng.uniform(0.05, 2),
                         e_orb=rng.choice([1.0, 0.9, 1.1]), theta=rng.uniform(0, np.pi),
                         varphi=rng.uniform(0, 2 * np.pi), varpi=rng.uniform(0, np.pi),
                         phase=rng.uniform(0, 2 * np.pi))
        ic = T.initial_state(s, k0=12.0)
        m = ic["masses"]
        x, p = ic["positions"], ic["momenta"]
        assert np.allclose(p.sum(axis=0), 0, atol=1e-12 * np.abs(p).max())
        assert np.allclose((m[:, None] * x).sum(axis=0), 0, atol=1e-12 * np.abs(m[:, None] * x).max())
        # binary: semi-major axis and eccentricity from the relative state
        d = x[2] - x[1]
        w = ic["velocities"][2] - ic["velocities"][1]
        gm = s.m
        eps = 0.5 * w @ w - gm / np.linalg.norm(d)
        assert abs(-gm / (2 * eps) / s.a - 1) < 1e-12
        hb = np.cross(d, w)
        eb = np.sqrt(1 + 2 * eps * (hb @ hb) / gm ** 2)
        assert abs(eb - s.e_b) < 1e-10
        lhat = hb / np.linalg.norm(hb)
        l, _, _ = orientation_basis(s.theta, s.varphi)
        assert np.allclose(lhat, l[0], atol=1e-12)
        # centre-of-mass conic: pericentre, eccentricity, distance, incoming
        xc = (s.m1 * x[1] + s.m2 * x[2]) / s.m
        vc = (s.m1 * ic["velocities"][1] + s.m2 * ic["velocities"][2]) / s.m
        Rv, Vv = xc - x[0], vc - ic["velocities"][0]
        mu = s.M + s.m
        hR = np.cross(Rv, Vv)
        eps_c = 0.5 * Vv @ Vv - mu / np.linalg.norm(Rv)
        ecc = np.sqrt(1 + 2 * eps_c * (hR @ hR) / mu ** 2)
        rp = (hR @ hR) / mu / (1 + ecc)
        assert abs(ecc - s.e_orb) < 1e-9
        assert abs(rp / ic["r_p"] - 1) < 1e-10
        assert abs(np.linalg.norm(Rv) / (12 * ic["r_t"]) - 1) < 1e-12
        assert Rv @ Vv < 0 and hR[2] > 0


def test_conservation_full_problem():
    ss = [T.HillsSetup(M=1e3, m1=1.0, m2=1 / 3, a=1.0, D=0.1, phase=ph)
          for ph in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
    out = T.scatter(ss)
    assert out["ok"].all()
    # total energy ~ binary binding energy; measure the error against the energy unit
    E0 = 1.0 * (1 / 3) / 2
    err_unit = np.abs(out["energy_error"]) * E0 / ss[0].energy_unit
    assert np.max(err_unit) < 1e-8, err_unit
    assert np.max(out["angmom_error"]) < 1e-9, out["angmom_error"]
    out = T.scatter(ss, rtol=1e-13)
    assert np.max(np.abs(out["energy_error"])) < 1e-9, out["energy_error"]


def test_restricted_phase_antisymmetry():
    """E2(phase + pi) = -E2(phase) (SKR prp.tex:365-372), and the same fate."""
    ph = np.linspace(0, np.pi, 7, endpoint=False)
    for th, vp in ((np.pi / 2, np.pi / 2), (0.7, 2.1)):
        a = R.run(0.3, th, vp, ph)
        b = R.run(0.3, th, vp, ph + np.pi)
        assert np.array_equal(a["disrupted"], b["disrupted"])
        assert np.allclose(a["E2"], -b["E2"], rtol=1e-8, atol=1e-10)


def test_restricted_against_scipy():
    from scipy.integrate import solve_ivp
    rng = np.random.default_rng(7)
    n = 10
    D = 10 ** rng.uniform(-2, 0.3, n)
    th = np.arccos(rng.uniform(-1, 1, n))
    vp = rng.uniform(0, 2 * np.pi, n)
    ph = rng.uniform(0, np.pi, n)
    out = R.run(D, th, vp, ph, rtol=1e-11)
    t0, y0 = R.initial_conditions(D, th, vp, ph)
    rhs = R.make_rhs(True)
    for i in range(n):
        sol = solve_ivp(lambda t, y: rhs(np.array([t]), y[None, :], None)[0],
                        (t0[i], out["t_end"][i]), y0[i], method="DOP853", rtol=1e-12, atol=1e-14)
        E2 = R.energy_bracket(np.array([sol.t[-1]]), sol.y[:, -1][None, :])[0] / D[i]
        assert abs(E2 - out["E2"][i]) < 1e-7 * max(1.0, abs(E2)), (i, E2, out["E2"][i])


def test_driver_against_scipy():
    s = T.HillsSetup(M=100.0, m1=1.0, m2=0.5, a=1.0, D=0.5, theta=1.0, varphi=0.3, phase=1.0)
    out = T.scatter([s])
    tt, X, V, sol = T.trajectory(s)
    assert np.allclose(X[-1], out["x_end"][0], rtol=0, atol=1e-6 * np.abs(X[-1]).max())


def test_initial_state_json_roundtrip():
    import json
    s = T.HillsSetup(M=10.0, m1=0.5, m2=0.5, a=30.0, D=0.7, phase=1.0)
    d = json.loads(json.dumps(T.initial_state_json(s, k0=10.0)))
    ic = T.initial_state(s, k0=10.0)
    assert np.allclose(np.array(d["momenta"]), ic["momenta"], rtol=0, atol=0)
    assert d["names"] == ["M", "m1", "m2"]


# ---------------------------------------------------------------- wave 2: member energies
INPUTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      "three_punctures", "inputs")
# the two passages of stage/G1/STATUS.md (three_punctures PLAN: phase 130 and 127 deg)
PASSAGES = {"q10": (dict(M=1.0, m1=0.05, m2=0.05, a=3.0, rp=8.0, phase=np.radians(130.0)),
                    "hills_q10_m8.athinput"),
            "q4": (dict(M=1.0, m1=0.125, m2=0.125, a=5.0, rp=1.2378 * 5.0 * 4.0 ** (1 / 3),
                        phase=np.radians(127.0)), "hills_q4_m8.athinput")}


def test_jacobi_identity_with_direct_coupling():
    """E_tot = E_in + E_out + W with W computed from its definition (not as the remainder);
    W tends to the quadrupole -G m_e mu_in r^2 P2/R^3 when the outer body is far."""
    rng = np.random.default_rng(3)
    for _ in range(20):
        ms = np.array([10 ** rng.uniform(0, 3), rng.uniform(0.1, 1), rng.uniform(0.1, 1)])
        x = rng.normal(size=(3, 3)) * rng.uniform(1, 10)
        v = rng.normal(size=(3, 3)) * 0.3
        en = T.member_energies(x[None], v[None], ms)
        c = int(en["inner"][0])
        e = 3 - c
        Mc = ms[0] + ms[c]
        Xc = (ms[0] * x[0] + ms[c] * x[c]) / Mc
        W = (-ms[0] * ms[e] / np.linalg.norm(x[e] - x[0]) - ms[c] * ms[e] / np.linalg.norm(x[e] - x[c])
             + Mc * ms[e] / np.linalg.norm(x[e] - Xc))
        scale = abs(en["E_in"][0]) + abs(en["E_out"][0]) + abs(W)
        assert abs(en["E_in"][0] + en["E_out"][0] + W - en["E_tot"][0]) < 1e-12 * scale
        assert abs(en["W"][0] - W) < 1e-12 * scale
    # quadrupole limit
    ms = np.array([1.0, 0.05, 0.05])
    r = np.array([3.0, 1.0, 0.5])
    for Rd in (50.0, 500.0):
        Rv = Rd * np.array([0.6, -0.8, 0.0])
        Mc = ms[0] + ms[1]
        x = np.array([-ms[1] / Mc * r, ms[0] / Mc * r, Rv])
        en = T.member_energies(x[None], np.zeros((1, 3, 3)), ms)
        assert en["inner"][0] == 1
        mu = ms[0] * ms[1] / Mc
        cosp = r @ Rv / (np.linalg.norm(r) * Rd)
        quad = -ms[2] * mu * (r @ r) / Rd ** 3 * 0.5 * (3 * cosp ** 2 - 1)
        assert abs(en["W"][0] / quad - 1) < 5 * np.linalg.norm(r) / Rd, (Rd, en["W"][0], quad)


def _passage_energies(name, t_end=1500.0, n_out=15001):
    from scipy.integrate import solve_ivp
    kw, _ = PASSAGES[name]
    s = T.HillsSetup(**kw)
    st = T.puncture_state(s, k0=4.0, k_from=10.0)
    m = st["masses"]
    rhs = T._rhs_factory(m[None, :], np.array([1.0]))
    idx0 = np.zeros(1, dtype=int)
    sol = solve_ivp(lambda t, y: rhs(np.array([t]), y[None, :], idx0)[0], (0.0, t_end),
                    np.concatenate([st["positions"].ravel(), st["velocities"].ravel()]),
                    method="DOP853", rtol=1e-12, atol=1e-14, dense_output=True)
    tt = np.linspace(0.0, t_end, n_out)
    Y = sol.sol(tt).T
    en = T.member_energies(Y[:, :9].reshape(-1, 3, 3), Y[:, 9:].reshape(-1, 3, 3), m)
    return s, tt, en


def test_member_energy_conserved_after_capture():
    """Q1 (JOURNAL wave 2): the case the lead found (V5b). After the encounter one member
    is captured; its partner's energy against M alone oscillates with the inner orbit by
    more than 0.1 units and never settles; the corrected energy varies at least 1000
    times less after t = 300 and settles below 1e-5 units after t = 1000; the corrected
    energies add up to E_tot - W exactly, and the coupling W decays."""
    want = {"q10": 1.6127, "q4": 1.3119}            # V5b, stage/G0/checks/v5b_summary.json
    for name in ("q10", "q4"):
        s, tt, en = _passage_energies(name)
        u = s.energy_unit
        late, later = tt >= 300.0, tt >= 1000.0
        assert np.all(en["inner"][late] == 2)        # m2 captured, m1 ejected (V5)
        old = np.ptp(en["E1_M"][late] / u)
        new = np.ptp(en["E1"][late] / u)
        assert old > 0.1, (name, old)
        assert new < 1e-3 * old, (name, new, old)
        assert np.ptp(en["E1"][later] / u) < 1e-5, (name, np.ptp(en["E1"][later] / u))
        assert np.ptp(en["E1_M"][later] / u) > 0.1
        assert abs(en["E1"][-1] / u - want[name]) < 1e-3, (name, en["E1"][-1] / u)
        ident = (en["E1"] + en["E2"] + en["W"] - en["E_tot"]) / u
        assert np.max(np.abs(ident[late])) < 1e-10, (name, np.max(np.abs(ident[late])))
        assert np.max(np.abs(en["W"][later] / u)) < 1e-5, (name, np.max(np.abs(en["W"][later] / u)))


def test_restricted_limit_of_corrected_energies():
    """Q3: at M/m = 1e6 the corrected and old dE agree to 1e-5 of |dE| for disrupted
    binaries (the difference is of order m/M)."""
    ss = [T.HillsSetup(M=1e6, m1=0.75, m2=0.25, a=1.0, D=0.3, phase=ph)
          for ph in np.linspace(0, 2 * np.pi, 16, endpoint=False)]
    o = T.scatter(ss)
    d = np.isin(o["outcome"], [T.EJECT1, T.EJECT2])
    assert d.sum() >= 8
    rel = np.abs(o["dE"][d] - o["dE_M"][d]) / np.abs(o["dE"][d])
    assert np.max(rel) < 1e-5, rel
    assert np.array_equal(o["outcome"], o["outcome_M"])


def test_end_time_independence_at_finite_q():
    """Q2 in small: M/m = 10, D = 0.5, prograde, 16 phases: the corrected dE of single
    ejections is the same at k_end = 30 and 100 r_t to 1e-3 units; the old one is not."""
    ss = [T.HillsSetup(M=10.0, m1=0.5, m2=0.5, a=1.0, D=0.5, phase=ph)
          for ph in np.linspace(0, 2 * np.pi, 16, endpoint=False)]
    a = T.scatter(ss, k_end=30.0)
    b = T.scatter(ss, k_end=100.0)
    single = np.isin(a["outcome"], [T.EJECT1, T.EJECT2]) & (a["outcome"] == b["outcome"])
    assert single.sum() >= 6
    assert np.max(np.abs(a["dE"][single] - b["dE"][single])) < 1e-3
    assert np.max(np.abs(a["dE_M"][single] - b["dE_M"][single])) > 0.05
    # survivors carry no member energies
    surv = a["outcome"] == T.SURVIVED
    assert np.all(np.isnan(a["dE"][surv])) and np.all(np.isfinite(a["dE_M"][surv]))


def test_puncture_state_reproduces_the_inputs():
    """Q6: the start states of three_punctures/inputs (newton_start.py: 20000-sample
    trajectory from 10 r_t, read at 4 r_t by linear interpolation) within 1e-4 in position
    and 1e-6 in momentum; invariants; the block parses back."""
    for name, (kw, fn) in PASSAGES.items():
        s = T.HillsSetup(**kw)
        st = T.puncture_state(s, k0=4.0, k_from=10.0)
        m, x, p = st["masses"], st["positions"], st["momenta"]
        assert abs(st["checks"]["cm_distance"] / (4.0 * s.r_t) - 1) < 1e-10
        assert np.abs(p.sum(axis=0)).max() < 1e-15 and np.abs((m[:, None] * x).sum(0)).max() < 1e-13
        order = [1, 2, 0]                                   # comp0 = m1, comp1 = m2, comp2 = M
        path = os.path.join(INPUTS, fn)
        if os.path.exists(path):
            ref = T.parse_problem_block(open(path).read())
            assert np.allclose(ref["masses"], m[order], rtol=0, atol=0)
            assert np.abs(ref["positions"] - x[order]).max() < 1e-4, (name, np.abs(ref["positions"] - x[order]).max())
            assert np.abs(ref["momenta"] - p[order]).max() < 1e-6, (name, np.abs(ref["momenta"] - p[order]).max())
        back = T.parse_problem_block(T.multi_puncture_block(st))
        assert np.abs(back["positions"] - x[order]).max() < 1e-11
        assert np.abs(back["momenta"] - p[order]).max() < 1e-14
        assert np.all(back["spins"] == 0)
        # placed directly on the conic: identical to initial_state
        d = T.puncture_state(s, r0=4.0 * s.r_t)
        ic = T.initial_state(s, r0=4.0 * s.r_t)
        assert np.allclose(d["momenta"], ic["momenta"], rtol=0, atol=1e-16)
        assert np.allclose(d["positions"], ic["positions"], rtol=0, atol=1e-13)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
