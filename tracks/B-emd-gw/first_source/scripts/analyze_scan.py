#!/usr/bin/env python3
"""Diagnostics of the crossed-wave runs (P1-P6 of JOURNAL.md).

    python3 analyze_scan.py <case dir> [<case dir> ...]     (output: $NRPIC_RUN_DIR)

Each <case dir> is an AthenaK run directory of the scan (cw_eps0, ..., cw_eps1_gd) with
bin/*.z4c.*.bin (single precision, every 0.1) and rst/*.rst (double, every 1.0). For every
dump fslib.modes.analyse: TT and non-TT parts of h and tilde A, the amplitudes h_+, h_x at
K1 = (k, k, 0) and K2 = (k, -k, 0), the spatial-gauge pieces G and G_A, the largest TT mode;
for the restart dumps also the Weyl E and B (order 6) and their TT parts.
Writes <case>.json per case; NWORK worker processes (default 8).
"""
import glob
import json
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import modes  # noqa: E402


def job(args):
    path, kind = args
    try:
        r = modes.analyse(path, with_gauge=True, with_weyl=(kind == "rst"))
    except Exception as e:                         # a broken dump is recorded, not fatal
        return {"file": os.path.basename(path), "kind": kind, "error": repr(e)}
    r["file"] = os.path.basename(path)
    r["kind"] = kind
    return r


def main():
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    nw = int(os.environ.get("NWORK", "8"))
    for cd in sys.argv[1:]:
        name = os.path.basename(cd.rstrip("/"))
        tasks = [(p, "bin") for p in sorted(glob.glob(os.path.join(cd, "bin", "*.z4c.*.bin")))]
        tasks += [(p, "rst") for p in sorted(glob.glob(os.path.join(cd, "rst", "*.rst")))]
        with Pool(nw) as pool:
            rows = pool.map(job, tasks, chunksize=1)
        rows.sort(key=lambda r: (r.get("kind"), r.get("time", 0.0)))
        with open(os.path.join(out, name + ".json"), "w") as f:
            json.dump({"case": name, "dir": os.path.abspath(cd), "rows": rows}, f)
        nerr = sum(1 for r in rows if "error" in r)
        print(f"{name}: {len(rows)} dumps, {nerr} errors", flush=True)


if __name__ == "__main__":
    main()
