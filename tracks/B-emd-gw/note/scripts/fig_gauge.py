"""Figure: the spatial gauge of the flat TT projection, two gauges of the same run (note v1, G1).

eps = 1, 64^3: zero shift and a Gamma-driver shift with the same slicing condition.
(a) c_+(K1)/s in both gauges, as projected (solid) and after removing the second-order
spatial-gauge piece G_tot of each dump (dashed). (b) Difference of c_+ between the two gauges
over |s|: as projected, after G_tot, and after the quadratic piece G alone (without the cross
terms with the TT part and the homogeneous anisotropy of the box). (c) Relative difference
between the gauges at K1 in the double-precision dumps: the flat TT strain and the magnetic
Weyl part (sine part of the x amplitude). Sources: B-20261115-180834-c77a132 (per-dump
diagnostics of the card runs B-20261115-165353-b592d43).
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402
import g1data as g  # noqa: E402

STEM = "fig_gauge"


def main():
    out = common.out_dir("figures")
    cz.use_style()
    s1 = g.s_static(1.0)
    a_x = 1.0 + 1.0 / g.DELTA
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(3.4, 6.6))
    fig.subplots_adjust(left=0.20, right=0.965, top=0.99, bottom=0.07, hspace=0.36)

    tz, a, cz0 = g.amplitude("cw_eps1")
    tg, _, cg0 = g.amplitude("cw_eps1_gd")
    _, _, gz = g.series("cw_eps1", "Gtot_K1_plus", 0)
    _, _, gg = g.series("cw_eps1_gd", "Gtot_K1_plus", 0)
    _, _, qz = g.series("cw_eps1", "G_K1_plus", 0)
    _, _, qg = g.series("cw_eps1_gd", "G_K1_plus", 0)
    iz, ig = g.common_dumps(tz, tg)
    a = a[iz]
    blue, green = cz.PAL["blue"], cz.PAL["green"]
    a1.plot(a, cz0[iz] / s1, color=blue, lw=1.2, label="zero shift")
    a1.plot(a, cg0[ig] / s1, color=green, lw=1.2, label="driven shift")
    a1.plot(a, (cz0[iz] - gz[iz]) / s1, "--", color=blue, lw=1.0, label=r"zero shift, minus $G_{\rm tot}$")
    a1.plot(a, (cg0[ig] - gg[ig]) / s1, "--", color=green, lw=1.0, label=r"driven shift, minus $G_{\rm tot}$")
    a1.set_xscale("log")
    a1.set_ylabel(r"$c_+/s$, $\epsilon=1$")
    a1.set_ylim(0, 2.8)
    a1.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.8)

    raw = (cz0[iz] - cg0[ig]) / s1
    cor = ((cz0[iz] - gz[iz]) - (cg0[ig] - gg[ig])) / s1
    quad = ((cz0[iz] - qz[iz]) - (cg0[ig] - qg[ig])) / s1
    sel = a > 1.05
    a2.loglog(a[sel], np.abs(raw[sel]), color="k", lw=1.2, label="as projected")
    a2.loglog(a[sel], np.abs(cor[sel]), "--", color=cz.PAL["red"], lw=1.0, label=r"minus $G_{\rm tot}$")
    a2.loglog(a[sel], np.abs(quad[sel]), ":", color=cz.PAL["yellow"], lw=1.2,
              label=r"minus quadratic piece only")
    a2.set_ylabel(r"gauge difference of $c_+$ over $|s|$")
    a2.set_ylim(1e-7, 30)
    a2.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.8)

    q = g.gauge_numbers()
    wa, dB, dh = np.array(q["weyl_a"]), np.array(q["weyl_dB"]), np.array(q["weyl_dh"])
    sel = wa > 1.5
    a3.loglog(wa[sel], dh[sel], "s-", color="k", ms=3.5, mfc="none", lw=0.8, label="flat TT strain")
    a3.loglog(wa[sel], dB[sel], "o-", color=cz.PAL["red"], ms=3.5, lw=0.8, label="magnetic Weyl part")
    a3.set_ylabel("relative gauge difference")
    a3.set_ylim(1e-5, 5)
    a3.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.8)

    for x, lab in ((a1, "(a)"), (a2, "(b)"), (a3, "(c)")):
        x.axvline(a_x, color="grey", lw=1.0, ls=":")
        x.set_xlim(1, 145)
        x.set_xlabel(r"scale factor $a$")
        x.text(0.96, 0.05, lab, transform=x.transAxes, ha="right", va="bottom")
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
