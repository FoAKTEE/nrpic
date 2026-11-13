#!/usr/bin/env python3
"""All particle files of the cluster campaign (docs/results_cluster_test.md).

  bound_a{a}_n{N}.nrp   bound family: r_0 = 10 M circular centre orbit, sigma_x = 0.5 M,
                        sigma_v = 0.02, conditioned on bound orbits (--bound_only),
                        N = 1e2, 1e3, 1e4 with independent seeds
  bound_a{a}_all.nrp    the three bound clusters of one spin concatenated, species
                        0, 1, 2 = N 1e2, 1e3, 1e4 (tags 0-99, 100-1099, 1100-11099), for
                        the analytic-metric runs, where particles are independent
  plunge_a{a}_n10000.nrp  plunging family: same widths, eccentric centre orbit with
                        apocentre 10 M and L = f_L L_circ (f_L = 0.96 for a = 0,
                        0.72 for a = 0.9), no conditioning

Usage: make_campaign_ic.py [outdir]   (default runs/cluster_test/ic)
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic.io import read_nrp, write_nrp  # noqa: E402

SEEDS = {(0.0, 100): 101, (0.0, 1000): 102, (0.0, 10000): 103,
         (0.9, 100): 201, (0.9, 1000): 202, (0.9, 10000): 203}
PLUNGE = {0.0: dict(fL=0.96, seed=301), 0.9: dict(fL=0.72, seed=401)}


def run(args):
    print(" ".join(args))
    subprocess.run([sys.executable, os.path.join(HERE, "make_cluster.py")] + args,
                   check=True)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "runs/cluster_test/ic")
    os.makedirs(out, exist_ok=True)
    for a in (0.0, 0.9):
        parts = []
        for k, n in enumerate((100, 1000, 10000)):
            f = os.path.join(out, f"bound_a{a}_n{n}.nrp")
            run(["--N", str(n), "--a", str(a), "--bound_only", "--seed",
                 str(SEEDS[(a, n)]), "--out", f])
            x, u, m, _ = read_nrp(f)
            parts.append((x, u, m, np.full(n, k, dtype=np.int32)))
        x, u, m, sp = (np.concatenate([p[i] for p in parts]) for i in range(4))
        write_nrp(os.path.join(out, f"bound_a{a}_all.nrp"), x, u, m, sp)
        p = PLUNGE[a]
        run(["--N", "10000", "--a", str(a), "--fL", str(p["fL"]), "--seed",
             str(p["seed"]), "--out", os.path.join(out, f"plunge_a{a}_n10000.nrp")])
    summary = {}
    for fn in sorted(os.listdir(out)):
        if fn.endswith(".json") and (fn.startswith("bound") or fn.startswith("plunge")):
            summary[fn[:-5]] = json.load(open(os.path.join(out, fn)))
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
