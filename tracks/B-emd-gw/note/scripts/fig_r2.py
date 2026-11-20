"""Figure: the second round of the first source (note v2): noise floor and amplitude scaling.

(a) Jittered-lattice null: modulus of the + amplitude at K1 = (k, k, 0) of the single plane
wave (delta = 0.01, 64^3, eight particles per cell) with the lattice jittered by 0.3 and 0.1
cells along y and z (solid), against the prediction written from the initial data before the
card run (second-order formula with the noise potential, response of a mode without peculiar
velocity, noise-noise term; thick pale), the eps = 0.1 crossed-wave signal (black) and the
quiet plane-symmetric null (grey). (b) Departure from the second-order value,
|c_+/(s g) - 1| at K1, for delta = 0.01 (solid) and 0.0025 (dashed), eps = 1 and 0.3;
single-precision dumps (lines) and, for delta = 0.0025, the double-precision dumps (circles).
(c) The same against a delta/0.01: the curves of the two amplitudes collapse, the scaling of
the next order in the potential. Dotted in (a): first shell crossing of the plane wave.
Sources: per-dump diagnostics B-20261119-160530-7bdcb45 (jitter 0.3), -161519-6e0bc42 (jitter
0.1; delta = 0.0025, eps = 1), -163027-f0d304f (delta = 0.0025, eps = 0.3) of card batch
B-20261119-142833-19edd82; prediction B-20261119-142733-932e595; wave-2 scan files
B-20261115-174722-ba1048d, -180834-c77a132 (delta = 0.01). Reduction in r2data.py.
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402
import r2data as r2  # noqa: E402

STEM = "fig_r2"
COL = {"e1": cz.PAL["blue"], "e0p3": cz.PAL["red"]}
LAB = {"e1": r"$\epsilon=1$", "e0p3": r"$\epsilon=0.3$"}


def main():
    out = common.out_dir("figures")
    cz.use_style()
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(7.0, 2.65))
    fig.subplots_adjust(left=0.09, right=0.99, top=0.965, bottom=0.165, wspace=0.42)

    # (a) jittered null against its prediction and the eps = 0.1 signal
    for name, col, lab in (("jit0p3", cz.PAL["blue"], "jitter 0.3 cells"),
                           ("jit0p1", cz.PAL["red"], "jitter 0.1 cells")):
        t, a, c = r2.complex_amp(name, "K1")
        sel = t > 0
        p = r2.null_prediction(name, "K1", t)
        a1.loglog(a[sel], np.abs(p[sel]), color=col, lw=4.0, alpha=0.25, solid_capstyle="butt")
        a1.loglog(a[sel], np.abs(c[sel]), color=col, lw=1.0, label=lab)
    t, a, c = r2.complex_amp("s01", "K1")
    sel = t > 0
    a1.loglog(a[sel], np.abs(c[sel].real), color="k", lw=1.0, label=r"signal, $\epsilon=0.1$")
    t, a, c = r2.complex_amp("null0", "K1")
    sel = t > 0
    a1.loglog(a[sel], np.abs(c[sel]), color="grey", lw=1.0, label="quiet lattice")
    a1.plot([], [], color="k", lw=4.0, alpha=0.25, label="predicted")
    a1.axvline(1.0 + 1.0 / 0.01, color="grey", lw=1.0, ls=":")
    a1.set_xlim(1, 145)
    a1.set_ylim(1e-18, 1e-4)
    a1.set_xlabel(r"scale factor $a$", labelpad=1)
    a1.set_ylabel("box-mode amplitude")
    a1.legend(frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.42), fontsize=7, handlelength=1.6)

    # (b, c) departure from second order at two amplitudes
    for e in ("e1", "e0p3"):
        for delta, ls in ((0.01, "-"), (0.0025, "--")):
            name = f"d01_{e}" if delta == 0.01 else f"d0025_{e}"
            _, a, v = r2.departure(name, "bin")
            for ax, x in ((a2, a), (a3, a * delta / 0.01)):
                ax.loglog(x, np.abs(v), ls, color=COL[e], lw=1.0,
                          label=(LAB[e] + r", $\delta=$" + f"{delta:g}") if ax is a2 else None)
            if delta == 0.0025:
                _, ad, vd = r2.departure(name, "dbin")
                for ax, x in ((a2, ad), (a3, ad * delta / 0.01)):
                    ax.loglog(x, np.abs(vd), "o", color=COL[e], ms=3.5, mfc="none", mew=1.0)
    a2.plot([], [], "o", color="k", ms=3.5, mfc="none", label="double-precision dumps")
    for ax in (a2, a3):
        ax.set_ylim(1e-5, 1e3)
    a2.set_ylabel("departure from second order")
    a2.set_xlim(1, 145)
    a3.set_xlim(0.25, 145)
    a2.set_xlabel(r"scale factor $a$", labelpad=1)
    a3.set_xlabel(r"$a\delta/0.01$", labelpad=1)
    a2.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.8)

    for x, lab in ((a1, "(a)"), (a2, "(b)"), (a3, "(c)")):
        x.text(0.96, 0.05, lab, transform=x.transAxes, ha="right", va="bottom")
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
