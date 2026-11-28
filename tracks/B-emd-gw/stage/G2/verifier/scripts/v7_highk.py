#!/usr/bin/env python3
"""V3 follow-up: is the difference between my raw TT measure above 16 k_f (all modes off the
Nyquist planes) and the analysis file's raw value the shell cut of the files' spectrum
(integer shells up to n/2 = 64 only, so the cube's corner modes with |n| > 64.5 drop out)?
Recomputes, from the two 128^3 dumps at t ~ 20 (a = 121), the measure with and without the
corner modes, and the files' values.

    python3 v7_highk.py OUTDIR SCRATCH
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

out, S = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
L, RHO_C = 8.0, 3.0/(8.0*np.pi)
G6 = ["z4c_gxx", "z4c_gxy", "z4c_gxz", "z4c_gyy", "z4c_gyz", "z4c_gzz"]
KEYS = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
runs = {"zs128": ("B-20261123-014847-f295ab4", "B-20261124-131918-e71996f/analysis_gr.json"),
        "gd128": ("B-20261124-210431-6bf48af", "B-20261125-115558-2ab4161/analysis_gr_gd.json")}
res = {}
for name, (rd, af) in runs.items():
    d, h = vlib.read_mesh(os.path.join(S, rd, "bin", "pop.z4cd.00080.bin"), G6)
    a = float(vlib.scale(h["time"]))
    f = {k: d[nm] - (1.0 if k[0] == k[1] else 0.0) for nm, k in zip(G6, KEYS)}
    del d
    p, KX, KY, KZ, nyq = vlib.tt_power(f, L)
    nn = np.sqrt(KX**2 + KY**2 + KZ**2)
    nk = np.rint(nn).astype(int)
    ok = (~nyq) & (nn > 0)
    w = p*(2*np.pi/L)**2*nn**2*a/(32*np.pi*RHO_C)
    A = json.load(open(os.path.join(S, af)))
    A = A[0] if isinstance(A, list) else A
    fd = min(A["dumps"], key=lambda x: abs(x["t"] - h["time"]))
    spec = np.asarray(fd["spec_raw"])
    res[name] = {"t": h["time"], "a": a, "gt16_all_modes": float(w[ok & (nk > 16)].sum()),
                 "gt16_shells_le64": float(w[ok & (nk > 16) & (nk <= 64)].sum()),
                 "gt16_file_raw": float(spec[17:].sum()), "file_t": fd["t"],
                 "corner_share": float(w[ok & (nk > 64)].sum()/w[ok & (nk > 16)].sum())}
    print(name, res[name], flush=True)
for key in ("gt16_all_modes", "gt16_shells_le64", "gt16_file_raw"):
    res["ratio_zs_over_gd_" + key] = res["zs128"][key]/res["gd128"][key]
json.dump(res, open(os.path.join(out, "v7_highk.json"), "w"), indent=1)
print({k: v for k, v in res.items() if k.startswith("ratio")})
