"""Resolution study of the collapse at amplitude 0.01: observer density contrast at the
overdensity, infall of the fiducial observers against the cell number, and the mean
relative Hamiltonian constraint."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "resolution.npz"))
ns = [int(n) for n in d["ns"]]
fs.use_style()
fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.95, wspace=0.42)
cols = {64: fs.PAL["blue"], 96: fs.PAL["green"], 128: fs.PAL["red"]}
for n in ns:
    c = cols[n]
    axs[0].loglog(d[f"gr_ap_{n}"], d[f"gr_do_{n}"], color=c, label=rf"$N_g = {n}$")
    if f"nw_ap_{n}" in d.files:
        axs[0].loglog(d[f"nw_ap_{n}"], d[f"nw_do_{n}"], color=c, ls="--", lw=0.8)
    axs[2].loglog(d[f"cs_a_{n}"][1:], d[f"cs_Hr_{n}"][1:], color=c)
axs[0].set_xlim(30.0, 150.0)
axs[0].set_ylim(3.0, 3e4)
axs[0].set_xlabel(r"$a_p$")
axs[0].set_ylabel(r"$\delta_{\rm obs}$ at the overdensity")
axs[0].legend(frameon=False, loc="lower right")
fs.no_minor_labels(axs[0], "x")
axs[0].set_xticks([30, 50, 100])
axs[0].set_xticklabels(["30", "50", "100"])
marks = ("o", "s", "^", "D")
labs = (r"$L/32$", r"$L/16$", r"$L/8$", r"$L/4$")
for k in range(4):
    g = np.array([d[f"a10_{n}"][k, 0] for n in ns])
    w = np.array([d[f"a10_{n}"][k, 1] for n in ns])
    axs[1].plot(ns, g/g[0], marker=marks[k], ms=3.5, color="k", lw=0.8, label=labs[k])
    ok = np.isfinite(w)
    axs[1].plot(np.array(ns)[ok], w[ok]/w[0], marker=marks[k], ms=3.5, color=fs.PAL["blue"],
                lw=0.8, ls="--", mfc="none")
axs[1].set_xlabel(r"cells per wavelength $N_g$")
axs[1].set_ylabel("infall, relative to 64 cells")
axs[1].yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.3f"))
axs[1].set_xticks(ns)
axs[1].legend(frameon=False, fontsize=7, loc="upper right", title="start", title_fontsize=7)
axs[2].set_xlabel(r"scale factor $a$")
axs[2].set_ylabel(r"mean of $H_r$")
savefig(fig, "fig_res")
