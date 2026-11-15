#!/usr/bin/env python3
"""Regression of the conformally flat problem generator with a format-1 table: compares
the outputs of two runs of problems/tests/cf_table_regress.athinput byte by byte.

    regress_format1.py <rundir before> <rundir after> [--start-only]

Compared: every file below the two directories except the logs (run.log, athena*.log,
*.gpumem.csv, slurm-*.out, the copied input and executable), which hold wall-clock
times.  In a mesh restart file (*.rst) 36 bytes are left out: the nine coarse-cell
members (cnx1 ... cke) of Mesh::mesh_indcs, which the mesh never sets and which the
restart output writes as they are in memory (athenak/src/outputs/restart.cpp:226,
athenak/src/mesh/mesh.hpp:40-41); they differ between two runs of one executable.

--start-only compares only what describes the start: the first restart files, the first
snapshot and the first record of each history file.  This is the comparison for card
runs, whose deposit adds the particles in an order that changes from run to run, so that
two runs of one executable differ from the first step on.

Exit status 0 and "IDENTICAL" if no compared byte differs.
"""
import os
import sys

SKIP_SUFFIX = (".log", ".gpumem.csv", ".athinput", ".exe")


def files(root):
    out = []
    for d, _, names in os.walk(root):
        for n in names:
            if n.startswith("slurm-") or n.endswith(SKIP_SUFFIX):
                continue
            out.append(os.path.relpath(os.path.join(d, n), root))
    return sorted(out)


def rst_mask(data):
    """(start, stop) of the unset members of mesh_indcs in a restart file."""
    i = data.find(b"<par_end>")
    if i < 0:
        return None
    hdr = i + len(b"<par_end>\n")
    start = hdr + 2 * 4 + 9 * 8 + 10 * 4      # nmb_total, root_level, RegionSize, 10 ints
    return start, start + 9 * 4


def first_record(data):
    for line in data.split(b"\n"):
        if line and not line.startswith(b"#"):
            return line
    return b""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    start_only = "--start-only" in sys.argv
    a, b = args
    fa, fb = files(a), files(b)
    if fa != fb:
        print("DIFFERENT: the two runs wrote different sets of files")
        print(sorted(set(fa) ^ set(fb)))
        return 1
    status, n = 0, 0
    for f in fa:
        if start_only and not (f.endswith(".hst") or ".00000." in f):
            continue
        with open(os.path.join(a, f), "rb") as fh:
            da = fh.read()
        with open(os.path.join(b, f), "rb") as fh:
            db = fh.read()
        note = ""
        if f.endswith(".rst"):
            ma, mb = rst_mask(da), rst_mask(db)
            if ma is not None and ma == mb:
                da = da[:ma[0]] + da[ma[1]:]
                db = db[:mb[0]] + db[mb[1]:]
                note = " (36 unset bytes left out)"
        elif start_only and f.endswith(".hst"):
            da, db = first_record(da), first_record(db)
            note = " (first record)"
        same = da == db
        n += 1
        status |= 0 if same else 1
        print("  %-9s %12d bytes  %s%s" % ("same" if same else "DIFFERENT", len(da), f, note))
    print(("IDENTICAL" if status == 0 else "DIFFERENT") + f" ({n} files compared)")
    return status


if __name__ == "__main__":
    sys.exit(main())
