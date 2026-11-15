#!/usr/bin/env python3
"""Regression case c5 of run_regression.py: where do the restart files of the baseline
and of the new executable differ?

The restart header is: parameter dump ending in "<par_end>\\n", int nmb_total, int
root_level, RegionSize mesh_size (9 doubles), RegionIndcs mesh_indcs (19 ints),
RegionIndcs mb_indcs, ... (outputs/restart.cpp).  The last nine ints of mesh_indcs (the
coarse-mesh indices cnx1 ... cke) are never set for the root mesh, so the file holds 36
bytes of whatever the heap contained.  This script lists the differing bytes of every
restart file of the case and says whether all of them lie in that range.

Usage: check_rst_diff.py <regression output directory> [case]   (writes rst_diff.json
into the current directory)
"""
import glob
import json
import os
import sys

import numpy as np


def main():
    top = os.path.abspath(sys.argv[1])
    case = sys.argv[2] if len(sys.argv) > 2 else "c5"
    out = {"regression": top, "case": case, "files": {}}
    ok = True
    for fa in sorted(glob.glob(os.path.join(top, case, "base", "rst", "*.rst"))):
        name = os.path.basename(fa)
        a = np.fromfile(fa, dtype=np.uint8)
        b = np.fromfile(os.path.join(top, case, "new", "rst", name), dtype=np.uint8)
        same_size = a.size == b.size
        diff = np.nonzero(a != b)[0] if same_size else np.array([-1])
        head = bytes(a[:200000])
        p = head.find(b"<par_end>\n") + len(b"<par_end>\n")
        lo = p + 4 + 4 + 9*8 + 10*4          # first unset int of mesh_indcs
        hi = lo + 9*4                        # one past the last
        inside = bool(same_size and diff.size > 0 and diff.min() >= lo and diff.max() < hi)
        out["files"][name] = dict(size=int(a.size), same_size=bool(same_size),
                                  differing_bytes=int(diff.size),
                                  first=int(diff.min()) if diff.size else None,
                                  last=int(diff.max()) if diff.size else None,
                                  unset_range=[int(lo), int(hi - 1)],
                                  all_inside_unset_range=inside or diff.size == 0)
        ok = ok and (inside or diff.size == 0)
    out["ok"] = ok
    with open("rst_diff.json", "w") as fp:
        json.dump(out, fp, indent=1)
    print(json.dumps(out, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
