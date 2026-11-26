#!/usr/bin/env python3
"""Draw every G2 data figure of flrw_conv and population with its own script (item C15).

    python3 c15_figs.py

Runs each one-figure script as a separate process (the interpreter running this driver) into
$NRPIC_RUN_DIR/<package>/, from the registered runs named below, and prints one line per figure.
Inputs: flrw_conv/inputs/runs.json (leg B and F runs); the full-GR analysis
B-20261124-131918-e71996f (analysis_gr.json) with the Newtonian fidL8 analysis; the Newtonian
analysis B-20261119-160632-e1a1d05 (fidL8, lambda = 2). The figures equal, pixel for pixel, those
the multi-figure scripts drew before the split (batch 28 check against B-20261123-015452-18d2956,
B-20261121-220428-7367d5e, B-20261119-160632-e1a1d05, and the pre-split analyze_gr.py).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S = "/data/haiyangw/nrpic/scratch/B-emd-gw/"
OUT = os.environ["NRPIC_RUN_DIR"]
FL = os.path.join(TRK, "flrw_conv", "scripts")
PO = os.path.join(TRK, "population", "scripts")
RUNS = os.path.join(TRK, "flrw_conv", "inputs", "runs.json")
GR = S + "B-20261124-131918-e71996f/analysis_gr.json"
FID = os.path.join(TRK, "population", "results", "analysis_fidL8.json")
NEWT = S + "B-20261119-160632-e1a1d05/analysis_fidL8.json"

JOBS = [("flrw_conv", os.path.join(FL, f + ".py"), [RUNS, os.path.join(OUT, "flrw_conv")])
        for f in ("fig_b_growth", "fig_b_error", "fig_b_conv", "fig_b_constraints",
                  "fig_f_lattice", "fig_f_noise", "fig_f_scaling", "fig_f_constraints")]
JOBS += [("population", os.path.join(PO, f"fig_pop_gr_{f}.py"),
          [GR, "--newton", FID, "--out", os.path.join(OUT, "population")])
         for f in ("constraints", "halos", "gw", "stop")]
JOBS += [("population", os.path.join(PO, f"fig_pop_{f}.py"),
          [NEWT, "--gw", "fid", "--lscale", "2", "--out", os.path.join(OUT, "population_newton_fidL8")])
         for f in ("halos", "density", "gw")]


def main():
    bad = 0
    for pkg, script, args in JOBS:
        r = subprocess.run([sys.executable, script] + args, capture_output=True, text=True)
        print(f"{os.path.basename(script)}: exit {r.returncode}", flush=True)
        if r.returncode:
            bad += 1
            print(r.stderr[-2000:])
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
