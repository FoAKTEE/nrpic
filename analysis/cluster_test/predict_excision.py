#!/usr/bin/env python3
"""Exact-metric prediction of the lapse excision of the plunging family: every particle
that make_cluster.classify marks as plunging is integrated from its initial state with
the exact Cartesian Kerr-Schild geodesic equations (RK4, dt/4 substeps) on the cycle grid
dt = 0.05 M until the exact lapse drops below alpha_exc = 0.62.  Writes
runs/cluster_test/ic/plunge_a{a}_pred_excision.npz (tag, cycles, position) and prints the
removal times and radii, for comparison with the excision history of the mesh runs.
"""
import time

import numpy as np

import ct_common as C
from fig_excision import continue_to_excision
from nrpic.io import read_nrp


def main():
    for a in (0.0, 0.9):
        x, u, m, sp = read_nrp(f"{C.RUNS}/ic/plunge_a{a}_n10000.nrp")
        pred = np.load(f"{C.RUNS}/ic/plunge_a{a}_n10000.class.npy")
        sel = np.nonzero(pred == 1)[0]
        t0 = time.time()
        ncyc, xr = continue_to_excision(x[sel], u[sel], a, nsub=4, nmax=8000)
        r = C.kerr.cks_radius(xr, a)
        t = ncyc[ncyc >= 0] * C.DT
        print(a, "n", len(sel), "not reached", np.sum(ncyc < 0),
              "removal time pct 0/10/50/90/99/100:", np.percentile(t, [0, 10, 50, 90, 99, 100]),
              "r pct 0/50/100:", np.nanpercentile(r, [0, 50, 100]),
              "excised by 100/200/300 M:", [int((t <= s).sum()) for s in (100, 200, 300)],
              f"{time.time() - t0:.0f} s")
        np.savez(f"{C.RUNS}/ic/plunge_a{a}_pred_excision.npz", tag=sel, ncyc=ncyc, xr=xr)


if __name__ == "__main__":
    main()
