#!/usr/bin/env python3
"""V3 caveat check: does the exact LTB solution of reference B (constants M, E, age per tracked tag) have shell
crossing (R(t, r0) not increasing in r0 at fixed time since the bang) before the end of P0L6 (tau = 141)?
Uses the cycloid of p0l6_verify.py.   python -I ltb_crossing.py --ref REFDIR --out DIR"""
import argparse, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p0l6_verify import cycloid_R  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--ref", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
z = np.load(os.path.join(a.ref, "ltb_reference.npz"))
r0, M, E, age = z["r0B"], z["MB"], z["EB"], z["ageB"]
# one tag per distinct r0 (axes and diagonals share radii)
u, idx = np.unique(np.round(r0, 9), return_index=True)
o = idx[np.argsort(r0[idx])]
out = dict(n_shells=int(len(o)), age_spread=[float(age.min()), float(age.max())], first_crossing=None)
# the initial slice taken as one LTB time: each shell's time since its own bang is age_i + tau
for tau in np.linspace(0.0, 141.0, 1411):
    tb = tau
    R = np.array([cycloid_R(float(M[i]), float(E[i]), np.array([age[i] + tau]))[0] for i in o])
    alive = R > 0
    d = np.diff(R[alive])
    if np.any(d <= 0):
        j = int(np.argmax(d <= 0))
        rr = r0[o][alive]
        out["first_crossing"] = dict(tau=float(tau), r0_pair=[float(rr[j]), float(rr[j + 1])])
        break
print(json.dumps(out))
with open(os.path.join(a.out, "ltb_crossing.json"), "w") as f:
    json.dump(out, f, indent=1)
