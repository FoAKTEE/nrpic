#!/usr/bin/env python3
"""Particle files of the first collisional cluster runs CC1 and CC2 (stage/G1/STATUS.md,
section 4): the King b = 1 models of 2009.08163 at the threshold y0 = y_max = 0.334032
(`king_y0p33403`) and on the stable side y0 = 0.314 (`king_y0p31400`), 10^5 equal-mass
macroparticles each, stratified sampler, seed 1.

The models, the sampler and the file writer are those of `tracks/C-sidm/equilibria/`
(make_equilibria.py, evstatic.py; checked there in runs C-sidm-20261115-121626-e99907d
and C-sidm-20261115-125308-54870b9); this script only calls them with N = 10^5.

    python3 make_ic.py [--out DIR] [--N 100000] [--seed 1]

--out defaults to $NRPIC_RUN_DIR (set by harness/bin/nrpic-run).
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAKE = os.path.join(HERE, "..", "equilibria", "make_equilibria.py")
MODELS = ("king_y0p33403", "king_y0p31400")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--N", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run (NRPIC_RUN_DIR)")
    cmd = [sys.executable, os.path.normpath(MAKE), "--out", a.out, "--N", str(a.N),
           "--seed", str(a.seed), "--sampler", "stratified", "--only", *MODELS]
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
