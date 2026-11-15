#!/usr/bin/env python3
"""P8a: convergence of the collisional relaxation in the time step.

  run_conv_dt.py OUTDIR [--exe ATHENA] [--n 1000000] [--nproc 8] [--seeds 3]

Two Maxwellian populations, theta_1 = 3 theta_2 = 3e-3, equal numbers. The decay rate of
theta_1 - theta_2 is fitted over [0, 2/nu_0] from the species columns of the collision
history, for nu_0 dt = 0.1, 0.05, 0.025, 0.0125 without sub-cycling (coll_pmax = 1) and
for nu_0 dt = 0.4 with sub-cycling (coll_pmax = 0.225, about eight sub-steps), each with
several seeds. Prediction: nu_fit = nu_inf + nu_0^2 dt_c/2 (first order; disjoint pairs
of one step use the momenta at its start), dt_c the collision sub-step.
"""
import argparse
import json
import os
import sys

import numpy as np

import common
from nrpic import collide

TH1, TH2 = 3.0e-3, 1.0e-3
NU0 = 1.25                       # non-relativistic closed form, per unit time
DTS = [0.08, 0.04, 0.02, 0.01]
DT_SUB, PMAX_SUB = 0.32, 0.225
TWIN = 2.0/NU0


def temperatures(h):
    """Temperatures of species 0 and 1 from their mean energies, for every record."""
    w0 = h["sum_MW_species0"]/h["sum_M_species0"]
    w1 = (h["sum_MW"] - h["sum_MW_species0"])/(h["sum_M"] - h["sum_M_species0"])
    return (np.array([collide.mj_theta_from_w(w) for w in w0]),
            np.array([collide.mj_theta_from_w(w) for w in w1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=1000000)
    ap.add_argument("--nx", type=int, default=32)
    ap.add_argument("--nproc", type=int, default=8)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--analyse-only", action="store_true")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, nx = args.n, args.nx
    ic = os.path.join(out, "twotemp.nrp")
    if not args.analyse_only:
        info = common.make_box(ic, "twotemp", n, seed=41, theta=TH1, theta2=TH2)
    sigma = NU0/float(collide.relax_rate_nr(TH1, TH2, 1.0))
    mesh = [f"mesh/nx{d}={nx}" for d in (1, 2, 3)] + [f"meshblock/nx{d}={nx}"
                                                      for d in (1, 2, 3)]
    jobs, meta = [], []
    for seed in range(1, args.seeds + 1):
        for dt, pmax, name in [(d, 1.0, f"dt{d:g}") for d in DTS] \
                + [(DT_SUB, PMAX_SUB, "subcycled")]:
            steps = int(round(TWIN/dt))
            rd = os.path.join(out, f"{name}_seed{seed}")
            ov = mesh + [f"particles/particle_file={ic}", f"particles/dt={dt}",
                         f"particles/coll_sigma={sigma!r}", f"particles/coll_pmax={pmax}",
                         "particles/snap_dt=1.0e9", f"time/nlim={steps}", "time/tlim=1.0e9",
                         f"job/rng_seed={500 + seed}"]
            jobs.append((args.exe, common.DECK_BOX, rd, ov))
            meta.append(dict(name=name, seed=seed, dt=dt, pmax=pmax, rundir=rd))
    summary = {"n": n, "nx": nx, "sigma": sigma, "nu0_nr": NU0, "theta": [TH1, TH2],
               "window": TWIN, "exe": args.exe, "exe_sha256": common.sha256(args.exe)}
    ok = True
    if not args.analyse_only:
        res = common.run_many(jobs, args.nproc)
        summary["exit"] = [r[0] for r in res]
        summary["wall_s"] = [round(r[1], 1) for r in res]
        ok = all(r[0] == 0 for r in res)

    # initial difference from the particle file (the same for all runs)
    from nrpic.io import read_nrp
    x, u, m, sp = read_nrp(ic)[:4]
    w = np.sqrt(1.0 + np.sum(u*u, axis=1))
    d0 = collide.mj_theta_from_w(np.mean(w[sp == 0])) \
        - collide.mj_theta_from_w(np.mean(w[sp == 1]))
    curves = {}
    fits = {}
    for mm in meta:
        h = collide.read_history(os.path.join(mm["rundir"], "box.coll.hst"))
        h["sum_M"] = np.full(len(h["time"]), float(np.sum(m)))
        t0, t1 = temperatures(h)
        t = np.concatenate(([0.0], h["time"]))
        dd = np.concatenate(([d0], t0 - t1))
        nu = -np.polyfit(t, np.log(dd), 1)[0]
        # initial slope: quadratic fit of ln D over the first fifth of the window
        sel = t <= 0.2*TWIN + 1e-9
        nu_init = -np.polyfit(t[sel], np.log(dd[sel]), 2)[1] if sel.sum() >= 4 else np.nan
        dtc = mm["dt"]/float(np.mean(h["mean_nsub"]))
        fits.setdefault(mm["name"], []).append(
            dict(seed=mm["seed"], nu_fit=float(nu), nu_init=float(nu_init), dt=mm["dt"],
                 dt_collision=dtc, mean_nsub=float(np.mean(h["mean_nsub"])),
                 max_P=float(h["max_P"].max()), n_trunc=int(h["n_trunc"].sum()),
                 collisions=int(h["n_coll"].sum())))
        curves[(mm["name"], mm["seed"])] = (t, dd)
    rows = []
    for name, lst in fits.items():
        v = np.array([f["nu_fit"] for f in lst])
        vi = np.array([f["nu_init"] for f in lst])
        rows.append(dict(name=name, dt=lst[0]["dt"],
                         dt_collision=float(np.mean([f["dt_collision"] for f in lst])),
                         nu_fit=float(v.mean()),
                         nu_fit_se=float(v.std(ddof=1)/np.sqrt(len(v))) if len(v) > 1 else None,
                         nu_init=float(np.nanmean(vi)),
                         nu_init_se=float(np.nanstd(vi, ddof=1)/np.sqrt(len(vi)))
                         if len(vi) > 1 else None,
                         mean_nsub=float(np.mean([f["mean_nsub"] for f in lst])),
                         max_P=float(max(f["max_P"] for f in lst)),
                         n_trunc=int(sum(f["n_trunc"] for f in lst)), runs=lst))
    summary["rows"] = rows
    plain = sorted([r for r in rows if r["name"] != "subcycled"], key=lambda r: -r["dt"])
    sub = [r for r in rows if r["name"] == "subcycled"][0]
    nus = np.array([r["nu_fit"] for r in plain])
    ses = np.array([r["nu_fit_se"] or 0.0 for r in plain])
    dts = np.array([r["dt"] for r in plain])
    # straight line through the four plain runs: nu = nu_inf + slope dt
    wts = 1.0/np.maximum(ses, 1e-12)**2
    A = np.vstack([np.ones_like(dts), dts]).T
    cov = np.linalg.inv(A.T @ (A*wts[:, None]))
    coef = cov @ (A.T @ (wts*nus))
    nu_inf, slope = float(coef[0]), float(coef[1])
    resid = (nus - A @ coef)/np.maximum(ses, 1e-12)
    d1, d2, d3 = nus[0] - nus[1], nus[1] - nus[2], nus[2] - nus[3]
    summary["fit"] = dict(nu_inf=nu_inf, nu_inf_se=float(np.sqrt(cov[0, 0])), slope=slope,
                          slope_se=float(np.sqrt(cov[1, 1])),
                          slope_predicted=0.5*NU0**2,
                          slope_predicted_with_nu_inf=0.5*nu_inf**2,
                          chi2=float(np.sum(resid**2)), dof=len(dts) - 2,
                          successive_differences=[float(d1), float(d2), float(d3)],
                          ratio_12=float(d1/d2), ratio_23=float(d2/d3),
                          nu_inf_over_nr_closed_form=nu_inf/NU0)
    pred_sub = nu_inf + slope*sub["dt_collision"]
    summary["subcycled"] = dict(nu_fit=sub["nu_fit"], nu_fit_se=sub["nu_fit_se"],
                                dt_collision=sub["dt_collision"], predicted=float(pred_sub),
                                z=float((sub["nu_fit"] - pred_sub)
                                        / np.hypot(sub["nu_fit_se"] or 1e-12,
                                                   np.sqrt(cov[0, 0]))),
                                plain_run_with_step_0p32_would_give=float(nu_inf + slope*DT_SUB))
    f = summary["fit"]
    good = (abs(f["slope"] - f["slope_predicted_with_nu_inf"]) < 4.0*f["slope_se"]
            + 0.15*f["slope_predicted_with_nu_inf"]
            and f["slope"] > 4.0*f["slope_se"]
            and abs(summary["subcycled"]["z"]) < 4.0
            and all(r["n_trunc"] == 0 for r in rows))
    summary["ok"] = bool(ok and good)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.93, wspace=0.3)
    cols = fs.series_colors(len(DTS) + 1)
    names = [f"dt{d:g}" for d in DTS] + ["subcycled"]
    for col, name in zip(cols, names):
        t, dd = curves[(name, 1)]
        lab = (r"$\nu_0\,dt = %g$" % (NU0*float(name[2:]))) if name != "subcycled" \
            else r"$\nu_0\,dt = 0.4$, sub-cycled"
        axs[0].plot(t*NU0, dd/d0*np.exp(nu_inf*t), color=col, lw=1.0, label=lab,
                    marker="o" if name == "subcycled" else None, ms=3)
    axs[0].axhline(1.0, **fs.GUIDE)
    axs[0].set_xlabel(r"$\nu_0 t$")
    axs[0].set_ylabel(r"$(\theta_1-\theta_2)/(\theta_1-\theta_2)_0\; e^{\nu_\infty t}$")
    axs[0].legend(fontsize=7, loc="lower left")
    xx = np.linspace(0.0, 0.085, 10)
    axs[1].plot(xx*NU0, (nu_inf + 0.5*nu_inf**2*xx)/NU0, **fs.GUIDE)
    axs[1].plot(xx*NU0, (nu_inf + slope*xx)/NU0, **fs.REF_LINE)
    axs[1].errorbar(dts*NU0, nus/NU0, yerr=ses/NU0, color=fs.PAL["blue"], marker="o",
                    ls="none", ms=4, capsize=2, label="no sub-cycling")
    axs[1].errorbar([sub["dt_collision"]*NU0], [sub["nu_fit"]/NU0],
                    yerr=[(sub["nu_fit_se"] or 0.0)/NU0], color=fs.PAL["red"], marker="s",
                    ls="none", ms=4, capsize=2, label=r"$\nu_0\,dt = 0.4$, sub-cycled")
    axs[1].set_xlabel(r"$\nu_0\,dt_c$ (collision sub-step)")
    axs[1].set_ylabel(r"fitted decay rate / $\nu_0$")
    axs[1].legend(fontsize=8, loc="upper left")
    fig.savefig(os.path.join(out, "fig_conv_dt.png"), dpi=200)
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
