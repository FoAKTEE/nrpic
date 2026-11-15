"""Phase scans of HRNA and Newtonian encounters (2404 protocol, article.tex:348 and :452-459).

    <venv>/bin/python -I scan.py --out FILE.npz --laws newton,hrna --senses 1,-1
        --betas START:STOP:N | --betas b1,b2,... [--nphi 400] [--coords sch] [--spin 0]
        [--mb 1e-6] [--a0 1.013] [--r0_rt 50] [--rf_rt 150] [--rtol 1e-12] [--workers 8]

Phases phi_k = pi k / nphi, k = 0..nphi-1 (2404 article.tex:348: 400 phases uniformly in
[0, pi]).  Output: one array per result key with shape (nlaw, nsense, nbeta, nphi).
"""
import argparse
import json
import math
import os
import sys
import time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

KEYS = ["outcome", "separated", "Eb_end", "eb_end", "eps1", "eps2", "L1", "L2", "eps_cm", "L_cm",
        "vinf", "vinf_exact", "t_peri", "r_peri", "t_s", "rcm_ts", "a_min", "alpha_max", "alpha_all",
        "plunged", "status", "nsteps", "t_end"]


def parse_betas(s):
    if ":" in s:
        a, b, n = s.split(":")
        return np.linspace(float(a), float(b), int(n))
    return np.array([float(x) for x in s.split(",")])


def work(task):
    import hrna
    law, sense, beta, phases, kw = task
    rows = []
    for ph in phases:
        o = hrna.run_encounter(law=law, beta=beta, phase=ph, sense=sense, **kw)
        rows.append([float(o[k]) for k in KEYS])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--laws", default="newton,hrna")
    ap.add_argument("--senses", default="1,-1")
    ap.add_argument("--betas", required=True)
    ap.add_argument("--nphi", type=int, default=400)
    ap.add_argument("--coords", default="sch")
    ap.add_argument("--spin", type=float, default=0.0)
    ap.add_argument("--spins", default=None,
                    help="comma list: the first axis then indexes the spin (law hrna, coords cks)")
    ap.add_argument("--mb", type=float, default=1e-6)
    ap.add_argument("--a0", type=float, default=1.013)
    ap.add_argument("--r0_rt", type=float, default=50.0)
    ap.add_argument("--rf_rt", type=float, default=150.0)
    ap.add_argument("--rtol", type=float, default=1e-12)
    ap.add_argument("--q12", type=float, default=1.0)
    ap.add_argument("--ic_gamma", action="store_true",
                    help="internal angular velocity divided by the CM Gamma at release (not 2404)")
    ap.add_argument("--rp_fixed", type=float, default=None,
                    help="keep r_p fixed (in r_g) and set a0 = beta r_p (mb/M)^(1/3) per beta")
    ap.add_argument("--r0_abs", type=float, default=None,
                    help="initial CM distance in r_g (overrides --r0_rt)")
    ap.add_argument("--workers", type=int, default=int(os.environ.get("NRPIC_CORES", "8")))
    a = ap.parse_args()
    laws = a.laws.split(",")
    spins = None
    if a.spins is not None:
        spins = [float(x) for x in a.spins.split(",")]
        laws = ["hrna"] * len(spins)
    senses = [int(x) for x in a.senses.split(",")]
    betas = parse_betas(a.betas)
    phases = math.pi * np.arange(a.nphi) / a.nphi
    kw = dict(coords=a.coords, spin=a.spin, mb=a.mb, a0=a.a0, r0_rt=a.r0_rt, rf_rt=a.rf_rt,
              rtol=a.rtol, q12=a.q12, ic_gamma=a.ic_gamma)
    nchunk = 4
    chunks = np.array_split(phases, nchunk)
    tasks, index = [], []
    for il, law in enumerate(laws):
        for js, se in enumerate(senses):
            for ib, be in enumerate(betas):
                kwb = dict(kw)
                if spins is not None:
                    kwb["spin"] = spins[il]
                    kwb["coords"] = "cks"
                if a.rp_fixed is not None:
                    kwb["a0"] = float(be) * a.rp_fixed * a.mb ** (1 / 3)
                rt = kwb["a0"] * a.mb ** (-1 / 3)
                if a.r0_abs is not None:
                    kwb["r0_rt"] = a.r0_abs / rt
                for ic, ch in enumerate(chunks):
                    tasks.append((law, se, float(be), ch, kwb))
                    index.append((il, js, ib, ic))
    res = np.full((len(laws), len(senses), len(betas), a.nphi, len(KEYS)), np.nan)
    offs = np.concatenate([[0], np.cumsum([len(c) for c in chunks])])
    import hrna
    hrna.run_encounter(law="hrna", beta=1.0, phase=0.0, rf_rt=2.0, r0_rt=2.0)   # compile once
    t0 = time.time()
    with get_context("fork").Pool(a.workers) as pool:
        for n, rows in enumerate(pool.imap(work, tasks, chunksize=1)):
            il, js, ib, ic = index[n]
            res[il, js, ib, offs[ic]:offs[ic + 1], :] = np.array(rows)
            if n % 200 == 0:
                print(f"{n}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    out = {k: res[..., i] for i, k in enumerate(KEYS)}
    meta = dict(laws=laws, spins=spins, senses=senses, nphi=a.nphi, kw=kw, rp_fixed=a.rp_fixed, r0_abs=a.r0_abs,
                wall_s=time.time() - t0)
    np.savez_compressed(a.out, betas=betas, phases=phases, meta=json.dumps(meta), **out)
    print("done", a.out, f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
