#!/usr/bin/env python3
"""Test T4, write and read without a step (prediction P4d of tracks/core/JOURNAL-mpi.md):
restart the dump of cycle 20 written on w ranks on r ranks with time/nlim=20, so that the
run takes no step and writes its final dump at cycle 20, and compare that dump with the
one it read: the particle restart file byte for byte, the mesh restart file after its
parameter header (and the bytes of its binary header separately).

    restart_zero.py --src DIR --pairs 1:2 2:1 ... [--rst rst/cl.00001.rst] [--exe EXE]
                    [--out DIR] [--max-cores 16]
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mpi_tests as mt  # noqa: E402


def compare(a, b):
    """bytes of two files: identical, or the number of differing bytes and their range"""
    x, y = open(a, "rb").read(), open(b, "rb").read()
    if x == y:
        return dict(identical=True, size=len(x))
    n = min(len(x), len(y))
    diff = np.nonzero(np.frombuffer(x[:n], np.uint8) != np.frombuffer(y[:n], np.uint8))[0]
    return dict(identical=False, sizes=[len(x), len(y)], differing=len(diff),
                first=int(diff[0]) if len(diff) else None,
                last=int(diff[-1]) if len(diff) else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--pairs", nargs="+", required=True)
    ap.add_argument("--rst", default="rst/cl.00001.rst")
    ap.add_argument("--exe", default=mt.DEFAULT_EXE)
    ap.add_argument("--out", default="t4_zero")
    ap.add_argument("--max-cores", type=int, default=16)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    pairs = [tuple(int(v) for v in q.split(":")) for q in a.pairs]
    res = {}
    # run in groups that stay within the allotment of cores
    queue = list(pairs)
    while queue:
        group, used = [], 0
        while queue and used + queue[0][1] <= a.max_cores:
            group.append(queue.pop(0))
            used += group[-1][1]
        procs = []
        for w, r in group:
            d = os.path.join(out, "z%dr%d" % (w, r))
            os.makedirs(d, exist_ok=True)
            cmd = [mt.MPIRUN, "--bind-to", "none", "-np", str(r), a.exe, "-r",
                   os.path.join(os.path.abspath(a.src), "np%d" % w, a.rst), "-d", d,
                   "time/nlim=20"]
            log = open(os.path.join(d, "run.log"), "w")
            procs.append(((w, r), d, subprocess.Popen(
                cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                env=dict(os.environ, OMP_NUM_THREADS="1")), log, time.time()))
        for (w, r), d, p, log, t0 in procs:
            rc = p.wait()
            log.close()
            src_rst = os.path.join(os.path.abspath(a.src), "np%d" % w, a.rst)
            new = sorted(glob.glob(os.path.join(d, "rst", "*.rst")))
            row = dict(exit=rc, wall_s=round(time.time() - t0, 1),
                       written=[os.path.basename(f) for f in new])
            if new:
                f = new[-1]
                row["prt"] = compare(src_rst + ".prt", f + ".prt")
                ka = open(src_rst, "rb").read()
                kb = open(f, "rb").read()
                ia, ib = ka.find(b"<par_end>"), kb.find(b"<par_end>")
                row["rst_after_header"] = (ka[ia:] == kb[ib:])
                if not row["rst_after_header"]:
                    m = min(len(ka) - ia, len(kb) - ib)
                    diff = np.nonzero(np.frombuffer(ka[ia:ia + m], np.uint8)
                                      != np.frombuffer(kb[ib:ib + m], np.uint8))[0]
                    row["rst_differing_bytes"] = int(len(diff))
                    row["rst_differing_range_after_par_end"] = (
                        [int(diff[0]), int(diff[-1])] if len(diff) else None)
            res["%d:%d" % (w, r)] = row
            print("%d:%d exit %d  prt %s  rst after header %s" % (
                w, r, rc, "identical" if row.get("prt", {}).get("identical") else row.get("prt"),
                "identical" if row.get("rst_after_header") else
                "%s bytes differ in %s" % (row.get("rst_differing_bytes"),
                                           row.get("rst_differing_range_after_par_end"))),
                flush=True)
    with open(os.path.join(out, "zero.json"), "w") as fjs:
        json.dump(res, fjs, indent=1)
    return 0 if all(v["exit"] == 0 for v in res.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
