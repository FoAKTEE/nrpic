#!/usr/bin/env python3
"""T12 of the work package cosmo-amr: the executable to be published gives the same bytes
as the executable that ran the tests T1, T2 and T9 (prediction:
tracks/core/JOURNAL-cosmo-amr.md).

    t12_same.py --new NEW_EXE --out DIR [--cores N] RUNDIR:case[,case...] ...

For every case directory RUNDIR/case of an earlier registered run, the input deck saved
there (the only *.athinput file) is run again with NEW in DIR/<run id>/<case>, from the
same start directory layout (-d), and every output file is compared byte by byte with the
earlier one; log.txt and status.txt are skipped.  The first column of the status file of
the horizon finder changed on purpose (Runge-Kutta stage -> cycle): for that file the
remaining columns are compared.  Writes DIR/t12_summary.json."""
import argparse
import concurrent.futures as cf
import filecmp
import glob
import json
import os
import subprocess
import sys
import time

SKIP = ("log.txt", "status.txt")


def run(exe, deck, rundir):
    os.makedirs(rundir, exist_ok=True)
    t0 = time.time()
    with open(os.path.join(rundir, "log.txt"), "w") as log:
        p = subprocess.run([exe, "-i", deck, "-d", rundir], cwd=rundir, stdout=log,
                           stderr=subprocess.STDOUT, env=dict(os.environ, OMP_NUM_THREADS="1"))
    with open(os.path.join(rundir, "status.txt"), "w") as f:
        f.write(f"exit {p.returncode}\nwall {time.time() - t0:.2f}\nexe {exe}\n")
    return p.returncode


def strip_first(path):
    with open(path) as f:
        return [" ".join(l.split()[1:]) if not l.startswith("#") else l for l in f]


def compare(da, db):
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    same, differ = [], []
    for n in sorted(names):
        if n in SKIP or n.endswith(".athinput"):
            continue
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(n + " (missing in one run)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        elif "horizon_status" in n and strip_first(fa) == strip_first(fb):
            same.append(n + " (columns 2-15)")
        else:
            differ.append(n)
    return same, differ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("sets", nargs="+")
    a = ap.parse_args()
    a.out, a.new = os.path.abspath(a.out), os.path.abspath(a.new)
    jobs = []
    for s in a.sets:
        rd, cases = s.split(":")
        for c in cases.split(","):
            old = os.path.join(rd, c)
            decks = glob.glob(os.path.join(old, "*.athinput"))
            if len(decks) != 1:
                print("skip", old, "(decks:", decks, ")")
                continue
            jobs.append((old, decks[0], os.path.join(a.out, os.path.basename(rd), c)))
    with cf.ThreadPoolExecutor(max_workers=a.cores) as ex:
        rcs = list(ex.map(lambda j: run(a.new, j[1], j[2]), jobs))
    res, nbad = {}, 0
    for (old, deck, new), rc in zip(jobs, rcs):
        with open(os.path.join(old, "status.txt")) as f:
            rc_old = int(f.readline().split()[1])
        same, differ = compare(old, new)
        key = os.path.relpath(new, a.out)
        res[key] = dict(old=old, exit_old=rc_old, exit_new=rc, identical=len(same),
                        differ=differ)
        bad = len(differ) + (rc != rc_old) + (0 if same else 1)
        nbad += bad
        print(f"{key:40s} exit {rc_old}/{rc} identical {len(same):3d} differing {differ}",
              flush=True)
    with open(os.path.join(a.out, "t12_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print("T12:", "PASS" if nbad == 0 else f"FAIL ({nbad})")
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
