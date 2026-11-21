#!/usr/bin/env python3
"""Where does the restarted one-rank run of the cluster of T3 first depart from the
uninterrupted one?  Runs (serial executable, one process) the uninterrupted run to cycle
21 with restart dumps every 20 cycles and a field dump at cycle 21, then the run
restarted from the dump of cycle 20 with the same field dump, and compares the field
dumps array by array: largest difference, and its distance (in cells) from the outer
boundary of the mesh.

    restart_locate.py <exe> <particle file> <table> <outdir>
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mpi_tests as mt  # noqa: E402

INP = os.path.join(mt.REPO, "problems", "tests", "mpi_cluster.athinput")


def main():
    exe, nrp, tab, out = sys.argv[1:5]
    out = os.path.abspath(out)
    args = ["particles/particle_file=" + os.path.abspath(nrp),
            "problem/comp0_file=" + os.path.abspath(tab),
            "time/nlim=21", "particles/field_time1=3.9375", "particles/field_time2=100.0"]
    full, rest = os.path.join(out, "full"), os.path.join(out, "restart")
    env = dict(os.environ, OMP_NUM_THREADS="1")
    for d, cmd in ((full, [exe, "-i", INP, "-d", full] + args),
                   (rest, [exe, "-r", os.path.join(full, "rst", "cl.00001.rst"), "-d", rest,
                           "time/nlim=21", "particles/field_time1=3.9375"])):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "run.log"), "w") as log:
            rc = subprocess.run(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT, env=env).returncode
        print(os.path.basename(d), "exit", rc, flush=True)
    t1, a = mt.read_field(os.path.join(full, "cl.field.00001.bin"))
    t2, b = mt.read_field(os.path.join(rest, "cl.field.00001.bin"))
    res = dict(t_full=t1, t_restart=t2, arrays={})
    n3, n2, n1 = a["H"].shape
    k, j, i = np.meshgrid(np.arange(n3), np.arange(n2), np.arange(n1), indexing="ij")
    dist = np.minimum.reduce([i, j, k, n1 - 1 - i, n2 - 1 - j, n3 - 1 - k])
    for name in a:
        d = np.abs(a[name] - b[name])
        sc = max(np.abs(a[name]).max(), 1e-300)
        row = dict(max_rel=float(d.max()/sc), cells_differing=int((d > 0).sum()))
        if d.max() > 0:
            idx = np.unravel_index(np.argmax(d), d.shape)
            row["at_cell"] = [int(v) for v in idx]
            row["distance_from_boundary_of_max"] = int(dist[idx])
            row["max_rel_by_distance"] = [float(d[dist == q].max()/sc) for q in range(0, 8)]
        res["arrays"][name] = row
        print("%-6s max rel %.2e  cells differing %6d  %s" % (
            name, row["max_rel"], row["cells_differing"],
            ("max at %s, %d cells from the boundary; by distance 0..7: %s" % (
                row["at_cell"], row["distance_from_boundary_of_max"],
                " ".join("%.0e" % v for v in row["max_rel_by_distance"])))
            if "at_cell" in row else ""))
    with open(os.path.join(out, "locate.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
