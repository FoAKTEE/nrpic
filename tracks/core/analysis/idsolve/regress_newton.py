#!/usr/bin/env python3
"""Byte regression of the Newtonian mode of the particle module between two executables
(the initial-data solver added a boundary kind to the multigrid module and an entry
point to its gravity driver, which the Newtonian mode shares).

    regress_newton.py --exe-a BASELINE --exe-b NEW [--out REPORT.json]

Cases: the isolated ball of problems/newton (multipole boundary, 32^3, 5 steps) and the
plane wave on the periodic expanding mesh (32^3, 10 steps); every output file of the two
runs is compared byte by byte (tracks/core/tools/regress_relativistic.py, compare).
Each run is registered by hand with tracks/core/tools/run_registered.py.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "tools"))
import regress_relativistic as rr  # noqa: E402

IC = "/data/haiyangw/nrpic/scratch/core/idsolve_ic"
MB = ["meshblock/nx1=16", "meshblock/nx2=16", "meshblock/nx3=16"]
CASES = {
    "isolated": dict(inp="problems/newton/isolated.athinput", ic="newton_ball32.nrp",
                     make=["ball", "--spacing", "0.125", "--ntracer", "0"],
                     args=["mesh/nx1=32", "mesh/nx2=32", "mesh/nx3=32"] + MB
                     + ["time/nlim=5", "particles/dt=0.002", "particles/snap_dt=0.004"]),
    "periodic": dict(inp="problems/newton/periodic.athinput", ic="newton_wave32.nrp",
                     make=["wave", "--n", "32"],
                     args=MB + ["time/nlim=10"]),
}


def run(exe, case, label):
    c = CASES[case]
    ic = os.path.join(IC, c["ic"])
    if not os.path.exists(ic):
        os.makedirs(IC, exist_ok=True)
        subprocess.run([sys.executable, os.path.join(WT, "problems/newton/make_ic.py"),
                        c["make"][0], "--out", ic] + c["make"][1:], check=True)
    cmd = [sys.executable, os.path.join(WT, "tracks/core/tools/run_registered.py"),
           "--purpose", "regression of the Newtonian mode, case %s, executable %s"
           % (case, label), "--tag", "regress-newton-%s-%s" % (case, label), "--cores", "1",
           "--input", os.path.join(WT, c["inp"]), "--input", ic, "--",
           exe, "-i", os.path.basename(c["inp"]),
           "particles/particle_file=" + c["ic"]] + c["args"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    lines = out.stdout.strip().splitlines()
    if len(lines) < 2:
        raise RuntimeError(out.stderr)
    time.sleep(1.1)
    return lines[-1], lines[-2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe-a", required=True)
    ap.add_argument("--exe-b", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    report, bad = {}, 0
    for case in CASES:
        ra, sa = run(a.exe_a, case, "baseline")
        rb, sb = run(a.exe_b, case, "new")
        same, differ = rr.compare(ra, rb)
        report[case] = dict(baseline=ra, new=rb, identical=same, differ=differ,
                            status_baseline=sa, status_new=sb)
        bad += len(differ) + (0 if same else 1)
        print("%-9s %s  %s  identical files: %d  differing: %s"
              % (case, ra, rb, len(same), differ if differ else "none"))
        print("          " + sa + " | " + sb)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(report, f, indent=1)
            f.write("\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
