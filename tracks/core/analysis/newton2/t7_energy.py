#!/usr/bin/env python3
"""Test T7 of work package newton2 (question of Track A): is the drift of the energy of
the Newtonian mode at shell crossing an error of the time integration or of the space
discretisation?  Plane wave of problems/newton (N = 32, crossing at a = 4) at the step
0.005 and at half of it, for the multigrid solver, the Fourier solver with the spectral
symbol, and the spectral solver with the cubic cloud and the cubic-spline gather.

    t7_energy.py --t1 RUNDIR_OF_cases.py_t1 --run RUNDIR_OF_cases.py_t7 [--out DIR]

Measure: largest |C - C_0| of the Layzer-Irvine combination (column 8 of
<basename>.newton.hst) before the crossing (a < 4) and over the run, in units of the
largest a|W|; the same for W_mesh in place of W.  Writes DIR/t7_energy.json and
DIR/t7_energy.{png,pdf}.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t1", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    cases = {"mg": [("dt", os.path.join(a.t1, "mg")), ("dt/2", os.path.join(a.run, "w32_dth_mg"))],
             "spectral": [("dt", os.path.join(a.t1, "fftsp")),
                          ("dt/2", os.path.join(a.run, "w32_dth_sp"))],
             "spectral, pcs + spline": [("dt", os.path.join(a.run, "w32_dt1_sp_pcs")),
                                        ("dt/2", os.path.join(a.run, "w32_dth_sp_pcs"))]}
    cols = {"mg": fs.PAL["red"], "spectral": fs.PAL["blue"],
            "spectral, pcs + spline": fs.PAL["green"]}
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.15, top=0.95, wspace=0.26)
    res = {}
    for name, runs in cases.items():
        res[name] = {}
        for lab, d in runs:
            h = nw.read_newton_hst(os.path.join(d, "newton.newton.hst"))
            aa = h["a"]
            scale = np.max(np.abs(aa*h["W"]))
            li = (h["C"] - h["C"][0])/scale
            cm = aa*(h["K"] + h["W_mesh"]) + h["int_K_da"]
            lim = (cm - cm[0])/scale
            pre = aa < 4.0
            res[name][lab] = dict(steps=int(len(aa) - 1), dt=float(h["dt"][1]),
                                  before=float(np.max(np.abs(li[pre]))),
                                  whole=float(np.max(np.abs(li))),
                                  end=float(li[-1]),
                                  before_mesh=float(np.max(np.abs(lim[pre]))),
                                  whole_mesh=float(np.max(np.abs(lim))))
            axs[0].plot(aa, li, color=cols[name], ls="-" if lab == "dt" else "--",
                        lw=1.5 if lab == "dt" else 1.0,
                        label=name if lab == "dt" else None)
            axs[1].semilogy(aa[1:], np.maximum(np.abs(li[1:]), 1e-12), color=cols[name],
                            ls="-" if lab == "dt" else "--", lw=1.5 if lab == "dt" else 1.0)
        r = res[name]
        r["ratio_before"] = r["dt"]["before"]/r["dt/2"]["before"]
        r["ratio_whole"] = r["dt"]["whole"]/r["dt/2"]["whole"]
    for ax in axs:
        ax.axvline(4.0, color="0.5", alpha=0.4, lw=1.0)
        ax.set_xlabel(r"$a$", labelpad=-1)
    axs[0].set_ylabel(r"$(C - C_0)/\max(a|W|)$")
    axs[1].set_ylabel(r"$|C - C_0|/\max(a|W|)$")
    axs[1].set_ylim(1e-9, 1e-1)
    axs[0].legend(loc="lower left", fontsize=8)
    axs[0].text(0.04, 0.93, "solid: step 0.005; dashed: 0.0025", transform=axs[0].transAxes,
                fontsize=8)
    fs.save(fig, os.path.join(a.out, "t7_energy"))
    with open(os.path.join(a.out, "t7_energy.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
