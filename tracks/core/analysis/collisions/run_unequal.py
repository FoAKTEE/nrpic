#!/usr/bin/env python3
"""Unequal rest masses of macroparticles (coll_weights = nanbu): two classes of equal
number with masses 1 : 4 and temperatures theta = 0.03 (light) and 0.01 (heavy).

  run_unequal.py OUTDIR [--exe ATHENA] [--n 200000] [--nproc 5] [--seeds 4]

Checked: with coll_weights = equal the run stops with an error naming the masses; with
nanbu both classes end at one temperature and Maxwell-Juttner; the momentum updates per
collision approach 20/13 (pairs light-light and heavy-heavy update two particles, mixed
pairs 5/4, weighted with the pair probabilities 1 : 4 : 8); light and heavy particles
are updated equally often; the energy and momentum defects recorded in the history sum
to the change measured from the snapshots, and their mean over the seeds is zero within
errors.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import common
from nrpic import collide

TH_LIGHT, TH_HEAVY = 0.03, 0.01
DUMP_CYCLE = 300


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--nx", type=int, default=16)
    ap.add_argument("--nproc", type=int, default=5)
    ap.add_argument("--seeds", type=int, default=4)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, nx, dt = args.n, args.nx, 0.01
    ic = os.path.join(out, "unequal.nrp")
    info = common.make_box(ic, "unequal", n, seed=81, theta=TH_LIGHT, theta2=TH_HEAVY,
                           mass_ratio=4.0)
    # mass-weighted mean energy fixes the expected final temperature
    w_eq = (1.0*collide.mj_mean_w(TH_LIGHT) + 4.0*collide.mj_mean_w(TH_HEAVY))/5.0
    theta_eq = collide.mj_theta_from_w(w_eq)
    gdt = 0.05
    sigma = gdt/dt/float(collide.mj_vmol(theta_eq))
    steps = int(round(25.0/gdt))
    mesh = [f"mesh/nx{d}={nx}" for d in (1, 2, 3)] + [f"meshblock/nx{d}={nx}"
                                                      for d in (1, 2, 3)]
    base = mesh + [f"particles/particle_file={ic}", f"particles/dt={dt}",
                   f"particles/coll_sigma={sigma!r}", f"particles/snap_dt={steps*dt!r}",
                   f"time/nlim={steps}", "time/tlim=1.0e9",
                   f"particles/coll_dump_cycle={DUMP_CYCLE}"]
    jobs = [(args.exe, common.DECK_BOX, os.path.join(out, "equal_refused"),
             base + ["job/rng_seed=900"])]
    for seed in range(1, args.seeds + 1):
        jobs.append((args.exe, common.DECK_BOX, os.path.join(out, f"nanbu_seed{seed}"),
                     base + ["particles/coll_weights=nanbu", f"job/rng_seed={900 + seed}"]))
    res = common.run_many(jobs, args.nproc)
    log = open(os.path.join(out, "equal_refused", "athena.log")).read()
    summary = {"n": n, "theta_eq_expected": theta_eq, "sigma": sigma, "steps": steps,
               "exe": args.exe, "exe_sha256": common.sha256(args.exe),
               "exit": [r[0] for r in res],
               "equal_refused": bool(res[0][0] != 0 and "unequal rest masses" in log),
               "equal_refused_message": [ln for ln in log.splitlines()
                                         if "unequal rest masses" in ln][:1], "seeds": []}
    ok = summary["equal_refused"] and all(r[0] == 0 for r in res[1:])
    series = []
    for seed in range(1, args.seeds + 1):
        rd = os.path.join(out, f"nanbu_seed{seed}")
        h = collide.read_history(os.path.join(rd, "box.coll.hst"))
        snaps = common.snapshots(rd)
        s0, s1 = collide.read_snapshot(snaps[0]), collide.read_snapshot(snaps[-1])
        light = s0["species"] == 0
        w0 = np.sqrt(1.0 + np.sum(s0["u"]**2, axis=1))
        w1 = np.sqrt(1.0 + np.sum(s1["u"]**2, axis=1))
        e0, e1 = common.exact_sum(s0["m"]*w0), common.exact_sum(s1["m"]*w1)
        mtot = common.exact_sum(s0["m"])
        th_end = collide.mj_theta_from_w(e1/mtot)
        cdf = collide.mj_cdf(th_end)
        um = np.linalg.norm(s1["u"], axis=1)
        dw = (collide.mj_mean_w(th_end*1.001) - collide.mj_mean_w(th_end*0.999))/(0.002*th_end)
        cls = {}
        for name, sel in (("light", light), ("heavy", ~light)):
            th = collide.mj_theta_from_w(np.mean(w1[sel]))
            cls[name] = dict(theta=th, theta_se=float(w1[sel].std()/np.sqrt(sel.sum())/dw),
                             ks_p=float(stats.kstest(um[sel], cdf).pvalue))
        zdiff = (cls["light"]["theta"] - cls["heavy"]["theta"]) \
            / np.hypot(cls["light"]["theta_se"], cls["heavy"]["theta_se"])
        late = h["ncycle"] > steps//2
        upd = h["n_updated"][late].sum()/h["n_coll"][late].sum()
        upd_se = np.sqrt(0.6154*0.25*0.75/h["n_coll"][late].sum())
        # one step: updates of light and of heavy particles
        d = collide.read_dump(os.path.join(rd, f"box.coll_dump.{DUMP_CYCLE}.bin"))
        mlight = d["m"] < 2.0*d["m"].min()
        ul, uh = int(d["nupd"][mlight].sum()), int(d["nupd"][~mlight].sum())
        pm = [common.exact_sum(s["m"]*s["u"][:, k]) for s in (s0, s1) for k in range(3)]
        pscale = common.exact_sum(s0["m"]*np.linalg.norm(s0["u"], axis=1))
        thermal = e0 - mtot
        r = dict(seed=seed, theta_end=th_end, classes=cls, theta_difference_z=float(zdiff),
                 updates_per_collision_late=float(upd),
                 updates_per_collision_z=float((upd - 20.0/13.0)/upd_se),
                 one_step_updates_light_heavy=[ul, uh],
                 one_step_updates_z=float((ul - uh)/np.sqrt(ul + uh)),
                 collisions=int(h["n_coll"].sum()), n_trunc=int(h["n_trunc"].sum()),
                 energy_change_over_thermal=float((e1 - e0)/thermal),
                 energy_change_history_minus_snapshots=float((h["dE"].sum() - (e1 - e0))/thermal),
                 momentum_change_over_scale=[float((pm[3 + k] - pm[k])/pscale) for k in range(3)],
                 momentum_history_minus_snapshots=[float((h[f"dP{k+1}"].sum()
                                                         - (pm[3 + k] - pm[k]))/pscale)
                                                   for k in range(3)])
        r["pass"] = bool(abs(zdiff) < 4.0 and cls["light"]["ks_p"] > 1e-3
                         and cls["heavy"]["ks_p"] > 1e-3
                         and abs(r["updates_per_collision_z"]) < 4.0
                         and abs(r["one_step_updates_z"]) < 4.0 and r["n_trunc"] == 0
                         and abs(r["energy_change_history_minus_snapshots"]) < 1e-9
                         and max(abs(x) for x in r["momentum_history_minus_snapshots"]) < 1e-9)
        ok = ok and r["pass"]
        summary["seeds"].append(r)
        series.append((h, thermal, pscale))
    de = np.array([r["energy_change_over_thermal"] for r in summary["seeds"]])
    dp = np.array([r["momentum_change_over_scale"] for r in summary["seeds"]]).ravel()
    summary["energy_drift_mean"] = float(de.mean())
    summary["energy_drift_sd"] = float(de.std(ddof=1)) if len(de) > 1 else None
    summary["energy_drift_mean_z"] = float(de.mean()/(de.std(ddof=1)/np.sqrt(len(de)))) \
        if len(de) > 1 else None
    summary["momentum_drift_mean_z"] = float(dp.mean()/(dp.std(ddof=1)/np.sqrt(len(dp))))
    summary["momentum_drift_sd"] = float(dp.std(ddof=1))
    if len(de) > 1:
        ok = ok and abs(summary["energy_drift_mean_z"]) < 4.0 \
            and abs(summary["momentum_drift_mean_z"]) < 4.0
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(8.0, 2.8))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.18, top=0.93, wspace=0.45)
    cols = fs.series_colors(len(series))
    for col, (h, thermal, pscale) in zip(cols, series):
        tg = h["time"]*gdt/dt
        axs[0].plot(tg, np.cumsum(h["dE"])/thermal, color=col, lw=1.0)
        axs[1].plot(tg, np.cumsum(h["dP1"])/pscale, color=col, lw=1.0)
        k = 25
        nb = len(tg)//k
        axs[2].plot(tg[:nb*k].reshape(nb, k).mean(axis=1),
                    h["n_updated"][:nb*k].reshape(nb, k).sum(axis=1)
                    / h["n_coll"][:nb*k].reshape(nb, k).sum(axis=1), color=col, lw=1.0)
    axs[0].axhline(0.0, **fs.GUIDE)
    axs[1].axhline(0.0, **fs.GUIDE)
    axs[2].axhline(20.0/13.0, **fs.GUIDE)
    axs[0].set_ylabel("cumulative energy defect / thermal energy")
    axs[1].set_ylabel(r"cumulative defect of $\Sigma M u_x$ / $\Sigma M|u|$")
    axs[2].set_ylabel("momentum updates per collision")
    for ax in axs:
        ax.set_xlabel(r"$\Gamma t$ (collision times)")
    fig.savefig(os.path.join(out, "fig_unequal.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
