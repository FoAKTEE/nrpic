#!/usr/bin/env python3
"""Re-derive and check the scale estimate of brief section 3.11, last item (lines 275).

Usage: python3 -I scale_estimate.py <outdir> <repo_root>

Units G = c = 1. M = mass of the large black hole (r_g = M), m_b = total binary mass,
q = M/m_b, r_gb = m_b, a_b = binary separation. Every closed form is checked against an
independent numerical computation:

1. tidal radius r_t = a_b q^(1/3) [0911.1136 prp.tex line 88; 2404.16270 article.tex
   eq. e1.1, lines 165-176] in units of r_g: r_t/r_g = (a_b/r_gb) q^(-2/3);
2. plunge bound: a parabolic (E = 1) Schwarzschild geodesic with pericentre below the
   marginally bound radius plunges; r_mb found numerically from the effective potential
   (expected 4 M, 2404.16270 line 209), and for equatorial Kerr from the radial
   potential R(r) (closed form 2 -+ a + 2 sqrt(1 -+ a) [BACKGROUND, Bardeen, Press and
   Teukolsky 1972], checked here); then a_b/r_gb > (r_mb/M) q^(2/3);
3. Peters (1964) circular merger time of an equal-mass binary, closed form
   (5/64)(a_b/r_gb)^4 m_b against direct integration of da/dt;
4. passage times: Newtonian parabolic time (Barker) and Schwarzschild parabolic
   geodesic coordinate time from r0 to r_p, against the binary period;
5. the Newtonian restricted three-body disruption probability fit of 1804.02911
   (mnras.tex lines 371-375) mapped to r_p/r_g for q = 10;
6. published full-NR three-body configurations placed in the same plane:
   2406.11985 (massratio_table.tex lines 9-30), 2505.03934 (apssamp.tex lines 244-246),
   and core's scouting input problems/puncture/by_triple.athinput (branch
   core/multi-puncture, header lines 1-8).
Writes results.json and figures (PNG and PDF) to <outdir>.
"""
import json
import os
import sys

import numpy as np
from scipy import integrate, optimize

OUT = sys.argv[1]
ROOT = sys.argv[2]
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

os.makedirs(OUT, exist_ok=True)
R = {}

# ---------------------------------------------------------------- 1. tidal radius
def rt_over_rg(ab, q):
    """r_t / r_g with r_t = a_b q^(1/3), a_b in units of r_gb = m_b, r_g = q m_b."""
    return ab * q ** (1.0 / 3.0) / q


def ab_plunge(q, rmb=4.0):
    """Smallest a_b/r_gb with r_t >= r_mb (separation possible before the plunge)."""
    return rmb * q ** (2.0 / 3.0)


R["closed_form_check"] = {
    "rt_over_rg_formula_vs_definition_maxdiff": float(max(
        abs(rt_over_rg(ab, q) - ab * q ** (-2.0 / 3.0))
        for ab in (10., 30., 60.) for q in (4., 10., 100.))),
    "ab_min_brief": {"q10": 19, "q100": 86, "q1000": 400},
    "ab_min_computed": {f"q{q}": ab_plunge(float(q)) for q in (10, 100, 1000)},
}

# ---------------------------------------------------------------- 2. marginally bound orbits
def schw_mb():
    """E = 1, Schwarzschild: V(r) = (1-2/r)(1+L^2/r^2); V = 1 and V' = 0."""
    def eqs(x):
        r, L = x
        V = (1 - 2 / r) * (1 + L ** 2 / r ** 2)
        dV = 2 / r ** 2 * (1 + L ** 2 / r ** 2) + (1 - 2 / r) * (-2 * L ** 2 / r ** 3)
        return [V - 1.0, dV]
    sol = optimize.fsolve(eqs, [3.5, 3.8], xtol=1e-14)
    return float(sol[0]), float(sol[1])


def kerr_mb_numeric(a, prograde=True):
    """E = 1 equatorial Kerr: R(r) = [(r^2+a^2) - a L]^2 - Delta [r^2 + (L - a)^2];
    marginally bound: R = 0 = R' at the double root."""
    s = 1.0 if prograde else -1.0

    def Rf(r, L):
        D = r * r - 2 * r + a * a
        return ((r * r + a * a) - a * L) ** 2 - D * (r * r + (L - a) ** 2)

    def dR(r, L):
        D = r * r - 2 * r + a * a
        dD = 2 * r - 2
        return 2 * ((r * r + a * a) - a * L) * 2 * r - dD * (r * r + (L - a) ** 2) - D * 2 * r

    guess_r = 2 - s * a + 2 * np.sqrt(1 - s * a)
    guess_L = s * 2 * (1 + np.sqrt(1 - s * a))
    sol = optimize.fsolve(lambda x: [Rf(*x), dR(*x)], [guess_r * 1.05, guess_L * 1.05],
                          xtol=1e-14)
    return float(sol[0]), float(sol[1])


def kerr_mb_closed(a, prograde=True):
    s = 1.0 if prograde else -1.0
    return 2 - s * a + 2 * np.sqrt(1 - s * a)


r_mb, L_mb = schw_mb()
R["schwarzschild_mb"] = {"r_mb": r_mb, "L_mb": L_mb,
                         "isotropic_radius_of_r_mb": float(
                             (r_mb - 1 + np.sqrt(r_mb ** 2 - 2 * r_mb)) / 2)}
kerr = {}
spins = np.linspace(0.0, 0.99, 34)
kerr_num_pro, kerr_num_ret = [], []
for a in spins:
    rp_n, _ = kerr_mb_numeric(a, True)
    rr_n, _ = kerr_mb_numeric(a, False)
    kerr_num_pro.append(rp_n)
    kerr_num_ret.append(rr_n)
kerr_num_pro = np.array(kerr_num_pro)
kerr_num_ret = np.array(kerr_num_ret)
kerr["max_abs_diff_numeric_vs_closed_prograde"] = float(
    np.max(np.abs(kerr_num_pro - kerr_mb_closed(spins, True))))
kerr["max_abs_diff_numeric_vs_closed_retrograde"] = float(
    np.max(np.abs(kerr_num_ret - kerr_mb_closed(spins, False))))
for a in (0.3, 0.6, 0.9):
    kerr[f"a{a}"] = {"r_mb_pro": float(kerr_mb_closed(a, True)),
                     "r_mb_ret": float(kerr_mb_closed(a, False)),
                     "ab_min_q10_pro": float(ab_plunge(10., kerr_mb_closed(a, True))),
                     "ab_min_q10_ret": float(ab_plunge(10., kerr_mb_closed(a, False)))}
R["kerr_mb"] = kerr

# ---------------------------------------------------------------- 3. Peters time
def peters_closed(ab, q):
    """Merger time of an equal-mass circular binary in units of M = q m_b."""
    return (5.0 / 64.0) * ab ** 4 / q


def peters_numeric(ab, q):
    """Integrate da/dt = -(64/5) m1 m2 (m1+m2) / a^3 with m_b = 1, then convert to M."""
    m1 = m2 = 0.5
    k = 64.0 / 5.0 * m1 * m2 * (m1 + m2)
    T, _ = integrate.quad(lambda a: a ** 3 / k, 0.0, ab, epsabs=0, epsrel=1e-13)
    return T / q


R["peters"] = {"closed_ab30_q10": peters_closed(30., 10.),
               "numeric_ab30_q10": peters_numeric(30., 10.),
               "brief_value": 6.0e3}

# ---------------------------------------------------------------- 4. passage times
def t_newton_parabolic(r0, rp):
    """Newtonian parabolic orbit, time from r0 to pericentre rp (M = 1)."""
    D = np.sqrt(r0 / rp - 1.0)
    return np.sqrt(2 * rp ** 3) * (D + D ** 3 / 3.0)


def t_schw_parabolic(r0, rp):
    """Schwarzschild E = 1 geodesic with periapsis rp > 4: coordinate time and proper
    time from r0 to rp. Substitution r = rp + s^2 removes the turning-point singularity."""
    L2 = 2 * rp ** 2 / (rp - 2)

    def radial(r):
        return 1.0 - (1 - 2 / r) * (1 + L2 / r ** 2)

    def f_t(s):
        r = rp + s * s
        if s == 0.0:
            # radial(r) ~ c1 (r - rp) near rp
            h = 1e-7
            c1 = (radial(rp + h) - radial(rp)) / h
            return 2.0 / (1 - 2 / rp) / np.sqrt(c1)
        return 2 * s / (1 - 2 / r) / np.sqrt(radial(r))

    def f_tau(s):
        r = rp + s * s
        if s == 0.0:
            h = 1e-7
            c1 = (radial(rp + h) - radial(rp)) / h
            return 2.0 / np.sqrt(c1)
        return 2 * s / np.sqrt(radial(r))

    smax = np.sqrt(r0 - rp)
    t, _ = integrate.quad(f_t, 0.0, smax, limit=200, epsrel=1e-11)
    tau, _ = integrate.quad(f_tau, 0.0, smax, limit=200, epsrel=1e-11)
    return t, tau


# check: for large rp the relativistic time tends to the Newtonian one
chk = []
for rp in (50.0, 200.0, 1000.0):
    tn = t_newton_parabolic(10 * rp, rp)
    ts, _ = t_schw_parabolic(10 * rp, rp)
    chk.append({"rp": rp, "t_newton": float(tn), "t_schw": float(ts),
                "ratio": float(ts / tn)})
R["passage_check_large_rp"] = chk


def binary_period(ab, q):
    return 2 * np.pi * ab ** 1.5 / q   # in units of M


pas = []
for q, ab in ((10., 30.), (10., 20.), (10., 60.), (4., 20.)):
    rt = rt_over_rg(ab, q)
    for f0 in (3.0, 4.0, 5.0):
        r0 = f0 * rt
        for rp in (4.5, 6.0, 8.0, 10.0, 13.0):
            if rp >= r0:
                continue
            ts, taus = t_schw_parabolic(r0, rp)
            pas.append({"q": q, "ab": ab, "rt": float(rt), "r0_over_rt": f0, "r0": float(r0),
                        "rp": rp, "D": float(rp / rt),
                        "t_in_schw": float(ts), "t_in_newton": float(t_newton_parabolic(r0, rp)),
                        "run_time_in_out": float(2 * ts),
                        "P_binary": float(binary_period(ab, q)),
                        "v_b": float(1 / np.sqrt(ab)),
                        "v_ej_scale": float(q ** (1 / 6) / np.sqrt(ab))})
R["passages"] = pas
# the brief's "few hundred GM/c^3 of one passage"
fid = [p for p in pas if p["q"] == 10. and p["ab"] == 30. and p["rp"] == 6.0]
R["fiducial_q10_ab30_rp6"] = fid

# ---------------------------------------------------------------- 5. disruption probability
A = [0.8830, -0.0809, -1.0541, 1.5377, -0.9249, 0.1881]   # 1804.02911 mnras.tex l. 373-374


def p_dis(D):
    D = np.asarray(D, dtype=float)
    p = sum(a * D ** k for k, a in enumerate(A))
    return np.where(D < 2.1, np.clip(p, 0, 1), 0.0)


R["p_dis_fit"] = {"P(0)": float(p_dis(0.0)), "P(1)": float(p_dis(1.0)),
                  "P(2.09)": float(p_dis(2.09)), "D_max": 2.1}
q = 10.0
R["scan_q10"] = {}
for ab in (20., 30., 60.):
    rt = rt_over_rg(ab, q)
    R["scan_q10"][f"ab{int(ab)}"] = {"rt_over_rg": float(rt), "rp_max_disruption": float(2.1 * rt),
                                    "rp_window": [4.0, float(2.1 * rt)]}

# ---------------------------------------------------------------- 6. published configurations
# 2406.11985 massratio_table.tex: columns 3BH1q8, 3BH2q8, 3BH1q18, 3BH2q18
pub = []
for name, m1, m2, m3, d, Dist in (("3BH1q8", 0.09997350, 0.09996202, 0.79961960, 1.97912096, 12.9299129),
                                  ("3BH2q8", 0.09998022, 0.10000287, 0.79964496, 1.97912096, 12.9311219),
                                  ("3BH1q18", 0.04997869, 0.04997149, 0.90002248, 0.98956048, 11.9614515),
                                  ("3BH2q18", 0.04997759, 0.04998916, 0.90002969, 0.98956048, 11.9618252)):
    mb = m1 + m2
    qq = m3 / mb
    ab = d / mb
    rt = rt_over_rg(ab, qq)
    pub.append({"source": "2406.11985 massratio_table.tex", "name": name, "q": qq, "ab_over_rgb": ab,
                "D_over_rg": Dist / m3, "rt_over_rg": rt, "D_over_rt": Dist / m3 / rt,
                "orbit": "bound quasi-circular outer orbit"})
# 2505.03934: all masses equal, binary separation 11.9718 M with M = total of one binary
pub.append({"source": "2505.03934 apssamp.tex l. 246", "name": "BSS (equal masses)", "q": 0.5,
            "ab_over_rgb": 11.9718, "orbit": "hyperbolic binary-single scattering"})
# core scouting input by_triple.athinput: binary 0.5+0.5 separation 10, heavy 10,
# Newtonian pericentre 30 (code units; heavy mass 10)
pub.append({"source": "core/multi-puncture problems/puncture/by_triple.athinput l. 1-8",
            "name": "core test 3", "q": 10.0, "ab_over_rgb": 10.0, "rp_over_rg": 3.0,
            "rt_over_rg": rt_over_rg(10.0, 10.0), "orbit": "Newtonian parabolic, r_p = 30 = 3 M_heavy"})
R["published"] = pub

with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(R, f, indent=1)

# ================================================================= figures
fs.use_style()

# Figure 1: left, the (q, a_b) plane; right, time scales for q = 10
fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.5))
ax = fig.add_axes([0.09, 0.14, 0.38, 0.80])
qq = np.logspace(0, 3.2, 200)
ax.plot(qq, ab_plunge(qq), **fs.GUIDE, label=r"$r_t = 4\,r_g$ (Schwarzschild plunge)")
ax.plot(qq, ab_plunge(qq, kerr_mb_closed(0.9, True)), color=fs.PAL["green"], lw=1.0, ls=":",
        label=r"$r_t = r_{\rm mb}$, $a=0.9$ pro / retro")
ax.plot(qq, ab_plunge(qq, kerr_mb_closed(0.9, False)), color=fs.PAL["green"], lw=1.0, ls=":")
for rr, lab in ((10.0, r"$r_t=10\,r_g$"), (30.0, r"$r_t=30\,r_g$")):
    ax.plot(qq, rr * qq ** (2 / 3), **fs.MASK_LINE)
    ax.text(1.25, rr * 1.25 ** (2 / 3) * 1.15, lab, color="grey", fontsize=8)
ax.fill_between([10, 30], [20, 20], [60, 60], color=fs.PAL["blue"], alpha=0.15, lw=0,
                label="brief's full-NR range")
ax.plot([10, 100, 1000], [19, 86, 400], "o", color=fs.PAL["blue"], ms=5, label="brief: 19, 86, 400")
ax.plot([10, 100, 1000], [ab_plunge(10.), ab_plunge(100.), ab_plunge(1000.)], "x",
        color=fs.PAL["red"], ms=6, label="recomputed")
p18 = [p for p in pub if p["name"].startswith("3BH")]
ax.plot([p["q"] for p in p18], [p["ab_over_rgb"] for p in p18], "s", color=fs.PAL["orange"],
        ms=5, mfc="none", label="2406.11985 (bound, $D/r_t$=4-6)")
ax.plot([10.0], [10.0], "^", color=fs.PAL["yellow"], ms=6, mfc="none", label="core test 3")
ax.plot([10.0, 4.0], [30.0, 20.0], "*", color=fs.PAL["red"], ms=9, label="F fiducials")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1, 1500)
ax.set_ylim(3, 1000)
ax.set_xlabel(r"$q = M/m_b$")
ax.set_ylabel(r"$a_b / r_{gb}$")
ax.legend(loc="upper left", fontsize=7, ncol=1)

ax2 = fig.add_axes([0.58, 0.14, 0.40, 0.80])
abv = np.logspace(np.log10(10), np.log10(100), 100)
ax2.plot(abv, peters_closed(abv, 10.), color=fs.PAL["blue"], label="Peters merger time (closed form)")
abn = np.array([10, 20, 30, 45, 60, 90])
ax2.plot(abn, [peters_numeric(a, 10.) for a in abn], "x", color=fs.PAL["red"], label="Peters, integrated")
ax2.plot(abv, binary_period(abv, 10.), color=fs.PAL["green"], label="binary period $P_b$")
# run time in and out from r0 = 4 r_t to r_p = 6 r_g (where r_t > 6)
abp = abv[rt_over_rg(abv, 10.) > 6.5]
ax2.plot(abp, [2 * t_schw_parabolic(4 * rt_over_rg(a, 10.), 6.0)[0] for a in abp],
         color=fs.PAL["orange"], label=r"passage in+out, $r_0=4r_t$, $r_p=6r_g$")
ax2.axvline(30, **fs.MASK_LINE)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel(r"$a_b / r_{gb}$  ($q=10$)")
ax2.set_ylabel(r"time  $[GM/c^3]$")
ax2.legend(loc="upper left", fontsize=7)
fs.save(fig, os.path.join(OUT, "fig_scale_plane"))
plt.close(fig)

# Figure 2: marginally bound radius against spin, numeric vs closed form; plunge-bound check
fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.0))
ax = fig.add_axes([0.16, 0.16, 0.80, 0.78])
sp = np.linspace(0, 0.99, 200)
ax.plot(sp, kerr_mb_closed(sp, True), color=fs.PAL["blue"], label="closed form, prograde")
ax.plot(sp, kerr_mb_closed(sp, False), color=fs.PAL["blue"], ls="--", label="closed form, retrograde")
ax.plot(spins, kerr_num_pro, "x", color=fs.PAL["red"], ms=4, label="numerical root of $R=R'=0$")
ax.plot(spins, kerr_num_ret, "x", color=fs.PAL["red"], ms=4)
ax.plot([0.0], [r_mb], "o", color=fs.PAL["red"], mfc="none", ms=7, label="Schwarzschild, $V=1$, $V'=0$")
ax.set_xlabel(r"spin $a/M$")
ax.set_ylabel(r"$r_{\rm mb}/M$ (Boyer-Lindquist)")
ax.set_ylim(1, 7.8)
ax.legend(loc="upper left", fontsize=7, ncol=1)
fs.save(fig, os.path.join(OUT, "fig_rmb_check"))
plt.close(fig)

# Figure 3: Newtonian restricted disruption probability mapped to r_p/r_g, q = 10
fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.0))
ax = fig.add_axes([0.16, 0.16, 0.80, 0.78])
rp = np.linspace(1, 30, 600)
for ab, c in ((20., fs.PAL["green"]), (30., fs.PAL["red"]), (60., fs.PAL["orange"])):
    rt = rt_over_rg(ab, 10.)
    ax.plot(rp, p_dis(rp / rt), color=c, label=rf"$a_b={int(ab)}\,r_{{gb}}$ ($r_t={rt:.1f}\,r_g$)")
ax.axvspan(1, 4, color="grey", alpha=0.25, lw=0)
ax.text(1.3, 0.05, "plunge\n(a=0)", fontsize=8)
ax.axvline(kerr_mb_closed(0.9, True), color=fs.PAL["blue"], lw=1.0, ls=":",
           label=r"$r_{\rm mb}$, $a=0.9$ pro / retro")
ax.axvline(kerr_mb_closed(0.9, False), color=fs.PAL["blue"], lw=1.0, ls=":")
ax.set_xlim(1, 30)
ax.set_ylim(0, 1.0)
ax.set_xlabel(r"pericentre $r_p / r_g$  ($q=10$)")
ax.set_ylabel(r"$P_{\rm dis}$ (Newtonian, restricted)")
ax.legend(loc="upper right", fontsize=7)
fs.save(fig, os.path.join(OUT, "fig_pdis_q10"))
plt.close(fig)

print(json.dumps({k: R[k] for k in ("closed_form_check", "schwarzschild_mb", "peters",
                                     "p_dis_fit", "scan_q10")}, indent=1))
print(json.dumps(R["kerr_mb"], indent=1))
print(json.dumps(R["passage_check_large_rp"], indent=1))
print(json.dumps(R["fiducial_q10_ab30_rp6"], indent=1))
print(json.dumps(R["published"], indent=1))
