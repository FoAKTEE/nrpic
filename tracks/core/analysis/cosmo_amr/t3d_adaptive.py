#!/usr/bin/env python3
"""T3d of the work package cosmo-amr: the density-adaptive cloud level
(<particles> deposit_adaptive) with clouds of the three shapes at a level boundary, in
the homogeneous universe with a static patch (T2's D8 deck: eight particles per root
cell, i.e. one per cell of the patch; prediction: tracks/core/JOURNAL-cosmo-amr.md).

    t3d_adaptive.py --new NEW_EXE --t2 T2_RUNDIR --out DIR [--cores N]

  <shape>_p2    deposit_ppc = 2: the adaptive level is the root everywhere (eight
                particles per root cell, one per cell of the patch)
  <shape>_p05   deposit_ppc = 0.5: the adaptive level is level 1 where the mesh has it
  <shape>_p2f   as _p2 with deposit_fine_shape
Writes DIR/t3d_summary.json and DIR/fig_t3d_adaptive.{pdf,png}."""
import argparse
import json
import os
import sys

import numpy as np

import amrlib as A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--t2", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=2)
    a = ap.parse_args()
    a.out, a.new = os.path.abspath(a.out), os.path.abspath(a.new)
    base = A.Inp(os.path.join(a.t2, "D8", "flrw.athinput"))
    base.set("time", nlim=4)
    cs = {}
    for s in ("cic", "tsc", "pcs"):
        cs[s + "_p2"] = base.copy().set("particles", deposit_shape=s, deposit_adaptive=True,
                                        deposit_ppc=2.0)
        cs[s + "_p05"] = base.copy().set("particles", deposit_shape=s, deposit_adaptive=True,
                                         deposit_ppc=0.5)
        cs[s + "_p2f"] = base.copy().set("particles", deposit_shape=s, deposit_adaptive=True,
                                         deposit_ppc=2.0, deposit_fine_shape=True)
    rcs = A.run_many([(a.new, cs[n], os.path.join(a.out, n), "flrw", (), None)
                      for n in cs], a.cores)
    res, hist = {}, {}
    for n, rc in zip(cs, rcs):
        h = A.read_hst(os.path.join(a.out, n, "flrw.nrpic.hst"))
        s = A.read_hst(os.path.join(a.out, n, "flrw.cstat.hst"))
        es = h["E_max"]/h["E_min"] - 1.0
        res[n] = dict(exit=rc[0], E_spread=[float(v) for v in es],
                      Hr_max=[float(v) for v in s["Hr_max"]],
                      identity_E=float(np.max(np.abs(h["int_E"]/h["sum_mW"] - 1.0))))
        hist[n] = (h["time"], es)
        print(n, rc[0], "E spread t0 %.3g end %.3g  Hr_max t0 %.3g  identity %.2g"
              % (es[0], es[-1], s["Hr_max"][0], res[n]["identity_E"]), flush=True)
    with open(os.path.join(a.out, "t3d_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(5.0, 3.2))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.26, top=0.95)
    names = list(cs)
    x = np.arange(len(names))
    col = {"cic": fs.SERIES[0], "tsc": fs.SERIES[1], "pcs": fs.SERIES[3]}
    for i, n in enumerate(names):
        t, es = hist[n]
        ax.semilogy([x[i]], [max(es[0], 1e-17)], "o", color=col[n.split("_")[0]])
        ax.semilogy([x[i]], [max(np.max(es), 1e-17)], "x", color=col[n.split("_")[0]])
    ax.axhline(1e-12, **fs.GUIDE)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=60, fontsize=7)
    ax.set_ylabel(r"$E_{\max}/E_{\min}-1$ (o: $t=0$, x: largest)")
    fs.save(fig, os.path.join(a.out, "fig_t3d_adaptive"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
