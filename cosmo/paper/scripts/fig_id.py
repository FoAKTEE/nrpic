"""Initial data: deposited density contrast and conformal factor along a mesh line
through the density peak, for particles at the cell centres and at the cell corners."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "id_profiles.npz"))
fs.use_style()
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.96, wspace=0.26)
x, s = d["x"], 1e4
for ax, name, lab in ((axs[0], "contrast", r"density contrast $\times 10^{4}$"),
                      (axs[1], "psi", r"$(\psi - 1) \times 10^{4}$")):
    ax.plot(x, s*d[f"centred_{name}"], color=fs.PAL["red"], marker="o", ms=2.5, lw=0.8,
            label="particles at cell centres")
    ax.plot(x, s*d[f"shifted_{name}"], color=fs.PAL["blue"], marker="o", ms=2.5, lw=0.8,
            label="particles at cell corners")
    ax.plot(x, s*d[f"target_{name}"], label="dictionary", **fs.GUIDE)
    ax.set_xlabel(r"$x H_0$")
    ax.set_ylabel(lab)
    ax.set_xlim(0.0, 4.0)
axs[0].legend(frameon=False, loc="upper right")
savefig(fig, "fig_id")
