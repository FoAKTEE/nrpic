#!/usr/bin/env python3
"""Figure and run-to-run ratios from results_cosmo.json of cosmo_demo.py.

    RUN_DIR=<out> python3 scripts/cosmo_demo_plot.py <results_cosmo.json>
"""
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

R = json.load(open(sys.argv[1]))
OUT = os.environ.get("RUN_DIR", os.path.join(HERE, "..", "figs"))
FIGS = os.path.join(HERE, "..", "figs")
fs.use_style()
C = fs.PAL
names = [k for k in R if k.startswith("dav")]
cols = {names[0]: C["red"], names[1]: C["blue"]}
lab = {names[0]: "quadratic cloud", names[1]: "cubic cloud + compensation"}

# shell ratios between the runs at common a
out = {}
s0 = {round(s["a"], 1): s for s in R[names[0]]["spectra"]}
s1 = {round(s["a"], 1): s for s in R[names[1]]["spectra"]}
L = R[names[0]]["box"][0]
for a in sorted(set(s0) & set(s1)):
    if a < 2:
        continue
    k = np.array(s0[a]["k"]) * L / (2 * np.pi)
    y0 = np.array(s0[a]["drho_dlnk/rho_bar"])
    y1 = np.array(s1[a]["drho_dlnk/rho_bar"])
    band = {"k<=6": (k >= 0.5) & (k <= 6.5), "10<=k<=60": (k >= 9.5) & (k <= 60.5)}
    out[str(a)] = {b: float(y1[m].sum() / y0[m].sum()) for b, m in band.items()}
with open(os.path.join(OUT, "cosmo_ratios.json"), "w") as f:
    json.dump({"ratio cubic/quadratic of rho_GW in the band": out}, f, indent=1)
print(json.dumps(out, indent=1))

fig = plt.figure(figsize=(8.0, 3.5))
axs = [fs.inch_axes(fig, 0.62 + 2.6 * i, 0.5, 1.95, 2.4) for i in range(3)]
for n in names:
    r = R[n]["rows"][1:]
    a = np.array([x["a"] for x in r])
    axs[0].loglog(a, [x["rms_hTT"] for x in r], "o-", ms=3, color=cols[n], label=r"$h^{\rm TT}$")
    axs[0].loglog(a, [x["rms_h_nonTT"] for x in r], "s--", ms=3, mfc="none", color=cols[n],
                  label=r"non-TT part")
    axs[1].loglog(a, [x["rho_kin/rho_bar"] for x in r], "o-", ms=3, color=cols[n],
                  label=r"$\rho_{\rm kin}$")
    axs[1].loglog(a, [x["rho_grad/rho_bar"] for x in r], "s--", ms=3, mfc="none", color=cols[n],
                  label=r"$\rho_{\rm grad}$")
    sp = {round(s["a"], 1): s for s in R[n]["spectra"]}
    for a_sel, ls in ((12.3, "-"), (342.3, "--"), (1001.0, ":")):
        s = sp.get(a_sel) or min(sp.values(), key=lambda q: abs(q["a"] - a_sel))
        k = np.array(s["k"]) * L / (2 * np.pi)
        y = np.array(s["drho_dlnk/rho_bar"])
        m = (y > 0) & (k >= 0.5)
        axs[2].loglog(k[m], y[m], color=cols[n], ls=ls, lw=1.2,
                      label=f"a = {s['a']:.0f}" if n == names[0] else None)
axs[0].set_title(r"rms of $\tilde\gamma_{ij}-\delta_{ij}$", fontsize=9)
axs[0].set_xlabel(r"$a$", labelpad=-2)
axs[0].legend(loc="center right", fontsize=7)
axs[1].set_title(r"$\rho/\bar\rho$ of the TT part", fontsize=9)
axs[1].set_xlabel(r"$a$", labelpad=-2)
axs[1].legend(loc="upper left", fontsize=7)
axs[2].set_title(r"$(d\rho_{\rm GW}/d\ln k)/\bar\rho$", fontsize=9)
axs[2].set_xlabel(r"$|k|L/2\pi$", labelpad=-2)
axs[2].set_ylim(1e-30, 1e-8)
axs[2].legend(loc="lower left", fontsize=7)
fig.text(0.5, 0.97, f"red: {lab[names[0]]}    blue: {lab[names[1]]}   (128$^3$, 1 particle per cell)",
         ha="center", va="top", fontsize=8)
files = fs.save(fig, os.path.join(OUT, "cosmo_tt"))
shutil.copy(files[1], os.path.join(FIGS, "cosmo_tt.png"))
