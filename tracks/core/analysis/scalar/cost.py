#!/usr/bin/env python3
"""Cost of the scalar field and of its stochastic sources next to Z4c: zone-cycles per
second of three short runs on an N^3 mesh,
  z4c     vacuum-type Z4c alone (problems/tests/z4c_bench.athinput, a puncture)
  field   Z4c with the coupled scalar field, no stochastic sources
  noise   the same with the Mukhanov-Sasaki sources, ball |n| <= N/4, six fields per stage

Usage: cost.py --exe ATHENA --n 64 --nlim 6 [--block 32]   (run in the output directory)
"""
import argparse
import json
import os
import re

import numpy as np

import common
from common import PROB, REPO, mesh_args, run_case
from nrpic import scalar_field as sfr


def rate(rundir):
    txt = open(os.path.join(rundir, "athena.log")).read()
    m = re.search(r"zone-cycles/cpu_second = ([0-9.eE+-]+)", txt)
    return float(m.group(1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--block", type=int, default=32)
    ap.add_argument("--nlim", type=int, default=6)
    args = ap.parse_args()
    top = os.getcwd()
    n, b = args.n, args.block
    nmax = n//4
    nmax2 = nmax*nmax
    modes, n2 = sfr.mode_set(nmax2)
    shells = np.unique(n2)
    q = np.sqrt(shells.astype(float))
    mfile = os.path.join(top, "modes.txt")
    np.savetxt(mfile, np.column_stack([shells, 1e-4*q**-1.5, 0.5e-4*q**-1.5,
                                       -1e-5*q**-1.5, 2e-5*q**-0.5]),
               fmt=["%d"] + ["%.17e"]*4)
    ms = os.path.join(PROB, "noise_ms.athinput")
    com = mesh_args(n, n, n, b, b, b) + [f"time/nlim={args.nlim}", "time/tlim=1000.0",
                                         "scalar_field/hist_dcycle=0",
                                         "scalar_field/dump_dt=-1.0", "output1/dcycle=100000"]
    cases = {
        "z4c": (os.path.join(REPO, "problems", "tests", "z4c_bench.athinput"),
                mesh_args(n, n, n, b, b, b) + [f"time/nlim={args.nlim}"]),
        "field": (ms, com + ["scalar_field/noise=none"]),
        "noise": (ms, com + [f"scalar_field/noise_nmax2={nmax2}",
                             f"scalar_field/noise_mode_file={mfile}"]),
    }
    res = {"n": n, "block": b, "nlim": args.nlim, "modes": int(len(modes)),
           "shells": int(len(shells)), "nmax2": nmax2}
    for name, (inp, a) in cases.items():
        rd = os.path.join(top, name)
        wall = run_case(args.exe, rd, inp, a)
        res[name] = dict(zone_cycles_per_s=rate(rd), wall_s=wall)
    res["field_over_z4c"] = res["z4c"]["zone_cycles_per_s"]/res["field"]["zone_cycles_per_s"]
    res["noise_over_field"] = res["field"]["zone_cycles_per_s"]/res["noise"]["zone_cycles_per_s"]
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
