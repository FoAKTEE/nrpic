#!/usr/bin/env python3
"""Validation of the reference solutions (JOURNAL.md, predictions P1 to P7).

    python3 validate.py --out <dir>

writes <dir>/validate.json and the figures <dir>/fig_*.{pdf,png}. Pure Python, one core.
"""
import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import ellipsoid as el  # noqa: E402
import tophat as th  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

# numbers printed in arXiv:2605.04487 (kb-data/raw/arxiv/2605.04487/v2/src/main_v3.tex)
PAPER_START = [  # (alpha, beta, gamma), start t/t_k from a figure file name, source line
    ((0.1114, 0.0667, 0.0219), 9.50883300, 2287),
    ((0.01112224, 0.00668337, 0.00219440), 301.41635408, 2654),
    ((0.14, 0.04, 0.02), 6.74936559, 2670),
    ((0.16, 0.10, 0.04), 5.52427173, 2690),
]
PAPER_EVENTS = [  # (alpha, beta, gamma), sigma, (t1, t2)/t_k, how the times are known
    ((0.1114, 0.0667, 0.0219), 0.1, (22.536, 29.097), "text, lines 2277 and 2279"),
    ((0.01112224, 0.00668337, 0.00219440), 0.01, (746.00547634, 966.03941482),
     "inferred from snapshot file names, lines 2655-2656 [JUDGEMENT]"),
    ((0.14, 0.04, 0.02), 0.1, (17.17713543, 29.62971494),
     "inferred from snapshot file names, lines 2672-2674 [JUDGEMENT]"),
    ((0.16, 0.10, 0.04), 0.1, (12.07053373, 16.02038801),
     "inferred from snapshot file names, lines 2691-2692 [JUDGEMENT]"),
]
MCOL = {"isolated": fs.PAL["yellow"], "embedded": fs.PAL["green"], "added": fs.PAL["red"]}


def p1_tophat(res, out):
    """Cycloid against direct integration; early-start limit of the linear contrasts."""
    lam = 0.1
    rows = []
    for a0 in (0.02 / lam, 0.2 / lam):
        R0, V0, t0 = th.za_sphere(lam, a0)
        cyc = th.cycloid(R0, V0, t0)
        sol = th.integrate_sphere(R0, V0, t0, 1.2 * cyc["t_c"], rstop=1e-3)
        t_ta_num = float(sol.t_events[0][0])
        t_in_num = float(sol.t_events[1][0])
        Rin = 1e-3 * R0
        thin = 2 * np.pi - np.arccos(1 - Rin / cyc["A"])
        t_in_cyc = cyc["t_off"] + cyc["B"] * (thin - np.sin(thin))
        tt = np.linspace(t0, sol.t[-1], 400)
        Rnum = sol.sol(tt)[0]
        Rcyc = th.cycloid_R(cyc, tt)
        rows.append(dict(a0=a0, t_ta_rel_err=abs(t_ta_num / cyc["t_ta"] - 1),
                         t_in_rel_err=abs(t_in_num / t_in_cyc - 1),
                         R_max_rel_err=float(np.max(np.abs(Rnum - Rcyc)) / cyc["R_max"]),
                         tt=tt, Rnum=Rnum, Rcyc=Rcyc, cyc=cyc))
    x = np.array([1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4])
    dta, dc, tc_over_tta = [], [], []
    for s in x:
        r = th.za_tophat_summary(lam, a0=s / lam)
        dta.append(r["deltaL_ta"])
        dc.append(r["deltaL_c"])
        tc_over_tta.append((r["t_c"] - 0.0) / r["t_ta"])
    dta, dc = np.array(dta), np.array(dc)
    slope_c = np.polyfit(np.log(x[2:]), np.log(np.abs(dc[2:] - th.DELTA_L_C)), 1)[0]
    slope_ta = np.polyfit(np.log(x[2:]), np.log(np.abs(dta[2:] - th.DELTA_L_TA)), 1)[0]
    res["P1"] = dict(
        closed_form=dict(deltaL_ta=th.DELTA_L_TA, deltaL_c=th.DELTA_L_C,
                         one_plus_delta_ta=th.ONE_PLUS_DELTA_TA),
        integration=[{k: v for k, v in r.items() if k in ("a0", "t_ta_rel_err",
                                                          "t_in_rel_err", "R_max_rel_err")}
                     for r in rows],
        early_start=dict(a0_lambda=x.tolist(), deltaL_ta=dta.tolist(),
                         deltaL_c=dc.tolist(), tc_over_tta=tc_over_tta,
                         slope_c=slope_c, slope_ta=slope_ta),
        paper_start_sphere=th.za_tophat_summary(0.1),
    )
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax1 = fs.inch_axes(fig, 0.7, 0.55, 3.0, 2.5)
    ax2 = fs.inch_axes(fig, 4.65, 0.55, 3.0, 2.5)
    r = rows[0]
    ax1.plot(r["tt"] / th.T_K, r["Rcyc"] / r["cyc"]["R_max"], color=fs.PAL["blue"],
             label="cycloid (closed form)")
    ax1.plot(r["tt"][::12] / th.T_K, r["Rnum"][::12] / r["cyc"]["R_max"], "o",
             color=fs.PAL["red"], ms=3, label="direct integration")
    ax1.axvline(r["cyc"]["t_ta"] / th.T_K, **fs.MASK_LINE)
    ax1.axvline(r["cyc"]["t_c"] / th.T_K, **fs.MASK_LINE)
    ax1.set_xlabel(r"$t/t_k$")
    ax1.set_ylabel(r"$R/R_{\max}$")
    ax1.set_ylim(0, 1.08)
    ax1.legend(loc="lower center")
    ax2.loglog(x, np.abs(dc - th.DELTA_L_C), "o-", color=fs.PAL["red"],
               label=r"$|\delta_L(t_c)-1.6865|$")
    ax2.loglog(x, np.abs(dta - th.DELTA_L_TA), "s-", color=fs.PAL["blue"],
               label=r"$|\delta_L(t_{\rm ta})-1.0624|$")
    ax2.loglog(x, 0.5 * x, **fs.GUIDE, label=r"$\propto a_0\lambda$")
    ax2.set_xlabel(r"$a_0\lambda$ (start of the Zel'dovich data)")
    ax2.set_ylabel("deviation from the EdS growing mode")
    ax2.legend(loc="upper left")
    fs.save(fig, os.path.join(out, "fig_tophat"))
    plt.close(fig)


def p2_coeffs(res, out):
    q = np.logspace(-3, 3, 61)
    err = []
    rows = []
    for r in q:
        A = np.array([1.0, 1.0, r])
        num = el.alphas(A)
        cf = el.alphas_spheroid(1.0, r)
        err.append(np.max(np.abs(num - cf)))
        rows.append((r, num[0], num[2], cf[0], cf[2]))
    rng = np.random.default_rng(1)
    sums = []
    for _ in range(1000):
        A = 10 ** rng.uniform(-3, 3, 3)
        sums.append(abs(el.alphas(A).sum() - 2))
    res["P2"] = dict(max_abs_err_spheroid=float(np.max(err)),
                     max_abs_sum_err_triaxial=float(np.max(sums)),
                     note="c/a from 1e-3 to 1e3; 1000 random triaxial shapes, ratios to 1e6")
    rows = np.array(rows)
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.2))
    ax = fs.inch_axes(fig, 0.7, 0.55, 3.1, 2.5)
    ax.semilogx(rows[:, 0], rows[:, 3], color=fs.PAL["blue"], label=r"$\alpha_1$ closed form")
    ax.semilogx(rows[:, 0], rows[:, 4], color=fs.PAL["blue"], ls="--",
                label=r"$\alpha_3$ closed form")
    ax.semilogx(rows[::4, 0], rows[::4, 1], "o", color=fs.PAL["red"], ms=3,
                label=r"$R_D$ form")
    ax.semilogx(rows[::4, 0], rows[::4, 2], "s", color=fs.PAL["red"], ms=3)
    ax.set_xlabel(r"$c/a$ of the spheroid $(a,a,c)$")
    ax.set_ylabel(r"$\alpha_i$")
    ax.legend(loc="center left")
    fs.save(fig, os.path.join(out, "fig_alphas"))
    plt.close(fig)


def p3_p4_limits(res, out):
    lam = 0.1
    sph = {}
    for a0 in (0.5 / lam, 0.05 / lam):
        R0, V0, t0 = th.za_sphere(lam, a0)
        cyc = th.cycloid(R0, V0, t0)
        for m in el.MODELS:
            r = el.evolve((lam, lam, lam), a0=a0, model=m)
            sph[f"{m}_a0lam{a0 * lam:g}"] = dict(t1=r["collapses"][0]["t"],
                                                 t_c_cycloid=cyc["t_c"],
                                                 rel_err=r["collapses"][0]["t"] / cyc["t_c"] - 1)
    # Newtonian comoving formulation (gamma = 1) against the physical one
    lams = (0.1114, 0.0667, 0.0219)
    rc = el.evolve(lams, model="added", sr="comoving", n_collapse=2)
    rp = el.evolve(lams, model="added", n_collapse=2)
    comov = [rc["collapses"][k]["t"] / rp["collapses"][k]["t"] - 1 for k in range(2)]
    # plane limit
    ks = np.arange(1, 7)
    errs = []
    t_za = float(th.t_of_a(1.0 / lam))
    for k in ks:
        RL = (1.0, 10.0 ** k, 10.0 ** k)
        r = el.evolve((lam, 0.0, 0.0), a0=0.5 / lam, model="embedded", RL=RL)
        errs.append(abs(r["collapses"][0]["t"] / t_za - 1))
    errs_early = []
    for k in ks:
        RL = (1.0, 10.0 ** k, 10.0 ** k)
        r = el.evolve((lam, 0.0, 0.0), a0=0.01 / lam, model="embedded", RL=RL)
        errs_early.append(abs(r["collapses"][0]["t"] / t_za - 1))
    res["P3"] = dict(sphere=sph, comoving_vs_physical_rel=comov)
    res["P4"] = dict(k=ks.tolist(), rel_err_start_turnaround=errs,
                     rel_err_start_a0lam_0p01=errs_early, t_za_over_tk=t_za / th.T_K)
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.2))
    ax = fs.inch_axes(fig, 0.75, 0.55, 3.05, 2.5)
    ax.semilogy(ks, errs, "o-", color=fs.PAL["red"], label=r"start $a_0\lambda_1=1/2$")
    ax.semilogy(ks, errs_early, "s-", color=fs.PAL["yellow"], label=r"start $a_0\lambda_1=0.01$")
    ax.semilogy(ks, errs[0] * 10.0 ** (-(ks - 1.0)), **fs.GUIDE, label=r"$\propto 10^{-k}$")
    ax.set_xlabel(r"$k$, transverse/collapsing Lagrangian radius $=10^k$")
    ax.set_ylabel(r"$|t_1/t_{\rm ZA}-1|$ (embedded)")
    ax.legend(loc="upper right")
    fs.save(fig, os.path.join(out, "fig_plane_limit"))
    plt.close(fig)


def p5_paper(res, out):
    starts = []
    for lams, t_print, line in PAPER_START:
        t0 = (0.5 / lams[0]) ** 1.5
        starts.append(dict(lams=lams, t0_over_tk=t0, printed=t_print, line=line,
                           rel=t0 / t_print - 1))
    ev = []
    trajs = {}
    for lams, sigma, (t1p, t2p), how in PAPER_EVENTS:
        e, p = el.ep_from_abg(*lams)
        row = dict(lams=lams, sigma=sigma, e=e, p=p, t1_paper=t1p, t2_paper=t2p, how=how,
                   models={})
        for m in el.MODELS:
            for sr in (False, True):
                r = el.evolve(lams, model=m, sr=sr, n_collapse=2)
                c = r["collapses"]
                key = m + ("_sr" if sr else "")
                row["models"][key] = dict(t1=c[0]["t_over_tk"], t2=c[1]["t_over_tk"],
                                          axis1=c[0]["axis"], axis2=c[1]["axis"],
                                          d1=c[0]["t_over_tk"] / t1p - 1,
                                          d2=c[1]["t_over_tk"] / t2p - 1,
                                          h1=c[0]["h"])
                if lams[0] == 0.1114:
                    trajs[key] = (r["t"] / th.T_K, r["A"])
        ev.append(row)
    lams = PAPER_EVENTS[0][0]
    res["P5"] = dict(starts=starts, events=ev)
    # trajectories of the main case
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fs.inch_axes(fig, 0.7, 0.55, 4.2, 2.75)
    for m in el.MODELS:
        t, A = trajs[m]
        for i, ls in enumerate(("-", "--", ":")):
            ax.plot(t, np.abs(A[:, i]), color=MCOL[m], ls=ls,
                    label=m if i == 0 else None)
    tt = np.linspace(9.50883, 40, 300)
    aa = th.a_of_t(tt * th.T_K)
    Z = np.array([el.za_axes(lams, a) for a in aa])
    Z[Z < 0] = np.nan
    for i, ls in enumerate(("-", "--", ":")):
        ax.plot(tt, Z[:, i], color=fs.PAL["blue"], ls=ls, lw=1.0,
                label="Zel'dovich" if i == 0 else None)
    for tp in PAPER_EVENTS[0][2]:
        ax.axvline(tp, **fs.REF_LINE, alpha=0.5)
    ax.set_xlim(9, 40)
    ax.set_ylim(0, 9.5)
    ax.set_xlabel(r"$t/t_k$")
    ax.set_ylabel(r"$|A_i|/r_g$ (solid 1, dashed 2, dotted 3)")
    ax.legend(loc="upper left", ncol=2)
    # relative differences, one row per case and event
    ax2 = fs.inch_axes(fig, 6.1, 0.55, 1.75, 2.75)
    names = ["main", "s=0.01", "(.14,.04,.02)", "(.16,.10,.04)"]
    labels = []
    for j, row in enumerate(ev):
        for k, key in enumerate(("d1", "d2")):
            y = 2 * j + k
            labels.append(f"{names[j]} {'1st' if k == 0 else '2nd'}")
            for m in el.MODELS:
                for sr, mk in ((False, "o"), (True, "^")):
                    d = row["models"][m + ("_sr" if sr else "")][key]
                    ax2.plot(100 * d, y + (0.15 if sr else -0.15), mk, color=MCOL[m],
                             ms=4, mfc=MCOL[m] if not sr else "none")
    ax2.axvline(0, **fs.GUIDE)
    ax2.set_yticks(range(8))
    ax2.set_yticklabels(labels, fontsize=8)
    ax2.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax2.set_ylim(7.6, -0.6)
    ax2.set_xlabel(r"$t_{\rm model}/t_{\rm paper}-1$ [%]")
    fs.save(fig, os.path.join(out, "fig_paper_cases"))
    plt.close(fig)


def p6_p7(res, out):
    rng = np.random.default_rng(7)
    errs = []
    for _ in range(200):
        e = rng.uniform(0.0, 0.5)
        p = rng.uniform(-e, e)
        al, be, ga = el.abg_from_dep(rng.uniform(0.05, 1.0), e, p)
        if al - ga <= 0:
            continue
        ac = 1.0 / al
        A = el.za_axes((al, be, ga), ac)
        A[0] = 0.0
        errs.append(abs(el.hoop_h(A) / el.h_za_closed(al, be, ga) - 1))
    sc = []
    for m in el.MODELS:
        for (e, p) in ((0.2, 0.0), (0.1, -0.05), (0.3, 0.2)):
            rows = [el.first_collapse(d, e, p, model=m) for d in (0.05, 0.2, 1.0)]
            tt = [r["t1_over_tk"] * r["deltaL"] ** 1.5 for r in rows]
            hh = [r["h1"] * r["deltaL"] for r in rows]
            sc.append(dict(model=m, e=e, p=p, t_scaled=tt, h_scaled=hh,
                           t_spread=float(np.ptp(tt) / np.mean(tt)),
                           h_spread=float(np.ptp(hh) / np.mean(hh))))
    res["P6"] = dict(max_rel_err=float(np.max(errs)), n=len(errs))
    res["P7"] = dict(cases=sc, max_t_spread=max(s["t_spread"] for s in sc),
                     max_h_spread=max(s["h_spread"] for s in sc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    res = {}
    p1_tophat(res, a.out)
    p2_coeffs(res, a.out)
    p3_p4_limits(res, a.out)
    p5_paper(res, a.out)
    p6_p7(res, a.out)
    with open(os.path.join(a.out, "validate.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k != "P5"}, indent=1, default=float)[:6000])
    for row in res["P5"]["events"]:
        print(row["lams"], row["sigma"], f"e={row['e']:.4f} p={row['p']:.5f}",
              row["t1_paper"], row["t2_paper"])
        for k, d in row["models"].items():
            print(f"   {k:13s} t1={d['t1']:10.4f} ({100 * d['d1']:+6.2f}%)  "
                  f"t2={d['t2']:10.4f} ({100 * d['d2']:+6.2f}%)  h1={d['h1']:.3f} "
                  f"axes {d['axis1']},{d['axis2']}")
    for s in res["P5"]["starts"]:
        print("start", s)


if __name__ == "__main__":
    main()
