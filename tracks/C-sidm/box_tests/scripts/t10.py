#!/usr/bin/env python3
"""T10 of collide/TESTS.md: reproducibility of the collisional state.

    python3 t10.py [--exe PATH] [--tag cpu]

twotemp box (theta_1 = 0.3, theta_2 = 0.1), 1e5 particles, 16^3 cells, sigma = 5,
dt = 0.02 (sub-cycling active), 100 cycles, rng_seed 7:
  mb1, mb8, mb64   MeshBlocks of 16^3, 8^3, 4^3 cells (1, 8, 64 blocks),
  rst<k>           resumed from each restart file of mb8 (written every 37 cycles),
  seed8            the same box with rng_seed 8 (must differ).
MPI variants: not run (the release processor build has no MPI).
Pass (TESTS.md): final snapshots (x, u, M, tag) bit-identical in all variants; a
different seed gives a different state. Also compared: the integer columns of every
coll.hst record (n_tested, n_coll, n_updated, max_nsub) and sum_P.
"""
import argparse
import json
import os
import sys

import numpy as np

import boxlib as bl

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

NCYC, DT, SIG = 100, 0.02, 5.0


def last_snap(rd):
    return bl.snap.read_snapshot(bl.snapshots(rd)[-1])


def same(a, b):
    return bool(a["cycle"] == b["cycle"] and np.array_equal(a["tag"], b["tag"]) and
                np.array_equal(a["x"], b["x"]) and np.array_equal(a["u"], b["u"]) and
                np.array_equal(a["m"], b["m"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    out = bl.outdir()
    ic = os.path.join(out, "ic")
    meta = bl.make_box(ic, "twotemp", n=100000, theta=0.3, sigma=SIG, seed=7)
    deck = os.path.join(out, "box_rst.athinput")
    with open(bl.DECK) as fh:
        txt = fh.read()
    with open(deck, "w") as fh:
        fh.write(txt + "\n<output1>\nfile_type = rst\ndcycle    = 37\n")
    base = [f"particles/dt={DT!r}", f"time/nlim={NCYC}", f"particles/coll_sigma={SIG!r}",
            f"particles/snap_dt={NCYC * DT * (1 - 1e-9)!r}",
            f"particles/particle_file={os.path.join(ic, 'box.nrp')}"]
    jobs = []
    for name, mb, seed in (("mb1", 16, 7), ("mb8", 8, 7), ("mb64", 4, 7), ("seed8", 16, 8)):
        rd = os.path.join(out, name)
        jobs.append((rd, bl.mesh_overrides(16, mb) + base + [f"job/rng_seed={seed}"],
                     dict(exe=a.exe, deck=deck)))
    rr = bl.run_many(jobs, 4)
    res = dict(meta=meta, runs={os.path.basename(j[0]): dict(rc=r["rc"], wall=r["wall"])
                                for j, r in zip(jobs, rr)})
    rsts = sorted(os.listdir(os.path.join(out, "mb8", "rst")))
    jobs2 = []
    for k, fn in enumerate(rsts):
        rd = os.path.join(out, f"rst{k}")
        jobs2.append((rd, [], dict(exe=a.exe, restart=os.path.join(out, "mb8", "rst", fn))))
    rr2 = bl.run_many(jobs2, 4)
    for j, r in zip(jobs2, rr2):
        res["runs"][os.path.basename(j[0])] = dict(rc=r["rc"], wall=r["wall"],
                                                   restart=j[2]["restart"])
    ref = last_snap(os.path.join(out, "mb1"))
    href = bl.coll_history(os.path.join(out, "mb1"))
    cmp = {}
    for name in [n for n in res["runs"] if n != "mb1"]:
        rd = os.path.join(out, name)
        if res["runs"][name]["rc"] != 0:
            cmp[name] = dict(failed=True)
            continue
        try:
            s = last_snap(rd)
        except (IndexError, AssertionError) as e:
            cmp[name] = dict(failed=True, why=f"no readable snapshot: {e!r}")
            continue
        h = bl.coll_history(rd)
        c = dict(final_cycle=s["cycle"], final_file=os.path.basename(bl.snapshots(rd)[-1]),
                 identical=same(ref, s))
        # history records present in both (restart runs append after the restart cycle)
        cyc = np.intersect1d(href["ncycle"], h["ncycle"])
        ia = np.searchsorted(href["ncycle"], cyc)
        ib = np.searchsorted(h["ncycle"], cyc)
        c["hist_records_compared"] = int(cyc.size)
        c["hist_integers_identical"] = bool(all(
            np.array_equal(href[k][ia], h[k][ib])
            for k in ("n_tested", "n_coll", "n_updated", "max_nsub", "n_cells")))
        c["hist_sumP_max_rel"] = float(np.max(np.abs(href["sum_P"][ia] / h["sum_P"][ib] - 1)))
        if not c["identical"] and np.array_equal(ref["tag"], s["tag"]):
            du = np.max(np.abs(ref["u"] - s["u"]), 1)
            c["frac_particles_differ"] = float((du > 0).mean())
            c["max_du"] = float(du.max())
        cmp[name] = c
    res["compare_to_mb1"] = cmp
    res["mpi"] = "not run: release processor build has Athena_ENABLE_MPI=OFF"
    hb = href
    res["collisions_total_mb1"] = float(hb["n_coll"].sum())
    res["max_nsub_mb1"] = float(hb["max_nsub"].max())
    res["pass"] = bool(all(cmp[n].get("identical") for n in cmp if n != "seed8") and
                       len(rsts) >= 2 and
                       not cmp["seed8"].get("identical", True) and
                       cmp["seed8"].get("frac_particles_differ", 0) > 0.5)
    bl.save_json(os.path.join(out, f"t10_{a.tag}.json"), res)
    # figure: per-record differences of the collision counts against mb1
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax1 = fig.add_axes([0.08, 0.16, 0.40, 0.76])
    ax2 = fig.add_axes([0.58, 0.16, 0.40, 0.76])
    for k, name in enumerate(n for n in cmp if not cmp[n].get("failed")):
        h = bl.coll_history(os.path.join(out, name))
        cyc = np.intersect1d(href["ncycle"], h["ncycle"])
        ia = np.searchsorted(href["ncycle"], cyc)
        ib = np.searchsorted(h["ncycle"], cyc)
        c = fs.SERIES[k % len(fs.SERIES)]
        ax1.plot(cyc, h["n_coll"][ib] - href["n_coll"][ia], "o", ms=2.5, color=c, label=name)
    ax1.set_xlabel("cycle"); ax1.set_ylabel(r"$n_{\rm coll} - n_{\rm coll}$(mb1)")
    ax1.legend(loc="upper left", fontsize=7, ncol=2)
    s8 = last_snap(os.path.join(out, "seed8"))
    ax2.hist(np.max(np.abs(ref["u"] - s8["u"]), 1), bins=60, color=fs.PAL["red"],
             histtype="step", label="seed 8 vs seed 7")
    for name in cmp:
        if name != "seed8" and not cmp[name].get("failed"):
            s = last_snap(os.path.join(out, name))
            ax2.axvline(np.max(np.abs(ref["u"] - s["u"])) + 1e-30, **fs.MASK_LINE)
    ax2.set_yscale("log")
    ax2.set_xlabel(r"$\max_i |u_i - u_i^{\rm mb1}|$ at cycle 100")
    ax2.set_ylabel("particles")
    ax2.legend(loc="upper right", fontsize=7)
    fs.save(fig, os.path.join(out, f"t10_repro_{a.tag}"))
    plt.close(fig)
    print(json.dumps({k: v for k, v in res.items() if k != "meta"}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
