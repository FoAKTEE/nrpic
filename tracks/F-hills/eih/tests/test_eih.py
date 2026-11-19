#!/usr/bin/env python3
"""Tests T0-T3 of the EIH reference (predictions: ../JOURNAL.md entries 1 and 5).

T0  Newtonian limit against newton3; the restricted equation of 2404.16270 (appendix.tex
    l. 127-131, written out here independently of eih.accel) at states with M at rest at the
    origin.
T1  Local consistency of the equations with the integrals: d/dt of Will's E and P, of
    J = sum x_a x p_a and of G - P t along the EIH flow scale as c2inv^2 (Newtonian ones as
    c2inv), at random weak-field three-body states.
T2  Two-body periastron advance k and radial period against Schaefer & Jaranowski
    1805.07240v5 LRRSJarXiv_v5.tex l. 3169-3184 (k = 3/j^2 + O(c^-4); P at 1PN).
T5  The isolated EIH binary: numerical 1PN circular speed against the textbook 1PN value;
    eccentricity of a Newtonian-circular binary at 1PN (JOURNAL entry 10).
T3  Conservation of the 1PN integrals in a Hills encounter, and its scaling with the size of
    the PN terms (lengths x lambda = 8 ... 128, perturbative; lambda = 1 reported).
Usage: test_eih.py <outdir>   (default $NRPIC_RUN_DIR). Writes tests.json and figures.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(WT, "python"))
import eih  # noqa: E402
from hills3.threebody import _rhs_factory, HillsSetup, initial_state_arrays, _stack  # noqa: E402
from hills3.orbits import conic_time_from_pericentre  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

RES = {}


def check(name, ok, **info):
    RES[name] = dict(passed=bool(ok), **info)
    print(f"{'PASS' if ok else 'FAIL'} {name} {json.dumps(info, default=float)}")


# ------------------------------------------------------------------------------------------
def restricted_2404(x1, v1, x2, v2, M, m1, m2):
    """2404.16270 appendix.tex l. 127-131, M fixed at the origin, acceleration of member 1."""
    x12 = x1 - x2
    r12 = np.linalg.norm(x12)
    r1 = np.linalg.norm(x1)
    r2 = np.linalg.norm(x2)
    br1 = (1 - 4 * m2 / r12 - 4 * M / r1 + M * (-1 / r2 + x12 @ x2 / (2 * r2 ** 3))
           - 5 * m1 / r12 + v1 @ v1 - 4 * v1 @ v2 + 2 * v2 @ v2 - 1.5 * (v2 @ x12 / r12) ** 2)
    br2 = (1 - 4 * m2 / r12 - 4 * M / r1 + m2 * (-1 / r2 - x1 @ x2 / (2 * r2 ** 3))
           - 5 * m1 / r1 + v1 @ v1)
    return (-m2 * x12 / r12 ** 3 * br1 - M * x1 / r1 ** 3 * br2
            - 7 * M * m2 * x2 / (2 * r2 ** 3) * (1 / r12 - 1 / r1)
            + m2 / r12 ** 3 * (x12 @ (4 * v1 - 3 * v2)) * (v1 - v2)
            + 4 * M / r1 ** 3 * (x1 @ v1) * v1)


def t0():
    rng = np.random.default_rng(20261119)
    n = 50
    x = rng.normal(size=(n, 3, 3)) * 10
    v = rng.normal(size=(n, 3, 3)) * 0.2
    m = np.abs(rng.normal(size=(n, 3))) + 0.05
    aE = eih.accel(x, v, m, c2inv=0.0)
    rhs = _rhs_factory(m, np.ones(n))
    y = np.concatenate([x.reshape(n, 9), v.reshape(n, 9)], axis=1)
    aN = rhs(np.zeros(n), y, np.arange(n))[:, 9:].reshape(n, 3, 3)
    err = np.max(np.abs(aE - aN)) / np.max(np.abs(aN))
    check("T0a_newton_limit", err < 1e-12, max_rel=err)
    # restricted 2404 form at states with M at rest at the origin
    errs = {}
    for mm in (1e-9, 1e-4, 1e-3, 1e-2, 1e-1):
        e = []
        for i in range(n):
            xs = x[i].copy()
            vs = v[i].copy()
            xs[0] = 0.0
            vs[0] = 0.0
            ms = np.array([1.0, mm, 0.7 * mm])
            a_e = eih.accel(xs, vs, ms)[1]
            a_r = restricted_2404(xs[1], vs[1], xs[2], vs[2], 1.0, ms[1], ms[2])
            a_n = eih.accel(xs, vs, ms, c2inv=0.0)[1]
            e.append(np.linalg.norm(a_e - a_r) / np.linalg.norm(a_e - a_n))
        errs[mm] = float(np.max(e))
    check("T0b_restricted_2404_same_state", max(errs.values()) < 1e-10,
          max_rel_of_PN_part={str(k): v for k, v in errs.items()})
    # derived integrals: sum of canonical momenta equals Will's P (identity)
    pc = eih.canonical_momenta(x, v, m).sum(axis=1)
    PW = eih.momentum(x, v, m)
    err = np.max(np.abs(pc - PW)) / np.max(np.abs(PW))
    check("T0c_sum_canonical_equals_P", err < 1e-12, max_rel=err)
    # inversion p -> v in the weak field of the puncture data (U <~ 0.1): positions x 10
    xw = 10.0 * x
    vb = eih.velocities_from_momenta(xw, eih.canonical_momenta(xw, v, m), m)
    check("T0d_momentum_inversion", np.max(np.abs(vb - v)) < 1e-12,
          max_abs=float(np.max(np.abs(vb - v))))


# ------------------------------------------------------------------------------------------
def t1():
    """Local consistency: d/dt of the integrals along the EIH flow scale as c2inv^2."""
    rng = np.random.default_rng(1119)
    rows = []
    for i in range(30):
        while True:
            x = rng.uniform(-40, 40, size=(3, 3))
            d = np.linalg.norm(x[:, None] - x[None], axis=-1)[np.triu_indices(3, 1)]
            if d.min() > 10:
                break
        v = rng.normal(size=(3, 3))
        v *= rng.uniform(0.05, 0.2, size=(3, 1)) / np.linalg.norm(v, axis=1, keepdims=True)
        ms = np.array([1.0, rng.uniform(0.02, 0.5), rng.uniform(0.02, 0.5)])
        row = {}
        for eps in (1e-2, 1e-3):
            a = eih.accel(x, v, ms, eps)
            h = 1e-2

            def ddt(Q):
                f = lambda s: Q(x + s * v, v + s * a)  # noqa: E731
                return (-f(2 * h) + 8 * f(h) - 8 * f(-h) + f(-2 * h)) / (12 * h)
            row[eps] = dict(
                E=abs(ddt(lambda X, V: eih.energy(X, V, ms, eps))),
                EN=abs(ddt(lambda X, V: eih.energy(X, V, ms, 0.0))),
                P=np.linalg.norm(ddt(lambda X, V: eih.momentum(X, V, ms, eps))),
                PN=np.linalg.norm(ddt(lambda X, V: eih.momentum(X, V, ms, 0.0))),
                J=np.linalg.norm(ddt(lambda X, V: eih.angular_momentum(X, V, ms, eps))),
                JN=np.linalg.norm(ddt(lambda X, V: eih.angular_momentum(X, V, ms, 0.0))),
                G=np.linalg.norm(ddt(lambda X, V: eih.centre_of_mass(X, V, ms, eps)[0])
                                 - eih.momentum(x, v, ms, eps)))
        rows.append({k: row[1e-2][k] / row[1e-3][k] for k in row[1e-2]})
    med = {k: float(np.median([r[k] for r in rows])) for k in rows[0]}
    ok = (all(90 <= med[k] <= 110 for k in ("E", "P", "J", "G"))
          and all(9 <= med[k] <= 11 for k in ("EN", "PN")))
    check("T1_integrals_conserved_to_1PN_order", ok, median_ratio_eps_0p01_over_0p001=med,
          note="JN: the Newtonian angular momentum; its derivative is also O(c2inv)")


# ------------------------------------------------------------------------------------------
def two_body(m1, m2, p, e=0.5, n_orb=6, rtol=1e-13):
    from scipy.optimize import brentq
    Mt = m1 + m2
    mu = m1 * m2 / Mt
    nu = mu / Mt
    rp = p / (1 + e)
    ms = np.array([m1, m2])

    def state(vrel):
        x = np.array([[m2 / Mt * rp, 0, 0], [-m1 / Mt * rp, 0, 0]], float)
        v = np.array([[0, m2 / Mt * vrel, 0], [0, -m1 / Mt * vrel, 0]], float)
        v = v - eih.momentum(x, v, ms) / Mt        # zero 1PN momentum at Newtonian order
        return x, v
    vN = math.sqrt(Mt * (1 + e) / rp)
    target = -(1 - e * e) / (2 * p)
    vrel = brentq(lambda w: float(eih.energy(*state(w), ms)) / mu - target, 0.5 * vN, 1.5 * vN,
                  xtol=1e-15)
    x, v = state(vrel)
    T = 2 * math.pi * math.sqrt((p / (1 - e * e)) ** 3 / Mt)

    def f(t, y):
        xx = y[:6].reshape(2, 3)
        vv = y[6:].reshape(2, 3)
        return np.concatenate([vv.ravel(), eih.accel(xx, vv, ms).ravel()])

    def peri(t, y):
        return (y[0:3] - y[3:6]) @ (y[6:9] - y[9:12])
    peri.direction = 1
    peri.terminal = n_orb
    sol = solve_ivp(f, (0, 50 * T), np.concatenate([x.ravel(), v.ravel()]),
                    method="DOP853", rtol=rtol, atol=1e-16, events=peri, dense_output=True)
    te = sol.t_events[0]
    te = te[te > 1e-6 * T]                      # the start is a periastron itself
    norb = len(te)
    grid = np.unique(np.concatenate([np.linspace(0, te[-1], 400 * norb + 1), te]))
    Y = sol.sol(grid)
    d = Y[0:3] - Y[3:6]
    phi = np.unwrap(np.arctan2(d[1], d[0]))
    k = (np.interp(te[-1], grid, phi) - phi[0]) / (2 * math.pi * norb) - 1.0
    Pr = te[-1] / norb
    J = np.linalg.norm(eih.angular_momentum(x, v, ms))
    E = float(eih.energy(x, v, ms))
    j = J / (mu * Mt)
    Ered = E / mu
    k_pred = 3.0 / j ** 2
    P_pred = 2 * math.pi * Mt / (-2 * Ered) ** 1.5 * (1 - 0.25 * (15 - nu) * Ered)
    Ef = float(eih.energy(sol.y[:6, -1].reshape(2, 3), sol.y[6:, -1].reshape(2, 3), ms))
    return dict(m1=m1, m2=m2, nu=nu, p=p, j=j, Ered=Ered, k=k, k_pred=k_pred,
                dev_k=k / k_pred - 1, P=Pr, P_pred=P_pred, dev_P=Pr / P_pred - 1,
                norb=norb, dE_rel=(Ef - E) / abs(E), vrel_over_newton=vrel / vN)


def t2(out):
    ps = [20, 40, 80, 160, 320, 640]      # fits use p >= 80
    cases = {"nu=0.25": (0.5, 0.5), "q=10": (10 / 11, 1 / 11), "test": (1 - 1e-5, 1e-5)}
    rows = {}
    for name, (m1, m2) in cases.items():
        rows[name] = [two_body(m1, m2, p) for p in ps]
    summ = {}
    ok_all = True
    for name, rr in rows.items():
        j = np.array([r["j"] for r in rr])
        dk = np.abs([r["dev_k"] for r in rr])
        dP = np.abs([r["dev_P"] for r in rr])
        pp = np.array([r["p"] for r in rr], float)
        sk = np.polyfit(np.log(j[2:]), np.log(dk[2:]), 1)[0]
        sP = np.polyfit(np.log(pp[2:]), np.log(dP[2:]), 1)[0]
        coef = (dk * j ** 2)
        ok = (-2.2 <= sk <= -1.8) and (-2.3 <= sP <= -1.7) and np.all((coef > 1) & (coef < 20))
        ok_all &= ok
        summ[name] = dict(slope_k_vs_j=sk, slope_P_vs_p=sP, coef_k_j2=coef.tolist(),
                          dev_k=[r["dev_k"] for r in rr], dev_P=[r["dev_P"] for r in rr],
                          j=j.tolist(), p=ps, k=[r["k"] for r in rr],
                          dE_rel=[r["dE_rel"] for r in rr], norb=[r["norb"] for r in rr])
    check("T2_periastron_advance_and_period", ok_all, **summ)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    for i, (name, s) in enumerate(summ.items()):
        c = fs.SERIES[i]
        ax[0].loglog(s["j"], np.abs(s["dev_k"]), "o-", color=c, label=name)
        ax[1].loglog(s["p"], np.abs(s["dev_P"]), "o-", color=c, label=name)
    jj = np.array(summ["test"]["j"])
    ax[0].loglog(jj, 8.0 / jj ** 2, **fs.GUIDE, label=r"$8/j^2$")
    pp = np.array(ps, float)
    ax[1].loglog(pp, 30 / pp ** 2, **fs.GUIDE, label=r"$\propto p^{-2}$")
    ax[0].set_xlabel(r"$j = J/(\mu M)$")
    ax[0].set_ylabel(r"$|k\,j^2/3 - 1|$")
    ax[1].set_xlabel(r"semi-latus rectum $p/M$")
    ax[1].set_ylabel(r"$|P/P_{\rm 1PN} - 1|$")
    ax[0].legend(frameon=False, fontsize=8)
    ax[0].set_title("periastron advance vs 3/j$^2$", fontsize=9)
    ax[1].set_title("radial period vs 1PN formula", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_t2_periastron"))
    plt.close(fig)


# ------------------------------------------------------------------------------------------
def t3(out):
    s = HillsSetup(M=1.0, m1=0.05, m2=0.05, a=3.0, rp=8.0, phase=math.radians(130.0))
    P = _stack([s])
    rt = P["r_t"][0]
    x0, v0, t0 = initial_state_arrays(P, 4.0 * rt)
    mu = P["M"][0] + P["m"][0]
    tend = conic_time_from_pericentre(P["rp"], P["e_orb"], np.array([mu]), np.array([30 * rt]))[0]
    lams = [1, 8, 16, 32, 64, 128]
    rows = []
    series = None
    for lam in lams:
        x = x0 * lam
        v = v0 / math.sqrt(lam)
        ms = np.array([1.0, 0.05, 0.05])
        res = eih.evolve_states(ms[None], x, v, t0 * lam ** 1.5, np.array([tend * lam ** 1.5]),
                                rtol=1e-12, record_every=(5 if lam == 1 else 0),
                                r_stop=0.0, r12_stop=0.0)
        # trajectory diagnostics: max deviation over the run
        xs = [x[0]]
        vs = [v[0]]
        ts = [t0[0] * lam ** 1.5]
        # rerun with SciPy dense output for the time series (independent integrator path)
        def f(t, y):
            xx = y[:9].reshape(3, 3)
            vv = y[9:].reshape(3, 3)
            return np.concatenate([vv.ravel(), eih.accel(xx, vv, ms).ravel()])
        sol = solve_ivp(f, (t0[0] * lam ** 1.5, tend * lam ** 1.5),
                        np.concatenate([x[0].ravel(), v[0].ravel()]), method="DOP853",
                        rtol=1e-12, atol=1e-14, dense_output=True)
        tt = np.linspace(sol.t[0], sol.t[-1], 4000)
        Y = sol.sol(tt).T
        X = Y[:, :9].reshape(-1, 3, 3)
        V = Y[:, 9:].reshape(-1, 3, 3)
        # scales: the largest kinetic energy, sum m|v| and sum m|x x v| along the run
        K0 = float(np.max(0.5 * np.sum(ms * np.sum(V ** 2, axis=-1), axis=-1)))
        Ps = float(np.max(np.sum(ms * np.linalg.norm(V, axis=-1), axis=-1)))
        Js = float(np.max(np.sum(ms * np.linalg.norm(np.cross(X, V), axis=-1), axis=-1)))
        E1 = eih.energy(X, V, ms)
        EN = eih.energy(X, V, ms, 0.0)
        P1 = eih.momentum(X, V, ms)
        PN = eih.momentum(X, V, ms, 0.0)
        J1 = eih.angular_momentum(X, V, ms)
        JN = eih.angular_momentum(X, V, ms, 0.0)
        G, Ms = eih.centre_of_mass(X, V, ms)
        drift = G - G[0] - np.outer(tt - tt[0], P1[0])
        rows.append(dict(lam=lam,
                         dE1=float(np.max(np.abs(E1 - E1[0])) / K0),
                         dEN=float(np.max(np.abs(EN - EN[0])) / K0),
                         dP1=float(np.max(np.linalg.norm(P1 - P1[0], axis=1)) / Ps),
                         dPN=float(np.max(np.linalg.norm(PN - PN[0], axis=1)) / Ps),
                         dJ1=float(np.max(np.linalg.norm(J1 - J1[0], axis=1)) / Js),
                         dJN=float(np.max(np.linalg.norm(JN - JN[0], axis=1)) / Js),
                         dG=float(np.max(np.linalg.norm(drift, axis=1)) / (lam * 4.0 * rt)),
                         dMs=float(np.max(np.abs(Ms - Ms[0]))),
                         vec_E1PN_err=float(res["E1PN_err"][0]),
                         outcome=int(res["outcome"][0]), rMmin=res["rMmin"][0].tolist()))
        if lam == 1:
            series = dict(t=tt, dE1=(E1 - E1[0]) / K0, dEN=(EN - EN[0]) / K0,
                          dP1=np.linalg.norm(P1 - P1[0], axis=1) / Ps,
                          dPN=np.linalg.norm(PN - PN[0], axis=1) / Ps,
                          dJ1=np.linalg.norm(J1 - J1[0], axis=1) / Js,
                          dJN=np.linalg.norm(JN - JN[0], axis=1) / Js,
                          r1=np.linalg.norm(X[:, 1] - X[:, 0], axis=1),
                          r2=np.linalg.norm(X[:, 2] - X[:, 0], axis=1))
    lam = np.array(lams, float)
    slopes = {}
    for key in ("dE1", "dEN", "dP1", "dPN", "dJ1", "dJN", "dG"):
        y = np.array([r[key] for r in rows])
        slopes[key] = float(np.polyfit(np.log(lam[1:]), np.log(y[1:]), 1)[0])
    same_outcome = len({r["outcome"] for r in rows[1:]}) == 1
    ok = (all(-2.3 <= slopes[k] <= -1.7 for k in ("dE1", "dP1", "dJ1", "dG"))
          and all(-1.15 <= slopes[k] <= -0.85 for k in ("dEN", "dPN"))
          and same_outcome)
    check("T3_conservation_scaling", ok, slopes=slopes, same_outcome_lambda_ge_8=same_outcome,
          rows=rows, note="lambda = 1 reported, not in the fit")
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    for i, (k1, kN, lab) in enumerate((("dE1", "dEN", "energy"), ("dP1", "dPN", "momentum"),
                                       ("dJ1", "dJN", "ang. mom."))):
        c = fs.SERIES[i]
        ax[0].loglog(lam, [r[k1] for r in rows], "o-", color=c, label=f"{lab}, 1PN")
        ax[0].loglog(lam, [r[kN] for r in rows], "s--", color=c, mfc="none",
                     label=f"{lab}, Newtonian")
    ax[0].loglog(lam, [r["dG"] for r in rows], "^-", color=fs.SERIES[3], label="c.o.m. drift")
    ax[0].loglog(lam[1:], rows[1]["dEN"] * lam[1] / lam[1:], **fs.GUIDE)
    ax[0].loglog(lam[1:], rows[1]["dE1"] * lam[1] ** 2 / lam[1:] ** 2, **fs.GUIDE)
    ax[0].set_xlabel(r"length scale $\lambda$ (PN terms $\propto 1/\lambda$)")
    ax[0].set_ylabel("max change / scale")
    ax[0].legend(frameon=False, fontsize=6.5, ncol=1)
    sr = series
    ax[1].semilogy(sr["t"], np.abs(sr["dE1"]) + 1e-18, color=fs.SERIES[0], label="1PN energy")
    ax[1].semilogy(sr["t"], np.abs(sr["dEN"]) + 1e-18, color=fs.SERIES[0], ls="--",
                   label="Newtonian energy")
    ax[1].semilogy(sr["t"], sr["dJ1"] + 1e-18, color=fs.SERIES[2], label="1PN ang. mom.")
    ax[1].set_xlabel(r"$t/M$ ($\lambda = 1$; pericentre at 0)")
    ax[1].set_ylabel("|change| / scale")
    ax2 = ax[1].twinx()
    ax2.plot(sr["t"], np.minimum(sr["r1"], sr["r2"]), color="grey", lw=1, alpha=0.6)
    ax2.set_ylabel(r"closest member to $M$ [$M$]", color="grey")
    ax[1].legend(frameon=False, fontsize=7, loc="lower right")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_t3_conservation"))
    plt.close(fig)


# ------------------------------------------------------------------------------------------
def t5(out):
    """The isolated EIH binary: 1PN circular speed (eih.circular_speed_1pn) against the
    textbook 1PN value u^2 = (m/a)(1 - (3 - nu) m/a) [BACKGROUND], and the eccentricity that a
    Newtonian-circular binary has at 1PN (JOURNAL entry 10)."""
    rows = []
    for (m1, m2, a) in ((0.05, 0.05, 3.0), (0.125, 0.125, 5.0), (0.05, 0.05, 10.0),
                        (0.05, 0.05, 30.0), (0.5, 0.5, 100.0)):
        mb = m1 + m2
        nu = m1 * m2 / mb ** 2
        uN = math.sqrt(mb / a)
        u = eih.circular_speed_1pn(m1, m2, a)
        ms = np.array([m1, m2])
        res = {}
        for lab, uu in (("1pn", u), ("newton", uN)):
            x = np.array([[m2 / mb * a, 0, 0], [-m1 / mb * a, 0, 0]])
            v = np.array([[0, m2 / mb * uu, 0], [0, -m1 / mb * uu, 0]])
            T = 2 * math.pi * math.sqrt(a ** 3 / mb)

            def f(t, y):
                xx = y[:6].reshape(2, 3)
                vv = y[6:].reshape(2, 3)
                return np.concatenate([vv.ravel(), eih.accel(xx, vv, ms).ravel()])
            sol = solve_ivp(f, (0, 5 * T), np.concatenate([x.ravel(), v.ravel()]),
                            method="DOP853", rtol=1e-12, atol=1e-14, dense_output=True)
            tt = np.linspace(0, 5 * T, 5001)
            Y = sol.sol(tt)
            r = np.linalg.norm(Y[0:3] - Y[3:6], axis=0)
            res[lab] = dict(r_min=float(r.min()), r_max=float(r.max()),
                            ecc=float((r.max() - r.min()) / (r.max() + r.min())))
        rows.append(dict(m1=m1, m2=m2, a=a, m_over_a=mb / a, u2_ratio_minus_1=(u / uN) ** 2 - 1,
                         textbook=-(3 - nu) * mb / a,
                         diff_over_m_over_a_sq=((u / uN) ** 2 - 1 + (3 - nu) * mb / a)
                         / (mb / a) ** 2, **{f"{k}_{kk}": vv for k, d in res.items()
                                              for kk, vv in d.items()}))
    coef = [r["diff_over_m_over_a_sq"] for r in rows]
    ok = (all(r["ecc" if False else "1pn_ecc"] < 1e-6 for r in rows)
          and max(coef) - min(coef) < 2.0)
    check("T5_isolated_binary_1pn_circular", ok, rows=rows)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    t0()
    t1()
    t2(out)
    t3(out)
    t5(out)
    with open(os.path.join(out, "tests.json"), "w") as fh:
        json.dump(RES, fh, indent=1, default=float)
    npass = sum(r["passed"] for r in RES.values())
    print(f"{npass} of {len(RES)} passed")


if __name__ == "__main__":
    main()
