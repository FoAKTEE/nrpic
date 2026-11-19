#!/usr/bin/env python3
"""Independent check of the exact events of data set 3 (prep_bh.py, exact.json): the
closed-form cycloid of expball/exact.py against a direct numerical integration of the
shell equation d^2R/dtau^2 = -m/R^2 (dust, Misner-Sharp mass m conserved) from the
initial slice (R = R_i, dR/dtau = v(R_i) of expball/model.py), for shells inside the
core, at its edge and in the underdense shell: turnaround, R = 2m (trapping) and the
radius at fixed proper times. Also the core mass in closed form,
m(R1) = (1 + delta_c) H^2 R1^3 / 2.

    verify_ds3.py --prep <prep_bh output> --out <dir>
"""
import argparse
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ex = C.load_json(os.path.join(a.prep, "exact.json"))
    spec = ex["spec"]
    ball = C.ball_from_spec(spec)
    R1 = spec["R1"]
    m_closed = 0.5 * (1.0 + spec["delta_c"]) * ball.H ** 2 * R1 ** 3
    shells = np.array([0.3 * R1, 0.8 * R1, R1 * (1 - 1e-9), R1 + 0.02, R1 + 0.1, R1 + 0.3])
    rows = []
    for Ri in shells:
        c = ball.at(np.array([Ri]))
        m, E, v = float(c["m"][0]), float(c["E"][0]), float(c["v"][0])

        def rhs(t, y):
            return [y[1], -m / y[0] ** 2]

        def ev_ah(t, y):
            return y[0] - 2.0 * m
        ev_ah.terminal = True
        ev_ah.direction = -1

        def ev_ta(t, y):
            return y[1]
        ev_ta.direction = -1
        sol = solve_ivp(rhs, (0.0, 200.0), [Ri, v], method="DOP853", rtol=1e-12, atol=1e-14,
                        events=[ev_ah, ev_ta], dense_output=True)
        tau_ah = float(sol.t_events[0][0]) if len(sol.t_events[0]) else math.inf
        tau_ta = float(sol.t_events[1][0]) if len(sol.t_events[1]) else math.inf
        S = C.XE.Shells(ball, np.array([Ri]))
        Rq = {}
        for tq in (2.0, 5.0, 8.0):
            if tq < sol.t[-1]:
                Rq[str(tq)] = dict(ode=float(sol.sol(tq)[0]), cycloid=float(S.R(np.array([tq]))[0, 0]))
        rows.append(dict(R_i=float(Ri), m=m, E=E, tau_ta_ode=tau_ta, tau_ta_cycloid=float(S.tau_ta[0]),
                         tau_ah_ode=tau_ah, tau_ah_cycloid=float(S.tau_ah[0]),
                         tau_ah_from_eta=float(S.tau_ah_cycloid()[0]), R_at=Rq))
        print(f"R_i = {Ri:.6f}: m = {m:.6f}, tau_ta ode {tau_ta:.9f} cycloid {S.tau_ta[0]:.9f}; "
              f"tau_AH ode {tau_ah:.9f} cycloid {S.tau_ah[0]:.9f} (eta form {S.tau_ah_cycloid()[0]:.9f})")
    res = dict(m_core_closed_form=m_closed, m_first_trapped=ex["first_trapped"]["m"],
               tau_first_trapped=ex["first_trapped"]["tau"], shells=rows,
               max_rel_diff_tau_ah=max(abs(r["tau_ah_ode"] / r["tau_ah_cycloid"] - 1) for r in rows
                                      if math.isfinite(r["tau_ah_ode"])),
               max_rel_diff_tau_ta=max(abs(r["tau_ta_ode"] / r["tau_ta_cycloid"] - 1) for r in rows),
               max_rel_diff_R=max(abs(q["ode"] / q["cycloid"] - 1) for r in rows for q in r["R_at"].values()))
    print(f"core mass closed form {m_closed:.9f}, exact.json first trapped m {ex['first_trapped']['m']:.9f}")
    print({k: v for k, v in res.items() if k.startswith("max")})
    C.write_json(os.path.join(a.out, "verify_ds3.json"), res)
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.90, wspace=0.32)
    ax = fig.add_subplot(1, 2, 1)
    ax.semilogy([r["R_i"] for r in rows], [max(abs(r["tau_ah_ode"] - r["tau_ah_cycloid"]), 1e-16) for r in rows],
                "o-", color=fs.PAL["blue"], label=r"$\tau_{\rm AH}$")
    ax.semilogy([r["R_i"] for r in rows], [max(abs(r["tau_ta_ode"] - r["tau_ta_cycloid"]), 1e-16) for r in rows],
                "s-", color=fs.PAL["red"], label=r"$\tau_{\rm ta}$")
    ax.axvline(R1, **fs.MASK_LINE)
    ax.set_xlabel(r"$R_i\,/M$")
    ax.set_ylabel(r"|ODE $-$ closed form| $/M$")
    ax.legend(fontsize=8)
    ax.set_title("data set 3: event times, two methods", fontsize=10)
    ax = fig.add_subplot(1, 2, 2)
    ax.plot([r["R_i"] for r in rows], [r["tau_ah_cycloid"] for r in rows], "o-", color=fs.PAL["blue"])
    ax.axhline(ex["first_trapped"]["tau"], **fs.GUIDE)
    ax.axvline(R1, **fs.MASK_LINE)
    ax.set_xlabel(r"$R_i\,/M$")
    ax.set_ylabel(r"$\tau_{\rm AH}\,/M$")
    ax.set_title("trapping times (dashed: first trapped sphere)", fontsize=10)
    fs.save(fig, os.path.join(a.out, "fig_verify_ds3"))


if __name__ == "__main__":
    main()
