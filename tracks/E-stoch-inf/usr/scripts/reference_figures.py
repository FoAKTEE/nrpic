#!/usr/bin/env python3
"""Figures of the USR reference (usr_reference.py output).

    python3 reference_figures.py --res DIR --out FIGDIR
"""
import argparse
import json
import os

import numpy as np

import figstyle as fs

SPEC_POINTS = dict(usr=(2.53, 6.55), eps1_min=(8.33, 9.7e-13), eps2_late=-2.76e-2)  # SPEC 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    r = json.load(open(os.path.join(a.res, "usr_reference.json")))
    d = np.load(os.path.join(a.res, "usr_reference.npz"))
    cn = d["bg_N"] - r["dn_star"]
    usr = r["usr_cN"]

    # ---------------------------------------------------------------- background
    fig, ax = plt.subplots(4, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 8.0), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.96, top=0.98, bottom=0.07, hspace=0.08)
    for x in ax:
        x.axvspan(usr[0], usr[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
    ax[0].semilogy(cn, d["bg_eps1"], color=fs.PAL["blue"], label="Friedmann (this package)")
    ax[0].plot(*SPEC_POINTS["eps1_min"], "o", mfc="none", color=fs.PAL["red"],
               label="SPEC 6 (eps1 min)")
    ax[0].set_ylabel(r"$\varepsilon_1$")
    ax[0].legend(loc="lower left")
    ax[1].plot(cn, d["bg_eps2"], color=fs.PAL["blue"])
    ax[1].axhline(3.0, **fs.MASK_LINE)
    for x0 in SPEC_POINTS["usr"]:
        ax[1].plot(x0, 3.0, "o", mfc="none", color=fs.PAL["red"])
    ax[1].set_ylabel(r"$\varepsilon_2=-d\ln\varepsilon_1/dN$")
    ax[2].plot(cn, d["bg_phi"], color=fs.PAL["blue"])
    ax[2].axhline(-np.sqrt(2.0) * r["vev"], **fs.GUIDE, label=r"$-\sqrt{2}v$ (inflection point)")
    ax[2].set_ylabel(r"$\phi/M_{\rm Pl}$")
    ax[2].legend(loc="upper right")
    ax[3].semilogy(cn, np.abs(d["bg_Pi"]), color=fs.PAL["blue"], label=r"$\Pi$ (code units)")
    ax[3].semilogy(cn, d["bg_H"], color=fs.PAL["green"], label=r"$H/H_*$")
    ax[3].set_ylabel("code units")
    ax[3].set_xlabel(r"$N-N_*$")
    ax[3].legend(loc="lower left")
    for lm in r["landmarks"]:
        for x in ax:
            x.axvline(lm["cN"], **fs.THIN, alpha=0.25)
    fs.save(fig, os.path.join(a.out, "fig_usr_background"))
    plt.close(fig)

    # ---------------------------------------------------------------- twin of a run
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 3.2))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.90, bottom=0.15)
    t = d["tw_t"]
    tw = r["T2_rk4_2s"]
    ax.semilogy(t[1:], d["tw_rel_Pi"][1:], color=fs.PAL["red"], label=r"$\Pi$")
    ax.semilogy(t[1:], d["tw_rel_phi"][1:], color=fs.PAL["red"], ls="--", label=r"$\phi$")
    ax.semilogy(t[1:], d["tw_rel_K"][1:], color=fs.PAL["red"], ls=":", label=r"$K$")
    ax.axhline(1e-3, **fs.GUIDE, label="A1 (USR), SCOPE 4")
    tb = np.array([lm["t"] for lm in r["landmarks"] if "USR" in lm["label"]])
    for x0 in tb:
        ax.axvline(x0, **fs.MASK_LINE)
    ax.set_xlabel(r"$t$ (code units, $1/H_*$)")
    ax.set_ylabel("relative error of RK4()4[2S]")
    ax.set_title(r"homogeneous twin, $\Delta t=0.0491$ ($N=32$, Courant 0.25)", fontsize=10)
    ax.legend(loc="center right", ncol=2)
    fs.save(fig, os.path.join(a.out, "fig_usr_twin"))
    plt.close(fig)

    # ---------------------------------------------------------------- spectrum
    k = d["k_code"]
    nout = d["n_out"] - r["dn_star"]
    dm, dfl, win = d["delta_ms"], d["delta_fl"], d["win"]
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.14, wspace=0.27)
    times = [0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0]
    cols = fs.series_colors(len(times))
    for c, tt in zip(cols, times):
        i = int(np.argmin(np.abs(nout - tt)))
        ax[0].loglog(k, win[:, i]**2 * dm[:, i], color=c, label=f"N-N* = {tt:g}")
    ax[0].loglog(k, dfl[:, -1], color="k", ls=":", label="FLRW lattice at N_f")
    ax[0].loglog(k, d["delta_sr"], **fs.GUIDE, label=r"$H^2/(8\pi^2\varepsilon_1)$ at $k=aH$")
    ax[0].set_xlabel(r"$k/dk=|n|$")
    ax[0].set_ylabel(r"$W^2\Delta_{\cal R}(k)$")
    ax[0].set_ylim(1e-14, 10)
    ax[0].legend(loc="lower right", ncol=2, fontsize=8)
    ax[1].loglog(k, dm[:, -1] / d["delta_sr"], color=fs.PAL["blue"],
                 label=r"enhancement $\Delta(N_f)/\Delta_{\rm SR}(k=aH)$")
    ax2 = ax[1].twinx()
    ax2.semilogx(k, dfl[:, -1] / dm[:, -1], color=fs.PAL["red"], label="FLRW / full MS at N_f")
    ax2.axhline(1.1, **fs.GUIDE)
    ax2.set_ylabel("FLRW / full MS", color=fs.PAL["red"])
    ax[1].set_xlabel(r"$k/dk$")
    ax[1].set_ylabel("enhancement", color=fs.PAL["blue"])
    h1, l1 = ax[1].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax[1].legend(h1 + h2, l1 + l2, loc="center right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_usr_spectrum"))
    plt.close(fig)

    # ---------------------------------------------------------------- modes in time
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.8))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.96, bottom=0.13)
    ax.axvspan(usr[0], usr[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
    pick = [1, 2, 3, 4, 8, 16, 32, 64]
    cols = fs.series_colors(len(pick))
    for c, p in zip(cols, pick):
        i = int(np.argmin(np.abs(k - p)))
        if abs(k[i] - p) > 1e-9:
            continue
        ax.semilogy(nout, dm[i], color=c, label=f"k = {p} dk")
        ax.semilogy(nout, win[i]**2 * dm[i], color=c, ls="--", lw=1.0)
        if p <= 4:
            ax.semilogy(nout, dfl[i], color=c, ls=":", lw=1.0)
    ax.set_xlabel(r"$N-N_*$")
    ax.set_ylim(1e-14, 10)
    ax.set_ylabel(r"$\Delta_{\cal R}$ (solid), $W^2\Delta_{\cal R}$ (dashed), FLRW (dotted)")
    ax.legend(loc="lower right", ncol=2, fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_usr_modes"))
    plt.close(fig)

    # ---------------------------------------------------------------- lattice rms
    lv = r["lattice_variance"]
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 3.2))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.95, bottom=0.15)
    ax.axvspan(usr[0], usr[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
    keys = [x for x in lv if x != "cN"]
    cols = fs.series_colors(len(keys))
    for c, key in zip(cols, keys):
        ax.semilogy(lv["cN"], np.sqrt(lv[key]["var_cg"]), color=c, label=key.replace("_", ", "))
    ax.set_xlabel(r"$N-N_*$")
    ax.set_ylabel(r"rms of $W{\cal R}$ on the lattice")
    ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_usr_rms"))
    plt.close(fig)


if __name__ == "__main__":
    main()
