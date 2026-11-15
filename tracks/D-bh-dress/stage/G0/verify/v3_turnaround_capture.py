#!/usr/bin/env python3
"""Verifier checks C3 and C5: turnaround and collapse of cold dust around a point mass in
Einstein-de Sitter (closed-form Kepler orbits, my own parametrisation), and the capture
condition of a particle at turnaround in Schwarzschild (exact effective potential).

C3. Units G = c = M = 1, dimensionless time tau = H_i t, radius x = r / r_i. A shell that
    encloses background mass M_b (mu = M / M_b) starts at tau = 0 with x = 1, x' = 1
    (unperturbed Hubble flow, the scoping set-up): x'' = -(1 + mu) / (2 x^2), energy
    -mu/2, so x = A (1 - cos th), tau - tau_0 = B (th - sin th), A = (1+mu)/(2 mu),
    B = sqrt(2 A^3/(1 + mu)). Background: (a/a_i)^(3/2) = 1 + (3/2) tau.
    Turnaround at th = pi, collapse (x = 0) at th = 2 pi. r_i = (2 M_b / eps^2)^(1/3).
    Cold growth law: shells are absorbed in order (collapse time increases with M_b), so
    M_BH(a) - M = M_b of the shell that collapses at a.
C5. Particle at areal radius r with zero radial and tangential speed v (static frame):
    E = sqrt(1 - 2/r) gamma, L = r gamma v. Captured iff E^2 > V_max(L), with
    V = (1 - 2/r)(1 + L^2/r^2) and V_max at r_u = (L^2/2)(1 - sqrt(1 - 12/L^2)).
    Threshold v_c(r) found by bisection; compared with 4/r (the E = 1 value L_c = 4).

Usage: v3_turnaround_capture.py [--out DIR]   (default $NRPIC_RUN_DIR)
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def orbit(mu):
    A = (1 + mu) / (2 * mu)
    B = math.sqrt(2 * A ** 3 / (1 + mu))
    th_i = math.acos(1 - 1 / A)          # outgoing branch, th in (0, pi)
    t_i = B * (th_i - math.sin(th_i))
    tau_ta = B * math.pi - t_i
    tau_c = B * 2 * math.pi - t_i
    return A, B, tau_ta, tau_c


def a_of_tau(tau):
    return (1 + 1.5 * tau) ** (2 / 3)


def a_ta(mu):
    return a_of_tau(orbit(mu)[2])


def a_c(mu):
    return a_of_tau(orbit(mu)[3])


def Mb_at(a, fn):
    """background mass M_b = 1/mu of the shell for which fn(mu) = a"""
    f = lambda lm: fn(math.exp(-lm)) - a   # lm = ln M_b
    return math.exp(brentq(f, -30, 30, xtol=1e-14, rtol=1e-14))


def r_ta(Mb, eps):
    mu = 1 / Mb
    ri = (2 * Mb / eps ** 2) ** (1 / 3)
    return ri * (1 + mu) / mu


def Vmax(L):
    if L * L <= 12:
        return None
    ru = (L * L / 2) * (1 - math.sqrt(1 - 12 / (L * L)))
    return (1 - 2 / ru) * (1 + L * L / ru ** 2), ru


def Lc_of_E(E):
    """critical angular momentum: V_max(L) = E^2 (E between sqrt(8/9) and above)"""
    f = lambda L: Vmax(L)[0] - E * E
    return brentq(f, math.sqrt(12) * (1 + 1e-12), 1e3, xtol=1e-14)


def captured(r, v):
    g = 1 / math.sqrt(1 - v * v)
    E = math.sqrt(1 - 2 / r) * g
    L = r * g * v
    vm = Vmax(L)
    if vm is None:
        return True
    Vm, ru = vm
    if r < ru:      # inside the barrier: falls in
        return True
    return E * E > Vm


def v_threshold(r):
    """captured below, not captured above (sign change found by bisection)"""
    return brentq(lambda v: 0.5 if captured(r, v) else -0.5, 1e-6, 0.99, xtol=1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--figdir", default=os.path.join(HERE, "..", "figs"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    # --- C3: turnaround ------------------------------------------------------------
    # integration check of one orbit against the closed form
    from scipy.integrate import solve_ivp
    mu = 1 / 0.525
    sol = solve_ivp(lambda t, y: [y[1], -(1 + mu) / (2 * y[0] ** 2)], [0, 50], [1, 1],
                    rtol=1e-12, atol=1e-14, events=lambda t, y: y[1], dense_output=True)
    res["integration_check"] = {"mu": mu, "tau_ta_ode": float(sol.t_events[0][0]),
                                "tau_ta_closed": orbit(mu)[2],
                                "x_max_ode": float(sol.y_events[0][0][0]), "x_max_closed": (1 + mu) / mu}
    tab = []
    for af in (2, 4, 10, 100, 121.5, 1000, 1e4):
        Mb = Mb_at(af, a_ta)
        Mbc = Mb_at(af, a_c) if af > 1.2 else float("nan")
        row = {"a_over_ai": af, "Mb_ta": Mb, "Mb_ta_over_a": Mb / af, "total_ta_with_hole": 1 + Mb,
               "Mb_captured": Mbc, "Mb_captured_over_a": Mbc / af,
               "r_ta": {str(e): r_ta(Mb, e) for e in (0.003, 0.01, 0.03, 0.1)}}
        tab.append(row)
    res["turnaround_table"] = tab
    res["asymptote_4_over_3pi_2_3"] = (4 / (3 * math.pi)) ** (2 / 3)
    res["asymptote_captured"] = (4 / (3 * math.pi)) ** (2 / 3) / 2 ** (2 / 3)
    # slopes at a = 1000
    h = 1e-4
    l1, l2 = math.log(1000 * (1 - h)), math.log(1000 * (1 + h))
    m1, m2 = Mb_at(1000 * (1 - h), a_ta), Mb_at(1000 * (1 + h), a_ta)
    r1, r2 = r_ta(m1, 0.01), r_ta(m2, 0.01)
    s_r = (math.log(r2) - math.log(r1)) / (l2 - l1)
    res["slope_dlnrta_dlna_at_1000"] = s_r
    res["frozen_density_slope_at_1000"] = -3 / s_r
    # monotonic collapse order (no shell crossing before capture)
    mbs = np.logspace(-2, 4, 400)
    acs = np.array([a_c(1 / m) for m in mbs])
    res["collapse_order_monotonic"] = bool(np.all(np.diff(acs) > 0))
    # run length per factor in a
    res["T_run"] = {str(e): {"x2": (2 / (3 * e)) * (2 ** 1.5 - 1), "x4": (2 / (3 * e)) * (4 ** 1.5 - 1)}
                    for e in (0.01, 0.03, 0.1)}
    # --- C5: capture -------------------------------------------------------------------
    cap = []
    for r in (8.0, 16.1, 18.1, 33.4, 40.3, 74.6, 187.0, 1000.0):
        vt = v_threshold(r)
        g = 1 / math.sqrt(1 - vt * vt)
        E = math.sqrt(1 - 2 / r) * g
        cap.append({"r": r, "v_threshold": vt, "4_over_r": 4 / r, "ratio": vt / (4 / r), "E_at_threshold": E,
                    "L_at_threshold": r * g * vt, "Lc_of_E": Lc_of_E(E) if E < 1 else float("nan"),
                    "v_circ_1.5M": math.sqrt(1.5 / r)})
    res["capture"] = cap
    res["Lc_E1"] = Lc_of_E(1.0)
    with open(os.path.join(a.out, "v3_turnaround_capture.json"), "w") as f:
        json.dump(res, f, indent=1)

    # --- figure -------------------------------------------------------------------------
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    aa = np.logspace(math.log10(1.05), 4, 120)
    mt = np.array([Mb_at(x, a_ta) for x in aa])
    mc = np.array([Mb_at(x, a_c) for x in aa if x > 1.2])
    ax[0].loglog(aa, mt / aa, color=fs.PAL["blue"], label=r"turned around, $M_{b,\rm ta}/(a/a_i)$")
    ax[0].loglog(aa[aa > 1.2], mc / aa[aa > 1.2], color=fs.PAL["red"], label=r"absorbed (cold), $M_{b,c}/(a/a_i)$")
    ax[0].axhline(res["asymptote_4_over_3pi_2_3"], **fs.GUIDE)
    ax[0].axhline(res["asymptote_captured"], color="k", lw=1.0, ls=":")
    for x in (2, 4, 10):
        ax[0].axvline(x, **fs.MASK_LINE)
    ax[0].set_xlabel(r"$a/a_i$"); ax[0].set_ylabel(r"mass $/ M$ per unit $a/a_i$")
    ax[0].set_ylim(0.05, 1.0)
    ax[0].legend(frameon=False, fontsize=7, loc="lower right")
    rr = np.logspace(math.log10(6.5), 3, 80)
    vt = np.array([v_threshold(x) for x in rr])
    ax[1].loglog(rr, vt, color=fs.PAL["blue"], label="exact Schwarzschild threshold")
    ax[1].loglog(rr, 4 / rr, **fs.GUIDE, label=r"$4M/r$ ($L_c = 4M$, $E = 1$)")
    ax[1].loglog(rr, np.sqrt(1.5 / rr), color=fs.PAL["red"], lw=1.0, label=r"$(1.5M/r)^{1/2}$")
    for x in (16.1, 33.4):
        ax[1].axvline(x, **fs.MASK_LINE)
    ax[1].set_xlabel(r"turnaround radius $r/M$"); ax[1].set_ylabel(r"tangential speed")
    ax[1].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    files = fs.save(fig, os.path.join(a.out, "v3_turnaround_capture"))
    shutil.copy(files[1], a.figdir)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
