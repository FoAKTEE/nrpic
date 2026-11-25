#!/usr/bin/env python3
"""Byte comparison of the output files of two calls of cpu_tests.py (or of any two run
directories with the same sub-directories): every *.dump, *.modes, *.rmodes, *.hst of
every case.  Restart files are left out (their header carries the wall clock).

    bytecmp.py --a DIR --b DIR --out DIR

Writes DIR/bytecmp.json; exit status 1 if a file differs or is missing on one side."""
import argparse
import filecmp
import json
import os
import sys

SUFFIX = (".dump", ".modes", ".rmodes", ".hst")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    same, differ, only = [], [], []
    for case in sorted(os.listdir(a.a)):
        da, db = os.path.join(a.a, case), os.path.join(a.b, case)
        if not os.path.isdir(da) or case.startswith("."):
            continue
        if not os.path.isdir(db):
            only.append(case + "/")
            continue
        names = sorted(set(f for f in os.listdir(da) + os.listdir(db)
                           if f.endswith(SUFFIX)))
        for f in names:
            fa, fb = os.path.join(da, f), os.path.join(db, f)
            if not (os.path.exists(fa) and os.path.exists(fb)):
                only.append(os.path.join(case, f))
            elif filecmp.cmp(fa, fb, shallow=False):
                same.append(os.path.join(case, f))
            else:
                differ.append(os.path.join(case, f))
    os.makedirs(a.out, exist_ok=True)
    res = dict(a=os.path.abspath(a.a), b=os.path.abspath(a.b), identical=len(same),
               differ=differ, only_one_side=only,
               cases=sorted(set(os.path.dirname(f) for f in same + differ)))
    with open(os.path.join(a.out, "bytecmp.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps({k: res[k] for k in ("identical", "differ", "only_one_side")},
                     indent=1))
    sys.exit(1 if (differ or only) else 0)


if __name__ == "__main__":
    main()
