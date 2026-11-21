"""Addendum to V4/V5 (g1verify, journal entry 6): three numbers that need the non-scaling part.

usage: v45_addendum.py OUTDIR V45_RUN_DIR
1. Halving factors with the floor defined as A5' of SCOPE 4b does ("the part that does not
   scale with s"): odd part counted where odd > 10 x rms(odd(s) - 2 odd(s/2)), even part
   where even > 10 x rms(even(s) - 4 even(s/2)) (L32, Q64, Q128).
2. Even parts of L128 and L256 (same modes at both N) with the out-band floor of each
   removed in quadrature, and the raw deviation.
3. Negative controls: the ratio of the maxima over the entry (NC odd / proper odd) besides
   the pointwise ratio.
Writes v45_addendum.json.
"""
import os
import sys
import json
import math
import numpy as np

out, vdir = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
r = json.load(open(os.path.join(vdir, "v45.json")))
S = r["sets"]
res = {}
h = {}
for k in ("L32", "Q64", "Q128"):
    o = S[k]
    t = np.array(o["time"])
    odd, even = np.array(o["oddH"]), np.array(o["evenH"])
    nlo, nle = np.array(o["nonlinear_odd"]), np.array(o["nonlinear_even"])
    fo, fe = np.array(o["F_oddH"]), np.array(o["F_evenH"])
    mo = (odd > 10 * nlo) & (t > 0)
    me = (even > 10 * nle) & (t > 0)
    fom, fem = np.array(o["F_oddM"]), np.array(o["F_evenM"])
    h[k] = dict(F_odd=[float(fo[mo].min()), float(fo[mo].max())] if mo.any() else None,
                t_odd=t[mo].tolist(),
                F_even=[float(fe[me].min()), float(fe[me].max())] if me.any() else None,
                t_even=t[me].tolist(),
                F_oddM_same_times=[float(fom[mo].min()), float(fom[mo].max())] if mo.any() else None,
                F_evenM_same_times=[float(fem[me].min()), float(fem[me].max())] if me.any() else None,
                sigma_round_est=(nlo / math.sqrt(10) * 2).tolist(),
                ratio_nleven_nlodd=(nle / np.maximum(nlo, 1e-300)).tolist())
res["halving_nonscaling_floor"] = h
A, B = S["L128"], S["L256"]
rows = []
for i, t in enumerate(B["time"]):
    j = int(np.argmin(np.abs(np.array(A["time"]) - t)))
    ea, fa, eb, fb = A["evenH"][j], A["floorH_even"][j], B["evenH"][i], B["floorH_even"][i]
    ca, cb = math.sqrt(max(ea ** 2 - fa ** 2, 0)), math.sqrt(max(eb ** 2 - fb ** 2, 0))
    rows.append(dict(t=t, t128=A["time"][j], even128=ea, floor128=fa, even256=eb, floor256=fb,
                     raw_dev=eb / ea - 1, floor_removed_dev=cb / ca - 1 if ca > 0 else None))
res["even_L128_L256"] = rows
res["even_L128_L256_max_abs_floor_removed_dev_t_gt_0"] = max(abs(x["floor_removed_dev"]) for x in rows if x["t"] > 0)
res["even_L128_L256_max_abs_raw_dev_t_gt_0"] = max(abs(x["raw_dev"]) for x in rows if x["t"] > 0)
nc = {}
for ncs, prop in (("NC32", "L32"), ("NC64", "Q64"), ("NC128", "Q128")):
    a, b = S[ncs], S[prop]
    n = min(len(a["time"]), len(b["time"]))
    ra = np.array(a["oddH"][1:n]) / np.array(b["oddH"][1:n])
    nc[ncs] = dict(max_ratio=float(max(a["oddH"][1:n]) / max(b["oddH"][1:n])),
                   pointwise_min=float(ra.min()), t_at_min=float(a["time"][1 + int(ra.argmin())]),
                   pointwise=ra.tolist(), times=a["time"][1:n])
res["negative_controls"] = nc
with open(os.path.join(out, "v45_addendum.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("sigma_round_est", "ratio_nleven_nlodd")}
                  for k, v in h.items()}, indent=1))
print("L128-L256 even: max |dev| raw", res["even_L128_L256_max_abs_raw_dev_t_gt_0"],
      "floor removed", res["even_L128_L256_max_abs_floor_removed_dev_t_gt_0"])
print(json.dumps({k: {kk: v[kk] for kk in ("max_ratio", "pointwise_min", "t_at_min")} for k, v in nc.items()}, indent=1))
