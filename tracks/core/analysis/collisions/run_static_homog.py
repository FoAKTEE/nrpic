#!/usr/bin/env python3
"""T12 of track C and G3: the static conformal metric without modulation (constant
lapse alpha0 and conformal factor psi0; problems/tests/coll_box_static.athinput with all
amplitudes zero), a homogeneous curved metric in which everything is known.

  run_static_homog.py OUT [--exe ATHENA] [--n 50000] [--steps 200] [--nproc 4]

Runs (two-temperature start, same triad momenta in all):
  homog     <problem> metric_kind = homogeneous with gxx = gyy = gzz = psi0^4 (deck
            coll_box_curved.athinput, the test bed of wave 1), coll_energy absent
  cell      metric_kind = static_conformal, coll_energy = cell
  particle  metric_kind = static_conformal, coll_energy = particle
  flat      analytic flat metric with the cross-section of the same collision rate per
            coordinate time
Checks: (a) the snapshots of "cell" are byte-identical to those of "homog" (the two
generators fill the same metric; coll_energy = cell is the operator of core-v0.3);
(b) "particle" has the same number of collisions in every step as "cell" and momenta
within 1e-9 at the end (in a homogeneous metric the two kinematics coincide; no
collision is rejected, no pair lacks a root); (c) collisions per coordinate step: with
the same number of particles and the rest masses scaled by psi0^6 (same proper
density) the curved box has alpha0 times the collisions of the flat box at the same
cross-section, i.e. alpha0 psi0^6 times the flat value per coordinate volume at the
same proper density and macroparticle mass (track C, TESTS.md T12): here the
cross-section of the flat run is scaled by alpha0 and the counts must agree within
4 sigma; pair counting exact against the cell populations; (d) sum M u_i conserved
to rounding in all runs; (e) the collision steps change neither sum M W nor sum M H at
the particles beyond rounding.
"""
import argparse
import filecmp
import json
import os
import sys

import numpy as np

import common
from nrpic import collide

DECK_STATIC = os.path.join(common.REPO, "problems", "tests", "coll_box_static.athinput")
DECK_HOMOG = os.path.join(common.REPO, "problems", "tests", "coll_box_curved.athinput")
ALPHA0, PSI0 = 0.8, 1.1
TH1, TH2 = 0.6, 0.2
LENGTHS = [1.0, 0.25, 0.25]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=50000)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--nproc", type=int, default=4)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, dt, steps = args.n, 0.01, args.steps
    psi4 = (PSI0*PSI0)*(PSI0*PSI0)                 # as the problem generator forms it
    gmat = np.diag([psi4, psi4, psi4])
    theta_eq = collide.mj_theta_from_w(0.5*(collide.mj_mean_w(TH1) + collide.mj_mean_w(TH2)))
    gdt = 0.05
    sig_flat = gdt/dt/float(collide.mj_vmol(theta_eq))
    sig_curv = sig_flat/ALPHA0
    ic_c = os.path.join(out, "curved.nrp")
    ic_f = os.path.join(out, "flat.nrp")
    common.make_box(ic_c, "twotemp", n, seed=91, theta=TH1, theta2=TH2, gmat=gmat,
                    lengths=LENGTHS)
    common.make_box(ic_f, "twotemp", n, seed=91, theta=TH1, theta2=TH2, lengths=LENGTHS)
    mesh = ["mesh/nx1=16", "mesh/nx2=4", "mesh/nx3=4", "meshblock/nx1=16", "meshblock/nx2=4",
            "meshblock/nx3=4", "mesh/x2max=100.25", "mesh/x3max=100.25"]
    base = [f"particles/dt={dt}", f"particles/snap_dt={(steps//4)*dt!r}",
            f"time/nlim={steps}", "time/tlim=1.0e9", "job/rng_seed=88",
            "particles/coll_budget=true"]
    static = ["problem/metric_kind=static_conformal", f"problem/alpha0={ALPHA0!r}",
              f"problem/psi0={PSI0!r}", "problem/alpha_amp=0.0", "problem/psi_amp=0.0",
              "problem/shift_amp=0.0", f"particles/particle_file={ic_c}",
              f"particles/coll_sigma={sig_curv!r}"]
    runs = {
        "homog": (DECK_HOMOG, mesh + base + [
            f"problem/alpha0={ALPHA0!r}", f"problem/gxx={psi4!r}", f"problem/gyy={psi4!r}",
            f"problem/gzz={psi4!r}", "problem/gxy=0.0", "problem/gxz=0.0", "problem/gyz=0.0",
            f"particles/particle_file={ic_c}", f"particles/coll_sigma={sig_curv!r}"]),
        "cell": (DECK_STATIC, base + static + ["particles/coll_energy=cell"]),
        "particle": (DECK_STATIC, base + static + ["particles/coll_energy=particle"]),
        "flat": (common.DECK_BOX, mesh + base + [f"particles/particle_file={ic_f}",
                                                 f"particles/coll_sigma={sig_flat!r}"]),
    }
    res = common.run_many([(args.exe, deck, os.path.join(out, k), ov)
                           for k, (deck, ov) in runs.items()], args.nproc)
    if any(r[0] != 0 for r in res):
        print("a run failed:", [r[0] for r in res])
        sys.exit(1)
    hst = {k: collide.read_history(os.path.join(out, k, "box.coll.hst")) for k in runs}
    snaps = {k: common.snapshots(os.path.join(out, k)) for k in runs}
    last = {k: collide.read_snapshot(snaps[k][-1]) for k in runs}
    first = {k: collide.read_snapshot(snaps[k][0]) for k in runs}
    same_snap = bool(len(snaps["homog"]) == len(snaps["cell"])
                     and all(filecmp.cmp(a, b, shallow=False)
                             for a, b in zip(snaps["homog"], snaps["cell"])))
    same_counts = bool(np.array_equal(hst["cell"]["n_coll"], hst["particle"]["n_coll"])
                       and np.array_equal(hst["cell"]["n_tested"], hst["particle"]["n_tested"]))
    du = float(np.max(np.abs(last["cell"]["u"] - last["particle"]["u"])))
    dx = float(np.max(np.abs(last["cell"]["x"] - last["particle"]["x"])))
    cc, cf = float(hst["cell"]["n_coll"].sum()), float(hst["flat"]["n_coll"].sum())
    # pair counting at the last snapshot: sum_W = sigma M alpha dt/(2 psi^6 V_cell) sum N(N-1)
    s1 = last["cell"]
    idx = [np.minimum((((s1["x"][:, d] - 100.0) % LENGTHS[d])/LENGTHS[d]*nc).astype(np.int64),
                      nc - 1) for d, nc in enumerate((16, 4, 4))]
    cnt = np.bincount((idx[2]*4 + idx[1])*16 + idx[0], minlength=256)
    vcell = LENGTHS[0]*LENGTHS[1]*LENGTHS[2]/256
    mass = float(s1["m"][0])
    pred = sig_curv*mass*ALPHA0*dt/(2.0*PSI0**6*vcell)*float(np.sum(cnt*(cnt - 1.0)))
    irec = int(np.argmin(np.abs(hst["cell"]["time"] - s1["time"])))
    out_runs = {}
    for k in runs:
        s0, s1k, h = first[k], last[k], hst[k]
        ps = common.exact_sum(s0["m"]*np.linalg.norm(s0["u"], axis=1))
        dp = [(common.exact_sum(s1k["m"]*s1k["u"][:, i]) - common.exact_sum(s0["m"]*s0["u"][:, i]))
              / ps for i in range(3)]
        r = dict(collisions=int(h["n_coll"].sum()), sum_P=float(h["sum_P"].sum()),
                 dP_over_scale=[float(v) for v in dp],
                 dE_particles_rel=float(h["dE_particles"].sum()/h["sum_MW_particles"][0]),
                 n_trunc=int(h["n_trunc"].sum()))
        if "dH_particles" in h:
            r.update(dH_particles_rel=float(h["dH_particles"].sum()/h["sum_MH_particles"][0]),
                     n_noroot=int(h["n_noroot"].sum()), n_balance=int(h["n_balance"].sum()),
                     max_dlam=float(h["max_dlam"].max()))
        out_runs[k] = r
    checks = dict(
        a_cell_snapshots_identical_to_homogeneous=same_snap,
        b_same_collisions_every_step=same_counts, b_momenta_within_1e9=bool(du < 1e-9),
        b_no_rejection=bool(out_runs["particle"]["n_noroot"] == 0
                            and out_runs["particle"]["n_balance"] == 0),
        c_rate_vs_flat=bool(abs(cc - cf) < 4.0*np.sqrt(cc + cf)),
        c_pair_counting=bool(abs(hst["cell"]["sum_W"][irec]/pred - 1.0) < 1e-10),
        d_momentum=bool(all(max(abs(v) for v in r["dP_over_scale"]) < 1e-12
                            for r in out_runs.values())),
        e_energy=bool(all(abs(out_runs[k]["dE_particles_rel"]) < 1e-12
                          for k in ("cell", "particle"))
                      and all(abs(out_runs[k]["dH_particles_rel"]) < 1e-12
                              for k in ("cell", "particle"))))
    summary = dict(n=n, steps=steps, alpha0=ALPHA0, psi0=PSI0, theta_eq=theta_eq,
                   exe=args.exe, exe_sha256=common.sha256(args.exe),
                   wall_s={k: round(r[1], 1) for k, r in zip(runs, res)}, runs=out_runs,
                   max_du_cell_particle=du, max_dx_cell_particle=dx,
                   collisions_curved_over_flat=cc/cf,
                   collisions_z=float((cc - cf)/np.sqrt(cc + cf)),
                   pair_count_rel_diff=float(abs(hst["cell"]["sum_W"][irec]/pred - 1.0)),
                   checks=checks, ok=bool(all(checks.values())))
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.9))
    fig.subplots_adjust(left=0.1, right=0.985, bottom=0.17, top=0.95, wspace=0.3)
    cols = {"homog": "k", "cell": fs.PAL["red"], "particle": fs.PAL["blue"],
            "flat": fs.PAL["yellow"]}
    k = 10
    for name, h in hst.items():
        nb = len(h["time"])//k
        tb = h["time"][:nb*k].reshape(nb, k).mean(axis=1)
        cb = h["n_coll"][:nb*k].reshape(nb, k).sum(axis=1)
        axs[0].plot(tb, cb/(0.5*n*gdt*k), color=cols[name], lw=1.0,
                    ls="--" if name in ("homog", "particle") else "-", label=name)
    axs[0].axhline(1.0, **fs.GUIDE)
    axs[0].set_xlabel("coordinate time")
    axs[0].set_ylabel("collisions per step / nominal")
    axs[0].legend(fontsize=7)
    d = np.abs(last["cell"]["u"] - last["particle"]["u"]).max(axis=1)
    axs[1].hist(np.maximum(d, 1.2e-18), bins=np.logspace(-18, -8, 61), histtype="step",
                color=fs.PAL["blue"], lw=1.0)
    axs[1].axvline(1e-9, **fs.GUIDE)
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_xlabel(r"$|u_{\rm particle} - u_{\rm cell}|$ at the end")
    axs[1].set_ylabel("particles")
    fig.savefig(os.path.join(out, "fig_static_homog.png"), dpi=200)
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
