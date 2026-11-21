#!/usr/bin/env python3
"""Particle files of block A for the particle seeds 2 and 3 of the threshold model
(King b = 1, y0 = 0.334032; seed 1 is run C-20261115-174556-3544e2c of threshold_scan):
the equilibria package's stratified sampler at N = 1e5, unperturbed, and with the coherent
one-percent radial kicks inward and outward of threshold_scan/make_scan.py (same function).

    python3 make_ic_seeds.py --out DIR [--seeds 2 3] [--N 100000]
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "threshold_scan"))
import common as C  # noqa: E402
import make_scan as S  # noqa: E402

TAG = "king_y0p33403"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--seeds", type=int, nargs="+", default=[2, 3])
    ap.add_argument("--N", type=int, default=100000)
    a = ap.parse_args()
    make = os.path.join(TRACK, "equilibria", "make_equilibria.py")
    index = {}
    for s in a.seeds:
        out = os.path.join(a.out, f"s{s}")
        os.makedirs(out, exist_ok=True)
        cmd = [sys.executable, make, "--out", out, "--N", str(a.N), "--seed", str(s),
               "--sampler", "stratified", "--only", TAG]
        print("+", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)
        st = C.stem(TAG, N=a.N, seed=s)
        x, u, m, _ = C.nio.read_nrp(os.path.join(out, st + ".nrp"))
        r_tab, u_tab, a_tab, _ = C.nio.read_tab(os.path.join(out, st + ".tab"))
        md = dict(meta=json.load(open(os.path.join(out, st + ".json"))), x=x, u=u, m=m,
                  r_tab=r_tab, psi_tab=1.0 + u_tab, alpha_tab=a_tab)
        r = np.linalg.norm(md["x"], axis=1)
        psi, alp = C.psi_alpha(md, r)
        for name, vp in S.VPERT.items():
            u2 = S.kick(md["x"], md["u"], psi, vp)
            path = os.path.join(out, f"{st}_{name}.nrp")
            C.nio.write_nrp(path, md["x"], u2, md["m"])
            W = np.sqrt(1.0 + np.sum(u2 ** 2, axis=1) / psi ** 4)
            vr = np.sum((u2 / psi[:, None] ** 2) * md["x"], axis=1) / r / W
            index[f"s{s}_{name}"] = dict(file=os.path.relpath(path, a.out), vpert=vp,
                                         mean_radial_velocity=float(np.mean(vr)),
                                         net_momentum=[float(v) for v in (md["m"][:, None] * u2).sum(0)])
            print(s, name, json.dumps(index[f"s{s}_{name}"]), flush=True)
    with open(os.path.join(a.out, "kicks.json"), "w") as f:
        json.dump(index, f, indent=1)


if __name__ == "__main__":
    main()
