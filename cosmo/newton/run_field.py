"""Newtonian particle-mesh run of a random field (the Newtonian counterpart of the
random-field runs of the relativistic code, cosmo/PLAN.md C5): the density field
delta0.npy of an initial-data directory, particles from make_field.newtonian_particles,
the cloud and its compensation as in the relativistic run, to z = 0.

    python3 run_field.py --ic-dir ../../runs/cosmo/dav_c704_n32_pcs4t --ppc 2 --shape pcs \
        --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 --out DIR

Writes DIR/newton_field.npz: the density contrast on the mesh at z = 1000, 100, 10, 1, 0.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ic"))
import cosmo_id as cid  # noqa: E402
import make_field as mf  # noqa: E402
import pm as P  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--ic-dir", required=True)
ap.add_argument("--ppc", type=int, default=2)
ap.add_argument("--shape", default="pcs", choices=("cic", "tsc", "pcs"))
ap.add_argument("--dep-comp-c", type=float, default=0.0)
ap.add_argument("--dep-comp-c2", type=float, default=0.0)
ap.add_argument("--cfl", type=float, default=0.25)
ap.add_argument("--dt-expansion", type=float, default=0.01)
ap.add_argument("--out", required=True)
a = ap.parse_args()

delta = np.load(os.path.join(a.ic_dir, "delta0.npy"))
meta = json.load(open(os.path.join(a.ic_dir, "meta.json")))
L, n = meta["L_code"], delta.shape[0]
cid.SHAPE = a.shape
cid.DEP_COMP_C, cid.DEP_COMP_C2 = a.dep_comp_c, a.dep_comp_c2
x, v, m, q = mf.newtonian_particles(delta, L, 1.0, a.ppc)
sim = P.PM(x, v, m, n, L, nfilter=0, compensate=False, shape=a.shape)
times = [4.2962, 17.0788, 42.7439, 61.277]              # z = 100, 10, 1, 0
out = {"t": [0.0], "delta": [sim.delta.copy()]}
h = L/n
t0 = time.time()
step = 0
for tend in times:
    while sim.tau < tend - 1e-12:
        dt = min(a.cfl*h, a.dt_expansion*(1.0 + 0.5*sim.tau), tend - sim.tau)
        sim.step(dt)
        step += 1
        if step % 200 == 0:
            print(f"  step {step}  tau = {sim.tau:.3f}  a = {P.scale_factor(sim.tau):.2f}  "
                  f"rms delta = {sim.delta.std():.4e}  ({time.time() - t0:.0f} s)", flush=True)
    out["t"].append(sim.tau)
    out["delta"].append(sim.delta.copy())
os.makedirs(a.out, exist_ok=True)
np.savez_compressed(os.path.join(a.out, "newton_field.npz"), t=np.array(out["t"]),
                    delta=np.array(out["delta"]), L=L, box=meta["box_mpch"])
print(f"done in {time.time() - t0:.0f} s, {step} steps")
