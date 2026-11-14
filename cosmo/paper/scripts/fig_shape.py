"""Sampling error of a compressed lattice against the compression, for three cloud
shapes and one or two particles per cell."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "shape_error.npz"))
c = d["c"]
fs.use_style()
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.93, wspace=0.06)
cols = {1: fs.PAL["red"], 2: fs.PAL["green"], 3: fs.PAL["blue"]}
names = {1: "linear", 2: "quadratic", 3: "cubic"}
for ax, npc in zip(axs, (1, 2)):
    for p in (1, 2, 3):
        ax.loglog(c, d[f"fil_p{p}_n{npc}"], color=cols[p], label=names[p])
    ax.loglog(c, 0.5*c, color="k", ls="--", lw=0.8)
    ax.loglog(c, 0.4*c**2, color="k", ls="--", lw=0.8)
    ax.loglog(c, 0.4*c**3, color="k", ls="--", lw=0.8)
    ax.set_xlabel(r"compression $c$")
    ax.set_title("one particle per cell" if npc == 1 else "two particles per cell",
                 fontsize=8)
    ax.set_ylim(1e-7, 1.0)
axs[0].set_ylabel("largest error of the deposited density")
axs[0].legend(frameon=False, loc="lower right")
axs[0].text(0.012, 1.2e-2, r"$c/2$", fontsize=7)
axs[0].text(0.012, 1.3e-4, r"$0.4\,c^2$", fontsize=7)
axs[0].text(0.012, 1.4e-6, r"$0.4\,c^3$", fontsize=7)
savefig(fig, "fig_shape")
