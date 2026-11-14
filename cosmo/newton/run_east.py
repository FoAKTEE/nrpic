"""Newtonian reference run of the single-wavelength problem (cosmo/PLAN.md, C2).

    python3 run_east.py --delta 0.01 --n 64 --tend 21.66 --out DIR

Same mesh, filter and step as the relativistic run; the fiducial observers are the
lattice particles on the three lines through the lattice point nearest to the
overdensity peak, in the order of cosmo/ic/make_east.py. Writes DIR/newton.npz."""
import argparse
import os
import time

import numpy as np

import pm as P

ap = argparse.ArgumentParser()
ap.add_argument("--delta", type=float, required=True)
ap.add_argument("--n", type=int, default=64)
ap.add_argument("--ppc", type=int, default=1)
ap.add_argument("--L", type=float, default=4.0)
ap.add_argument("--tend", type=float, required=True)
ap.add_argument("--nfilter", type=int, default=2)
ap.add_argument("--no-compensate", action="store_true")
ap.add_argument("--cfl", type=float, default=0.25)
ap.add_argument("--every", type=int, default=2)
ap.add_argument("--out", required=True)
a = ap.parse_args()

x, v, m, q = P.east_particles(a.delta, a.n, a.ppc, a.L)
npd = a.n*a.ppc
q1 = (np.arange(npd) + (1.0 if a.ppc % 2 == 1 else 0.5))*a.L/npd
ic = int(np.argmin(np.abs(q1 - 0.25*a.L)))
I = [b.ravel() for b in np.meshgrid(np.arange(npd), np.arange(npd), np.arange(npd),
                                    indexing="ij")]
on = [(I[1] == ic) & (I[2] == ic), (I[0] == ic) & (I[2] == ic), (I[0] == ic) & (I[1] == ic)]
centre = on[0] & on[1]
track = np.concatenate([np.flatnonzero(on[0]), np.flatnonzero(on[1] & ~centre),
                        np.flatnonzero(on[2] & ~centre)])
sim = P.PM(x, v, m, a.n, a.L, nfilter=a.nfilter, compensate=not a.no_compensate)
t0 = time.time()
res = P.run(sim, dtau=a.cfl*a.L/a.n, tau_end=a.tend,
            probes=[(0.25*a.L,)*3, (0.75*a.L,)*3], track=track, every=a.every,
            verbose=True)
res["q_fid"] = q[track]
res["axis_fid"] = np.concatenate([np.zeros(npd, int), np.ones(npd - 1, int),
                                  np.full(npd - 1, 2)])
os.makedirs(a.out, exist_ok=True)
np.savez(os.path.join(a.out, "newton.npz"), **res)
print(f"done in {time.time() - t0:.0f} s; a_end = {res['a'][-1]:.2f}; "
      f"delta_obs at the probes at the end: {res['delta_obs_0'][-1]:.4g}, "
      f"{res['delta_obs_1'][-1]:.4g}")
