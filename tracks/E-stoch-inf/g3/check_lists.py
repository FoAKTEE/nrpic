#!/usr/bin/env python3
"""Every override of a batch list must name a line its deck already has (athenak/src/parameter_input.cpp line
400 stops the run otherwise; the pilot's k and l members, g3/JOURNAL.md entry 5). Run from the worktree root:
    python3 tracks/E-stoch-inf/g3/check_lists.py tracks/E-stoch-inf/g3/inputs/*.list
Prints per list the number of runs and the overrides missing from the deck; exit status 1 if any is missing."""
import sys


def keys(deck):
    blk, s = None, set()
    for line in open(deck):
        t = line.split("#")[0].strip()
        if t.startswith("<"):
            blk = t.strip("<>")
        elif "=" in t:
            s.add((blk, t.split("=")[0].strip()))
    return s


bad_any = False
for f in sys.argv[1:]:
    bad, n = set(), 0
    for line in open(f):
        if line.startswith("#") or not line.strip():
            continue
        tok = line.split()
        K = keys(tok[1])
        n += 1
        for o in tok[2:]:
            b, k = o.split("=")[0].split("/")
            if (b, k) not in K:
                bad.add(o.split("=")[0])
    bad_any |= bool(bad)
    print(f, n, "missing:", sorted(bad))
sys.exit(1 if bad_any else 0)
