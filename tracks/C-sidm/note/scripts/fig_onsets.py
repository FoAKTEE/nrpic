"""Figure: where the equilibria turn unstable, collisionless and collision-dominated (gate G1).

Top: binding-energy fraction near its maximum, (a) along the King family against its central
potential y0, (b) along the thermal core (b = 0.1) against its central redshift, with the
particle models built for the runs and the two King models of the first collisional runs.
Bottom: the lowest squared radial-pulsation frequency of the same profiles treated as a
perfect fluid, normalised by its largest value on the sequence, for the adiabatic index of a
Juttner gas at the energy-matched temperature and for Gamma = 1 + p/u, (c) King, (d) thermal
core. Vertical lines: binding-energy maximum (dotted), Juttner onset (dashed), 1 + p/u onset
(dash-dotted).
Reads runs kingonset (King sequence and onsets), onset (thermal-core onsets and frequency
sequences), thermal (thermal-core sequence and maximum) and models2 (particle models).
"""
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_onsets"


def vlines(ax, xmax, xj, xg):
    ax.axvline(xmax, color=cz.PAL["blue"], lw=1.0, ls=":")
    ax.axvline(xj, color=cz.PAL["red"], lw=1.0, ls="--")
    ax.axvline(xg, color="0.45", lw=1.0, ls="-.")


def main():
    out = cm.out_dir("figures")
    ko = cm.load_json("kingonset", "rv_king_onset.json")
    fo = cm.load_json("onset", "fluid_onset.json")["results"]["0.1"]
    fd = np.load(cm.run_file("onset", "fluid_onset_figdata.npz"))
    seq = cm.load_json("thermal", "sequences.json")["0.1"]
    idx = cm.load_json("models2", "index.json")["models"]

    # King family
    ky = np.array(ko["seq"]["y0"])
    keps = np.array(ko["seq"]["eps"])
    kwj = np.array(ko["seq"]["J_E"])
    kwg = np.array(ko["seq"][cm.K_F21])
    k_max = ko["eps_max_y0"]
    k_j = ko["onset"][cm.K_JE_N]["y0"]
    k_jp = ko["onset"][cm.K_JP_N]["y0"]
    k_g = ko["onset"][cm.K_F21_N]["y0"]
    kmods = [m for m in idx if m["family"] == "king"]
    # thermal core b = 0.1
    tz = np.array([r["Z0"] for r in seq])
    teps = np.array([r["eps"] for r in seq])
    fz = fd["b0.1_seq_Z0"]
    fwj = fd["b0.1_seq_J_E"]
    fwg = fd["b0.1_seq_" + cm.K_F21]
    t_max = fo["eps_max"]["Z0"]
    t_j = fo["onset"][cm.K_JE_N]["Z0"]
    t_jp = fo["onset"][cm.K_JP_N]["Z0"]
    t_g = fo["onset"][cm.K_F21_N]["Z0"]
    tmods = [m for m in idx if m["family"] != "king"]

    cz.use_style()
    fig = plt.figure(figsize=(7.0, 4.1))
    axa = fig.add_axes([0.105, 0.56, 0.37, 0.40])
    axb = fig.add_axes([0.595, 0.56, 0.38, 0.40])
    axc = fig.add_axes([0.105, 0.10, 0.37, 0.40])
    axd = fig.add_axes([0.595, 0.10, 0.38, 0.40])

    # (a) King binding energy
    yy = np.linspace(0.28, 0.40, 200)
    # cubic interpolation of the tabulated sequences for smooth curves (the onsets are the
    # solver's roots, read from the files)
    cs = CubicSpline(ky, keps)
    axa.plot(yy, cs(yy) * 1e2, color=cz.PAL["green"], lw=1.3, label="King sequence")
    axa.plot([m["y0"] for m in kmods], [m["Eb"] * 1e2 for m in kmods], "o", ms=4, mfc="none",
             mec="k", mew=0.8, label="particle models")
    for m in kmods:
        tag = {0.314: "CC2", 0.33403: "CC1"}.get(round(m["y0"], 5))
        if tag:
            axa.annotate(tag, (m["y0"], m["Eb"] * 1e2), xytext=(-4, -13 if tag == "CC2" else 7),
                         textcoords="offset points", fontsize=7.5, ha="center")
    vlines(axa, k_max, k_j, k_g)
    axa.set_xlim(0.28, 0.40)
    axa.set_ylim(3.47, 3.575)
    axa.set_xticklabels([])
    axa.set_ylabel(r"binding fraction $\epsilon$ ($10^{-2}$)")
    axa.legend(frameon=False, loc="lower right", fontsize=7, handlelength=1.3)
    axa.text(0.03, 0.9, "(a) King", transform=axa.transAxes, fontsize=8.5)

    # (b) thermal core binding energy
    o = np.argsort(tz)
    zz = np.linspace(0.45, 0.68, 300)
    axb.plot(zz, CubicSpline(tz[o], teps[o])(zz) * 1e2, color=cz.PAL["blue"], lw=1.3, label=r"thermal core, $b=0.1$")
    axb.plot([q["Zc"] for q in tmods], [q["Eb"] * 1e2 for q in tmods], "o", ms=4, mfc="none",
             mec="k", mew=0.8, label="particle models")
    vlines(axb, t_max, t_j, t_g)
    axb.set_xlim(0.45, 0.68)
    axb.set_ylim(3.44, 3.53)
    axb.set_xticklabels([])
    axb.set_ylabel(r"binding fraction $\epsilon$ ($10^{-2}$)")
    axb.legend(frameon=False, loc="lower center", fontsize=7, handlelength=1.3)
    axb.text(0.03, 0.9, "(b) thermal core", transform=axb.transAxes, fontsize=8.5)

    # (c), (d) pulsation frequencies
    for ax, x, wj, wg, lim, (xm, xj, xg), lab in (
            (axc, ky, kwj, kwg, (0.28, 0.40), (k_max, k_j, k_g), r"central potential $y_0$"),
            (axd, fz, fwj, fwg, (0.45, 0.68), (t_max, t_j, t_g), r"central redshift $Z(0)$")):
        ax.axhline(0, color="k", lw=0.6)
        xs = np.linspace(lim[0], lim[1], 300)
        ax.plot(xs, CubicSpline(x, wj)(xs) / np.max(wj), color=cz.PAL["red"], lw=1.3, label="Jüttner $\Gamma_1$")
        ax.plot(xs, CubicSpline(x, wg)(xs) / np.max(wg), color="0.45", lw=1.3, label=r"$\Gamma=1+p/u$")
        vlines(ax, xm, xj, xg)
        ax.set_xlim(*lim)
        ax.set_ylim(-1.6, 1.15)
        ax.set_xlabel(lab)
        ax.set_ylabel(r"$\omega_0^2/\max\,\omega_0^2$")
    axc.legend(frameon=False, loc="lower left", fontsize=7, handlelength=1.3)
    axc.text(0.97, 0.9, "(c) King", transform=axc.transAxes, fontsize=8.5, ha="right")
    axd.text(0.97, 0.9, "(d) thermal core", transform=axd.transAxes, fontsize=8.5, ha="right")

    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    ac = {round(m["y0"], 5): m["alpha_c"] for m in kmods}
    print(f"{STEM}: King: binding-energy maximum y0 {k_max:.6f}; Juttner onset y0 {k_j:.5f} "
          f"(central lapse {1 / (1 + ko['onset'][cm.K_JE_N]['Z0']):.4f}), at theta = p/n "
          f"{k_jp:.5f}; 1 + p/u onset {k_g:.5f}; CC2 y0 0.314 lapse {ac[0.314]:.4f}, CC1 "
          f"y0 0.33403 lapse {ac[0.33403]:.4f}")
    print(f"{STEM}: thermal core: maximum Z(0) {t_max:.5f}; Juttner onset {t_j:.5f}, at "
          f"theta = p/n {t_jp:.5f}; 1 + p/u onset {t_g:.5f}; particle models "
          + ", ".join(f"{q['Zc']:.4f}" for q in tmods))
    for nm, x, w in (("King J", ky, kwj), ("King 1+p/u", ky, kwg), ("thermal J", fz, fwj),
                     ("thermal 1+p/u", fz, fwg)):
        i = np.flatnonzero((w[:-1] > 0) & (w[1:] <= 0))
        print(f"{STEM}: {nm}: tabulated omega^2 changes sign between "
              + ", ".join(f"{x[j]:.4f} and {x[j + 1]:.4f}" for j in i))


if __name__ == "__main__":
    main()
