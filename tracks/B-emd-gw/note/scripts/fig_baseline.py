"""Figure: the semi-analytic Newtonian baseline, Zel'dovich ellipsoid with the quadrupole formula.

(a) Total radiated energy and the peak of the spectrum per logarithmic frequency, in units
of the rest-mass energy, against the linear amplitude, with the 7/2 power law. (b) Local
logarithmic slopes of the energy, of the peak and of the peak frequency, with the values
7/2 and 3/2 of the literature. Source: run B-emd-gw-20261115-115752-840e994,
baseline_results.json (check T2).
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402

STEM = "fig_baseline"


def main():
    out = common.out_dir("figures")
    cz.use_style()
    b = common.load_json("baseline", "baseline_results.json")["T2"]
    d = np.array(b["delta_L"])
    E = np.array(b["E_tot_over_Mc2"])
    P = np.array(b["peak_dEdlnw_over_Mc2"])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.4, 5.0))
    fig.subplots_adjust(left=0.19, right=0.96, top=0.98, bottom=0.09, hspace=0.32)
    ax1.loglog(d, E, "o-", color=cz.PAL["blue"], ms=4, lw=1.0, label="total energy")
    ax1.loglog(d, P, "s-", color=cz.PAL["red"], ms=4, mfc="none", lw=1.0,
               label="spectral peak")
    ax1.loglog(d, E[0]*(d/d[0])**3.5, "k--", lw=1.0, label=r"$\propto\delta_L^{7/2}$")
    ax1.set_xlabel(r"linear amplitude $\delta_L$")
    ax1.set_ylabel(r"energy in units of $Mc^2$")
    ax1.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.6)
    ax1.text(0.97, 0.07, "(a)", transform=ax1.transAxes, ha="right", va="bottom")

    dm = np.array(b["delta_mid"])
    ax2.semilogx(dm, b["slope_E"], "o-", color=cz.PAL["blue"], ms=4, lw=1.0, label="energy")
    ax2.semilogx(dm, b["slope_peak"], "s-", color=cz.PAL["red"], ms=4, mfc="none", lw=1.0,
                 label="spectral peak")
    ax2.semilogx(dm, b["slope_wpeak"], "D-", color=cz.PAL["yellow"], ms=4, lw=1.0,
                 label="peak frequency")
    ax2.axhline(3.5, color="k", lw=1.0, ls="--")
    ax2.axhline(1.5, color="k", lw=1.0, ls="--")
    ax2.set_xlabel(r"linear amplitude $\delta_L$")
    ax2.set_ylabel("local logarithmic slope")
    ax2.set_ylim(1.0, 4.0)
    ax2.legend(frameon=False, loc="center left", fontsize=7, handlelength=1.6)
    ax2.text(0.97, 0.07, "(b)", transform=ax2.transAxes, ha="right", va="bottom")
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
