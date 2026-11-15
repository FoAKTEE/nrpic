#!/usr/bin/env python3
"""Rerun of the box tests of wave 1 (P0 to P11 of tracks/core/JOURNAL-coll.md) with a
new executable, each as a registered run with the arguments of its wave-1 run, and
comparison of every output file with the run directory of wave 1, byte by byte.

  rerun_wave1.py SUMMARY.json --exe ATHENA [--tests kernel,replay,...]

Compared: all files of the wave-1 directory except logs, summaries, figures and restart
files (the mesh restart header holds 36 bytes that are never set, tracks/core/HANDOFF.md).
A test passes if its driver exits with status 0 (its own criteria) and no compared file
differs or is missing.
"""
import argparse
import filecmp
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
RUNREG = os.path.join(REPO, "tracks", "core", "analysis", "rng", "runreg.py")

# test: (driver, arguments after the output directory, cores, wave-1 run, purpose)
TESTS = {
    "kernel": ("run_kernel_test.py", [], 1, "core-20261115-132556-a7dc8ab",
               "P0 kernels against the track's test vectors"),
    "replay": ("run_replay.py", ["--nproc", "6"], 6, "core-20261115-134644-466dcfd",
               "one collision step against the Python twin, seven cases"),
    "rate": ("run_rate.py", ["--nproc", "8"], 8, "core-20261115-133533-0ca5e3b",
             "P2 P3 P4 rate, conservation, null runs"),
    "relax": ("run_relax.py", ["--nproc", "4"], 4, "core-20261115-134036-5684674",
              "P5 P6 relaxation and entropy"),
    "repro": ("run_repro.py", ["--nproc", "6"], 6, "core-20261115-140950-0f9d0cf",
              "P7 MeshBlock divisions, restart, seed"),
    "conv_dt": ("run_conv_dt.py", ["--nproc", "8"], 8, "core-20261115-134511-0607ce8",
                "P8a time step"),
    "cells": ("run_cells.py", ["--nproc", "8"], 8, "core-20261115-135219-42c8489",
              "P8b cell size and cell factor"),
    "unequal": ("run_unequal.py", ["--nproc", "5"], 5, "core-20261115-140030-7a0efc0",
                "unequal masses (nanbu)"),
    "curved": ("run_curved_box.py", ["--nproc", "3"], 3, "core-20261115-140147-15c576d",
               "P10 homogeneous curved metric"),
    "smr": ("run_smr.py", ["--nproc", "3"], 3, "core-20261115-140539-54f8bee",
            "statically refined mesh"),
    "cluster": ("run_cluster.py", ["--tlim", "0.25", "--kn", "30", "--snap-dt", "0.125"], 1,
                "core-20261115-135728-18d4555", "P11 null on the processor (two steps)"),
}
SKIP = re.compile(r"(\.log$|\.png$|\.pdf$|summary.*\.json$|\.rst$|\.json$|\.out$|\.o$|kernel_test_|run\.log$)")


def compare(new, old):
    ncmp, diff, missing, skipped = 0, [], [], 0
    for root, _, files in os.walk(old):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), old)
            if SKIP.search(rel):
                skipped += 1
                continue
            a, b = os.path.join(old, rel), os.path.join(new, rel)
            if not os.path.exists(b):
                missing.append(rel)
                continue
            ncmp += 1
            if not filecmp.cmp(a, b, shallow=False):
                diff.append(rel)
    return ncmp, diff, missing, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("summary")
    ap.add_argument("--exe", required=True)
    ap.add_argument("--tests", default=",".join(TESTS))
    ap.add_argument("--python", default=sys.executable)
    args = ap.parse_args()
    res = {}
    if os.path.exists(args.summary):
        with open(args.summary) as fp:
            res = json.load(fp)
    ok = True
    for name in args.tests.split(","):
        drv, extra, cores, old_id, what = TESTS[name]
        drv_path = os.path.join(HERE, drv)
        exe_arg = [] if name == "kernel" else ["--exe", args.exe]
        cmd = [args.python, RUNREG, "--kind", "production", "--cores", str(cores),
               "--purpose", f"Rerun of wave 1 with the executable of core/collisions-2 "
               f"(options absent): {what}; outputs compared with {old_id}",
               "--input", drv_path] + ([] if name == "kernel" else ["--input", args.exe]) \
            + ["--", args.python, drv_path, "{out}"] + exe_arg + extra
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        line = (proc.stdout.strip().splitlines() or [""])[-1]
        run_id = line.split()[0] if line else ""
        new = os.path.join(SCRATCH, run_id)
        ncmp, diff, missing, skipped = compare(new, os.path.join(SCRATCH, old_id))
        passed = (proc.returncode == 0 and not diff and not missing)
        res[name] = dict(run_id=run_id, wave1_run=old_id, driver_exit=proc.returncode,
                         files_compared=ncmp, files_differ=diff, files_missing=missing,
                         files_skipped=skipped, passed=passed)
        ok = ok and passed
        print(f"{name:8s} {run_id}  driver exit {proc.returncode}  compared {ncmp}  "
              f"differ {len(diff)}  missing {len(missing)}  {'ok' if passed else 'FAIL'}",
              flush=True)
        with open(args.summary, "w") as fp:
            json.dump(res, fp, indent=1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
