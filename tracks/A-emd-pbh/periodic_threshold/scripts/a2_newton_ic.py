#!/usr/bin/env python3
"""A2 control (JOURNAL 2026-11-25 08:10 PST): particle files of the Newtonian members from S1L's particle file.

    a2_newton_ic.py --src particles.nrp --out DIR [--box 20 --n 64]

N-z.nrp: S1L's positions x, equal masses rho_m L^3 / N (rho_m = 3/(8 pi), H = 1 at a = 1), momenta p = x - q (q the
lattice site): the pure Newtonian Zel'dovich growing mode at a = 1 (f = 1, D = a; in conformal time with a = (1+eta/2)^2
p = a dx/deta = dD/deta psi = psi at a = 1). N-f uses S1L's file unchanged (not written here).
Writes N-z.nrp and ic.json (lattice offset, displacement and velocity statistics of the source file)."""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from nrpic import io as nio  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--box", type=float, default=20.0)
    ap.add_argument("--n", type=int, default=64)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    x, u, m, sp = nio.read_nrp(a.src)
    L, n = a.box, a.n
    h = L / n
    off = np.array([np.median(np.mod(x[:, d] + L / 2, h)) for d in range(3)])
    q = np.rint((x + L / 2 - off) / h) * h - L / 2 + off
    d = x - q
    idx = np.rint((q + L / 2 - off) / h).astype(int) % n
    lin = idx[:, 0] + n * (idx[:, 1] + n * idx[:, 2])
    assert len(np.unique(lin)) == n ** 3 == len(x), "lattice not one-to-one"
    rho_m = 3.0 / (8.0 * math.pi)
    m_eq = np.full(len(x), rho_m * L ** 3 / len(x))
    nio.write_nrp(os.path.join(a.out, "N-z.nrp"), x, d.copy(), m_eq, species=sp)
    s = np.abs(d) > 1e-3
    ratio = [float(np.median(u[s[:, k], k] / d[s[:, k], k])) for k in range(3)]
    info = dict(src=os.path.abspath(a.src), n=n, box=L, lattice_offset=off.tolist(), max_abs_disp_over_h=float(np.abs(d).max() / h),
                total_mass_src=float(m.sum()), total_mass_eq=float(m_eq.sum()), mass_src_min_over_mean=float(m.min() / m.mean()),
                mass_src_max_over_mean=float(m.max() / m.mean()), median_u_over_disp=ratio,
                p95_u_over_disp=[float(np.percentile(u[s[:, k], k] / d[s[:, k], k], 95)) for k in range(3)])
    json.dump(info, open(os.path.join(a.out, "ic.json"), "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
