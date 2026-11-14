"""Relativistic delay of the infall against the amplitude, for the three cloud shapes,
with the values read from the figures of East, Wojtak & Pretorius (left), and against the
depth of the initial potential for all wavelengths (right)."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "east.npz"))
deltas = d["deltas"]
fs.use_style()
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.15, top=0.96, wspace=0.24)
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
# right: all runs against the depth of the initial potential at the overdensity,
# |psi_N| = (3/2) (H/k)^2 x 3 delta, with (H/k)^2 = (L / (2 pi))^2 in initial Hubble radii
def depth(delta, Lbox):
    return 4.5*(Lbox/(2.0*np.pi))**2*delta


for tag, name, col, mk in shapes:
    x = [depth(dl, 4.0) for dl in deltas]
    y = [np.nanmean(d[f"a10_{tag}_{dl:g}"][:, 0]/d[f"a10_{tag}_{dl:g}"][:, 1]) - 1.0
         for dl in deltas]
    ax2.loglog(x, y, mk, color=col, ms=4)
for Lb, mk in ((2.0, "v"), (8.0, "D")):
    key = f"a10_tsc_L{Lb:g}"
    if key in d.files:
        a = d[key]
        ax2.loglog([depth(0.01, Lb)], [np.nanmean(a[:, 0]/a[:, 1]) - 1.0], mk, color="k",
                   ms=5, mfc="none", label=rf"wavelength {Lb:g} Hubble radii")
xx = np.geomspace(3e-3, 0.12, 20)
ax2.loglog(xx, 2.9*xx, label=r"$2.9\,|\psi_N|$", **fs.GUIDE)
ax2.set_xlabel(r"depth of the initial potential $|\psi_N|$")
ax2.set_ylabel("relativistic delay of the infall")
ax2.legend(frameon=False, loc="upper left", fontsize=7)
savefig(fig, "fig_delay")
