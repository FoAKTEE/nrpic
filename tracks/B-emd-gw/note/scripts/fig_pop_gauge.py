"""Figure: the halo population box in full relativity, read in two spatial gauges (note G2).

(a) sigma1 = 0.028: largest value of the trace K of the extrinsic curvature against a (a >= 15) for the zero-shift
run (restart X0 of the stop) and the Gamma-driver restart X2 from the same t = 8; the
zero-shift run stops with non-finite fields at a = 30.7, the shifted one passes to a = 36.
(b) sigma1 = 0.014: largest FoF halo (>= 100 particles), GR over the Newtonian mode of the
code with the same particles, and the median |M_GR/M_N - 1| of the ten largest, both gauges.
(c) sigma1 = 0.014: quasi-static TT measure of the metric (spatial-gauge piece removed) over
the estimate from the Newtonian particles, both gauges; diamonds: the GR particles through the
same estimator with the Newtonian masses (the rest-mass weight removed).
Sources: stop028.json of B-20261125-115619-ad8b3f4; compare_newton.json of
B-20261125-165836-70b17b6 (zero shift) and -165845-0621554 (Gamma driver); vel_check.json of
B-20261125-170535-84c9ba5.
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402

STEM = "fig_pop_gauge"
ZS, GD = cz.PAL["red"], cz.PAL["blue"]


def a_of_t(t):
    return (1.0 + 0.5*np.asarray(t))**2


def main():
    out = common.out_dir("figures")
    cz.use_style()
    st = common.load_json("pop_stop028", "stop028.json")
    cz_ = common.load_json("pop_cmp_zs", "compare_newton.json")
    cg = common.load_json("pop_cmp_gd", "compare_newton.json")
    vc = common.load_json("pop_velchk", "vel_check.json")
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(7.0, 2.5))
    fig.subplots_adjust(left=0.105, right=0.99, top=0.96, bottom=0.18, wspace=0.48)

    for key, col, lab in (("base", ZS, "zero shift"), ("x0_ctrl", ZS, None),
                          ("x2_gd", GD, "Gamma driver")):
        c = st[key]["cstat"]
        aa = a_of_t(c["t"])
        m = aa >= 15
        a1.plot(aa[m], np.asarray(c["K_max"])[m], "-", color=col, lw=1.1, label=lab)
    a1.axvline(float(a_of_t(st["base"]["stop_t"])), color=ZS, ls=":", lw=0.9)
    a1.set_xlabel(r"$a$")
    a1.axhline(0, color="k", lw=0.6)
    a1.set_ylabel(r"largest $K$ in the box")
    a1.legend(frameon=False, fontsize=7, loc="upper left")
    a1.text(0.96, 0.05, "(a)", transform=a1.transAxes, ha="right", va="bottom")

    for c, col, lab in ((cz_, ZS, "zero shift"), (cg, GD, "Gamma driver")):
        R = [r for r in c["N2"] if r["M1_N"] and r["a_GR"] > 60]
        aa = np.array([r["a_GR"] for r in R])
        a2.plot(aa, [r["M1_GR"]/r["M1_N"] - 1 for r in R], "o-", color=col, ms=3.5, lw=1.0,
                label=lab + ", largest")
        a2.plot(aa, [r["median_abs_dM"] for r in R], "s--", color=col, ms=3, lw=0.8,
                mfc="none", label=lab + ", median |.|")
    a2.axhline(0, color="k", lw=0.6)
    a2.axhspan(-0.05, 0.05, color="0.92", zorder=0)
    a2.set_xlabel(r"$a$")
    a2.set_ylabel(r"$M_{\rm GR}/M_{\rm N}-1$")
    a2.legend(frameon=False, fontsize=6, loc="upper right", ncol=1)
    a2.set_ylim(-0.08, 0.2)
    a2.text(0.04, 0.05, "(b)", transform=a2.transAxes, ha="left", va="bottom")

    for c, col, lab in ((cz_, ZS, "metric, zero shift"), (cg, GD, "metric, Gamma driver")):
        R = [r for r in c["N4"] if r["Omega_metric_cor"]]
        a3.loglog([r["a"] for r in R], [r["Omega_metric_cor"]/r["Omega_qs_Npart"] for r in R],
                  "o-", color=col, ms=3, lw=1.0, label=lab)
    a3.loglog([r["a_GR"] for r in vc], [r["ratio_GRpos_Nmass"] for r in vc], "D", color="k",
              ms=4, mfc="none", label="GR particles, equal masses")
    a3.axhspan(0.9, 1.1, color="0.92", zorder=0)
    a3.set_xlabel(r"$a$")
    a3.set_ylabel(r"$\Omega_{\rm qs}/\Omega_{\rm qs}^{\rm N}$")
    a3.legend(frameon=False, fontsize=6, loc="upper left")
    a3.text(0.96, 0.05, "(c)", transform=a3.transAxes, ha="right", va="bottom")
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
