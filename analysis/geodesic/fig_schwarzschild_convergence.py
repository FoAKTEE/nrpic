#!/usr/bin/env python3
"""Figure fig_schwarzschild_convergence.pdf: Schwarzschild (a = 0) single-particle convergence.

Top row: final-position error max(|dr|/M, |dtheta|, |dphi|) against the exact solution at t_end
versus dt for the circular (r = 8 M, t_end = 1000 M), eccentric (p = 8 M, e = 0.3, plane
inclined by 30 deg, t_end = 1000 M) and plunging (plane inclined by 45 deg, crosses the horizon,
t_end = 77.52 M) orbits.  Bottom row: the Cartesian Kerr-Schild metric stored on the AthenaK mesh
(dt = 0.01 M): final-position error versus dx for the circular and eccentric orbits (mesh: dotted,
filled markers; virtual lattice with the same spacing: large open markers; analytic Cartesian KS
at the same dt: dashed horizontal lines), and max |Delta E/E_0| versus dx.
Colours: red midpoint, yellow Boris symmetric triad, green Boris Cholesky triad; line style:
solid analytic spherical KS, dashed analytic Cartesian KS, dotted Hermite mesh (geo_style.py).

Data: problems/schwarzschild/results/schw_convergence.json (analyze_schwarzschild.py).
Output: paper/figures/fig_schwarzschild_convergence.pdf (+ PNG copy in analysis/geodesic/figs).
"""

from __future__ import annotations

import numpy as np

from geo_common import SCHW_RESULTS, load_json
import geo_style as gs

TITLES = {"circ": "circular, $r=8M$", "ecc": "eccentric, $e=0.3$", "plunge": "plunge"}
COMBOS = [("mid", "ks"), ("mid", "cks"), ("bsym", "ks"), ("bsym", "cks"), ("bchol", "cks")]


def main():
    gs.use_style()
    import matplotlib.pyplot as plt

    c = load_json(SCHW_RESULTS / "schw_convergence.json")
    fig, axs = plt.subplots(2, 3, figsize=(gs.FULL_WIDTH, 5.8))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.075, top=0.985, wspace=0.34,
                        hspace=0.27)
    for ax, orbit in zip(axs[0], ("circ", "ecc", "plunge")):
        for p, m in COMBOS:
            d = c["dt"].get(f"{orbit}_{p}_{m}")
            if d is None:
                continue
            ax.plot(d["dt"], d["final_err"], marker=gs.MARKER[p], ms=4.5,
                    mfc=gs.COLOR[p] if m == "ks" else "white", mec=gs.COLOR[p],
                    label=gs.label(p, m).replace("analytic ", ""), **gs.style(p, m))
        # guide anchored to a truncation-error-dominated series (for the circular orbit the
        # spherical-KS runs are exact up to round-off, so the Cartesian midpoint run is used)
        d = c["dt"][f"{orbit}_mid_cks" if orbit == "circ" else f"{orbit}_mid_ks"]
        dts = np.array([0.004, 0.1])
        e01 = d["final_err"][d["dt"].index(0.01)]
        fg = 0.03 if orbit == "circ" else 0.25
        ax.plot(dts, fg * e01 * (dts / 0.01) ** 2, **gs.GUIDE)
        ax.text(0.03, fg * e01 * 3 ** 2 / 6, r"$\propto\Delta t^2$", fontsize=9)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.004, 0.095)
        ax.set_xlabel(r"$\Delta t/M$", labelpad=-2)
        if orbit == "circ":
            ax.text(0.97, 0.17, TITLES[orbit] + "\nsph. KS: round-off only", transform=ax.transAxes,
                    ha="right", va="bottom", fontsize=8.5)
        else:
            ax.text(0.97, 0.04, TITLES[orbit], transform=ax.transAxes, ha="right", va="bottom",
                    fontsize=9)
    axs[0, 0].set_ylabel(r"$\|\delta(r/M,\theta,\phi)\|_\infty$ at $t_{\rm end}$")
    lo, hi = axs[0, 0].get_ylim()
    axs[0, 0].set_ylim(lo, hi * 1e4)
    axs[0, 0].legend(loc="upper left", fontsize=7, ncol=1, handlelength=2.0)

    # mesh: final error vs dx
    for ax, orbit in zip(axs[1, :2], ("circ", "ecc")):
        for p in ("mid", "bsym"):
            d = c["dx"].get(f"{orbit}_{p}_mesh")
            if d is not None:
                ax.plot(d["dx"], d["final_err"], marker=gs.MARKER[p], ms=4.5,
                        label=f"{gs.PUSHER_NAME[p]}, mesh", **gs.style(p, "mesh"))
                a = d.get("analytic_cks_same_dt")
                if a is not None:
                    ax.axhline(a["final_err"], lw=1.0, **gs.style(p, "cks"))
            d = c["dx"].get(f"{orbit}_{p}_lat")
            if d is not None:
                ax.plot(d["dx"], d["final_err"], ls="none", marker=gs.MARKER[p], ms=9,
                        mfc="none", mec=gs.COLOR[p], mew=1.0)
        d = c["dx"].get(f"{orbit}_mid_mesh")
        if d is not None:
            dx = np.array([0.1, 0.6])
            e = d["final_err"][d["dx"].index(0.25)]
            for pw, f in ((3, 0.35),):
                ax.plot(dx, f * e * (dx / 0.25) ** pw, **gs.GUIDE)
                ax.text(0.3, f * e * (0.3 / 0.25) ** pw / 5, rf"$\propto\Delta x^{pw}$", fontsize=9)
            a = d.get("analytic_cks_same_dt")
            if a is not None:
                ax.text(0.106, a["final_err"] * 1.6, r"analytic Cart. KS, $\Delta t=0.01M$",
                        fontsize=8, ha="left")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.1, 0.6)
        ax.set_xticks([0.125, 0.25, 0.5])
        ax.set_xticklabels(["0.125", "0.25", "0.5"])
        ax.xaxis.set_minor_formatter(plt.NullFormatter())
        ax.set_xlabel(r"$\Delta x/M$ (mesh)", labelpad=-2)
        ax.text(0.97, 0.30, TITLES[orbit], transform=ax.transAxes, ha="right", va="bottom",
                fontsize=9)
    axs[1, 0].set_ylabel(r"$\|\delta(r/M,\theta,\phi)\|_\infty$ at $t_{\rm end}$")
    hs = [plt.Line2D([], [], marker="o", ms=4.5, label="midpoint, mesh", **gs.style("mid", "mesh")),
          plt.Line2D([], [], marker="^", ms=4.5, label="Boris sym., mesh", **gs.style("bsym", "mesh")),
          plt.Line2D([], [], marker="o", ms=9, mfc="none", mec="0.3", ls="none", label="lattice")]
    axs[1, 0].legend(handles=hs, loc="upper left", fontsize=7.5)

    # mesh: energy error vs dx
    ax = axs[1, 2]
    for orbit, mfc in (("circ", None), ("ecc", "white")):
        for p in ("mid", "bsym"):
            d = c["dx"].get(f"{orbit}_{p}_mesh")
            if d is None:
                continue
            ax.plot(d["dx"], d["dE"], marker=gs.MARKER[p], ms=4.5, mfc=mfc or gs.COLOR[p],
                    mec=gs.COLOR[p], label=f"{gs.PUSHER_NAME[p]}, {orbit}", **gs.style(p, "mesh"))
    d = c["dx"].get("ecc_mid_mesh")
    if d is not None:
        dx = np.array([0.1, 0.6])
        e = d["dE"][d["dx"].index(0.25)]
        ax.plot(dx, 0.3 * e * (dx / 0.25) ** 3, **gs.GUIDE)
        ax.text(0.3, 0.3 * e * 1.2 ** 3 / 5, r"$\propto\Delta x^3$", fontsize=9)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.1, 0.6)
    ax.set_xticks([0.125, 0.25, 0.5])
    ax.set_xticklabels(["0.125", "0.25", "0.5"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel(r"$\Delta x/M$ (mesh)", labelpad=-2)
    ax.set_ylabel(r"$\max|\Delta E/E_0|$")
    ax.legend(loc="upper left", fontsize=7.5, ncol=1)
    print("wrote", gs.save_paper(fig, "fig_schwarzschild_convergence"))


if __name__ == "__main__":
    main()
