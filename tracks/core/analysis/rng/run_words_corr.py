#!/usr/bin/env python3
"""Covariances between the words of one generator call from many calls: compiles
words_corr.cpp, runs it with several seeds in parallel and combines the sums.

Usage: run_words_corr.py [--seeds 1001,1002,...] [--n calls per seed] [--jobs N]
Writes words_corr.json in the current directory; exit status 0 if every covariance is
within 3.5 standard errors of zero.
"""
import argparse
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PAIRS = ["01", "02", "03", "12", "13", "23"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default=",".join(str(1001 + i) for i in range(14)))
    ap.add_argument("--n", type=float, default=7.2e10)
    args = ap.parse_args()
    exe = os.path.abspath("words_corr")
    subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", "-DNRPIC_STANDALONE",
                    "-I", os.path.join(REPO, "athenak", "src"),
                    os.path.join(HERE, "words_corr.cpp"), "-o", exe], check=True)
    seeds = args.seeds.split(",")
    procs = [subprocess.Popen([exe, s, repr(args.n)], stdout=subprocess.PIPE, text=True)
             for s in seeds]
    tot = [0.0] * 14
    n = 0
    per_seed = {}
    for s, p in zip(seeds, procs):
        out = p.communicate()[0].split()
        if p.returncode != 0:
            raise RuntimeError(f"seed {s} failed")
        ni = int(out[0])
        vals = [float(v) for v in out[1:]]
        n += ni
        tot = [a + b for a, b in zip(tot, vals)]
        per_seed[s] = {pr: vals[8 + k] / math.sqrt(ni / 144.0)
                       for k, pr in enumerate(PAIRS)}
    res = {"calls": n, "seeds": seeds,
           "mean_z": [tot[k] / math.sqrt(n / 12.0) for k in range(4)],
           "variance_z": [(tot[4 + k] - n / 12.0) / math.sqrt(n / 180.0)
                          for k in range(4)],
           "covariance_z": {pr: tot[8 + k] / math.sqrt(n / 144.0)
                            for k, pr in enumerate(PAIRS)},
           "correlation": {pr: 12.0 * tot[8 + k] / n for k, pr in enumerate(PAIRS)},
           "correlation_se": 1.0 / math.sqrt(n),
           "covariance_z_per_seed": per_seed}
    res["ok"] = bool(all(abs(z) < 3.5 for z in res["covariance_z"].values()))
    with open("words_corr.json", "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "covariance_z_per_seed"},
                     indent=1))
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
