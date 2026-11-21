#!/usr/bin/env python3
"""Test T4a of work package newton2: figure and summary of the deformed ball written by
problems/newton/make_ic.py (--axes, --vgrad, --rotate) next to the particle file of Track
A's make_deformed_ball.py for the same parameters (the comparison itself is done by
cases.py t4a, file t4a.json).

    t4a_generator.py --run RUNDIR_OF_cases.py_t4a [--out DIR]

Writes DIR/t4a_generator.{png,pdf} (projections of positions and velocities of both
files, with and without the rotation of the lattice) and DIR/t4a_generator.json.
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
from nrpic import io as nio  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    res = json.load(open(os.path.join(a.run, "t4a.json")))
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.4))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.19, top=0.93, wspace=0.42)
    for k, label in enumerate(("plain", "rot3")):
        xa, ua, ma, _ = nio.read_nrp(os.path.join(a.run, "a_%s.nrp" % label))
        xb, ub, mb, _ = nio.read_nrp(os.path.join(a.run, "core_%s.nrp" % label))
        ja = json.load(open(os.path.join(a.run, "a_%s.json" % label)))
        jb = json.load(open(os.path.join(a.run, "core_%s.json" % label)))
        sl = np.abs(xa[:, 2]) < 0.5*np.abs(xa[:, 2]).max()/10.0
        ax = axs[2*k]
        ax.plot(xa[sl, 0], xa[sl, 1], ".", ms=2.5, color=fs.PAL["blue"], label="track A",
                rasterized=True)
        ax.plot(xb[sl, 0], xb[sl, 1], ".", ms=1.0, color=fs.PAL["red"], label="core",
                rasterized=True)
        ax.set_aspect("equal")
        ax.set_xlabel(r"$x$", labelpad=-1)
        ax.set_ylabel(r"$y$", labelpad=-2)
        ax.set_title("%s: thin slab" % ("aligned" if k == 0 else "rotated"), fontsize=9)
        if k == 0:
            ax.legend(fontsize=7, loc="upper right", markerscale=3, handletextpad=0.1)
        ax = axs[2*k + 1]
        for d, col in zip(range(3), (fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"])):
            ax.plot(xb[::37, d], ub[::37, d], ".", ms=1.5, color=col, rasterized=True,
                    label=r"$i = %s$" % "xyz"[d])
        ax.set_xlabel(r"$x_i$", labelpad=-1)
        ax.set_ylabel(r"$v_i$", labelpad=-2)
        if k == 0:
            ax.legend(fontsize=7, loc="upper left", markerscale=4, handletextpad=0.1)
        res[label].update(identical_bytes=bool(open(os.path.join(a.run, "a_%s.nrp" % label), "rb").read()
                                               == open(os.path.join(a.run, "core_%s.nrp" % label), "rb").read()),
                          semi_axes_core=jb.get("semi_axes"),
                          semi_axes_track=ja.get("semi_axes_start"),
                          centre_of_mass=float(np.abs((mb[:, None]*xb).sum(axis=0)).max()/mb.sum()),
                          net_momentum=float(np.abs((mb[:, None]*ub).sum(axis=0)).max()/mb.sum()))
    fs.save(fig, os.path.join(a.out, "t4a_generator"))
    with open(os.path.join(a.out, "t4a_generator.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
