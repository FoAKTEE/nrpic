#!/usr/bin/env python3
"""Collision cells on a statically refined mesh: the periodic Minkowski box with one
octant, [100, 100.5]^3, refined by one level (32^3 root cells; 64^3 cells per unit
volume in the octant).

  run_smr.py OUTDIR [--exe ATHENA] [--n 200000] [--nproc 3]

Runs: MeshBlocks of 16^3 and of 8^3 cells (the same leaf cells), and 16^3 with
coll_cell_factor = 2. Checked: level and collision cell of every particle against an
assignment from the geometry (dump of cycle 10); the summed probability weight against
sigma M dt/2 x sum over the cells of both levels of N (N - 1)/V_cell from the last
snapshot; collisions against their expectation; byte-identical snapshots for the two
MeshBlock divisions.
"""
import argparse
import filecmp
import json
import os
import sys

import numpy as np

import common
from nrpic import collide

SMR = """
<mesh_refinement>
refinement = static

<refined_region1>
level = 1
x1min = 100.0
x1max = 100.5
x2min = 100.0
x2max = 100.5
x3min = 100.0
x3max = 100.5
"""
EPS = 2.0**-52
DUMP = 10


def geometry_cells(x, f):
    """Level and collision-cell index of every position from the geometry."""
    xw = (x - common.BOX_MIN) % common.BOX_LEN
    fine = np.all(xw < 0.5, axis=1)
    lev = fine.astype(np.int64)
    ncell = np.where(fine, 64, 32)[:, None]
    idx = np.minimum((xw*ncell).astype(np.int64), ncell - 1)//f
    return lev, idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--nproc", type=int, default=3)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, dt, steps = args.n, 0.01, 40
    deck = os.path.join(out, "box_smr.athinput")
    with open(deck, "w") as fp:
        fp.write(open(common.DECK_BOX).read() + SMR)
    ic = os.path.join(out, "mj.nrp")
    info = common.make_box(ic, "mj", n, seed=91, theta=0.1)
    sigma = 0.05/dt/float(collide.mj_vmol(0.1))
    base = [f"particles/particle_file={ic}", f"particles/dt={dt}",
            f"particles/coll_sigma={sigma!r}", f"particles/snap_dt={steps*dt!r}",
            f"time/nlim={steps}", "time/tlim=1.0e9", "job/rng_seed=91",
            f"particles/coll_dump_cycle={DUMP}"]
    runs = {"mb16": (16, 1), "mb8": (8, 1), "mb16_f2": (16, 2)}
    res = common.run_many([(args.exe, deck, os.path.join(out, k),
                            base + [f"meshblock/nx{d}={nb}" for d in (1, 2, 3)]
                            + [f"particles/coll_cell_factor={f}"])
                           for k, (nb, f) in runs.items()], args.nproc)
    ok = all(r[0] == 0 for r in res)
    if not ok:
        print("a run failed:", [r[0] for r in res])
        sys.exit(1)
    summary = {"n": n, "sigma": sigma, "exe": args.exe, "exe_sha256": common.sha256(args.exe),
               "runs": {}}
    occ = {}
    hists = {}
    for name, (nb, f) in runs.items():
        rd = os.path.join(out, name)
        log = open(os.path.join(rd, "athena.log")).read()
        h = collide.read_history(os.path.join(rd, "box.coll.hst"))
        d = collide.read_dump(os.path.join(rd, f"box.coll_dump.{DUMP}.bin"))
        lev, idx = geometry_cells(d["x"], f)
        s1 = collide.read_snapshot(common.snapshots(rd)[-1])
        lev1, idx1 = geometry_cells(s1["x"], f)
        mass = s1["m"][0]
        pred = 0.0
        counts = {}
        for lv, ncd in ((0, 32//f), (1, 64//f)):
            sel = lev1 == lv
            key = (idx1[sel, 2]*ncd + idx1[sel, 1])*ncd + idx1[sel, 0]
            cnt = np.bincount(key, minlength=ncd**3).astype(np.float64)
            vcell = (common.BOX_LEN/ncd)**3
            pred += sigma*mass*dt/(2.0*vcell)*float(np.sum(cnt*(cnt - 1.0)))
            counts[lv] = cnt[cnt > 0]
        irec = int(np.argmin(np.abs(h["time"] - s1["time"])))
        nominal = 0.5*n*info["rho0"]*sigma*dt*len(h["time"])
        r = dict(meshblocks=int(log.count("")) and None, cell_factor=f,
                 levels_agree=bool(np.array_equal(lev, d["level"])),
                 cells_agree=bool(np.array_equal(idx, d["cell"])),
                 particles_fine=int(np.count_nonzero(lev1 == 1)),
                 pair_count_rel_diff=float(abs(h["sum_W"][irec]/pred - 1.0)),
                 pair_count_rounding_bound=float(h["n_tested"][irec]*EPS),
                 weight_rel=float(h["sum_W"].sum()/nominal - 1.0),
                 count_z=float((h["n_coll"].sum() - h["sum_P"].sum())/np.sqrt(h["sum_P"].sum())),
                 collisions=int(h["n_coll"].sum()), n_trunc=int(h["n_trunc"].sum()),
                 mean_N=float(np.mean(h["mean_N"])),
                 edge_warning="differ from the" in log)
        del r["meshblocks"]
        r["pass"] = bool(r["levels_agree"] and r["cells_agree"]
                         and r["pair_count_rel_diff"] < r["pair_count_rounding_bound"]
                         and abs(r["weight_rel"]) < 0.02 and abs(r["count_z"]) < 4.0
                         and r["n_trunc"] == 0 and not r["edge_warning"])
        ok = ok and r["pass"]
        summary["runs"][name] = r
        occ[name] = counts
        hists[name] = (h, nominal/len(h["time"]))
    sa = common.snapshots(os.path.join(out, "mb16"))
    sb = common.snapshots(os.path.join(out, "mb8"))
    summary["layouts_identical"] = bool(len(sa) == len(sb) and all(
        filecmp.cmp(a, b, shallow=False) for a, b in zip(sa, sb)))
    summary["ok"] = bool(ok and summary["layouts_identical"])
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 2.9))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.93, wspace=0.27)
    cols = {"mb16": fs.PAL["blue"], "mb8": fs.PAL["red"], "mb16_f2": fs.PAL["yellow"]}
    for name, col in cols.items():
        h, nom = hists[name]
        axs[0].plot(h["time"], h["sum_W"]/nom, color=col, lw=1.0,
                    ls="--" if name == "mb8" else "-", label=name.replace("_", " "))
    axs[0].axhline(1.0, **fs.GUIDE)
    axs[0].set_xlabel("time")
    axs[0].set_ylabel(r"$\Sigma W$ per step / nominal")
    axs[0].legend(fontsize=8)
    bins = np.arange(0.5, 90.5, 1.0)
    for (name, lv, col, lab) in (("mb16", 0, fs.PAL["blue"], "level 0, factor 1"),
                                 ("mb16", 1, fs.PAL["red"], "level 1, factor 1"),
                                 ("mb16_f2", 0, fs.PAL["yellow"], "level 0, factor 2"),
                                 ("mb16_f2", 1, fs.PAL["green"], "level 1, factor 2")):
        axs[1].hist(occ[name][lv], bins=bins, histtype="step", color=col, lw=1.0, label=lab)
    axs[1].set_yscale("log")
    axs[1].set_xlabel("particles in a collision cell")
    axs[1].set_ylabel("cells")
    axs[1].legend(fontsize=7)
    fig.savefig(os.path.join(out, "fig_smr.png"), dpi=200)
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
