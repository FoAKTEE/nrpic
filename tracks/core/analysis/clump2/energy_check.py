#!/usr/bin/env python3
"""Test EN of tracks/core/JOURNAL-clump2.md: the mass that the second-order correction of
psi adds to an equilibrium cluster of momentum P = M V, against the special-relativistic
E = (M^2 + P^2)^(1/2) = M + M V^2/2 + O(V^4), for several cluster models y_c. Also the
flux balance of the monopole equation across the surface (zero for a solution; the
defect of the correction before commit baa6f99e) and the residual of the radial
equations on the solution nodes.

    energy_check.py [--yc 0.6,0.819,0.9,0.95] [--out DIR]

Writes energy_check.json and fig_energy_check.{pdf,png} into --out. Nothing is evolved.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import boosted_cluster as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yc", default="0.6,0.819,0.9,0.95")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    prof = {}
    for s in a.yc.split(","):
        yc = float(s)
        md = stc.STModel(yc)
        B = bc.BoostedST(md)
        co = B.correction()
        ratio = B.second_order_mass([1.0, 0.0, 0.0]) / (0.5 * md.M)
        r, y0 = np.asarray(co["r"]), np.asarray(co["y0"])
        # exterior of the monopole: y0 -> C/r + particular part falling as r^-2
        tail = float(r[-1] * y0[-1])
        res[s] = dict(yc=yc, M=md.M, R=md.R, rbar_s=md.rbar_s, alpha_c=md.alpha_c,
                      compactness=md.M / md.R, pmass_over_M=float(B.pmass) / md.M,
                      monopole=float(co["monopole"]),
                      added_mass_over_half_M_V2=float(ratio),
                      deviation=float(ratio - 1.0),
                      y0_centre=float(y0[0]), r_last=float(r[-1]),
                      r_y0_last_over_monopole=tail / float(co["monopole"]))
        prof[s] = (r / md.rbar_s, y0, np.asarray(co["y2"]))
        print(f"yc {yc:5.3f}  M/R {md.M / md.R:.4f}  alpha_c {md.alpha_c:.4f}  "
              f"pmass/M - 1 {float(B.pmass) / md.M - 1.0:+.2e}  "
              f"added mass/(M V^2/2) {ratio:.6f}", flush=True)

    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.95, wspace=0.28)
    cols = fs.series_colors(len(res))
    for c, s in zip(cols, res):
        x, y0, y2 = prof[s]
        w = x < 6.0
        ax[0].plot(x[w], y0[w], color=c, label=rf"$y_c = {s}$")
        ax[0].plot(x[w], y2[w], color=c, ls="--")
    ax[0].set_xlabel(r"$\bar r/\bar r_s$")
    ax[0].set_ylabel(r"$y_0$ (solid), $y_2$ (dashed)")
    ax[0].legend(loc="upper right", fontsize=8)
    cc = [res[s]["compactness"] for s in res]
    dev = [abs(res[s]["deviation"]) for s in res]
    ax[1].plot(cc, dev, "o", color=fs.PAL["red"])
    ax[1].axhline(1e-3, **fs.GUIDE)
    ax[1].set_yscale("log")
    ax[1].set_xlabel(r"compactness $M/R$")
    ax[1].set_ylabel(r"$|\,\delta M/(M V^2/2) - 1\,|$")
    fs.save(fig, os.path.join(a.out, "fig_energy_check"))

    with open(os.path.join(a.out, "energy_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
