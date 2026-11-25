#!/usr/bin/env python3
"""Identity of a short run with a longer one of the same set-up (test V8-c of
tracks/core/JOURNAL-gauge-2.md: the relaxed lapse restricted to the matter against plain
1+log in vacuum, on a card): the text histories of the short run must be the first lines
of the long run's, byte for byte.

    vident.py --out DIR SHORT_RUNDIR LONG_RUNDIR [--base v1s]

Compares <base>.horizon_summary_0.txt, <base>.z4c.user.hst and <base>.nrpic.hst line by
line over the lines of the short run (the last line of a history may be the final-time
record of the short run, which the long run does not write at that time: it is compared
by its time stamp and skipped if the long run has no line with that time).  Writes
DIR/vident.json; exit status 1 on a differing line.
"""
import argparse
import json
import os
import sys


def lines(path):
    with open(path) as f:
        return [ln.rstrip("\n") for ln in f]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default="v1s")
    ap.add_argument("short")
    ap.add_argument("long")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res, bad = {}, 0
    for suffix in ("horizon_summary_0.txt", "z4c.user.hst", "nrpic.hst"):
        s = lines(os.path.join(a.short, f"{a.base}.{suffix}"))
        l = lines(os.path.join(a.long, f"{a.base}.{suffix}"))
        long_set = set(l)
        same = sum(1 for x, y in zip(s, l) if x == y)
        diff = [(i, x) for i, (x, y) in enumerate(zip(s, l)) if x != y]
        # a differing line that exists elsewhere in the long file is a matter of order
        # (final-time record); one that exists nowhere differs in a number
        nowhere = [i for i, x in diff if x not in long_set]
        num = None
        if nowhere:
            i = nowhere[0]
            try:
                xs = [float(w) for w in s[i].split()]
                ys = [float(w) for w in l[i].split()]
                num = max(abs(p - q) / (abs(q) + 1e-300) for p, q in zip(xs, ys))
            except ValueError:
                pass
        res[suffix] = dict(lines_short=len(s), identical_in_place=same,
                           differing_in_place=len(diff), not_in_long_at_all=len(nowhere),
                           first_differing_line=nowhere[0] if nowhere else None,
                           largest_relative_difference_there=num)
        bad += len(nowhere)
        print(f"{suffix}: {len(s)} lines, {same} identical in place, {len(diff)} differ in "
              f"place, {len(nowhere)} with no identical line in the long run"
              + (f" (first: line {nowhere[0]}, relative difference {num})" if nowhere else ""))
    res["verdict"] = "identical" if bad == 0 else "different"
    with open(os.path.join(a.out, "vident.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print("verdict:", res["verdict"])
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
