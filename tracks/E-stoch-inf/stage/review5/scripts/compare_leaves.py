#!/usr/bin/env python3
"""Lead's check (batch 5): compare the numeric leaves of committed JSON results with a rerun.

    compare_leaves.py <out.json> <committed.json>:<rerun.json> [...]

Writes, per pair, the number of numeric leaves, how many differ, the largest relative
difference and the keys that differ (wall times and paths excluded by name).
"""
import json
import math
import sys

SKIP = ("wall", "time_s", "seconds", "path", "dir", "file", "host", "date", "created")


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{prefix}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield prefix, float(obj)
    elif isinstance(obj, str):
        yield prefix, obj


def main():
    out = {}
    for pair in sys.argv[2:]:
        a, b = pair.split(":")
        la = dict(leaves(json.load(open(a))))
        lb = dict(leaves(json.load(open(b))))
        keys = [k for k in la if not any(s in k.lower() for s in SKIP)]
        missing = [k for k in keys if k not in lb]
        nnum, ndiff, worst, wkey, diffs = 0, 0, 0.0, None, []
        for k in keys:
            if k not in lb:
                continue
            x, y = la[k], lb[k]
            if isinstance(x, float) and isinstance(y, float):
                nnum += 1
                if x == y or (math.isnan(x) and math.isnan(y)):
                    continue
                r = abs(x - y) / max(abs(x), abs(y), 1e-300)
                ndiff += 1
                diffs.append((r, k))
                if r > worst:
                    worst, wkey = r, k
            elif x != y:
                ndiff += 1
                diffs.append((float("inf"), k))
        diffs.sort(reverse=True)
        out[pair] = {"numeric_leaves": nnum, "differing": ndiff, "missing_in_rerun": len(missing),
                     "max_rel_diff": worst, "worst_key": wkey,
                     "top_differences": [[r, k] for r, k in diffs[:12]]}
        print(f"{a}\n  vs {b}: {nnum} numeric leaves, {ndiff} differ, {len(missing)} missing; "
              f"max rel diff {worst:.3e} at {wkey}")
    json.dump(out, open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
