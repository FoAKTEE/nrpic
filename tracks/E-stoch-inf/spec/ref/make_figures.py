#!/usr/bin/env python3
"""Figures and the drift check (test T2d) of E-pre-1 from the outputs of ms_reference.py and
norm_test.py.

Usage: python3 make_figures.py --ms MS_RUN_DIR --norm NORM_RUN_DIR --out DIR
Writes fig_background.png, fig_freezing.png, fig_spectra.png, fig_drift.png, fig_norm.png
and checks.json into DIR.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

# Values read by eye off Fig. 1 of arXiv:2512.14649 (files 64quad_back__MeanRolls.pdf and
# 64usr_back__MeanRolls.pdf of the source); precision of the reading about 2 percent of
# the axis range. V is in the units Mpl = 100 of that figure.
READ = {
    "quadratic": {"V": [(0.0, 2.68e-2), (7.6, 2.22e-2)],
                  "eps1": [(0.0, 1.11e-2), (7.6, 1.33e-2)],
                  "eps2": [(0.0, -2.23e-2), (7.6, -2.62e-2)]},
    "inflection": {"V": [(0.0, 2.615e-2), (9.6, 2.385e-2)],
                   "eps1": [(0.0, 1.32e-2), (1.65, 2.41e-2)],
                   "eps2": [(0.0, -0.42), (2.5, 3.2), (4.5, 5.9), (6.45, 3.2)]},
}


def load(msdir, name):
    d = np.load(os.path.join(msdir, name + ".npz"))
    r = json.load(open(os.path.join(msdir, name + ".json")))
    return d, r


def fig_background(msdir, out):
    fig, axs = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 6.0), sharex="col")
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.95, hspace=0.0, wspace=0.28)
    for j, name in enumerate(("quadratic", "inflection")):
        d, r = load(msdir, name)
        cN = d["N"] - float(d["Nstar"])
        V = d["H"] ** 2 * (3 - d["eps1"]) * 1e8          # Mpl = 100 units as in the paper
        for i, (key, y) in enumerate((("V", V), ("eps1", d["eps1"]), ("eps2", d["eps2"]))):
            ax = axs[i, j]
            ax.plot(cN, y, color=fs.PAL["red"], label="this reference")
            pts = np.array(READ[name][key])
            ax.plot(pts[:, 0], pts[:, 1], "o", color=fs.PAL["blue"], ms=4,
                    label="read off Fig. 1 of 2512.14649")
            ax.axvline(0.0, **fs.MASK_LINE)
            if key == "eps2" and name == "inflection":
                ax.axhline(3.0, **fs.THIN, ls=":")
            if key == "eps1" and name == "inflection":
                ax.set_yscale("log")
            ax.set_ylabel({"V": r"$V\ [(0.01 M_{\rm Pl})^4]$", "eps1": r"$\varepsilon_1$",
                           "eps2": r"$\varepsilon_2$"}[key])
        axs[0, j].set_title(name)
        axs[2, j].set_xlabel(r"$\mathcal{N}-\mathcal{N}^\circledast$")
        axs[0, j].legend(loc="upper right")
    fs.save(fig, os.path.join(out, "fig_background"), png=True)
    plt.close(fig)


def fig_freezing(msdir, out):
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.5), sharex="col")
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.95, hspace=0.0, wspace=0.28)
    styles = ["-", "--", "-.", ":"]
    for j, name in enumerate(("quadratic", "inflection")):
        d, r = load(msdir, name)
        cN = d["N"] - float(d["Nstar"])
        k = d["k"]
        kd = k / float(d["dk"])
        pick = [np.argmin(abs(kd - x)) for x in (1, 4, 16, 64)]
        for s, i in zip(styles, pick):
            Dm = k[i] ** 3 * np.abs(d["R_ms"][i]) ** 2 / (2 * np.pi**2)
            Dd = k[i] ** 3 * np.abs(d["R_def"][i]) ** 2 / (2 * np.pi**2)
            axs[0, j].plot(cN, Dm, color=fs.PAL["blue"], ls=s,
                           label=r"MS, $k=%g\,dk$" % round(kd[i]))
            axs[0, j].plot(cN, Dd, color=fs.PAL["red"], ls=s)
            axs[1, j].plot(cN, Dd / Dm, color=fs.PAL["red"], ls=s)
            axs[0, j].axvline(float(d["Ncross"][i]) - float(d["Nstar"]), **fs.MASK_LINE)
            if name == "quadratic":
                # guide: exp(-4 int_{Nx}^{N} eps1 dN) after crossing (2606.14853 eq. 6)
                Nx = float(d["Ncross"][i])
                m = d["N"] >= Nx
                e = d["eps1"][m]
                integ = np.concatenate([[0], np.cumsum(0.5 * (e[1:] + e[:-1]) * np.diff(d["N"][m]))])
                g = np.exp(-4 * integ)
                axs[1, j].plot(cN[m], g, **fs.GUIDE, alpha=0.6 if s != "-" else 1.0)
        axs[0, j].set_yscale("log")
        axs[0, j].set_title(name)
        axs[0, j].set_ylabel(r"$\Delta_{\mathcal{R}}$ (blue MS, red deformed)")
        axs[1, j].set_ylabel(r"$\Delta_{\rm def}/\Delta_{\rm MS}$")
        axs[1, j].set_xlabel(r"$\mathcal{N}-\mathcal{N}^\circledast$")
        if name == "inflection":
            axs[1, j].set_yscale("log")
        axs[0, j].legend(loc="lower right" if name == "inflection" else "lower left", ncol=1,
                         fontsize=8)
        axs[1, j].axhline(1.0, **fs.THIN, ls=":")
    fs.save(fig, os.path.join(out, "fig_freezing"), png=True)
    plt.close(fig)


def fig_spectra(msdir, out):
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.0), sharex="col",
                            gridspec_kw=dict(height_ratios=[2, 1]))
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.10, top=0.94, hspace=0.0, wspace=0.32)
    for j, name in enumerate(("quadratic", "inflection")):
        d, r = load(msdir, name)
        kd = np.array(r["k_over_dk"])
        Dm = np.array(r["Delta_ms_Nf"])
        Dd = np.array(r["Delta_def_Nf"])
        axs[0, j].plot(kd, Dm, "o-", color=fs.PAL["blue"], ms=3, label="Mukhanov-Sasaki")
        axs[0, j].plot(kd, Dd, "s-", color=fs.PAL["red"], ms=3, label="deformed (no metric pert.)")
        if name == "quadratic":
            axs[0, j].plot(kd, r["Delta_SR_estimate_at_cross"], **fs.GUIDE,
                           label=r"$H^2/(8\pi^2\varepsilon_1)$ at $k=aH$")
        axs[0, j].set_xscale("log")
        axs[0, j].set_yscale("log")
        axs[0, j].set_title(r"%s, $\mathcal{N}_f-\mathcal{N}^\circledast=%g$" % (name, r["Nf"] - r["Nstar"]))
        axs[0, j].set_ylabel(r"$\Delta_{\mathcal{R}}(k,\mathcal{N}_f)$")
        axs[0, j].legend(loc="upper left" if name == "inflection" else "lower left")
        axs[1, j].plot(kd, Dd / Dm, "s-", color=fs.PAL["red"], ms=3)
        axs[1, j].axhline(1.0, **fs.THIN, ls=":")
        axs[1, j].set_ylabel("deformed / MS")
        axs[1, j].set_xlabel(r"$k/dk$ ($dk=k_\sigma^\circledast$, $\sigma=1$, $N=256$)")
        if name == "inflection":
            axs[1, j].set_yscale("log")
    fs.save(fig, os.path.join(out, "fig_spectra"), png=True)
    plt.close(fig)


def drift_check(msdir, out):
    """T2d: drift of ln Delta_MS per e-fold in windows [Nx + j, Nx + j + 1]."""
    d, r = load(msdir, "quadratic")
    N = d["N"]
    k = d["k"]
    res = {}
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.2))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.15, top=0.95)
    js = np.arange(1, 8)
    for i in range(0, 8):
        Nx = float(d["Ncross"][i])
        lnD = np.log(k[i] ** 3 * np.abs(d["R_ms"][i]) ** 2 / (2 * np.pi**2))
        dr = []
        for jj in js:
            m = (N >= Nx + jj) & (N <= Nx + jj + 1)
            dr.append(np.polyfit(N[m], lnD[m], 1)[0] if (m.sum() > 10 and N[m][-1] - N[m][0] > 0.9) else np.nan)
        dr = np.array(dr)
        res["k=%.3g dk" % (k[i] / float(d["dk"]))] = dr.tolist()
        ax.semilogy(js + 0.5, np.abs(dr), "o-", color=fs.SERIES[i % 5], ms=3, lw=1.0)
    g = 1e-2 * np.exp(-2 * (js + 0.5 - 3.5))
    ax.semilogy(js + 0.5, g, **fs.GUIDE, label=r"$\propto e^{-2\Delta\mathcal{N}}$")
    ax.set_xlabel(r"e-folds after crossing, $\mathcal{N}-\mathcal{N}_k$")
    ax.set_ylabel(r"$|d\ln\Delta_{\rm MS}/d\mathcal{N}|$ (quadratic)")
    ax.legend(loc="upper right")
    fs.save(fig, os.path.join(out, "fig_drift"), png=True)
    plt.close(fig)
    ratios = {}
    for key, dr in res.items():
        dr = np.array(dr)
        if np.isfinite(dr[2]) and np.isfinite(dr[4]):
            ratios[key] = float(abs(dr[4] / dr[2]))   # window [Nx+5,Nx+6] over [Nx+3,Nx+4]
    return {"drift_windows_j": js.tolist(), "drift": res, "ratio_j5_over_j3": ratios}


def fig_norm(normdir, out):
    r = json.load(open(os.path.join(normdir, "norm_test.json")))
    e = np.array(r["edges_over_dk"])
    kc = np.sqrt(e[:-1] * e[1:])
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.2))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.15, top=0.95)
    cols = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"]]
    for c, name in zip(cols, ("L^-3/2", "dk^3/2", "(dk/sqrt(2pi))^3/2")):
        m = np.array(r[name]["mean_ratio_per_shell"])
        s = np.array(r[name]["std_of_mean_per_shell"])
        ax.errorbar(kc, m, yerr=s, fmt="o-", color=c, ms=3, lw=1.0, label=name)
        ax.axhline(r["expected_power_ratio"][name], color=c, lw=1.0, ls="--")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$k/dk$")
    ax.set_ylabel(r"$\Delta_{\rm measured}/\Delta_{\rm input}$")
    ax.legend(loc="center right", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_norm"), png=True)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True)
    ap.add_argument("--norm", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    fig_background(a.ms, a.out)
    fig_freezing(a.ms, a.out)
    fig_spectra(a.ms, a.out)
    chk = drift_check(a.ms, a.out)
    fig_norm(a.norm, a.out)
    with open(os.path.join(a.out, "checks.json"), "w") as fh:
        json.dump(chk, fh, indent=1)
    print(json.dumps(chk["ratio_j5_over_j3"], indent=1))


if __name__ == "__main__":
    main()
