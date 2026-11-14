"""Homogeneous universe over a thousandfold expansion: errors of the conformal factor
for exact data, and the largest constraint violations with white noise on every field,
with the values read from the figures of Daverio, Dirian & Mitsou."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "daverio.npz"))
fs.use_style()
fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
cols = {8: fs.PAL["blue"], 16: fs.PAL["green"], 32: fs.PAL["red"]}
# source paper (read from its figures): error of chi at the end, exact data; H and |M|
# with noise at three times
p_chi = {8: 2.55e-9, 16: 1.59e-10, 32: 9.8e-12}
p_H = {500.0: (7.4e-7, 3.7e-7, 1.3e-7), 1000.0: (4.7e-8, 1.7e-8, 5.9e-9),
       5806.0: (4.1e-12, 1.6e-12, 6.8e-13)}
p_M = {500.0: (1.9e-7, 1.2e-7, 5.6e-8), 1000.0: (1.4e-8, 6.6e-9, 2.7e-9),
       5806.0: (2.3e-12, 8.0e-13, 3.6e-13)}
for j, n in enumerate((8, 16, 32)):
    c = cols[n]
    axs[0].semilogy(d[f"a0_{n}_t"][1:], d[f"a0_{n}_dchi"][1:], color=c, ls="--", lw=0.9)
    if f"a0k_{n}_t" in d.files:
        axs[0].semilogy(d[f"a0k_{n}_t"][1:], d[f"a0k_{n}_dchi"][1:], color=c,
                        label=rf"$N_g = {n}$")
    axs[0].plot([5806.0], [p_chi[n]], "x", color=c, ms=5)
    axs[1].semilogy(d[f"a_{n}_t"][1:], d[f"a_{n}_H"][1:], color=c, label=rf"$N_g = {n}$")
    axs[2].semilogy(d[f"a_{n}_t"][1:], d[f"a_{n}_M"][1:], color=c)
    for t in p_H:
        axs[1].plot([t], [p_H[t][j]], "x", color=c, ms=5)
        axs[2].plot([t], [p_M[t][j]], "x", color=c, ms=5)
for ax in axs:
    ax.set_xlabel(r"conformal time (Mpc/$h$)")
    ax.set_xlim(-150.0, 6100.0)
axs[0].set_ylabel(r"error of $\chi$, exact data")
axs[1].set_ylabel(r"largest $H$, noise")
axs[2].set_ylabel(r"largest $|M|$, noise")
axs[1].legend(frameon=False, loc="upper right")
savefig(fig, "fig_daverio_a")
