#!/usr/bin/env python3
"""Sensitivity of the 'entry maximum' of the constraint records of the convergence rungs to the
window (the ledger does not say which window it uses). Records only, own reader.

Usage: python entrywin.py --out DIR
"""
import argparse
import glob
import json
import os

import numpy as np

RUNG = "/data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261123-020704-2b99463"
WINDOWS = {"0..ln8+0.5": (0.0, np.log(8) + 0.5), "0.5..ln8+0.5": (0.5, np.log(8) + 0.5),
           "1..3": (1.0, 3.0), "0.25..ln8+1": (0.25, np.log(8) + 1.0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for case in ("S", "U"):
        for w, (lo, hi) in WINDOWS.items():
            row = {}
            for n in (32, 64, 128):
                R = np.loadtxt(glob.glob(f"{RUNG}/C{n}{case}/*.sf.con.hst")[0], comments="#")
                s = (R[:, 2] >= lo) & (R[:, 2] <= hi)
                row[n] = dict(H=float(R[s, 3].max()), M=float(R[s, 6].max()),
                              H0=float(R[s, 24].max()) if R.shape[1] >= 26 else None)
            for q in ("H", "M", "H0"):
                if row[32][q] is not None:
                    row[f"order_{q}_32_64"] = float(np.log2(row[32][q]/row[64][q]))
                    row[f"order_{q}_64_128"] = float(np.log2(row[64][q]/row[128][q]))
            res[f"{case} {w}"] = row
    with open(os.path.join(a.out, "entrywin.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
