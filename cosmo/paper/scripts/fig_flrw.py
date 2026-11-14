"""Homogeneous universe: errors of the lapse, the density and the observer proper time against the exact matter-dominated solution, for the two couplings."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, H0, L, RHO0, fs, savefig, scale_factor

d = np.load(os.path.join(DATA, "flrw.npz"))
fs.use_style()
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.96, wspace=0.26)
quant = (("alpha_probe", lambda a: a, "lapse", fs.PAL["blue"]),
         ("E_probe", lambda a: RHO0/a**3, "density", fs.PAL["red"]),
         ("tau_probe", lambda a: (2.0/(3.0*H0))*(a**1.5 - 1.0), "proper time",
          fs.PAL["orange"]))
for key, ls in (("frozen", "--"), ("density", "-")):
    t = d[f"{key}_time"]
    a = scale_factor(t)
    for name, exact, label, col in quant:
        y = d[f"{key}_{name}"]
        ex = exact(a)
        ok = ex != 0.0
        axs[0].semilogy(a[ok], np.abs(y[ok]/ex[ok] - 1.0), color=col, ls=ls,
                        label=label if key == "density" else None)
    az = scale_factor(d[f"{key}_zt"])
    # root mean square of the Hamiltonian constraint over the box, in units of its
    # largest term 16 pi rho of the exact solution
    rel = d[f"{key}_Hnorm"]/np.sqrt(L**3)/(16.0*np.pi*RHO0/az**3)
    axs[1].semilogy(az, np.maximum(rel, 1e-16), color="k", ls=ls,
                    label="densities converted per stage" if key == "density"
                    else "sources held fixed")
axs[0].set_ylim(1e-11, 1.0)
axs[0].set_xlabel(r"scale factor $a$")
axs[0].set_ylabel("relative error")
axs[0].legend(frameon=False, ncol=3, loc="lower center", handlelength=1.4, columnspacing=1.2)
axs[1].set_ylim(1e-12, 10.0)
axs[1].set_xlabel(r"scale factor $a$")
axs[1].set_ylabel("constraint / largest term")
axs[1].legend(frameon=False, loc="lower right")
savefig(fig, "fig_flrw")
