#!/usr/bin/env python3
"""Second gate review of B G2: figure and judgement of W6 / RE5 from the Weyl statistics of the
four 128^3 members (weyl_splitx.json of the reviewer's rerun B-20261128-084129-a0a5947 of the
lead's population/scripts/weyl_gauge.py splitx).

Ratios of B_ij B^ij statistics are quadratic in the field; the figure shows their square roots
(amplitude-like), the JSON both.

    python3 review_fig_w6.py WEYL_JSON OUTDIR
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/data/haiyangw/nrpic/python")
from nrpic import figstyle as fs  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
tab = json.load(open(src))["table"]
STATS = {"B2_q50": "median", "I_B_void": "larger-lapse half", "I_B": "mean (cores)"}
res = {"source": src, "rows": []}
for e in tab:
    r = {"a": e["a"]}
    for s in STATS:
        for p in ("R1", "R8", "Pgd", "Pzs"):
            r[f"{p}_{s}"] = e[f"{p}_{s}"]
        d1, d8 = abs(e[f"R1_{s}"] - 1), abs(e[f"R8_{s}"] - 1)
        r[f"fall_{s}"] = d8/d1 if d1 > 0 else None          # |R8-1| / |R1-1|
    res["rows"].append(r)
# W6 of the lead (population/JOURNAL 2026-11-27 23:35) and the reviewer's RE5
late = {round(r["a"]): r for r in res["rows"]}
w6 = {}
for a in (100, 132):
    r = late[a]
    w6[a] = {s: r[f"fall_{s}"] for s in ("B2_q50", "I_B_void")}
res["W6_refuted"] = all(w6[132][s] >= 0.8 for s in w6[132])
res["W6_holds_half"] = all(w6[a][s] <= 0.5 for a in w6 for s in w6[a])
res["W6_fall"] = w6
res["RE5_holds"] = all(abs(late[a][f"R8_{s}"] - late[a][f"R1_{s}"]) <= 0.02
                       for a in (100, 132) for s in ("B2_q50", "I_B_void"))
json.dump(res, open(os.path.join(out, "review_w6.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402
a = np.array([r["a"] for r in res["rows"]])
fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.4))
fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.9, wspace=0.28)
col = {"B2_q50": fs.PAL["blue"], "I_B_void": fs.PAL["green"], "I_B": fs.PAL["orange"]}
ax = axs[0]
ax.axhline(1.0, color="k", lw=0.8)
for s, lab in STATS.items():
    ax.plot(a, np.sqrt([r[f"R1_{s}"] for r in res["rows"]]), "o-", color=col[s], label=f"{lab}, 1 per cell")
    ax.plot(a, np.sqrt([r[f"R8_{s}"] for r in res["rows"]]), "s--", color=col[s], mfc="none", label=f"{lab}, 8 per cell")
ax.set_xscale("log")
ax.set_xlabel(r"$a$")
ax.set_ylabel(r"$\sqrt{\mathrm{ratio}}$ of $B_{ij}B^{ij}$: Gamma driver / zero shift")
ax.set_title("(a) gauge ratio of the magnetic Weyl invariant", fontsize=9)
ax.legend(frameon=False, fontsize=6.5, loc="lower left", ncol=1)
ax = axs[1]
ax.axhline(1.0, color="k", lw=0.8)
for s, lab in STATS.items():
    ax.plot(a, np.sqrt([r[f"Pgd_{s}"] for r in res["rows"]]), "o-", color=col[s], label=f"{lab}, Gamma driver")
    ax.plot(a, np.sqrt([r[f"Pzs_{s}"] for r in res["rows"]]), "s--", color=col[s], mfc="none", label=f"{lab}, zero shift")
ax.set_xscale("log")
ax.set_xlabel(r"$a$")
ax.set_ylabel(r"$\sqrt{\mathrm{ratio}}$: 8 / 1 per cell")
ax.set_title("(b) particle number at fixed gauge", fontsize=9)
ax.legend(frameon=False, fontsize=6.5, loc="lower left")
fs.save(fig, os.path.join(out, "review_w6"))
