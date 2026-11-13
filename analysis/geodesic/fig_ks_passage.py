#!/usr/bin/env python3
"""Figure fig_ks_passage.pdf: the off-equatorial e = 0.99 Kerr-Schild passage (a = 0.9 M).

Analogue of the paper's six-panel passage figure.  Top left: r(t).  Top middle: the r < 4M
segment in Cartesian Kerr-Schild coordinates with the event horizon.  Top right: final-position
error max(|dr|/M, |dtheta|, |dphi|) at t = 230 M against the exact final state versus dt, for
analytic spherical KS input (solid), analytic Cartesian KS input (dashed) and the Hermite
lattice (dx = 0.025 M, dotted).  Bottom: |Delta E/E_0|, |Delta L_z/L_z0|, |Delta Q/Q_0| versus
t.  Grey vertical lines: exact pericentre.  Histories: dt = 0.01 M.
Colours: red midpoint, yellow Boris symmetric triad, green Boris Cholesky triad (geo_style.py).

Data: problems/kerr/results/{ks_passage_histories.npz, ks_passage_convergence.json}
(analyze_kerr.py).  Output: paper/figures/fig_ks_passage.pdf (+ PNG copy in
analysis/geodesic/figs/).
"""

from __future__ import annotations

import numpy as np

from geo_common import KERR_RESULTS, kerr, load_json
import geo_style as gs

A = 0.9
SERIES = [("mid", "ks"), ("bsym", "ks"), ("mid", "lat"), ("bchol", "lat")]   # paper's four
FLOOR = 1e-17


def main():
    gs.use_style()
    import matplotlib.pyplot as plt

    h = np.load(KERR_RESULTS / "ks_passage_histories.npz")
    conv = load_json(KERR_RESULTS / "ks_passage_convergence.json")
    t_p = float(h["t_peri_exact"])
    r_plus = 1 + np.sqrt(1 - A * A)

    fig = plt.figure(figsize=(gs.FULL_WIDTH, 5.8))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.075, top=0.985, wspace=0.42,
                        hspace=0.28)
    ax_a = fig.add_subplot(2, 3, 1)
    ax_b = fig.add_subplot(2, 3, 2, projection="3d")
    ax_c = fig.add_subplot(2, 3, 3)
    ax_inv = [fig.add_subplot(2, 3, 4 + k) for k in range(3)]

    # r(t)
    for p, m in SERIES:
        k = f"{p}_{m}"
        ax_a.plot(h[f"{k}__t"], h[f"{k}__r"], label=gs.label(p, m), **gs.style(p, m))
    ax_a.axhline(r_plus, **gs.MASK_LINE)
    ax_a.text(200, r_plus * 1.05, r"$r_+$", fontsize=9, color="0.4")
    ax_a.axvline(t_p, **gs.MASK_LINE)
    ax_a.set_yscale("log")
    ax_a.set_yticks([1.5, 2, 3, 5, 10, 20])
    ax_a.set_yticklabels(["1.5", "2", "3", "5", "10", "20"])
    ax_a.yaxis.set_minor_formatter(plt.NullFormatter())
    ax_a.set_ylim(1.3, 30)
    ax_a.set_xlim(0, 230)
    ax_a.set_xlabel(r"$t/M$", labelpad=-2)
    ax_a.set_ylabel(r"$r/M$")

    # r < 4M segment in Cartesian KS coordinates
    for p, m in SERIES:
        k = f"{p}_{m}"
        x = h[f"{k}__x"].astype(float)
        xc = kerr.ks_to_cks_position(x, A) if m == "ks" else x
        idx = np.where(h[f"{k}__r"] < 4.0)[0]
        seg = slice(idx[0], idx[-1] + 1)
        ax_b.plot(xc[seg, 0], xc[seg, 1], xc[seg, 2], lw=1.2, **gs.style(p, m))
    th, ph = np.meshgrid(np.linspace(0, np.pi, 40), np.linspace(0, 2 * np.pi, 60))
    rho = np.sqrt(r_plus ** 2 + A * A)
    ax_b.plot_surface(rho * np.sin(th) * np.cos(ph), rho * np.sin(th) * np.sin(ph),
                      r_plus * np.cos(th), color="black", linewidth=0, antialiased=False,
                      shade=False)
    lim = 3.0
    for setl in (ax_b.set_xlim, ax_b.set_ylim, ax_b.set_zlim):
        setl(-lim, lim)
    ax_b.set_box_aspect((1, 1, 1))
    ax_b.set_xticks([-2, 0, 2])
    ax_b.set_yticks([-2, 0, 2])
    ax_b.set_zticks([-2, 0, 2])
    ax_b.set_xlabel(r"$x/M$", labelpad=-7)
    ax_b.set_ylabel(r"$y/M$", labelpad=-7)
    ax_b.set_zlabel(r"$z/M$", labelpad=-8)
    ax_b.tick_params(axis="both", which="major", pad=-3, labelsize=8)
    for axis in (ax_b.xaxis, ax_b.yaxis, ax_b.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("0.8")
        axis._axinfo["grid"]["linewidth"] = 0.3
    ax_b.view_init(elev=22, azim=-60)
    from matplotlib.ticker import NullLocator
    for axis in (ax_b.xaxis, ax_b.yaxis, ax_b.zaxis):
        axis.set_minor_locator(NullLocator())
    ax_b.text2D(0.5, 0.98, r"$r<4M$ (Cartesian KS)", transform=ax_b.transAxes, ha="center",
                va="top", fontsize=9)

    # final-position error vs dt
    for p in ("mid", "bsym"):
        c = conv["analytic_ks"].get(p)
        if c is not None:
            ax_c.plot(c["dt"], c["err"], marker=gs.MARKER[p], ms=4, **gs.style(p, "ks"))
        c = conv.get("analytic_cks", {}).get(p)
        if c is not None:
            ax_c.plot(c["dt"], c["err"], marker=gs.MARKER[p], ms=4, mfc="white",
                      **gs.style(p, "cks"))
    for p in ("mid", "bchol"):
        c = conv.get("lattice", {}).get(p)
        if c is not None:
            ax_c.plot(c["dt"], c["err"], marker=gs.MARKER[p], ms=4, **gs.style(p, "lat"))
    c = conv["analytic_ks"]["mid"]
    dts = np.array([0.00125, 0.08])
    e01 = c["err"][c["dt"].index(0.01)]
    ax_c.plot(dts, 0.3 * e01 * (dts / 0.01) ** 2, **gs.GUIDE)
    ax_c.text(0.012, 0.3 * e01 * 1.2 ** 2 / 3.5, r"$\propto\Delta t^2$", fontsize=9)
    ax_c.set_xscale("log")
    ax_c.set_yscale("log")
    ax_c.set_xlim(0.0009, 0.095)
    ax_c.set_xlabel(r"$\Delta t/M$", labelpad=-2)
    ax_c.set_ylabel(r"$\|\delta(r/M,\theta,\phi)\|_\infty$ at $t=230M$")
    hs = [plt.Line2D([], [], color="0.3", ls="-", label="sph. KS"),
          plt.Line2D([], [], color="0.3", ls="--", marker="o", mfc="white", label="Cart. KS"),
          plt.Line2D([], [], color="0.3", ls=":", label="Hermite")]
    ax_c.legend(handles=hs, loc="upper left", fontsize=7.5, ncol=1, handlelength=2.2)

    # invariant errors
    names = [("dE", r"$|\Delta E/E_0|$"), ("dLz", r"$|\Delta L_z/L_{z,0}|$"),
             ("dQ", r"$|\Delta Q/Q_0|$")]
    for ax, (q, lab) in zip(ax_inv, names):
        for p, m in SERIES:
            k = f"{p}_{m}"
            y = np.abs(h[f"{k}__{q}"].astype(float))
            if q == "dLz" and np.all(y == 0):
                continue
            ax.plot(h[f"{k}__t"], np.maximum(y, FLOOR), lw=1.0, **gs.style(p, m))
        ax.axvline(t_p, **gs.MASK_LINE)
        ax.set_yscale("log")
        ax.set_xlim(0, 230)
        ax.set_ylim(1e-17, 1e-3)
        ax.set_yticks(10.0 ** np.arange(-16, -2, 3))
        ax.set_xlabel(r"$t/M$", labelpad=-2)
        ax.set_ylabel(lab)
    hs = [plt.Line2D([], [], label=gs.label(p, m).replace(" sph. KS", "").replace(" lattice", ""),
                     **gs.style(p, m)) for p, m in SERIES]
    ax_inv[0].legend(handles=hs, loc="lower right", fontsize=7.5, ncol=1, handlelength=2.2)
    ax_inv[1].text(0.97, 0.04, "midpoint, analytic:\n" + r"$\Delta L_z=0$ exactly",
                   transform=ax_inv[1].transAxes, ha="right", va="bottom", fontsize=8,
                   color=gs.COLOR["mid"])
    print("wrote", gs.save_paper(fig, "fig_ks_passage"))


if __name__ == "__main__":
    main()
