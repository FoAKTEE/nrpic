#!/usr/bin/env python3
"""T3c of the work package cosmo-amr: clouds of the three shapes on the finest level of a
static patch in the homogeneous universe (T2's D8 deck; prediction:
tracks/core/JOURNAL-cosmo-amr.md).

    t3c_shapes.py --new NEW_EXE --t2 T2_RUNDIR --out DIR [--cores N]

Writes DIR/t3c_summary.json and DIR/fig_t3c_shapes.{pdf,png}."""
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
    ap.add_argument("--cores", type=int, default=3)
    a = ap.parse_args()
    a.out, a.new = os.path.abspath(a.out), os.path.abspath(a.new)
    base = A.Inp(os.path.join(a.t2, "D8", "flrw.athinput"))
    base.set("time", nlim=4)
    cs = {s: base.copy().set("particles", deposit_shape=s) for s in ("cic", "tsc", "pcs")}
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
        hist[n] = (h["time"], es, s["time"], s["Hr_max"])
        print(n, rc[0], "E spread t0 %.3g end %.3g  Hr_max t0 %.3g  identity %.2g"
              % (es[0], es[-1], s["Hr_max"][0], res[n]["identity_E"]), flush=True)
    with open(os.path.join(a.out, "t3c_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.95, wspace=0.30)
    for i, n in enumerate(hist):
        t, es, ts, hr = hist[n]
        ax[0].semilogy(t, np.maximum(es, 1e-17), "o-", ms=3, color=fs.SERIES[i], label=n)
        ax[1].semilogy(ts, np.maximum(hr, 1e-17), "o-", ms=3, color=fs.SERIES[i], label=n)
    ax[0].set_ylabel(r"$E_{\max}/E_{\min}-1$")
    ax[1].set_ylabel(r"largest relative $|H|$")
    for q in ax:
        q.set_xlabel("conformal time")
        q.legend(frameon=False)
    fs.save(fig, os.path.join(a.out, "fig_t3c_shapes"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
