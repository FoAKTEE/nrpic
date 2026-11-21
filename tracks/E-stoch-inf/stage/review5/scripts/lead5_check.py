#!/usr/bin/env python3
"""Lead's own-code check of a4res (batch 5): largest odd/even ratio of H and |M| over the dumps.

Reads the raw dumps of card run E-20261121-131000-b23055b with the verifier's reader
(g1verify/scripts/nrsf.py, not a4res's code). For each set-up X: odd = (C(X_p) - C(X_m))/2,
even = (C(X_p) + C(X_m))/2 for C = H and M = (Mx, My, Mz), box means removed, rms over the box;
pairs only at equal recorded times (|dt| <= 1e-9); the ratio odd/even at every dump; the
largest over the dumps with t > 0. Writes <out>/lead5_check.json and a figure.

    lead5_check.py <job dir> <out dir> SETUP [SETUP ...]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "g1verify", "scripts"))
import nrsf  # noqa: E402

job, out, setups = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(out, exist_ok=True)


def rms0(x):
    x = x - x.mean()
    return float(np.sqrt(np.mean(x * x)))


res = {}
for su in setups:
    fp = nrsf.dumps(os.path.join(job, su + "_p"))
    fm = nrsf.dumps(os.path.join(job, su + "_m"))
    rows = []
    for a, b in zip(fp, fm):
        ha, hb = nrsf.header(a), nrsf.header(b)
        if abs(ha["time"] - hb["time"]) > 1e-9:
            continue
        A = nrsf.read(a, ["H", "Mx", "My", "Mz"], h=ha)
        B = nrsf.read(b, ["H", "Mx", "My", "Mz"], h=hb)
        oH, eH = rms0(0.5 * (A["H"] - B["H"])), rms0(0.5 * (A["H"] + B["H"]))
        oM = float(np.sqrt(sum(rms0(0.5 * (A[c] - B[c])) ** 2 for c in ("Mx", "My", "Mz"))))
        eM = float(np.sqrt(sum(rms0(0.5 * (A[c] + B[c])) ** 2 for c in ("Mx", "My", "Mz"))))
        rows.append([ha["time"], oH, eH, oM, eM])
    r = np.array(rows)
    late = r[:, 0] > 0
    res[su] = {"dumps": int(len(r)), "max_ratio_H": float(np.max(r[late, 1] / r[late, 2])),
               "max_ratio_M": float(np.max(r[late, 3] / r[late, 4])),
               "t_max_H": float(r[late, 0][np.argmax(r[late, 1] / r[late, 2])]), "rows": r.tolist()}
    print(f"{su}: {len(r)} dumps; largest odd/even H {res[su]['max_ratio_H']:.4g} at t = "
          f"{res[su]['t_max_H']:.3f}; M {res[su]['max_ratio_M']:.4g}")
json.dump(res, open(os.path.join(out, "lead5_check.json"), "w"), indent=1)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
sys.path.insert(0, HERE)
try:
    import figstyle  # noqa: E402
    figstyle.use_style()
except Exception:  # style is cosmetic; the numbers are in the JSON
    pass
fig, ax = plt.subplots(figsize=(6.4, 4.0))
for su in setups:
    r = np.array(res[su]["rows"])
    ax.semilogy(r[:, 0], r[:, 1] / r[:, 2], label=f"{su} H")
    ax.semilogy(r[:, 0], r[:, 3] / r[:, 4], "--", label=f"{su} |M|")
ax.axhline(1.0, color="0.6", lw=1)
ax.set_xlabel("t")
ax.set_ylabel("odd/even (lead's reader)")
ax.legend(fontsize=7, ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(out, "fig_lead5_ratio.png"), dpi=150)
