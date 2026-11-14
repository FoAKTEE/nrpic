"""Linear regime: observer density contrast at the overdensity and the underdensity for
the relativistic run, the Newtonian reference and linear theory."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig
from delta_obs import linear

d = np.load(os.path.join(DATA, "linear.npz"))
delta, n = float(d["delta"]), int(d["n"])
fs.use_style()
fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 4.6), sharex=True,
                        gridspec_kw={"height_ratios": [2.0, 1.0]})
fig.subplots_adjust(left=0.10, right=0.985, bottom=0.10, top=0.97, wspace=0.27, hspace=0.06)
names = ("overdensity", "underdensity")
for i, sign in ((0, 1.0), (1, -1.0)):
    ag, dg = d[f"gr_a_p_{i}"], d[f"gr_delta_obs_{i}"]
    an, dn = d[f"nw_a_p_{i}"], d[f"nw_delta_obs_{i}"]
    ax = axs[0, i]
    ax.loglog(ag, np.abs(dg), color=fs.PAL["red"], label="general relativity")
    ax.loglog(an, np.abs(dn), color=fs.PAL["blue"], ls="--", label="Newtonian")
    ax.loglog(ag, np.abs(linear(ag, delta, sign, n=n)), label="linear theory", **fs.GUIDE)
    ax.set_ylabel(r"$|\delta_{\rm obs}|$, " + names[i])
    ax.legend(frameon=False, loc="upper left")
    ax = axs[1, i]
    ax.semilogx(ag, 100.0*(dg/linear(ag, delta, sign, n=n) - 1.0), color=fs.PAL["red"])
    ax.semilogx(an, 100.0*(dn/linear(an, delta, sign, n=n) - 1.0), color=fs.PAL["blue"],
                ls="--")
    ax.axhline(0.0, **fs.THIN)
    ax.set_ylim(-2.0, 2.0)
    ax.set_ylabel("departure (percent)")
    ax.set_xlabel(r"$a_p$")
savefig(fig, "fig_linear")
