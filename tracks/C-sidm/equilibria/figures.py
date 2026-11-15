#!/usr/bin/env python3
"""Figures of Tests 1-2 from the output of check_equilibria.py.

    python3 figures.py --checks DIR_OF_check_equilibria --ic DIR_OF_make_equilibria --out FIGDIR
"""

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evstatic  # noqa: E402,F401  (puts python/ on the path)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
import paper_values as pv  # noqa: E402

THR = [("king_y0p33403", "King, $y_0=y_{\\max}$"),
       ("poly05_y0p29766", "polytrope $k=1/2$, $y_0=y_{\\max}$"),
       ("arshell_y0p13545", "shell $L_0=0.1$, $E_b$ max")]


def fig_binding(D, out):
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fig.add_axes([0.10, 0.14, 0.38, 0.80])
    names = [("king", "King"), ("poly_k0.5", "$k=0.5$"), ("poly_k0.5_L0.001", "$k=0.5$, $L_0=10^{-3}$"),
             ("poly_k0.5_l0.1_L0.001", "$k=0.5$, $l=0.1$, $L_0=10^{-3}$")]
    for (nm, lab), c in zip(names, fs.SERIES):
        ax.plot(D[f"eb_{nm}_y"], D[f"eb_{nm}_Eb"], color=c, label=lab)
        ym, ebm, yz = D[f"eb_{nm}_ours"]
        ax.plot([ym], [ebm], "o", color=c, ms=4)
        row = next(r for r in pv.BINDING_TABLE if r["name"] == nm)
        for v in (row["y_max"], row["y_zero"]):
            ax.plot([float(v)], [0.0 if v == row["y_zero"] else ebm], "x", color="k", ms=6, mew=1.0)
    ax.axhline(0, **fs.MASK_LINE)
    ax.set_xlabel("$y_0$")
    ax.set_ylabel("$E_b=(N-M)/N$")
    ax.set_xlim(0, 1.2)
    ax.set_ylim(-0.08, 0.085)
    ax.plot([], [], "x", color="k", ms=6, mew=1.0, label="printed $y_{\\max}$, $y_{\\rm zero}$")
    ax.plot([], [], "o", color="grey", ms=4, label="computed maximum")
    ax.legend(loc="lower left", ncol=1, fontsize=7)
    # zoom on the maxima: printed y_max as vertical ticks, computed maxima as dots
    ins = fig.add_axes([0.31, 0.69, 0.16, 0.22])
    for (nm, lab), c in zip(names, fs.SERIES):
        ins.plot(D[f"eb_{nm}_y"], D[f"eb_{nm}_Eb"], color=c, lw=1.0)
        ym, ebm, yz = D[f"eb_{nm}_ours"]
        ins.plot([ym], [ebm], "o", color=c, ms=3)
        row = next(r for r in pv.BINDING_TABLE if r["name"] == nm)
        ins.plot([float(row["y_max"])] * 2, [ebm + 0.0001, ebm + 0.0004], color=c, lw=1.5)
    ins.set_xlim(0.22, 0.38)
    ins.set_ylim(0.0345, 0.0372)
    ins.tick_params(labelsize=6)
    ins.set_title("bars: printed $y_{\\max}$", fontsize=6, pad=2)
    ax = fig.add_axes([0.60, 0.14, 0.38, 0.80])
    for (case, lab), c in zip(((1, "Case 1 $(0,0)$"), (2, "Case 2 $(0,1/2)$"), (4, "Case 4 $(0,3/2)$")),
                              fs.SERIES):
        Z, E = D[f"ar{case}_Zc"], D[f"ar{case}_Eb"]
        ax.plot(Z, E, color=c, label=lab)
        tb = D[f"ar{case}_table"]
        rows = pv.AR_TABLES[case]["rows"]
        xerr = [pv.half_unit(r[0]) for r in rows]
        yerr = [pv.half_unit(r[1]) for r in rows]
        ax.errorbar(tb[:, 0], tb[:, 1], xerr=xerr, yerr=yerr, fmt="s", ms=3, color=c,
                    mfc="none", lw=1.0, capsize=0)
        Zm, Em = D[f"ar{case}_max"]
        ax.plot([Zm], [Em], "o", color=c, ms=4)
    ax.plot(D["ar1_sqrtZc"], D["ar1_Eb"], ls=":", color="grey",
            label="Case 1 vs $1/\\sqrt{\\alpha_c}-1$")
    ax.axhline(0, **fs.MASK_LINE)
    ax.set_xlabel("$Z_c=1/\\alpha(0)-1$")
    ax.set_ylabel("$E_b=(M_0-M)/M_0$")
    ax.set_xlim(0.1, 1.3)
    ax.set_ylim(-0.09, 0.075)
    ax.legend(loc="lower left", fontsize=8)
    ax.text(0.97, 0.97, "gr-qc/0601112, $L_0=0.1$\nsquares: Tables 1, 2, 4\n(bars: printed rounding)\n"
            "dots: computed maxima", transform=ax.transAxes, ha="right", va="top", fontsize=8)
    return fs.save(fig, os.path.join(out, "binding_energy"))


def fig_mass_radius(D, out):
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.4))
    ax = fig.add_axes([0.17, 0.14, 0.78, 0.80])
    y, M, R = D["king_MR_y"], D["king_MR_M"], D["king_MR_R"]
    ax.plot(R, M, color=fs.PAL["blue"])
    ymax, yM = D["king_MR_marks"]
    for yv, lab, c in ((yM, "first $M$ maximum", fs.PAL["yellow"]),
                       (ymax, "$E_b$ maximum $y_{\\max}$", fs.PAL["red"])):
        ax.plot(np.interp(yv, y, R), np.interp(yv, y, M), "o", color=c, label=f"{lab}, $y_0={yv:.4f}$")
    ax.set_xlabel("$R$ (paper units)")
    ax.set_ylabel("$M$ (paper units)")
    ax.legend(loc="lower right", fontsize=8)
    ax.text(0.04, 0.95, "King model, $y_0=0.02\\ldots3$", transform=ax.transAxes, va="top")
    return fs.save(fig, os.path.join(out, "king_mass_radius"))


def fig_profiles(D, out):
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.6))
    W, H = 0.27, 0.36
    for j, (tag, lab) in enumerate(THR):
        r = D[f"prof_{tag}_r"]
        ax = fig.add_axes([0.07 + j * 0.32, 0.56, W, H])
        sc = D[f"prof_{tag}_rho"].max()
        for key, c, ls, nm in (("n", fs.PAL["blue"], "-", "$n$"), ("rho", fs.PAL["red"], "-", "$\\rho$"),
                               ("p", fs.PAL["yellow"], "-", "$p$"), ("pT", fs.PAL["green"], "--", "$p_T$")):
            ax.plot(r, D[f"prof_{tag}_{key}"] / sc, color=c, ls=ls, label=nm)
        ax.set_title(lab, fontsize=9)
        ax.set_xlim(0, r[-1])
        if j == 0:
            ax.set_ylabel("moment / max $\\rho$")
        ax.legend(loc="upper right", fontsize=8, ncol=2)
        ax = fig.add_axes([0.07 + j * 0.32, 0.10, W, H])
        ax.plot(r, D[f"prof_{tag}_psi"], color=fs.PAL["blue"], label="$\\psi$")
        ax.plot(r, D[f"prof_{tag}_alpha"], color=fs.PAL["red"], label="$\\alpha$")
        ax.set_xlim(0, r[-1])
        ax.set_xlabel("$\\bar r/M$")
        if j == 0:
            ax.set_ylabel("metric")
        ax.legend(loc="center right", fontsize=8)
    return fs.save(fig, os.path.join(out, "profiles_threshold"))


def fig_constraint(D, specs, out):
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH * 1.5, 3.4))
    ax = fig.add_axes([0.13, 0.14, 0.84, 0.80])
    cols = {"king": fs.PAL["blue"], "poly05": fs.PAL["red"], "arshell": fs.PAL["green"]}
    seen = set()
    for sp in specs:
        tag = sp["tag"]
        r, res = D[f"hc_{tag}_r"], D[f"hc_{tag}_res"]
        rs = r[-1] / 1.5
        lab = sp["family"] if sp["family"] not in seen else None
        seen.add(sp["family"])
        ax.semilogy(r / rs, np.where(res > 0, res, np.nan), color=cols[sp["family"]], lw=0.8,
                    alpha=0.8, label=lab)
    ax.axhline(1e-6, **fs.GUIDE)
    ax.axvspan(0.95, 1.05, color="grey", alpha=0.15)
    import models
    import evstatic as ev
    for sp in specs:
        if sp["family"] == "arshell":
            md = ev.Equilibrium(models.FAMILIES["arshell"], sp["y0"])
            x = md.rbar_in / md.rbar_s
            ax.axvspan(x - 0.05, x + 0.05, color=cols["arshell"], alpha=0.06)
    ax.set_xlabel("$\\bar r/\\bar r_s$")
    ax.set_ylabel("$|\\Delta\\psi+2\\pi\\psi^5\\rho|$ / max source")
    ax.set_ylim(1e-14, 1e-1)
    ax.legend(loc="upper left", fontsize=8, ncol=3)
    ax.text(0.98, 0.04, "13 tables, 4th-order differences; dashed: test bound $10^{-6}$;\n"
            "shaded: bands excluded by the check at the outer (grey) and\n"
            "inner (green, shells) matter edge, where the source is not smooth",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7)
    return fs.save(fig, os.path.join(out, "constraint_residual"))


def fig_sampling(D, out):
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.6))
    W, H = 0.27, 0.235
    for j, (tag, lab) in enumerate(THR):
        x0 = 0.07 + j * 0.32
        # energies
        ax = fig.add_axes([x0, 0.71, W, H])
        xs, pdf, Es = D[f"E_{tag}_x"], D[f"E_{tag}_pdf"], D[f"E_{tag}_sample"]
        ax.hist(Es, bins=50, range=(xs[0], 1.0), density=True, histtype="step", color=fs.PAL["red"],
                lw=1.2, label="$10^4$ particles")
        ax.plot(xs, pdf, color=fs.PAL["blue"], label="continuum")
        ax.set_xlabel("$E/E_0$", labelpad=-2)
        ax.set_title(lab, fontsize=9)
        if j == 0:
            ax.set_ylabel("pdf")
        ax.legend(loc="upper left", fontsize=7)
        # radii
        ax = fig.add_axes([x0, 0.39, W, H])
        r = D[f"prof_{tag}_r"]
        dens = 4 * math.pi * r * r * D[f"prof_{tag}_psi"] ** 6 * D[f"prof_{tag}_n"]
        dens /= np.trapezoid(dens, r)
        rb = D[f"r_{tag}_sample"]
        ax.hist(rb, bins=50, range=(0, r[-1]), density=True, histtype="step", color=fs.PAL["red"], lw=1.2)
        ax.plot(r, dens, color=fs.PAL["blue"])
        ax.set_xlabel("$\\bar r/M$", labelpad=-2)
        if j == 0:
            ax.set_ylabel("$dN/d\\bar r$ (normalised)")
        # moment z-scores
        ax = fig.add_axes([x0, 0.07, W, H])
        zm, zs = D[f"z_{tag}_mc"], D[f"z_{tag}_strat"]
        sh = np.arange(1, 9)
        for k, (nm, mk) in enumerate((("$n$", "o"), ("$\\rho$", "s"), ("$p_r$", "^"), ("$p_t$", "v"))):
            ax.plot(sh + 0.08 * (k - 1.5), zm[:, k], mk, color=fs.PAL["blue"], ms=3.5, mfc="none",
                    label=f"mc {nm}" if j == 0 else None)
            ax.plot(sh + 0.08 * (k - 1.5), zs[:, k], mk, color=fs.PAL["red"], ms=3.5,
                    label=f"strat. {nm}" if j == 0 else None)
        ax.axhline(4.5, **fs.GUIDE)
        ax.set_ylim(0, 8)
        ax.set_xlabel("equal-mass shell", labelpad=-2)
        if j == 0:
            ax.set_ylabel("$|$est$-$exp$|/\\sigma$ ($N=2\\times10^4$)")
            ax.legend(loc="upper left", fontsize=6, ncol=2)
    return fs.save(fig, os.path.join(out, "sampling_threshold"))


def fig_shell_L(D, out):
    tag = THR[2][0]
    if f"L_{tag}_sample" not in D:
        return []
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.0))
    ax = fig.add_axes([0.16, 0.16, 0.79, 0.78])
    L = D[f"L_{tag}_sample"]
    ax.hist(L, bins=60, histtype="step", color=fs.PAL["red"], lw=1.2)
    ax.axvline(1.0, **fs.GUIDE)
    ax.set_xlabel("$L/L_0$ per particle")
    ax.set_ylabel("count")
    ax.text(0.95, 0.92, f"shell, $E_b$ max: min $L/L_0$ = {L.min():.6f}", transform=ax.transAxes,
            ha="right", va="top", fontsize=8)
    return fs.save(fig, os.path.join(out, "shell_angular_momentum"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checks", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    fs.use_style()
    os.makedirs(a.out, exist_ok=True)
    D = dict(np.load(os.path.join(a.checks, "figdata.npz")))
    specs = json.load(open(os.path.join(a.checks, "checks.json")))["model_set"]
    files = []
    files += fig_binding(D, a.out)
    files += fig_mass_radius(D, a.out)
    files += fig_profiles(D, a.out)
    files += fig_constraint(D, specs, a.out)
    files += fig_sampling(D, a.out)
    files += fig_shell_L(D, a.out)
    for f in files:
        print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
