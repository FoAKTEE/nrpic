"""Collapse at one wavelength: coordinate distance of fiducial observers from the
overdensity against their own proper-time scale factor; relativistic run upwards,
Newtonian reference mirrored downwards."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, L, fs, savefig

d = np.load(os.path.join(DATA, "east.npz"))
fs.use_style()
fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.6), sharey=True)
fig.subplots_adjust(left=0.075, right=0.99, bottom=0.18, top=0.90, wspace=0.07)
cols = fs.series_colors(4)
for ax, dl in zip(axs, d["deltas"]):
    k = f"{dl:g}"
    ag, dg = d[f"fid_gr_ap_{k}"], d[f"fid_gr_d_{k}"]/L
    an, dn = d[f"fid_nw_ap_{k}"], d[f"fid_nw_d_{k}"]/L
    for j in range(ag.shape[1]):
        ax.plot(ag[:, j], np.abs(dg[:, j]), color=cols[j], lw=0.9)
        ok = np.isfinite(an[:, j]) & np.isfinite(dn[:, j])
        ax.plot(an[ok, j], -np.abs(dn[ok, j]), color=cols[j], lw=0.9)
    ax.axhline(0.0, **fs.THIN)
    a10 = d[f"a10_v2_{k}"]
    lo = np.nanmin(a10)
    ax.set_xlim(0.45*lo, min(np.nanmax(ag), 1.9*lo))
    ax.set_title(rf"$\bar\delta = {k}$", fontsize=8)
    ax.set_xlabel(r"$a_p$")
axs[0].set_ylim(-0.27, 0.27)
axs[0].set_ylabel(r"distance / $L$")
axs[0].text(0.04, 0.93, "general relativity", transform=axs[0].transAxes, fontsize=7, va="top")
axs[0].text(0.04, 0.07, "Newtonian", transform=axs[0].transAxes, fontsize=7, va="bottom")
savefig(fig, "fig_east_fid")
