"""Newtonian particle-mesh reference (cosmo/newton/pm.py, used as a library, unchanged)
for the plane-wave pancake of verify_cosmo.

    python3 newton_pancake.py --delta 0.05 --n 64 --L 1 --tend 10.9615 --out DIR

Particles: pm.east_particles with ratios (1, 0, 0), i.e. the Newtonian positions,
velocities and masses that cosmo/ic/make_east.py --ratios 1,0,0 uses for its positions
(identical positions in both calculations). Numerics as the production configuration of
cosmo/README.md: cubic cloud, compensation c = 1/6, c2 = 7/15 on the deposited density,
no filter, cubic-spline force interpolation, step a quarter cell.

Writes DIR/newton.npz: tau, a, x (records, sheets; unwrapped, sheets of the x line in
order of their lattice coordinate), v (dx/dtau of the same), q (lattice coordinates),
m_line (masses on the line), and, at the requested times, the plane-averaged density
contrast and potential on the mesh (prof_tau, prof_delta, prof_psi), plus the spread of
the positions over each lattice plane (plane-symmetry check) at those times.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "cosmo", "newton"))
import pm as P  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--delta", type=float, required=True)
ap.add_argument("--n", type=int, default=64)
ap.add_argument("--L", type=float, default=1.0)
ap.add_argument("--ppc", type=int, default=1, help="particles per cell and direction")
ap.add_argument("--tend", type=float, required=True)
ap.add_argument("--cfl", type=float, default=0.25)
ap.add_argument("--every", type=int, default=2)
ap.add_argument("--prof-a", default="1,2,5,10,15,18,20,21,22,25,30,35,42",
                help="scale factors at which mesh profiles are recorded")
ap.add_argument("--out", required=True)
a = ap.parse_args()

P.cid.DEP_COMP_C = 1.0/6.0
P.cid.DEP_COMP_C2 = 7.0/15.0
x, v, m, q = P.east_particles(a.delta, a.n, a.ppc, a.L, ratios=(1.0, 0.0, 0.0))
n, L = a.n, a.L
npd = n*a.ppc
h = L/n
# the x line through the first lattice point in y and z, ordered by q_x
line = np.flatnonzero((np.abs(q[:, 1] - q[0, 1]) < 1e-12*L)
                      & (np.abs(q[:, 2] - q[0, 2]) < 1e-12*L))
line = line[np.argsort(q[line, 0])]
qx = q[line, 0]
# lattice-plane index of every particle (for the plane-symmetry check)
iplane = np.rint(q[:, 0]/(L/npd) - (1.0 if a.ppc % 2 == 1 else 0.5)).astype(int) % npd

sim = P.PM(x, v, m, n, L, nfilter=0, compensate=False, shape="pcs")
dtau = a.cfl*L/n
nstep = int(round(a.tend/dtau))
prof_a = [float(s) for s in a.prof_a.split(",")]
prof_tau = [2.0*(np.sqrt(ai) - 1.0) for ai in prof_a]
prof_step = sorted(set(int(round(t/dtau)) for t in prof_tau if t <= a.tend + 0.5*dtau))


def unwrap(xx, qq):
    return qq + np.mod(xx - qq + 0.5*L, L) - 0.5*L


rec = {"tau": [], "a": [], "x": [], "v": []}
prof = {"tau": [], "delta": [], "psi": [], "spread_x": [], "max_vperp": []}
xu = unwrap(sim.x[line, 0], qx)


def record():
    rec["tau"].append(sim.tau)
    rec["a"].append(P.scale_factor(sim.tau))
    rec["x"].append(xu.copy())
    rec["v"].append(sim.velocity()[line, 0].copy())


def profile():
    prof["tau"].append(sim.tau)
    prof["delta"].append(sim.delta.mean(axis=(1, 2)))
    prof["psi"].append(sim.psi().mean(axis=(1, 2)))
    # spread of x over each lattice plane relative to the line particle of that plane
    xl = sim.x[line, 0]
    dx = sim.x[:, 0] - xl[iplane]
    dx -= L*np.round(dx/L)
    prof["spread_x"].append(float(np.abs(dx).max()))
    prof["max_vperp"].append(float(np.abs(sim.velocity()[:, 1:]).max()))


t0 = time.time()
record()
if 0 in prof_step:
    profile()
for s in range(nstep):
    xb = sim.x[line, 0].copy()
    sim.step(dtau)
    dx = sim.x[line, 0] - xb
    dx -= L*np.round(dx/L)
    xu += dx
    if (s + 1) % a.every == 0 or s == nstep - 1:
        record()
    if (s + 1) in prof_step:
        profile()
    if (s + 1) % 200 == 0:
        print(f"step {s+1}/{nstep} a = {P.scale_factor(sim.tau):.3f} "
              f"max delta = {sim.delta.max():.4g} ({time.time() - t0:.0f} s)", flush=True)
os.makedirs(a.out, exist_ok=True)
out = {k: np.array(val) for k, val in rec.items()}
out.update({f"prof_{k}": np.array(val) for k, val in prof.items()})
out.update({"q": qx, "m_line": m[line], "x0_line": x[line, 0], "v0_line": v[line, 0],
            "n": n, "ppc": a.ppc, "L": L, "delta": a.delta, "dtau": dtau})
np.savez(os.path.join(a.out, "newton.npz"), **out)
with open(os.path.join(a.out, "newton.json"), "w") as f:
    json.dump({"n": n, "ppc": a.ppc, "L": L, "delta": a.delta, "dtau": dtau, "nstep": nstep,
               "wall_s": time.time() - t0, "a_end": float(out["a"][-1])}, f, indent=1)
print(f"done in {time.time() - t0:.0f} s, a_end = {out['a'][-1]:.3f}")
