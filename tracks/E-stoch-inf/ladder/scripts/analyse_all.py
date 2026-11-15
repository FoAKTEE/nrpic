#!/usr/bin/env python3
"""Runs extract, judge and pair of ladder_analysis.py on every ladder run that exists in
the given output directories of registered runs, then writes summary.json with the
verdicts on A1-A5 (thresholds of SCOPE 4, restated in ../JOURNAL.md entry 1).

    analyse_all.py --runs DIR [DIR ...] --out DIR [--only NAME ...]

Each DIR is the output directory of one registered run whose subdirectories are the
named runs of the lists in ../inputs/ (P256, L128p, ...).
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.abspath(os.path.join(HERE, "..", "inputs"))

# name -> (N, nmax2, scale)
RUNS = {"P256": (256, 4096, 1.0), "P256m": (256, 4096, -1.0),
        "L256p": (256, 64, 1.0), "L256m": (256, 64, -1.0),
        "L128p": (128, 64, 1.0), "L128m": (128, 64, -1.0),
        "L64p": (64, 64, 1.0), "L64m": (64, 64, -1.0),
        "L32p": (32, 64, 1.0), "L32m": (32, 64, -1.0),
        "L32ph": (32, 64, 0.5), "L32mh": (32, 64, -0.5),
        "NC32p": (32, 64, 1.0), "NC32m": (32, 64, -1.0)}
for n, q in ((128, 1024), (64, 256)):
    RUNS.update({f"Q{n}p": (n, q, 1.0), f"Q{n}m": (n, q, -1.0), f"Q{n}ph": (n, q, 0.5),
                 f"Q{n}mh": (n, q, -0.5), f"NC{n}p": (n, q, 1.0), f"NC{n}m": (n, q, -1.0)})
PAIRS = [("L32p", "L32m", 1.0), ("L32ph", "L32mh", 0.5), ("NC32p", "NC32m", 1.0),
         ("L64p", "L64m", 1.0), ("L128p", "L128m", 1.0), ("L256p", "L256m", 1.0),
         ("P256", "P256m", 1.0), ("Q128p", "Q128m", 1.0), ("Q128ph", "Q128mh", 0.5),
         ("NC128p", "NC128m", 1.0), ("Q64p", "Q64m", 1.0), ("Q64ph", "Q64mh", 0.5),
         ("NC64p", "NC64m", 1.0)]


def call(args):
    print("+", " ".join(args), flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, "ladder_analysis.py")] + args,
                   check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    where = {}
    for d in a.runs:
        for name in RUNS:
            p = os.path.join(d, name)
            if os.path.isfile(os.path.join(p, "sr.sf.con.hst")):
                where[name] = p
    if a.only:
        where = {k: v for k, v in where.items() if k in a.only}
    found = {}
    for name, p in sorted(where.items()):
        n, q, s = RUNS[name]
        npz = os.path.join(a.out, f"{name}.npz")
        if not os.path.isfile(npz):
            call(["extract", p, "--nmesh", str(n), "--nmax2", str(q), "--modefile",
                  os.path.join(INP, f"modes_n{q}.txt"), "--scale", str(s), "--out", npz])
        found[name] = p
        with open(os.path.join(a.out, f"{name}.json")) as fp:
            if json.load(fp)["has_metric"]:
                jj = os.path.join(a.out, f"{name}_judge.json")
                if not os.path.isfile(jj):
                    call(["judge", npz, "--out", jj])
    for p, m, s in PAIRS:
        if p in found and m in found:
            out = os.path.join(a.out, f"pair_{p}_{m}.json")
            if not os.path.isfile(out):
                call(["pair", found[p], found[m], "--scale", str(s), "--out", out])
    with open(os.path.join(a.out, "found.json"), "w") as fp:
        json.dump(found, fp, indent=1)
    print("runs analysed:", ", ".join(sorted(found)))


if __name__ == "__main__":
    main()
