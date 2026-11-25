#!/usr/bin/env python3
"""Second part of N4 (JOURNAL.md 2026-11-24 05:48): the radiated box measure of the Newtonian
0.014 run at 128^3 (analysis_n128.json, case newton_s014) at a = 120 against the fidL8 value at
a_N = 30 (64^3 Newtonian box, results/analysis_fidL8.json) times 4.014^(-7/2); within a factor 2.

    python3 n4_rad.py --n128 analysis_n128.json --fid analysis_fidL8.json [--out DIR]
"""
import argparse
import json
import os

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--n128", required=True)
ap.add_argument("--fid", required=True)
ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
a = ap.parse_args()
n = {r["name"]: r for r in json.load(open(a.n128))}["newton_s014"]["gw"]["rows"]
f = json.load(open(a.fid))[0]["gw"]["rows"]
n, f = np.array(n), np.array(f)
res = {}
for col, name in ((8, "Omega_rad"), (7, "Omega_rad1"), (6, "Omega_switchoff")):
    i = int(np.argmin(np.abs(n[:, 1] - 120.0)))
    j = int(np.argmin(np.abs(f[:, 1] - 30.0)))
    pred = f[j, col]*4.014**(-3.5)
    res[name] = {"a_128": float(n[i, 1]), "value_128": float(n[i, col]), "a_fid": float(f[j, 1]),
                 "value_fid": float(f[j, col]), "predicted": float(pred), "ratio": float(n[i, col]/pred)}
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(a.out, "n4_rad.json"), "w"), indent=1)
