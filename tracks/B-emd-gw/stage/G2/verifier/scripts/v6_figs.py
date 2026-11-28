#!/usr/bin/env python3
"""Figures of V1 (waves) and V4 (halos) from the JSON of their registered runs, with the
claimed numbers of the ledger (note Table V; note section VI, Tables VII-VIII) overlaid.

    python3 v6_figs.py OUTDIR V1_JSON V5_JSON
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

out, f1, f5 = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

# claims (ledger Table V)
CF = {"N": [16, 32, 48, 64], "amp": [-0.000141, -1.72e-6, -1.57e-7, -3.1e-8], "ph": [0.000253, 1.22e-5, 2.27e-6, 7.07e-7]}
CX = {"N": [16, 32, 48, 64], "amp": [-7.05e-5, 1.32e-6, 4.25e-7, 1.4e-7], "ph": [8.3e-5, 3.06e-6, 5.88e-7, 2.76e-7]}
w = json.load(open(f1))
fig, axs = plt.subplots(1, 3, figsize=(8, 2.9))
fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.88, wspace=0.35)
F = sorted(w["F"], key=lambda r: r["N"])
X = sorted(w["X"], key=lambda r: r["N"])
ax = axs[0]
ax.loglog([r["N"] for r in F], [abs(r["last"]["amp_err"]) for r in F], "o", color=fs.PAL["red"], label="amplitude, mine")
ax.loglog([r["N"] for r in F], [abs(r["last"]["phase_err"]) for r in F], "s", color=fs.PAL["red"], mfc="none", label="phase, mine")
ax.loglog(CF["N"], np.abs(CF["amp"]), "x", color="k", ms=8, label="claimed")
ax.loglog(CF["N"], np.abs(CF["ph"]), "+", color="k", ms=9)
ax.set_xlabel("cells per side")
ax.set_ylabel("|error| at the last dump")
ax.set_title("F: flat, k = 2 pi (1,1,1)", fontsize=10)
ax.legend(frameon=False, fontsize=7)
ax = axs[1]
for pol, c in (("cross", fs.PAL["red"]), ("plus", fs.PAL["yellow"])):
    ax.loglog([r["N"] for r in X], [abs(r["last"][pol + "_amp_err"]) for r in X], "o", color=c, label=f"{pol}: amplitude")
    ax.loglog([r["N"] for r in X], [abs(r["last"][pol + "_phase_err"]) for r in X], "s", color=c, mfc="none", label=f"{pol}: phase")
ax.loglog(CX["N"], np.abs(CX["amp"]), "x", color="k", ms=8, label="claimed (cross)")
ax.loglog(CX["N"], np.abs(CX["ph"]), "+", color="k", ms=9)
ax.set_xlabel("cells per side")
ax.set_title("X: matter era, t = 10 (a = 36)", fontsize=10)
ax.legend(frameon=False, fontsize=7)
ax = axs[2]
cols = fs.series_colors(len(X))
for c, r in zip(cols, X):
    t = [x["t"] for x in r["rows"]]
    ax.semilogy(t, [abs(x["cross_amp_err"]) + 1e-16 for x in r["rows"]], color=c, label=f"N = {r['N']}")
ax.set_xlabel("t")
ax.set_ylabel("|amplitude error|, cross")
ax.set_title("X against time", fontsize=10)
ax.legend(frameon=False, fontsize=7)
fs.save(fig, os.path.join(out, "v1_waves"))

h = json.load(open(f5))
cat, cmpd = h["catalogues"], h["compare"]
fig, axs = plt.subplots(1, 2, figsize=(8, 3.1))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.88, wspace=0.3)
ax = axs[0]
for k, c, mk in (("zs128_a121_vs_newton_a121", fs.PAL["red"], "o"), ("gd128_a121_vs_newton_a121", fs.PAL["blue"], "s")):
    rr = [p["ratio"] for p in cmpd[k]["pairs"] if p["ratio"] is not None]
    ax.plot(range(1, len(rr) + 1), rr, mk + "-", color=c, label=("zero shift" if "zs" in k else "Gamma driver")
            + f": median |r-1| = {cmpd[k]['median_abs_dev']:.4f}")
ax.axhline(1.0, color="k", lw=1.0)
ax.axhspan(0.95, 1.05, color="grey", alpha=0.15)
ax.set_xlabel("rank of the Newtonian halo")
ax.set_ylabel(r"$M_{\rm GR}/M_{\rm N}$ (partner within 0.1)")
ax.set_title(r"$128^3$, $a = 121$, equal masses", fontsize=10)
ax.legend(frameon=False, fontsize=7, loc="lower right")
ax = axs[1]
names = ["newton_a64", "gd128_a64", "gd256_a64", "newton_a121", "zs128_a121", "gd128_a121", "gd256_a121"]
x = np.arange(len(names))
ax.bar(x - 0.2, [cat[n]["n_common"] for n in names], 0.4, color=fs.PAL["blue"], label=r"$M \geq 100\,m_N$ (mine)")
ax.bar(x + 0.2, [cat[n]["n_halos_100"]/10 for n in names], 0.4, color=fs.PAL["yellow"], label=r"$\geq 100$ particles / 10 (mine)")
ax.set_xticks(x)
ax.set_xticklabels([n.replace("_a", "\na=") for n in names], fontsize=7)
ax.set_ylabel("halo count")
ax.set_title("catalogues, both epochs", fontsize=10)
ax.legend(frameon=False, fontsize=7)
fs.save(fig, os.path.join(out, "v5_halos"))
print("written")
