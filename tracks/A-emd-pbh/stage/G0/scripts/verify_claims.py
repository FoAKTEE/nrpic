#!/usr/bin/env python3
"""Independent re-derivation of the claims C1-C6 of Track A's G0/G1 material (verifier, wave 2).

Written by the verifier from the scoping text and the source papers, not from the track's
code: every number below is recomputed here by a route of its own. Only the part V5b calls
the track's own test function (expball.mesh.residuals) on purpose, to rerun "the test said to
support" the G1 claim; V5c builds the ball data from scratch and checks them with its own
finite differences.

    python3 verify_claims.py --out <dir> [--parts V1,V2,V3,V4,V5,V6] [--Nmax 128]

Writes <dir>/verify.json and figures <dir>/fig_V*.{pdf,png}; V3/V4 also render two figures of
the arXiv:2609.14218 source (read-only, raw store) to PNG in <dir>/src_render/ for reading by
eye (never committed). Units G = c = 1.
"""
import argparse
import json
import math
import os
import subprocess
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "4"
sys.dont_write_bytecode = True        # never write into the track's package directories

import numpy as np
from scipy import integrate, optimize, special
from scipy.interpolate import CubicSpline

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402

E_EULER = math.e
RAW = "/data/haiyangw/nrpic/kb-data/raw/arxiv"
SRC_2609 = os.path.join(RAW, "2609.14218", "v1", "src")


def jdump(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(type(o))


# ============================================================================ top hat, own
def cycloid_age(R, m, E):
    """Proper time since the bang of a dust shell (R, m, E), E < 0 branch before turnaround
    (own implementation: parametric cycloid, eta in (0, pi))."""
    A = m / (-2.0 * E)
    T0 = m / (-2.0 * E) ** 1.5
    eta = math.acos(1.0 - R / A)
    return T0 * (eta - math.sin(eta)), A, T0


def E_for_age(R, m, age):
    """Bound energy E < 0 such that the shell (R, m) has the given age on the expanding branch
    (bisection in E; the marginally bound age (2/3) sqrt(R^3/(2m)) is the upper end)."""
    t_mb = (2.0 / 3.0) * math.sqrt(R ** 3 / (2.0 * m))
    if age <= t_mb:
        raise ValueError("age too small for a bound shell")
    Emin = -m / (2.0 * R) * (1 - 1e-15)        # R = R_max: shell exactly at turnaround

    def f(E):
        return cycloid_age(R, m, E)[0] - age
    return optimize.brentq(f, Emin, -1e-30, xtol=1e-300, rtol=1e-15, maxiter=500)


def tophat_shell(Delta_i, HR_i, H=1.0):
    """Shell with mean contrast Delta_i on a slice with Hubble rate H, simultaneous bang
    (age 2/(3H)); returns R_max, 2m/R_max, t_ta, t_c, t_AH (times since the bang)."""
    R = HR_i / H
    m = 0.5 * H ** 2 * R ** 3 * (1 + Delta_i)
    E = E_for_age(R, m, 2.0 / (3.0 * H))
    A = m / (-2 * E)
    T0 = m / (-2 * E) ** 1.5
    eta_ah = 2 * math.pi - math.acos(1 + 4 * E)
    return dict(R=R, m=m, E=E, R_max=2 * A, C_ta=2 * m / (2 * A), t_ta=math.pi * T0,
                t_c=2 * math.pi * T0, t_AH=T0 * (eta_ah - math.sin(eta_ah)), t_i=2.0 / (3.0 * H))


# ============================================================================ V2
def part_V2(out, figdir):
    import sympy as sp
    r, k, mu, K = sp.symbols("r k mu K", positive=True)
    lnPsi = mu / 2 * sp.exp(-k ** 2 * r ** 2 / 6)
    # linear density contrast delta = -(4/5) (aH)^-2 lap ln Psi; (aH)^-2 = K/k^2, K = 6 at entry
    lap = sp.diff(r ** 2 * sp.diff(lnPsi, r), r) / r ** 2
    delta = -sp.Rational(4, 5) * (K / k ** 2) * lap
    s = sp.symbols("s", positive=True)
    dbar = sp.simplify(3 / r ** 3 * sp.integrate((delta * r ** 2).subs(r, s), (s, 0, r)))
    dbar6 = sp.simplify(dbar.subs(K, 6))
    rm_sol = sp.solve(sp.diff(r ** 2 * dbar6, r), r)       # linear compaction ~ r^2 dbar
    rm = [x for x in rm_sol if x.is_positive][0]
    paper_rm = sp.solve(sp.diff(lnPsi, r) + r * sp.diff(lnPsi, r, 2), r)   # MDPBH.tex L709-711
    dbar_rm = sp.simplify(dbar6.subs(r, rm) / mu)
    dc = sp.limit(dbar6 / mu, r, 0)
    res = dict(dbar_closed=str(dbar6), r_m=str(rm), r_m_paper=[str(x) for x in paper_rm],
               dbar_rm_over_mu=float(dbar_rm), dbar_rm_over_mu_expr=str(dbar_rm),
               delta_c_over_mu=float(dc), ratio_central_to_mean=float(dc / dbar_rm),
               scope_value_0p883=12 / (5 * E_EULER))
    # turnaround compactness from exact shells
    rows = []
    for Di in (1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4):
        HRi = 0.5
        sh = tophat_shell(Di, HRi)
        dbar_ent = Di * HRi ** 2            # growing mode: Delta (HR)^2 conserved at linear order
        rows.append(dict(Delta_i=Di, C_ta=sh["C_ta"], ratio=sh["C_ta"] / dbar_ent,
                         tc_lin=Di * (sh["t_c"] / sh["t_i"]) ** (2.0 / 3.0)))
    res["turnaround_rows"] = rows
    res["ratio_limit_est"] = rows[-1]["ratio"]
    res["delta_crit_limit_est"] = rows[-1]["tc_lin"]
    res["delta_crit_textbook"] = 3.0 / 20.0 * (12 * math.pi) ** (2.0 / 3.0)
    res["pass"] = bool(abs(res["dbar_rm_over_mu"] - 12 / (5 * E_EULER)) < 1e-12
                       and abs(res["delta_c_over_mu"] - 2.4) < 1e-12
                       and abs(res["ratio_limit_est"] - 5 / 3) < 1e-3)
    # figure
    fs.use_style()
    fig, (a1, a2) = fs.plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.95, wspace=0.3)
    f = sp.lambdify(r, dbar6.subs({mu: 1, k: 1}), "numpy")
    rr = np.linspace(1e-3, 4.5, 400)
    a1.plot(rr / math.sqrt(6), f(rr), color=fs.PAL["blue"], label=r"$\bar\delta(r)/\mu$ at $aH=k/\sqrt{6}$")
    a1.plot(rr / math.sqrt(6), rr ** 2 / 6 * f(rr), color=fs.PAL["red"],
            label=r"$(r/r_m)^2\,\bar\delta/\mu$ (compaction)")
    a1.axvline(1.0, **fs.MASK_LINE)
    a1.axhline(12 / (5 * E_EULER), **fs.GUIDE)
    a1.set_xlabel(r"$r/r_m$, $r_m=\sqrt{6}/k$")
    a1.set_ylabel("contrast / $\\mu$")
    a1.legend(fontsize=7, loc="upper right")
    D = np.array([x["Delta_i"] for x in rows])
    a2.semilogx(D, [x["ratio"] for x in rows], "o-", color=fs.PAL["blue"], ms=4,
                label=r"$(2m/R_{\rm ta})/\bar\delta_{\rm ent}$")
    a2.semilogx(D, [x["tc_lin"] for x in rows], "s-", color=fs.PAL["red"], ms=4,
                label=r"$\Delta_i (t_c/t_i)^{2/3}$")
    a2.axhline(5 / 3, **fs.GUIDE)
    a2.axhline(res["delta_crit_textbook"], color="k", lw=1.0, ls=":")
    a2.set_xlabel(r"start contrast $\Delta_i$ (exact shell, simultaneous bang)")
    a2.set_ylabel("ratio")
    a2.legend(fontsize=7, loc="center left")
    fs.save(fig, os.path.join(figdir, "fig_V2_conventions"))
    fs.plt.close(fig)
    out["V2"] = res
    return res


# ============================================================================ V1
def part_V1(out, figdir):
    c_mean = 12 / (5 * E_EULER)
    res = {"rows": []}
    for q in (2.0, 3.0, 4.0):
        for RbH in (0.5, 0.7, 0.9):
            # R_b H_i = q r_m (aH)_i ; (aH) ~ a^(-1/2); r_m (aH)_H = 1
            a_ratio = optimize.brentq(lambda x: q * x ** 0.5 - RbH, 1e-9, 1e6)   # x = a_H/a_i
            ai_aH = 1.0 / a_ratio
            for cap in (0.3, 0.5, 1.0):
                res["rows"].append(dict(q=q, RbH=RbH, ai_over_aH=ai_aH, cap=cap,
                                        mu_max_mean=cap / (c_mean * ai_aH),
                                        mu_max_centre=cap / (2.4 * ai_aH)))
    pick = {(r["q"], r["RbH"], r["cap"]): r for r in res["rows"]}
    res["mu_max_q3_0p9_cap0p3"] = pick[(3.0, 0.9, 0.3)]["mu_max_mean"]
    res["mu_max_q2_0p9_cap0p3"] = pick[(2.0, 0.9, 0.3)]["mu_max_mean"]
    res["mu_max_q2_0p9_cap0p3_centre"] = pick[(2.0, 0.9, 0.3)]["mu_max_centre"]
    # cap needed to hold the particle bracket mu = 0.05 and the hoop value mu = 0.45 at e = 0.2
    res["cap_needed"] = {f"q{q:g}_mu{m:g}": m * c_mean * (q / 0.9) ** 2
                         for q in (2.0, 3.0) for m in (0.05, 0.45)}
    res["particle_bracket_inside_q2"] = bool(res["mu_max_q2_0p9_cap0p3"] > 0.05)
    # anti-trapping on the data sets: own Misner-Sharp max on the own construction (see V5)
    out["V1"] = res
    fs.use_style()
    fig, ax = fs.plt.subplots(figsize=(fs.COLUMN_WIDTH + 0.8, 3.2))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.96)
    RbH = np.linspace(0.3, 0.99, 200)
    for q, c in ((2.0, fs.PAL["blue"]), (3.0, fs.PAL["red"])):
        ai = (q / RbH) ** 2
        ax.plot(RbH, 0.3 / (c_mean * ai), color=c, label=fr"$q={q:g}$, mean in $r_m\leq0.3$")
        ax.plot(RbH, 0.3 / (2.4 * ai), color=c, ls=":", lw=1.0, label=fr"$q={q:g}$, centre $\leq0.3$")
        ax.plot(RbH, 1.0 / (c_mean * ai), color=c, ls="--", lw=1.0, label=fr"$q={q:g}$, mean $\leq1$")
    ax.axhspan(0.045, 0.05, color="grey", alpha=0.35, lw=0)
    ax.axhline(0.452, **fs.MASK_LINE)
    ax.text(0.31, 0.052, "particle bracket (0.045, 0.05]", fontsize=7)
    ax.text(0.31, 0.47, r"hoop line $\hat h(0.2,0)$", fontsize=7)
    ax.set_yscale("log")
    ax.set_ylim(2e-3, 1.0)
    ax.set_xlabel(r"$R_b H_i$")
    ax.set_ylabel(r"largest $\mu$ the ball holds")
    ax.legend(fontsize=6, loc="lower right", ncol=2)
    fs.save(fig, os.path.join(figdir, "fig_V1_ball_window"))
    fs.plt.close(fig)
    return res


# ============================================================================ V3
def ellipse_perimeter(a, b):
    f = lambda th: math.sqrt(a * a * math.sin(th) ** 2 + b * b * math.cos(th) ** 2)
    return integrate.quad(f, 0.0, 2 * math.pi, epsabs=1e-14, epsrel=1e-13, limit=200)[0]


def hoop_h(mu, e, p):
    """Zel'dovich pancake of the Lagrangian sphere r_m (units: a_ent = 1, r_m = 1, H_ent = 1,
    so M = 1/2) at the first caustic; h = C / (4 pi M) (Thorne hoop: C <= 4 pi M)."""
    lam = 2 * mu / 15 * 6 * np.array([1 + 3 * e + p, 1 - 2 * p, 1 - 3 * e + p])   # at entry
    al, be, ga = sorted(lam, reverse=True)
    a_c = 1.0 / al                               # growing mode: lambda(a) = lambda_ent a
    A = a_c * (1 - ga / al)                      # semi-axes of the pancake ellipse
    B = a_c * (1 - be / al)
    C = ellipse_perimeter(A, B)
    return C / (4 * math.pi * 0.5)


def render_pdf(pdf, outdir, stem, dpi=200):
    os.makedirs(outdir, exist_ok=True)
    target = os.path.join(outdir, stem)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", pdf, target], check=True,
                   timeout=120)
    return target + ".png"


def part_V3(out, figdir, rundir):
    res = {}
    rows = []
    for e in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3):
        mc = optimize.brentq(lambda m: hoop_h(m, e, 0.0) - 1.0, 1e-3, 5.0, xtol=1e-14)
        x = 0.5
        hhat_mod = 15 / math.pi * e / (1 + 3 * e) ** 2 * special.ellipe(1 - x * x)      # modulus k
        hhat_par = 15 / math.pi * e / (1 + 3 * e) ** 2 * special.ellipe(math.sqrt(1 - x * x))
        rows.append(dict(e=e, mu_c_quadrature=mc, hhat_modulus=hhat_mod, hhat_parameter=hhat_par))
    res["rows"] = rows
    r02 = [r for r in rows if r["e"] == 0.2][0]
    res["mu_c_0p2"] = r02["mu_c_quadrature"]
    res["max_rel_dev_modulus"] = max(abs(r["mu_c_quadrature"] / r["hhat_modulus"] - 1) for r in rows)
    # a prolate / oblate point
    res["p_rows"] = []
    for p in (-0.1, 0.1):
        mc = optimize.brentq(lambda m: hoop_h(m, 0.2, p) - 1.0, 1e-3, 5.0, xtol=1e-14)
        x = (0.2 + p) / 0.4
        hh = 15 / math.pi * 0.2 / (1 + 0.6 + p) ** 2 * special.ellipe(1 - x * x)
        res["p_rows"].append(dict(e=0.2, p=p, mu_c_quadrature=mc, hhat_modulus=hh))
    res["pass"] = bool(res["max_rel_dev_modulus"] < 1e-6 and abs(res["mu_c_0p2"] - 0.452) < 5e-4)
    try:
        res["render_thre_p0"] = render_pdf(os.path.join(SRC_2609, "thre_p0.pdf"),
                                           os.path.join(rundir, "src_render"), "thre_p0")
    except Exception as exc:                       # noqa: BLE001
        res["render_thre_p0"] = f"failed: {exc}"
    fs.use_style()
    fig, ax = fs.plt.subplots(figsize=(fs.COLUMN_WIDTH + 0.5, 3.0))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.16, top=0.96)
    ee = np.array([r["e"] for r in rows])
    ax.plot(ee, [r["mu_c_quadrature"] for r in rows], "o", color=fs.PAL["blue"], ms=5,
            label="pancake perimeter by quadrature")
    eg = np.linspace(0.01, 0.3, 200)
    ax.plot(eg, 15 / np.pi * eg / (1 + 3 * eg) ** 2 * special.ellipe(0.75), color=fs.PAL["blue"], lw=1.0,
            label=r"$\hat h$, $E$ of modulus $\sqrt{3}/2$")
    ax.plot(eg, 15 / np.pi * eg / (1 + 3 * eg) ** 2 * special.ellipe(math.sqrt(0.75)), color=fs.PAL["red"],
            lw=1.0, ls="--", label=r"$\hat h$, parameter $\sqrt{3}/2$ (wrong)")
    ax.set_xlabel(r"ellipticity $e$ ($p=0$)")
    ax.set_ylabel(r"hoop threshold $\mu_c$")
    ax.legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(figdir, "fig_V3_hoop"))
    fs.plt.close(fig)
    out["V3"] = res
    return res


# ============================================================================ V4
def part_V4(out, figdir, rundir):
    dcrit = 3.0 / 20.0 * (12 * math.pi) ** (2.0 / 3.0)
    c_mean = 12 / (5 * E_EULER)

    def t_c(mu, centre=False):                 # in t_H; linear contrast grows as t^(2/3)
        d = (2.4 if centre else c_mean) * mu
        return (dcrit / d) ** 1.5

    def mu_fd(tend):
        return dcrit / (c_mean * tend ** (2.0 / 3.0))
    res = dict(delta_crit=dcrit, mu_fd={str(t): mu_fd(t) for t in (100, 245, 250, 400, 1000)},
               t_c_rm={str(m): t_c(m) for m in (0.3, 0.15, 0.1, 0.075, 0.06, 0.05, 0.045, 0.04)},
               t_c_centre={str(m): t_c(m, True) for m in (0.05, 0.045)},
               delta_fd_literal_250=250.0 ** (-2.0 / 3.0),
               mu_from_literal_delta_fd_250=250.0 ** (-2.0 / 3.0) / c_mean)
    res["t_pred_0p045_ratio0p86"] = 0.86 * t_c(0.045)
    res["t_pred_0p045_ratio1p01"] = 1.01 * t_c(0.045)
    res["t_pred_0p045_ratio0p80"] = 0.80 * t_c(0.045)
    # by-eye read-offs of the verifier from the rendered alpha.pdf (recorded in the JOURNAL
    # after the first run A-20261115-160935-41f721d; not the track's values)
    res["readoff_alpha_pdf"] = dict(mu=[0.15, 0.10, 0.075, 0.06, 0.05], t_drop=[46.0, 74.0, 106.0, 145.0, 180.0],
                                    **{"mu0.05_final": 218.0, "mu0.045_dip": 208.0})
    res["readoff_ratio_to_tc_rm"] = [t / t_c(m) for m, t in zip(res["readoff_alpha_pdf"]["mu"],
                                                                res["readoff_alpha_pdf"]["t_drop"])]
    res["ratio_0p045_dip"] = 208.0 / t_c(0.045)
    res["ratio_0p05_final_over_first"] = 218.0 / 180.0
    res["t_0p045_by_two_stage_scaling"] = 208.0 * 218.0 / 180.0
    try:
        res["render_alpha"] = render_pdf(os.path.join(SRC_2609, "alpha.pdf"),
                                         os.path.join(rundir, "src_render"), "alpha", dpi=250)
    except Exception as exc:                       # noqa: BLE001
        res["render_alpha"] = f"failed: {exc}"
    fs.use_style()
    fig, ax = fs.plt.subplots(figsize=(fs.COLUMN_WIDTH + 0.5, 3.2))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.96)
    mu = np.logspace(np.log10(0.03), np.log10(0.4), 200)
    ax.loglog(mu, t_c(mu), color=fs.PAL["blue"], label=r"top hat, shell $r_m$")
    ax.loglog(mu, t_c(mu, True), color=fs.PAL["blue"], ls=":", lw=1.0, label="top hat, centre")
    ax.loglog(mu, 0.86 * t_c(mu), color=fs.PAL["red"], ls="--", lw=1.0, label=r"$0.86\,t_c(r_m)$")
    ax.axhline(250, **fs.MASK_LINE)
    ax.text(0.12, 290, "end of the plotted runs, 250 $t_H$", fontsize=7, color="grey")
    ax.axvspan(0.045, 0.05, color="grey", alpha=0.3, lw=0)
    # verifier's by-eye read-offs of the steep lapse drops in alpha.pdf (src_render/alpha.png)
    ro = res["readoff_alpha_pdf"]
    ax.plot(ro["mu"], ro["t_drop"], "o", color="k", ms=4, label="alpha.pdf, steep drop (by eye)")
    ax.plot([0.05], [ro["mu0.05_final"]], "v", color="k", ms=5, label=r"$\mu=0.05$, final collapse")
    ax.plot([0.045], [ro["mu0.045_dip"]], "x", color="k", ms=6, label=r"$\mu=0.045$, dip, recovers")
    ax.set_xlabel(r"$\mu$")
    ax.set_ylabel(r"$t/t_H$")
    ax.set_xlim(0.03, 0.4)
    ax.set_ylim(5, 800)
    ax.set_xticks([0.03, 0.05, 0.1, 0.2, 0.4])
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%g"))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.legend(fontsize=7, loc="lower left")
    fs.save(fig, os.path.join(figdir, "fig_V4_timing"))
    fs.plt.close(fig)
    out["V4"] = res
    return res


# ============================================================================ V5: own ball
def F_hyp(y):
    return special.hyp2f1(0.5, 1.5, 2.5, y)


def y_of_D(D):
    """Invert F(y) = sqrt(1 + D) by bracketing per point (own, no Newton from the track)."""
    D = np.atleast_1d(D)
    y = np.zeros_like(D)
    for i, d in enumerate(D):
        if d == 0.0:
            continue
        target = math.sqrt(1 + d)
        lo, hi = (-50.0, 0.0) if d < 0 else (0.0, 1.0 - 1e-15)
        y[i] = optimize.brentq(lambda t: F_hyp(t) - target, lo, hi, xtol=1e-17, rtol=1e-15, maxiter=300)
    return y


def S_inf(u):
    u = np.asarray(u, float)
    out = np.where(u >= 1, 1.0, 0.0)
    s = (u > 0) & (u < 1)
    us = u[s]
    out[s] = 1.0 / (1.0 + np.exp(1.0 / us - 1.0 / (1.0 - us)))
    return out


def S4(u):
    u = np.clip(u, 0, 1)
    # C^4 smoothstep (zero derivatives 1..4 at both ends), standard degree-9 polynomial
    return 126 * u ** 5 - 420 * u ** 6 + 540 * u ** 7 - 315 * u ** 8 + 70 * u ** 9


class OwnBall:
    """Expanding ball, built from its definition: H R_b, M (R_b = 2M/(H R_b)^2), core Delta(R)
    = dc (1 - S((R - R1)/(R2 - R1))), C^4 taper of half width w at R_b, simultaneous bang."""

    def __init__(self, HRb=0.5, M=1.0, dc=1.0, R1f=0.3, R2f=0.75, wf=0.1875, n=300001, flipKL=False,
                 staticKL=False, flipK=False):
        self.dc = dc
        self.Rb = 2 * M / HRb ** 2
        self.H = HRb / self.Rb
        H, Rb = self.H, self.Rb
        self.R1, self.R2, self.w = R1f * Rb, R2f * Rb, wf * Rb
        Rmax = 2.6 * Rb
        # dense grid with points at the region boundaries
        R = np.unique(np.concatenate([np.linspace(1e-6 * Rb, self.R2, n // 2),
                                      np.linspace(self.R2, Rmax, n // 2)]))
        self.Rg = R
        rho_b = 3 * H ** 2 / (8 * math.pi)
        self.rho_b = rho_b
        D = np.where(R < self.R2, dc * (1 - S_inf((R - self.R1) / (self.R2 - self.R1))), 0.0)
        y = np.zeros_like(R)
        core = (R < self.R2) & (D != 0)
        # y depends on R only through D: invert on a D grid and interpolate (monotone, smooth)
        Du = np.unique(D[core])
        if Du.size:
            Dg = np.linspace(Du.min(), Du.max(), 4001)
            yg = y_of_D(Dg)
            y[core] = CubicSpline(Dg, yg)(D[core])
        # density: core rho_b (1 + Delta + R Delta'/3) from m = (H^2/2) R^3 (1 + Delta), with
        # dS/du = S (1 - S) (1/u^2 + 1/(1-u)^2); envelope rho_b; C^4 taper; vacuum outside
        u = (R - self.R1) / (self.R2 - self.R1)
        Su = S_inf(u)
        uc = np.clip(u, 1e-12, 1 - 1e-12)
        dS = np.where((u > 0) & (u < 1), Su * (1 - Su) * (1 / uc ** 2 + 1 / (1 - uc) ** 2), 0.0)
        dD = np.where(R < self.R2, -dc * dS / (self.R2 - self.R1), 0.0)
        rho = np.where(R <= Rb - self.w, rho_b * (1 + D + R * dD / 3.0), 0.0)
        tap = (R > Rb - self.w) & (R < Rb + self.w)
        rho[tap] = rho_b * (1 - S4(((R[tap] - Rb) / self.w + 1) / 2))
        # mass: core from Delta; outside R2 by a spline antiderivative of 4 pi R^2 rho
        m = np.empty_like(R)
        m_core = 0.5 * H ** 2 * R ** 3 * (1 + D)
        inner = R <= self.R2
        m[inner] = m_core[inner]
        outer = ~inner
        Ro = R[outer]
        m_R2 = 0.5 * H ** 2 * self.R2 ** 3
        sp_dm = CubicSpline(np.concatenate([[self.R2], Ro]),
                            np.concatenate([[4 * math.pi * self.R2 ** 2 * rho_b], 4 * math.pi * Ro ** 2 * rho[outer]]))
        anti = sp_dm.antiderivative()
        m[outer] = m_R2 + anti(Ro) - anti(self.R2)
        self.M = float(m[-1])
        E = -y * m / R
        f = 1 + 2 * E
        v = np.sqrt(2 * m / R + 2 * E)
        sv = CubicSpline(R, v)
        KL = -sv(R, 1)
        if staticKL:            # the "static metric" mistake named in DERIVATION.md section 2
            dE = CubicSpline(R, E)(R, 1)
            KL = KL + v * dE / f
        if flipKL:
            KL = -KL
        KT = -v / R
        if flipK:               # time reverse (collapsing ball): K -> -K
            KL, KT = -KL, -KT
        # conformal map: G(R) = int_R^R2 (1/sqrt f - 1) dR'/R'
        g = (1 / np.sqrt(f) - 1) / R
        sg = CubicSpline(R, g).antiderivative()
        G = np.where(R < self.R2, sg(self.R2) - sg(R), 0.0)
        rbar = R * np.exp(-G)
        psi = np.exp(0.5 * G)
        self.d = dict(R=R, D=D, y=y, m=m, E=E, f=f, v=v, KL=KL, KT=KT, rho=rho, G=G, rbar=rbar, psi=psi,
                      betar=-v / (psi ** 2 * np.sqrt(f)))
        self.sp = {k: CubicSpline(rbar, self.d[k]) for k in ("psi", "KL", "KT", "rho", "betar", "R")}
        self.rbar_max = rbar[-1]

    def fields(self, rb):
        rb = np.asarray(rb)
        o = {k: self.sp[k](np.minimum(rb, self.rbar_max)) for k in self.sp}
        far = rb > self.rbar_max
        if np.any(far):
            vv = np.sqrt(2 * self.M / rb[far])
            o["psi"][far] = 1.0
            o["KL"][far] = vv / (2 * rb[far])
            o["KT"][far] = -vv / rb[far]
            o["rho"][far] = 0.0
        return o

    def max_compactness(self):
        q = 2 * self.d["m"] / self.d["R"]
        i = int(np.argmax(q))
        return float(q[i]), float(self.d["R"][i])

    def shell_times(self, Ri):
        """Own cycloid times since the slice for shells at areal radius Ri < R2, with (m, E)
        computed at Ri from the definition (no interpolation)."""
        Ri = np.atleast_1d(np.asarray(Ri, float))
        H = self.H
        D = self.dc * (1 - S_inf((Ri - self.R1) / (self.R2 - self.R1)))
        y = y_of_D(D)
        m = 0.5 * H ** 2 * Ri ** 3 * (1 + D)
        E = -y * m / Ri
        out = []
        t_i = 2 / (3 * H)
        for mm, EE in zip(m, E):
            if EE >= 0:
                out.append((np.inf, np.inf, np.inf))
                continue
            T0 = mm / (-2 * EE) ** 1.5
            eta = 2 * math.pi - math.acos(1 + 4 * EE)
            out.append((math.pi * T0 - t_i, 2 * math.pi * T0 - t_i, T0 * (eta - math.sin(eta)) - t_i))
        return np.array(out)


def constraints_own(ball, N, L):
    """Hamiltonian and momentum residuals on the full cell-centred box [-L, L]^3 (N even),
    second-order centred differences written here (np.gradient interior + 7-point Laplacian),
    Christoffel symbols of psi^4 delta_ij by hand: M_i = d_j K^j_i + 6 K^l_i d_l ln psi
    - 2 K d_i ln psi - d_i K. Returns arrays on the interior (N-2)^3 and the radius."""
    h = 2 * L / N
    c = -L + (np.arange(N) + 0.5) * h
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    rb = np.sqrt(X * X + Y * Y + Z * Z)
    fl = ball.fields(rb)
    psi, KL, KT, rho = fl["psi"], fl["KL"], fl["KT"], fl["rho"]
    n = (X / rb, Y / rb, Z / rb)
    Km = [[(KL - KT) * n[i] * n[j] + (KT if i == j else 0.0) for j in range(3)] for i in range(3)]
    trK = KL + 2 * KT
    lp = np.log(psi)
    I = (slice(1, -1),) * 3

    def d(F, ax):
        return np.gradient(F, h, axis=ax)[I]
    lap = ((psi[2:, 1:-1, 1:-1] + psi[:-2, 1:-1, 1:-1] + psi[1:-1, 2:, 1:-1] + psi[1:-1, :-2, 1:-1]
            + psi[1:-1, 1:-1, 2:] + psi[1:-1, 1:-1, :-2] - 6 * psi[I]) / h ** 2)
    Hres = -8 * psi[I] ** -5 * lap + trK[I] ** 2 - (KL[I] ** 2 + 2 * KT[I] ** 2) - 16 * math.pi * rho[I]
    dl = [d(lp, a) for a in range(3)]
    Mv = []
    for i in range(3):
        s = sum(d(Km[j][i], j) for j in range(3))
        s = s + 6 * sum(Km[l][i][I] * dl[l] for l in range(3))
        s = s - 2 * trK[I] * dl[i] - d(trK, i)
        Mv.append(s)
    Mabs = np.sqrt(Mv[0] ** 2 + Mv[1] ** 2 + Mv[2] ** 2)
    return Hres, Mabs, rb[I]


def part_V5(out, figdir, Nmax=128, Ns=None, Ntrack=128):
    res = {}
    ball = OwnBall()
    H = ball.H
    norm = 6 * H ** 2
    res["own_ball"] = dict(H=H, Rb=ball.Rb, M=ball.M, R1=ball.R1, R2=ball.R2, w=ball.w,
                           psi_centre=float(ball.d["psi"][0]), KT_centre=float(ball.d["KT"][0]))
    q, Rq = ball.max_compactness()
    res["own_ball"]["max_2m_over_R"] = q
    res["own_ball"]["R_at_max"] = Rq
    # (i) compare with the table that goes into AthenaK (data set 2t)
    tabp = ("/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/"
            "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875.tab")
    if os.path.exists(tabp):
        T = np.loadtxt(tabp, comments="#")
        rbt = T[:, 0]
        o = ball.fields(rbt)
        dev = {"u": np.abs((T[:, 1] + 1) - o["psi"]),
               "KL": np.abs(T[:, 2] - o["KL"]) / H, "KT": np.abs(T[:, 3] - o["KT"]) / H,
               "betar": np.abs(T[:, 5] - o["betar"])}
        res["table_vs_own"] = {k: dict(max=float(v.max()), at_rbar=float(rbt[int(np.argmax(v))]))
                               for k, v in dev.items()}
        res["table_alpha_all_one"] = bool(np.all(T[:, 4] == 1.0))
        res["table_sign_expanding"] = bool(T[0, 2] < 0 and T[0, 3] < 0)
    # (ii) own cycloid times vs the predictions written with the data set
    Ri = np.linspace(0.02375, ball.R2 * 0.999, 400)
    tt = ball.shell_times(Ri)
    k = int(np.argmin(tt[:, 2]))
    fh = optimize.minimize_scalar(lambda x: ball.shell_times([x])[0, 2],
                                  bounds=(Ri[max(k - 2, 0)], Ri[min(k + 2, len(Ri) - 1)]), method="bounded",
                                  options=dict(xatol=1e-9))
    res["own_times"] = dict(core_tau_ta=float(tt[0, 0]), core_tau_c=float(tt[0, 1]),
                            core_edge_tau_ah=float(ball.shell_times([ball.R1])[0, 2]),
                            first_horizon_tau_grid=float(tt[k, 2]), first_horizon_Ri_grid=float(Ri[k]),
                            first_horizon_tau=float(fh.fun), first_horizon_Ri=float(fh.x),
                            first_horizon_m=float(0.5 * ball.H ** 2 * fh.x ** 3 * (1 + ball.dc * (
                                1 - S_inf((fh.x - ball.R1) / (ball.R2 - ball.R1))))))
    pred = ("/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/"
            "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875.json")
    if os.path.exists(pred):
        pj = json.load(open(pred))["predictions"]
        res["track_predictions"] = dict(core_tau_ta=pj["core_tau_ta"], core_tau_c=pj["core_tau_c"],
                                        first_horizon=pj["first_horizon"], core_edge=pj["core_edge_shell"])
    # (iii) own 3D constraint convergence, with two deliberately broken variants
    Ns = Ns or [n for n in (32, 48, 64, 96, 128, 160, 192) if n <= Nmax]
    L = 1.25 * ball.Rb
    variants = {"own": ball, "flipKL": OwnBall(flipKL=True), "staticKL": OwnBall(staticKL=True),
                "flipK": OwnBall(flipK=True)}
    conv = {}
    for name, b in variants.items():
        conv[name] = {"N": [], "h": [], "H_L2": [], "M_L2": [], "H_L2_all": [], "M_L2_all": []}
        for N in Ns:
            Hr, Ma, rr = constraints_own(b, N, L)
            # exclude the outer two cells (box edge) and nothing else: the data are smooth
            sel = (rr < 1.15 * ball.Rb)
            conv[name]["N"].append(N)
            conv[name]["h"].append(2 * L / N)
            conv[name]["H_L2"].append(float(np.sqrt(np.mean((Hr[sel] / norm) ** 2))))
            conv[name]["M_L2"].append(float(np.sqrt(np.mean((Ma[sel] / norm) ** 2))))
            conv[name]["H_L2_all"].append(float(np.sqrt(np.mean((Hr / norm) ** 2))))
            conv[name]["M_L2_all"].append(float(np.sqrt(np.mean((Ma / norm) ** 2))))
        hs = np.array(conv[name]["h"])
        for key in ("H_L2", "M_L2"):
            e = np.array(conv[name][key])
            conv[name][key + "_orders"] = (np.log(e[:-1] / e[1:]) / np.log(hs[:-1] / hs[1:])).tolist()
    res["own_convergence"] = conv
    # (iv) the track's own test function on the track's own Ball (rerun of the G1 test)
    try:
        sys.path.insert(0, os.path.join(ROOT, "tracks", "A-emd-pbh", "expball"))
        from expball import mesh as tmesh, model as tmodel
        RB = 8.0
        tb = tmodel.Ball.from_HRb(0.5, profile=tmodel.SmoothTopHat(1.0, 0.3 * RB, 0.75 * RB),
                                  edge_width=0.1875 * RB)
        src = tmesh.radial_source(tb)
        tr = {"N": [], "p2_H": [], "p2_M": [], "p4_H": [], "p4_M": []}
        regs = {"all": lambda r: np.ones_like(r, dtype=bool)}
        for N in [n for n in (32, 64, 128, 256) if n <= Ntrack]:
            r = tmesh.residuals(src, N, 1.25 * RB, (2, 4), regs, norm=6 * tb.H ** 2)
            tr["N"].append(N)
            for p in (2, 4):
                tr[f"p{p}_H"].append(r[p]["all"]["H_L2"])
                tr[f"p{p}_M"].append(r[p]["all"]["M_L2"])
        for key in ("p2_H", "p2_M", "p4_H", "p4_M"):
            e = np.array(tr[key])
            tr[key + "_orders"] = (np.log2(e[:-1] / e[1:])).tolist()
        res["track_test_rerun_dataset2t"] = tr
        # the track's Ball against the own construction, pointwise
        x = np.linspace(0.01, 1.6 * RB, 3000)
        fo = ball.fields(x)
        ft = tb.fields(x, ("u", "KL", "KT", "rho", "betar"))
        res["track_ball_vs_own"] = {"psi": float(np.max(np.abs(ft["u"] + 1 - fo["psi"]))),
                                    "KL_over_H": float(np.max(np.abs(ft["KL"] - fo["KL"])) / H),
                                    "KT_over_H": float(np.max(np.abs(ft["KT"] - fo["KT"])) / H),
                                    "rho_over_rhob": float(np.max(np.abs(ft["rho"] - fo["rho"])) / ball.rho_b),
                                    "betar": float(np.max(np.abs(ft["betar"] - fo["betar"])))}
        res["track_summary_max_2m_over_R"] = tb.summary()["max_2m_over_R"]
    except Exception as exc:                        # noqa: BLE001
        res["track_test_rerun_dataset2t"] = f"failed: {exc!r}"
    out["V5"] = res
    # figures: convergence and the radial data
    fs.use_style()
    fig, axs = fs.plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.30, top=0.96, wspace=0.3)
    sty = {"own": dict(color=fs.PAL["blue"], marker="o", ms=8, mfc="none", lw=2.5),
           "flipKL": dict(color=fs.PAL["red"], marker="s", ms=4),
           "staticKL": dict(color=fs.PAL["yellow"], marker="^", ms=4),
           "flipK": dict(color=fs.PAL["green"], marker=".", ms=6, lw=1.0, ls="--")}
    labs = {"own": "own data (expanding)", "flipKL": r"$K_L\to-K_L$ (broken)",
            "staticKL": r"$K_L$ of a static $\gamma_{RR}$ (broken)",
            "flipK": r"$K_{ij}\to-K_{ij}$ (collapsing ball)"}
    for i, key in enumerate(("H_L2", "M_L2")):
        ax = axs[i]
        for name in ("own", "flipKL", "staticKL", "flipK"):
            hh = np.array(conv[name]["h"]) / ball.Rb
            ax.loglog(hh, conv[name][key], label=labs[name] if i == 0 else None, **sty[name])
        hh = np.array(conv["own"]["h"]) / ball.Rb
        e = np.array(conv["own"][key])
        ax.loglog(hh, e[-1] * (hh / hh[-1]) ** 2, **fs.GUIDE, label=r"$\propto h^2$" if i == 0 else None)
        ax.set_xticks([0.01, 0.02, 0.04, 0.08])
        ax.set_xticklabels(["0.01", "0.02", "0.04", "0.08"])
        ax.xaxis.set_minor_formatter(mticker.NullFormatter())
        ax.set_xlabel(r"$h/R_b$")
        ax.set_ylabel(("Hamiltonian" if key == "H_L2" else "momentum") + r" $L_2/6H^2$, $r<1.15R_b$")
    fig.legend(loc="lower center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, 0.0))
    fs.save(fig, os.path.join(figdir, "fig_V5_constraints"))
    fs.plt.close(fig)
    tr = res.get("track_test_rerun_dataset2t")
    if isinstance(tr, dict) and len(tr["N"]) > 1:
        fig, ax = fs.plt.subplots(figsize=(fs.COLUMN_WIDTH + 0.6, 3.2))
        fig.subplots_adjust(left=0.17, right=0.97, bottom=0.15, top=0.96)
        hN = 1.25 / np.array(tr["N"])
        for key, c, mk in (("p2_H", fs.PAL["blue"], "o"), ("p2_M", fs.PAL["blue"], "s"),
                           ("p4_H", fs.PAL["red"], "o"), ("p4_M", fs.PAL["red"], "s")):
            ax.loglog(hN, tr[key], mk + "-", color=c, ms=4, mfc="none" if key.endswith("M") else c,
                      label=f"order {key[1]}, " + ("Hamiltonian" if key.endswith("H") else "momentum"))
        for q, key in ((2, "p2_M"), (4, "p4_H")):
            e = np.array(tr[key])
            ax.loglog(hN, e[-1] * (hN / hN[-1]) ** q, **fs.GUIDE)
        ax.set_xlabel(r"$h/R_b$ (track's octant mesh)")
        ax.set_ylabel(r"$L_2/6H^2$, all cells, data set 2t")
        ax.legend(fontsize=7, loc="lower right")
        fs.save(fig, os.path.join(figdir, "fig_V5_track_test_rerun"))
        fs.plt.close(fig)
    fig, axs = fs.plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.18, top=0.95, wspace=0.35)
    R = ball.d["R"] / ball.Rb
    s = slice(None, None, 50)
    axs[0].plot(R[s], ball.d["rho"][s] / ball.rho_b, color=fs.PAL["blue"])
    axs[0].set_ylabel(r"$\rho/\rho_b$")
    axs[1].plot(R[s], ball.d["KL"][s] / H, color=fs.PAL["blue"], label=r"$K_L/H$")
    axs[1].plot(R[s], ball.d["KT"][s] / H, color=fs.PAL["red"], label=r"$K_T/H$")
    axs[1].legend(fontsize=7)
    axs[2].plot(R[s], 2 * ball.d["m"][s] / ball.d["R"][s], color=fs.PAL["blue"], label=r"$2m/R$")
    axs[2].plot(R[s], -2 * ball.d["E"][s], color=fs.PAL["red"], label=r"$-2E$")
    axs[2].legend(fontsize=7)
    for ax in axs:
        ax.set_xlabel(r"$R/R_b$")
        ax.set_xlim(0, 2.0)
    fs.save(fig, os.path.join(figdir, "fig_V5_radial"))
    fs.plt.close(fig)
    return res


# ============================================================================ V6
def part_V6(out, figdir):
    res = {}
    # virial (arXiv:2507.18312 L540-542): 2K + U = 0, 2K = M sigma^2, U = -(3/5) M^2/R, sigma R
    # conserved (Liouville, arXiv:2211.13950 L330-334): sigma = 2 M s / R
    # -> R_min = (20/3) M s^2 ; BH iff R_min < 2M
    res["s_c_virial"] = math.sqrt(3.0 / 10.0)
    # arXiv:2211.13950 L349-358: R_halt = (4/9) sigma*^2 R*^2 / R_ent, R_ent = 2M -> s < 3/2
    res["s_c_2211"] = optimize.brentq(lambda s: 4.0 / 9.0 * s * s - 1.0, 0.1, 10)
    dbar = np.array([0.01, 0.02, 0.04, 0.08])
    bBH = 5.0 / 3.0 * dbar                         # arXiv:2507.18312 L314-316
    res["N_lattice"] = ((0.1 * bBH) ** (-9.0 / 4.0)).tolist()      # b_min ~ N^(-4/9), L524
    res["N_random"] = ((1.2 / (0.1 * bBH)) ** 3).tolist()          # b_min = 1.2 N^(-1/3), L489-492
    res["ratio_random_lattice"] = (np.array(res["N_random"]) / np.array(res["N_lattice"])).tolist()
    res["dbar"] = dbar.tolist()
    out["V6"] = res
    fs.use_style()
    fig, (a1, a2) = fs.plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.95, wspace=0.3)
    s = np.linspace(0, 2.2, 300)
    a1.plot(s, 10 / 3 * s * s, color=fs.PAL["blue"], label="virial halt (2507.18312)")
    a1.plot(s, 4 / 9 * s * s, color=fs.PAL["red"], label=r"$t_{\rm ff}=t_{\rm cross}$ (2211.13950)")
    a1.axhline(1, **fs.GUIDE)
    a1.set_yscale("log")
    a1.set_ylim(1e-2, 20)
    a1.set_xlabel(r"$s=\sigma_v R/(2M)$")
    a1.set_ylabel(r"$R_{\rm halt}/2M$")
    a1.legend(fontsize=7, loc="lower right")
    dd = np.logspace(-2.2, -0.9, 100)
    a2.loglog(dd, (0.1 * 5 / 3 * dd) ** (-9 / 4), color=fs.PAL["blue"], label=r"lattice $N^{-4/9}$")
    a2.loglog(dd, (1.2 / (0.1 * 5 / 3 * dd)) ** 3, color=fs.PAL["red"], label=r"random $1.2N^{-1/3}$")
    a2.set_xlabel(r"$\bar\delta_{\rm ent}$")
    a2.set_ylabel(r"$N$ for $b_{\rm min}=0.1\,b_{\rm BH}$")
    a2.legend(fontsize=7)
    fs.save(fig, os.path.join(figdir, "fig_V6_dispersion_noise"))
    fs.plt.close(fig)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"),
                    help="output directory (default: NRPIC_RUN_DIR, set by nrpic-run)")
    ap.add_argument("--parts", default="V1,V2,V3,V4,V5,V6")
    ap.add_argument("--Nmax", type=int, default=128, help="largest N of the own check (full box)")
    ap.add_argument("--Ntrack", type=int, default=128, help="largest N of the track's test (octant)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    out = {}
    parts = a.parts.split(",")
    if "V2" in parts:
        part_V2(out, a.out)
    if "V1" in parts:
        part_V1(out, a.out)
    if "V3" in parts:
        part_V3(out, a.out, a.out)
    if "V4" in parts:
        part_V4(out, a.out, a.out)
    if "V6" in parts:
        part_V6(out, a.out)
    if "V5" in parts:
        part_V5(out, a.out, a.Nmax, Ntrack=a.Ntrack)
    with open(os.path.join(a.out, "verify.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=jdump)
    print(json.dumps(out, indent=1, default=jdump)[:20000])


if __name__ == "__main__":
    main()
