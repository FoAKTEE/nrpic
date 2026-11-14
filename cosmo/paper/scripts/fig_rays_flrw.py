"""Light rays in the homogeneous universe: errors of the redshift and of the luminosity
distance along bundles emitted at two times, with the expected error of a pusher that
centres the metric in time."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "rays_flrw.npz"))
dt = float(d["dt"])
fs.use_style()
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.10, right=0.985, bottom=0.17, top=0.95, wspace=0.28)
cols = {0: fs.PAL["blue"], 1: fs.PAL["red"]}
seen = set()
for i in range(int(d["nbundle"])):
    if int(d[f"kind_{i}"]) != 0:
        continue                      # the two directions coincide
    t, te = d[f"t_{i}"], float(d[f"t_emit_{i}"])
    a, ae = (1.0 + 0.5*t)**2, (1.0 + 0.5*te)**2
    zex = a/ae - 1.0
    dex = 2.0*ae**1.5*(1.0 + zex)**2*(np.sqrt(1.0 + zex) - 1.0)
    c = cols[len(seen)]
    seen.add(i)
    axs[0].semilogy(zex, np.abs(d[f"z_{i}"]/zex - 1.0), color=c,
                    label=rf"emitted at $a = {ae:.0f}$")
    axs[1].semilogy(zex, np.abs(d[f"D_L_{i}"]/dex - 1.0), color=c)
    pred = (dt*dt/8.0)*(2.0/(1.0 + 0.5*te) - 2.0/(1.0 + 0.5*t))/(t - te)
    axs[1].semilogy(zex, pred, label="time-centred metric" if len(seen) == 1 else None,
                    **fs.GUIDE)
axs[0].set_xlabel(r"redshift $z$")
axs[0].set_ylabel("relative error of the redshift")
axs[0].set_ylim(1e-9, 1e-4)
axs[0].legend(frameon=False, loc="upper right")
axs[1].set_xlabel(r"redshift $z$")
axs[1].set_ylabel(r"relative error of $D_L$")
axs[1].set_ylim(1e-6, 1e-3)
axs[1].legend(frameon=False, loc="upper right")
savefig(fig, "fig_rays_flrw")
