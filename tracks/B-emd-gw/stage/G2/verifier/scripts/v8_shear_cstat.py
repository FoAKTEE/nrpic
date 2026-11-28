#!/usr/bin/env python3
"""V7c: time means of the relative constraint norms of shearing-dust series 7 over
1 <= t <= t_A (trapezoid in t; also the plain mean of the records), from shear.cstat.hst and
t_A of rays.json, with a figure of the histories.

    python3 v8_shear_cstat.py OUTDIR DIR64 DIR128 DIR256
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402
import figstyle as fs  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
res = {}
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402
fig, axs = plt.subplots(1, 2, figsize=(8, 3.0))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.9, wspace=0.28)
for d, c in zip(sys.argv[2:], fs.series_colors(3)):
    h = vlib.read_hst(os.path.join(d, "shear.cstat.hst"))
    r = json.load(open(os.path.join(d, "rays.json")))
    tA = r["t_A"]
    m = (h["time"] >= 1.0) & (h["time"] <= tA)
    e = {"ny": r["ny"], "t_A": tA, "n_records": int(m.sum())}
    for col in ("Hr_mean", "Mr_mean"):
        t, q = h["time"][m], h[col][m]
        e[col + "_trapz"] = float(np.trapezoid(q, t)/(t[-1] - t[0]))
        e[col + "_plain"] = float(q.mean())
    res[str(r["ny"])] = e
    print(e)
    for ax, col in zip(axs, ("Hr_mean", "Mr_mean")):
        ax.semilogy(h["time"], h[col], color=c, label=rf"$N_y={r['ny']}$")
        ax.axvline(tA, color=c, ls=":", lw=1.0)
for ax, ttl in zip(axs, ("mean relative Hamiltonian", "mean relative momentum")):
    ax.axvspan(1.0, 4.12, color="grey", alpha=0.1)
    ax.set_xlabel(r"$t$")
    ax.set_title(ttl + " constraint, series 7", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
fs.save(fig, os.path.join(out, "v8_shear_cstat"))
ks = sorted(res, key=int)
for col in ("Hr_mean_trapz", "Mr_mean_trapz"):
    v = [res[k][col] for k in ks]
    res["ratios_" + col] = [v[0]/v[1], v[1]/v[2]]
json.dump(res, open(os.path.join(out, "v8_shear_cstat.json"), "w"), indent=1)
print({k: v for k, v in res.items() if k.startswith("ratios")})
