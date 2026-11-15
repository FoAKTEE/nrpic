"""P1: coplanar restricted scan (SKR arXiv:0911.1136 sections 5-7).

For every D of the grid and both directions, N_PHA phases equally spaced in [0, pi)
(SKR prp.tex:763-764: 3000 points in [0, pi]); start 10 r_t (SKR prp.tex:599), end
30 r_t; trajectories left 'ambiguous' (bound but wide) are rerun to 300 r_t.
Writes coplanar.npz into the run directory.

Run: cd tracks/F-hills/newton3 && OMP_NUM_THREADS=1 python3 scripts/scan_coplanar.py [--workers 8]
"""
import argparse
import os
import sys
import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from hills3 import restricted as R  # noqa: E402
import runlib  # noqa: E402

N_PHA = 3000


def d_grid():
    g = np.concatenate([np.logspace(-5, -1.5, 15), np.arange(0.04, 2.3001, 0.02),
                        np.arange(0.395, 0.4851, 0.005), np.arange(2.05, 2.1501, 0.005)])
    return np.unique(np.round(g, 6))


RTOL = 1e-10


def task(args):
    D, prograde = args
    ph_skr = np.linspace(0, np.pi, N_PHA, endpoint=False)
    th, vp, ph = R.coplanar_phase(ph_skr, prograde)
    o = R.run(D, th, vp, ph, k0=10.0, k_end=30.0, rtol=RTOL, atol=RTOL * 1e-3)
    amb = o["ambiguous"] & o["ok"]
    n_rerun = int(amb.sum())
    if n_rerun:
        o2 = R.run(D, th, vp, np.asarray(ph)[amb], k0=10.0, k_end=300.0, rtol=RTOL,
                   atol=RTOL * 1e-3)
        for k in ("E2", "disrupted", "survived", "ambiguous", "rmin", "af", "ef", "ok"):
            o[k][amb] = o2[k]
    keep = ("E2", "disrupted", "survived", "ambiguous", "rmin", "af", "ok", "nacc")
    return D, prograde, {k: o[k] for k in keep}, n_rerun


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--rtol", type=float, default=1e-10)
    ap.add_argument("--D-list", default=None, help="comma-separated D values (supplement run)")
    args = ap.parse_args()
    global RTOL
    RTOL = args.rtol
    run = runlib.start_run("P1: coplanar restricted scan, disruption probability and ejection "
                           "energy vs penetration factor, both directions, 3000 phases per D"
                           + (f" (supplement at rtol {args.rtol:g}: D = {args.D_list})" if args.D_list else ""),
                           cores=args.workers, preregistered="tracks/F-hills/newton3/JOURNAL.md#P1")
    Ds = d_grid() if not args.D_list else np.array([float(x) for x in args.D_list.split(",")])
    jobs = [(D, pro) for D in Ds[::-1] for pro in (True, False)]
    res = {}
    with Pool(args.workers) as pool:
        for D, pro, o, nr in pool.imap_unordered(task, jobs):
            res[(D, pro)] = o
            print(f"D={D:.5g} {'pro' if pro else 'ret'} Pdis={o['disrupted'][o['ok']].mean():.4f} "
                  f"amb={o['ambiguous'].sum()} fail={(~o['ok']).sum()} rerun={nr}", flush=True)
    out = {"D": Ds, "phase_skr": np.linspace(0, np.pi, N_PHA, endpoint=False)}
    for pro, tag in ((True, "pro"), (False, "ret")):
        for k in ("E2", "disrupted", "survived", "ambiguous", "rmin", "af", "ok", "nacc"):
            out[f"{k}_{tag}"] = np.stack([res[(D, pro)][k] for D in Ds])
    np.savez_compressed(os.path.join(run["dir"], "coplanar.npz"), **out)
    runlib.finish_run(run)


if __name__ == "__main__":
    main()
