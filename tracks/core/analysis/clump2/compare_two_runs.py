#!/usr/bin/env python3
"""Test M2 of tracks/core/JOURNAL-clump2.md: the histories of two runs of one input (two
executables, or two runs of one) at their common records.

    compare_two_runs.py --a RUN_ID/name --b RUN_ID/name [--tsplit 10] [--out DIR]

Differences a - b of the minimum lapse, sum m u_x, sum m W, the number of particles and
the relative differences of the H-norm and M-norm, as maxima up to --tsplit and over the
whole common time. Writes compare_two_runs.json and fig_compare_two_runs.{pdf,png}.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, HERE)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from card_vs_cpu import compare_history  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--tsplit", type=float, default=10.0)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    o, t, tz, d = compare_history(os.path.join(SCRATCH, a.a), os.path.join(SCRATCH, a.b))
    res = dict(a=a.a, b=a.b, whole=o, tsplit=a.tsplit, early={})
    for k, v in d.items():
        tt = tz if k in ("H", "M") else t
        res["early"][k] = float(np.max(np.abs(v[tt <= a.tsplit + 1e-9])))
    print(json.dumps(res, indent=1))
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.10, right=0.985, bottom=0.16, top=0.95, wspace=0.30)
    cols = fs.series_colors(3)
    for c, (k, lab) in zip(cols, (("alpha_min", r"$\alpha_{\min}$"),
                                  ("sum_mux", r"$\sum m u_x$"), ("sum_mW", r"$\sum m W$"))):
        ax[0].plot(t, np.maximum(np.abs(d[k]), 1e-17), color=c, label=lab)
    ax[0].set_yscale("log")
    ax[0].set_xlabel(r"$t/M$")
    ax[0].set_ylabel("|difference of the two runs|")
    ax[0].legend(loc="lower right", fontsize=8)
    for c, (k, lab) in zip(cols, (("H", "H-norm"), ("M", "M-norm"))):
        ax[1].plot(tz, np.maximum(np.abs(d[k]), 1e-17), color=c, label=lab)
    ax[1].set_yscale("log")
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel("|relative difference|")
    ax[1].legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_compare_two_runs"))
    with open(os.path.join(a.out, "compare_two_runs.json"), "w") as f:
        json.dump(res, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
