#!/usr/bin/env python3
"""G4: a gas in equilibrium in a static potential well, with streaming and collisions,
for the collision operator of core-v0.3 (coll_energy = cell) and for the kinematics
with the metric at each particle (coll_energy = particle).

  run_tolman.py OUT [--exe ATHENA] [--n 1000000] [--steps 600] [--nproc 3]
                [--lam-cells 1.0] [--theta 0.05] [--seeds 2]

Metric: problems/tests/coll_box_static.athinput with alpha = 1 - 0.2 cos phi,
psi = 1 + 0.1 cos phi (16 x 4 x 4 cells). Particles: f ~ exp(-alpha W/theta_inf), the
exact equilibrium of the collisionless and of the collisional equation in this metric
(local temperature theta_inf/alpha, Tolman's law; coordinate density ~ psi^6 K2(z)/z
exp(-z), z = alpha/theta_inf). Mean free path = lam-cells mesh cells.
Measured: the sum of M H, H = alpha W, of all particles against time and the part of
its change that happens in the collision steps (history columns 32, 33); the amplitude
of the cos(phi) mode of ln(theta_local alpha) and of the density, from snapshots.
Writes summary.json and fig_tolman.png.
"""
import argparse
import json
import os
import sys

import numpy as np

import common
import scbox
from nrpic import collide

DECK = os.path.join(common.REPO, "problems", "tests", "coll_box_static.athinput")
LENGTHS = [1.0, 0.25, 0.25]
NBIN = 32


def mode_amplitudes(met, snap, theta_inf):
    """cos(phi) amplitudes of ln(theta_local alpha/theta_inf) and of ln(density/psi^6)
    over NBIN bins in x, with the temperature of a bin from its mean W (metric at each
    particle); also the profiles."""
    x = snap["x"][:, 0]
    w, _ = scbox.energies(met, snap["x"][:, 0], snap["u"])
    ib = np.minimum(((x - met.xmin)/met.length*NBIN).astype(np.int64) % NBIN, NBIN - 1)
    cnt = np.bincount(ib, minlength=NBIN)
    wm = np.bincount(ib, weights=w, minlength=NBIN)/cnt
    w2 = np.bincount(ib, weights=w*w, minlength=NBIN)/cnt
    xc = met.xmin + (np.arange(NBIN) + 0.5)*met.length/NBIN
    alp, _, psi4 = met.at(xc)
    th = np.array([collide.mj_theta_from_w(v) for v in wm])
    # standard error of theta of a bin: dtheta = dW/(dW/dtheta)
    dwdt = np.array([(collide.mj_mean_w(t*1.001) - collide.mj_mean_w(t*0.999))/(0.002*t)
                     for t in th])
    th_se = np.sqrt((w2 - wm*wm)/cnt)/dwdt
    lt = np.log(th*alp/theta_inf)
    ph = 2.0*np.pi*(xc - met.xmin)/met.length
    a_t = 2.0*np.mean(lt*np.cos(ph))
    a_t_se = 2.0*np.sqrt(np.sum((th_se/th*np.cos(ph))**2))/NBIN
    ln_n = np.log(cnt/cnt.mean()/psi4**1.5)
    a_n = 2.0*np.mean(ln_n*np.cos(ph))
    return dict(a_T=float(a_t), a_T_se=float(a_t_se), a_n=float(a_n),
                mean_lnT=float(np.mean(lt)), profile_T=(th*alp/theta_inf).tolist(),
                profile_T_se=(th_se*alp/theta_inf).tolist(), xc=xc.tolist())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=1000000)
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--nproc", type=int, default=4)
    ap.add_argument("--lam-cells", type=float, default=1.0)
    ap.add_argument("--theta", type=float, default=0.05)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--dt", type=float, default=0.01)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    met = scbox.Metric(nx=16, a_alpha=-0.2, a_psi=0.1)
    th = args.theta
    sigma = 1.0/(args.lam_cells*met.dx)            # rho_0 = 1 (coordinate density)
    tcoll = 1.0/(sigma*float(collide.mj_vmol(th)))
    snap_dt = args.steps*args.dt/12.0
    jobs, names = [], []
    for seed in range(args.seeds):
        ic = os.path.join(out, f"tolman_s{seed}.nrp")
        scbox.make_particles(ic, met, args.n, 700 + seed, th, 1.0, 0.0, LENGTHS,
                             weight="tolman")
        for mode in ("cell", "particle"):
            name = f"{mode}_s{seed}"
            ov = met.problem_block() + [
                f"particles/particle_file={ic}", f"particles/dt={args.dt!r}",
                f"time/nlim={args.steps}", "time/tlim=1.0e9",
                f"particles/coll_sigma={sigma!r}", f"particles/coll_energy={mode}",
                f"particles/snap_dt={snap_dt!r}", f"job/rng_seed={40 + seed}"]
            jobs.append((args.exe, DECK, os.path.join(out, name), ov))
            names.append(name)
    res = common.run_many(jobs, args.nproc)
    if any(r[0] != 0 for r in res):
        print("a run failed:", [r[0] for r in res])
        sys.exit(1)
    summary = dict(n=args.n, steps=args.steps, dt=args.dt, theta_inf=th, sigma=sigma,
                   t_coll=tcoll, lam_cells=args.lam_cells, exe=args.exe,
                   exe_sha256=common.sha256(args.exe), wall_s=[round(r[1], 1) for r in res],
                   runs={})
    series = {}
    for name in names:
        rd = os.path.join(out, name)
        h = collide.read_history(os.path.join(rd, "box.coll.hst"))
        snaps = [collide.read_snapshot(p) for p in common.snapshots(rd)]
        amps = [mode_amplitudes(met, s, th) for s in snaps]
        tt = np.array([s["time"] for s in snaps])
        e0 = h["sum_MH_particles"][0] - h["dH_particles"][0]
        cum_h = np.cumsum(h["dH_particles"])
        cum_w = np.cumsum(h["dE_particles"])
        ncoll = float(h["n_coll"].sum())
        mass = float(snaps[0]["m"][0])
        # momentum from the snapshots (exact sums); not conserved by the motion in the
        # well along x, conserved along y and z
        ps = common.exact_sum(snaps[0]["m"]*np.linalg.norm(snaps[0]["u"], axis=1))
        dpy = (common.exact_sum(snaps[-1]["m"]*snaps[-1]["u"][:, 1])
               - common.exact_sum(snaps[0]["m"]*snaps[0]["u"][:, 1]))/ps
        dpz = (common.exact_sum(snaps[-1]["m"]*snaps[-1]["u"][:, 2])
               - common.exact_sum(snaps[0]["m"]*snaps[0]["u"][:, 2]))/ps
        late = [a for a, t in zip(amps, tt) if t > 0.5*tt[-1]]
        r = dict(collisions=int(ncoll), collisions_per_particle=2.0*ncoll/args.n,
                 n_trunc=int(h["n_trunc"].sum()), n_noroot=int(h["n_noroot"].sum()),
                 n_balance=int(h["n_balance"].sum()),
                 max_dlam=float(h["max_dlam"].max()), max_nsub=int(h["max_nsub"].max()),
                 dH_total_rel=float((h["sum_MH_particles"][-1] - e0)/e0),
                 dH_collisions_rel=float(cum_h[-1]/e0),
                 dH_per_collision=float(cum_h[-1]/(mass*ncoll)),
                 dW_collisions_rel=float(cum_w[-1]/e0),
                 dPy_over_scale=float(dpy), dPz_over_scale=float(dpz),
                 a_T=[a["a_T"] for a in amps], a_T_se=[a["a_T_se"] for a in amps],
                 a_n=[a["a_n"] for a in amps], time=tt.tolist(),
                 a_T_late=float(np.mean([a["a_T"] for a in late])),
                 a_T_late_se=float(np.sqrt(np.mean([a["a_T_se"]**2 for a in late])
                                           / len(late))),
                 a_n_late=float(np.mean([a["a_n"] for a in late])), a_n0=amps[0]["a_n"],
                 profile_T_end=amps[-1]["profile_T"],
                 profile_T_end_se=amps[-1]["profile_T_se"], xc=amps[-1]["xc"])
        summary["runs"][name] = r
        series[name] = (h["time"], (h["sum_MH_particles"] - e0)/e0, cum_h/e0)
    ok = True
    checks = {}
    for name, r in summary["runs"].items():
        if name.startswith("particle"):
            c = dict(dH_total=bool(abs(r["dH_total_rel"]) < 1e-6),
                     dH_collisions=bool(abs(r["dH_collisions_rel"]) < 1e-12),
                     a_T=bool(abs(r["a_T_late"]) < 0.005), noroot=bool(r["n_noroot"] == 0))
        else:
            c = dict(dH_grows=bool(2e-3 < r["dH_collisions_rel"] < 6e-3),
                     a_T=bool(-0.10 < r["a_T_late"] < -0.02))
        checks[name] = c
        ok = ok and all(c.values())
    summary["checks"] = checks
    summary["ok"] = bool(ok)
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    for name, r in summary["runs"].items():
        print(f"{name:14s} coll/particle {r['collisions_per_particle']:.1f}  dH total "
              f"{r['dH_total_rel']:+.3e}  in collisions {r['dH_collisions_rel']:+.3e}  "
              f"dW in collisions {r['dW_collisions_rel']:+.3e}  a_T late "
              f"{r['a_T_late']:+.4f} ({r['a_T_late_se']:.4f})  a_n {r['a_n0']:+.4f} -> "
              f"{r['a_n_late']:+.4f}  noroot {r['n_noroot']} rejected {r['n_balance']}  "
              f"{checks[name]}")
    print("ok:", ok)

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(9.0, 2.9))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.17, top=0.93, wspace=0.34)
    cols = {"cell": fs.PAL["red"], "particle": fs.PAL["blue"]}
    for name, r in summary["runs"].items():
        mode, seed = name.split("_s")
        col, ls = cols[mode], ("-" if seed == "0" else "--")
        t, de, dc = series[name]
        lab = f"coll_energy = {mode}" if seed == "0" else None
        axs[0].plot(t/tcoll, 1e3*de, color=col, ls=ls, lw=1.0, label=lab)
        axs[1].errorbar(np.array(r["time"])/tcoll, 1e2*np.array(r["a_T"]),
                        yerr=1e2*np.array(r["a_T_se"]), color=col, ls=ls, lw=1.0,
                        marker="o", ms=2.5)
        if seed == "0":
            xc = (np.array(r["xc"]) - met.xmin)/met.length
            axs[2].errorbar(xc, r["profile_T_end"], yerr=r["profile_T_end_se"], color=col,
                            lw=0.9, marker="o", ms=2.5)
    for ax in axs:
        ax.axhline(1.0 if ax is axs[2] else 0.0, **fs.GUIDE)
    axs[0].set_xlabel(r"$t/t_{\rm coll}$")
    axs[0].set_ylabel(r"$\Delta\sum M H/\sum M H$ [$10^{-3}$]")
    axs[1].set_xlabel(r"$t/t_{\rm coll}$")
    axs[1].set_ylabel(r"$\cos\phi$ amplitude of $\ln(\theta\alpha)$ [percent]")
    axs[2].set_xlabel(r"$(x - x_{\min})/L$")
    axs[2].set_ylabel(r"$\theta_{\rm local}\,\alpha/\theta_\infty$ at the end")
    axs[0].legend(fontsize=7, loc="upper left")
    fig.savefig(os.path.join(out, "fig_tolman.png"), dpi=200)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
