#!/usr/bin/env python3
"""Lead's independent checks of wave 3, batch 2a (F-hills JOURNAL.md, lead session of
2026-11-21, predictions L1-L3).

Written by the lead without the packages' readers (p1lib.py, nrread.py, eih.py, ledger_check.py):
it parses AthenaK's raw files and integrates its own equations.

  review3.py p1  <out> <P1 run dir>
      L1: trackers (trk_keep/<stamp>/ copies in time order, then the live files; a later file
      wins where times overlap), separation of trackers 0 and 1, distances to tracker 2;
      horizon summaries (a failed search repeats the previous row or is NaN; good = hrms < 1e-3).
  review3.py g0  <out> <s1.npz>
      L2: arithmetic of the verifier's WRONG items; alpha = a/R_curv in the S1 scan.
  review3.py eih <out>
      L3b: relative 1PN two-body motion (harmonic coordinates; Blanchet, Living Rev. Rel., the
      1PN part of the relative acceleration) of a binary started with the Newtonian circular
      speed. L3c: test-mass parabolas, 1PN (from the Lagrangian
      v^2/2 + M/r + v^4/8 + 3 v^2 M/(2 r) - M^2/(2 r^2)) against exact Schwarzschild.

Writes <out>/review3_<mode>.json and <out>/fig_review3_<mode>.{png,pdf}.
"""
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))


def _fig():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    return plt, fs


# ----------------------------------------------------------------------------------- p1
def read_tracker_series(rundir, n):
    files = sorted(glob.glob(os.path.join(rundir, "trk_keep", "*", f"hills.co_{n}.txt")))
    files.append(os.path.join(rundir, f"hills.co_{n}.txt"))
    rows = {}
    for f in files:                          # later file wins on equal time keys
        a = np.loadtxt(f, comments="#", ndmin=2)
        for r in a:
            rows[round(float(r[1]), 9)] = r[2:5]
    t = np.array(sorted(rows))
    x = np.array([rows[k] for k in t])
    return t, x


def read_horizon(path):
    a = np.loadtxt(path, comments="#", ndmin=2)
    t, m, hrms = a[:, 1], a[:, 2], a[:, 8]
    good = np.isfinite(m) & np.isfinite(hrms) & (hrms < 1e-3)
    rep = np.zeros(len(a), bool)
    rep[1:] = np.all(a[1:, 2:12] == a[:-1, 2:12], axis=1)
    good &= ~rep
    return t, m, hrms, good


def mode_p1(out, rundir):
    res = {"rundir": rundir}
    tr = [read_tracker_series(rundir, n) for n in range(3)]
    tc = np.intersect1d(np.intersect1d(tr[0][0], tr[1][0]), tr[2][0])
    X = [tri[1][np.searchsorted(tri[0], tc)] for tri in tr]
    d01 = np.linalg.norm(X[0] - X[1], axis=1)
    d02 = np.linalg.norm(X[0] - X[2], axis=1)
    d12 = np.linalg.norm(X[1] - X[2], axis=1)
    res["t_range"] = [float(tc[0]), float(tc[-1])]
    res["n_common_rows"] = int(len(tc))
    res["sep01_t0"] = float(d01[0])
    for thr in (2.0, 1.0, 0.5, 0.1):
        i = np.argmax(d01 < thr)
        res[f"t_sep01_below_{thr}"] = float(tc[i]) if d01[i] < thr else None
    early = tc <= 30.0
    res["sep01_monotone_decreasing_to_30"] = bool(np.all(np.diff(d01[early]) <= 1e-6))
    res["sep01_max_increase_to_30"] = float(np.max(np.diff(d01[early])))
    res["d02_t0"], res["d12_t0"] = float(d02[0]), float(d12[0])
    i60 = np.argmin(np.abs(tc - 60.0))
    res["sep01_at_60"] = float(d01[i60])
    # remnant (mean of trackers 0, 1) against tracker 2 at the last common time
    rem = 0.5 * (X[0] + X[1])
    drem = np.linalg.norm(rem - X[2], axis=1)
    res["remnant_to_2_last"] = [float(tc[-1]), float(drem[-1])]
    res["remnant_to_2_min"] = [float(tc[np.argmin(drem)]), float(drem.min())]
    hz = {}
    for n in range(3):
        t, m, h, g = read_horizon(os.path.join(rundir, f"hills.horizon_summary_{n}.txt"))
        big = g & (m > 0.2) & (m < 0.5)
        hz[n] = dict(t=t, m=m, g=g)
        res[f"finder{n}_rows"] = int(len(t))
        res[f"finder{n}_good"] = int(g.sum())
        res[f"finder{n}_first_good"] = [float(t[g][0]), float(m[g][0])] if g.any() else None
        res[f"finder{n}_last_good"] = [float(t[g][-1]), float(m[g][-1])] if g.any() else None
        if big.any():
            res[f"finder{n}_first_common"] = [float(t[big][0]), float(m[big][0])]
            res[f"finder{n}_common_median"] = float(np.median(m[big]))
        pre = g & (t < 48.0) & (m < 0.2)
        if pre.any():
            res[f"finder{n}_last_member_before_48"] = [float(t[pre][-1]), float(m[pre][-1])]
    json.dump(res, open(os.path.join(out, "review3_p1.json"), "w"), indent=1)

    plt, fs = _fig()
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 5.2), sharex=True)
    ax[0].semilogy(tc, d01, color=fs.PAL["red"], label="trackers 0-1")
    ax[0].semilogy(tc, d02, color=fs.PAL["blue"], label="tracker 0 to 2")
    ax[0].semilogy(tc, d12, color=fs.PAL["green"], ls="--", label="tracker 1 to 2")
    ax[0].semilogy(tc, drem, color="k", ls=":", label="mean of 0, 1 to 2")
    ax[0].set_ylabel("coordinate distance [M]")
    ax[0].legend(loc="lower left", fontsize=7)
    for n, c in zip(range(3), (fs.PAL["red"], fs.PAL["orange"], fs.PAL["blue"])):
        g = hz[n]["g"]
        ax[1].plot(hz[n]["t"][g], hz[n]["m"][g], ".", ms=1.5, color=c, label=f"finder {n}")
    ax[1].set_yscale("log")
    ax[1].set_ylabel("horizon mass (hrms < 1e-3) [M]")
    ax[1].set_xlabel("t [M]")
    ax[1].legend(loc="center right", fontsize=7, markerscale=5)
    fig.subplots_adjust(left=0.14, right=0.97, top=0.98, bottom=0.09, hspace=0.06)
    fs.save(fig, os.path.join(out, "fig_review3_p1"))
    print(json.dumps(res, indent=1))


# ----------------------------------------------------------------------------------- g0
def mode_g0(out, s1path):
    res = {}
    g2 = {"q4 triple 15+28+41": 15 + 28 + 41, "two large-r_p passages": 30, "3BH1 rerun": 12,
          "clump relaxation": 5}
    res["G2_items"] = g2
    res["G2_sum"] = sum(g2.values())
    res["G2_sum_m16_corrected"] = res["G2_sum"] - 41 + 44.8
    res["MiB_per_slot"] = 70847.0 / 2700.0
    res["slots_on_81920MiB"] = 81920.0 / res["MiB_per_slot"]
    res["sep_bound_D2085"] = {q: 4 * q ** (2 / 3) / 2.085 for q in (10, 20, 30)}
    res["plunge_bound_4q23"] = {q: 4 * q ** (2 / 3) for q in (10, 20, 30)}
    d = np.load(s1path, allow_pickle=True)
    betas = d["betas"]
    aa, am = d["alpha_all"], d["alpha_max"]   # (law, sense, beta, phase); law 1 = hrna
    meta = json.loads(str(d["meta"]))
    il = meta["laws"].index("hrna")
    ib = int(np.argmin(np.abs(betas - 10.0)))
    res["beta_used"] = float(betas[ib])
    for js, s in enumerate(meta["senses"]):
        res[f"alpha_all_max_hrna_sense{s}_beta10"] = float(np.nanmax(aa[il, js, ib]))
        res[f"alpha_max_max_hrna_sense{s}_beta10"] = float(np.nanmax(am[il, js, ib]))
    res["alpha_all_max_hrna_any"] = float(np.nanmax(aa[il]))
    scop = open(os.path.join(WT, "tracks/F-hills/stage/G0/SCOPING.md")).read().splitlines()
    res["SCOPING_lines_q10_first"] = [f"{i + 1}: {l.strip()[:110]}" for i, l in enumerate(scop)
                                      if ("first passage" in l and "10" in l)
                                      or "hills_q10_m8" in l or "G1 about" in l]
    json.dump(res, open(os.path.join(out, "review3_g0.json"), "w"), indent=1)

    plt, fs = _fig()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.3, 3.0))
    for js, s, c in ((0, meta["senses"][0], fs.PAL["red"]), (1, meta["senses"][1], fs.PAL["blue"])):
        ax.semilogy(betas, np.nanmax(aa[il, js], axis=-1), color=c, label=f"any time, sense {s:+d}")
        ax.semilogy(betas, np.nanmax(am[il, js], axis=-1), color=c, ls="--",
                    label=f"pair bound, sense {s:+d}")
    ax.set_xlabel(r"$\beta$")
    ax.set_ylabel(r"largest $a/R_{\rm curv}$ (HRNA, S1)")
    ax.legend(fontsize=7)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.97, bottom=0.16)
    fs.save(fig, os.path.join(out, "fig_review3_g0"))
    print(json.dumps(res, indent=1))


# ---------------------------------------------------------------------------------- eih
def rel_1pn(t, y, m, nu):
    x, v = y[:3], y[3:]
    r = np.linalg.norm(x)
    n = x / r
    rd = n @ v
    v2 = v @ v
    A = -1.5 * nu * rd ** 2 + (1 + 3 * nu) * v2 - 2 * (2 + nu) * m / r
    B = -2 * (2 - nu) * rd
    return np.concatenate([v, -(m / r ** 2) * ((1 + A) * n + B * v)])


def tm_1pn(t, y):            # test mass, M = 1 (nu = 0 of the same form)
    return rel_1pn(t, y, 1.0, 0.0)


def tm_E_J(r, v):            # radial velocity zero (pericentre)
    E = 0.5 * v ** 2 - 1 / r + 0.375 * v ** 4 + 1.5 * v ** 2 / r + 0.5 / r ** 2
    J = r * v * (1 + 0.5 * v ** 2 + 3 / r)
    return E, J


def swept_gr(rp, r0):
    from scipy.integrate import quad
    L2 = 2 * rp ** 2 / (rp - 2)
    L = math.sqrt(L2)
    up, u0 = 1 / rp, 1 / r0
    f = lambda u: 2 * u - L2 * u ** 2 + 2 * L2 * u ** 3
    g = lambda w: L * 2 * (up - u0) * w / math.sqrt(max(f(u0 + (up - u0) * (1 - w * w)), 1e-300))
    val, err = quad(g, 0, 1, epsabs=1e-13, epsrel=1e-12, limit=400)
    return 2 * val, L


def swept_1pn_at_peri(L, r0):
    """First attempt (run F-20261121-063527-b4453db): E_1PN = 0 imposed AT PERICENTRE. Wrong
    definition of the parabola: the truncated equation does not conserve E_1PN beyond 1PN
    order, and imposing it where M/r = 0.1 leaves a hyperbola at large r. Kept for the record."""
    from scipy.integrate import solve_ivp
    from scipy.optimize import fsolve
    r_n = L * L / 2
    sol = fsolve(lambda p: list(tm_E_J(p[0], p[1]) - np.array([0.0, L])),
                 [r_n, math.sqrt(2 / r_n)], xtol=1e-14)
    rp, vp = sol
    ev = lambda t, y: np.linalg.norm(y[:3]) - r0
    ev.terminal, ev.direction = True, 1
    s = solve_ivp(tm_1pn, [0, 1e9], [rp, 0, 0, 0, vp, 0], method="DOP853", rtol=1e-12,
                  atol=1e-14, events=ev)
    xe = s.y_events[0][0]
    phi = math.atan2(xe[1], xe[0]) % (2 * math.pi)
    return 2 * phi, rp


def tm_E_J_general(r, vr, vt):
    v2 = vr * vr + vt * vt
    E = 0.5 * v2 - 1 / r + 0.375 * v2 ** 2 + 1.5 * v2 / r + 0.5 / r ** 2
    J = r * vt * (1 + 0.5 * v2 + 3 / r)
    return E, J


def swept_1pn(L, r0):
    """E_1PN = 0 and J = L imposed at r0 on the way in (where 1PN terms are 1e-4), integrated
    through pericentre back to r0; returns the swept angle, the pericentre and E_1PN at the end."""
    from scipy.integrate import solve_ivp
    from scipy.optimize import fsolve
    vt0 = L / r0
    vr0 = -math.sqrt(max(2 / r0 - vt0 ** 2, 0.0))
    vr, vt = fsolve(lambda p: list(np.array(tm_E_J_general(r0, p[0], p[1])) - np.array([0.0, L])),
                    [vr0, vt0], xtol=1e-15)
    ev = lambda t, y: np.linalg.norm(y[:3]) - r0
    ev.terminal, ev.direction = True, 1
    s = solve_ivp(tm_1pn, [0, 1e9], [r0, 0, 0, vr, vt, 0], method="DOP853", rtol=1e-12,
                  atol=1e-13, events=ev, max_step=r0 / 20)
    ang = np.unwrap(np.arctan2(s.y[1], s.y[0]))
    xe = s.y_events[0][0]
    a_end = ang[-1] + ((math.atan2(xe[1], xe[0]) - ang[-1] + math.pi) % (2 * math.pi) - math.pi)
    r = np.linalg.norm(s.y[:3], axis=0)
    rv = xe[:3]
    vv = s.y_events[0][0][3:]
    rn = np.linalg.norm(rv)
    Eend, _ = tm_E_J_general(rn, (rv @ vv) / rn, np.linalg.norm(np.cross(rv, vv)) / rn)
    return a_end, float(r.min()), float(Eend)


def mode_eih(out):
    from scipy.integrate import solve_ivp
    res = {}
    # L3b: Newtonian-circular binary at a = 30 m_b (and 20), nu = 1/4
    for a in (30.0, 20.0):
        m, nu = 1.0, 0.25
        v = math.sqrt(m / a)
        P = 2 * math.pi * math.sqrt(a ** 3 / m)
        s = solve_ivp(rel_1pn, [0, 6 * P], [a, 0, 0, 0, v, 0], args=(m, nu), method="DOP853",
                      rtol=1e-12, atol=1e-12, max_step=P / 400)
        r = np.linalg.norm(s.y[:3], axis=0)
        res[f"binary_a{int(a)}"] = {"rmin": float(r.min()), "rmax": float(r.max()),
                                    "e_r": float((r.max() - r.min()) / (r.max() + r.min())),
                                    "vc2_1pn_over_vN2": 1 - (3 - nu) * m / a}
        if a == 30.0:
            tb, rb = s.t / P, r / a
    # L3c: test-mass parabolas
    r0 = 1e4
    rows = []
    for rp in (8.0, 10.0, 12.0, 20.0, 40.0):
        sg, L = swept_gr(rp, r0)
        p = L * L
        sn = 2 * math.acos(p / r0 - 1)
        se, rp_h, e_end = swept_1pn(L, r0)
        sp, rpp = swept_1pn_at_peri(L, r0)
        rows.append({"rp_areal": rp, "L": L, "swept_gr": sg, "swept_newton": sn, "swept_1pn": se,
                     "rp_1pn_harmonic": rp_h, "E1pn_end": e_end, "err_exc": (se - sn) / (sg - sn) - 1,
                     "first_attempt_E0_at_peri": {"swept": sp, "rp": rpp,
                                                  "err_exc": (sp - sn) / (sg - sn) - 1}})
    res["t4_rows"] = rows
    ref = json.load(open(os.path.join(WT, "tracks/F-hills/eih/results/trust.json")))["rows"]
    refd = {r["rp_areal"]: r for r in ref}
    for r in rows:
        q = refd.get(r["rp_areal"]) or refd.get(int(r["rp_areal"]))
        if q:
            r["eih_err_exc"] = q["err_exc"]
            r["eih_swept_gr"] = q["swept_gr"]
            r["eih_swept_eih"] = q["swept_eih"]
    json.dump(res, open(os.path.join(out, "review3_eih.json"), "w"), indent=1)

    plt, fs = _fig()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    ax[0].plot(tb, rb, color=fs.PAL["red"])
    ax[0].set_xlabel("t / Newtonian period")
    ax[0].set_ylabel("r / a (1PN, Newtonian-circular start)")
    xr = [q["rp_areal"] for q in ref]
    ax[1].semilogx(xr, [q["err_exc"] for q in ref], color=fs.PAL["blue"], label="eih T4 (trust.json)")
    ax[1].semilogx([r["rp_areal"] for r in rows], [r["err_exc"] for r in rows], "o",
                   color=fs.PAL["red"], ms=4, label="lead, own integration")
    ax[1].set_xlabel(r"areal $r_p$ [M]")
    ax[1].set_ylabel("error of the 1PN excess angle")
    ax[1].legend(fontsize=7)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.96, bottom=0.17, wspace=0.3)
    fs.save(fig, os.path.join(out, "fig_review3_eih"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    {"p1": lambda: mode_p1(out, sys.argv[3]), "g0": lambda: mode_g0(out, sys.argv[3]),
     "eih": lambda: mode_eih(out)}[mode]()
