"""Figure: the first gravitational-wave source and where its radiation band sits.

(a) Quasi-static second-order TT strain of two crossed sine waves of the potential with
amplitude ratio (1, eps, 0) in the box of four initial Hubble radii at delta = 0.01: the
amplitude of the (k, k, 0) mode against eps, with the closed form (5/12)|phi_x phi_y| of the
Fourier coefficient; the plane wave (eps = 0) has no TT part at any nonzero wave vector.
Source: run B-emd-gw-20261115-113148-4e5c33b, crossed_waves_tt.json.
(b) Virial gravitational-wave frequency at the collapse epoch, in units of c times the lowest
box wave number, against the amplitude, for boxes of two, four and eight initial Hubble
radii, with the two collapse epochs measured in the earlier full-relativity runs. Source:
run B-emd-gw-20261115-113632-2960145, regime_estimates.json (check 3B).
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402

STEM = "fig_source"


def main():
    out = common.out_dir("figures")
    cz.use_style()
    tt = common.load_json("crossed_tt", "crossed_waves_tt.json")
    rg = common.load_json("regime", "regime_estimates.json")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.4, 5.0))
    fig.subplots_adjust(left=0.19, right=0.96, top=0.98, bottom=0.09, hspace=0.32)

    scan = tt["eps_scan"]
    eps = np.array([r["ratios"][1] for r in scan])
    amp = np.array([r["hplus_kk0_abs"] for r in scan])
    pred = np.array([r["hplus_kk0_predicted"] for r in scan])
    ax1.loglog(eps, pred, "k-", lw=1.0, label=r"$\frac{5}{12}|\phi_x\phi_y|$")
    ax1.loglog(eps, amp, "o", color=cz.PAL["blue"], ms=4.5,
               label=r"$(k,k,0)$ mode, projected")
    c = tt["cases"]
    for key, col, lab in (("equal three (1,1,1)", cz.PAL["red"], "three equal waves"),
                          ("cosmo/ runs (1,0.9,1.1)", cz.PAL["yellow"], "three-wave data")):
        ax1.loglog(c[key]["ratios"][1], c[key]["hplus_kk0_abs"], "D", color=col, ms=5,
                   mfc="none", label=lab)
    ax1.set_xlabel(r"second-wave ratio $\epsilon$")
    ax1.set_ylabel(r"TT strain amplitude at $(k,k,0)$")
    ax1.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.2)
    ax1.text(0.97, 0.07, "(a)", transform=ax1.transAxes, ha="right", va="bottom")

    for L, col in ((2, cz.PAL["red"]), (4, cz.PAL["blue"]), (8, cz.PAL["yellow"])):
        r = rg["3B"][f"L{L}"]
        ax2.loglog(r["delta"], r["omega_over_ck1"], "-", color=col,
                   label=rf"box of {L} Hubble radii")
    for d, v in rg["3B"]["measured_infall_L4"].items():
        ax2.loglog(float(d), v["omega_over_ck1"], "s", color=cz.PAL["blue"], ms=5)
    ax2.axhline(1.0, color="grey", lw=1.0, ls=":")
    ax2.axhline(np.sqrt(2.0), color="grey", lw=1.0, ls=":")
    ax2.set_xlabel(r"amplitude $\delta$")
    ax2.set_ylabel(r"$\omega_{\rm vir}/(c\,k_1)$ at collapse")
    ax2.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.2)
    ax2.text(0.97, 0.07, "(b)", transform=ax2.transAxes, ha="right", va="bottom")
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
