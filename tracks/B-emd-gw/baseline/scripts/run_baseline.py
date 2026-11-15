"""Checks T1-T8 of the baseline package (predictions: ../JOURNAL.md, 2026-11-15T11:44Z
and 11:48Z entries).

    OMP_NUM_THREADS=4 python3 run_baseline.py OUTDIR [T1 T2 ...]

Writes OUTDIR/baseline_results.json and OUTDIR/<test>_*.png. Semi-analytic only: ordinary
differential equations, closed forms and Fourier sums (ellipsoid.py); no simulation code.
"""
import json
import os
import sys
import time

import numpy as np
import sympy as sp
from scipy.integrate import quad, solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
import ellipsoid as el  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

fs.use_style()
B2605 = np.array([0.11122237, 0.06683367, 0.02194397])   # 2605.04487 figure names, l. 2275
B2605_SNAP = np.array([0.1114, 0.0667, 0.0219])           # 2605.04487 snapshot names, l. 2287
B2403 = [np.array([0.2, -0.02, -0.08]), np.array([0.079, 0.045, 0.036]),
         np.array([0.059, 0.0, -0.054])]                  # 2403.15126 lines 719-721
PAPER_X, PAPER_Y = 22.536, 29.097                         # 2605.04487 lines 2277, 2279
MODEL_COL = {"ZA": fs.PAL["blue"], "A": fs.PAL["red"], "B": fs.PAL["green"],
             "C": fs.PAL["orange"]}


def save(fig, out, name):
    p = os.path.join(out, name)
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- T1
def t1(out):
    res = {}
    # (1a) symbolic prefactor
    t, tk, M, Gs, w, al = sp.symbols("t t_k M G omega alpha", positive=True)
    RL = sp.Rational(3, 2)*tk                       # R_L = c/H_k = (3/2) c t_k, c = 1
    c3_sq_sum = (M*RL**2/15)**2*(sp.Rational(80, 27))**2*tk**sp.Rational(-16, 3)*6
    # |window|^2 = t_k^(4/3) |E(i w t_k) - alpha^-1 E(i w t_col)|^2
    mine = Gs*w/(5*sp.pi)*c3_sq_sum*tk**sp.Rational(4, 3)
    paper2605 = sp.Rational(32, 135)/sp.pi*(1/Gs)*w*(Gs*M)**2
    # G M = (3/4) t_k (c = 1): substitute t_k = 4 G M / 3
    ratio_2605 = sp.simplify((mine/paper2605).subs(tk, 4*Gs*M/3))
    # 2403.15126: dE/dln w = (4 pi G/5) w^7 sum|Q~|^2 with Q~ = (1/2pi) int ..., and
    # w^6 sum|Q~|^2 = (1/(54 pi^2)) t_k^(4/3) t_1^(4/3)/t_max^(8/3) M^2 [S/alpha^4] |..|^2
    tmax = (2*al)**sp.Rational(-3, 2)*tk
    p2403 = (4*sp.pi*Gs/5)*w/(54*sp.pi**2)*tk**sp.Rational(4, 3)*tk**sp.Rational(4, 3) \
        / tmax**sp.Rational(8, 3)*M**2/al**4
    ratio_2403 = sp.simplify(p2403/paper2605)
    res["1a_ratio_mine_over_2605"] = str(ratio_2605)
    res["1a_ratio_2403_over_2605"] = str(ratio_2403)
    # (1d) 2403.15126 quadrupole, lines 959-961, against its axes, line 485
    lam = sp.symbols("l1 l2 l3", real=True)
    tm = sp.symbols("t_max", positive=True)
    al_ = lam[0]
    r = [sp.Rational(3, 2)*tk**sp.Rational(1, 3)*t**sp.Rational(2, 3)
         * (1 - (lam[i]/al_)/2*(t/tm)**sp.Rational(2, 3)) for i in range(3)]
    Qax = (M/15)*(3*r[0]**2 - (r[0]**2 + r[1]**2 + r[2]**2))
    s1, s2 = sum(lam), sum(x**2 for x in lam)
    Q2403 = sp.Rational(3, 80)*M*(tk/tm**2)**sp.Rational(2, 3)/al_**2 \
        * ((3*lam[0]**2 - s2)*t**sp.Rational(8, 3) - 4*(3*lam[0] - s1)*t**2*tm**sp.Rational(2, 3))
    d = sp.expand(sp.simplify((Q2403 - Qax).subs(tm, (2*al_)**sp.Rational(-3, 2)*tk)))
    c83 = sp.simplify(sp.expand(d).coeff(t**sp.Rational(8, 3)))
    c2 = sp.simplify(sp.expand(d).coeff(t**2))
    lin_ax = sp.simplify(sp.expand(Qax.subs(tm, (2*al_)**sp.Rational(-3, 2)*tk)).coeff(t**2))
    lin_2403 = sp.simplify(sp.expand(Q2403.subs(tm, (2*al_)**sp.Rational(-3, 2)*tk)).coeff(t**2))
    res["1d_t83_difference"] = str(c83)
    res["1d_t2_ratio_2403_over_axes"] = str(sp.simplify(lin_2403/lin_ax))

    # (1b) direct Fourier sum against the closed form; (1c) Parseval
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.2), sharex="col")
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.10, top=0.93, hspace=0.0, wspace=0.25)
    for col, lamv in enumerate([B2403[0], B2605]):
        tc = el.t_col_za(lamv[0])
        dt = 2e-4
        tt = np.arange(el.TK, tc + 0.5*dt, dt)
        tt = np.linspace(el.TK, tc, len(tt))
        Q3 = el.za_Q3(tt, lamv)
        om = np.logspace(-3, 2, 120)/el.TK
        direct = el.spectrum_from_Q3(tt, Q3, om)
        closed = el.za_spectrum(om, lamv, el.TK, tc)
        p2605 = el.za_spectrum_2605(om, lamv)
        nyq = np.pi/(tt[1] - tt[0])
        m = om < 0.1*nyq
        rel_direct = np.abs(direct/closed - 1)
        rel_2605 = np.abs(p2605/closed - 1)
        # Parseval on a wide grid (tails: dE/dln w ~ w in the IR, ~ 1/w in the UV)
        omp = np.logspace(-6, 5, 2201)/el.TK
        sp_p = el.za_spectrum(omp, lamv, el.TK, tc)
        lnw = np.log(omp)
        e_int = np.trapezoid(sp_p, lnw) + sp_p[0] + sp_p[-1]
        e_cl = el.za_energy(el.TK, tc, lamv)
        tag = "2403" if col == 0 else "2605"
        res[f"1b_{tag}"] = {"lam": lamv.tolist(), "t_col": tc, "dt": tt[1] - tt[0],
                            "omega_max_over_nyquist": float(om.max()/nyq),
                            "max_rel_direct_vs_closed": float(rel_direct[m].max()),
                            "max_rel_2605_vs_closed": float(rel_2605.max())}
        res[f"1c_{tag}"] = {"E_parseval_over_Mc2": float(e_int/el.MASS),
                            "E_closed_over_Mc2": float(e_cl/el.MASS),
                            "rel": float(abs(e_int/e_cl - 1)),
                            "E_closed_formula": "(8/15) S (alpha^-1/2 - 1)",
                            "E_check": float((8/15)*el.shape_S(lamv)*(lamv[0]**-0.5 - 1))}
        ax = axs[0, col]
        ax.loglog(om*el.TK, closed/el.MASS, color=fs.PAL["blue"], label="closed form (this note)")
        ax.loglog(om*el.TK, p2605/el.MASS, **fs.GUIDE, label="2605.04487 eq.")
        ax.loglog(om[::3]*el.TK, direct[::3]/el.MASS, "o", ms=3, color=fs.PAL["red"],
                  label="Fourier sum of $\\dddot Q_{ij}(t)$")
        ax.set_ylabel(r"$dE/d\ln\omega\ /\ Mc^2$")
        ax.set_title(r"$(\alpha,\beta,\gamma)=(%.4g, %.4g, %.4g)$" % tuple(lamv), fontsize=10)
        ax.axvline(1/tc, **fs.MASK_LINE)
        ax.legend(loc="lower center", fontsize=8)
        ax = axs[1, col]
        ax.loglog(om*el.TK, np.maximum(rel_direct, 1e-17), color=fs.PAL["red"],
                  label="Fourier sum / closed $-1$")
        ax.loglog(om*el.TK, np.maximum(rel_2605, 1e-17), color="k", ls="--",
                  label="2605 eq. / closed $-1$")
        ax.set_ylim(1e-17, 1e-1)
        ax.set_xlabel(r"$\omega t_k$", labelpad=-2)
        ax.set_ylabel("relative difference")
        ax.legend(loc="upper left", fontsize=8)
    res["figure"] = save(fig, out, "t1_za_spectrum.png")
    return res


# --------------------------------------------------------------------------- T2
def peak_of(fun, lo, hi, n=500):
    om = np.logspace(np.log10(lo), np.log10(hi), n)
    y = fun(om)
    j = int(np.argmax(y))
    om2 = np.logspace(np.log10(om[max(j-2, 0)]), np.log10(om[min(j+2, n-1)]), 201)
    y2 = fun(om2)
    k = int(np.argmax(y2))
    return om2[k], y2[k]


def t2(out):
    shape = B2605/np.sum(B2605)
    dls = np.array([1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 0.1, 0.2, 0.4, 0.8])
    E, wp, Ap = [], [], []
    for dl in dls:
        lam = shape*dl
        tc = el.t_col_za(lam[0])
        E.append(el.za_energy(el.TK, tc, lam)/el.MASS)
        w, A = peak_of(lambda om: el.za_spectrum(om, lam, el.TK, tc), 1e-2/tc, 1e2/tc, 160)
        wp.append(w*el.TK)
        Ap.append(A/el.MASS)
    E, wp, Ap = map(np.array, (E, wp, Ap))
    ld = np.log(dls)
    sl = lambda y: np.diff(np.log(y))/np.diff(ld)  # noqa: E731
    mid = np.sqrt(dls[1:]*dls[:-1])
    res = {"delta_L": dls.tolist(), "E_tot_over_Mc2": E.tolist(),
           "omega_peak_tk": wp.tolist(), "peak_dEdlnw_over_Mc2": Ap.tolist(),
           "delta_mid": mid.tolist(), "slope_E": sl(E).tolist(), "slope_wpeak": sl(wp).tolist(),
           "slope_peak": sl(Ap).tolist()}
    m = mid <= 1e-2
    res["max_dev_small_delta"] = {"E": float(np.max(np.abs(sl(E)[m] - 3.5))),
                                  "wpeak": float(np.max(np.abs(sl(wp)[m] - 1.5))),
                                  "peak": float(np.max(np.abs(sl(Ap)[m] - 3.5)))}
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.95, wspace=0.38)
    ax = axs[0]
    ax.loglog(dls, E, "o-", color=fs.PAL["blue"], label=r"$E_{\rm tot}$")
    ax.loglog(dls, Ap, "s-", color=fs.PAL["red"], label=r"peak of $dE/d\ln\omega$")
    ax.loglog(dls, E[0]*(dls/dls[0])**3.5, **fs.GUIDE, label=r"$\propto\delta_L^{7/2}$")
    ax.loglog(dls, Ap[0]*(dls/dls[0])**3.5, **fs.GUIDE)
    ax.set_xlabel(r"$\delta_L=\alpha+\beta+\gamma$", labelpad=-2)
    ax.set_ylabel(r"energy / $Mc^2$")
    ax.legend(loc="upper left", fontsize=8)
    ax = axs[1]
    ax.loglog(dls, wp, "o-", color=fs.PAL["blue"], label=r"$\omega_{\rm peak}t_k$")
    ax.loglog(dls, wp[0]*(dls/dls[0])**1.5, **fs.GUIDE, label=r"$\propto\delta_L^{3/2}$")
    ax.set_xlabel(r"$\delta_L$", labelpad=-2)
    ax.set_ylabel(r"$\omega_{\rm peak}\,t_k$")
    ax.legend(loc="upper left", fontsize=8)
    ax = axs[2]
    ax.semilogx(mid, sl(E), "o-", color=fs.PAL["blue"], label=r"$E_{\rm tot}$")
    ax.semilogx(mid, sl(Ap), "s-", color=fs.PAL["red"], label="peak amplitude")
    ax.semilogx(mid, sl(wp) + 2.0, "^-", color=fs.PAL["green"], label=r"$\omega_{\rm peak}$ (+2)")
    ax.axhline(3.5, **fs.GUIDE)
    ax.axvspan(mid.min(), 1e-2, color="grey", alpha=0.1)
    ax.set_xlabel(r"$\delta_L$", labelpad=-2)
    ax.set_ylabel("local slope")
    ax.set_ylim(2.6, 3.8)
    ax.legend(loc="lower left", fontsize=8)
    res["figure"] = save(fig, out, "t2_za_scaling.png")
    return res


# --------------------------------------------------------------------------- T3
def t3(out):
    rng = np.random.default_rng(1)
    errs, sums = [], []
    for _ in range(200):
        R = np.exp(rng.uniform(np.log(1e-3), np.log(1e1), 3))
        A = el.shape_coeffs(R)
        sums.append(abs(A.sum() - 2.0))
        Aq = []
        for i in range(3):
            # u = exp(v): the integrand is smooth in v; breakpoints at the three scales
            def g(v, i=i):
                u = np.exp(v)
                return u/((R[i]**2 + u)*np.sqrt(np.prod(R**2 + u)))
            lo = np.log(np.min(R)**2) - 60.0
            hi = np.log(np.max(R)**2) + 60.0
            pts = sorted(np.log(R**2))
            Aq.append(np.prod(R)*quad(g, lo, hi, points=pts, limit=800, epsabs=0,
                                      epsrel=1e-13)[0])
        errs.append(np.max(np.abs(np.array(Aq) - A)/np.abs(A)))
    res = {"max_abs_sumA_minus_2": float(max(sums)), "max_rel_RD_vs_quadrature": float(max(errs))}
    # sphere: models A and C against the top hat from rest
    lamv = np.array([0.1, 0.1, 0.1])
    out_sph = {}
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.95, wspace=0.3)
    for model in ("A", "C", "B"):
        t0, R0, V0 = el.initial_state(lamv)
        r0 = R0[0]
        stop = 1e-4*r0

        def ev(t, y):
            return y[0] - stop
        ev.terminal = True
        sol = solve_ivp(lambda t, y: np.concatenate([y[3:6], el.accel(t, y[0:3], model)]),
                        (t0, 3*t0), np.concatenate([R0, V0]), method="DOP853",
                        rtol=1e-13, atol=1e-16, events=ev, dense_output=True)
        te = sol.t_events[0][0]
        tff = np.sqrt(r0**3/(2*el.G*el.MASS))
        eta = np.arccos(np.sqrt(stop/r0))
        t_cyc = t0 + tff*(eta + np.sin(eta)*np.cos(eta))
        t_c = t0 + tff*np.pi/2
        tt = np.linspace(t0, te, 400)
        Rt = sol.sol(tt)[0:3].T
        Q = el.quad_derivs(Rt, np.zeros_like(Rt), np.zeros_like(Rt), np.zeros_like(Rt))[0]
        etas = np.linspace(0, eta, 400)
        out_sph[model] = {"t_turn": t0, "t_event_R_1e-4": te, "t_cycloid_R_1e-4": t_cyc,
                          "rel_event_vs_cycloid": abs(te - t_cyc)/t_cyc,
                          "t_collapse_cycloid_over_t_turn": t_c/t0,
                          "t_event_over_t_turn": te/t0,
                          "max_abs_Q_over_M_RL2": float(np.max(np.abs(Q))/(el.MASS*el.RL**2))}
        axs[0].plot(tt/t0, Rt[:, 0]/r0, color=MODEL_COL[model], label=f"model {model}")
    etas = np.linspace(0, np.pi/2, 400)
    t0 = el.t_turn(0.1)
    r0 = el.initial_state(lamv)[1][0]
    tff = np.sqrt(r0**3/(2*el.G*el.MASS))
    axs[0].plot((t0 + tff*(etas + np.sin(etas)*np.cos(etas)))/t0, np.cos(etas)**2, **fs.GUIDE,
                label="top hat from rest")
    axs[0].axvline(1 + 3*np.pi/(8*np.sqrt(2)), **fs.MASK_LINE)
    axs[0].set_xlabel(r"$t/t_{\rm turn}$", labelpad=-2)
    axs[0].set_ylabel(r"$R/R(t_{\rm turn})$")
    axs[0].legend(loc="lower left", fontsize=8)
    axs[1].semilogy(np.arange(200), np.maximum(errs, 1e-17), ".", color=fs.PAL["red"],
                    label=r"$|A_i^{R_D}-A_i^{\rm quad}|/A_i$")
    axs[1].semilogy(np.arange(200), np.maximum(sums, 1e-17), ".", color=fs.PAL["blue"],
                    label=r"$|\sum A_i-2|$")
    axs[1].set_xlabel("random axes (index)", labelpad=-2)
    axs[1].set_ylabel("error")
    axs[1].set_ylim(1e-17, 1e-8)
    axs[1].legend(loc="upper left", fontsize=8)
    res["sphere"] = out_sph
    res["sphere_prediction_t_c_over_t_turn"] = 1 + 3*np.pi/(8*np.sqrt(2))
    res["figure"] = save(fig, out, "t3_sphere_and_shape.png")
    return res


# --------------------------------------------------------------------------- T4, T5
def run_models(lamv, t_end_fac=5.0, models=("A", "B", "C")):
    t0 = el.t_turn(lamv[0])
    return {m: el.integrate(lamv, m, t_end_fac*t0) for m in models}


def first_cross(run, axis=None):
    for tc, k in run["crossings"]:
        if axis is None or k == axis:
            return tc
    return None


def t4_t5(out):
    res = {}
    runs = run_models(B2605)
    t0 = el.t_turn(B2605[0])
    # ---- crossings (T5)
    cr = {}
    for m, r in runs.items():
        cr[m] = {"crossings": [(tc, ["x", "y", "z"][k]) for tc, k in r["crossings"]],
                 "first_x": first_cross(r, 0), "first_y": first_cross(r, 1),
                 "first_z": first_cross(r, 2)}
        cr[m]["rel_x_vs_paper"] = (cr[m]["first_x"]/PAPER_X - 1) if cr[m]["first_x"] else None
        cr[m]["rel_y_vs_paper"] = (cr[m]["first_y"]/PAPER_Y - 1) if cr[m]["first_y"] else None
    cr["ZA"] = {"first_x": el.t_col_za(B2605[0]), "first_y": el.t_col_za(B2605[1]),
                "first_z": el.t_col_za(B2605[2])}
    res["T5_crossings_2605_benchmark"] = cr
    res["t_turn"] = t0
    snap = run_models(B2605_SNAP, 4.0, ("A", "B"))
    res["T5_crossings_snapshot_values"] = {
        m: {"t_turn": el.t_turn(B2605_SNAP[0]), "first_x": first_cross(r, 0),
            "first_y": first_cross(r, 1)} for m, r in snap.items()}
    c2403 = {}
    for lamv in B2403:
        r = el.integrate(lamv, "C", 4.0*el.t_turn(lamv[0]))
        tx = first_cross(r, 0)
        ta = el.t_turn(lamv[0])
        c2403[str(lamv.tolist())] = {"t_turn": ta, "t_x_C": tx, "dt_col_over_tmax_C": (tx - ta)/ta,
                                     "dt_col_over_tmax_ZA": 2*np.sqrt(2) - 1,
                                     "dt_col_over_tmax_2403_calibration": 1.8}
    res["T5_2403_model_C"] = c2403

    # ---- quadrupole, stencil, energies (T4)
    tx = {m: first_cross(r, 0) for m, r in runs.items()}
    samp = {}
    for m in ("A", "B"):
        tt = np.linspace(t0, 5*t0, 20001)
        samp[m] = el.sample(runs[m], tt)
    # stencil on model A
    sA = samp["A"]
    h = 2e-3*t0
    tc_all = [tc for tc, _ in runs["A"]["crossings"]]
    tt = sA["t"][(sA["t"] > t0 + 3*h) & (sA["t"] < 5*t0 - 3*h)][::10]
    tt = np.array([x for x in tt if min(abs(x - c) for c in tc_all) > 3*h])
    st = {}
    for k in (-2, -1, 1, 2):
        st[k] = el.sample(runs["A"], tt + k*h)["Q"][0]
    q3_fd = (st[2] - 2*st[1] + 2*st[-1] - st[-2])/(2*h**3)
    q3_an = el.sample(runs["A"], tt)["Q"][3]
    scale = np.max(np.abs(sA["Q"][3]))
    res["T4_stencil"] = {"h_over_t_turn": 2e-3, "n_points": len(tt),
                         "max_abs_diff_over_max_Q3": float(np.max(np.abs(q3_fd - q3_an))/scale)}
    # where the difference sits: bands of distance to the nearest crossing, two steps
    bands = {}
    for hf in (2e-3, 5e-4):
        hh = hf*t0
        tb = np.linspace(t0 + 3*hh, 5*t0 - 3*hh, 3000)
        dist = np.array([min(abs(x - c) for c in tc_all) for x in tb])
        sb = {k: el.sample(runs["A"], tb + k*hh)["Q"][0] for k in (-2, -1, 1, 2)}
        fd = (sb[2] - 2*sb[1] + 2*sb[-1] - sb[-2])/(2*hh**3)
        err = np.max(np.abs(fd - el.sample(runs["A"], tb)["Q"][3]), axis=1)/scale
        row = {}
        for name, lo, hi in (("3h_to_10h", 3*hh, 10*hh), ("10h_to_0.2tturn", 10*hh, 0.2*t0),
                             ("beyond_0.2tturn", 0.2*t0, np.inf)):
            m = (dist > lo) & (dist <= hi)
            row[name] = float(err[m].max()) if np.any(m) else None
        row["before_first_crossing"] = float(err[tb < tc_all[0] - 3*hh].max())
        bands[str(hf)] = row
    res["T4_stencil_bands"] = bands
    # energies
    eza = el.za_energy(t0, el.t_col_za(B2605[0]), B2605)
    en = {"ZA_t_turn_to_t_col": eza/el.MASS,
          "ZA_t_k_to_t_col": el.za_energy(el.TK, el.t_col_za(B2605[0]), B2605)/el.MASS}
    for m, r in runs.items():
        seg0 = r["segments"][0]
        e_x = seg0.y[6, -1]
        en[f"{m}_t_turn_to_first_x"] = e_x/el.MASS
        en[f"{m}_ratio_to_ZA_turn_col"] = e_x/eza
        ty = first_cross(r, 1)
        if ty is not None:
            ey = [s.y[6, -1] for s in r["segments"] if s.t[-1] <= ty*(1 + 1e-12)][-1]
            en[f"{m}_t_turn_to_first_y"] = ey/el.MASS
    res["T4_energies_over_Mc2"] = en
    res["T4_first_x"] = tx

    # ---- figure: axes (T5)
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH*1.6, 7.0), sharex=True)
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.07, top=0.98, hspace=0.0)
    tg = np.linspace(t0, 5*t0, 4001)
    za = el.za_axes(tg, B2605)
    a = el.a_of_t(tg)
    ls = ["-", "--", ":"]
    ax = axs[0]
    for i in range(3):
        ax.plot(tg, np.abs(za[:, i])/a/el.RL, color=MODEL_COL["ZA"], ls=ls[i],
                label="ZA" if i == 0 else None)
    for m in ("A", "B", "C"):
        s = el.sample(runs[m], tg)
        for i in range(3):
            ax.plot(tg, np.abs(s["R"][:, i])/a/el.RL, color=MODEL_COL[m], ls=ls[i],
                    label=f"model {m}" if i == 0 else None)
    for x in (PAPER_X, PAPER_Y):
        ax.axvline(x, **fs.MASK_LINE)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(r"comoving semi-axis $|R_i|/(aR_L)$")
    ax.legend(loc="lower left", fontsize=8, ncol=2)
    ax.text(PAPER_X, 1.0, " 22.536", fontsize=8, va="top")
    ax.text(PAPER_Y, 1.0, " 29.097", fontsize=8, va="top")
    ax = axs[1]
    for i in range(3):
        qza = (el.MASS/15)*(3*za[:, i]**2 - np.sum(za**2, axis=1))
        ax.plot(tg, qza/(el.MASS*el.RL**2), color=MODEL_COL["ZA"], ls=ls[i])
        for m in ("A", "B"):
            ax.plot(samp[m]["t"], samp[m]["Q"][0][:, i]/(el.MASS*el.RL**2), color=MODEL_COL[m],
                    ls=ls[i])
    ax.set_ylabel(r"$Q_{ii}/(MR_L^2)$")
    ax = axs[2]
    tz = np.linspace(t0, el.t_col_za(B2605[0]), 2000)
    ax.semilogy(tz, el.power(el.za_Q3(tz, B2605)), color=MODEL_COL["ZA"], label="ZA")
    for m in ("A", "B"):
        ax.semilogy(samp[m]["t"], samp[m]["P"], color=MODEL_COL[m], label=f"model {m}")
    ax.semilogy(tt, el.power(q3_fd), ".", ms=2, color="k", label="model A, 5-point stencil")
    ax.set_ylabel(r"$P_{\rm GW}=\frac{G}{5c^5}\dddot Q_{ij}\dddot Q_{ij}$")
    ax.set_xlabel(r"$t/t_k$", labelpad=-2)
    ax.legend(loc="lower right", fontsize=8)
    res["figure_T4_T5"] = save(fig, out, "t4_t5_axes_quadrupole_power.png")
    return res, runs, samp


# --------------------------------------------------------------------------- T6
def t6(out):
    ratios = B2605/B2605[0]
    alphas = [0.01, 0.03, 0.1, 0.3]
    res = {}
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.17, top=0.95, wspace=0.3)
    for m in ("A", "B", "C"):
        F, tau = [], []
        for al in alphas:
            lam = ratios*al
            t0 = el.t_turn(al)
            r = el.integrate(lam, m, 4*t0, rtol=1e-13, atol=1e-30)
            seg0 = r["segments"][0]
            F.append(seg0.y[6, -1]/el.MASS/(2*al)**3.5)
            tau.append(first_cross(r, 0)/t0)
        F, tau = np.array(F), np.array(tau)
        res[m] = {"alpha": alphas, "E_over_Mc2_over_(2alpha)^3.5": F.tolist(),
                  "t_x_over_t_turn": tau.tolist(),
                  "rel_spread_F": float(np.ptp(F)/np.mean(F)),
                  "rel_spread_tau": float(np.ptp(tau)/np.mean(tau))}
        axs[0].semilogx(alphas, F/np.mean(F) - 1, "o-", color=MODEL_COL[m], label=f"model {m}")
        axs[1].semilogx(alphas, tau, "o-", color=MODEL_COL[m], label=f"model {m}")
    za_F = [el.za_energy(el.TK, el.t_col_za(al), ratios*al)/el.MASS/(2*al)**3.5 for al in alphas]
    res["ZA_t_k_to_t_col"] = {"E_over_Mc2_over_(2alpha)^3.5": za_F}
    axs[0].set_xlabel(r"$\alpha$ (fixed $\beta/\alpha$, $\gamma/\alpha$)", labelpad=-2)
    axs[0].set_ylabel(r"$F/\langle F\rangle-1$, $F=E/[Mc^2(2\alpha)^{7/2}]$")
    axs[0].set_ylim(-1e-6, 1e-6)
    axs[0].legend(loc="upper left", fontsize=8)
    axs[1].set_xlabel(r"$\alpha$", labelpad=-2)
    axs[1].set_ylabel(r"$t_x/t_{\rm turn}$")
    axs[1].legend(loc="center right", fontsize=8)
    res["figure"] = save(fig, out, "t6_self_similarity.png")
    return res


# --------------------------------------------------------------------------- T7
SI = {"G": 6.67430e-11, "c": 2.99792458e8, "hbar": 1.054571817e-34, "kB": 1.380649e-23,
      "GeV": 1.602176634e-10, "Msun": 1.98841e30, "T0": 2.7255, "gs0": 3.931,
      "H100": 1e5/3.0856775814913673e22}


def today(M_sun, T_GeV, theta, x_peak, eps_peak, gstar=106.75):
    """f_0 [Hz] and h^2 Omega_GW at the peak, conversion of 2605.04487 lines 1963-2063
    with constant g_* = g_*s; source: dE/dln omega_e = eps_peak M c^2 at
    omega_e = x_peak / t_k, emitted at t_e = theta t_k."""
    G, c, hb, kB = SI["G"], SI["c"], SI["hbar"], SI["kB"]
    M = M_sun*SI["Msun"]
    tk = 4*G*M/(3*c**3)
    T = T_GeV*SI["GeV"]
    rho_rh = np.pi**2/30*gstar*T**4/(hb**3*c**3)
    H_rh = np.sqrt(8*np.pi*G*rho_rh/(3*c**2))
    t_rh = 2/(3*H_rh)
    zrh1 = (T/kB/SI["T0"])*(gstar/SI["gs0"])**(1/3)
    te = theta*tk
    ze1 = zrh1*(t_rh/te)**(2/3)
    f0 = x_peak/tk/(2*np.pi)/ze1
    rho_M = rho_rh/c**2
    Vk = M*zrh1**3/rho_M
    h2_over_rhoc = 8*np.pi*G/(3*SI["H100"]**2*c**2)
    om = h2_over_rhoc/(Vk*ze1)*eps_peak*M*c**2
    return f0, om, tk/t_rh


def t7(out):
    res = {}
    Ms = np.logspace(-20, 2, 12)
    Ts = np.logspace(-2, 9, 12)
    f_M = np.array([today(m, 1.0, 50, 0.1, 1e-5)[0] for m in Ms])
    o_M = np.array([today(m, 1.0, 50, 0.1, 1e-5)[1] for m in Ms])
    f_T = np.array([today(1.0, T, 50, 0.1, 1e-5)[0] for T in Ts])
    o_T = np.array([today(1.0, T, 50, 0.1, 1e-5)[1] for T in Ts])
    s = lambda y, x: np.polyfit(np.log(x), np.log(y), 1)[0]  # noqa: E731
    lin = lambda y, x: float(np.max(np.abs(np.diff(np.log(y))/np.diff(np.log(x))  # noqa: E731
                                        - s(y, x))))
    res["slopes"] = {"f0_M": s(f_M, Ms), "f0_T": s(f_T, Ts), "Omega_M": s(o_M, Ms),
                     "Omega_T": s(o_T, Ts),
                     "max_local_dev": max(lin(f_M, Ms), lin(f_T, Ts), lin(o_M, Ms), lin(o_T, Ts))}
    C = today(1.0, 1.0, 1.0, 0.1, 1e-5)[2]
    res["tk_over_trh_coefficient"] = C
    res["tk_over_trh_coefficient_paper"] = 21.03
    res["rel_coeff"] = C/21.03 - 1
    res["Trh_bound_coefficient"] = 1/np.sqrt(C)
    # T7b: numbers of 2403.15126 (sigma = 0.1)
    x_p = 0.1*(2.0/3.0)            # omega_e = H_k/10, H_k t_k = 2/3
    eps = 2e-5/0.5                 # <dE/dln w> = 2e-5 in G = c = H_k = 1 units, M = 1/2
    thetas = np.array([28.0, 42.0, 84.0, 126.0])
    fo = np.array([today(1.0, 1.0, th, x_p, eps)[0] for th in thetas])
    oo = np.array([today(1.0, 1.0, th, x_p, eps)[1] for th in thetas])
    res["T7b"] = {"theta": thetas.tolist(), "f0_Hz": fo.tolist(), "f0_over_4e-9": (fo/4e-9).tolist(),
                  "h2Omega": oo.tolist(), "Omega_over_3.16e-10": (oo/(1e-6*0.1**3.5)).tolist(),
                  "note": "2403.15126 writes Omega (not h^2 Omega); h = 0.67 would change the ratio by 1/h^2 = 2.2"}
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.95, wspace=0.3)
    axs[0].loglog(Ms, f_M/f_M[0], "o", color=fs.PAL["red"], label=r"$f_{0}$, $T_{\rm rh}$ = 1 GeV")
    axs[0].loglog(Ms, (Ms/Ms[0])**(-1/3), **fs.GUIDE)
    axs[0].loglog(Ms, o_M/o_M[0], "s", color=fs.PAL["blue"], label=r"$h^2\Omega_{\rm GW}$")
    axs[0].loglog(Ms, (Ms/Ms[0])**(2/3), **fs.GUIDE, label=r"$M^{-1/3}$, $M^{2/3}$")
    axs[0].set_xlabel(r"$M_k/M_\odot$", labelpad=-2)
    axs[0].set_ylabel("relative to the first point")
    axs[0].legend(loc="upper left", fontsize=8)
    axs[1].loglog(Ts, f_T/f_T[0], "o", color=fs.PAL["red"], label=r"$f_0$, $M_k=M_\odot$")
    axs[1].loglog(Ts, (Ts/Ts[0])**(1/3), **fs.GUIDE)
    axs[1].loglog(Ts, o_T/o_T[0], "s", color=fs.PAL["blue"], label=r"$h^2\Omega_{\rm GW}$")
    axs[1].loglog(Ts, (Ts/Ts[0])**(4/3), **fs.GUIDE, label=r"$T^{1/3}$, $T^{4/3}$")
    axs[1].set_xlabel(r"$T_{\rm rh}$ / GeV", labelpad=-2)
    axs[1].legend(loc="upper left", fontsize=8)
    res["figure"] = save(fig, out, "t7_redshift_scalings.png")
    return res


# --------------------------------------------------------------------------- T8
def t8(out, runs=None):
    res = {}
    ratios = B2605/B2605[0]
    alphas = [0.03, 0.06, 0.11122237, 0.2, 0.3]
    Lbox = (4*np.pi/3)**(1/3)*el.RL
    rows = {}
    spectra = {}
    for m in ("A", "B"):
        lam_c, lam_typo, tes, wps = [], [], [], []
        for al in alphas:
            lam = ratios*al
            t0 = el.t_turn(al)
            r = el.integrate(lam, m, 4*t0)
            tx = first_cross(r, 0)
            tt = np.linspace(t0, tx, 6001)
            s = el.sample(r, tt)
            P = s["P"]
            te = np.trapezoid(tt*P, tt)/np.trapezoid(P, tt)
            om = np.logspace(-2, 2.5, 300)/t0
            spec = el.spectrum_from_Q3(tt, s["Q"][3], om)
            j = int(np.argmax(spec))
            wpk = om[j]
            ae = el.a_of_t(te)
            lam_c.append(2*np.pi*el.C/(ae*wpk)/el.RL)
            lam_typo.append(2*np.pi*el.C*ae/wpk/el.RL)
            tes.append(te/t0)
            wps.append(wpk*t0)
            if abs(al - B2605[0]) < 1e-12:
                spectra[m] = (om, spec, t0, tx, te)
        rows[m] = {"alpha": alphas, "lambda_com_over_RL": lam_c,
                   "lambda_typo_formula_over_RL": lam_typo, "t_e_over_t_turn": tes,
                   "omega_peak_t_turn": wps,
                   "slope_lambda_com": float(np.polyfit(np.log(alphas), np.log(lam_c), 1)[0])}
    res["rows"] = rows
    res["box_side_one_patch_per_Vk_over_RL"] = Lbox
    al = B2605[0]
    res["benchmark"] = {m: {"lambda_com_over_RL": rows[m]["lambda_com_over_RL"][2],
                            "ratio_to_box": rows[m]["lambda_com_over_RL"][2]*el.RL/Lbox}
                        for m in rows}
    # ZA spectrum on [t_turn, t_col] for the same benchmark, and box fundamental
    t0 = el.t_turn(al)
    tc = el.t_col_za(al)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.95, wspace=0.3)
    ax = axs[0]
    om = spectra["A"][0]
    ax.loglog(om*el.TK, el.za_spectrum(om, B2605, t0, tc)/el.MASS, color=MODEL_COL["ZA"],
              label=r"ZA, $[t_{\rm turn},t_{\rm col}]$")
    for m in ("A", "B"):
        o, sp_, _, tx, te = spectra[m]
        ax.loglog(o*el.TK, sp_/el.MASS, color=MODEL_COL[m],
                  label=r"model %s, $[t_{\rm turn},t_x]$" % m)
        # box fundamental (comoving side Lbox) as a physical angular frequency at t_e
        ax.axvline(2*np.pi*el.C/Lbox/el.a_of_t(te)*el.TK, color=MODEL_COL[m], lw=1.0, ls=":")
    ax.set_xlabel(r"$\omega t_k$", labelpad=-2)
    ax.set_ylabel(r"$dE/d\ln\omega\ /\ Mc^2$")
    ax.set_ylim(1e-12, None)
    ax.legend(loc="lower left", fontsize=8)
    ax = axs[1]
    for m in ("A", "B"):
        ax.loglog(alphas, rows[m]["lambda_com_over_RL"], "o-", color=MODEL_COL[m],
                  label=f"model {m}")
    a_ = np.array(alphas)
    ax.loglog(a_, rows["A"]["lambda_com_over_RL"][0]*(a_/a_[0])**-0.5, **fs.GUIDE,
              label=r"$\propto\alpha^{-1/2}$")
    ax.axhline(Lbox/el.RL, **fs.REF_LINE)
    ax.text(0.031, Lbox/el.RL*1.05, r"box side $V_k^{1/3}$", fontsize=8)
    ax.set_xlabel(r"$\alpha$ (fixed $\beta/\alpha$, $\gamma/\alpha$)", labelpad=-2)
    ax.set_ylabel(r"comoving $\lambda_{\rm GW}$ at the peak $/R_L$")
    ax.legend(loc="upper right", fontsize=8)
    res["figure"] = save(fig, out, "t8_box_and_spectra.png")
    return res


def main():
    out = sys.argv[1]
    which = sys.argv[2:] or ["T1", "T2", "T3", "T45", "T6", "T7", "T8"]
    os.makedirs(out, exist_ok=True)
    res = {}
    t_start = time.time()
    for w in which:
        t_a = time.time()
        if w == "T1":
            res["T1"] = t1(out)
        elif w == "T2":
            res["T2"] = t2(out)
        elif w == "T3":
            res["T3"] = t3(out)
        elif w == "T45":
            res["T45"] = t4_t5(out)[0]
        elif w == "T6":
            res["T6"] = t6(out)
        elif w == "T7":
            res["T7"] = t7(out)
        elif w == "T8":
            res["T8"] = t8(out)
        res.setdefault("wall_s", {})[w] = time.time() - t_a
        print(w, "done", round(time.time() - t_a, 1), "s", flush=True)
    res["wall_s"]["total"] = time.time() - t_start
    with open(os.path.join(out, "baseline_results.json"), "w") as f:
        json.dump(res, f, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


if __name__ == "__main__":
    main()
