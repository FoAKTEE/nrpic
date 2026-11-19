#!/usr/bin/env python3
"""Predictions for the passages from the start states of the NR inputs, with the three references
(predictions: ../JOURNAL.md entry 6, P1a-P1c).

Inputs (read only): nr_first/inputs/p1_q4.athinput (P1 of wave 2, q = 4) and
three_punctures/inputs/hills_q10_m8.athinput (the q = 10 passage of stage/G1/STATUS.md).
Components: members first (comp0 = m1, comp1 = m2), M last; bare masses, positions and
Bowen-York momenta P.
Models (all from the same positions; t = 0 at the start state):
  newton     full Newtonian three-body problem, v = P/m (eih.accel with c2inv = 0)
  hrna       geodesic_binary/hrna.py, hole fixed, positions and v = P/m relative to M
  eih_v      EIH, v = P/m read as coordinate velocities (like-for-like with the two baselines)
  eih_p      EIH, P read as canonical 1PN momenta (the reading of the Bowen-York momenta)
  eih_p_m    eih_p with the masses of the horizons at t = 0 instead of the bare masses
             (q = 4: 0.12778 for the members and 0.99607 for M, nr_first C0 at m/8;
             q = 10: 0.052 and 1.0, the middle of the run-health prediction of
             stage/G1/STATUS.md) [JUDGEMENT: a sensitivity variant, not a reading]
Writes p1.json and fig_p1_<q>.{png,pdf}. Needs numba (venv-gb). Usage: p1.py [outdir]
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRK = os.path.dirname(PKG)
WT = os.path.abspath(os.path.join(TRK, "..", ".."))
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(TRK, "geodesic_binary"))
sys.path.insert(0, os.path.join(WT, "python"))
import eih  # noqa: E402
from hills3 import threebody as tb  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

CASES = {
    "q4": dict(path=os.path.join(TRK, "nr_first/inputs/p1_q4.athinput"), a=5.0, tlim=280.0,
               horizon=(0.99607, 0.12778, 0.12778)),
    "q10": dict(path=os.path.join(TRK, "three_punctures/inputs/hills_q10_m8.athinput"), a=3.0,
                tlim=200.0, horizon=(1.0, 0.052, 0.052)),
}
T_END = 1500.0
R_GRCAP = 5.35
R_TRUST = 12.0


def integrate(ms, x, v, c2inv, t_end=T_END):
    def f(t, y):
        xx = y[:9].reshape(3, 3)
        vv = y[9:].reshape(3, 3)
        return np.concatenate([vv.ravel(), eih.accel(xx, vv, ms, c2inv).ravel()])
    sol = solve_ivp(f, (0.0, t_end), np.concatenate([x.ravel(), v.ravel()]), method="DOP853",
                    rtol=1e-12, atol=1e-14, dense_output=True)
    tt = np.linspace(0.0, t_end, 30001)
    Y = sol.sol(tt).T
    return tt, Y[:, :9].reshape(-1, 3, 3), Y[:, 9:].reshape(-1, 3, 3), sol


def first_min(t, r):
    i = np.arange(1, len(r) - 1)
    lo = i[(r[i] < r[i - 1]) & (r[i] <= r[i + 1])]
    return (float(t[lo[0]]), float(r[lo[0]])) if lo.size else (None, None)


def summarize_nbody(name, tt, X, V, ms, unit, a0, tlim, c2inv):
    r1 = np.linalg.norm(X[:, 1] - X[:, 0], axis=1)
    r2 = np.linalg.norm(X[:, 2] - X[:, 0], axis=1)
    r12 = np.linalg.norm(X[:, 2] - X[:, 1], axis=1)
    en = tb.member_energies(X[-1][None], V[-1][None], ms)
    outc, _ = tb.classify(en, X[-1][None], V[-1][None], ms)
    inner = int(en["inner"][0])
    leaves = None
    if outc[0] in (1, 2):
        leaves = "m1" if outc[0] == 2 else "m2"
    i_lim = np.searchsorted(tt, tlim)
    E0 = float(eih.energy(X[0], V[0], ms, c2inv))
    Ef = float(eih.energy(X[-1], V[-1], ms, c2inv))
    mc = ms[inner]
    me = ms[3 - inner]
    mu_out = me * (ms[0] + mc) / ms.sum()
    eout = float(en["E_out"][0])
    sep = np.argmax(r12 > 2 * a0)
    out = dict(model=name, outcome=int(outc[0]), outcome_name=tb.OUTCOME_NAMES[int(outc[0])],
               leaves=leaves, E_out_units=eout / unit, E_in_units=float(en["E_in"][0]) / unit,
               vinf=(math.sqrt(2 * eout / mu_out) if eout > 0 else None),
               inner_a=float(en["a_in"][0]), inner_e=float(en["e_in"][0]),
               inner_rp=float(en["rp_in"][0]),
               rmin_m1=float(r1.min()), rmin_m2=float(r2.min()),
               first_peri_m1=first_min(tt, r1), first_peri_m2=first_min(tt, r2),
               t_binary_wider_2a=(float(tt[sep]) if r12[sep] > 2 * a0 else None),
               at_tlim=dict(t=float(tt[i_lim]), r1M=float(r1[i_lim]), r2M=float(r2[i_lim]),
                            r12=float(r12[i_lim])),
               M_displacement_tlim=float(np.linalg.norm(X[i_lim, 0] - X[0, 0])),
               dE_run_units=(Ef - E0) / unit)
    if c2inv:
        out["grcap_proxy_m1"] = bool(r1.min() < R_GRCAP)
        out["grcap_proxy_m2"] = bool(r2.min() < R_GRCAP)
        out["inside_trust_radius"] = bool(min(r1.min(), r2.min()) < R_TRUST)
    return out, dict(t=tt, r1=r1, r2=r2, r12=r12)


def run_hrna(ms, x, v, a0, rt, unit, tlim):
    import hrna
    if hrna._WK is None:
        hrna._WK = hrna._work()
    M, m1, m2 = ms
    y0 = np.concatenate([x[1] - x[0], v[1] - v[0], x[2] - x[0], v[2] - v[0]])
    T0 = 2 * math.pi * math.sqrt(a0 ** 3 / (m1 + m2))
    status, t, y, diag, rec_t, rec_y, nrec, nsteps, nrej = hrna.integrate(
        hrna.LAW_HRNA, hrna.COORDS_SCH, hrna.PAIR_GRAVITY, M, 0.0, m1, m2, 0.0, 0.0, y0,
        T0 / 200.0, 1e-12, 1e-14, 1e9, 1e9, 2.5, T_END, 50_000_000, a0, 400000,
        hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._WK)
    s = hrna.summarize(hrna.LAW_HRNA, hrna.COORDS_SCH, M, 0.0, m1, m2, a0, y, diag, T0)
    rt_ = np.array(rec_t[:nrec])
    ry = np.array(rec_y[:nrec])
    r1 = np.linalg.norm(ry[:, 0:3], axis=1)
    r2 = np.linalg.norm(ry[:, 6:9], axis=1)
    r12 = np.linalg.norm(ry[:, 0:3] - ry[:, 6:9], axis=1)
    leaves = None
    if s["outcome"] in (1, 2):
        leaves = "m1" if s["outcome"] == 2 else "m2"
    elif s["outcome"] == 6:
        leaves = ("m2" if s["eps2"] > 0 else None) if s["plunged"] == 1 else \
                 (("m1" if s["eps1"] > 0 else None) if s["plunged"] == 2 else None)
    i_lim = min(np.searchsorted(rt_, tlim), len(rt_) - 1)
    sep = np.argmax(r12 > 2 * a0)
    return dict(model="hrna", outcome=int(s["outcome"]), status=int(status), t_end=float(t),
                plunged=int(s["plunged"]), leaves=leaves, E1_u=s["E1_u"], E2_u=s["E2_u"],
                vinf_exact=s["vinf_exact"], rmin_m1=float(r1.min()), rmin_m2=float(r2.min()),
                first_peri_m1=first_min(rt_, r1), first_peri_m2=first_min(rt_, r2),
                t_binary_wider_2a=(float(rt_[sep]) if r12[sep] > 2 * a0 else None),
                at_tlim=dict(t=float(rt_[i_lim]), r1M=float(r1[i_lim]), r2M=float(r2[i_lim]),
                             r12=float(r12[i_lim]))), dict(t=rt_, r1=r1, r2=r2, r12=r12)


def cm_invariants(ms, x, v, c2inv=1.0):
    M, m1, m2 = ms
    mb = m1 + m2
    xc = (m1 * x[1] + m2 * x[2]) / mb
    vc = (m1 * v[1] + m2 * v[2]) / mb
    X = np.array([x[0], xc])
    V = np.array([v[0], vc])
    m2b = np.array([M, mb])
    mu = M * mb / (M + mb)
    return dict(E_per_mu=float(eih.energy(X, V, m2b, c2inv)) / mu,
                J_per_mu=float(np.linalg.norm(eih.angular_momentum(X, V, m2b, c2inv))) / mu,
                r0=float(np.linalg.norm(xc - x[0])))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    allres = {}
    fs.use_style()
    import matplotlib.pyplot as plt
    for qn, case in CASES.items():
        ms, x, P = eih.puncture_masses_positions_momenta(case["path"])
        a0 = case["a"]
        mb = ms[1] + ms[2]
        rt = a0 * (ms[0] / mb) ** (1 / 3)
        unit = ms[1] * ms[2] / a0 * (ms[0] / mb) ** (1 / 3)
        v_newt = P / ms[:, None]
        v_can = eih.velocities_from_momenta(x, P, ms)
        msh = np.array(case["horizon"])
        v_can_h = eih.velocities_from_momenta(x, P, msh)
        res = dict(input=os.path.relpath(case["path"], WT), masses=ms.tolist(), unit=unit, a0=a0,
                   r_t=rt, tlim=case["tlim"],
                   start=dict(cm_1pn_velocity_reading=cm_invariants(ms, x, v_newt),
                              cm_1pn_canonical_reading=cm_invariants(ms, x, v_can),
                              cm_newton=cm_invariants(ms, x, v_newt, 0.0),
                              v_can_over_v_newt=(np.linalg.norm(v_can, axis=1)
                                                 / np.linalg.norm(v_newt, axis=1)).tolist(),
                              P_total_1pn_canonical=eih.momentum(x, v_can, ms).tolist()),
                   models={})
        curves = {}
        for name, msx, vv, c2 in (("newton", ms, v_newt, 0.0), ("eih_v", ms, v_newt, 1.0),
                                  ("eih_p", ms, v_can, 1.0), ("eih_p_m", msh, v_can_h, 1.0)):
            tt, X, V, _ = integrate(msx, x, vv, c2)
            u = msx[1] * msx[2] / a0 * (msx[0] / (msx[1] + msx[2])) ** (1 / 3)
            s, c = summarize_nbody(name, tt, X, V, msx, u, a0, case["tlim"], c2)
            res["models"][name] = s
            curves[name] = c
            print(qn, json.dumps(s, default=float))
        s, c = run_hrna(ms, x, v_newt, a0, rt, unit, case["tlim"])
        res["models"]["hrna"] = s
        curves["hrna"] = c
        print(qn, json.dumps(s, default=float))
        allres[qn] = res
        # figure
        fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.2, 3.0))
        sty = dict(newton=dict(color="grey", lw=1.5, label="Newton"),
                   hrna=dict(color=fs.PAL["green"], lw=1.5, label="HRNA (hole fixed)"),
                   eih_v=dict(color=fs.PAL["red"], lw=1.5, label="EIH, v = P/m"),
                   eih_p=dict(color=fs.PAL["blue"], lw=1.5, label="EIH, P canonical"),
                   eih_p_m=dict(color=fs.PAL["blue"], lw=1.0, ls="--",
                                label="EIH, P canonical, horizon masses"))
        for name, c in curves.items():
            m = c["t"] <= 320
            ax[0].plot(c["t"][m], c["r1"][m], **sty[name])
            ax[1].plot(c["t"][m], c["r2"][m], **sty[name])
            ax[2].semilogy(c["t"][m], c["r12"][m], **sty[name])
        for k in (0, 1):
            ax[k].axhspan(0, R_GRCAP, color="grey", alpha=0.15, lw=0)
            ax[k].axhline(R_TRUST, **fs.MASK_LINE)
            ax[k].set_ylim(0, 60)
            ax[k].set_xlabel(r"$t/M$")
        for k in range(3):
            ax[k].axvline(case["tlim"], color="k", lw=0.8, ls=":")
        ax[0].set_ylabel(r"$|x_1 - x_M|\,/M$ (m1, comp0)")
        ax[1].set_ylabel(r"$|x_2 - x_M|\,/M$ (m2, comp1)")
        ax[2].set_ylabel(r"$|x_1 - x_2|\,/M$")
        ax[2].set_xlabel(r"$t/M$")
        ax[0].legend(frameon=False, fontsize=6.5, loc="upper left")
        ax[0].set_title(f"{qn}: {os.path.basename(case['path'])}", fontsize=8)
        fig.tight_layout()
        fs.save(fig, os.path.join(out, f"fig_p1_{qn}"))
        plt.close(fig)
    with open(os.path.join(out, "p1.json"), "w") as fh:
        json.dump(allres, fh, indent=1, default=float)


if __name__ == "__main__":
    main()
