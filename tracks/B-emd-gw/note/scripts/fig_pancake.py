"""Figure: the plane-wave pancake through shell crossing in full relativity.

(a) Largest difference between the relativistic and the Newtonian coordinate positions of
the sheets, relative to the displacement since the start, against the scale factor: box of
one initial Hubble radius at 32 and 64 cells, and the box of four Hubble radii divided by
16, the ratio of the two values of (H/k)^2. (b) Box mean of the relative Hamiltonian
constraint of the relativistic runs with one particle per cell (32, 64, 96 cells) and with
two per cell and direction (64 cells). Source: analysis run B-emd-gw-20261115-123852-ea4475c
(pancake.json) of the card runs B-emd-gw-20261115-115217-69ab1db and -115902-a3207d7 and the
Newtonian runs -115239-69ab1db.
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import czstyle as cz  # noqa: E402

STEM = "fig_pancake"


def series(d, prefix):
    pts = sorted((float(k[len(prefix):]), v) for k, v in d.items()
                 if k.startswith(prefix) and k[len(prefix):].replace(".", "").isdigit())
    return np.array([p[0] for p in pts]), np.array([p[1] for p in pts])


def main():
    out = common.out_dir("figures")
    cz.use_style()
    p = common.load_json("pancake", "pancake.json")
    a_cross = p["L1_n64"]["a_cross"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.4, 5.0))
    fig.subplots_adjust(left=0.20, right=0.96, top=0.98, bottom=0.09, hspace=0.32)

    for key, col, mk, lab, scale in (
            ("diff_L1_n32_N_n32", cz.PAL["red"], "o", "one Hubble radius, 32 cells", 1.0),
            ("diff_L1_n64_N_n64", cz.PAL["blue"], "s", "one Hubble radius, 64 cells", 1.0),
            ("diff_L4_n64_N4_n64", "k", "D", "four Hubble radii, 64 cells, / 16", 16.0)):
        a, dx = series(p[key], "dx_a")
        ax1.semilogy(a, dx/scale, "-", marker=mk, color=col, ms=4, mfc="none", lw=1.0,
                     label=lab)
    ax1.axvline(a_cross, color="grey", lw=1.0, ls=":")
    ax1.set_xlabel(r"scale factor $a$")
    ax1.set_ylabel("relativistic minus Newtonian")
    ax1.set_xlim(0, 44)
    ax1.set_ylim(6e-4, 1.5e-2)
    ax1.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.6)
    ax1.text(0.97, 0.07, "(a)", transform=ax1.transAxes, ha="right", va="bottom")

    for key, col, ls, lab in (("constraints_L1_n32", cz.PAL["red"], "-", "one per cell, 32 cells"),
                              ("constraints_L1_n64", cz.PAL["blue"], "-", "one per cell, 64 cells"),
                              ("constraints_L1_n96", cz.PAL["yellow"], "-", "one per cell, 96 cells"),
                              ("constraints_L1_n64_p2", "k", "--", "two per cell and direction, 64 cells")):
        h = p[key]["Hr_mean"]
        a = np.array([float(k) for k in h])
        v = np.array(list(h.values()))
        o = np.argsort(a)
        ax2.semilogy(a[o], v[o], ls, color=col, marker="o", ms=3, lw=1.0, label=lab)
    ax2.axvline(a_cross, color="grey", lw=1.0, ls=":")
    ax2.set_xlabel(r"scale factor $a$")
    ax2.set_ylabel(r"mean relative $|\mathcal{H}|$")
    ax2.set_xlim(0, 44)
    ax2.legend(frameon=False, loc="lower right", fontsize=7, handlelength=1.6)
    ax2.text(0.03, 0.93, "(b)", transform=ax2.transAxes, ha="left", va="top")
    cz.save(fig, os.path.join(out, STEM))


if __name__ == "__main__":
    main()
