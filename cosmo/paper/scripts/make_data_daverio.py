"""Data of the tests of Daverio, Dirian & Mitsou for the working paper: homogeneous
universe with and without noise (tests A0, A) and the plane-wave linear mode (test B)."""
import os

import numpy as np

from common import DATA, RUNS
import daverio_a as da
import daverio_b as db


def thin(n, m=500):
    return np.unique(np.linspace(0, n - 1, min(n, m)).astype(int))


out = {}
for k in ("a0", "a", "a0k", "anp"):
    for n in (8, 16, 32):
        d = da.load(os.path.join(RUNS, f"dav_{k}_n{n}"))
        if d is None:
            continue
        i = thin(len(d["t"]))
        for key in ("t", "a", "dchi", "dE", "H", "M"):
            out[f"{k}_{n}_{key}"] = d[key][i]
for c in ("dav_b_n32", "dav_b_n32_c01", "dav_b_n64", "dav_b_n32_pcs4b_f2", "dav_b_n64_pcs4b"):
    d = db.load(os.path.join(RUNS, c))
    if d is None:
        continue
    tag = c.replace("dav_b_", "")
    out[f"b_{tag}_x"] = d["x"]
    out[f"b_{tag}_phi0"] = d["phi"][0] - d["phi"][0].mean()
    out[f"b_{tag}_phi1"] = d["phi"][-1] - d["phi"][-1].mean()
    out[f"b_{tag}_t"] = d["t"]
    out[f"b_{tag}_dd0"] = d["dd0"]
    out[f"b_{tag}_phi_amp"] = d["phi_amp"]
    i = thin(len(d["ct"]))
    out[f"b_{tag}_ct"] = d["ct"][i]
    out[f"b_{tag}_Hr"] = d["Hr_max"][i]
np.savez_compressed(os.path.join(DATA, "daverio.npz"), **out)
print("wrote", os.path.join(DATA, "daverio.npz"), sorted({k.split("_")[0] + "_" + k.split("_")[1] for k in out}))
