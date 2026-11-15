#!/usr/bin/env python3
"""P8b: the collision operator against the size of the collision cell in a homogeneous
gas (two Maxwellian populations, theta_1 = 3 theta_2 = 3e-3, the box of run_conv_dt.py at
nu_0 dt = 0.025).

  run_cells.py OUTDIR [--exe ATHENA] [--n 400000] [--nproc 8] [--seeds 2]

Mesh cells per direction and coll_cell_factor: (8,4) (8,1) (16,1) (32,1) (64,2) (64,1)
(64,4), i.e. 2^3 to 64^3 collision cells and 50000 to 1.5 particles per cell. (32,1) and
(64,2), and (16,1) and (64,4), have the same collision cells and must give byte-identical
particle states. For every configuration: pair counting against the cell populations of
the last snapshot, collisions against their expectation, the summed probability weight
against the nominal rate, and the fitted decay rate of theta_1 - theta_2.
"""
import argparse
import filecmp
import json
import os
import sys

import numpy as np

import common
from nrpic import collide
from run_conv_dt import NU0, TH1, TH2, TWIN, temperatures

CONFIGS = [(8, 4), (8, 1), (16, 1), (32, 1), (64, 2), (64, 1), (64, 4)]
EPS = 2.0**-52


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--nproc", type=int, default=8)
    ap.add_argument("--seeds", type=int, default=2)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, dt = args.n, 0.02
    steps = int(round(TWIN/dt))
    ic = os.path.join(out, "twotemp.nrp")
    info = common.make_box(ic, "twotemp", n, seed=61, theta=TH1, theta2=TH2)
    sigma = NU0/float(collide.relax_rate_nr(TH1, TH2, 1.0))
    jobs, meta = [], []
    for seed in range(1, args.seeds + 1):
        for nx, f in CONFIGS:
            rd = os.path.join(out, f"nx{nx}_f{f}_seed{seed}")
            ov = [f"mesh/nx{d}={nx}" for d in (1, 2, 3)] \
                + [f"meshblock/nx{d}={nx}" for d in (1, 2, 3)] \
                + [f"particles/particle_file={ic}", f"particles/dt={dt}",
                   f"particles/coll_sigma={sigma!r}", "particles/coll_pmax=0.1",
                   f"particles/coll_cell_factor={f}", f"particles/snap_dt={steps*dt!r}",
                   f"time/nlim={steps}", "time/tlim=1.0e9", f"job/rng_seed={600 + seed}"]
            jobs.append((args.exe, common.DECK_BOX, rd, ov))
            meta.append(dict(nx=nx, f=f, seed=seed, rundir=rd))
    res = common.run_many(jobs, args.nproc)
    ok = all(r[0] == 0 for r in res)
    summary = {"n": n, "dt": dt, "steps": steps, "sigma": sigma, "exe": args.exe,
               "exe_sha256": common.sha256(args.exe), "exit": [r[0] for r in res],
               "wall_s": [round(r[1], 1) for r in res]}

    from nrpic.io import read_nrp
    x, u, m, sp = read_nrp(ic)[:4]
    w = np.sqrt(1.0 + np.sum(u*u, axis=1))
    d0 = collide.mj_theta_from_w(np.mean(w[sp == 0])) \
        - collide.mj_theta_from_w(np.mean(w[sp == 1]))
    rows = {}
    for mm in meta:
        nc = mm["nx"]//mm["f"]
        ncell = nc**3
        mu = n/ncell
        h = collide.read_history(os.path.join(mm["rundir"], "box.coll.hst"))
        h["sum_M"] = np.full(len(h["time"]), float(np.sum(m)))
        s1 = collide.read_snapshot(common.snapshots(mm["rundir"])[-1])
        xw = (s1["x"] - common.BOX_MIN) % common.BOX_LEN
        idx = np.minimum((xw*nc).astype(np.int64), nc - 1)
        cnt = np.bincount((idx[:, 2]*nc + idx[:, 1])*nc + idx[:, 0], minlength=ncell)
        vcell = (common.BOX_LEN/nc)**3
        pred = sigma*m[0]*dt/(2.0*vcell)*float(np.sum(cnt*(cnt - 1.0)))
        irec = int(np.argmin(np.abs(h["time"] - s1["time"])))
        nominal = 0.5*n*info["rho0"]*sigma*dt*len(h["time"])
        t0, t1 = temperatures(h)
        t = np.concatenate(([0.0], h["time"]))
        dd = np.concatenate(([d0], t0 - t1))
        nu = -np.polyfit(t, np.log(dd), 1)[0]
        r = dict(seed=mm["seed"], pair_count_rel_diff=float(abs(h["sum_W"][irec]/pred - 1.0)),
                 pair_count_rounding_bound=float(max(h["n_tested"][irec], 1.0)*EPS),
                 cells_with_pairs_last=int(h["n_cells"][irec]),
                 count_z=float((h["n_coll"].sum() - h["sum_P"].sum())/np.sqrt(h["sum_P"].sum())),
                 weight_rel=float(h["sum_W"].sum()/nominal - 1.0),
                 weight_sd_frozen=float(np.sqrt((4.0/mu + 2.0/mu**2)/ncell)),
                 nu_fit=float(nu), mean_nsub=float(np.mean(h["mean_nsub"])),
                 max_nsub=int(h["max_nsub"].max()), max_P=float(h["max_P"].max()),
                 n_trunc=int(h["n_trunc"].sum()), collisions=int(h["n_coll"].sum()),
                 min_N=int(h["min_N"].min()), mean_N=float(np.mean(h["mean_N"])),
                 max_dx_mfp=float(h["max_dx_mfp"].max()))
        rows.setdefault(f"nx{mm['nx']}_f{mm['f']}", dict(nx=mm["nx"], f=mm["f"],
                        cells=ncell, particles_per_cell=mu, runs=[]))["runs"].append(r)
    table = []
    for key, row in rows.items():
        v = np.array([r["nu_fit"] for r in row["runs"]])
        row["nu_fit_mean"] = float(v.mean())
        row["nu_fit_se"] = float(v.std(ddof=1)/np.sqrt(len(v))) if len(v) > 1 else None
        row["pass_counting"] = bool(all(
            r["pair_count_rel_diff"] < r["pair_count_rounding_bound"]
            and abs(r["count_z"]) < 4.0 and abs(r["weight_rel"]) < 4.0*r["weight_sd_frozen"]
            and r["n_trunc"] == 0 for r in row["runs"]))
        table.append(row)
    summary["configurations"] = table
    # identical collision cells: byte-identical final snapshots
    same = {}
    for a, b in ((("nx32_f1"), ("nx64_f2")), (("nx16_f1"), ("nx64_f4"))):
        fa = common.snapshots(os.path.join(out, a + "_seed1"))[-1]
        fb = common.snapshots(os.path.join(out, b + "_seed1"))[-1]
        same[a + "=" + b] = bool(filecmp.cmp(fa, fb, shallow=False))
    summary["identical_collision_cells_give_identical_states"] = same
    # decay rate against the configurations with at least 40 particles per cell
    ref = [r for r in table if r["particles_per_cell"] >= 40.0]
    ref_nu = float(np.mean([r["nu_fit_mean"] for r in ref]))
    ref_se = float(np.sqrt(np.sum([(r["nu_fit_se"] or 0.0)**2 for r in ref]))/len(ref))
    for r in table:
        r["nu_rel_to_large_cells"] = r["nu_fit_mean"]/ref_nu - 1.0
        r["nu_z"] = float((r["nu_fit_mean"] - ref_nu)/np.hypot(r["nu_fit_se"] or 1e-12, ref_se))
    summary["nu_reference_large_cells"] = ref_nu
    summary["ok"] = bool(ok and all(r["pass_counting"] for r in table) and all(same.values()))
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(8.0, 2.8))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.18, top=0.93, wspace=0.5)
    mu = np.array([r["particles_per_cell"] for r in table])
    for r in table:
        col = fs.PAL["blue"] if r["f"] == 1 else fs.PAL["red"]
        mk = "o" if r["f"] == 1 else "s"
        axs[0].errorbar([r["particles_per_cell"]]*len(r["runs"]),
                        [x["weight_rel"] for x in r["runs"]],
                        yerr=[x["weight_sd_frozen"] for x in r["runs"]], color=col,
                        marker=mk, ls="none", ms=4, capsize=2)
        axs[1].plot([r["particles_per_cell"]]*len(r["runs"]),
                    [x["count_z"] for x in r["runs"]], color=col, marker=mk, ls="none", ms=4)
        axs[2].errorbar([r["particles_per_cell"]], [r["nu_fit_mean"]/NU0],
                        yerr=[(r["nu_fit_se"] or 0.0)/NU0], color=col, marker=mk, ls="none",
                        ms=4, capsize=2)
    axs[0].axhline(0.0, **fs.GUIDE)
    axs[1].axhline(0.0, **fs.GUIDE)
    axs[2].axhline(ref_nu/NU0, **fs.GUIDE)
    axs[0].set_ylabel(r"$\Sigma W$ / nominal $- 1$")
    axs[1].set_ylabel(r"(collisions $- \Sigma P)/\sqrt{\Sigma P}$")
    axs[2].set_ylabel(r"fitted decay rate / $\nu_0$")
    for ax in axs:
        ax.set_xscale("log")
        ax.set_xlabel("particles per collision cell")
    axs[1].plot([], [], color=fs.PAL["blue"], marker="o", ls="none", ms=4, label="factor 1")
    axs[1].plot([], [], color=fs.PAL["red"], marker="s", ls="none", ms=4,
                label="factor 2, 4")
    axs[1].legend(fontsize=8)
    fig.savefig(os.path.join(out, "fig_cells.png"), dpi=200)
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
