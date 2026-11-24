#!/usr/bin/env python3
"""Package step-limit, test T5a: what evaluating the bound in every cycle costs.

Flat box of 32^3 cells in eight blocks (problems/tests/z4c_step_limit.athinput with the
mesh doubled), cfl_number 0.25, so that dt_gauge = 0.9 never sets the step: the two runs
take the same steps and their histories must be byte-identical.  Each variant is run
REPS times in turn on one core; the cost is the "cpu time used" of the log.

  python time_overhead.py --exe ATHENA --out DIR [--nlim 20] [--reps 3]
"""
import argparse
import filecmp
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DECK = os.path.join(REPO, "problems", "tests", "z4c_step_limit.athinput")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--nlim", type=int, default=20)
    ap.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    a.exe = os.path.abspath(a.exe)
    a.out = os.path.abspath(a.out)
    os.makedirs(a.out, exist_ok=True)
    base = ["mesh/nx1=32", "mesh/nx2=32", "mesh/nx3=32", "time/cfl_number=0.25",
            "time/nlim=%d" % a.nlim, "output2/dcycle=1000"]
    var = {"off": ["z4c/dt_gauge=0.0"], "on": ["z4c/dt_gauge=0.9"]}
    cpu = {k: [] for k in var}
    zc = {k: [] for k in var}
    for r in range(a.reps):
        for k in ("off", "on"):
            d = os.path.join(a.out, "%s_%d" % (k, r))
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "athena.log"), "w") as log:
                subprocess.run([a.exe, "-i", DECK] + base + var[k] + ["-d", d], cwd=d,
                               stdout=log, stderr=subprocess.STDOUT, check=True,
                               env=dict(os.environ, OMP_NUM_THREADS="1"))
            txt = open(os.path.join(d, "athena.log")).read()
            cpu[k].append(float(re.search(r"cpu time used\s*=\s*([-+.0-9eE]+)", txt).group(1)))
            zc[k].append(float(re.search(r"zone-cycles/cpu_second\s*=\s*([-+.0-9eE]+)",
                                         txt).group(1)))
    same = filecmp.cmp(os.path.join(a.out, "off_0", "flat.z4c.user.hst"),
                       os.path.join(a.out, "on_0", "flat.z4c.user.hst"), shallow=False)
    res = {"nlim": a.nlim, "cpu_s": cpu, "zone_cycles_per_s": zc,
           "min_off": min(cpu["off"]), "min_on": min(cpu["on"]),
           "overhead_of_min": min(cpu["on"]) / min(cpu["off"]) - 1.0,
           "overhead_of_median": float(np.median(cpu["on"]) / np.median(cpu["off"]) - 1.0),
           "histories_identical": bool(same)}
    with open(os.path.join(a.out, "time_overhead.json"), "w") as f:
        json.dump(res, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 2.8))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.17, top=0.95)
    for i, (k, c) in enumerate((("off", fs.PAL["blue"]), ("on", fs.PAL["red"]))):
        ax.plot([i] * len(cpu[k]), np.array(cpu[k]) / a.nlim, "o", color=c)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["without dt_gauge", "dt_gauge = 0.9 (not binding)"])
    ax.set_xlim(-0.6, 1.6)
    lo = min(cpu["off"] + cpu["on"]) / a.nlim
    hi = max(cpu["off"] + cpu["on"]) / a.nlim
    ax.set_ylim(lo - 0.6 * (hi - lo) - 1e-3, hi + 0.6 * (hi - lo) + 1e-3)
    ax.set_ylabel(r"processor seconds per step (32$^3$)")
    fig.savefig(os.path.join(a.out, "fig_time_overhead.png"), dpi=150)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
