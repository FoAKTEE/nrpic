"""Relativistic delay of the infall against the amplitude, for the three cloud shapes,
with the values read from the figures of East, Wojtak & Pretorius."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "east.npz"))
deltas = d["deltas"]
fs.use_style()
fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.1))
fig.subplots_adjust(left=0.17, right=0.96, bottom=0.15, top=0.96)
shapes = (("v2", "linear cloud", fs.PAL["red"], "o"), ("tsc", "quadratic", fs.PAL["green"], "s"),
          ("pcs", "cubic", fs.PAL["blue"], "^"))
for tag, name, col, mk in shapes:
    y = []
    for dl in deltas:
        a = d[f"a10_{tag}_{dl:g}"]
        y.append(np.nanmean(a[:, 0]/a[:, 1]) - 1.0)
    ax.loglog(deltas, y, mk, color=col, ms=4, label=name)
xx = np.geomspace(0.002, 0.06, 20)
ax.loglog(xx, 5.2*xx, label=r"$5.2\,\bar\delta$", **fs.GUIDE)
# source paper: ratio of the scale factors at which the distance falls below a tenth
# (mean over its starting distances) and at which the density contrast reaches ten
paper_a10 = {0.0025: (1.068, 1.060, 1.043), 0.005: (1.065, 1.064, 1.057),
             0.01: (1.109, 1.106, 1.097, 1.101), 0.05: (1.485, 1.508)}
paper_d10 = {0.0025: 1.019, 0.005: 1.058, 0.01: 1.069, 0.05: 1.310}
ax.loglog(list(paper_a10), [np.mean(v) - 1.0 for v in paper_a10.values()], "x", color="k",
          ms=5, label="source paper, observers")
ax.loglog(list(paper_d10), [v - 1.0 for v in paper_d10.values()], "+", color="k", ms=6,
          label="source paper, density")
ax.set_xlabel(r"amplitude $\bar\delta$")
ax.set_ylabel("relativistic delay of the infall")
ax.legend(frameon=False, loc="upper left", fontsize=7)
savefig(fig, "fig_delay")
