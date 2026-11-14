"""Initial conditions of Barrera-Hinojosa & Li (arXiv:2001.07968) without radiation:
growth rate of the particle-number contrast, ratio of the power of the particle-number
contrast to that of the synchronous density in the 4 Gpc/h box, and the error of the
finite-difference velocity. Numbers from cosmo/analysis/gramses_tests.json (written by
cosmo/analysis/gramses_tests.py); the values read from the figures of the source paper
are stored there too."""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import REPO, fs, savefig
import gramses_ic as gi
import gramses_tests as gt

d = json.load(open(os.path.join(REPO, "cosmo", "analysis", "gramses_tests.json")))
P = d["settings"]["params"]
fs.use_style()
fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.95, wspace=0.34)
cols = {99: fs.PAL["red"], 49: fs.PAL["blue"]}

# growth rate of the particle-number contrast
k = np.logspace(-4, -0.5, 300)
kf = np.array(gt.PAPER["fig1_k_f"])
for z in (99, 49):
    a = 1.0/(1.0 + z)
    axs[0].semilogx(k, gi.growth_rate_p(k, a, P), color=cols[z], label=rf"$z = {z}$")
    axs[0].plot(kf, d["fig1"][f"z{z}"]["paper_f_p"], "x", color=cols[z], ms=5)
axs[0].set_xlabel(r"$k$ ($h$/Mpc)")
axs[0].set_ylabel(r"growth rate $f_p$")
axs[0].legend(frameon=False, loc="upper left")

# power of the particle-number contrast over that of the synchronous density
k2 = np.logspace(np.log10(1.6e-3), np.log10(2.0e-2), 200)
for z in (99, 49):
    a = 1.0/(1.0 + z)
    r = d["ics"][f"L4000_z{z}"]["fig2"]
    axs[1].loglog(k2, gi.power_ratio_pS(k2, a, P), color=cols[z], lw=0.9)
    axs[1].plot(r["k"], r["measured"], "o", color=cols[z], ms=3.5)
    axs[1].plot(r["k"], r["paper_measured"], "x", color=cols[z], ms=5)
axs[1].set_xlabel(r"$k$ ($h$/Mpc)")
axs[1].set_ylabel(r"power ratio $P_p/P_S$")

# finite-difference velocity against the two-step velocity
dz = np.array([1.0, 0.5, 0.25, 0.05])
paper = {99: (2.0e-4, 5.0e-5, 1.1e-5), 49: (8.0e-4, 2.0e-4, 5.1e-5)}
dd = np.logspace(-1.5, 0.15, 50)
for z in (99, 49):
    t0 = d["ics"][f"L4000_z{z}"]["t0"]
    y = [t0[f"{v:g}"]["mean_double"] for v in dz]
    axs[2].loglog(dd, 2.0*dd**2/(1.0 + z)**2, color=cols[z], lw=0.9)
    axs[2].plot(dz, y, "o", color=cols[z], ms=3.5)
    axs[2].plot(dz[:3], paper[z], "x", color=cols[z], ms=5)
axs[2].set_xlabel(r"redshift offset $\Delta z$")
axs[2].set_ylabel(r"$\Delta P_{\theta\theta}/P_{\theta\theta}$")
savefig(fig, "fig_gramses")
