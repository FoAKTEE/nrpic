#!/usr/bin/env python3
"""X1 follow-up: where do the files that differ between the two executables differ?

For each pair (gauge/<f>, v04/<f>) that is not byte-identical, report the differing byte
offsets, whether all of them lie inside the text header (AthenaK bin and restart files
start with the parameter dump, ended by the line '<par_end>'), and the header lines that
differ. A difference outside the header is a difference of data.
Usage: x1_locate.py <X1 run dir>
"""
import os
import sys

run = sys.argv[1]
names = [l.split(None, 1)[1].strip() for l in open(os.path.join(run, "x1_compare.txt"))
         if l.startswith("differs ")]
for n in names:
    a = open(os.path.join(run, "gauge", n), "rb").read()
    b = open(os.path.join(run, "v04", n), "rb").read()
    m = min(len(a), len(b))
    diff = [i for i in range(m) if a[i] != b[i]]
    end = a.find(b"<par_end>")
    hdr_end = end + len("<par_end>") if end >= 0 else -1
    in_hdr = all(i < hdr_end for i in diff) and len(a) == len(b)
    print(f"{n}: sizes {len(a)} {len(b)}; {len(diff)} differing bytes, first {diff[:1]}, "
          f"last {diff[-1:]}; header ends at {hdr_end}; all inside header: {in_hdr}")
    if hdr_end > 0:
        la = a[:hdr_end].decode(errors="replace").splitlines()
        lb = b[:hdr_end].decode(errors="replace").splitlines()
        for x, y in zip(la, lb):
            if x != y:
                print(f"   gauge: {x.strip()}\n   v04:   {y.strip()}")
    out = [i for i in diff if i >= hdr_end]
    if out:
        print(f"   bytes outside the header: {len(out)}, offsets {out[0]}..{out[-1]}")
