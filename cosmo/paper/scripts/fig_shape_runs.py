"""Constraint violation through the collapse runs for the three cloud shapes: cell mean
of the relative Hamiltonian and momentum constraints against the scale factor."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "east.npz"))
fs.use_style()
fig, axs = plt.subplots(2, 4, figsize=(fs.FULL_WIDTH, 4.2), sharex="col", sharey="row")
fig.subplots_adjust(left=0.085, right=0.99, bottom=0.11, top=0.93, wspace=0.07, hspace=0.08)
shapes = (("v2", "linear", fs.PAL["red"]), ("tsc", "quadratic", fs.PAL["green"]),
          ("pcs", "cubic", fs.PAL["blue"]))
for k, dl in enumerate(d["deltas"]):
    key = f"{dl:g}"
    for tag, name, col in shapes:
        if f"cs_a_{tag}_{key}" not in d.files:
            continue
        a = d[f"cs_a_{tag}_{key}"]
        axs[0, k].loglog(a[1:], d[f"cs_Hr_{tag}_{key}"][1:], color=col, label=name)
        axs[1, k].loglog(a[1:], d[f"cs_Mr_{tag}_{key}"][1:], color=col)
    axs[0, k].set_title(rf"$\bar\delta = {key}$", fontsize=8)
    axs[1, k].set_xlabel(r"scale factor $a$")
axs[0, 0].set_ylabel(r"mean of $H_r$")
axs[1, 0].set_ylabel(r"mean of $M_r$")
axs[0, 0].set_ylim(5e-8, 5e-2)
axs[1, 0].set_ylim(5e-6, 0.5)
axs[1, 3].legend(*axs[0, 0].get_legend_handles_labels(), frameon=False, loc="lower right")
savefig(fig, "fig_shape_runs")
