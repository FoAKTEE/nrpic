#!/usr/bin/env python3
"""Coordinate radius of the six massless tracers of problems/puncture/horizon_calib.athinput
in two runs of the same input: the D-pre-4 run with the release card executable and the
earlier run runs/puncture/single_v3 (docs/TESTLOG.md tracer test).

    tracer_check.py --out DIR NEW_TRAJ OLD_TRAJ

traj.bin: float64 records (time, tag, x^i, u_i) (docs/FORMATS.md:42). The tracers carry no
mass and are not deposited, so they do not act on the spacetime; this is a side check.
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/python")
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

NAMES = ["circular r=6", "circular r=8", "circular r=10", "inclined r=8", "plunge from 12",
         "radial infall from 10"]


def load(p):
    a = np.fromfile(p, dtype="<f8").reshape(-1, 8)
    return {k: a[a[:, 1] == k] for k in range(6)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("new")
    ap.add_argument("old")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fs.use_style()
    new, old = load(a.new), load(a.old)
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 4.6), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.11, wspace=0.28, hspace=0.0)
    for k, ax in enumerate(axs.ravel()):
        for d, c, lab in ((old, fs.PAL["blue"], "single_v3 (earlier executable)"),
                          (new, fs.PAL["red"], "D-pre-4 M/8 (release card executable)")):
            b = d[k]
            if len(b):
                r = np.linalg.norm(b[:, 2:5], axis=1)
                ax.semilogy(b[:, 0], r, color=c, label=lab)
                print(f"{lab:40s} tag {k}: records {len(b)}, t_last {b[-1, 0]:.2f}, "
                      f"r(0) {r[0]:.3f}, r(t_last) {r[-1]:.3f}")
        ax.text(0.04, 0.92, NAMES[k], transform=ax.transAxes, fontsize=8, va="top")
        ax.set_ylim(0.1, 300)
        if k >= 3:
            ax.set_xlabel(r"$t/M$")
        if k % 3 == 0:
            ax.set_ylabel(r"coordinate radius $/M$")
    axs[0, 0].legend(fontsize=7, loc="lower right")
    os.makedirs(a.out, exist_ok=True)
    print("\n".join(fs.save(fig, os.path.join(a.out, "tracer_check"))))


if __name__ == "__main__":
    main()
