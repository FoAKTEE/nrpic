#!/usr/bin/env python3
"""Test G of tracks/core/JOURNAL-clump2.md: the inputs of the card jobs TC and TE (batch
lists card_tc.list, card_te.list) started on a processor with time/nlim=0, so that the
records at t = 0 of the card runs can be compared with those of the processor
executable of the same source. Writes <out>/<name>/ for every entry and records.json
with the first record of the two history files of each.

    run_t0_records.py [--exe .work/build_cpu/src/athena] [--out DIR] [--names a,b]
"""
import argparse
import json
import os
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LISTS = ("card_tc.list", "card_te.list")


def entries():
    for lst in LISTS:
        for ln in open(os.path.join(HERE, lst)):
            if ln.strip() and not ln.startswith("#"):
                w = shlex.split(ln)
                yield w[0], w[1], w[2:]


def first_record(path):
    with open(path) as f:
        head = [ln for ln in f if ln.startswith("#")]
    with open(path) as f:
        row = next(ln for ln in f if not ln.startswith("#") and ln.strip()).split()
    return dict(header=head[-1].strip() if head else "", row=[float(x) for x in row])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=os.path.join(WT, ".work", "build_cpu", "src", "athena"))
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--names", default=None)
    a = ap.parse_args()
    exe = os.path.abspath(a.exe)
    want = set(a.names.split(",")) if a.names else None
    res, ok = {}, True
    for name, inp, args in entries():
        if want and name not in want:
            continue
        d = os.path.join(a.out, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "athena.log"), "w") as log:
            p = subprocess.run([exe, "-i", os.path.join(WT, inp), "-d", d] + args
                               + ["time/nlim=0"], cwd=d, stdout=log,
                               stderr=subprocess.STDOUT,
                               env=dict(os.environ, OMP_NUM_THREADS="1"))
        r = dict(status=p.returncode)
        if p.returncode == 0:
            for kind in ("nrpic", "z4c.user"):
                fs_ = [f for f in os.listdir(d) if f.endswith(f".{kind}.hst")]
                if fs_:
                    r[kind] = first_record(os.path.join(d, fs_[0]))
        ok = ok and p.returncode == 0
        res[name] = r
        print(name, "status", p.returncode, flush=True)
    with open(os.path.join(a.out, "records.json"), "w") as f:
        json.dump(res, f, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
