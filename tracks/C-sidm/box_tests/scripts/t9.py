#!/usr/bin/env python3
"""T9 of collide/TESTS.md: unequal macroparticle masses (coll_weights = nanbu).

    python3 t9.py DESIGN_JSON [--seeds 1..8] [--n 1000000] [--nproc 8] [--exe PATH]

`make_box.py unequal`: class A of mass M (8e5 particles, theta_A = 0.03), class B of
mass 4M (2e5, theta_B = 0.01), equal total rest mass; sigma = 1, rho_0 = 1, 16^3 cells,
dt = 0.02 tau_rel (design run; tau_rel = 4.985), to 15 tau_rel; 8 seeds.
Criteria (TESTS.md, fixed in wave 1): at the end both classes at the same theta within
4 sigma and both Maxwell-Juttner (KS p > 1e-3; declared before the run: against MJ at the
class's own final temperature, and reported against theta_eq of the initial energy);
total energy and momentum drifts (exactly rounded sums, end minus start) have zero mean
over the seeds within 4 standard errors; with coll_weights = equal the same file stops
at start-up with an error naming the unequal masses.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import boxlib as bl
import mj
import relax as rx

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def theta_of(u):
    k = bl.snap.kinetic_flat(u)
    th = float(mj.theta_from_kinetic(float(k.mean())))
    return th, float(k.std() / np.sqrt(k.size)) / float(mj.c_v(th))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--seeds", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--nproc", type=int, default=8)
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    des = json.load(open(a.design))["T9"]
    tau = des["tau_rel"]
    dt = 0.02 * tau
    nst = int(round(15 * tau / dt))
    out = bl.outdir()
    jobs, cases = [], []
    for seed in [int(s) for s in a.seeds.split(",")]:
        rd = os.path.join(out, f"T9_s{seed}")
        meta = bl.make_box(rd, "unequal", n=a.n, theta=0.03, theta2=0.01, sigma=1.0,
                           seed=seed, wratio=4.0)
        jobs.append((rd, bl.mesh_overrides(16) + [
            f"particles/dt={dt!r}", f"time/nlim={nst}", "particles/coll_sigma=1.0",
            "particles/coll_weights=nanbu", f"particles/snap_dt={75 * dt * (1 - 1e-9)!r}",
            f"job/rng_seed={seed}"], dict(exe=a.exe)))
        cases.append((rd, seed, meta))
    # refusal with coll_weights = equal (seed 1 file, one step)
    rdq = os.path.join(out, "T9_equal_refused")
    os.makedirs(rdq, exist_ok=True)
    jobs.append((rdq, bl.mesh_overrides(16) + [
        f"particles/dt={dt!r}", "time/nlim=1", "particles/coll_sigma=1.0",
        "particles/coll_weights=equal",
        f"particles/particle_file={os.path.join(cases[0][0], 'box.nrp')}"], dict(exe=a.exe)))
    rr = bl.run_many(jobs, a.nproc)
    res = dict(tau_rel=tau, dt=dt, steps=nst, seeds={})
    log = open(os.path.join(rdq, "athena.log")).read()
    res["equal_refused"] = dict(rc=rr[-1]["rc"], log_tail=log[-1500:],
                                names_masses=("mass" in log.lower()))
    dE, dP = [], []
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax1 = fig.add_axes([0.08, 0.15, 0.25, 0.78])
    ax2 = fig.add_axes([0.42, 0.15, 0.25, 0.78])
    ax3 = fig.add_axes([0.76, 0.15, 0.22, 0.78])
    for (rd, seed, meta), r0 in zip(cases, rr[:-1]):
        c = dict(rc=r0["rc"], wall=r0["wall"])
        if r0["rc"]:
            c["failed"] = True
            res["seeds"][seed] = c
            continue
        nA = meta["n_classA"]
        files = bl.snapshots(rd)
        s0 = bl.snap.read_snapshot(files[0])
        s1 = bl.snap.read_snapshot(files[-1])
        A0, A1 = s0["tag"] < nA, s1["tag"] < nA
        thA0, _ = theta_of(s0["u"][A0]); thB0, _ = theta_of(s0["u"][~A0])
        rhoA, rhoB = s0["m"][A0].sum(), s0["m"][~A0].sum()     # V = 1
        th_eq = float(rx.theta_eq(rhoA, rhoB, thA0, thB0))
        thA, seA = theta_of(s1["u"][A1]); thB, seB = theta_of(s1["u"][~A1])
        uA = np.sqrt(np.sum(s1["u"][A1] ** 2, 1)); uB = np.sqrt(np.sum(s1["u"][~A1] ** 2, 1))
        ksA = stats.kstest(uA, mj.Sampler(thA).cdf_u).pvalue
        ksB = stats.kstest(uB, mj.Sampler(thB).cdf_u).pvalue
        ksA_eq = stats.kstest(uA, mj.Sampler(th_eq).cdf_u).pvalue
        ksB_eq = stats.kstest(uB, mj.Sampler(th_eq).cdf_u).pvalue
        e0 = bl.fsum_cols((s0["m"] * bl.W(s0["u"]))[:, None])[0]
        e1 = bl.fsum_cols((s1["m"] * bl.W(s1["u"]))[:, None])[0]
        p0 = bl.fsum_cols(s0["m"][:, None] * s0["u"])
        p1 = bl.fsum_cols(s1["m"][:, None] * s1["u"])
        kin0 = bl.fsum_cols((s0["m"] * bl.snap.kinetic_flat(s0["u"]))[:, None])[0]
        h = bl.coll_history(rd)
        c.update(t_end_over_tau=float(s1["time"] / tau), thetaA0=thA0, thetaB0=thB0,
                 theta_eq=th_eq, thetaA=thA, thetaB=thB, seA=seA, seB=seB,
                 z_same=float((thA - thB) / np.hypot(seA, seB)),
                 ksA=float(ksA), ksB=float(ksB), ksA_eq=float(ksA_eq), ksB_eq=float(ksB_eq),
                 dE=float(e1 - e0), dE_over_kin=float((e1 - e0) / kin0),
                 dP=(p1 - p0).tolist(), collisions=float(h["n_coll"].sum()),
                 updates_per_coll=float(h["n_updated"].sum() / h["n_coll"].sum()),
                 hst_dE_sum=float(h["dE"].sum()), n_trunc=float(h["n_trunc"].sum()),
                 max_nsub=float(h["max_nsub"].max()), mass_identical=bool(
                     np.array_equal(s0["m"], s1["m"])))
        c["pass_seed"] = bool(abs(c["z_same"]) < 4 and ksA > 1e-3 and ksB > 1e-3 and
                              c["n_trunc"] == 0)
        res["seeds"][seed] = c
        dE.append(e1 - e0); dP.append(p1 - p0)
        # figure: class temperatures over time (seed 1, 2 only), drifts
        if seed <= 2:
            T = []
            for f in files:
                s = bl.snap.read_snapshot(f)
                A = s["tag"] < nA
                T.append((s["time"], theta_of(s["u"][A])[0], theta_of(s["u"][~A])[0]))
            T = np.array(T)
            ls = "-" if seed == 1 else "--"
            ax1.plot(T[:, 0] / tau, T[:, 1] / th_eq, ls=ls, marker="o", ms=2.5,
                     color=fs.PAL["red"], label=f"class A (M), seed {seed}")
            ax1.plot(T[:, 0] / tau, T[:, 2] / th_eq, ls=ls, marker="s", ms=2.5, mfc="none",
                     color=fs.PAL["blue"], label=f"class B (4M), seed {seed}")
    dE = np.array(dE); dP = np.array(dP)
    n = len(dE)
    res["dE_mean"] = float(dE.mean()); res["dE_se"] = float(dE.std(ddof=1) / np.sqrt(n))
    res["dP_mean"] = dP.mean(0).tolist(); res["dP_se"] = (dP.std(0, ddof=1) / np.sqrt(n)).tolist()
    res["z_dE"] = res["dE_mean"] / res["dE_se"]
    res["z_dP"] = (dP.mean(0) / (dP.std(0, ddof=1) / np.sqrt(n))).tolist()
    res["pass"] = bool(n == 8 and all(c.get("pass_seed") for c in res["seeds"].values()) and
                       abs(res["z_dE"]) < 4 and all(abs(z) < 4 for z in res["z_dP"]) and
                       res["equal_refused"]["rc"] != 0 and res["equal_refused"]["names_masses"])
    ax1.axhline(1, **fs.GUIDE)
    ax1.set_xlabel(r"$t/\tau_{\rm rel}$"); ax1.set_ylabel(r"$\theta/\theta_{\rm eq}$")
    ax1.legend(loc="upper right", fontsize=7)
    seeds = sorted(res["seeds"])
    ax2.plot(seeds, [res["seeds"][s]["z_same"] for s in seeds], "o", color=fs.PAL["red"],
             label=r"$(\theta_A-\theta_B)/\sigma$")
    ax2.plot(seeds, [np.log10(max(res["seeds"][s]["ksA"], 1e-12)) for s in seeds], "^",
             color=fs.PAL["yellow"], label=r"$\log_{10} p_{\rm KS}$ A")
    ax2.plot(seeds, [np.log10(max(res["seeds"][s]["ksB"], 1e-12)) for s in seeds], "v",
             color=fs.PAL["green"], label=r"$\log_{10} p_{\rm KS}$ B")
    ax2.axhspan(-4, 4, color="grey", alpha=0.12)
    ax2.axhline(-3, **fs.GUIDE)
    ax2.set_xlabel("seed"); ax2.set_ylim(-6, 5)
    ax2.legend(loc="lower right", fontsize=7)
    ax3.errorbar(seeds, [res["seeds"][s]["dE"] for s in seeds], fmt="o", color=fs.PAL["red"],
                 label=r"$\Delta\Sigma MW$")
    for k, col in enumerate((fs.PAL["blue"], fs.PAL["yellow"], fs.PAL["green"])):
        ax3.plot(seeds, [res["seeds"][s]["dP"][k] for s in seeds], "x", color=col,
                 label=rf"$\Delta\Sigma Mu_{k + 1}$")
    ax3.axhline(0, **fs.GUIDE)
    ax3.set_xlabel("seed"); ax3.set_ylabel("drift over the run")
    ax3.legend(loc="best", fontsize=7)
    fs.save(fig, os.path.join(out, f"t9_unequal_{a.tag}"))
    plt.close(fig)
    bl.save_json(os.path.join(out, f"t9_{a.tag}.json"), res)
    print(json.dumps({k: v for k, v in res.items() if k != "seeds"}, indent=1, default=float))
    for s, c in res["seeds"].items():
        print(s, {k: c.get(k) for k in ("z_same", "ksA", "ksB", "ksA_eq", "ksB_eq", "dE_over_kin",
                                         "updates_per_coll", "collisions", "max_nsub", "wall")})


if __name__ == "__main__":
    sys.exit(main())
