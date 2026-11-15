#!/usr/bin/env python3
"""Checks of wave 2 (criteria2): amplitude conversion (A1-A5) and the LTB profile of
arXiv:2609.14218 in expball form (L1-L5). Predictions in JOURNAL.md (wave 2).

    python3 check_criteria2.py [--out DIR]

Without --out the run registers itself (runlog.Run) and writes results_criteria2.json and
the figures fig_amplitude.{pdf,png}, fig_ltb2609.{pdf,png} into scratch/A-emd-pbh/<run_id>/.
`test_criteria2.py` calls the same functions and asserts the tolerances.
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
import ltb2609 as L  # noqa: E402
import predict as P  # noqa: E402

EUL = math.e


# ------------------------------------------------------------------- A: amplitude measures
def zeta_839(X, Y, Z, mu, e, p, k):
    """zeta = 2 ln Psi of MDPBH.tex:839, coded from the equation."""
    r2 = X * X + Y * Y + Z * Z
    return mu * np.exp(-k * k * r2 / 6.0) * (1.0 + k * k / 6.0 * (p * (2 * X * X - Y * Y - Z * Z)
                                                                + 3 * e * (Y * Y - Z * Z)))


def check_A1(mu=0.1, k=1.0):
    """Closed forms against the quadrature route of predict.measures_from_zeta."""
    rm = math.sqrt(6.0) / k
    dz = lambda r: -mu * k * k * r / 3.0 * math.exp(-k * k * r * r / 6.0)
    lap0 = -mu * k * k                       # lap zeta at r = 0: zeta''(0) = -mu k^2/3, times 3
    num = P.measures_from_zeta(dz, lap0, 3 * rm)
    cf = P.amplitude_measures(mu, "mu")
    return dict(r_m_num=num["r_m"], r_m=rm, delta_c_num=num["delta_c"], delta_c=cf["delta_c"],
                deltabar_num=num["deltabar"], deltabar=cf["deltabar"],
                ratio=cf["delta_c"] / cf["deltabar"],
                err_rm=abs(num["r_m"] / rm - 1), err_c=abs(num["delta_c"] / cf["delta_c"] - 1),
                err_bar=abs(num["deltabar"] / cf["deltabar"] - 1))


def _lap_fd(f, X, Y, Z, h):
    c = f(X, Y, Z)
    return ((f(X + h, Y, Z) + f(X - h, Y, Z) + f(X, Y + h, Z) + f(X, Y - h, Z)
             + f(X, Y, Z + h) + f(X, Y, Z - h) - 6 * c) / (h * h))


def check_A2(mu=0.1, cases=((0.0, 0.0), (0.2, 0.0), (0.25, -0.1), (0.1, 0.1)), k=1.0):
    """Ball average of delta_lin = -(2/5) r_m^2 lap(zeta) inside r_m (Gauss-Legendre in r and
    cos theta, trapezoid in phi; Laplacian by second differences) and the eigenvalues of
    -(2/5) r_m^2 d_i d_j zeta at the centre, against 12 mu/(5e) and (4mu/5)(1+3e+p, 1-2p,
    1-3e+p) (MDPBH.tex:908 at k^2/(aH)^2 = 6)."""
    rm = math.sqrt(6.0) / k
    xr, wr = np.polynomial.legendre.leggauss(48)
    xc, wc = np.polynomial.legendre.leggauss(32)
    nph = 64
    r = 0.5 * rm * (xr + 1)
    wr = 0.5 * rm * wr
    ph = 2 * math.pi * np.arange(nph) / nph
    Rr, Cc, Pp = np.meshgrid(r, xc, ph, indexing="ij")
    W = (wr[:, None, None] * wc[None, :, None] * (2 * math.pi / nph)) * Rr ** 2
    S = np.sqrt(1 - Cc ** 2)
    X, Y, Z = Rr * S * np.cos(Pp), Rr * S * np.sin(Pp), Rr * Cc
    vol = 4.0 / 3.0 * math.pi * rm ** 3
    out = []
    for e, p in cases:
        f = lambda X, Y, Z: zeta_839(X, Y, Z, mu, e, p, k)
        dl = -0.4 * rm * rm * _lap_fd(f, X, Y, Z, 1e-3 * rm)
        mean = float(np.sum(W * dl) / vol)
        h = 1e-3 * rm
        Hs = np.zeros((3, 3))
        E = np.eye(3) * h
        for i in range(3):
            for j in range(3):
                fpp = f(*(E[i] + E[j]))
                fpm = f(*(E[i] - E[j]))
                fmp = f(*(-E[i] + E[j]))
                fmm = f(*(-E[i] - E[j]))
                Hs[i, j] = (fpp - fpm - fmp + fmm) / (4 * h * h)
        ev = np.sort(np.linalg.eigvalsh(-0.4 * rm * rm * Hs))[::-1]
        ref = 0.8 * mu * np.array([1 + 3 * e + p, 1 - 2 * p, 1 - 3 * e + p])
        out.append(dict(e=e, p=p, mean=mean, mean_ref=12 * mu / (5 * EUL),
                        err_mean=abs(mean / (12 * mu / (5 * EUL)) - 1),
                        eig=ev.tolist(), eig_ref=ref.tolist(),
                        err_eig=float(np.max(np.abs(ev - ref)) / (0.8 * mu)),
                        trace=float(ev.sum()), trace_ref=12 * mu / 5))
    return out


def check_A3(mus=(0.01, 0.1, 0.33, 0.5)):
    """2507.18312:188: zeta(0) = (5e/12) delta_m for the Gaussian K; with delta_m = deltabar."""
    return [dict(mu=mu, back=float(C.zeta_peak_gaussian(P.convert_amplitude(mu, "mu", "mean"))),
                 err=abs(C.zeta_peak_gaussian(P.convert_amplitude(mu, "mu", "mean")) / mu - 1))
            for mu in mus] + [dict(roundtrip=max(
                abs(P.convert_amplitude(P.convert_amplitude(v, a, b), b, a) / v - 1)
                for v in (0.003, 0.1, 0.7) for a in P.AMP_MEASURES for b in P.AMP_MEASURES))]


def check_A4(mus=(0.03, 0.32, 0.33, 0.5), k=1.0):
    out = []
    for mu in mus:
        pr = L.Profile2609(mu, k, 1.0)
        r = np.linspace(1e-3, 4.0, 400001) * pr.r_m
        Cr = pr.compaction(r)
        j = int(np.argmax(Cr))
        cf = P.amplitude_measures(mu, "mu")["C_max"]
        out.append(dict(mu=mu, kr_at_max=float(k * r[j]), C_max_grid=float(Cr[j]), C_max=cf,
                        err=abs(Cr[j] / cf - 1), err_loc=abs(k * r[j] / math.sqrt(6) - 1)))
    return out


def hhat_918(e, p):
    """hhat(e, p) = (15/pi) e/(1+3e+p)^2 E(sqrt(1 - (e+p)^2/(4e^2))), MDPBH.tex:918."""
    from scipy.special import ellipe
    kk = 1.0 - (e + p) ** 2 / (4 * e * e)
    return 15.0 / math.pi * e / (1 + 3 * e + p) ** 2 * float(ellipe(kk))


def check_A5(cases=((0.2, 0.0), (0.1, 0.0), (0.25, -0.1), (0.2, 0.1))):
    out = []
    for e, p in cases:
        hh = hhat_918(e, p)
        dth = float(C.hoop_threshold_delta(e, p))
        out.append(dict(e=e, p=p, hhat=hh, mu_hoop=hh, delta_c_hoop=12 * hh / 5,
                        R1_delta_th=dth, err=abs(dth / (12 * hh / 5) - 1),
                        deltabar_hoop=12 * hh / (5 * EUL)))
    return out


# ------------------------------------------------------------------- L: LTB profile
def check_L1(mus=(1e-4, 1e-5), HRm=0.3):
    out = []
    for mu in mus:
        prof = L.LTBPeak2609(mu, 1.0, HRm, cut=(3.0, 4.0))
        r = np.linspace(0.05, 2.5, 50)
        R = prof.R_of_r(r)
        D = prof.Delta(R)
        rhat = r * prof.P.psi(r) ** 2
        lin = prof.P.compaction(r) / (HRm * rhat) ** 2
        rel = np.abs(D / lin - 1)
        out.append(dict(mu=mu, H_Rm=HRm, Delta_centre=float(D[0]), max_rel=float(rel.max()),
                        max_rel_over_Delta=float(np.max(rel / D))))
    return out


def check_L2L3(mus=(0.005, 0.01, 0.015), q=4.5, HRb=0.9):
    from expball.exact import Shells
    out = []
    for mu in mus:
        ball, prof = L.make_ball(mu, q=q, HRb=HRb)
        pr = prof.P
        r = np.array([0.05, 0.3, 0.6, 1.0, 1.5, 2.0, 2.5, 2.9]) * prof.Rm
        R = prof.R_of_r(r)
        sh = Shells(ball, R)
        age = float(np.max(np.abs(sh.age_i / ball.t_i - 1)))
        tc = float(np.max(np.abs(sh.t_c / pr.t_s(r) - 1)))
        tah = float(np.max(np.abs(sh.t_ah / pr.t_ah(r) - 1)))
        t0 = float(pr.t_s(0.0))
        taus = np.array([0.1, 0.5, 0.9]) * (t0 - ball.t_i)
        errR = []
        for tau in taus:
            Re = sh.R(tau)
            Rp = pr.R(ball.t_i + tau, r)
            errR.append(float(np.max(np.abs(Re / Rp - 1))))
        out.append(dict(mu=mu, q=q, HRb=HRb, H_Rm=ball.H * prof.Rm, R_b=ball.Rb, Rm=prof.Rm,
                        err_age=age, err_tc=tc, err_tah=tah, err_R=errR,
                        tau_checked=taus.tolist(), t_s0=t0, delta_min=prof.delta_min,
                        rest_mass=float(ball.rest_mass()), M=ball.M))
    return out


def check_L4(HRb=0.9, qs=(2.0, 3.0, 4.5)):
    out = []
    for q in qs:
        HRm = HRb / q
        mmax = L.max_mu_on_slice(HRm)
        ok_below = ok_above = None
        try:
            L.LTBPeak2609(0.999 * mmax, 1.0, HRm, cut=(min(3.0, 0.6 * q), min(4.0, 0.9 * q)), ntab=201)
            ok_below = True
        except ValueError:
            ok_below = False
        try:
            L.LTBPeak2609(1.001 * mmax, 1.0, HRm, cut=(min(3.0, 0.6 * q), min(4.0, 0.9 * q)), ntab=201)
            ok_above = True
        except ValueError:
            ok_above = False
        out.append(dict(q=q, HRb=HRb, H_Rm=HRm, a_slice_over_aH=HRm ** -2, mu_max=mmax,
                        leading_order=0.4431 * HRb ** 2 / q ** 2, builds_below=ok_below,
                        refuses_above=not ok_above))
    return out


def check_L5(mus=(0.01, 0.1, 0.32, 0.33, 0.5)):
    out = []
    for mu in mus:
        pr = L.Profile2609(mu, 1.0, 1.0)
        r = np.linspace(1e-3, 4.0, 4001) * pr.r_m
        ts = pr.t_s(r)
        mono = bool(np.all(np.diff(ts) > 0))
        t0 = float(pr.t_s(0.0))
        # R(t, r) increasing in r at times before the central crunch
        okR = True
        for f in (0.5, 0.9, 0.99):
            Rr = pr.R(f * t0, r)
            okR &= bool(np.all(np.diff(Rr) > 0))
        fh = pr.first_trapped()
        out.append(dict(mu=mu, t_s_increasing=mono, R_increasing_before_crunch=okR,
                        t_s0_over_tH=t0 / pr.t_H, first_trapped=fh,
                        first_trapped_before_central_crunch=fh["t"] < t0))
    return out


# ------------------------------------------------------------------- figures
def figures(out):
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    # Figure 1: the two measures for the profile of 839 and the thresholds in both
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax = fs.inch_axes(fig, 0.75, 0.55, 3.15, 2.55)
    ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.55)
    mu, k = 0.1, 1.0
    rm = math.sqrt(6.0)
    r = np.linspace(1e-3, 3.2, 600) * rm
    pr = L.Profile2609(mu, k, 1.0)
    u = r * r / 6.0
    local = -0.4 * rm * rm * (mu * k * k * np.exp(-u) * (2 * u - 3) / 3.0)  # -(2/5) r_m^2 lap zeta
    mean = -1.2 * rm * rm * (pr.rzeta1(r) / r ** 2)                          # -(6/5) r_m^2 zeta'/r
    ax.plot(r / rm, local / mu, color=fs.PAL["blue"], label=r"local $\delta_{\rm lin}(r)/\mu$")
    ax.plot(r / rm, mean / mu, color=fs.PAL["red"], label=r"mean inside $r$, $/\mu$")
    ax.axhline(12 / 5, **fs.MASK_LINE)
    ax.axhline(12 / (5 * EUL), **fs.MASK_LINE)
    ax.axvline(1.0, **fs.THIN, ls=":")
    ax.text(2.0, 12 / 5 + 0.06, r"$\delta_c = 12\mu/5$", fontsize=8)
    ax.text(2.0, 12 / (5 * EUL) + 0.06, r"$\bar\delta = 12\mu/(5e)$", fontsize=8)
    ax.set_xlabel(r"$r/r_m$", labelpad=-2)
    ax.set_ylabel(r"linear contrast at $aHr_m=1$, $/\mu$")
    ax.legend(loc="center right", fontsize=7)
    ax.set_xlim(0, 3.2)
    # right: thresholds of the literature in the three measures
    rows = [("hoop line, e = 0.2 (1609.01588 via 2609:913)", hhat_918(0.2, 0.0), None),
            ("2609 particles, e = 0.2 (0.045, 0.05]", 0.045, 0.05),
            ("LTB nakedness, e = 0 (0.32, 0.33]", 0.32, 0.33),
            ("top-hat time = 250 t_H (SCOPE H1)", 0.048, None)]
    for i, (lab, lo, hi) in enumerate(rows):
        for jj, (meas, col) in enumerate((("mu", "k"), ("central", fs.PAL["blue"]),
                                          ("mean", fs.PAL["red"]))):
            v = P.convert_amplitude(lo, "mu", meas)
            y = i + 0.18 * (jj - 1)
            if hi is None:
                ax2.plot([v], [y], "o", color=col, ms=4)
            else:
                v2 = P.convert_amplitude(hi, "mu", meas)
                ax2.plot([v, v2], [y, y], color=col, lw=3)
    ax2.plot([], [], "o", color="k", ms=4, label=r"$\mu$")
    ax2.plot([], [], "o", color=fs.PAL["blue"], ms=4, label=r"$\delta_c$")
    ax2.plot([], [], "o", color=fs.PAL["red"], ms=4, label=r"$\bar\delta$")
    ax2.set_xscale("log")
    ax2.set_xlim(0.02, 2.0)
    ax2.set_yticks(range(len(rows)))
    ax2.set_yticklabels(["hoop e=0.2", "2609 ptcl e=0.2", "LTB naked", "250 t_H top hat"],
                        fontsize=7)
    ax2.set_ylim(-0.6, len(rows) - 0.4)
    ax2.set_xlabel("threshold amplitude", labelpad=-2)
    ax2.legend(loc="lower right", fontsize=7)
    fs.save(fig, os.path.join(out, "fig_amplitude"))
    plt.close(fig)

    # Figure 2: the LTB profile in expball form and its exact shells
    from expball.exact import Shells
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.9))
    a1 = fs.inch_axes(fig, 0.75, 3.35, 3.1, 2.3)
    a2 = fs.inch_axes(fig, 4.75, 3.35, 3.0, 2.3)
    a3 = fs.inch_axes(fig, 0.75, 0.5, 3.1, 2.3)
    a4 = fs.inch_axes(fig, 4.75, 0.5, 3.0, 2.3)
    for mu, col in zip((0.005, 0.01, 0.015), fs.SERIES):
        ball, prof = L.make_ball(mu, q=4.5, HRb=0.9)
        R = np.linspace(1e-4, 1.02 * prof.R2, 800)
        D = prof.Delta(R)
        a1.plot(R / prof.Rm, D, color=col, label=fr"$\mu={mu}$")
        a1.plot(R / prof.Rm, D + R * prof.dDelta(R) / 3, color=col, ls="--", lw=1.0)
        r = np.linspace(0.02, 2.95, 60) * prof.Rm
        sh = Shells(ball, prof.R_of_r(r))
        a2.semilogy(r / prof.Rm, np.abs(sh.t_c / prof.P.t_s(r) - 1) + 1e-18, color=col, ls="-")
        t0 = prof.P.t_s(0.0)
        for f, ls in ((0.5, ":"), (0.9, "-.")):
            tau = f * (t0 - ball.t_i)
            a2.semilogy(r / prof.Rm, np.abs(sh.R(tau)[:, ] / prof.P.R(ball.t_i + tau, r) - 1)
                        + 1e-18, color=col, ls=ls, lw=1.0)
    a1.axvspan(3.0, 4.0, color="grey", alpha=0.15)
    a1.text(3.05, 0.02, "taper", fontsize=7)
    a1.set_xlabel(r"$R/r_m$ on the slice ($Hr_m=0.2$)", labelpad=-2)
    a1.set_ylabel(r"$\Delta(R)$ (solid), local $\delta$ (dashed)")
    a1.legend(loc="upper right", fontsize=7)
    a2.set_ylim(1e-18, 1e-10)
    a2.set_xlabel(r"$r/r_m$", labelpad=-2)
    a2.set_ylabel("relative difference")
    a2.plot([], [], color="k", label=r"$t_c$ vs $t_s$ (743)")
    a2.plot([], [], color="k", ls=":", lw=1, label=r"$R$ vs $S(x)$ (593), $0.5\,t_s(0)$")
    a2.plot([], [], color="k", ls="-.", lw=1, label=r"same, $0.9\,t_s(0)$")
    a2.legend(loc="upper left", fontsize=7)
    a2.text(0.3, 2e-11, "expball shells vs 2609.14218 closed forms", fontsize=7)
    for mu, col in zip((0.32, 0.33, 0.5), fs.SERIES):
        pr = L.Profile2609(mu, 1.0, 1.0)
        r = np.linspace(1e-3, 3.0, 600) * pr.r_m
        a3.semilogy(r / pr.r_m, pr.t_s(r) / pr.t_H, color=col, label=fr"$t_s$, $\mu={mu}$")
        a3.semilogy(r / pr.r_m, pr.t_ah(r) / pr.t_H, color=col, ls="--", lw=1.0)
        fh = pr.first_trapped()
        a3.plot([fh["r_over_rm"]], [fh["t_over_tH"]], "o", color=col, ms=4)
        a4.plot(r / pr.r_m, pr.compaction(r), color=col, label=fr"$\mu={mu}$")
    a3.set_xlabel(r"$r/r_m$", labelpad=-2)
    a3.set_ylabel(r"$t/t_H$: crunch (solid), $R=2M$ (dashed)")
    a3.legend(loc="upper left", fontsize=7)
    a4.set_xlabel(r"$r/r_m$", labelpad=-2)
    a4.set_ylabel(r"compaction $\frac{3}{5}\tilde k r^2$")
    a4.axvline(1.0, **fs.THIN, ls=":")
    a4.legend(loc="upper right", fontsize=7)
    fs.save(fig, os.path.join(out, "fig_ltb2609"))
    plt.close(fig)


def run_all():
    return dict(A1=check_A1(), A2=check_A2(), A3=check_A3(), A4=check_A4(), A5=check_A5(),
                L1=check_L1(), L2L3=check_L2L3(), L4=check_L4(), L5=check_L5())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None, help="output directory (no registration)")
    a = ap.parse_args()

    def body(out):
        res = run_all()
        with open(os.path.join(out, "results_criteria2.json"), "w") as f:
            json.dump(res, f, indent=1, default=float)
        print(json.dumps(res, indent=1, default=float))
        figures(out)

    if a.out:
        os.makedirs(a.out, exist_ok=True)
        body(a.out)
        return
    import runlog
    inputs = [os.path.join(HERE, f) for f in ("check_criteria2.py", "predict.py", "ltb2609.py",
                                              "emd_criteria.py")]
    inputs.append(os.path.join(L.EXPBALL_DIR, "expball", "model.py"))
    inputs.append(os.path.join(L.EXPBALL_DIR, "expball", "exact.py"))
    with runlog.Run("criteria2: amplitude conversion (A1-A5) and LTB profile of 2609.14218 in "
                    "expball form (L1-L5)", "scouting", inputs) as run:
        print("run", run.run_id)
        body(run.out)


if __name__ == "__main__":
    main()
