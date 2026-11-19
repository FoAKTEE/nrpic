#!/usr/bin/env python3
"""Outcome of test TD of tracks/core/JOURNAL-clump2.md: reads the runs of
run_binary_static.py (directory --dir), prints the norms near cluster 0 (within 14 of its
centre) and writes binary_static_check.json into --out.

    binary_static_check.py --dir SCRATCH_RELATIVE_DIR [--out DIR]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
from mp_common import read_bin  # noqa: E402

X0 = np.array([-20.0, 0.0, 0.0])
RCUT = 14.0


def load(top, label):
    d = os.path.join(top, label, "bin")
    _, _, x, y, z, dx, con = read_bin(os.path.join(d, "clump.con.00000.bin"))
    _, _, _, _, _, _, adm = read_bin(os.path.join(d, "clump.adm_psi4.00000.bin"))
    X = np.stack([x, y, z], axis=-1)
    near = np.sqrt(np.sum((X - X0) ** 2, axis=1)) < RCUT
    psi = adm["adm_psi4"] ** 0.25
    return dict(psi=psi, dV=dx ** 3, near=near, H=con["con_H"],
                M=np.stack([con["con_Mx"], con["con_My"], con["con_Mz"]], axis=-1))


def nH(c, H=None):
    H = c["H"] if H is None else H
    return math.sqrt(np.sum((c["psi"] ** 6 * H * H * c["dV"])[c["near"]]))


def nM(c):
    return math.sqrt(np.sum((c["psi"] ** 2 * np.sum(c["M"] ** 2, axis=1) * c["dV"])[c["near"]]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    top = os.path.join(SCRATCH, a.dir)
    c = {k: load(top, k) for k in ("single", "b0", "bv_none", "bv_curv", "bv_corr")}
    with open(os.path.join(top, "cases.json")) as f:
        cj = json.load(f)
    b0 = c["b0"]
    dcurv = c["bv_curv"]["H"] - b0["H"]
    dcorr = c["bv_corr"]["H"] - b0["H"]
    wt = b0["psi"] ** 6 * b0["dV"] * b0["near"]
    out = dict(
        dir=a.dir, lam=cj["ic"]["bv"]["clusters"][0]["lam"],
        momenta=[cj["ic"]["bv"]["athenak"]["problem"][f"comp{k}_p2"] for k in (0, 1)],
        M_ADM=cj["ic"]["bv"]["M_ADM"], M_ADM_rest=cj["ic"]["b0"]["M_ADM"],
        H_single=nH(c["single"]), H_b0=nH(b0), H_b0_over_single=nH(b0) / nH(c["single"]),
        M_none=nM(c["bv_none"]), M_curv=nM(c["bv_curv"]),
        M_ratio=nM(c["bv_curv"]) / nM(c["bv_none"]),
        DH_curv=nH(b0, dcurv), DH_corr=nH(b0, dcorr),
        DH_ratio=nH(b0, dcorr) / nH(b0, dcurv),
        projection=float(np.sum(wt * dcorr * dcurv) / np.sum(wt * dcurv ** 2)),
        history={k: dict(H_norm=math.sqrt(v["hst0"][3]), M_norm=math.sqrt(v["hst0"][4]))
                 for k, v in cj["cases"].items()})
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "binary_static_check.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
