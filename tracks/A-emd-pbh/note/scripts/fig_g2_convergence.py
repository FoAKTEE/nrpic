"""Convergence of the expanding ball's horizon times (gate G2, items C2, C7, C11).

Reads convergence.json of the registered analysis CONV (conv_ball, checked against its
sha256sums.txt): the error of the first detection time of the apparent horizon, ddet, and of
the trapping time of the core edge, dtrap, against the time-reversed Oppenheimer-Snyder
solution (units of the ball mass M), in three legs: (a) mesh spacing h at one particle per
cell, (b) particles per cell on meshes A and B, (c) outer boundary L = 16 M against 32 M and
ball radius R (in units of the fiducial radius) on meshes A and B.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

common.RUNS["conv"] = "A-20261121-120257-a2eb839"
STEM = "fig_g2_convergence"


def main():
    out = common.out_dir("figures")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    legs = common.load_json("conv", "convergence.json")["legs"]
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.6))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.2, top=0.93, wspace=0.34)
    cb, cr = fs.PAL["blue"], fs.PAL["red"]
    m = legs["mesh"]
    h = np.array(m["x"])
    for q, c, lab in (("ddet", cb, r"$|\Delta t_{\rm det}|$"), ("dtrap", cr, r"$|\Delta t_{\rm trap}|$")):
        v = np.abs(m[q]["values"])
        ax[0].loglog(h, v, "o-", color=c, ms=4, label=lab)
    ref = abs(m["ddet"]["values"][-1])
    ax[0].loglog(h, ref * (h / h[-1]) ** 2, **fs.GUIDE, label=r"$\propto h^2$")
    ax[0].loglog(h, ref * (h / h[-1]), color="k", lw=1.0, ls=":", label=r"$\propto h$")
    fs.no_minor_labels(ax[0], "x")
    ax[0].set_xticks(h)
    ax[0].set_xticklabels([r"$1/64$", r"$1/32$", r"$1/16$"])
    ax[0].set_xlabel(r"cell size $h/M$")
    ax[0].set_ylabel(r"time error $/M$")
    ax[0].legend(frameon=False, fontsize=7, loc="lower right")
    ax[0].set_title("(a) mesh", fontsize=8)
    for key, mk, lab in (("N", "o", "mesh A"), ("NB", "s", "mesh B")):
        L = legs[key]
        n = np.array(L["x"])
        ax[1].semilogx(n, np.abs(L["ddet"]["values"]), marker=mk, ls="-", color=cb, ms=4, label=f"{lab}, det")
        ax[1].semilogx(n, np.abs(L["dtrap"]["values"]), marker=mk, ls="--", color=cr, ms=4, label=f"{lab}, trap")
    ax[1].set_xlabel("particles per cell")
    ax[1].set_ylabel(r"time error $/M$")
    ax[1].set_ylim(0, 0.3)
    ax[1].legend(frameon=False, fontsize=6, ncol=2, loc="upper right")
    ax[1].set_title("(b) particle number", fontsize=8)
    for key, mk, lab in (("R", "o", "mesh A"), ("RB", "s", "mesh B")):
        L = legs[key]
        ax[2].plot(L["x"], np.abs(L["ddet"]["values"]), marker=mk, ls="-", color=cb, ms=4, label=f"radius, {lab}")
    for key, mk in (("L", "o"), ("LB", "s")):
        L = legs[key]
        ax[2].plot([1.0, 1.0], np.abs(L["ddet"]["values"]), marker=mk, ls="none", mfc="none", color="k", ms=7)
    ax[2].plot([], [], "o", mfc="none", color="k", label=r"boundary $16M$, $32M$")
    ax[2].set_xlabel(r"ball radius $R/R_0$")
    ax[2].set_ylabel(r"$|\Delta t_{\rm det}|/M$")
    ax[2].set_ylim(0, None)
    ax[2].legend(frameon=False, fontsize=6, loc="lower right")
    ax[2].set_title("(c) radius and boundary", fontsize=8)
    fs.save(fig, os.path.join(out, STEM))
    for k in ("mesh", "N", "NB", "R", "RB", "L", "LB"):
        L = legs[k]
        print(f"{STEM}: leg {k}: x = {L['x']}, ddet = {[round(v, 4) for v in L['ddet']['values']]}, "
              f"dtrap = {[round(v, 4) for v in L['dtrap']['values']]}")
    common.report_checks(STEM)


if __name__ == "__main__":
    main()
