#!/usr/bin/env python3
"""Cost of coll_energy = particle against cell in the flat T2 box, under the same machine
load: the runs start together, one core each.

    python3 timing.py DESIGN_JSON [--theta 1.0] [--n 1000000] [--steps 200] [--repeat 2]

Runs (mj box of t1t2.py, plain variant, seed 1; executable of core/collisions-2, deck
inputs/box_c2.athinput): coll_energy = particle, coll_energy = cell, collisions = false
(the push alone), each `--repeat` times, all concurrently. Reported: wall times, the
collision part (wall - wall of the collisionless run) per tested pair, and the ratio
particle/cell. Writes timing.json into $NRPIC_RUN_DIR.
"""
import argparse
import json
import os
import sys

import numpy as np

import boxlib as bl

DECK = os.path.join(bl.PKG, "inputs", "box_c2.athinput")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--theta", default="1.0")
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--repeat", type=int, default=2)
    a = ap.parse_args()
    d = json.load(open(a.design))["T2"][a.theta]
    out = bl.outdir()
    ic = os.path.join(out, "ic")
    bl.make_box(ic, "mj", n=a.n, theta=float(a.theta), sigma=d["sigma"], seed=1)
    base = bl.mesh_overrides(32) + [
        f"particles/dt={d['dt']!r}", f"time/nlim={a.steps}",
        f"particles/coll_sigma={d['sigma']!r}", "particles/snap_dt=1e9", "job/rng_seed=1",
        f"particles/particle_file={os.path.join(ic, 'box.nrp')}"]
    modes = {"particle": ["particles/coll_energy=particle"],
             "cell": ["particles/coll_energy=cell"],
             "off": ["particles/collisions=false"]}
    jobs, names = [], []
    for r in range(a.repeat):
        for m, ov in modes.items():
            rd = os.path.join(out, f"{m}_{r}")
            jobs.append((rd, base + ov, dict(exe=bl.EXE_CPU_C2, deck=DECK)))
            names.append((m, r, rd))
    rr = bl.run_many(jobs, len(jobs))
    res = dict(theta=a.theta, n=a.n, steps=a.steps, runs={})
    for (m, r, rd), x in zip(names, rr):
        e = dict(rc=x["rc"], wall=x["wall"])
        if m != "off" and x["rc"] == 0:
            h = bl.coll_history(rd)
            e.update(n_tested=float(h["n_tested"].sum()), n_coll=float(h["n_coll"].sum()))
        res["runs"][f"{m}_{r}"] = e
    w = {m: np.array([res["runs"][f"{m}_{r}"]["wall"] for r in range(a.repeat)])
         for m in modes}
    nt = res["runs"]["cell_0"].get("n_tested", float("nan"))
    res["wall_mean"] = {m: float(v.mean()) for m, v in w.items()}
    res["wall_spread"] = {m: float(v.max() - v.min()) for m, v in w.items()}
    res["collision_part_per_tested_pair"] = {
        m: float((w[m].mean() - w["off"].mean()) / nt) for m in ("cell", "particle")}
    res["ratio_collision_part_particle_over_cell"] = float(
        (w["particle"].mean() - w["off"].mean()) / (w["cell"].mean() - w["off"].mean()))
    res["ratio_wall_particle_over_cell"] = float(w["particle"].mean() / w["cell"].mean())
    bl.save_json(os.path.join(out, "timing.json"), res)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    sys.exit(main())
