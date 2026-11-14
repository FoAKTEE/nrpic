"""Luminosity distance against redshift along light rays between the overdensity and the
underdensity: deviation from the homogeneous relation (left) and ratio of the
relativistic to the Newtonian result (right), for three amplitudes."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "rays.npz"))
amps = [a for a in (0.01, 0.005, 0.0025) if f"n_{a:g}" in d.files and int(d[f"n_{a:g}"]) > 0]
fs.use_style()
fig, axs = plt.subplots(len(amps), 2, figsize=(fs.FULL_WIDTH, 2.35*len(amps)), squeeze=False,
                        sharex=True)
fig.subplots_adjust(left=0.10, right=0.985, bottom=0.22/len(amps) + 0.03, top=0.98,
                    wspace=0.24, hspace=0.07)
cols = [fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"], fs.PAL["red"]]
ZMIN = 0.01
for r, a in enumerate(amps):
    ems = sorted({float(d[f"meta_{a:g}_{k}"][2]) for k in range(int(d[f"n_{a:g}"]))})
    for k in range(int(d[f"n_{a:g}"])):
        key = f"{a:g}_{k}"
        kind, ae, near = d[f"meta_{key}"]
        c = cols[ems.index(float(near)) % len(cols)]
        ls = "-" if kind == 0 else "--"
        z, y = d[f"z_{key}"], d[f"y_{key}"]
        zn, yn = d[f"zn_{key}"], d[f"yn_{key}"]
        axs[r, 0].plot(np.where(z >= ZMIN, z, np.nan), y, color=c, ls=ls, lw=1.2,
                       label=rf"$a_e \approx {near:.0f}$" if kind == 0 else None)
        axs[r, 0].plot(np.where(zn >= ZMIN, zn, np.nan), yn, color="k", ls=ls, lw=0.45)
        zc, df = d[f"zc_{key}"], d[f"diff_{key}"]
        axs[r, 1].plot(np.where(zc >= ZMIN, zc, np.nan), np.abs(df), color=c, ls=ls, lw=1.0)
    axs[r, 0].set_xscale("log")
    axs[r, 0].set_yscale("symlog", linthresh=1e-2)
    axs[r, 0].axhline(0.0, **fs.THIN)
    axs[r, 0].set_xlim(ZMIN, 10.0)
    axs[r, 0].set_ylabel(r"$D_L/D_{\rm FRW} - 1$")
    axs[r, 0].text(0.03, 0.56, rf"$\bar\delta = {a:g}$", transform=axs[r, 0].transAxes,
                   fontsize=8)
    axs[r, 1].set_xscale("log")
    axs[r, 1].set_yscale("log")
    axs[r, 1].set_ylim(1e-5, 1.0)
    axs[r, 1].set_ylabel(r"$|D_L^{\rm GR}/D_L^{\rm N} - 1|$")
    axs[r, 0].legend(frameon=False, fontsize=6, ncol=2, loc="upper right")
for ax in axs[-1]:
    ax.set_xlabel(r"redshift $z$")
savefig(fig, "fig_rays")
