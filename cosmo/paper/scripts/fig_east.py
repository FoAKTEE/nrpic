"""Collapse at one wavelength: observer density contrast at the underdensity and at the
overdensity for the four amplitudes, relativistic run against the Newtonian reference."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "east.npz"))
fs.use_style()
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.15, top=0.96, wspace=0.24)
cols = [fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"], fs.PAL["red"]]
for c, dl in zip(cols, d["deltas"]):
    k = f"{dl:g}"
    axs[0].plot(d[f"gr_ap1_{k}"], -d[f"gr_do1_{k}"], color=c, label=rf"$\bar\delta = {k}$")
    axs[0].plot(d[f"nw_ap1_{k}"], -d[f"nw_do1_{k}"], color="k", ls="--", lw=0.6)
    axs[1].plot(d[f"gr_ap0_{k}"], d[f"gr_do0_{k}"], color=c)
    axs[1].plot(d[f"nw_ap0_{k}"], d[f"nw_do0_{k}"], color="k", ls="--", lw=0.6)
axs[0].set_xscale("log")
axs[0].set_ylim(0.0, 1.0)
axs[0].set_xlabel(r"$a_p$")
axs[0].set_ylabel(r"$-\delta_{\rm obs}$ at the underdensity")
axs[0].legend(frameon=False, loc="upper left")
axs[1].set_xscale("log")
axs[1].set_yscale("log")
axs[1].set_ylim(1e-2, 3e4)
axs[1].set_xlabel(r"$a_p$")
axs[1].set_ylabel(r"$\delta_{\rm obs}$ at the overdensity")
axs[1].plot([], [], color="0.4", label="general relativity")
axs[1].plot([], [], color="k", ls="--", lw=0.6, label="Newtonian")
axs[1].legend(frameon=False, loc="lower right")
savefig(fig, "fig_east")
