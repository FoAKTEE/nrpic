#!/usr/bin/env python3
"""G2M-1b of g2mesh: the largest tree along the tracks at the regrid cadence (16^3 blocks).

AthenaK regrids every refinement_interval = 8 cycles (P1's input) and stops when a new tree
needs more MeshBlocks than max_nmb_per_rank (mesh/mesh_refinement.cpp lines 494-500), so the
slots must cover the largest tree at any regrid, not at the 0.25 M samples of model_run.py.
Here every variant with 16^3 blocks is evaluated at every 8th cycle of its own time step
(dt = cfl * h_min, cfl = 0.25): along P1's measured tracks (interpolated) and the Newtonian
tracks to 280 M. Writes the maximum, its time, upper percentiles, the fraction of regrids
above slot limits, and the mean (for the cost). Usage: fine_max.py <out> [--cores N]
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model_run as mr  # noqa: E402
import tree3 as t3  # noqa: E402

LIMITS = (2400, 2700, 2800, 2900, 3000, 3100, 3200)
BLOCK = 16
_INP = None


def _init(path):
    global _INP
    _INP = t3.read_athinput(path)


def _count(args):
    res, name, k, pos = args
    return res, name, k, t3.total(mr.tree_for(_INP, res, BLOCK).build(np.asarray(pos)))


def main():
    out = sys.argv[1]
    cores = int(sys.argv[sys.argv.index("--cores") + 1]) if "--cores" in sys.argv else 1
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, os.path.join(mr.WT, "tracks/F-hills/nr_first/scripts"))
    sys.path.insert(0, os.path.join(mr.WT, "tracks/F-hills/stage/G0/checks"))
    import nrread as nr
    import lead_checks as lc
    inp = t3.read_athinput(mr.P1_INPUT)
    trk = nr.read_trackers(mr.P1_RUN)
    keys = sorted(trk)
    m, x, p = lc.read_athinput(mr.P1_INPUT)
    tracks, jobs = {}, []
    for res in mr.RES:
        T = mr.tree_for(inp, res, BLOCK)
        dt_regrid = 8 * mr.CFL * T.h(T.lmax)
        tn = np.arange(0.0, mr.T_PASS + 1e-9, dt_regrid)
        ts, Y = lc.newton_full(m, x, p, t_end=tn[-1], nout=len(tn))
        XN = Y[:, :9].reshape(-1, 3, 3)
        t1 = min(trk[k]["t"][-1] for k in keys)
        tp = np.arange(0.0, t1, dt_regrid)
        XP = np.stack([np.stack([np.interp(tp, trk[k]["t"], trk[k]["x"][:, c]) for c in range(3)], 1)
                       for k in keys], axis=1)
        tracks[res] = dict(dt_regrid=dt_regrid, newton=ts, p1=tp)
        jobs += [(res, "newton", i, XN[i].tolist()) for i in range(len(ts))]
        jobs += [(res, "p1", i, XP[i].tolist()) for i in range(len(tp))]
    t0 = time.time()
    with Pool(cores, initializer=_init, initargs=(mr.P1_INPUT,)) as pool:
        got = pool.map(_count, jobs, chunksize=64)
    print("%d trees in %.0f s" % (len(jobs), time.time() - t0))
    res_out = {}
    for res in mr.RES:
        r = dict(dt_regrid=tracks[res]["dt_regrid"])
        for name in ("newton", "p1"):
            n = np.zeros(len(tracks[res][name]), dtype=int)
            for rr, nm, k, c in got:
                if rr == res and nm == name:
                    n[k] = c
            t = tracks[res][name]
            i = int(np.argmax(n))
            r[name] = dict(n_regrids=int(len(n)), t_end=float(t[-1]), n_max=int(n.max()),
                           t_max=float(t[i]), n_mean=float(n.mean()),
                           p99=float(np.percentile(n, 99)), p999=float(np.percentile(n, 99.9)),
                           frac_above={str(L): float(np.mean(n > L)) for L in LIMITS},
                           n_above={str(L): int(np.sum(n > L)) for L in LIMITS})
            np.save(os.path.join(out, f"n_{res}_{name}.npy"), np.stack([t, n]))
            print(res, name, "regrids", len(n), "max", n.max(), "at %.3f" % t[i], "mean %.0f" % n.mean(),
                  "p99.9 %.0f" % r[name]["p999"], "above 3000:", r[name]["n_above"]["3000"])
        res_out[res] = r
    json.dump(dict(block=BLOCK, limits=LIMITS, variants=res_out),
              open(os.path.join(out, "fine_max.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
