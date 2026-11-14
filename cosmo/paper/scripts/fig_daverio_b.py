"""Plane-wave linear mode over a thousandfold expansion: the potential at the start and
at the end, the departure of the density contrast from linear theory, and the largest
relative Hamiltonian constraint, with the values read from the figures of Daverio,
Dirian & Mitsou."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "daverio.npz"))
fs.use_style()
fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
cols = {"n32": fs.PAL["blue"], "n64": fs.PAL["red"]}
p_dd = {"n32": (2.5e-3, 1.81e-2, 2.89e-2, 3.57e-2), "n64": (6.2e-4, 4.55e-3, 7.3e-3, 9.10e-3)}
p_hr = {"n32": 4.6e-9, "n64": 2.3e-8}
tp = (100.0, 1000.0, 3000.0, 5806.0)
for tag, lab in (("n32", r"$N_g = 32$"), ("n64", r"$N_g = 64$")):
    c = cols[tag]
    x = d[f"b_{tag}_x"]
    x = x/(x[-1] + x[0])
    axs[0].plot(x, 1e9*d[f"b_{tag}_phi0"], color=c, ls=":", lw=0.9)
    axs[0].plot(x, 1e9*d[f"b_{tag}_phi1"], color=c, label=lab)
    axs[1].semilogy(d[f"b_{tag}_t"][1:], d[f"b_{tag}_dd0"][1:], color=c)
    axs[1].plot(tp, p_dd[tag], "x", color=c, ms=5)
    axs[2].semilogy(d[f"b_{tag}_ct"][1:], d[f"b_{tag}_Hr"][1:], color=c)
    axs[2].plot([5806.0], [p_hr[tag]], "x", color=c, ms=5)
# production configuration (cubic cloud, compensation, spline interpolation, step limit)
for tag, base in (("n32_pcs4b_f2", "n32"), ("n64_pcs4b", "n64")):
    if f"b_{tag}_t" in d.files:
        axs[1].semilogy(d[f"b_{tag}_t"][1:], d[f"b_{tag}_dd0"][1:], color=cols[base], lw=2.0)
        axs[2].semilogy(d[f"b_{tag}_ct"][1:], d[f"b_{tag}_Hr"][1:], color=cols[base], lw=2.0)
if "b_n32_c01_ct" in d.files:
    axs[2].semilogy(d["b_n32_c01_ct"][1:], d["b_n32_c01_Hr"][1:], color=cols["n32"], ls="--",
                    lw=0.9)
axs[0].set_xlabel(r"$x/L$")
axs[0].set_ylabel(r"potential $\phi \times 10^{9}$")
axs[0].legend(frameon=False, loc="upper left")
for ax in axs[1:]:
    ax.set_xlabel(r"conformal time (Mpc/$h$)")
    ax.set_xlim(-150.0, 6100.0)
axs[1].set_ylabel("departure of the density contrast")
axs[2].set_ylabel(r"largest $H_r$")
savefig(fig, "fig_daverio_b")
