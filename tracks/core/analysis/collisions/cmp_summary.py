#!/usr/bin/env python3
"""Compare two summary.json files value by value.

  cmp_summary.py A.json B.json [--ignore key,key,...]

Prints every path whose value differs or exists in only one file (keys named in
--ignore are skipped at any depth). Exit status 0 if nothing differs.
"""
import argparse
import json
import math
import sys


def walk(a, b, path, ignore, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in ignore:
                continue
            if k not in a or k not in b:
                out.append(f"{path}/{k}: only in {'B' if k not in a else 'A'}")
                continue
            walk(a[k], b[k], f"{path}/{k}", ignore, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: lengths {len(a)} and {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", ignore, out)
    else:
        same = a == b or (isinstance(a, float) and isinstance(b, float)
                          and math.isnan(a) and math.isnan(b))
        if not same:
            out.append(f"{path}: {a!r} != {b!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--ignore", default="")
    args = ap.parse_args()
    ignore = {k for k in args.ignore.split(",") if k}
    out = []
    walk(json.load(open(args.a)), json.load(open(args.b)), "", ignore, out)
    for line in out:
        print(line)
    print(f"{len(out)} differences (ignored keys: {sorted(ignore)})")
    sys.exit(0 if not out else 1)


if __name__ == "__main__":
    main()
