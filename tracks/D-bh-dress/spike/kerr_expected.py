"""K2 reference: coordinate number density n(r, theta) of the Hernquist-grown Kerr spike
(kerr_lib.moments, E <= E_cut) on a grid of (ln r, cos theta), for the binned counts of the
AthenaK test-particle runs; also the number-weighted <Lz>.

n_x(x, mu) = particles per (d ln r, d cos theta), integrated over phi:
    n_x = 2 pi r n / sin(theta) = 2 pi r * moments()["n_over_sin"]
(equatorial symmetry: mu in [0, 1] covers one hemisphere; the other doubles it).

usage: python3 kerr_expected.py --out DIR [--a 0.8] [--ecut 0.99] [--nx 72] [--nmu 10] [--np 4]
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from kerr_lib import Kerr, KerrHernquist  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
_H = None


def _init():
    global _H
    os.environ["OMP_NUM_THREADS"] = "1"
    _H = KerrHernquist(m_sun=4e6)


def job(arg):
    a, r, mu, ecut = arg
    K = Kerr(a)
    th = np.arccos(mu)
    if K.Delta(r) <= a * a * np.sin(th) ** 2:
        return 0.0, np.nan, 1.0
    m = K.moments(r, th, fmodel=_H, Eup=ecut)
    return 2 * np.pi * r * m.get("n_over_sin", 0.0), m["Lz_mean"], m["Emin"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--a", type=float, default=0.8)
    ap.add_argument("--ecut", type=float, default=0.99)
    ap.add_argument("--rlo", type=float, default=2.05)
    ap.add_argument("--rhi", type=float, default=100.0)
    ap.add_argument("--nx", type=int, default=73)
    ap.add_argument("--nmu", type=int, default=10)
    ap.add_argument("--np", type=int, default=4)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    x = np.linspace(np.log(args.rlo), np.log(args.rhi), args.nx)
    mu = np.linspace(0.0, 1.0, args.nmu)
    jobs = [(args.a, float(np.exp(xx)), float(m), args.ecut) for xx in x for m in mu]
    with mp.Pool(args.np, initializer=_init) as pool:
        res = pool.map(job, jobs, chunksize=1)
    nx = np.array([q[0] for q in res]).reshape(x.size, mu.size)
    lz = np.array([q[1] for q in res]).reshape(x.size, mu.size)
    em = np.array([q[2] for q in res]).reshape(x.size, mu.size)
    np.savez(out / "expected.npz", x=x, mu=mu, n_x=nx, Lz_mean=lz, Emin=em, a=args.a,
             ecut=args.ecut)
    tot = np.trapezoid(np.trapezoid(nx, mu, axis=1), x)
    summ = {"args": vars(args), "total_one_hemisphere": float(tot), "wall_s": time.time() - t0,
            "n_x_at_rhi_over_max": float(nx[-1].max() / nx.max())}
    (out / "expected.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
