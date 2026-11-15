#!/usr/bin/env python3
"""T1 (conservation, per step, on every T2 run) and T2 (collision rate) of
collide/TESTS.md with the release executable, plus the processor cost per pair.

    python3 t1t2.py DESIGN_JSON [--n 1000000] [--steps 200] [--nproc 8] [--exe PATH]
                    [--tag cpu]

Runs (each with the two seeds (make_box seed, rng_seed) = (1, 1) and (2, 2)):
  mj box, N = 1e6, 32^3 cells, theta in {1e-3, 0.1, 1, 10}, 200 steps;
  variant "plain": sigma and dt of the design run (max P ~ 0.02, one sub-step);
  variant "sub":   sigma x 25 at the same dt (max P before sub-cycling ~ 0.5);
  baselines "off" at theta = 0.1 and 10 with collisions = false (cost of the push).
Criteria (TESTS.md, fixed in wave 1):
  T2 (a) sum n_coll within 4 sqrt(sum sum_P) of sum sum_P;
     (b) mean sum_P per step within 4 standard errors (step-to-step scatter) and within
         0.5 percent of (1/2) N rho_0 sigma <v_Mol>(theta) dt, theta = temperature of the
         gas from <W - 1> of the initial snapshot (as in (c));
     (c) theta from <W - 1> constant within 4 sigma (initial against final snapshot).
  T1 per step: |dE| / sum_MW and |dP_i| / sum_MW below 1e-14 sqrt(n_coll + 1)
     (coll.hst columns 20-23 and 16), n_trunc = 0; exactly rounded sums of M W and M u_i
     of the initial and final snapshots reported as an independent check.
Writes t1t2_<tag>.json and figures t2_rate_<tag>.png, t1_step_<tag>.png into
$NRPIC_RUN_DIR.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import boxlib as bl
import mj
import rate

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

THETAS = ("0.001", "0.1", "1.0", "10.0")
SEEDS = (1, 2)


def theta_of(u):
    k = bl.snap.kinetic_flat(u)
    kb = float(k.mean())
    se = float(k.std() / np.sqrt(k.size))
    th = float(mj.theta_from_kinetic(kb))
    return th, se / float(mj.c_v(th))


def analyse(rd, meta, steps):
    h = bl.coll_history(rd)
    files = bl.snapshots(rd)
    s0 = bl.snap.read_snapshot(files[0])
    s1 = bl.snap.read_snapshot(files[-1])
    N = int(h["n_part"][0])
    dt = float(np.diff(np.concatenate([[0.0], h["time"]])).mean())
    th_nom = float(meta["theta"])
    th0, se0 = theta_of(s0["u"])
    th1, se1 = theta_of(s1["u"])
    rho0 = float(meta["rho0"])
    sig = float(meta["sigma"])
    exp_sample = 0.5 * N * rho0 * sig * float(rate.vmol_mean(th0)) * dt
    exp_nom = 0.5 * N * rho0 * sig * float(rate.vmol_mean(th_nom)) * dt
    sP, nc = h["sum_P"], h["n_coll"]
    se_step = float(sP.std(ddof=1) / np.sqrt(sP.size))
    r = dict(run=rd, steps=int(h["ncycle"].size), last_cycle=int(h["ncycle"][-1]), N=N,
             dt=dt, sigma=sig, theta_nominal=th_nom, theta0=th0, theta0_se=se0,
             theta_end=th1, theta_end_se=se1, collisions=float(nc.sum()),
             sum_P=float(sP.sum()), n_trunc=float(h["n_trunc"].sum()),
             max_P=float(h["max_P"].max()), max_nsub=float(h["max_nsub"].max()),
             mean_nsub=float(h["mean_nsub"].mean()), mean_N=float(h["mean_N"].mean()),
             min_N=float(h["min_N"].min()), n_tested=float(h["n_tested"].sum()),
             sumP_per_step=float(sP.mean()), sumP_per_step_se=se_step,
             expected_per_step=exp_sample, expected_per_step_nominal=exp_nom,
             ratio_b=float(sP.mean() / exp_sample),
             ratio_b_nominal=float(sP.mean() / exp_nom),
             # diagnostics: mean Moller speed of tested pairs, pair weight
             vmol_tested=float(sP.sum() / h["sum_W"].sum()),
             vmol_ref=float(rate.vmol_mean(th0)),
             sumW_ratio=float(h["sum_W"].mean() / (0.5 * N * rho0 * sig * dt)))
    r["T2a_z"] = float((nc.sum() - sP.sum()) / np.sqrt(sP.sum()))
    r["T2a_pass"] = bool(abs(r["T2a_z"]) < 4)
    r["T2b_z"] = float((sP.mean() - exp_sample) / se_step)
    r["T2b_pass"] = bool(abs(r["T2b_z"]) < 4 and abs(r["ratio_b"] - 1) < 0.005)
    r["T2b_z_nominal"] = float((sP.mean() - exp_nom) / se_step)
    r["T2c_z"] = float((th1 - th0) / np.hypot(se0, se1))
    r["T2c_pass"] = bool(abs(r["T2c_z"]) < 4)
    # diagnostic: end state against MJ(theta0)
    absu = np.sqrt(np.sum(s1["u"] ** 2, 1))
    r["ks_end_p"] = float(stats.kstest(absu, mj.Sampler(th0).cdf_u).pvalue)
    # T1 per step
    smw = h["sum_MW"]
    bound = 1e-14 * np.sqrt(nc + 1)
    relE = np.abs(h["dE"]) / smw
    relP = np.max(np.abs(np.stack([h["dP1"], h["dP2"], h["dP3"]])), axis=0) / smw
    r.update(T1_max_relE=float(relE.max()), T1_max_relP=float(relP.max()),
             T1_max_relE_over_bound=float((relE / bound).max()),
             T1_max_relP_over_bound=float((relP / bound).max()),
             T1_mean_abs_dE_per_coll_rel=float((h["abs_dE"] / np.maximum(nc, 1)).mean()
                                               / (smw[0] / N)))
    r["T1_step_pass"] = bool((relE < bound).all() and (relP < bound).all() and
                             r["n_trunc"] == 0)
    # independent: exactly rounded sums of the snapshots
    e0 = bl.fsum_cols((s0["m"] * bl.W(s0["u"]))[:, None])[0]
    e1 = bl.fsum_cols((s1["m"] * bl.W(s1["u"]))[:, None])[0]
    p0 = bl.fsum_cols(s0["m"][:, None] * s0["u"])
    p1 = bl.fsum_cols(s1["m"][:, None] * s1["u"])
    r.update(snap_t0=s0["time"], snap_t1=s1["time"], snap_cycle1=s1["cycle"],
             exact_dE_rel=float((e1 - e0) / e0),
             exact_dP_rel=float(np.max(np.abs(p1 - p0)) / e0),
             mass_identical=bool(np.array_equal(s0["m"], s1["m"])),
             series=dict(sumP=(sP / exp_sample).tolist(), ncoll=(nc / exp_sample).tolist(),
                         relE=relE.tolist(), relP=relP.tolist(), bound=bound.tolist(),
                         vmol=(sP / h["sum_W"] / r["vmol_ref"]).tolist(),
                         sumW=(h["sum_W"] / (0.5 * N * rho0 * sig * dt)).tolist()))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--nproc", type=int, default=8)
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    ap.add_argument("--only", default=None, help="comma list of thetas")
    a = ap.parse_args()
    des = json.load(open(a.design))["T2"]
    out = bl.outdir()
    thetas = a.only.split(",") if a.only else THETAS
    jobs, runs = [], []
    for th in thetas:
        d = des[th]
        for var in ("plain", "sub", "off"):
            if var == "off" and th not in ("0.1", "10.0"):
                continue
            sig = d["sigma"] * (25.0 if var == "sub" else 1.0)
            for seed in (SEEDS if var != "off" else SEEDS[:1]):
                name = f"T2_th{th}_{var}_s{seed}"
                rd = os.path.join(out, name)
                meta = bl.make_box(rd, "mj", n=a.n, theta=float(th), sigma=sig, seed=seed)
                ov = bl.mesh_overrides(32) + [
                    f"particles/dt={d['dt']!r}", f"time/nlim={a.steps}",
                    f"particles/coll_sigma={sig!r}",
                    f"particles/snap_dt={a.steps * d['dt'] * (1 - 1e-9)!r}",
                    f"job/rng_seed={seed}"]
                if var == "off":
                    ov.append("particles/collisions=false")
                jobs.append((rd, ov, dict(exe=a.exe)))
                runs.append((name, rd, meta, var, th, seed))
    res_run = bl.run_many(jobs, a.nproc)
    results = {}
    for (name, rd, meta, var, th, seed), rr in zip(runs, res_run):
        if rr["rc"] != 0:
            results[name] = dict(rc=rr["rc"], wall=rr["wall"], failed=True)
            continue
        if var == "off":
            results[name] = dict(rc=0, wall=rr["wall"], steps=a.steps, var=var, theta=th)
            continue
        r = analyse(rd, meta, a.steps)
        r.update(rc=0, wall=rr["wall"], var=var, theta=th, seed=seed)
        results[name] = r
    # cost per pair (processor or card): (wall - wall_off)/(tested pairs)
    for name, r in results.items():
        if r.get("var") in ("plain", "sub") and not r.get("failed"):
            off = results.get(f"T2_th{r['theta']}_off_s1") or results.get("T2_th0.1_off_s1")
            if off and not off.get("failed"):
                r["cost_per_tested_pair_s"] = (r["wall"] - off["wall"]) / r["n_tested"]
                r["cost_per_particle_step_s"] = (r["wall"] - off["wall"]) / (r["N"] * a.steps)
                r["wall_per_step_s"] = r["wall"] / a.steps
                r["wall_off_per_step_s"] = off["wall"] / a.steps
    summ = dict(tag=a.tag, exe=a.exe, runs={k: {kk: vv for kk, vv in v.items()
                                                 if kk != "series"}
                                             for k, v in results.items()})
    ok = [v for v in results.values() if v.get("var") in ("plain", "sub")]
    summ["T2_pass"] = bool(ok and all(v.get("T2a_pass") and v.get("T2b_pass") and
                                      v.get("T2c_pass") for v in ok))
    summ["T1_step_pass"] = bool(ok and all(v.get("T1_step_pass") for v in ok))
    summ["any_failed_run"] = any(v.get("failed") for v in results.values())
    bl.save_json(os.path.join(out, f"t1t2_{a.tag}.json"), summ)
    figures(results, out, a.tag)
    print(json.dumps({k: {kk: vv for kk, vv in v.items()
                          if kk in ("ratio_b", "T2a_z", "T2b_z", "T2c_z", "T2a_pass",
                                    "T2b_pass", "T2c_pass", "T1_step_pass", "max_P",
                                    "max_nsub", "wall", "n_trunc", "vmol_tested",
                                    "vmol_ref", "ks_end_p", "cost_per_tested_pair_s")}
                      for k, v in summ["runs"].items()}, indent=1))
    print("T2_pass", summ["T2_pass"], "T1_step_pass", summ["T1_step_pass"])


def figures(results, out, tag):
    fs.use_style()
    cols = {"0.001": fs.PAL["blue"], "0.1": fs.PAL["red"], "1.0": fs.PAL["yellow"],
            "10.0": fs.PAL["green"]}
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax1 = fig.add_axes([0.08, 0.15, 0.24, 0.79])
    ax2 = fig.add_axes([0.42, 0.15, 0.23, 0.79])
    ax3 = fig.add_axes([0.75, 0.15, 0.23, 0.79])
    xs, labels = [], []
    k = 0
    for name, r in sorted(results.items()):
        if r.get("var") not in ("plain", "sub") or r.get("failed"):
            continue
        c = cols[r["theta"]]
        ls = "-" if r["var"] == "plain" else "--"
        s = np.array(r["series"]["sumP"])
        if r["seed"] == 1:
            ax1.plot(np.arange(1, s.size + 1), s, ls=ls, color=c, lw=0.8,
                     label=rf"$\theta={r['theta']}$ {r['var']}")
        ax2.errorbar(k, r["ratio_b"] - 1, yerr=r["sumP_per_step_se"] / r["expected_per_step"],
                     fmt="o" if r["var"] == "plain" else "s", color=c, ms=4,
                     mfc=c if r["seed"] == 1 else "none")
        ax2.plot(k, r["ratio_b_nominal"] - 1, "x", color="k", ms=3)
        ax3.plot(k, r["T2a_z"], "o" if r["var"] == "plain" else "s", color=c, ms=4,
                 mfc=c if r["seed"] == 1 else "none")
        ax3.plot(k, (r["vmol_tested"] / r["vmol_ref"] - 1) * 1e3, "^", color="grey", ms=3)
        xs.append(k); labels.append(f"{r['theta']}\n{r['var'][0]}{r['seed']}")
        k += 1
    ax1.axhline(1, **fs.GUIDE)
    ax1.set_xlabel("step"); ax1.set_ylabel(r"$\Sigma P$ per step / expected")
    ax1.legend(loc="upper right", fontsize=7, ncol=2)
    ax1.set_ylim(0.985, 1.02)
    ax2.axhspan(-0.005, 0.005, color="grey", alpha=0.15)
    ax2.axhline(0, **fs.GUIDE)
    ax2.set_xticks(xs); ax2.set_xticklabels(labels, fontsize=6)
    ax2.set_ylabel(r"$\overline{\Sigma P}$/expected $-$ 1  (x: nominal $\theta$)", fontsize=8)
    ax3.axhspan(-4, 4, color="grey", alpha=0.15)
    ax3.axhline(0, **fs.GUIDE)
    ax3.set_xticks(xs); ax3.set_xticklabels(labels, fontsize=6)
    ax3.set_ylabel(r"$z_a$;  $\triangle$: $10^3(\bar v_{\rm Mol}/\langle v_{\rm Mol}\rangle-1)$",
                   fontsize=8)
    bl.os.makedirs(out, exist_ok=True)
    fs.save(fig, os.path.join(out, f"t2_rate_{tag}"))
    plt.close(fig)
    # T1 per step
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax1 = fig.add_axes([0.08, 0.15, 0.40, 0.78])
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    for name, r in sorted(results.items()):
        if r.get("var") not in ("plain", "sub") or r.get("failed") or r["seed"] != 1:
            continue
        c = cols[r["theta"]]
        ls = "-" if r["var"] == "plain" else "--"
        b = np.array(r["series"]["bound"])
        ax1.semilogy(np.maximum(np.array(r["series"]["relE"]), 1e-30), ls=ls, color=c, lw=0.8,
                     label=rf"$\theta={r['theta']}$ {r['var']}")
        ax1.semilogy(b, ls=":", color=c, lw=0.8)
        ax2.semilogy(np.maximum(np.array(r["series"]["relP"]), 1e-30), ls=ls, color=c, lw=0.8)
        ax2.semilogy(b, ls=":", color=c, lw=0.8)
    ax1.set_xlabel("step"); ax1.set_ylabel(r"$|dE|/\Sigma MW$ per step (dotted: bound)")
    ax2.set_xlabel("step"); ax2.set_ylabel(r"$\max_i|dP_i|/\Sigma MW$ per step")
    ax1.legend(loc="lower right", fontsize=7, ncol=2)
    for ax in (ax1, ax2):
        ax.set_ylim(1e-22, 1e-10)
    fs.save(fig, os.path.join(out, f"t1_step_{tag}"))
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
