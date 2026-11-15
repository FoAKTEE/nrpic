#!/usr/bin/env python3
"""P7: reproducibility of collisional runs.

  run_repro.py OUTDIR [--exe ATHENA] [--n 100000] [--nproc 6]

Analytic path (flat Kerr-Schild functor, the particles do not read the mesh): the same
two-temperature box for 1, 8 and 64 MeshBlocks, a run restarted from the dump of cycle
37, and another seed. Mesh path (the flat metric carried by the mesh, <adm> block): 1
and 64 MeshBlocks and a restart. Every snapshot and the integer columns of the collision
history are compared; the momenta of the two layouts are compared particle by particle.
"""
import argparse
import filecmp
import json
import os
import sys

import numpy as np

import common
from nrpic import collide

INT_COLS = ["ncycle", "n_part", "n_cells", "n_tested", "n_coll", "n_updated", "n_trunc",
            "max_nsub", "min_N", "n_bad_cells"]


def make_deck(path, mesh_metric):
    """The box deck with a restart output every 37 cycles; optionally the mesh metric."""
    text = open(common.DECK_BOX).read()
    if mesh_metric:
        text = text.replace("metric         = kerr_schild", "metric         = mesh")
        text = text.replace("<particles>", "<adm>\ndynamic = false\n\n<particles>")
        assert "metric         = mesh" in text and "<adm>" in text
    text += "\n<output1>\nfile_type = rst\ndcycle    = 37\n"
    with open(path, "w") as fp:
        fp.write(text)


def compare(a, b):
    """Snapshots of two runs: byte-identical files, and the largest difference of the
    momenta at the last snapshot (particles matched by tag)."""
    sa, sb = common.snapshots(a), common.snapshots(b)
    same = len(sa) == len(sb) and all(filecmp.cmp(x, y, shallow=False)
                                      for x, y in zip(sa, sb))
    first_diff = None
    for i, (x, y) in enumerate(zip(sa, sb)):
        if not filecmp.cmp(x, y, shallow=False):
            first_diff = i
            break
    da, db = collide.read_snapshot(sa[-1]), collide.read_snapshot(sb[-1])
    ia, ib = np.argsort(da["tag"]), np.argsort(db["tag"])
    du = np.abs(da["u"][ia] - db["u"][ib])
    ha = collide.read_history(os.path.join(a, "box.coll.hst"))
    hb = collide.read_history(os.path.join(b, "box.coll.hst"))
    ints = all(np.array_equal(ha[c], hb[c]) for c in INT_COLS)
    first_cycle = None
    if not ints:
        nmin = min(len(ha["n_coll"]), len(hb["n_coll"]))
        bad = np.nonzero(ha["n_coll"][:nmin] != hb["n_coll"][:nmin])[0]
        first_cycle = int(ha["ncycle"][bad[0]]) if len(bad) else None
    return dict(snapshots=len(sa), identical_files=bool(same),
                first_differing_snapshot=first_diff,
                particles_differing=int(np.count_nonzero(np.any(du > 0.0, axis=1))),
                max_abs_du=float(du.max()), history_integers_identical=bool(ints),
                first_cycle_with_different_collisions=first_cycle,
                collisions=[float(ha["n_coll"].sum()), float(hb["n_coll"].sum())])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--exe", default=common.EXE_CPU)
    ap.add_argument("--n", type=int, default=100000)
    ap.add_argument("--nproc", type=int, default=6)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    n, dt, steps = args.n, 0.01, 100
    ic = os.path.join(out, "twotemp.nrp")
    common.make_box(ic, "twotemp", n, seed=31, theta=0.3, theta2=0.1)
    theta_eq = collide.mj_theta_from_w(0.5*(collide.mj_mean_w(0.3) + collide.mj_mean_w(0.1)))
    sigma = 0.1/dt/float(collide.mj_vmol(theta_eq))       # Gamma dt = 0.1: sub-cycling
    deck_a = os.path.join(out, "box_analytic.athinput")
    deck_m = os.path.join(out, "box_mesh.athinput")
    make_deck(deck_a, False)
    make_deck(deck_m, True)
    common_ov = [f"particles/particle_file={ic}", f"particles/dt={dt}",
                 f"particles/coll_sigma={sigma!r}", f"particles/snap_dt={25*dt!r}",
                 f"time/nlim={steps}", "time/tlim=1.0e9"]

    def ov(nb, seed=7):
        return common_ov + [f"meshblock/nx{d}={32//nb}" for d in (1, 2, 3)] \
            + [f"job/rng_seed={seed}"]

    runs = {"a1": (deck_a, ov(1)), "a8": (deck_a, ov(2)), "a64": (deck_a, ov(4)),
            "a1_seed8": (deck_a, ov(1, seed=8)), "m1": (deck_m, ov(1)),
            "m64": (deck_m, ov(4))}
    res = common.run_many([(args.exe, d, os.path.join(out, k), o) for k, (d, o) in
                           runs.items()], args.nproc)
    ok = all(r[0] == 0 for r in res)
    # restarts from the dump of cycle 37 (second restart file), the parameters are read
    # from the restart file
    rst = os.path.join("rst", "box.00001.rst")
    r2 = common.run_many([(args.exe, None, os.path.join(out, "a1_restart"), [],
                           "athena.log", os.path.join(out, "a1", rst)),
                          (args.exe, None, os.path.join(out, "a64_restart"), [],
                           "athena.log", os.path.join(out, "a64", rst)),
                          (args.exe, None, os.path.join(out, "m1_restart"), [],
                           "athena.log", os.path.join(out, "m1", rst))], args.nproc)
    ok = ok and all(r[0] == 0 for r in r2)

    def restart_compare(full, part):
        """A restarted run holds the snapshots after the restart; compare the last one
        and the history records after cycle 37."""
        sa, sb = common.snapshots(full), common.snapshots(part)
        same = filecmp.cmp(sa[-1], sb[-1], shallow=False)
        ha = collide.read_history(os.path.join(full, "box.coll.hst"))
        hb = collide.read_history(os.path.join(part, "box.coll.hst"))
        sel = ha["ncycle"] > 37
        ints = all(np.array_equal(ha[c][sel], hb[c][hb["ncycle"] > 37]) for c in INT_COLS)
        flt = all(np.array_equal(ha[c][sel], hb[c][hb["ncycle"] > 37])
                  for c in ("sum_P", "max_P", "sum_MW", "sum_W"))
        return dict(last_snapshot_identical=bool(same), restart_snapshots=len(sb),
                    history_integers_identical=bool(ints),
                    history_sums_identical=bool(flt))

    d = lambda k: os.path.join(out, k)   # noqa: E731
    summary = {"n": n, "steps": steps, "sigma": sigma, "exe": args.exe,
               "exe_sha256": common.sha256(args.exe),
               "analytic_1_vs_8": compare(d("a1"), d("a8")),
               "analytic_1_vs_64": compare(d("a1"), d("a64")),
               "analytic_restart_1": restart_compare(d("a1"), d("a1_restart")),
               "analytic_restart_64": restart_compare(d("a64"), d("a64_restart")),
               "analytic_other_seed": compare(d("a1"), d("a1_seed8")),
               "mesh_1_vs_64": compare(d("m1"), d("m64")),
               "mesh_restart_1": restart_compare(d("m1"), d("m1_restart")),
               "analytic_vs_mesh_1": compare(d("a1"), d("m1"))}
    s = summary
    expect = {
        "analytic path: snapshots byte-identical for 1, 8, 64 MeshBlocks":
            s["analytic_1_vs_8"]["identical_files"] and s["analytic_1_vs_64"]["identical_files"],
        "analytic path: integer history columns identical for the layouts":
            s["analytic_1_vs_8"]["history_integers_identical"]
            and s["analytic_1_vs_64"]["history_integers_identical"],
        "analytic path: restart at cycle 37 byte-identical (1 and 64 MeshBlocks)":
            s["analytic_restart_1"]["last_snapshot_identical"]
            and s["analytic_restart_64"]["last_snapshot_identical"]
            and s["analytic_restart_1"]["history_integers_identical"],
        "another seed gives another state":
            not s["analytic_other_seed"]["identical_files"]
            and s["analytic_other_seed"]["particles_differing"] > n//2,
        "mesh path: restart byte-identical":
            s["mesh_restart_1"]["last_snapshot_identical"],
    }
    summary["expectations"] = {k: bool(v) for k, v in expect.items()}
    # the mesh path is predicted NOT to be identical between layouts (metric gather)
    summary["mesh_layouts_identical"] = s["mesh_1_vs_64"]["identical_files"]
    ca, cb = s["mesh_1_vs_64"]["collisions"]
    summary["mesh_layouts_collision_count_z"] = float((ca - cb)/np.sqrt(ca + cb))
    summary["ok"] = bool(ok and all(expect.values()))
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    print(json.dumps(summary, indent=1))

    # figure: difference of the momenta between two runs, particle by particle
    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 2.9))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.9, wspace=0.28)
    pairs = [("a1", "a8", "analytic, 1 vs 8 blocks", fs.PAL["blue"]),
             ("a1", "a64", "analytic, 1 vs 64 blocks", fs.PAL["red"]),
             ("a1", "a1_seed8", "analytic, other seed", fs.PAL["yellow"]),
             ("m1", "m64", "mesh metric, 1 vs 64 blocks", fs.PAL["green"])]
    for a, b, lab, col in pairs:
        frac, mx = [], []
        sa, sb = common.snapshots(d(a)), common.snapshots(d(b))
        tt = []
        for x, y in zip(sa, sb):
            da, db = collide.read_snapshot(x), collide.read_snapshot(y)
            du = np.abs(da["u"][np.argsort(da["tag"])] - db["u"][np.argsort(db["tag"])])
            frac.append(np.count_nonzero(np.any(du > 0.0, axis=1))/len(du))
            mx.append(du.max())
            tt.append(da["time"]/dt)
        axs[0].plot(tt, np.maximum(frac, 1e-7), marker="o", ms=3, color=col, label=lab)
        axs[1].plot(tt, np.maximum(mx, 1e-18), marker="o", ms=3, color=col)
    axs[0].set_yscale("log")
    axs[1].set_yscale("log")
    axs[0].set_ylim(5e-8, 3.0)
    axs[0].set_ylabel("fraction of particles that differ")
    axs[1].set_ylabel(r"largest $|\Delta u_i|$")
    for ax in axs:
        ax.set_xlabel("cycle")
    axs[0].legend(fontsize=7, loc="center right")
    fig.savefig(os.path.join(out, "fig_repro.png"), dpi=200)
    sys.exit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
