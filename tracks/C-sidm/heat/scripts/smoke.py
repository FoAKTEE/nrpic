#!/usr/bin/env python3
"""S0 of the heat package: does the deck run with core's collisions-2 processor
executable, and what does one particle cost per collision time in a mode box?

Mode box at theta = 0.003, k lambda = 0.2 (lambda = 1, Lx = 2 pi/k, 128 x 4 x 4 cells,
dx = 0.245 lambda), 2e5 particles, dt = 0.1 t_coll, 60 steps, with
coll_energy = particle and = cell (same particles and seed; in a flat box the two must
agree to rounding). Writes smoke.json into the run directory.
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl   # noqa: E402
import rate            # noqa: E402
import snap            # noqa: E402


def main():
    out = hl.outdir("smoke")
    th, kl, N = 0.003, 0.2, 200000
    k = kl
    Lx = 2 * np.pi / k
    box = [Lx, 1.0, 1.0]
    nx = [128, 4, 4]
    tcoll = 1.0 / float(rate.vmol_mean(th))
    dt = 0.1 * tcoll
    nsteps = 60
    jobs = []
    for energy in ("particle", "cell"):
        d = os.path.join(out, energy)
        meta = hl.make_box(d, "mode", n=N, box=box, theta=th, eps=0.05, kmode=1, sigma=1.0,
                           seed=11)
        ovr = hl.overrides(box, nx, dt, nsteps * dt * (1 + 1e-9), 20 * dt, 1.0, 1,
                           energy=energy)
        jobs.append((d, ovr))
    with ThreadPoolExecutor(2) as ex:
        res = list(ex.map(lambda j: hl.run_athena(j[0], j[1]), jobs))
    summary = dict(theta=th, k_lambda=kl, N=N, t_coll=tcoll, dt=dt, nsteps=nsteps)
    for (d, _), r, energy in zip(jobs, res, ("particle", "cell")):
        cs = hl.coll_summary(d) if r["rc"] == 0 else {}
        summary[energy] = dict(rc=r["rc"], wall=r["wall"], coll=cs,
                               s_per_particle_step=r["wall"] / (N * nsteps),
                               s_per_particle_tcoll=r["wall"] / (N * nsteps * 0.1),
                               s_per_tested_pair=(r["wall"] / cs["n_tested"]) if cs else None)
    try:
        fa = snap.snapshots(jobs[0][0], hl.BASE)[-1]
        fb = snap.snapshots(jobs[1][0], hl.BASE)[-1]
        a, b = snap.read_snapshot(fa), snap.read_snapshot(fb)
        summary["particle_vs_cell_max_du"] = float(np.abs(a["u"] - b["u"]).max())
        summary["particle_vs_cell_max_dx"] = float(np.abs(a["x"] - b["x"]).max())
    except Exception as e:      # report, do not hide
        summary["compare_error"] = repr(e)
    with open(os.path.join(out, "smoke.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
