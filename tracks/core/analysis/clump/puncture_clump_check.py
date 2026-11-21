#!/usr/bin/env python3
"""Test T7 of tracks/core/JOURNAL-clump.md: two Gaussian clumps with momentum (one with
spin) beside a Bowen-York puncture with momentum, at t = 0 on processors
(problems/tests/clump_puncture.athinput). Three runs that differ only in <problem>:
  all     curvature of the clumps and of the puncture
  punc    clumps' momenta and spin set to zero in the curvature (puncture's kept)
  clumps  puncture's momentum set to zero (clumps' kept)
Projection of the momentum constraint on the smooth field of the clumps,
T_i = -8 pi psi^-6 Stilde_i (closed form, psi with the puncture), over the cells within
4 sigma of a clump centre: A = <M, T>/<T, T>, <f, g> = sum f_i g_i psi^6 dV.

    puncture_clump_check.py --out DIR     (registered: runreg.py ... --out {out})
Writes puncture_clump_check.json into DIR and into this directory.
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
from mp_common import read_bin  # noqa: E402
from nrpic import clumps as clm  # noqa: E402

EXE = os.environ.get("NRPIC_EXE_CPU", os.path.join(WT, ".work", "build_cpu", "src", "athena"))
INPUT = os.path.join(WT, "problems", "tests", "clump_puncture.athinput")
GA = ["--gaussian", "0.2,1,-3,0,0,0,-0.04,0", "--gaussian", "0.2,1,3,0,0,0,0.04,0,0,0,0.02",
      "--puncture", "1,0,5,0,0.1,0,0"]
ZC = [f"problem/comp{c}_{k}{a}=0.0" for c in (0, 1) for k in "ps" for a in (1, 2, 3)]
CASES = {"all": [], "punc": ZC, "clumps": ["problem/comp2_p1=0.0"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    top = a.out
    env = dict(os.environ, OMP_NUM_THREADS="1")
    subprocess.run([sys.executable, os.path.join(WT, "problems", "ic", "make_ic.py"),
                    "clumps", *GA, "--sampler", "lattice", "--lattice-h", "0.125", "--out",
                    top, "--prefix", "particles"], check=True, env=env)
    with open(os.path.join(top, "particles.json")) as f:
        meta = json.load(f)

    def run(label):
        d = os.path.join(top, label)
        os.makedirs(d, exist_ok=True)
        if not os.path.exists(os.path.join(d, "particles.nrp")):
            os.symlink(os.path.join("..", "particles.nrp"), os.path.join(d, "particles.nrp"))
        with open(os.path.join(d, "athena.log"), "w") as log:
            st = subprocess.run([EXE, "-i", INPUT, "-d", d, *CASES[label]], cwd=d,
                                stdout=log, stderr=subprocess.STDOUT, env=env).returncode
        if st != 0:
            raise RuntimeError(f"{label}: exit status {st}")
        with open(os.path.join(d, "clump.z4c.user.hst")) as f:
            return label, [float(v) for v in
                           next(l for l in f if not l.startswith("#")).split()]

    with ThreadPoolExecutor(3) as ex:
        hst = dict(ex.map(run, CASES))

    G = clm.GaussianClumps(meta["gaussians"], meta["punctures"])
    out = dict(problem=meta["athenak"]["problem"], particles_by_clump=meta["particles_by_clump"],
               history_t0={k: dict(H2=v[3], M2=v[4], Mx2=v[6], My2=v[7], Mz2=v[8])
                           for k, v in hst.items()}, projection={})
    geom = None
    for label in CASES:
        t, par, x, y, z, dx, var = read_bin(os.path.join(top, label, "bin",
                                                         "clump.con.00000.bin"))
        if geom is None:
            X = np.stack([x, y, z], axis=-1)
            near = np.zeros(len(x), bool)
            for g in G.gaussians:
                near |= np.sum((X - g["centre"]) ** 2, axis=-1) < (4.0 * g["sigma"]) ** 2
            X = X[near]
            psi = G.psi(X)
            w = psi ** 6 * dx[near] ** 3
            T = -8.0 * np.pi * psi[:, None] ** -6 * G.momentum_density(X)
            tt = float(np.sum(w[:, None] * T * T))
            geom = True
        M = np.stack([var["con_Mx"][near], var["con_My"][near], var["con_Mz"][near]], axis=-1)
        out["projection"][label] = dict(
            A=float(np.sum(w[:, None] * M * T) / tt),
            M_norm_near_clumps=float(np.sqrt(np.sum(w[:, None] * M * M))),
            T_norm=float(np.sqrt(tt)))
    for path in (os.path.join(top, "puncture_clump_check.json"),
                 os.path.join(HERE, "puncture_clump_check.json")):
        with open(path, "w") as f:
            json.dump(out, f, indent=1)
    for k in CASES:
        h, p = out["history_t0"][k], out["projection"][k]
        print(f"{k:7s} M-norm2 {h['M2']:.6e} Mx2 {h['Mx2']:.6e} My2 {h['My2']:.6e} "
              f"H-norm2 {h['H2']:.6e};  near the clumps: A = {p['A']:+.5f}, "
              f"|M| = {p['M_norm_near_clumps']:.4e}, |T| = {p['T_norm']:.4e}")


if __name__ == "__main__":
    main()
