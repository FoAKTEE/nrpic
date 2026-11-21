#!/usr/bin/env python3
"""Figures of two small card tests of the closing session of coll2 (JOURNAL-coll2.md,
2026-11-19): Ct, the step time of the cluster deck per mode, and X, the smoke deck run by
the repaired incremental card build against the clean build.

  fig_close.py OUT --steptime RUNDIR [--wave1 LOG ...] --x NEWDIR REFDIR

Ct: seconds per step = "cpu time used" / number of cycles from each RUNDIR/<name>/athena.log
(and from the wave-1 logs given with --wave1: the same deck over 1200 steps).
X: the collision history of NEWDIR/static and REFDIR/static, column by column.
Writes OUT/close.json, OUT/fig_steptime.png, OUT/fig_smoke_x.png.
"""
import argparse
import filecmp
import json
import os
import re

import numpy as np

import common
from nrpic import collide


def step_time(log):
    txt = open(log).read()
    cpu = float(re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt).group(1))
    ncyc = int(re.findall(r"cycle=(\d+)", txt)[-1])
    return cpu/ncyc, ncyc, cpu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--steptime", required=True)
    ap.add_argument("--wave1", nargs="*", default=[])
    ap.add_argument("--x", nargs=2, required=True)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    res = {"steptime": {}, "wave1": {}, "x": {}}
    for name in ("off", "kn3_cell", "kn3_particle"):
        s, n, c = step_time(os.path.join(args.steptime, name, "athena.log"))
        res["steptime"][name] = dict(s_per_step=s, cycles=n, cpu_s=c)
    for lg in args.wave1:
        s, n, c = step_time(lg)
        res["wave1"][lg] = dict(s_per_step=s, cycles=n, cpu_s=c)
    new, ref = args.x
    files = {}
    for f in ("static/box.coll.hst", "static/box.nrpic.hst", "static/box.part.00000.bin",
              "pert/pert.part.00000.bin", "pert/pert.part.00001.bin"):
        files[f] = bool(filecmp.cmp(os.path.join(new, f), os.path.join(ref, f), shallow=False))
    res["x"]["files_identical"] = files
    hn = collide.read_history(os.path.join(new, "static", "box.coll.hst"))
    hr = collide.read_history(os.path.join(ref, "static", "box.coll.hst"))
    res["x"]["n_coll"] = [hn["n_coll"].tolist(), hr["n_coll"].tolist()]
    with open(os.path.join(out, "close.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.2, top=0.95)
    names = list(res["steptime"])
    ax.bar(np.arange(len(names)), [res["steptime"][n]["s_per_step"] for n in names],
           color=fs.PAL["blue"], width=0.6, label="2026-11-19, 40 steps (f46f159)")
    for k, (lg, v) in enumerate(res["wave1"].items()):
        ax.axhline(v["s_per_step"], color=fs.PAL["red"], lw=1.0, ls="-" if k == 0 else "--",
                   label="wave 1, 1200 steps" if k == 0 else None)
    ax.axhspan(0.19, 0.25, color="0.85", zorder=0, label="predicted band")
    ax.set_xticks(np.arange(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylabel("card seconds per step")
    ax.legend(fontsize=7, loc="lower right")
    fig.savefig(os.path.join(out, "fig_steptime.png"), dpi=200)

    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.17, top=0.95)
    ax.plot(hr["ncycle"], hr["n_coll"], "o", color=fs.PAL["red"], ms=7, mfc="none",
            label="clean build f46f159 (job 4485)")
    ax.plot(hn["ncycle"], hn["n_coll"], "x", color=fs.PAL["blue"], ms=6,
            label="incremental build, nine objects recompiled")
    ax.set_xlabel("cycle")
    ax.set_ylabel("collisions in the step")
    ax.legend(fontsize=7)
    fig.savefig(os.path.join(out, "fig_smoke_x.png"), dpi=200)


if __name__ == "__main__":
    main()
