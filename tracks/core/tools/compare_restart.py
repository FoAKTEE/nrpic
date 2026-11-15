#!/usr/bin/env python3
"""Compare a continued run with the uninterrupted one (test T5).

    compare_restart.py FULL_RUNDIR CONTINUED_RUNDIR

Particle snapshots present in both directories are compared byte for byte; the history
files (*.newton.hst, *.nrpic.hst) are compared as text, record by record, for the cycles
that the continued run wrote. Exit status 0 if everything is identical.
"""
import filecmp
import glob
import os
import sys


def records(path):
    out = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            out[int(line.split()[1])] = line.rstrip("\n")
    return out


def main():
    full, cont = sys.argv[1], sys.argv[2]
    bad = 0
    snaps = sorted(os.path.basename(p) for p in glob.glob(os.path.join(cont, "*.part.*.bin")))
    same = [s for s in snaps if filecmp.cmp(os.path.join(full, s), os.path.join(cont, s),
                                            shallow=False)]
    print("snapshots: %d written by the continued run, %d identical" % (len(snaps),
                                                                        len(same)))
    bad += len(snaps) - len(same)
    for pat in ("*.newton.hst", "*.nrpic.hst"):
        fa, fb = glob.glob(os.path.join(full, pat)), glob.glob(os.path.join(cont, pat))
        if not fa or not fb:
            continue
        ra, rb = records(fa[0]), records(fb[0])
        diff = [c for c in sorted(rb) if ra.get(c) != rb[c]]
        print("%s: %d records in the continued run (cycles %d to %d), %d differ%s"
              % (pat, len(rb), min(rb), max(rb), len(diff),
                 (" (first: cycle %d)" % diff[0]) if diff else ""))
        bad += len(diff)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
