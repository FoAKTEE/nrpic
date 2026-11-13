#!/usr/bin/env python3
"""Diagnostic figure for part C: the e = 0.99 Kerr-Schild passage, all pusher / metric-input
combinations.

Top left: exact trajectory projected on the x-y plane of Cartesian KS (blue), event horizon
(black) and equatorial ergosphere (grey), pericentre marked.  Top middle: position error
max(|dr|/M, |dtheta|, |dphi|) against the reference trajectory versus t at dt = 0.01 M.
Top right: final-position error at t = 230 M versus dt.  Bottom: |Delta E/E_0| and
|Delta Q/Q_0| versus t at dt = 0.01 M (max over 0.4 M bins), and max |Delta E/E_0| versus dt.
Colour = pusher (red midpoint, yellow Boris symmetric, green Boris Cholesky); line style =
metric input (solid analytic spherical KS, dashed analytic Cartesian KS, dotted Hermite lattice
dx = 0.025 M).

Data: problems/kerr/results/{kerr_histories.npz, ks_passage_convergence.json}.
Output: analysis/geodesic/figs/diag_kerr_passage.{pdf,png}.
"""

from __future__ import annotations

import numpy as np

from geo_common import KERR_RESULTS, kerr, load_json
import geo_style as gs

A = 0.9
PUSHERS = ("mid", "bsym", "bchol")
METRICS = ("ks", "cks", "lat")


def main():
    gs.use_style()
    import matplotlib.pyplot as plt

    h = np.load(KERR_RESULTS / "kerr_histories.npz")
    conv = load_json(KERR_RESULTS / "ks_passage_convergence.json")
    S = load_json(KERR_RESULTS / "kerr_summary.json")["C"]
    t = h["C__t"]
    fig, axs = plt.subplots(2, 3, figsize=(gs.FULL_WIDTH, 5.8))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.075, top=0.985, wspace=0.36, hspace=0.27)

    ax = axs[0, 0]
    xr = kerr.ks_to_cks_position(h["C__xref"].astype(float), A)
    r_plus = 1 + np.sqrt(1 - A * A)
    gs.black_hole_disk(ax, np.sqrt(r_plus ** 2 + A * A), np.sqrt(4 + A * A))
    ax.plot(xr[:, 0], xr[:, 1], color=gs.COLOR["ref"], lw=1.2, label="exact")
    ip = int(np.argmin(h["C__xref"][:, 0]))
    ax.plot(xr[0, 0], xr[0, 1], "o", color=gs.COLOR["ref"], mec="k", ms=5, label="start")
    ax.plot(xr[ip, 0], xr[ip, 1], "s", color="white", mec="k", ms=5,
            label=rf"pericentre, $t\approx{S['exact']['t_peri']:.1f}M$")
    ax.set_aspect("equal")
    ax.set_xlim(-25, 25)
    ax.set_ylim(-25, 25)
    ax.set_xlabel(r"$x/M$", labelpad=-2)
    ax.set_ylabel(r"$y/M$")
    ax.legend(loc="lower left", fontsize=7.5)

    def conv_of(p, m):
        if m == "ks":
            return conv["analytic_ks"].get(p)
        return conv["analytic_cks" if m == "cks" else "lattice"].get(p)

    for p in PUSHERS:
        for m in METRICS:
            k = f"C--{p}_{m}_dt0.01"
            if f"{k}__dpos" not in h.files:
                continue
            axs[0, 1].plot(t, h[f"{k}__dpos"], lw=1.0, **gs.style(p, m))
            axs[1, 0].plot(t[1:], h[f"{k}__dE"], lw=1.0, **gs.style(p, m))
            axs[1, 1].plot(t[1:], h[f"{k}__dQ"], lw=1.0, **gs.style(p, m))
            c = conv_of(p, m)
            if c is not None:
                axs[0, 2].plot(c["dt"], c["err"], marker=gs.MARKER[p], ms=4,
                               mfc="white" if m != "ks" else gs.COLOR[p], **gs.style(p, m))
                axs[1, 2].plot(c["dt"], c["dE"], marker=gs.MARKER[p], ms=4,
                               mfc="white" if m != "ks" else gs.COLOR[p], **gs.style(p, m))
    for ax, lab in ((axs[0, 1], r"$\|\delta(r/M,\theta,\phi)\|_\infty$, $\Delta t=0.01M$"),
                    (axs[1, 0], r"$|\Delta E/E_0|$, $\Delta t=0.01M$"),
                    (axs[1, 1], r"$|\Delta Q/Q_0|$, $\Delta t=0.01M$")):
        ax.axvline(S["exact"]["t_peri"], **gs.MASK_LINE)
        ax.set_yscale("log")
        ax.set_xlim(0, 230)
        ax.set_xlabel(r"$t/M$", labelpad=-2)
        ax.set_ylabel(lab)
    axs[0, 1].set_ylim(1e-15, 1e0)
    axs[1, 0].set_ylim(1e-14, 1e-2)
    axs[1, 1].set_ylim(1e-14, 1e-2)
    for ax, lab in ((axs[0, 2], r"$\|\delta(r/M,\theta,\phi)\|_\infty$ at $t=230M$"),
                    (axs[1, 2], r"$\max|\Delta E/E_0|$")):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.001, 0.095)
        ax.set_xlabel(r"$\Delta t/M$", labelpad=-2)
        ax.set_ylabel(lab)
    c = conv["analytic_ks"]["mid"]
    dts = np.array([0.001, 0.1])
    for ax, q, f in ((axs[0, 2], "err", 0.3), (axs[1, 2], "dE", 0.3)):
        e = c[q][c["dt"].index(0.01)]
        ax.plot(dts, f * e * (dts / 0.01) ** 2, **gs.GUIDE)
        ax.text(0.012, f * e * 1.2 ** 2 / 4, r"$\propto\Delta t^2$", fontsize=9)
    hs = [plt.Line2D([], [], color=gs.COLOR[p], label=gs.PUSHER_NAME[p]) for p in PUSHERS]
    hs += [plt.Line2D([], [], color="0.3", ls=gs.LS[m], label=gs.METRIC_NAME[m]) for m in METRICS]
    axs[0, 1].legend(handles=hs, loc="lower right", fontsize=7, ncol=2, handlelength=1.8,
                     columnspacing=0.6)
    print("wrote", gs.save_diag(fig, "diag_kerr_passage"))


if __name__ == "__main__":
    main()
