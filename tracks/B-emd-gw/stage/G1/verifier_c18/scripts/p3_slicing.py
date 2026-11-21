"""P3: ledger row 125 (first-order slicing of the earlier three-wave runs) from their restart dumps.

For each restart dump of runs/cosmo/dav_c256_n128_t and _pcs4bt (read-only): a = <chi>^(-1/2),
d ln alpha and d ln gamma^(1/6) (gamma^(1/6) = chi^(-1/2) for chi = gamma^(-1/3)) about their box
means; Pearson correlation of the two; rms of d ln(alpha gamma^(1/6)) over rms of d ln alpha.
A Newtonian slicing at first order has alpha gamma^(1/6) = a(t) * (1 + O(Phi^2)): correlation -1.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", "/data/haiyangw/nrpic/scratch/B-emd-gw/tmp/p3")
os.makedirs(OUT, exist_ok=True)
res = {}
for run in ("dav_c256_n128_t", "dav_c256_n128_pcs4bt"):
    rows = []
    for f in sorted(glob.glob(f"/data/haiyangw/nrpic/runs/cosmo/{run}/rst/east.*.rst")):
        d = vlib.read_rst(f, want={"chi", "alpha"})
        la = np.log(d["alpha"]); lg = -0.5 * np.log(d["chi"])
        da, dg = la - la.mean(), lg - lg.mean()
        s = da + dg
        rows.append({"file": os.path.basename(f), "time": d["time"], "a": float(np.mean(d["chi"]) ** -0.5),
                     "n": d["n"], "corr": float(np.sum(da * dg) / np.sqrt(np.sum(da ** 2) * np.sum(dg ** 2))) if np.sum(da ** 2) > 0 else None,
                     "rms_ratio": float(np.sqrt(np.mean(s ** 2)) / np.sqrt(np.mean(da ** 2))) if np.sum(da ** 2) > 0 else None})
        print(run, rows[-1], flush=True)
    res[run] = rows
sel = [r for run in res for r in res[run] if r["corr"] is not None and 1.0 < r["a"] <= 121.5]
res["row125"] = {"n_dumps": len(sel), "largest_corr": max(r["corr"] for r in sel),
                 "rms_ratio_min": min(r["rms_ratio"] for r in sel), "rms_ratio_max": max(r["rms_ratio"] for r in sel),
                 "a_range": [min(r["a"] for r in sel), max(r["a"] for r in sel)]}
with open(os.path.join(OUT, "p3_slicing.json"), "w") as f:
    json.dump(res, f, indent=1)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle  # noqa: E402,F401

fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))
for run in ("dav_c256_n128_t", "dav_c256_n128_pcs4bt"):
    rr = [r for r in res[run] if r["corr"] is not None]
    ax[0].semilogx([r["a"] for r in rr], [1 + r["corr"] for r in rr], "o-", ms=3, label=run)
    ax[1].loglog([r["a"] for r in rr], [r["rms_ratio"] for r in rr], "o-", ms=3, label=run)
ax[0].set_xlabel("a"); ax[0].set_ylabel("1 + corr(d ln alpha, d ln gamma^(1/6))"); ax[0].set_yscale("log"); ax[0].legend(fontsize=7)
ax[1].set_xlabel("a"); ax[1].set_ylabel("rms d ln(alpha gamma^1/6) / rms d ln alpha"); ax[1].legend(fontsize=7)
ax[0].set_title("row 125: slicing of the three-wave runs", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "p3_slicing.png"), dpi=130)
print(json.dumps(res["row125"], indent=1))
