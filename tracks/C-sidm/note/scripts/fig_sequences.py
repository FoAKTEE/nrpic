"""Figure: equilibrium sequences of the three families and where they turn unstable.

(a) fractional binding energy of the truncated Maxwell-Boltzmann (thermal-core) family at
b = 0.1 against the central redshift, solver curve and the printed rows of the source
table; (b) the lowest squared radial-pulsation frequency of the same models (finite
elements) for the two adiabatic indices, normalised at the binding-energy maximum;
(c) the King and monoenergetic families with the particle models built for the runs.
Reads runs thermal (sequences, criteria, table comparison), king, mono, models (common.RUNS).
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_sequences"


def main():
    out = cm.out_dir("figures")
    seq = cm.load_json("thermal", "sequences.json")["0.1"]
    crit = cm.load_json("thermal", "criteria.json")["0.1"]
    rows = list(csv.DictReader(open(cm.run_file("thermal", "table1_compare.csv"))))
    king = cm.load_json("king", "king_sequence.json")
    mono = cm.load_json("mono", "seq_monoenergetic.json")
    idx = cm.load_json("models", "index.json")

    Z = np.array([r["Z0"] for r in seq])
    eps = np.array([r["eps"] for r in seq])
    w2a = np.array([r["omega2_F21"] for r in seq])
    w2b = np.array([r["omega2_53"] for r in seq])
    tz = np.array([float(r["Z0_paper"]) for r in rows if float(r["b"]) == 0.1])
    te = np.array([float(r["eps_paper"]) for r in rows if float(r["b"]) == 0.1])

    cz.use_style()
    fig = plt.figure(figsize=(7.0, 2.55))
    axa = fig.add_axes([0.088, 0.18, 0.235, 0.72])
    axb = fig.add_axes([0.418, 0.18, 0.235, 0.72])
    axc = fig.add_axes([0.752, 0.18, 0.225, 0.72])

    # (a) binding energy, b = 0.1
    m = Z <= 1.05
    axa.plot(Z[m], eps[m], color=cz.PAL["blue"], label="solver")
    k = tz <= 1.05
    axa.plot(tz[k], te[k], "o", ms=3.5, mfc="none", mec="k", mew=0.8, label="printed table")
    marks = [("max_eps", cz.PAL["blue"], ":"), ("omega2_zero_F21gamma", cz.PAL["red"], "--"),
             ("gavg_eq_gcr", "0.45", "-.")]
    for key, col, ls in marks:
        axa.axvline(crit[key]["Z0"], color=col, lw=1.0, ls=ls)
    axa.set_xlim(0, 1.05)
    axa.set_ylim(0.0, 0.039)
    axa.set_xlabel(r"central redshift $Z(0)$")
    axa.set_ylabel(r"binding energy fraction")
    axa.legend(frameon=False, loc="lower right", fontsize=7.5, handlelength=1.4)
    axa.text(0.04, 0.93, "(a)  $b=0.1$", transform=axa.transAxes, fontsize=8.5)

    # (b) lowest pulsation frequency, normalised at the binding-energy maximum
    i0 = int(np.argmax(eps))
    m = (Z >= 0.30) & (Z <= 0.92)
    axb.axhline(0.0, color="k", lw=0.6)
    axb.plot(Z[m], w2a[m] / w2a[i0], color=cz.PAL["red"], label=r"$\Gamma=1+p/u$")
    axb.plot(Z[m], w2b[m] / w2b[i0], color=cz.PAL["yellow"], label=r"$\Gamma=5/3$")
    axb.axvline(crit["max_eps"]["Z0"], color=cz.PAL["blue"], lw=1.0, ls=":")
    axb.axvline(crit["omega2_zero_F21gamma"]["Z0"], color=cz.PAL["red"], lw=1.0, ls="--")
    axb.axvline(crit["omega2_zero_gamma53"]["Z0"], color=cz.PAL["yellow"], lw=1.0, ls="--")
    axb.set_xlim(0.30, 0.92)
    axb.set_ylim(-4.0, 2.2)
    axb.set_xlabel(r"central redshift $Z(0)$")
    axb.set_ylabel(r"$\omega_0^2/\omega_0^2(\epsilon_{\max})$")
    axb.legend(frameon=False, loc="lower left", fontsize=7.5, handlelength=1.4)
    axb.text(0.04, 0.93, "(b)  $b=0.1$", transform=axb.transAxes, fontsize=8.5)

    # (c) King (b = 1) and monoenergetic families
    ks = king["sequences"]["1.0"]
    kz = np.array([r["Z0"] for r in ks])
    ke = np.array([r["eps_b"] for r in ks])
    ms_ = mono["sequence"]
    mz = np.array([r["zc"] for r in ms_])
    me = np.array([r["Eb_over_M0"] for r in ms_])
    m = kz <= 1.05
    axc.plot(kz[m], ke[m], color=cz.PAL["green"], label="King")
    m = mz <= 1.05
    axc.plot(mz[m], me[m], color=cz.PAL["orange"], label="monoenergetic")
    kmax = king["maxima"]["1.0"]
    mmax = mono["binding_energy_maximum"]
    axc.plot([kmax["Z0"]], [kmax["eps_b"]], "*", ms=8, color=cz.PAL["green"])
    axc.plot([mmax["zc"]], [mmax["Eb_over_M0"]], "*", ms=8, color=cz.PAL["orange"])
    kp = [r for r in idx["models"] if r["family"] == "king"]
    axc.plot([r["Zc"] for r in kp], [r["Eb"] for r in kp], "o", ms=3.2, mfc="none",
             mec="k", mew=0.8, label="particle models")
    wm = mono["models"]
    axc.plot([r["zc"] for r in wm], [r["Eb_over_M0"] for r in wm], "s", ms=3.0, mfc="none",
             mec="0.35", mew=0.8, label="source-paper models")
    axc.set_xlim(0, 1.05)
    axc.set_ylim(0.0, 0.039)
    axc.set_xlabel(r"central redshift $z_c$")
    axc.set_ylabel(r"binding energy fraction")
    axc.legend(frameon=False, loc="lower right", fontsize=7.0, handlelength=1.3, labelspacing=0.25)
    axc.text(0.04, 0.93, "(c)", transform=axc.transAxes, fontsize=8.5)

    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    print(f"{STEM}: eps max at Z(0) = {crit['max_eps']['Z0']:.7f}; FEM onset (1+p/u) "
          f"Z(0) = {crit['omega2_zero_F21gamma']['Z0']:.7f}; (5/3) "
          f"{crit['omega2_zero_gamma53']['Z0']:.7f}; trial {crit['gavg_eq_gcr']['Z0']:.7f}")
    print(f"{STEM}: King max y0 = {kmax['y0']:.7f} Z0 = {kmax['Z0']:.7f}; mono max y_c = "
          f"{mmax['yc']:.7f} z_c = {mmax['zc']:.7f}; table rows b=0.1: {len(tz)}")


if __name__ == "__main__":
    main()
