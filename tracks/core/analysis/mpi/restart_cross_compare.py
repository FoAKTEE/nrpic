#!/usr/bin/env python3
"""Test T4, prediction P4e: the restarted runs compared with each other (not with the
uninterrupted runs, from which every restart departs at the outer boundary, also on one
rank).  Sets of restarted runs that read the same dump on different numbers of ranks,
and the restarts of the dumps of 1, 2, 4 ranks each on its own rank count, are compared
with mpi_tests.compare_case (symbolic links np<N> to the restarted run directories).

    restart_cross_compare.py <dir of the same-rank restarts> <dir of the cross restarts> <out>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mpi_tests as mt  # noqa: E402


def main():
    same, cross, out = (os.path.abspath(p) for p in sys.argv[1:4])
    sets = {
        "file of 1 rank, read on 1 and 4": ([1, 4], {1: (same, "w1r1"), 4: (cross, "w1r4")}),
        "file of 4 ranks, read on 4 and 1": ([4, 1], {4: (same, "w4r4"), 1: (cross, "w4r1")}),
        "file of 2 ranks, read on 2 and 4": ([2, 4], {2: (same, "w2r2"), 4: (cross, "w2r4")}),
        "files of 1, 2, 4 ranks, each read on its own": (
            [1, 2, 4], {1: (same, "w1r1"), 2: (same, "w2r2"), 4: (same, "w4r4")}),
    }
    res = {}
    for k, (name, (ranks, dirs)) in enumerate(sets.items()):
        base = os.path.join(out, "set%d" % k)
        os.makedirs(base, exist_ok=True)
        for n, (root, sub) in dirs.items():
            link = os.path.join(base, "np%d" % n)
            if not os.path.islink(link):
                os.symlink(os.path.join(root, sub), link)
        r = mt.compare_case("t3_cluster_ext", ranks, base)
        res[name] = r
        print("== %s (reference: %d rank%s)" % (name, ranks[0], "" if ranks[0] == 1 else "s"))
        for line in mt.summary_lines(r):
            if line.startswith(("history", "snap", "line", "identity", "bytes   cl.trajmet",
                                "fdump")):
                print("   " + line)
    with open(os.path.join(out, "cross_compare.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
