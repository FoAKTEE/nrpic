"""Random field from a power spectrum over a thousandfold expansion (test C of Daverio,
Dirian & Mitsou), both boxes: cell means of the relative constraints against redshift
and the departure of the power spectrum from linear theory, with and without the
compensation of the cloud, and the values read from the figures of the source paper."""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import DATA, fs, savefig

d = np.load(os.path.join(DATA, "daverio_c.npz"))
fs.use_style()
ZP = (100.0, 10.0, 1.0, 0.02)
# values read from Figs. 9, 12 and 15 of the source paper
PAPER = {
    "c704": {"Hr": {32: (3.1e-7, 5.1e-7, 2.6e-6, 3.5e-6), 64: (9.1e-8, 8.9e-8, 9.8e-8, 1.2e-7),
                    128: (2.4e-8, 2.4e-8, 2.8e-8, 5.1e-8)},
             "Mr": {32: (1.8e-2, 1.27e-2, 9.1e-3, 7.8e-3), 64: (4.9e-3, 4.1e-3, 4.2e-3, 4.3e-3),
                    128: (1.2e-3, 1.1e-3, 1.4e-3, 2.2e-3)}},
    "c256": {"Hr": {64: (2.5e-7, 2.0e-7, 9.6e-7, 5.3e-6), 128: (4.5e-8, 4.3e-8, 3.9e-7, 4.8e-6)},
             "Mr": {64: (7.6e-3, 7.2e-3, 1.6e-2, 6.7e-2), 128: (2.0e-3, 2.8e-3, 7.1e-3, 4.2e-2)}},
}
PK = {64: {100: (9.3e-3, 6.8e-2, 0.13), 10: (1.5e-2, 0.17, 0.31)},
      128: {100: (3.3e-3, 1.8e-2, 3.5e-2), 10: (3.3e-3, 4.3e-2, 0.10)}}
KP = (0.0245, 0.1032, 0.1442)
COL = {32: fs.PAL["blue"], 64: fs.PAL["green"], 128: fs.PAL["red"]}


def have(tag):
    return f"{tag}_z" in d.files


def zz(tag):
    return np.maximum(d[f"{tag}_z"], 1.0e-2)[1:]


def constraints(axs, box, cells, comp, plain):
    for n in cells:
        c = COL[n]
        for name, ls, lw in ((comp, "-", 1.4), (plain, "--", 0.9)):
            tag = f"{box}_n{n}_{name[n]}" if isinstance(name, dict) else f"{box}_n{n}_{name}"
            if not have(tag):
                continue
            lab = rf"$N_g = {n}$" if ls == "-" else None
            axs[0].loglog(zz(tag), d[f"{tag}_Hr"][1:], color=c, ls=ls, lw=lw, label=lab)
            axs[1].loglog(zz(tag), d[f"{tag}_Mr"][1:], color=c, ls=ls, lw=lw)
        axs[0].plot(ZP, PAPER[box]["Hr"][n], "x", color=c, ms=5)
        axs[1].plot(ZP, PAPER[box]["Mr"][n], "x", color=c, ms=5)
    for ax, lab in zip(axs[:2], (r"mean of $H_r$", r"mean of $M_r$")):
        ax.set_xlabel(r"redshift $z$")
        ax.set_ylabel(lab)
        ax.set_xlim(1.2e3, 0.9e-2)
    axs[0].legend(frameon=False, loc="lower right", fontsize=7)


# larger box
fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
constraints(axs, "c704", (32, 64, 128), "pcs4bt", {32: "t", 64: "t", 128: "k"})
if have("c704_n32_k"):
    axs[0].loglog(zz("c704_n32_k"), d["c704_n32_k_Hr"][1:], color=COL[32], ls=":", lw=0.9)
if have("c704_n64_dcompt"):
    for ax, key in ((axs[0], "Hr"), (axs[1], "Mr")):
        ax.loglog(zz("c704_n64_dcompt"), d[f"c704_n64_dcompt_{key}"][1:], color=COL[64],
                  ls="-.", lw=0.9)
for n in (32, 64, 128):
    for name, ls, lw in (("pcs4bt", "-", 1.2), ("t" if n < 128 else "k", "--", 0.9)):
        tag = f"c704_n{n}_{name}"
        if f"{tag}_dev_z10" in d.files:
            axs[2].semilogy(d[f"{tag}_k"], d[f"{tag}_dev_z10"], color=COL[n], ls=ls, lw=lw,
                            marker="o", ms=2.5)
axs[2].set_xlabel(r"$k$ ($h$/Mpc)")
axs[2].set_ylabel(r"$|P/P_{\rm lin} - 1|$ at $z = 10$")
savefig(fig, "fig_daverio_c")

# smaller box
fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
constraints(axs, "c256", (64, 128), "pcs4bt", "t")
for n in (64, 128):
    for z, mk in ((100, "o"), (10, "s")):
        for name, ls, lw in (("pcs4bt", "-", 1.2), ("t", "--", 0.9)):
            tag = f"c256_n{n}_{name}"
            if f"{tag}_dev_z{z}" in d.files:
                axs[2].semilogy(d[f"{tag}_k"], d[f"{tag}_dev_z{z}"], color=COL[n], ls=ls, lw=lw,
                                marker=mk, ms=2.5, mfc="w" if z == 10 else None)
        axs[2].plot(KP, PK[n][z], "x" if z == 100 else "+", color=COL[n], ms=5)
axs[2].set_xlabel(r"$k$ ($h$/Mpc)")
axs[2].set_ylabel(r"$|P/P_{\rm lin} - 1|$")
savefig(fig, "fig_daverio_c256")
