#!/usr/bin/env python3
"""Figures of Test 3 from knudsen.json (knudsen.py).

    python3 fig_knudsen.py --run DIR_OF_knudsen --out FIGDIR
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evstatic  # noqa: E402,F401  (puts python/ on the path)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402

COL = {"king": fs.PAL["blue"], "poly05": fs.PAL["red"], "arshell": fs.PAL["green"]}
LAB = {"king": "King", "poly05": "polytrope $k=1/2$", "arshell": "shell $L_0=0.1$"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    fs.use_style()
    K = json.load(open(os.path.join(a.run, "knudsen.json")))
    N = K["N"]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.6))
    # left: Kn against sigma~ for every model
    ax = fig.add_axes([0.08, 0.14, 0.40, 0.78])
    sig = np.logspace(0, 5, 200)
    seen = set()
    for m in K["models"]:
        f = m["family"]
        thr = "threshold" in m["role"]
        ax.loglog(sig, m["Kn_times_sigma_tilde"] / sig, color=COL[f], lw=1.5 if thr else 0.7,
                  alpha=1.0 if thr else 0.6, label=LAB[f] if f not in seen else None)
        seen.add(f)
    for kn in (10, 0.01):
        ax.axhline(kn, **fs.GUIDE)
    ax.axhspan(0.01, 10, color="grey", alpha=0.08)
    ax.set_xlabel("$\\tilde\\sigma=(\\sigma/m)/M$")
    ax.set_ylabel("Kn $=\\ell_c/H_c$")
    ax.set_ylim(3e-4, 300)
    ax.legend(loc="upper right", fontsize=8)
    ax.text(0.03, 0.04, "thick: threshold models; thin: the other 10\nshaded: Kn = 10 ... 0.01",
            transform=ax.transAxes, fontsize=7)
    # right: collisions per particle per t_d and resolution at N = 1e4, threshold models
    ax = fig.add_axes([0.58, 0.14, 0.40, 0.78])
    for m in K["models"]:
        if "threshold" not in m["role"]:
            continue
        f = m["family"]
        kn = np.array([r["Kn"] for r in m["rows"]])
        ax.loglog(kn, [r["nu_c"] for r in m["rows"]], "-o", color=COL[f], ms=3,
                  label=f"{LAB[f]}: $\\nu_c$")
        ax.loglog(kn, [r["nu_bar"] for r in m["rows"]], "--s", color=COL[f], ms=3, mfc="none",
                  label=f"$\\bar\\nu$")
        ax.loglog(kn, [r["l_over_d"] for r in m["rows"]], ":", color=COL[f], lw=1.0,
                  label=f"$\\ell_c/d_c$ ($N=10^{{{int(np.log10(N))}}}$)")
    ax.axhline(1.0, **fs.MASK_LINE)
    ax.set_xlabel("Kn")
    ax.set_ylabel("per particle per $t_d$; $\\ell_c/d_c$")
    ax.invert_xaxis()
    ax.legend(loc="upper left", fontsize=6, ncol=3)
    ax.set_ylim(1e-2, 3e4)
    fs.save(fig, os.path.join(a.out, "knudsen_conversion"))
    # profiles of the local rate and of v_Mol/<v>
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax1 = fig.add_axes([0.08, 0.16, 0.40, 0.76])
    ax2 = fig.add_axes([0.58, 0.16, 0.40, 0.76])
    for m in K["models"]:
        if "threshold" not in m["role"]:
            continue
        f = m["family"]
        pr = m["profile"]
        rb = np.array(pr["rbar"])
        rate = np.array(pr["alpha"]) * np.array(pr["rho0"]) * np.array(pr["vmol"])
        ax1.semilogy(rb, rate, "-o", color=COL[f], ms=2.5, label=LAB[f])
        ax2.plot(rb, np.array(pr["vmol"]) / np.array(pr["mean_speed"]), "-o", color=COL[f], ms=2.5,
                 label=LAB[f])
    ax1.set_xlabel("$\\bar r/M$")
    ax1.set_ylabel("$\\alpha\\,\\rho_0\\langle v_{\\rm M\\o l}\\rangle=\\alpha\\Gamma/\\tilde\\sigma$")
    ax1.legend(loc="lower left", fontsize=8)
    ax2.axhline(np.sqrt(2.0), **fs.GUIDE)
    ax2.set_xlabel("$\\bar r/M$")
    ax2.set_ylabel("$\\langle v_{\\rm M\\o l}\\rangle/\\langle v\\rangle$")
    ax2.text(0.97, 0.06, "dashed: $\\sqrt{2}$ (Newtonian Maxwellian)", transform=ax2.transAxes,
             ha="right", fontsize=8)
    ax2.legend(loc="center right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "knudsen_profiles"))
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
