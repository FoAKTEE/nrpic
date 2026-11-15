#!/usr/bin/env python3
"""Draws keyed by cells do not depend on the division into MeshBlocks.

Runs the problem generator ``rng_test`` with ``cell_check = true`` on a mesh of 32^3
root cells in [-1,1]^3:
  uniform mesh, MeshBlocks of 32^3, 16^3 and 8^3 cells (1, 8, 64 MeshBlocks);
  one refinement level in the octant [0,1]^3, MeshBlocks of 16^3 and of 8^3 cells (both
  divisions refine exactly the octant);
  two refinement levels (level 1 in [0,1]^3, level 2 in [0,0.5]^3), MeshBlocks of 16^3
  and of 8^3 cells. Here AthenaK refines further MeshBlocks around the second level,
  differently for the two divisions, so only the finest level holds the same cells.
The code writes, per refinement level, the number of cells and a checksum of a raw word
and a normal deviate drawn for every cell (utils/rng_mesh.hpp). The script compares the
checksums with the same sum from the Python twin, in which the cells of each level are
listed from the geometry alone (so equal checksums also mean equal checksums between
the divisions).

Usage: run_cell_check.py --exe ATHENA     (runs in the current directory; summary.json)
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import rng  # noqa: E402

SEED = 20261115
SMR1 = """
<mesh_refinement>
refinement = static

<refined_region1>
level = 1
x1min = 0.0
x1max = 1.0
x2min = 0.0
x2max = 1.0
x3min = 0.0
x3max = 1.0
"""
SMR2 = SMR1 + """
<refined_region2>
level = 2
x1min = 0.0
x1max = 0.5
x2min = 0.0
x2max = 0.5
x3min = 0.0
x3max = 0.5
"""


def twin_checksum(level, lo, hi, hole=None):
    """Checksum of the cells with global indices in [lo, hi)^3 on a level, without those
    in hole = (lo, hi), as the code forms it."""
    idx = np.arange(lo, hi, dtype=np.uint64)
    k, j, i = np.meshgrid(idx, idx, idx, indexing="ij")
    if hole is not None:
        inside = ((i >= hole[0]) & (i < hole[1]) & (j >= hole[0]) & (j < hole[1])
                  & (k >= hole[0]) & (k < hole[1]))
        i, j, k = i[~inside], j[~inside], k[~inside]
    key = dict(seed=SEED, stream=rng.stream(rng.STREAM_TESTS, 6),
               entity=rng.cell_entity(i.ravel(), j.ravel(), k.ravel()), step=3,
               entity_hi=level, draw=0)
    w = rng.bits(**key)
    zb = rng.normal(**key).view(np.uint64)
    h = w ^ ((zb << np.uint64(17)) | (zb >> np.uint64(47)))
    with np.errstate(over="ignore"):
        return int(h.size), f"{int(np.sum(h, dtype=np.uint64)):016x}"


def read_cells(path):
    out = {}
    with open(path) as fp:
        for line in fp:
            f = line.split()
            if f and f[0] == "level":
                out[int(f[1])] = (int(f[3]), f[5])
            elif f and f[0] == "meshblocks":
                out["meshblocks"] = int(f[1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    args = ap.parse_args()
    exe = os.path.abspath(args.exe)
    top = os.getcwd()
    base = open(os.path.join(REPO, "problems", "tests", "rng_test.athinput")).read()
    with open(os.path.join(top, "uniform.athinput"), "w") as fp:
        fp.write(base)
    with open(os.path.join(top, "smr1.athinput"), "w") as fp:
        fp.write(base + SMR1)
    with open(os.path.join(top, "smr2.athinput"), "w") as fp:
        fp.write(base + SMR2)
    runs = {"uniform_32": ("uniform", 32), "uniform_16": ("uniform", 16),
            "uniform_8": ("uniform", 8), "smr1_16": ("smr1", 16), "smr1_8": ("smr1", 8),
            "smr2_16": ("smr2", 16), "smr2_8": ("smr2", 8)}
    res = {}
    for name, (inp, nb) in runs.items():
        rd = os.path.join(top, name)
        os.makedirs(rd, exist_ok=True)
        cmd = [exe, "-i", os.path.join(top, inp + ".athinput"), "mesh/nx1=32",
               "mesh/nx2=32", "mesh/nx3=32", f"meshblock/nx1={nb}", f"meshblock/nx2={nb}",
               f"meshblock/nx3={nb}", "problem/cell_check=true", f"job/rng_seed={SEED}",
               "-d", rd]
        with open(os.path.join(rd, "athena.log"), "w") as log:
            subprocess.run(cmd, cwd=rd, stdout=log, stderr=subprocess.STDOUT, check=True)
        res[name] = read_cells(os.path.join(rd, "rngtest.rng_cells.txt"))
        print(name, res[name], flush=True)
    # cells of each level from the geometry; for the two-level mesh only the finest
    twin = {
        "uniform": {0: twin_checksum(0, 0, 32)},
        "smr1": {0: twin_checksum(0, 0, 32, hole=(16, 32)),
                 1: twin_checksum(1, 32, 64)},
        "smr2": {2: twin_checksum(2, 64, 96)},
    }
    print("twin", twin, flush=True)
    checks = {}
    for name, (inp, nb) in runs.items():
        levels = {k: v for k, v in res[name].items() if k != "meshblocks"}
        checks[name] = bool(all(lv in levels and tuple(levels[lv]) == tuple(twin[inp][lv])
                                for lv in twin[inp])
                            and (inp == "smr2" or set(levels) == set(twin[inp])))
    ok = all(checks.values())
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump({"exe": exe, "code": {k: {str(a): b for a, b in v.items()}
                                        for k, v in res.items()},
                   "twin": {k: {str(a): b for a, b in v.items()} for k, v in twin.items()},
                   "equal_to_twin": checks, "ok": ok}, fp, indent=1)
    print(json.dumps({"equal_to_twin": checks, "ok": ok}, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
