#!/usr/bin/env python3
"""Compare two JSON result files leaf by leaf (lead's rerun check).

    compare_json.py ORIGINAL RERUN [--ignore SUBSTR ...] [--stat]

Prints one line: number of numeric leaves, number identical, maximum relative difference
and its key; string leaves that differ are listed. Without --stat the exit status is 1 if
any numeric leaf differs by more than 1e-9 relative (deterministic scripts with fixed
seeds should reproduce bit for bit up to library rounding). With --stat (Monte Carlo rerun
with other seeds or sample size) differences are only reported.
Keys containing an --ignore substring (wall times, paths) are skipped.
"""
import argparse
import json
import math


def leaves(o, prefix=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{prefix}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--ignore", nargs="*", default=[])
    ap.add_argument("--stat", action="store_true")
    x = ap.parse_args()
    A = dict(leaves(json.load(open(x.a))))
    B = dict(leaves(json.load(open(x.b))))
    ign = list(x.ignore) + ["path", "dir", "exe", "time_s", "wall", "elapsed", "date", "utc",
                            "run_id", "commit"]
    keys = [k for k in A if not any(s in k.lower() for s in ign)]
    num = same = 0
    worst = (0.0, None)
    sdiff = []
    missing = [k for k in keys if k not in B]
    for k in keys:
        if k not in B:
            continue
        va, vb = A[k], B[k]
        if isinstance(va, bool) or isinstance(vb, bool) or not isinstance(va, (int, float)) \
                or not isinstance(vb, (int, float)):
            if va != vb:
                sdiff.append(k)
            continue
        num += 1
        if va == vb or (isinstance(va, float) and math.isnan(va) and math.isnan(vb)):
            same += 1
            continue
        d = abs(va - vb) / max(abs(va), abs(vb), 1e-300)
        if d > worst[0]:
            worst = (d, k)
    print(f"{x.b}: {num} numeric leaves, {same} identical, max rel diff {worst[0]:.3g} at "
          f"{worst[1]}; {len(sdiff)} other leaves differ {sdiff[:6]}; {len(missing)} missing "
          f"{missing[:6]}")
    bad = (worst[0] > 1e-9 or sdiff or missing) and not x.stat
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
