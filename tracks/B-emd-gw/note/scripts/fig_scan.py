"""Figure: the crossed waves in full relativity against the second-order strain (note v1, G1).

(a) c_+(K1)/(s eps) against the scale factor for eps = 0.1, 0.3, 1 (64^3), with the
second-order reference g(tau) from conformally flat data (computed in g1data, independently
of the helper's code). (b) |c_+/(s eps g) - 1|, the departure from the second-order value.
(c) |c_+(32^3)/c_+(64^3) - 1| at the 64^3 dump times (32^3 interpolated in tau). (d) The null
eps = 0: largest TT amplitude of h at any nonzero wave vector in the single- and
double-precision dumps. Dotted: a = 1 + 1/delta, the first shell crossing of the Zel'dovich
plane wave of the x wave. Sources: per-dump diagnostics B-20261115-174722-ba1048d,
B-20261115-180834-c77a132 (64^3), B-20261115-184650-2d155b6 (32^3) of the card runs
B-20261115-164059-d802e82, -165353-b592d43 and the processor runs -165525-f7c2004.
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402
import g1data as g  # noqa: E402

STEM = "fig_scan"
COL = {"cw_eps0p1": cz.PAL["yellow"], "cw_eps0p3": cz.PAL["red"], "cw_eps1": cz.PAL["blue"],
       "cw_eps1_gd": cz.PAL["green"]}
LAB = {"cw_eps0p1": r"$\epsilon=0.1$", "cw_eps0p3": r"$\epsilon=0.3$", "cw_eps1": r"$\epsilon=1$"}


def main():
    out = common.out_dir("figures")
    cz.use_style()
    a_x = 1.0 + 1.0 / g.DELTA
    fig, ax = plt.subplots(2, 2, figsize=(7.0, 4.9))
    fig.subplots_adjust(left=0.095, right=0.985, top=0.985, bottom=0.095, wspace=0.28, hspace=0.30)
    (a1, a2), (a3, a4) = ax

    tt = np.linspace(0.0, 2.0 * (np.sqrt(140.0) - 1.0), 3000)
    a1.plot(g.a_of_tau(tt), g.g_ref(tt), **cz.GUIDE, label="second order")
    for name in ("cw_eps0p1", "cw_eps0p3", "cw_eps1"):
        t, a, c = g.amplitude(name)
        a1.plot(a, c / g.s_static(g.EPS[name]), color=COL[name], lw=1.2, label=LAB[name])
        ad, d = g.departure(name)
        a2.loglog(ad, np.abs(d), color=COL[name], lw=1.0, label=LAB[name])
    a1.set_xscale("log")
    a1.set_xlabel(r"scale factor $a$")
    a1.set_ylabel(r"$c_+/(s\,\epsilon)$")
    a1.set_ylim(0, 2.8)
    a1.legend(frameon=False, loc="upper left", fontsize=7.5, handlelength=1.8)
    a2.set_xlabel(r"scale factor $a$")
    a2.set_ylabel("departure from second order")
    a2.set_ylim(1e-5, 3)

    for name in ("cw_eps0p1", "cw_eps0p3", "cw_eps1", "cw_eps1_gd"):
        t6, a6, c6 = g.amplitude(name, 64)
        t3, _, c3 = g.amplitude(name, 32)
        i6 = np.nonzero((t6 >= t3.min()) & (t6 <= t3.max()) & (t6 > 0))[0]
        r = g.CubicSpline(t3, c3)(t6[i6]) / c6[i6] - 1.0
        lab = LAB.get(name, r"$\epsilon=1$, driven shift")
        ls = "--" if name == "cw_eps1_gd" else "-"
        a3.loglog(a6[i6], np.abs(r), ls, color=COL[name], lw=1.0, label=lab)
    a3.set_xlabel(r"scale factor $a$")
    a3.set_ylabel(r"$|c_+(32^3)/c_+(64^3)-1|$")
    a3.set_ylim(1e-7, 1)
    a3.legend(frameon=False, loc="upper left", fontsize=7.5, handlelength=1.8)

    for kind, mk, lab in (("bin", "-", "single-precision dumps"), ("rst", "o", "double-precision dumps")):
        t, a, m = g.series("cw_eps0", "max_TT_mode", kind=kind)
        sel = t > 0
        a4.semilogy(a[sel], m[sel], mk, color="k", lw=0.8, ms=3.5, mfc="none", label=lab)
    _, a, c = g.amplitude("cw_eps0p1")
    a4.semilogy(a[1:], np.abs(c[1:]), color=COL["cw_eps0p1"], lw=1.0, label=r"$|c_+|$, $\epsilon=0.1$")
    a4.set_xscale("log")
    a4.set_xlabel(r"scale factor $a$")
    a4.set_ylabel(r"largest TT amplitude, $\epsilon=0$")
    a4.set_ylim(1e-17, 1e-2)
    a4.legend(frameon=False, loc="center right", fontsize=7.5, handlelength=1.8)

    for x, lab, y, va in ((a1, "(a)", 0.05, "bottom"), (a2, "(b)", 0.95, "top"),
                          (a3, "(c)", 0.05, "bottom"), (a4, "(d)", 0.95, "top")):
        x.axvline(a_x, color="grey", lw=1.0, ls=":")
        x.set_xlim(1, 145)
        x.text(0.04 if lab == "(b)" else 0.96, y, lab, transform=x.transAxes,
               ha="left" if lab == "(b)" else "right", va=va)
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
