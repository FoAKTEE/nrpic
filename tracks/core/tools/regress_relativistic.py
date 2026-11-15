#!/usr/bin/env python3
"""Regression of the relativistic mode: run a set of short existing problems with two
executables and compare every output file byte by byte.

    regress_relativistic.py --exe-a BASELINE --exe-b NEW [--cases geo,boris,dep,east,os]
                            [--cores N] [--card] [--out REPORT.json]

Cases (inputs under problems/, initial data under scratch/core/regress/ic/, made once by
the commands in tracks/core/JOURNAL-newton.md):
  geo    test particle in Kerr, analytic metric, implicit midpoint       (2000 steps)
  boris  the same with the spacetime-Boris pusher on the virtual lattice (2000 steps)
  dep    10^4 particles on a statically refined mesh, flat metric on the mesh, deposit
  east   periodic cosmology with Z4c, deposit, filter and compensation, 16^3 (20 steps)
  os     Oppenheimer-Snyder ball with Z4c on a statically refined mesh    (3 steps)
Every run is registered (run_registered.py). The report lists, per case, the two run ids
and the files that differ; exit status 0 only if no file differs.
"""
import argparse
import filecmp
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
IC = "/data/haiyangw/nrpic/scratch/core/regress/ic"
SCRATCH = "/data/haiyangw/nrpic/scratch/core"

OS = "os_R5_lattice_N2176_s1"
CASES = {
    "geo": dict(inp="problems/kerr/geodesic.athinput", files=[],
                args=["time/tlim=20.0", "particles/hist_dcycle=100"]),
    "boris": dict(inp="problems/kerr/geodesic.athinput", files=[],
                  args=["time/tlim=20.0", "particles/hist_dcycle=100",
                        "particles/pusher=boris", "particles/metric=lattice"]),
    "dep": dict(inp="problems/tests/deposit_smr.athinput", files=[IC + "/random.nrp"],
                args=["time/tlim=2.0", "particles/deposit_max_level=1"]),
    "east": dict(inp="problems/cosmo/east.athinput",
                 files=[IC + "/east16/particles.nrp", IC + "/east16/fields.bin"],
                 args=["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8",
                       "meshblock/nx2=8", "meshblock/nx3=8", "time/nlim=20",
                       "particles/snap_dt=0.2", "particles/traj_ntrack=46"]),
    "os": dict(inp="problems/os/os_smr_dev.athinput",
               files=[IC + "/os/%s.nrp" % OS, IC + "/os/%s.tab" % OS],
               args=["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "meshblock/nx1=16",
                     "meshblock/nx2=16", "meshblock/nx3=16", "time/nlim=3",
                     "particles/particle_file=%s.nrp" % OS,
                     "problem/comp0_file=%s.tab" % OS, "particles/snap_dt=0.05",
                     "output2/dt=0.1"]),
}
SKIP = ("run.log",)


def run(exe, case, label, cores, card):
    c = CASES[case]
    cmd = [sys.executable, os.path.join(HERE, "run_registered.py"),
           "--purpose", "regression of the relativistic mode, case %s, executable %s"
           % (case, label), "--tag", "regress-%s-%s" % (case, label),
           "--cores", str(cores), "--input", os.path.join(WT, c["inp"])]
    for f in c["files"]:
        cmd += ["--input", f]
    cmd += ["--"]
    if card:
        cmd += ["srun", "-p", "preempt", "--gres=gpu:1", "-c", "1", "-t", "00:10:00"]
    cmd += [exe, "-i", os.path.basename(c["inp"])] + c["args"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    lines = out.stdout.strip().splitlines()
    if not lines:
        raise RuntimeError(out.stderr)
    return lines[-1], lines[-2]


def compare(ra, rb):
    da, db = os.path.join(SCRATCH, ra), os.path.join(SCRATCH, rb)
    differ, same = [], []
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    for n in sorted(names):
        if n in SKIP or os.path.islink(os.path.join(da, n)):
            continue
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(n + " (missing in one run)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        else:
            differ.append(n)
    return same, differ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe-a", required=True)
    ap.add_argument("--exe-b", required=True)
    ap.add_argument("--cases", default="geo,boris,dep,east,os")
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--card", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--repeat-a", action="store_true",
                    help="run the baseline twice and compare it with itself as well "
                         "(is the executable reproducible from run to run?)")
    a = ap.parse_args()
    report, bad = {}, 0
    for case in a.cases.split(","):
        ra, sa = run(a.exe_a, case, "baseline", a.cores, a.card)
        rb, sb = run(a.exe_b, case, "new", a.cores, a.card)
        same, differ = compare(ra, rb)
        report[case] = dict(baseline=ra, new=rb, identical=same, differ=differ,
                            status_baseline=sa, status_new=sb)
        if a.repeat_a:
            ra2, _ = run(a.exe_a, case, "baseline-repeat", a.cores, a.card)
            same2, differ2 = compare(ra, ra2)
            report[case].update(baseline_repeat=ra2, repeat_identical=same2,
                                repeat_differ=differ2)
            print("%-6s baseline against itself (%s): identical files: %d  differing: %s"
                  % (case, ra2, len(same2), differ2 if differ2 else "none"))
        bad += len(differ) + (0 if same else 1)
        print("%-6s %s  %s  identical files: %d  differing: %s"
              % (case, ra, rb, len(same), differ if differ else "none"))
        print("       " + sa + " | " + sb)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(report, f, indent=1)
            f.write("\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
