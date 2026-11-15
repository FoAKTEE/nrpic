#!/usr/bin/env python3
"""P5, P6: relaxation of non-thermal starts to the Maxwell-Juttner distribution fixed
by the conserved energy, and the growth of the entropy estimate.

  run_relax.py OUTDIR [--exe ATHENA] [--n 400000] [--nproc 4] [--analyse-only]

Cases: shell_0.3, shell_2 (monoenergetic isotropic shell |u| = u0) and twotemp_0.01,
twotemp_1 (two Maxwell-Juttner populations, theta_1 = 3 theta_2, equal numbers). Each
runs for 25 collision times of the final state at Gamma dt = 0.05.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import common
from nrpic import collide

CASES = [("shell_0.3", "shell", dict(u0=0.3)), ("shell_2", "shell", dict(u0=2.0)),
         ("twotemp_0.01", "twotemp", dict(theta=0.03, theta2=0.01)),
         ("twotemp_1", "twotemp", dict(theta=3.0, theta2=1.0))]


def theta_and_se(u):
    """Temperature from the mean energy of a sample, and its standard error."""
    w = np.sqrt(1.0 + np.sum(u*u, axis=1))
    th = collide.mj_theta_from_w(w.mean())
    dw = (collide.mj_mean_w(th*1.001) - collide.mj_mean_w(th*0.999))/(0.002*th)
    return th, w.std()/np.sqrt(len(w))/dw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--nx", type=int, default=16)
    ap.add_argument("--nproc", type=int, default=4)
    ap.add_argument("--tcoll", type=float, default=25.0)
    ap.add_argument("--gdt", type=float, default=0.05)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--extra", default="")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, nx, dt = args.n, args.nx, 0.01
    steps = int(round(args.tcoll/args.gdt))
    snap_every = int(round(1.0/args.gdt))
    extra = [e for e in args.extra.split(",") if e]
    mesh = [f"mesh/nx{d}={nx}" for d in (1, 2, 3)] + [f"meshblock/nx{d}={nx}"
                                                      for d in (1, 2, 3)]
    jobs, meta = [], []
    for name, kind, kw in CASES:
        rd = os.path.join(out, name)
        ic = os.path.join(out, name + ".nrp")
        if kind == "shell":
            w_mean = np.sqrt(1.0 + kw["u0"]**2)
        else:
            w_mean = 0.5*(collide.mj_mean_w(kw["theta"]) + collide.mj_mean_w(kw["theta2"]))
        theta_eq = collide.mj_theta_from_w(w_mean)
        gamma = args.gdt/dt
        sigma = gamma/float(collide.mj_vmol(theta_eq))
        if not args.analyse_only:
            common.make_box(ic, kind, n, seed=21, **kw)
        ov = mesh + [f"particles/particle_file={ic}", f"particles/dt={dt}",
                     f"particles/coll_sigma={sigma!r}", "particles/coll_pmax=0.1",
                     f"particles/snap_dt={snap_every*dt!r}", f"time/nlim={steps}",
                     "time/tlim=1.0e9", "job/rng_seed=202"] + extra
        jobs.append((args.exe, common.DECK_BOX, rd, ov))
        meta.append(dict(name=name, kind=kind, kw=kw, rundir=rd, theta_eq_nominal=theta_eq,
                         sigma=sigma, gamma=gamma))
    summary = {"n": n, "nx": nx, "steps": steps, "dt": dt, "exe": args.exe,
               "exe_sha256": common.sha256(args.exe), "cases": []}
    ok = True
    if not args.analyse_only:
        res = common.run_many(jobs, args.nproc)
        summary["exit"] = [r[0] for r in res]
        summary["wall_s"] = [round(r[1], 1) for r in res]
        ok = all(r[0] == 0 for r in res)

    series = {}
    for m in meta:
        snaps = [collide.read_snapshot(p) for p in common.snapshots(m["rundir"])]
        h = collide.read_history(os.path.join(m["rundir"], "box.coll.hst"))
        s0 = snaps[0]
        wmean = common.exact_sum(s0["m"]*np.sqrt(1.0 + np.sum(s0["u"]**2, axis=1))) \
            / common.exact_sum(s0["m"])
        theta_eq = collide.mj_theta_from_w(wmean)
        s_mj = float(collide.mj_entropy(theta_eq))
        # Bias and scatter of the entropy estimate at fixed energy, from exact
        # Maxwell-Juttner samples of the same size: each sample is compared with the
        # exact entropy at its own temperature (from its mean energy), because the run
        # has a fixed energy and the energy of a sample fluctuates.
        gen = np.random.default_rng(5)
        ref = []
        for _ in range(16):
            us = collide.mj_sample(theta_eq, gen.random(n))
            ths = collide.mj_theta_from_w(np.mean(np.sqrt(1.0 + us*us)))
            ref.append(collide.entropy_estimate(us, theta_eq)[0]
                       - float(collide.mj_entropy(ths)))
        bias, s_ref_sd = float(np.mean(ref)), float(np.std(ref, ddof=1))
        s_ref = s_mj + bias
        t, ent, ent_se, ksp, pres = [], [], [], [], []
        th_pop = [[], []]
        th_pop_se = [[], []]
        cdf = collide.mj_cdf(theta_eq)
        for s in snaps:
            um = np.linalg.norm(s["u"], axis=1)
            e, se = collide.entropy_estimate(um, theta_eq)
            t.append(s["time"]*m["gamma"])
            ent.append(e)
            ent_se.append(se)
            ksp.append(stats.kstest(um, cdf).pvalue)
            w = np.sqrt(1.0 + um*um)
            pres.append((np.mean(um*um/w)/3.0, np.std(um*um/w)/3.0/np.sqrt(len(um))))
            if m["kind"] == "twotemp":
                for k in (0, 1):
                    th, tse = theta_and_se(s["u"][s["species"] == k])
                    th_pop[k].append(th)
                    th_pop_se[k].append(tse)
        t, ent, ent_se = np.array(t), np.array(ent), np.array(ent_se)
        # monotonic growth: pairs of snapshots at least a quarter relaxation time apart
        # (relaxation time taken as 1.5 collision times)
        worst = 0.0
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                if t[j] - t[i] >= 0.25*1.5:
                    z = (ent[j] - ent[i])/(np.sqrt(2.0)*s_ref_sd)
                    worst = min(worst, z)
        late = t >= 20.0
        end_z = (ent[-1] - s_ref)/s_ref_sd
        late_z = (float(np.mean(ent[late])) - s_ref)/(s_ref_sd/np.sqrt(np.count_nonzero(late)))
        case = dict(name=m["name"], theta_eq=theta_eq, theta_eq_nominal=m["theta_eq_nominal"],
                    sigma=m["sigma"], collisions_per_particle=float(2.0*h["n_coll"].sum()/n),
                    n_trunc=int(h["n_trunc"].sum()), max_nsub=int(h["max_nsub"].max()),
                    entropy_start=float(ent[0]), entropy_end=float(ent[-1]),
                    entropy_end_se=float(ent_se[-1]), entropy_mj_exact=s_mj,
                    entropy_estimator_bias_on_mj_samples=bias,
                    entropy_estimator_sd_at_fixed_energy=s_ref_sd,
                    entropy_end_z=float(end_z), entropy_late_mean_z=float(late_z),
                    entropy_late_sd=float(np.std(ent[late], ddof=1)),
                    entropy_worst_decrease_z=float(worst),
                    ks_p_start=float(ksp[0]), ks_p_end=float(ksp[-1]),
                    ks_p_late_min=float(np.min(np.array(ksp)[late])),
                    pressure_theta_end=float(pres[-1][0]),
                    pressure_z_end=float((pres[-1][0] - theta_eq)/pres[-1][1]),
                    energy_rel_change=float(
                        common.exact_sum(snaps[-1]["m"]*np.sqrt(1.0 + np.sum(snaps[-1]["u"]**2, axis=1)))
                        / common.exact_sum(s0["m"]*np.sqrt(1.0 + np.sum(s0["u"]**2, axis=1))) - 1.0))
        good = (case["ks_p_end"] > 1e-3 and abs(case["pressure_z_end"]) < 4.0
                and worst > -4.0 and abs(end_z) < 4.0 and case["n_trunc"] == 0
                and abs(case["energy_rel_change"]) < 1e-13)
        if m["kind"] == "twotemp":
            case["theta_pop_start"] = [th_pop[0][0], th_pop[1][0]]
            case["theta_pop_end"] = [th_pop[0][-1], th_pop[1][-1]]
            case["theta_pop_end_z"] = [float((th_pop[k][-1] - theta_eq)/th_pop_se[k][-1])
                                       for k in (0, 1)]
            good = good and all(abs(z) < 4.0 for z in case["theta_pop_end_z"])
        case["pass"] = bool(good)
        ok = ok and case["pass"]
        summary["cases"].append(case)
        series[m["name"]] = dict(t=t, ent=ent, ent_se=np.full(len(t), s_ref_sd),
                                 ksp=np.array(ksp), snaps=snaps,
                                 theta_eq=theta_eq, s_mj=s_mj, s_ref=s_ref, th_pop=th_pop,
                                 kind=m["kind"])
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    # figure 1: distributions of the kinetic energy at several times against MJ
    fig, axs = plt.subplots(1, 4, figsize=(8.0, 2.7))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.18, top=0.9, wspace=0.34)
    for ax, (name, sr) in zip(axs, series.items()):
        th = sr["theta_eq"]
        edges = np.linspace(0.0, 4.0, 81)
        xc = 0.5*(edges[1:] + edges[:-1])
        # reference: exact MJ density of q = sqrt((W - 1)/theta)
        cdf = collide.mj_cdf(th)
        w_e = 1.0 + th*edges**2
        ref = np.diff(cdf(np.sqrt(w_e*w_e - 1.0)))/np.diff(edges)
        picks = [0, 1, 3, len(sr["snaps"]) - 1]
        cols = fs.series_colors(len(picks))
        for c, i in zip(cols, picks):
            s = sr["snaps"][i]
            q = np.sqrt((np.sqrt(1.0 + np.sum(s["u"]**2, axis=1)) - 1.0)/th)
            hh, _ = np.histogram(q, bins=edges, density=True)
            ax.plot(xc, hh, color=c, lw=1.0, label=rf"$\Gamma t = {sr['t'][i]:.0f}$")
        ax.plot(xc, ref, **fs.GUIDE)
        ax.set_ylim(0.0, 1.6*ref.max())
        ax.set_xlabel(r"$[(W-1)/\theta_{\rm eq}]^{1/2}$")
        ax.set_title(name.replace("_", " "), fontsize=9)
    axs[0].set_ylabel("probability density")
    axs[0].legend(fontsize=6.5, loc="upper right")
    fig.savefig(os.path.join(out, "fig_relax_distributions.png"), dpi=200)

    # figure 2: entropy estimate and KS p-value against time
    fig, axs = plt.subplots(2, 4, figsize=(8.0, 4.0), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.12, top=0.93, wspace=0.42,
                        hspace=0.08)
    for i, (name, sr) in enumerate(series.items()):
        axs[0, i].plot(sr["t"], sr["s_ref"] - sr["ent"], color=fs.PAL["red"], marker="o",
                       ms=2.5, lw=1.0)
        axs[0, i].fill_between(sr["t"], sr["s_ref"] - sr["ent"] - 4*sr["ent_se"],
                               sr["s_ref"] - sr["ent"] + 4*sr["ent_se"],
                               color=fs.PAL["red"], alpha=0.2, lw=0)
        axs[0, i].set_yscale("symlog", linthresh=10.0*sr["ent_se"][0])
        axs[0, i].axhline(0.0, **fs.GUIDE)
        axs[0, i].set_title(name.replace("_", " "), fontsize=9)
        axs[1, i].semilogy(sr["t"], np.maximum(sr["ksp"], 1e-300), color=fs.PAL["red"],
                           marker="o", ms=2.5, lw=1.0)
        axs[1, i].axhline(1e-3, **fs.GUIDE)
        axs[1, i].set_ylim(1e-12, 3.0)
        axs[1, i].set_xlabel(r"$\Gamma t$ (collision times)", labelpad=-1)
    axs[0, 0].set_ylabel(r"$s_{\rm MJ} + b - s(t)$")
    axs[1, 0].set_ylabel("KS p-value against MJ")
    fig.savefig(os.path.join(out, "fig_relax_entropy.png"), dpi=200)

    # figure 3: population temperatures of the two-temperature starts
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 2.8))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.9, wspace=0.28)
    k = 0
    for name, sr in series.items():
        if sr["kind"] != "twotemp":
            continue
        ax = axs[k]
        k += 1
        ax.plot(sr["t"], np.array(sr["th_pop"][0])/sr["theta_eq"], color=fs.PAL["red"],
                label="population 1 (hot)")
        ax.plot(sr["t"], np.array(sr["th_pop"][1])/sr["theta_eq"], color=fs.PAL["blue"],
                label="population 2 (cold)")
        ax.axhline(1.0, **fs.GUIDE)
        ax.set_xlabel(r"$\Gamma t$ (collision times)")
        ax.set_ylabel(r"$\theta(\langle W\rangle)/\theta_{\rm eq}$")
        ax.set_title(name.replace("_", " "), fontsize=9)
        ax.set_xlim(0.0, 12.0)
    axs[0].legend(fontsize=8)
    fig.savefig(os.path.join(out, "fig_relax_temperatures.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
