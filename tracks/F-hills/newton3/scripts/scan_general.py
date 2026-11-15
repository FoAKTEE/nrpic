"""P2: restricted scan over binary orientation (BKRS arXiv:1804.02911 section 3.1).

Part A (isotropic): N_ORI orientations on a Fibonacci lattice over the whole sphere x
N_PHA phases equally spaced in [0, pi) (BKRS mnras.tex:352-357 used 2000 x 200), per D.
Part B (inclination): theta on a uniform grid in [0, pi/2] x N_AZ azimuths x N_PHA
phases, for the D values of BKRS's inclination figures (mnras.tex:490-494, 532-535).
Start 10 r_t, end 30 r_t; 'ambiguous' trajectories rerun to 300 r_t.

Run: cd tracks/F-hills/newton3 && OMP_NUM_THREADS=1 python3 scripts/scan_general.py [--workers 8]
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
from hills3.orbits import fibonacci_sphere  # noqa: E402
import runlib  # noqa: E402

N_ORI, N_PHA = 512, 64
N_TH, N_AZ, N_PHA_B = 31, 32, 64
D_A = np.unique(np.round(np.concatenate([np.logspace(-4, -1, 7), np.arange(0.15, 2.2001, 0.1),
                                          [1.95, 2.05, 2.15]]), 6))
D_B = np.array([1e-5, 1e-2, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0])
CHUNK = 8192


def _run_chunked(D, th, vp, ph):
    n = th.size
    parts = []
    for i in range(0, n, CHUNK):
        sl = slice(i, i + CHUNK)
        o = R.run(D, th[sl], vp[sl], ph[sl], k0=10.0, k_end=30.0)
        amb = o["ambiguous"] & o["ok"]
        if amb.any():
            o2 = R.run(D, th[sl][amb], vp[sl][amb], ph[sl][amb], k0=10.0, k_end=300.0)
            for k in ("E2", "disrupted", "survived", "ambiguous", "rmin", "af", "ef", "ok"):
                o[k][amb] = o2[k]
        parts.append(o)
    keep = ("E2", "disrupted", "survived", "ambiguous", "rmin", "ok")
    return {k: np.concatenate([p[k] for p in parts]) for k in keep}


def task(args):
    part, D = args
    if part == "A":
        th0, vp0 = fibonacci_sphere(N_ORI)
        ph0 = np.linspace(0, np.pi, N_PHA, endpoint=False)
        th = np.repeat(th0, N_PHA)
        vp = np.repeat(vp0, N_PHA)
        ph = np.tile(ph0, N_ORI)
    else:
        th0 = np.linspace(0, np.pi / 2, N_TH)
        az0 = np.linspace(0, 2 * np.pi, N_AZ, endpoint=False)
        ph0 = np.linspace(0, np.pi, N_PHA_B, endpoint=False)
        TH, AZ, PH = np.meshgrid(th0, az0, ph0, indexing="ij")
        th, vp, ph = TH.ravel(), AZ.ravel(), PH.ravel()
    return part, D, _run_chunked(D, th, vp, ph)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    run = runlib.start_run("P2: restricted scan over orientation: isotropic disruption probability "
                           "and mean ejection energy vs D; inclination dependence at fixed D",
                           cores=args.workers, preregistered="tracks/F-hills/newton3/JOURNAL.md#P2")
    jobs = [("A", D) for D in D_A[::-1]] + [("B", D) for D in D_B[::-1]]
    res = {}
    with Pool(args.workers) as pool:
        for part, D, o in pool.imap_unordered(task, jobs):
            res[(part, D)] = o
            ok = o["ok"]
            print(f"{part} D={D:.5g} Pdis={o['disrupted'][ok].mean():.4f} amb={o['ambiguous'].sum()} "
                  f"fail={(~ok).sum()} <|E|>={np.abs(o['E2'][o['disrupted'] & ok]).mean():.4f}",
                  flush=True)
    th0, vp0 = fibonacci_sphere(N_ORI)
    out = {"D_A": D_A, "D_B": D_B, "theta_A": th0, "varphi_A": vp0,
           "phase_A": np.linspace(0, np.pi, N_PHA, endpoint=False),
           "theta_B": np.linspace(0, np.pi / 2, N_TH),
           "varphi_B": np.linspace(0, 2 * np.pi, N_AZ, endpoint=False),
           "phase_B": np.linspace(0, np.pi, N_PHA_B, endpoint=False)}
    for k in ("E2", "disrupted", "survived", "ambiguous", "rmin", "ok"):
        out[f"{k}_A"] = np.stack([res[("A", D)][k].reshape(N_ORI, N_PHA) for D in D_A])
        out[f"{k}_B"] = np.stack([res[("B", D)][k].reshape(N_TH, N_AZ, N_PHA_B) for D in D_B])
    np.savez_compressed(os.path.join(run["dir"], "general.npz"), **out)
    runlib.finish_run(run)


if __name__ == "__main__":
    main()
