#!/usr/bin/env python3
"""P2, P3, P4: collision rate of a Maxwell-Juttner gas in the periodic Minkowski box,
conservation, and the null runs (operator absent, operator on with sigma = 0).

  run_rate.py OUTDIR [--exe ATHENA] [--n 1000000] [--nproc 8] [--thetas 0.01,0.1,1,10]

For every temperature two runs: Gamma dt = 0.015 without sub-cycling (coll_pmax = 1) and
Gamma dt = 0.15 with coll_pmax = 0.1. Writes summary.json and figures into OUTDIR.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import common
from nrpic import collide

EPS = 2.0**-52


def pair_average(u, npair, seed):
    """Mean and standard error of the Moller speed over random pairs of the particles,
    and the standard deviation of the Moller speed of a pair."""
    gen = np.random.default_rng(seed)
    n = len(u)
    i = gen.integers(0, n, npair)
    j = gen.integers(0, n - 1, npair)
    j = np.where(j >= i, j + 1, j)
    g1, wa, wb = collide.gamma_rel_m1(u[i], u[j])
    v = collide.moller(g1, wa, wb)
    return float(v.mean()), float(v.std()/np.sqrt(npair)), float(v.std())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=1000000)
    ap.add_argument("--nproc", type=int, default=8)
    ap.add_argument("--thetas", default="0.01,0.1,1,10")
    ap.add_argument("--nx", type=int, default=32)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--extra", default="", help="further input overrides, comma separated")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    thetas = [float(t) for t in args.thetas.split(",")]
    n, nx, steps, dt = args.n, args.nx, args.steps, 0.01
    extra = [e for e in args.extra.split(",") if e]
    mesh = [f"mesh/nx{d}={nx}" for d in (1, 2, 3)] + [f"meshblock/nx{d}={nx}"
                                                      for d in (1, 2, 3)]
    jobs, meta = [], []
    for th in thetas:
        ic = os.path.join(out, f"mj_{th:g}.nrp")
        info = common.make_box(ic, "mj", n, seed=11, theta=th)
        for mode, gdt, pmax in (("plain", 0.015, 1.0), ("subcycled", 0.15, 0.1)):
            sigma = gdt/(float(collide.mj_vmol(th))*dt)
            rd = os.path.join(out, f"theta{th:g}_{mode}")
            ov = mesh + [f"particles/particle_file={ic}", f"particles/dt={dt}",
                         f"particles/coll_sigma={sigma!r}", f"particles/coll_pmax={pmax}",
                         f"particles/snap_dt={steps*dt!r}", f"time/nlim={steps}",
                         "time/tlim=1.0e9", "job/rng_seed=101"] + extra
            jobs.append((args.exe, common.DECK_BOX, rd, ov))
            meta.append(dict(theta=th, mode=mode, sigma=sigma, rundir=rd, gdt=gdt,
                             pmax=pmax, ic=info))
    # null runs at the second temperature: operator absent, and present with sigma = 0
    th0 = thetas[min(1, len(thetas) - 1)]
    ic0 = os.path.join(out, f"mj_{th0:g}.nrp")
    base_ov = mesh + [f"particles/particle_file={ic0}", f"particles/dt={dt}",
                      f"particles/snap_dt={steps*dt!r}", f"time/nlim={steps}",
                      "time/tlim=1.0e9", "job/rng_seed=101"] + extra
    jobs.append((args.exe, common.DECK_BOX, os.path.join(out, "null_off"),
                 base_ov + ["particles/collisions=false"]))
    jobs.append((args.exe, common.DECK_BOX, os.path.join(out, "null_sigma0"),
                 base_ov + ["particles/coll_sigma=0.0"]))
    res = common.run_many(jobs, args.nproc)
    summary = {"n": n, "nx": nx, "steps": steps, "dt": dt, "exe": args.exe,
               "exe_sha256": common.sha256(args.exe), "cases": [],
               "exit": [r[0] for r in res], "wall_s": [round(r[1], 1) for r in res]}
    ok = all(r[0] == 0 for r in res)

    ncell = nx**3
    mu = n/ncell
    pop_sd = np.sqrt((4.0/mu + 2.0/mu**2)/ncell)
    hist_all = {}
    for m in meta:
        rd = m["rundir"]
        h = collide.read_history(os.path.join(rd, "box.coll.hst"))
        snaps = common.snapshots(rd)
        s0, s1 = collide.read_snapshot(snaps[0]), collide.read_snapshot(snaps[-1])
        mass = s0["m"][0]
        w0 = np.sqrt(1.0 + np.sum(s0["u"]**2, axis=1))
        w1 = np.sqrt(1.0 + np.sum(s1["u"]**2, axis=1))
        e0, e1 = common.exact_sum(s0["m"]*w0), common.exact_sum(s1["m"]*w1)
        p0 = [common.exact_sum(s0["m"]*s0["u"][:, k]) for k in range(3)]
        p1 = [common.exact_sum(s1["m"]*s1["u"][:, k]) for k in range(3)]
        pscale = common.exact_sum(s0["m"]*np.linalg.norm(s0["u"], axis=1))
        theta_s = collide.mj_theta_from_w(e0/common.exact_sum(s0["m"]))
        # P3a: pair counting at the cycle of the last snapshot
        xw = (s1["x"] - common.BOX_MIN) % common.BOX_LEN
        idx = np.minimum((xw*nx).astype(np.int64), nx - 1)
        cnt = np.bincount((idx[:, 2]*nx + idx[:, 1])*nx + idx[:, 0], minlength=ncell)
        vcell = (common.BOX_LEN/nx)**3
        sum_w_pred = m["sigma"]*mass*dt/(2.0*vcell)*float(np.sum(cnt*(cnt - 1.0)))
        irec = int(np.argmin(np.abs(h["time"] - s1["time"])))
        p3a = abs(h["sum_W"][irec]/sum_w_pred - 1.0)
        # P3b: kinematics
        vbar = float(h["sum_P"].sum()/h["sum_W"].sum())
        va, sea, sdv = pair_average(s0["u"], 4000000, 1)
        vb, seb, _ = pair_average(s1["u"], 4000000, 2)
        vmc, semc = 0.5*(va + vb), 0.5*np.hypot(sea, seb)
        se_code = sdv/np.sqrt(h["n_tested"].sum())
        vmj = float(collide.mj_vmol(theta_s))
        z3b = (vbar - vmc)/np.hypot(se_code, semc)
        # P3c: counting statistics
        z3c = (h["n_coll"].sum() - h["sum_P"].sum())/np.sqrt(h["sum_P"].sum())
        # P3d: unconditional rate
        nominal = 0.5*n*m["ic"]["rho0"]*m["sigma"]*dt*len(h["time"])
        r3d = h["sum_W"].sum()/nominal - 1.0
        # P3e: still Maxwell-Juttner
        ks = stats.kstest(np.linalg.norm(s1["u"], axis=1), collide.mj_cdf(theta_s))
        # P4: conservation
        ncoll = np.maximum(h["n_coll"], 1.0)
        wmean = e0/common.exact_sum(s0["m"])
        umean = pscale/common.exact_sum(s0["m"])
        case = dict(theta=m["theta"], mode=m["mode"], sigma=m["sigma"], theta_sample=theta_s,
                    gamma_dt=m["gdt"], pmax=m["pmax"],
                    collisions=int(h["n_coll"].sum()), sum_P=float(h["sum_P"].sum()),
                    n_trunc=int(h["n_trunc"].sum()), max_P=float(h["max_P"].max()),
                    max_nsub=int(h["max_nsub"].max()),
                    mean_nsub=float(h["mean_nsub"].mean()),
                    p3a_rel_diff=float(p3a), vbar_code=vbar, vbar_pairs_mc=vmc,
                    vbar_pairs_mc_se=float(semc), vbar_code_se=float(se_code),
                    v_mj_sample_temperature=vmj, v_mj_nominal=float(collide.mj_vmol(m["theta"])),
                    p3b_z=float(z3b), p3b_rel_to_mj=float(vbar/vmj - 1.0),
                    p3c_z=float(z3c), p3d_rel=float(r3d), p3d_sd=float(pop_sd),
                    p3e_ks_p=float(ks.pvalue),
                    energy_rel_change=float((e1 - e0)/e0),
                    momentum_change_over_scale=[float((p1[k] - p0[k])/pscale) for k in range(3)],
                    pair_dE_eps=float(np.max(h["abs_dE"]/ncoll)/(EPS*2.0*mass*wmean)),
                    pair_dP_eps=float(np.max(h["abs_dP"]/ncoll)/(EPS*2.0*mass*max(umean, 1.0))),
                    hist_sum_MW_rel_spread=float(np.ptp(h["sum_MW"])/h["sum_MW"][0]))
        case["pass"] = bool(p3a < 1e-12 and abs(z3b) < 4.0 and abs(vbar/vmj - 1.0) < 3e-3
                            and abs(z3c) < 4.0 and abs(r3d) < 4.0*pop_sd
                            and ks.pvalue > 1e-3 and case["n_trunc"] == 0
                            and abs(case["energy_rel_change"]) < 1e-13
                            and max(abs(v) for v in case["momentum_change_over_scale"]) < 1e-13
                            and case["pair_dE_eps"] < 8.0 and case["pair_dP_eps"] < 5.0)
        ok = ok and case["pass"]
        summary["cases"].append(case)
        hist_all[(m["theta"], m["mode"])] = (h, nominal/len(h["time"]), vmj)

    # P2: null runs
    import filecmp
    a = common.snapshots(os.path.join(out, "null_off"))[-1]
    b = common.snapshots(os.path.join(out, "null_sigma0"))[-1]
    summary["null_identical_snapshots"] = bool(filecmp.cmp(a, b, shallow=False))
    summary["null_off_has_no_coll_history"] = not os.path.exists(
        os.path.join(out, "null_off", "box.coll.hst"))
    ok = ok and summary["null_identical_snapshots"] and summary["null_off_has_no_coll_history"]
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    # figure 1: collisions per step against the expectation, per temperature
    fig, axs = plt.subplots(2, len(thetas), figsize=(8.0, 4.2), sharex=True, squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.11, top=0.93, wspace=0.32,
                        hspace=0.08)
    for i, th in enumerate(thetas):
        for mode, col in (("plain", fs.PAL["blue"]), ("subcycled", fs.PAL["red"])):
            h, nom, vmj = hist_all[(th, mode)]
            axs[0, i].plot(h["time"], h["sum_P"]/h["sum_W"]/vmj, color=col, lw=0.8,
                           label=mode)
            axs[1, i].plot(h["time"], h["n_coll"]/h["sum_P"], color=col, lw=0.8)
        axs[0, i].axhline(1.0, **fs.GUIDE)
        axs[1, i].axhline(1.0, **fs.GUIDE)
        axs[0, i].set_title(rf"$\theta = {th:g}$", fontsize=10)
        axs[1, i].set_xlabel("time", labelpad=-2)
    axs[0, 0].set_ylabel(r"$\Sigma P/\Sigma W\,/\,\langle v_{\rm Mol}\rangle(\theta_s)$")
    axs[1, 0].set_ylabel(r"collisions / $\Sigma P$")
    axs[0, 0].legend(fontsize=8, loc="upper right")
    fig.savefig(os.path.join(out, "fig_rate_history.png"), dpi=200)

    # figure 2: summary against temperature
    fig, axs = plt.subplots(1, 3, figsize=(8.0, 2.8))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.93, wspace=0.42)
    for mode, col, mk in (("plain", fs.PAL["blue"], "o"), ("subcycled", fs.PAL["red"], "s")):
        cs = [c for c in summary["cases"] if c["mode"] == mode]
        tt = np.array([c["theta"] for c in cs])
        axs[0].errorbar(tt, [c["vbar_code"]/c["vbar_pairs_mc"] - 1.0 for c in cs],
                        yerr=[np.hypot(c["vbar_code_se"], c["vbar_pairs_mc_se"])/c["vbar_pairs_mc"]
                              for c in cs], color=col, marker=mk, ls="none", ms=4,
                        capsize=2, label=mode)
        axs[1].plot(tt, [c["p3b_rel_to_mj"] for c in cs], color=col, marker=mk, ls="none",
                    ms=4)
        axs[2].errorbar(tt, [c["p3d_rel"] for c in cs], yerr=[c["p3d_sd"] for c in cs],
                        color=col, marker=mk, ls="none", ms=4, capsize=2)
    tg = np.logspace(np.log10(min(thetas)) - 0.3, np.log10(max(thetas)) + 0.3, 50)
    for ax in axs:
        ax.axhline(0.0, **fs.GUIDE)
        ax.set_xscale("log")
        ax.set_xlabel(r"$\theta = T/m$")
    axs[0].set_ylabel(r"$\bar v_{\rm code}/\bar v_{\rm pairs} - 1$")
    axs[1].set_ylabel(r"$\bar v_{\rm code}/\langle v_{\rm Mol}\rangle_{\rm MJ}(\theta_s) - 1$")
    axs[2].set_ylabel(r"$\Sigma W$ / nominal $- 1$")
    axs[0].legend(fontsize=8)
    fig.savefig(os.path.join(out, "fig_rate_summary.png"), dpi=200)

    # figure 3: conservation
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 2.8))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.93, wspace=0.3)
    cols = fs.series_colors(len(thetas))
    for i, th in enumerate(thetas):
        h, _, _ = hist_all[(th, "plain")]
        nc = np.maximum(h["n_coll"], 1.0)
        axs[0].semilogy(h["time"], h["abs_dE"]/nc/(h["sum_MW"]/h["n_part"]*2.0)/EPS,
                        color=cols[i], lw=0.8, label=rf"$\theta={th:g}$")
        axs[1].plot(h["time"], (h["sum_MW"] - h["sum_MW"][0])/h["sum_MW"][0]/EPS,
                    color=cols[i], lw=0.8)
    axs[0].set_ylabel(r"mean $|\Delta E_{\rm pair}|$ / $\epsilon E_{\rm pair}$")
    axs[1].set_ylabel(r"$(\Sigma MW - \Sigma MW_0)/\Sigma MW_0$ / $\epsilon$")
    for ax in axs:
        ax.set_xlabel("time")
    axs[0].legend(fontsize=8, ncol=2)
    fig.savefig(os.path.join(out, "fig_rate_conservation.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
