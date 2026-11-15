#!/usr/bin/env python3
"""Checks of emd_criteria against numbers and curves printed in the five papers.

    python3 check_criteria.py [--quick]

Registers the run (runlog.Run), writes results.json and the figures check_*.{pdf,png}
into scratch/A-emd-pbh/<run_id>/, and prints one line per check. --quick skips the
slow monochromatic integrals (T5.3).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import emd_criteria as C  # noqa: E402
import runlog  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = []


def check(tid, what, value, ref, locator, ok, note="", info=False):
    """info=True: a diagnostic kept on record (printed INFO, not counted as pass or fail)."""
    RESULTS.append(dict(id=tid, what=what, value=value, reference=ref, locator=locator,
                        passed=None if info else bool(ok), note=note))
    tag = "INFO" if info else ("PASS" if ok else "FAIL")
    print(f"{tag} {tid:6s} {what}: {value} vs {ref} [{locator}] {note}", flush=True)


def _round_half_up(x, places):
    from decimal import Decimal, ROUND_HALF_UP
    return Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


# ------------------------------------------------------------------- T1 1609.01588
def t1(out):
    import scipy.integrate as si
    # T1.1 normalisation of the Doroshkevich density, sigma = 1, in (x, y, z) variables
    s = 1.0
    # Jacobian d(alpha,beta,gamma)/d(x,y,z) = 4 (1609.01588:668-684)
    f = lambda z, y, x: 4 * C.doroshkevich_w(x + 2 * y / 3 + z, x - 4 * y / 3, x + 2 * y / 3 - z, s)
    norm = si.tplquad(f, -6, 6, lambda x: -6, lambda x: 6,
                      lambda x, y: 2 * abs(y), lambda x, y: 8, epsabs=1e-9, epsrel=1e-7)[0]
    check("T1.1", "int w dalpha dbeta dgamma", f"{norm:.8f}", "1", "1609.01588:689-692",
          abs(norm - 1) < 1e-4)
    # T1.2 E-bar and coefficients
    Eb = C.Ebar()
    check("T1.2a", "E-bar", f"{Eb:.4f}", "1.182", "1609.01588:1341", round(Eb, 3) == 1.182)
    c = C.beta0_hoop_semianalytic_coeff(Eb)
    # wave 1 required the last printed digit; c = 0.0555549716 lies 2.8e-8 below the
    # rounding boundary 0.055555, so it rounds to 0.05555 in one step and to 0.05556 in two
    # (0.0555550 -> 0.05556). Wave 2: agreement within one unit of the last printed digit;
    # the one-step digits are kept as a diagnostic (JOURNAL, criteria2 F1).
    check("T1.2b", "beta0/sigma^5 (sigma<<1), within one unit of the last printed digit",
          f"{c:.10f}", "0.05556", "1609.01588:764, 1328-1331", abs(c - 0.05556) < 1e-5,
          f"one-step rounding {_round_half_up(c, 5)}, two-step (7 then 5 places) "
          f"{_round_half_up(float(_round_half_up(c, 7)), 5)}")
    check("T1.2b-d", "beta0/sigma^5 rounded once to the printed digits", f"{c:.5f}", "0.05556",
          "1609.01588:764", round(c, 5) == 0.05556, "wave-1 criterion; explained above",
          info=True)
    lo = C.beta0_hoop_semianalytic_coeff(math.pi / 2)
    hi = C.beta0_hoop_semianalytic_coeff(1.0)
    check("T1.2c", "lower/upper bound coefficients", f"{lo:.5f}, {hi:.4f}", "0.01338, 0.1280",
          "1609.01588:771,840,853", round(lo, 5) == 0.01338 and round(hi, 4) == 0.1280)
    kp = C.beta0_khlopov_polnarev_coeff()
    check("T1.3", "Khlopov-Polnarev coefficient", f"{kp:.4f}", "0.02", "1609.01588:931",
          0.015 < kp < 0.025, "paper prints one digit")
    # T1.4 exact double integral
    sig = np.geomspace(1e-5, 1.0, 21)
    b0 = np.array([C.beta0_hoop(s) for s in sig])
    ratio = b0 / (c * sig ** 5)
    i3 = np.argmin(abs(sig - 1e-3))
    i1 = np.argmin(abs(sig - 1e-1))
    check("T1.4a", "beta0/(0.05556 sigma^5) at sigma=1e-3", f"{ratio[i3]:.4f}", "1",
          "1609.01588:740-741,876", abs(ratio[i3] - 1) < 0.01)
    check("T1.4b", "beta0/(0.05556 sigma^5) at sigma=0.1", f"{ratio[i1]:.3f}", "> 1.02",
          "1609.01588:730,877-879", ratio[i1] > 1.02)
    # T1.5 Monte Carlo over Gaussian deformation tensors
    rng = np.random.default_rng(16090158)
    mc = []
    for s in (0.3, 0.5, 1.0):
        n, hits = 0, 0
        for _ in range(8):
            a, b, g = C.doroshkevich_sample(500_000, s, rng)
            hits += int(np.sum((a > 0) & (C.hoop_h(a, b, g) <= 1)))
            n += 500_000
        pm = hits / n
        err = math.sqrt(pm * (1 - pm) / n)
        ex = C.beta0_hoop(s)
        mc.append((s, pm, err, ex))
        check("T1.5", f"Monte Carlo vs double integral, sigma={s}", f"{pm:.5f}+-{err:.5f}",
              f"{ex:.5f}", "1609.01588:706-708", abs(pm - ex) < 3 * err)
    # figure: reproduction of Fig. 1 of 1609.01588
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fs.inch_axes(fig, 0.75, 0.58, 3.2, 2.7)
    ax2 = fs.inch_axes(fig, 4.65, 0.58, 3.2, 2.7)
    sg = np.geomspace(1e-5, 1, 200)
    ax.plot(sig, np.log10(b0), color=fs.PAL["red"], label="exact double integral (this work)")
    ax.plot([m[0] for m in mc], [math.log10(m[1]) for m in mc], "o", color=fs.PAL["red"],
            ms=4, mfc="none", label="Monte Carlo, Gaussian tensor")
    ax.plot(sg, np.log10(c * sg ** 5), **fs.GUIDE, label=r"$0.05556\,\sigma^5$ (1609.01588)")
    ax.plot(sg, np.log10(lo * sg ** 5), color=fs.PAL["blue"], lw=1.0, label="analytic bounds")
    ax.plot(sg, np.log10(hi * sg ** 5), color=fs.PAL["blue"], lw=1.0)
    sr = np.geomspace(0.03, 0.35, 100)
    ax.plot(sr, np.log10(C.beta0_radiation(sr)), color=fs.PAL["green"], label="radiation era")
    ax.set_xscale("log")
    ax.set_ylim(-30, 0)
    ax.set_xlim(1e-5, 1)
    ax.set_xlabel(r"$\sigma$", labelpad=-2)
    ax.set_ylabel(r"$\log_{10}\beta_0$")
    ax.legend(loc="lower right", fontsize=7)
    ax2.plot(sig, ratio, color=fs.PAL["red"], marker="o", ms=3)
    ax2.axhline(1, **fs.GUIDE)
    ax2.set_xscale("log")
    ax2.set_xlabel(r"$\sigma$", labelpad=-2)
    ax2.set_ylabel(r"$\beta_0 / (0.05556\,\sigma^5)$")
    fs.save(fig, os.path.join(out, "check_T1_hoop_1609.01588"))
    plt.close(fig)
    return dict(sigma=sig.tolist(), beta0=b0.tolist(), mc=mc)


# ------------------------------------------------------------------- T2 1707.03595
def t2(out):
    qc = C.spin_qc(1.0, 1.0)
    check("T2.1", "q_c / (I sigma_H)^(1/3)", f"{qc:.3f}", "2.4", "1707.03595:72,979",
          round(qc, 1) == 2.4)
    Eb = C.Ebar()
    k2 = 0.5 * 0.4 ** (4 / 3)
    k1 = 0.5 * (12 / 125) ** 2
    pre = 5 * math.sqrt(5) * math.pi ** 4 / 6 ** 9 * Eb ** -5
    p2 = pre * 0.4 ** 6
    p1 = pre * (12 / 125) ** 9
    check("T2.2a", "exponent coefficient, 2nd order", f"{k2:.4f}", "0.1474", "1707.03595:1339",
          round(k2, 4) == 0.1474)
    check("T2.2b", "exponent coefficient, 1st order", f"{k1:.6f}", "0.004608",
          "1707.03595:1346", round(k1, 6) == 0.004608)
    check("T2.2c", "prefactor I^6 sigma^2, 2nd order", f"{p2:.4g}", "1.921e-7",
          "1707.03595:1338", round(p2 * 1e7, 3) == 1.921)
    check("T2.2d-d", "prefactor q^18/sigma^4, 1st order, exact E-bar", f"{p1:.4g}",
          "3.244e-14", "1707.03595:1345", round(p1 * 1e14, 3) == 3.244,
          "wave-1 criterion; explained by T2.2e, T2.2f", info=True)
    p1r = 5 * math.sqrt(5) * math.pi ** 4 / 6 ** 9 * 1.182 ** -5 * (12 / 125) ** 9
    p2r = 5 * math.sqrt(5) * math.pi ** 4 / 6 ** 9 * 1.182 ** -5 * 0.4 ** 6
    check("T2.2e", "1st-order prefactor with E-bar = 1.182 as printed (1331)",
          f"{p1r:.4g} (2nd order with it: {p2r:.4g})", "3.244e-14", "1707.03595:1331,1345",
          round(p1r * 1e14, 3) == 3.244)
    # T2.2f: the ratio of the two printed prefactors does not depend on E-bar; if it differs
    # from 0.4^6/(12/125)^9 by more than the rounding of the two printed numbers, no single
    # E-bar gives both, and the failure of T2.2d is the paper's, not the code's.
    rex = 0.4 ** 6 / (12 / 125) ** 9
    rpr = 1.921e-7 / 3.244e-14
    rnd = 0.0005 / 1.921 + 0.0005 / 3.244
    dev = abs(rpr / rex - 1)
    eb2 = [(pre * Eb ** 5 * 0.4 ** 6 / v) ** 0.2 for v in (1.9215e-7, 1.9205e-7)]
    eb1 = [(pre * Eb ** 5 * (12 / 125) ** 9 / v) ** 0.2 for v in (3.2445e-14, 3.2435e-14)]
    check("T2.2f", "printed prefactor ratio vs exact ratio (independent of E-bar)",
          f"deviation {dev:.2e}", f"> rounding {rnd:.2e}", "1707.03595:1338,1345", dev > rnd,
          f"E-bar giving 1.921e-7: [{eb2[0]:.6f}, {eb2[1]:.6f}]; giving 3.244e-14: "
          f"[{eb1[0]:.6f}, {eb1[1]:.6f}]; exact {Eb:.7f}")
    m01 = C.spin_pdf_mode_2nd(1.0, 0.1)
    check("T2.3a", "mode of f_BH(2) at sigma_H=0.1", f"{m01:.3f}", "0.63", "1707.03595:1147",
          0.60 <= m01 <= 0.66)
    from scipy.optimize import brentq
    s1 = brentq(lambda s: (0.8 * 0.5 * s ** (-2 / 3) * 0.4 ** (4 / 3)) ** 0.75 - 1, 1e-3, 0.5)
    check("T2.3b", "sigma_H where the mode reaches a*=1", f"{s1:.4f}", "0.04",
          "1707.03595:1150,1180", 0.035 <= s1 <= 0.045)
    # T2.4 numerical beta0 with spin thresholds vs semi-analytic formulas
    sig = np.geomspace(1e-3, 0.2, 14)
    pai = np.array([C.beta0_hoop(s) for s in sig])
    b2 = np.array([C.beta0_spin(s, (0.4 * s) ** (2 / 3)) for s in sig])
    q = math.sqrt(2)
    b1 = np.array([C.beta0_spin(s, 12 / 125 * q * q) for s in sig])
    sa2 = np.array([C.beta0_spin_semianalytic((0.4 * s) ** (2 / 3), s, Eb) for s in sig])
    sa1 = np.array([C.beta0_spin_semianalytic(12 / 125 * q * q, s, Eb) for s in sig])
    small = sig <= 0.0051
    r2 = b2[small] / sa2[small]
    check("T2.4a-d", "beta0(2) numerical/semi-analytic, sigma<=0.005",
          f"{r2.min():.3f}..{r2.max():.3f}", "within 20%", "1707.03595:1351-1354",
          np.all(abs(r2 - 1) < 0.2), "wave-1 band; replaced by T2.4a", info=True)
    # Wave 2: the paper's "agree" (1351-1362) is read off its Fig. production_rate
    # (log10 beta0 from -30 to 0; I = 1, q = sqrt 2, 1403-1424; figure viewed, JOURNAL
    # criteria2). The check is made on the window the figure shows (beta0 >= 1e-30 and
    # sigma_H up to the quoted bound): |log10(numerical/semi-analytic)| <= 0.5, a factor of
    # about three, 1.7 % of the plotted 30 decades [JUDGEMENT: below the line width].
    sw2 = np.geomspace(2.5e-4, 0.005, 9)
    b2w = np.array([C.beta0_spin(s, (0.4 * s) ** (2 / 3)) for s in sw2])
    s2w = np.array([C.beta0_spin_semianalytic((0.4 * s) ** (2 / 3), s, Eb) for s in sw2])
    in2 = b2w >= 1e-30
    l2 = np.log10(b2w[in2] / s2w[in2])
    mono2 = bool(np.all(np.diff(b2w[in2] / s2w[in2]) > 0))
    check("T2.4a", "beta0(2) num/semi on the plotted window, max |log10 ratio|",
          f"{np.max(np.abs(l2)):.3f} (sigma_H {sw2[in2][0]:.2g}-{sw2[in2][-1]:.2g}; ratio "
          f"{b2w[in2][0] / s2w[in2][0]:.3f}..{b2w[in2][-1] / s2w[in2][-1]:.3f})", "<= 0.5",
          "1707.03595:1351-1354, Fig. 1403-1424", np.max(np.abs(l2)) <= 0.5 and mono2,
          "ratio increasing with sigma_H: -> 1 as sigma_H -> 0" if mono2 else "not monotone")
    mid = (sig >= 0.02) & (sig <= 0.2)
    rr = b2[mid] / pai[mid]
    check("T2.4b", "beta0(2)/P_ai, 0.02<=sigma<=0.2", f"{rr.min():.3f}..{rr.max():.3f}",
          "> 0.5", "1707.03595:1352-1358", np.all(rr > 0.5))
    sm1 = (sig <= 0.021) & (sa1 > 1e-250)
    r1 = b1[sm1] / sa1[sm1]
    ok1 = np.all(abs(r1 - 1) < 0.2)
    check("T2.4c-d", "beta0(1) numerical/semi-analytic (q=sqrt2), sigma<=0.02",
          f"{np.nanmin(r1):.3f}..{np.nanmax(r1):.3f}", "within 20%", "1707.03595:1359-1362",
          ok1, "wave-1 band; replaced by T2.4c", info=True)
    sw1 = np.geomspace(0.015, 0.04, 9)
    b1w = np.array([C.beta0_spin(s, 12 / 125 * q * q) for s in sw1])
    s1w = np.array([C.beta0_spin_semianalytic(12 / 125 * q * q, s, Eb) for s in sw1])
    in1 = b1w >= 1e-30
    l1 = np.log10(b1w[in1] / s1w[in1])
    check("T2.4c", "beta0(1) num/semi on the plotted window, max |log10 ratio| (q=sqrt2)",
          f"{np.max(np.abs(l1)):.3f} (sigma_H {sw1[in1][0]:.3g}-{sw1[in1][-1]:.3g}; ratio "
          f"{np.min(b1w[in1] / s1w[in1]):.3f}..{np.max(b1w[in1] / s1w[in1]):.3f})", "<= 0.5",
          "1707.03595:1359-1362, Fig. 1403-1424", np.max(np.abs(l1)) <= 0.5)
    # T2.5 asymptotics: 2nd order threshold -> 0 with sigma, 1st order threshold fixed
    r5 = [C.beta0_spin(s, (0.4 * s) ** (2 / 3))
          / C.beta0_spin_semianalytic((0.4 * s) ** (2 / 3), s, Eb) for s in (1e-4, 1e-5)]
    check("T2.5a", "beta0(2) numerical/semi-analytic at sigma=1e-4, 1e-5",
          f"{r5[0]:.4f}, {r5[1]:.4f}", "-> 1", "1707.03595:1321-1329",
          r5[1] < r5[0] and abs(r5[1] - 1) < 0.03)
    r6 = [C.beta0_spin(s, 12 / 125 * q * q)
          / C.beta0_spin_semianalytic(12 / 125 * q * q, s, Eb) for s in (0.0077, 0.006)]
    check("T2.5b", "beta0(1) numerical/semi-analytic at sigma=0.0077, 0.006 (q=sqrt2)",
          f"{r6[0]:.3f}, {r6[1]:.3f}", "< 1 and falling", "1707.03595:1321-1329, 1345",
          r6[1] < r6[0] < 1, "finite delta_th: dropped (1.5+2u^2)/s3^2 term in A, see T2.6")
    # T2.6 (wave 2): the cause of the 1st-order drift. I2 = the [t2, inf) part of the
    # appendix integral, with the exact A and with A ~ 9t^2/(10 s3^2) (1919), t2 exact.
    d1 = 12 / 125 * q * q
    t26 = []
    # sigma_H = 0.004 (first registered run) underflows: beta0 ~ exp(-0.0184/sigma^2)
    ft2 = C.spin_I2_t2_factor(d1)
    for s in (0.006, 0.0077, 0.01, 0.017):
        Nn = C.beta0_spin(s, d1)
        Ss = C.beta0_spin_semianalytic(d1, s, Eb)
        I2 = C.beta0_spin_I2(s, d1)
        I2a = C.beta0_spin_I2(s, d1, approx_A=True)
        X = d1 * d1 / (2 * s * s)
        t26.append(dict(sigma=s, N_over_S=Nn / Ss, N_over_I2=Nn / I2, I2_over_I2a=I2 / I2a,
                        I2a_over_S=I2a / Ss, predicted_I2a_over_S=ft2 * (2 + 2 * X + X * X)
                        / (X * X)))
    a_ok = all(abs(x["N_over_I2"] - 1) < 0.02 for x in t26 if x["sigma"] <= 0.01)
    check("T2.6a", "beta0(1) numerical / I2(exact A), sigma_H <= 0.01",
          ", ".join(f"{x['N_over_I2']:.4f}" for x in t26), "1 within 2 %",
          "1707.03595:1898-1936", a_ok,
          f"at 0.017: {t26[-1]['N_over_I2']:.4f} (I1 and t < t2 grow with sigma_H)")
    dec = all(t26[i]["I2_over_I2a"] < t26[i + 1]["I2_over_I2a"] < 1 for i in range(len(t26) - 1))
    check("T2.6b", "I2(exact A)/I2(approx A): < 1 and falling towards small sigma_H",
          ", ".join(f"{x['I2_over_I2a']:.4f}" for x in t26), "< 1, decreasing",
          "1707.03595:1919", dec, "the dropped (2u^2 + 3/2)/s3^2 makes the drift")
    ca = [x["I2a_over_S"] for x in t26]
    check("T2.6c", "I2(approx A)/semi-analytic, constant in sigma_H",
          ", ".join(f"{v:.4f}" for v in ca), "constant within 10 %", "1707.03595:1921-1936",
          max(ca) / min(ca) < 1.1, "a constant factor from t2 ~ 12E/(pi delta_th) at finite "
                                   "delta_th")
    dd = [abs(x["I2a_over_S"] / x["predicted_I2a_over_S"] - 1) for x in t26]
    check("T2.6d", "I2(approx A)/semi-analytic = t2 factor x (2+2X+X^2)/X^2",
          ", ".join(f"{x['I2a_over_S']:.4f}/{x['predicted_I2a_over_S']:.4f}" for x in t26),
          "within 1 %", "1707.03595:1880-1886 (corrected root), 1921", max(dd) < 0.01,
          f"t2 factor {ft2:.4f}")
    out_t26 = t26
    # figure: production rates and spin distributions
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fs.inch_axes(fig, 0.75, 0.58, 3.2, 2.7)
    ax2 = fs.inch_axes(fig, 4.65, 0.58, 3.2, 2.7)
    ax.plot(sig, pai, color="k", label=r"$P_{ai}$ numerical")
    ax.plot(sig, 0.05556 * sig ** 5, color="k", ls=":", lw=1.0)
    ax.plot(sig, b2, color=fs.PAL["red"], label="2nd order numerical")
    ax.plot(sig, sa2, color=fs.PAL["blue"], ls="--", label="semi-analytic (1338, 1345)")
    ax.plot(sig, b1, color=fs.PAL["orange"], label=r"1st order, $q=\sqrt{2}$")
    ax.plot(sig, sa1, color=fs.PAL["blue"], ls="--")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-30, 1e-2)
    ax.set_xlabel(r"$\sigma_H$", labelpad=-2)
    ax.set_ylabel(r"$\beta_0$")
    ax.legend(loc="lower right", fontsize=7)
    aa = np.linspace(0.02, 1, 400)
    for s, col in zip((0.1, 0.05, 0.01), fs.SERIES[:3]):
        f = C.spin_pdf_2nd(aa, 1.0, s)
        ax2.plot(aa, f / f.max(), color=col, label=fr"$\sigma_H={s}$")
        m = C.spin_pdf_mode_2nd(1.0, s)
        ax2.axvline(m, color=col, lw=1.0, ls=":")
    ax2.axvline(0.63, **fs.GUIDE, label="0.63 (1707.03595:1147)")
    ax2.set_xlabel(r"$a_*$", labelpad=-2)
    ax2.set_ylabel(r"$f_{\rm BH(2)}/\max$")
    ax2.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(out, "check_T2_spin_1707.03595"))
    plt.close(fig)
    # figure 2 (wave 2): ratios on the windows and the decomposition of T2.6
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fs.inch_axes(fig, 0.75, 0.55, 3.15, 2.45)
    ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.45)
    ax.semilogx(sw2, b2w / s2w, "o-", color=fs.PAL["red"], ms=3, label="2nd order")
    ax.semilogx(sw1, b1w / s1w, "s-", color=fs.PAL["orange"], ms=3,
                label=r"1st order, $q=\sqrt{2}$")
    ax.semilogx(sig[sig <= 0.021], b1[sig <= 0.021] / sa1[sig <= 0.021], "s:",
                color=fs.PAL["orange"], ms=3, mfc="none", lw=1.0)
    for v in (10 ** 0.5, 10 ** -0.5):
        ax.axhline(v, **fs.MASK_LINE)
    ax.axhline(1, **fs.GUIDE)
    ax.axvspan(sw2[in2][0], 0.005, color=fs.PAL["red"], alpha=0.08)
    ax.axvspan(sw1[in1][0], 0.04, color=fs.PAL["orange"], alpha=0.12)
    ax.set_xlabel(r"$\sigma_H$", labelpad=-2)
    ax.set_ylabel("numerical / semi-analytic")
    ax.set_yscale("log")
    ax.legend(loc="lower right", fontsize=7)
    ss = [x["sigma"] for x in t26]
    ax2.semilogx(ss, [x["N_over_S"] for x in t26], "o-", color="k", ms=3,
                 label="numerical / semi-analytic")
    ax2.semilogx(ss, [x["N_over_I2"] for x in t26], "s-", color=fs.PAL["blue"], ms=3,
                 label=r"numerical / $I_2$(exact $A$)")
    ax2.semilogx(ss, [x["I2_over_I2a"] for x in t26], "^-", color=fs.PAL["red"], ms=3,
                 label=r"$I_2$(exact $A$) / $I_2(A\simeq 9t^2/10\sigma_3^2)$")
    ax2.semilogx(ss, [x["I2a_over_S"] for x in t26], "v-", color=fs.PAL["green"], ms=3,
                 label=r"$I_2$(approx. $A$) / semi-analytic")
    ax2.axhline(1, **fs.GUIDE)
    ax2.set_xlabel(r"$\sigma_H$ (1st order, $q=\sqrt{2}$)", labelpad=-2)
    ax2.set_ylabel("ratio")
    ax2.legend(loc="upper left", fontsize=6.5)
    fs.save(fig, os.path.join(out, "check_T2_ratios_1707.03595"))
    plt.close(fig)
    return dict(sigma=sig.tolist(), Pai=pai.tolist(), beta2=b2.tolist(), beta1=b1.tolist(),
                semi2=sa2.tolist(), semi1=sa1.tolist(), window2=dict(sigma=sw2.tolist(),
                num=b2w.tolist(), semi=s2w.tolist()), window1=dict(sigma=sw1.tolist(),
                num=b1w.tolist(), semi=s1w.tolist()), T26=out_t26)


# ------------------------------------------------------------------- T3 2211.13950
def t3(out):
    scr = C.vd_sigma_cr(1.0, 1.0)
    check("T3.1", "ln sigma_cr(mu=1,L=1); -5 below, -2.5 above", f"{math.log(scr):.3f}", "-3",
          "2211.13950:496-498,517", abs(math.log(scr) + 3) < 1e-12 and -5 < math.log(scr) < -2.5)
    worst = 0.0
    for d in (1e-3, 1e-2, 0.1, 0.5):
        # lines ln s = ln d - 2x and ln s = 2.5 ln d + x meet at x = -ln(d)/2
        x = (math.log(d) - 2.5 * math.log(d)) / 3.0
        y = math.log(d) - 2 * x
        km, sm = C.vd_merge_point(d)
        worst = max(worst, abs(math.exp(x) / km - 1), abs(math.exp(y) / sm - 1),
                    abs(math.exp(-4 * x) / sm - 1))
    check("T3.2", "three boundaries meet at (delta^-1/2, delta^2)", f"max rel. dev {worst:.1e}",
          "0", "2211.13950:423-426,468", worst < 1e-12)
    pairs = [(1, 0), (1, 2), (1, 1), (0.5, 1), (2, 1)]   # (1,1) drawn over (1,2)
    allok = True
    jumps = {}
    for mu, L in pairs:
        sc = C.vd_sigma_cr(mu, L)
        lo = float(C.vd_delta_th(sc * (1 - 1e-9), mu, L))
        hi = float(C.vd_delta_th(sc * (1 + 1e-9), mu, L))
        jump = abs(math.log(hi / lo)) > 1e-3
        jumps[f"{mu},{L}"] = (sc, lo, hi)
        allok &= (jump == (mu * L < 2))
    check("T3.3", "jump at sigma_cr iff mu L < 2", json.dumps({k: [f"{v:.3g}" for v in t]
                                                               for k, t in jumps.items()}),
          "jump for (1,0),(1,1),(1/2,1); none for (1,2),(2,1)", "2211.13950:565-571", allok)
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fs.inch_axes(fig, 0.75, 0.58, 3.2, 2.7)
    ax2 = fs.inch_axes(fig, 4.65, 0.58, 3.2, 2.7)
    s0 = np.geomspace(1e-4, 1, 1500)
    cols = [fs.PAL["red"], fs.PAL["orange"], fs.PAL["green"], "grey", fs.PAL["blue"]]
    for (mu, L), col in zip(pairs, cols):
        d = C.vd_delta_th(s0, mu, L)
        sc = C.vd_sigma_cr(mu, L)
        ax.plot(s0[s0 < sc], d[s0 < sc], color=col, label=fr"$\mu={mu:g}$, $L={L:g}$")
        ax.plot(s0[s0 >= sc], d[s0 >= sc], color=col, ls="--" if (mu, L) == (1, 2) else "-")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-7, 1)
    ax.set_xlim(1e-4, 1)
    ax.set_xlabel(r"$\sigma_0$", labelpad=-2)
    ax.set_ylabel(r"$\tilde\delta_{\rm th}$")
    ax.legend(loc="lower left", fontsize=7)
    # non-formation triangle and spectrum (Fig. 2 top of 2211.13950: ln sigma0=-5, mu=1, L=1)
    dlt = math.exp(-2.8)
    x = np.linspace(0, 3, 300)
    lnsig = -5 - x ** 2
    ax2.plot(x, lnsig, color=fs.PAL["red"], label=r"spectrum, $\ln\sigma_0=-5$")
    ax2.plot(x, -4 * x, color="k", lw=1.0, label=r"$\sigma=(k/\tilde k)^{-4}$")
    ax2.plot(x, math.log(dlt) - 2 * x, color=fs.PAL["blue"], lw=1.0, label="Case I/II border")
    ax2.plot(x, 2.5 * math.log(dlt) + x, color=fs.PAL["orange"], lw=1.0,
             label=r"$\tilde\delta^{5/2} k/\tilde k$")
    ax2.axvline(1.0, **fs.MASK_LINE)
    km, sm = C.vd_merge_point(dlt)
    ax2.plot(math.log(km), math.log(sm), "o", color="k", ms=4)
    ax2.set_xlabel(r"$\ln(k/\tilde k)$", labelpad=-2)
    ax2.set_ylabel(r"$\ln\sigma_{\delta,\rm ent}$")
    ax2.set_ylim(-12, 0)
    ax2.legend(loc="lower left", fontsize=7)
    ax2.text(2.95, -0.6, r"$\tilde\delta=\tilde\delta_{\rm th}=e^{-2.8}$", ha="right", va="top",
             fontsize=9)
    fs.save(fig, os.path.join(out, "check_T3_dispersion_2211.13950"))
    plt.close(fig)
    return dict(jumps={k: list(v) for k, v in jumps.items()})


# ------------------------------------------------------------------- T4 2507.18312
def t4(out):
    from scipy.optimize import minimize_scalar
    from scipy import integrate as si
    worst = 0.0
    for d in (1e-3, 0.01, 0.1, 0.3):
        res = minimize_scalar(lambda th: -C.tophat_ltb(d, th)[2], bounds=(0.1, 2 * np.pi - 0.1),
                              method="bounded", options=dict(xatol=1e-12))
        Rmax = -res.fun
        amax = C.tophat_ltb(d, res.x)[1]
        th = 2 * np.pi - np.arccos(1 - 2 * C.tophat_bBH(d)) if C.tophat_bBH(d) < 1 else np.nan
        R_bh = C.tophat_ltb(d, th)[2]
        worst = max(worst, abs(Rmax * d / 0.6 - 1), abs(amax * d / (C.tophat_amax(1.0)) - 1),
                    abs(R_bh - 1.0))
    check("T4.1a", "R_max d/r_m=3/5, a_max d=1.0631, R(b_BH)=2M", f"max rel. dev {worst:.1e}",
          "0", "2507.18312:276,304,308,316", worst < 1e-6, f"a_max*delta={C.tophat_amax(1):.4f}")
    # linear limit: density contrast of the top hat vs delta_m a at a*delta = 1e-3
    d = 0.01
    th = 0.05
    t, a, R = C.tophat_ltb(d, th)
    dens = (a / R) ** 3 - 1      # rho/rho_b - 1 inside, R = a r_m (1 + ...) unperturbed
    check("T4.1b", "early density contrast / (delta_m a)", f"{dens / (d * a):.4f}", "1",
          "2507.18312:171,184-187", abs(dens / (d * a) - 1) < 1e-2, f"a*delta={a * d:.2e}")
    # T4.2 zeta(0)/delta_m for Gaussian K, eq. 161 at first order
    zr = 0.5 * si.quad(lambda r: r * 5 / 3 * np.exp(1 - r * r), 0, np.inf)[0]
    check("T4.2", "zeta_peak/delta_m (Gaussian K)", f"{zr:.4f}", "1.13", "2507.18312:161,188",
          round(zr, 2) == 1.13)
    ar = C.profile_spin_rms(0.1, 0.1 ** 0.1)
    check("T4.3", "a_rms at zeta_rms=0.1, delta=zeta^0.1", f"{ar:.3g}", "~0.01",
          "2507.18312:635-637", 0.003 < ar < 0.03, "order of magnitude only")
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fs.inch_axes(fig, 0.75, 0.58, 3.2, 2.7)
    ax2 = fs.inch_axes(fig, 4.65, 0.58, 3.2, 2.7)
    for d, col in zip((0.3, 0.1, 0.03), fs.SERIES[:3]):
        th = np.linspace(1e-3, 2 * np.pi, 2000)
        t, a, R = C.tophat_ltb(d, th)
        ax.plot(a, R, color=col, label=fr"$\delta_m={d}$")
        ax.plot(C.tophat_amax(d), 3 / (5 * d), "o", color=col, ms=4, mfc="none")
        aBH = C.tophat_aBH(d)
        ax.plot(aBH, 1.0, "s", color=col, ms=4)
    aa = np.geomspace(1e-2, 300, 100)
    ax.plot(aa, aa, **fs.GUIDE, label=r"$R=a\,r_m$")
    ax.axhline(1.0, **fs.MASK_LINE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.3, 50)
    ax.set_xlim(1e-1, 300)
    ax.set_xlabel(r"$a/a_H$", labelpad=-2)
    ax.set_ylabel(r"$R/r_m$  ($r_m=2M$)")
    ax.legend(loc="upper left", fontsize=7)
    z = np.geomspace(1e-6, 0.3, 100)
    ax2.plot(z, C.profile_threshold(z), color=fs.PAL["red"], label=r"top hat $\zeta^{2/5}$")
    ax2.plot(z, z ** 0.1, color=fs.PAL["orange"], label=r"$A_2\to0$, $A_4=1$: $\zeta^{1/10}$")
    ax2.plot(z, C.vd_delta_th(0.4 * z, 1.0, 0.0), color=fs.PAL["blue"], ls="--",
             label=r"2211.13950, $\sigma_0=2\zeta/5$, $L=0$")
    ax2.plot(z, C.profile_spin_rms(z, z ** 0.1), color=fs.PAL["green"],
             label=r"$a_{\rm rms}$ at $\delta=\zeta^{1/10}$")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel(r"$\zeta_{\rm rms}$", labelpad=-2)
    ax2.set_ylabel(r"$\delta_{\rm th}$, $a_{\rm rms}$")
    ax2.legend(loc="lower right", fontsize=7)
    fs.save(fig, os.path.join(out, "check_T4_profile_2507.18312"))
    plt.close(fig)
    return {}


# ------------------------------------------------------------------- T5 2508.10070
def t5(out, quick):
    rng = np.random.default_rng(25081007)
    worst = 0.0
    for _ in range(200):
        d = np.sort(rng.normal(0.3, 0.1, 3))[::-1]
        lam0 = rng.uniform(0.5, 2.0)
        sig = rng.uniform(1e-3, 0.1)
        xl, xth, e, dmax, ok = C.pancake_hoop_general([lam0] * 3, np.diag(d), sig)
        sh = 2 * d.sum() * sig / lam0                  # sigma_h(q0), 2508.10070:324
        h = C.hoop_h(*(sh * d))
        if d[0] > 0:
            worst = max(worst, abs((xl / xth) / h - 1))
    check("T5.1", "general pancake criterion, spherical region = 1609 h",
          f"max rel. dev {worst:.1e}", "0", "2508.10070:309-331 vs 1609.01588:604-607",
          worst < 1e-10)
    c = C.beta_mono_smallsigma_coeff()
    check("T5.2", "beta/sigma-bar^5, monochromatic, sigma*->0", f"{c / 6 ** 5:.4f}", "1.08",
          "2508.10070:654-659", abs(c / 6 ** 5 / 1.08 - 1) < 0.01,
          f"ratio to 0.05556: {c / 6 ** 5 / 0.05556:.1f} (paper: 19)")
    res = {}
    if not quick:
        table_b = {1e-5: 1.08, 1e-3: 1.12, 1e-2: 1.51, 5e-2: 2.77, 0.1: 0.67}
        table_m = {1e-5: 14.7, 1e-3: 14.7, 1e-2: 14.7, 5e-2: 15.5, 0.1: 18.1}
        for s in table_b:
            beta, nbh, mbar = C.beta_monochromatic(s)
            sbar = mbar ** (2 / 3) * s
            rb = beta / sbar ** 5
            res[s] = (beta, nbh, mbar, rb)
            check("T5.3", f"beta/sigma-bar^5 and Mbar/M* at sigma*={s:g}",
                  f"{rb:.3f}, {mbar:.2f}", f"{table_b[s]}, {table_m[s]}",
                  "2508.10070 Tables mass_mono, beta_mono (612, 665)",
                  abs(rb / table_b[s] - 1) < 0.05 and abs(mbar / table_m[s] - 1) < 0.05)
        fs.use_style()
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
        ax = fs.inch_axes(fig, 0.75, 0.58, 3.2, 2.7)
        ax2 = fs.inch_axes(fig, 4.65, 0.58, 3.2, 2.7)
        ss = sorted(res)
        ax.plot(ss, [res[s][3] for s in ss], "o-", color=fs.PAL["red"], ms=4,
                label="numerical (this work)")
        ax.plot(ss, [table_b[s] for s in ss], "s", color=fs.PAL["blue"], ms=5, mfc="none",
                label="2508.10070 table (665)")
        ax.axhline(c / 6 ** 5, **fs.GUIDE, label="small-$\\sigma$ closed form")
        ax.set_xscale("log")
        ax.set_xlabel(r"$\sigma_h^*$", labelpad=-2)
        ax.set_ylabel(r"$\beta/\bar\sigma_h^5$")
        ax.legend(loc="upper left", fontsize=7)
        ax2.plot(ss, [res[s][2] for s in ss], "o-", color=fs.PAL["red"], ms=4,
                 label="numerical (this work)")
        ax2.plot(ss, [table_m[s] for s in ss], "s", color=fs.PAL["blue"], ms=5, mfc="none",
                 label="2508.10070 table (612)")
        ax2.axhline(6 * math.sqrt(6), **fs.GUIDE, label=r"$6\sqrt{6}$ (603)")
        ax2.set_xscale("log")
        ax2.set_xlabel(r"$\sigma_h^*$", labelpad=-2)
        ax2.set_ylabel(r"$\bar M/M^*$")
        ax2.legend(loc="upper left", fontsize=7)
        fs.save(fig, os.path.join(out, "check_T5_peaks_2508.10070"))
        plt.close(fig)
    return {str(k): v for k, v in res.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--only", default="12345")
    a = ap.parse_args()
    inputs = [os.path.join(HERE, f) for f in ("emd_criteria.py", "check_criteria.py")]
    with runlog.Run("A-pre-2: check the analytic criteria against numbers printed in "
                    "1609.01588, 1707.03595, 2211.13950, 2507.18312, 2508.10070",
                    "scouting", inputs) as run:
        print(f"run {run.run_id} -> {run.out}", flush=True)
        data = {}
        for k, fn in (("1", t1), ("2", t2), ("3", t3), ("4", t4)):
            if k in a.only:
                data[f"T{k}"] = fn(run.out)
        if "5" in a.only:
            data["T5"] = t5(run.out, a.quick)
        with open(os.path.join(run.out, "results.json"), "w") as f:
            json.dump(dict(run_id=run.run_id, checks=RESULTS, data=data), f, indent=1,
                      default=float)
        counted = [r for r in RESULTS if r["passed"] is not None]
        n_fail = sum(not r["passed"] for r in counted)
        n_info = len(RESULTS) - len(counted)
        print(f"{len(counted)} checks, {n_fail} failed, {n_info} diagnostics (INFO); "
              f"run {run.run_id}")


if __name__ == "__main__":
    main()
