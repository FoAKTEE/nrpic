#!/usr/bin/env python3
"""Leaf-by-leaf comparison of JSON files (original run against rerun): for every pair, the
number of numeric leaves, the largest relative difference, the number of differing string
leaves and of missing keys. Usage: cmp_tree.py OUT.json orig1 new1 [orig2 new2 ...]"""
import json
import sys


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, path + "[%d]" % i)
    else:
        yield path, o


def main():
    out = sys.argv[1]
    args = sys.argv[2:]
    res = {}
    for a, b in zip(args[::2], args[1::2]):
        la = dict(leaves(json.load(open(a))))
        lb = dict(leaves(json.load(open(b))))
        num, worst, worst_path, sdiff = 0, 0.0, None, []
        for p, va in la.items():
            if p not in lb:
                continue
            vb = lb[p]
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)) \
                    and not isinstance(va, bool):
                num += 1
                d = abs(va - vb) / max(abs(va), abs(vb), 1e-300) if va != vb else 0.0
                if d > worst:
                    worst, worst_path = d, p
            elif va != vb:
                sdiff.append(p)
        res[b] = dict(original=a, numeric_leaves=num, max_rel_diff=worst,
                      worst_leaf=worst_path, differing_other_leaves=sdiff[:20],
                      missing_in_rerun=[p for p in la if p not in lb][:20],
                      new_in_rerun=[p for p in lb if p not in la][:20])
        print(b, num, worst, worst_path, len(sdiff))
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
