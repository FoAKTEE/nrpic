#!/usr/bin/env python3
"""P10: collisions in a static homogeneous curved metric carried by the mesh
(problems/tests/coll_box_curved.athinput: lapse 0.7, constant spatial metric that is not
diagonal). Flat spacetime in oblique coordinates, so everything is known exactly, while
lapse, volume element and triad of the collision cells are not trivial.

  run_curved_box.py OUTDIR [--exe ATHENA] [--n 200000] [--nproc 3]

Runs: symmetric triad with the midpoint pusher; Cholesky triad with the Boris pusher;
and the flat box (analytic metric) with the same triad momenta, the same proper density
and the same collision rate per coordinate time. Two-temperature start, 20 collision
times.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import common
from nrpic import collide

DECK_CURVED = os.path.join(common.REPO, "problems", "tests", "coll_box_curved.athinput")
GMAT = np.array([[1.44, 0.3, -0.2], [0.3, 0.81, 0.15], [-0.2, 0.15, 1.21]])
ALPHA0 = 0.7
TH1, TH2 = 0.6, 0.2
EPS = 2.0**-52


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--nx", type=int, default=16)
    ap.add_argument("--nproc", type=int, default=3)
    ap.add_argument("--steps", type=int, default=400)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, nx, dt, steps = args.n, args.nx, 0.01, args.steps
    sg = float(np.sqrt(np.linalg.det(GMAT)))
    ginv = np.linalg.inv(GMAT)
    s_chol = np.linalg.cholesky(GMAT)
    theta_eq = collide.mj_theta_from_w(0.5*(collide.mj_mean_w(TH1) + collide.mj_mean_w(TH2)))
    gdt = 0.05                                  # collisions per particle and step
    sig_flat = gdt/dt/float(collide.mj_vmol(theta_eq))
    sig_curv = sig_flat/ALPHA0
    ic_c = os.path.join(out, "curved.nrp")
    ic_f = os.path.join(out, "flat.nrp")
    info_c = common.make_box(ic_c, "twotemp", n, seed=71, theta=TH1, theta2=TH2, gmat=GMAT)
    info_f = common.make_box(ic_f, "twotemp", n, seed=71, theta=TH1, theta2=TH2)
    mesh = [f"mesh/nx{d}={nx}" for d in (1, 2, 3)] + [f"meshblock/nx{d}={nx}"
                                                      for d in (1, 2, 3)]
    base = mesh + [f"particles/dt={dt}", f"particles/snap_dt={(steps//4)*dt!r}",
                   f"time/nlim={steps}", "time/tlim=1.0e9", "job/rng_seed=88",
                   "particles/coll_budget=true"]
    runs = {
        "curved_symmetric_midpoint": (DECK_CURVED, [f"particles/particle_file={ic_c}",
                                                    f"particles/coll_sigma={sig_curv!r}",
                                                    "particles/triad=symmetric",
                                                    "particles/pusher=midpoint"]),
        "curved_cholesky_boris": (DECK_CURVED, [f"particles/particle_file={ic_c}",
                                                f"particles/coll_sigma={sig_curv!r}",
                                                "particles/triad=cholesky",
                                                "particles/pusher=boris"]),
        "flat": (common.DECK_BOX, [f"particles/particle_file={ic_f}",
                                   f"particles/coll_sigma={sig_flat!r}"]),
    }
    res = common.run_many([(args.exe, deck, os.path.join(out, k), base + ov)
                           for k, (deck, ov) in runs.items()], args.nproc)
    ok = all(r[0] == 0 for r in res)
    summary = {"n": n, "nx": nx, "steps": steps, "alpha0": ALPHA0, "sqrt_det_gamma": sg,
               "theta_eq": theta_eq, "exe": args.exe, "exe_sha256": common.sha256(args.exe),
               "exit": [r[0] for r in res], "wall_s": [round(r[1], 1) for r in res],
               "runs": {}}
    ncell = nx**3
    mu = n/ncell
    pop_sd = float(np.sqrt((4.0/mu + 2.0/mu**2)/ncell))
    hist, temps = {}, {}
    for name in runs:
        curved = name != "flat"
        rd = os.path.join(out, name)
        h = collide.read_history(os.path.join(rd, "box.coll.hst"))
        snaps = [collide.read_snapshot(p) for p in common.snapshots(rd)]
        s0, s1 = snaps[0], snaps[-1]
        sigma = sig_curv if curved else sig_flat
        lapse = ALPHA0 if curved else 1.0
        vfac = sg if curved else 1.0

        def triad_u(s):
            return np.linalg.solve(s_chol, s["u"].T).T if curved else s["u"]

        def lorentz(s):
            if curved:
                return np.sqrt(1.0 + np.einsum("pi,ij,pj->p", s["u"], ginv, s["u"]))
            return np.sqrt(1.0 + np.sum(s["u"]**2, axis=1))

        mass = s0["m"][0]
        # pair counting at the last snapshot
        xw = (s1["x"] - common.BOX_MIN) % common.BOX_LEN
        idx = np.minimum((xw*nx).astype(np.int64), nx - 1)
        cnt = np.bincount((idx[:, 2]*nx + idx[:, 1])*nx + idx[:, 0], minlength=ncell)
        vcell = (common.BOX_LEN/nx)**3
        pred = sigma*mass*lapse*dt/(2.0*vfac*vcell)*float(np.sum(cnt*(cnt - 1.0)))
        irec = int(np.argmin(np.abs(h["time"] - s1["time"])))
        rho0 = common.exact_sum(s0["m"])/(vfac*common.BOX_LEN**3)
        nominal = 0.5*n*rho0*sigma*lapse*dt*len(h["time"])
        # kinematics in the equilibrium phase (last quarter of the run)
        late = h["ncycle"] > 0.75*steps
        vbar = float(h["sum_P"][late].sum()/h["sum_W"][late].sum())
        gen = np.random.default_rng(3)
        uh = triad_u(s1)
        i = gen.integers(0, n, 4000000)
        j = gen.integers(0, n - 1, 4000000)
        j = np.where(j >= i, j + 1, j)
        g1, wa, wb = collide.gamma_rel_m1(uh[i], uh[j])
        vm = collide.moller(g1, wa, wb)
        vmc, vmc_se = float(vm.mean()), float(vm.std()/np.sqrt(len(vm)))
        v_se = float(vm.std()/np.sqrt(h["n_tested"][late].sum()))
        # conservation from the snapshots (exact sums)
        e0 = common.exact_sum(s0["m"]*lorentz(s0))
        e1 = common.exact_sum(s1["m"]*lorentz(s1))
        pscale = common.exact_sum(s0["m"]*np.linalg.norm(triad_u(s0), axis=1))
        dp = [(common.exact_sum(s1["m"]*s1["u"][:, k]) - common.exact_sum(s0["m"]*s0["u"][:, k]))
              / pscale for k in range(3)]
        ncoll = np.maximum(h["n_coll"], 1.0)
        # relaxation
        um = np.linalg.norm(uh, axis=1)
        th_s = collide.mj_theta_from_w(e0/common.exact_sum(s0["m"]))
        ks = stats.kstest(um, collide.mj_cdf(th_s))
        tt, th_pop = [], [[], []]
        for s in snaps:
            w = lorentz(s)
            tt.append(s["time"])
            for k in (0, 1):
                th_pop[k].append(collide.mj_theta_from_w(np.mean(w[s["species"] == k])))
        wl = lorentz(s1)
        zpop = []
        for k in (0, 1):
            wk = wl[s1["species"] == k]
            dw = (collide.mj_mean_w(th_s*1.001) - collide.mj_mean_w(th_s*0.999))/(0.002*th_s)
            zpop.append(float((collide.mj_theta_from_w(wk.mean()) - th_s)
                              / (wk.std()/np.sqrt(len(wk))/dw)))
        r = dict(collisions=int(h["n_coll"].sum()), sum_P=float(h["sum_P"].sum()),
                 n_trunc=int(h["n_trunc"].sum()), n_bad_cells=int(h["n_bad_cells"].sum()),
                 pair_count_rel_diff=float(abs(h["sum_W"][irec]/pred - 1.0)),
                 pair_count_rounding_bound=float(h["n_tested"][irec]*EPS),
                 weight_rel=float(h["sum_W"].sum()/nominal - 1.0), weight_sd=pop_sd,
                 count_z=float((h["n_coll"].sum() - h["sum_P"].sum())/np.sqrt(h["sum_P"].sum())),
                 vbar_code_late=vbar, vbar_pairs_last_snapshot=vmc,
                 vbar_z=float((vbar - vmc)/np.hypot(v_se, vmc_se)),
                 energy_rel_change=float((e1 - e0)/e0),
                 momentum_change_over_scale=[float(x) for x in dp],
                 pair_dE_eps=float(np.max(h["abs_dE"]/ncoll)/(EPS*2.0*mass*e0/common.exact_sum(s0["m"]))),
                 dE_particles_sum_rel=float(h["dE_particles"].sum()/e0),
                 dE_particles_max_abs_rel=float(np.max(np.abs(h["dE_particles"]))/e0),
                 theta_sample=th_s, ks_p_end=float(ks.pvalue), theta_pop_end_z=zpop,
                 theta_pop=[[float(x) for x in th_pop[0]], [float(x) for x in th_pop[1]]])
        r["pass"] = bool(r["pair_count_rel_diff"] < r["pair_count_rounding_bound"]
                         and abs(r["weight_rel"]) < 4.0*pop_sd and abs(r["count_z"]) < 4.0
                         and abs(r["vbar_z"]) < 4.0 and abs(r["energy_rel_change"]) < 1e-12
                         and max(abs(x) for x in dp) < 1e-12 and r["pair_dE_eps"] < 8.0
                         and abs(r["dE_particles_sum_rel"]) < 1e-12 and r["ks_p_end"] > 1e-3
                         and all(abs(z) < 4.0 for z in zpop) and r["n_trunc"] == 0
                         and r["n_bad_cells"] == 0)
        ok = ok and r["pass"]
        summary["runs"][name] = r
        hist[name] = h
        temps[name] = (np.array(tt), th_pop)
    # curved against flat: the same collision rate per coordinate time
    cf = summary["runs"]["flat"]["collisions"]
    for name in ("curved_symmetric_midpoint", "curved_cholesky_boris"):
        cc = summary["runs"][name]["collisions"]
        summary["runs"][name]["collisions_vs_flat_z"] = float((cc - cf)/np.sqrt(cc + cf))
        ok = ok and abs(summary["runs"][name]["collisions_vs_flat_z"]) < 4.0
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(8.0, 2.8))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.18, top=0.93, wspace=0.42)
    cols = {"curved_symmetric_midpoint": fs.PAL["red"],
            "curved_cholesky_boris": fs.PAL["yellow"], "flat": fs.PAL["blue"]}
    for name, col in cols.items():
        h = hist[name]
        k = 20
        nb = len(h["time"])//k
        tb = h["time"][:nb*k].reshape(nb, k).mean(axis=1)
        cb = h["n_coll"][:nb*k].reshape(nb, k).sum(axis=1)
        axs[0].plot(tb, cb/(0.5*n*gdt*k), color=col, lw=1.0, label=name.replace("_", " "))
        tt, th_pop = temps[name]
        axs[1].plot(tt, np.array(th_pop[0])/theta_eq, color=col, marker="o", ms=3)
        axs[1].plot(tt, np.array(th_pop[1])/theta_eq, color=col, marker="o", ms=3, ls="--")
        axs[2].plot(h["time"], np.cumsum(h["dE_particles"])/h["sum_MW"][0]/EPS, color=col,
                    lw=1.0)
    axs[0].axhline(1.0, **fs.GUIDE)
    axs[1].axhline(1.0, **fs.GUIDE)
    axs[0].set_ylabel("collisions per step / nominal")
    axs[1].set_ylabel(r"$\theta$ of each population / $\theta_{\rm eq}$")
    axs[2].set_ylabel(r"cumulative $\Delta E_{\rm coll}$ / $\epsilon E$")
    for ax in axs:
        ax.set_xlabel("coordinate time")
    axs[0].legend(fontsize=6.5, loc="lower right")
    fig.savefig(os.path.join(out, "fig_curved_box.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
