#!/usr/bin/env python3
"""G2M-2 preparation: MeshBlock counts of the candidate card cases (start rule and first
regrid at t = 0), from tree3.py and from `athena -m` of the release processor executable.

A card allocates max_nmb_per_rank slots at the start and stops when the tree needs more
(athenak/src/mesh/build_tree.cpp lines 270-282 at the start, mesh/mesh_refinement.cpp
lines 494-500 at a regrid), so a case needs slots >= max(start, first regrid).
Candidates: P1's input (R8, R16n) and smaller three-hole meshes for the 32^3 rate test:
P1 with 8 or 9 levels, core's by_triple with 6, 7 or 8 levels.
Usage: bench_cases.py <out>   (writes <out>/bench_cases.json)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model_run as mr  # noqa: E402
import tree3 as t3  # noqa: E402

CASES = [
    # name, input, nx, num_levels
    ("P1_R8", mr.P1_INPUT, 64, 10),
    ("P1_R16n", mr.P1_INPUT, 64, 11),
    ("P1_L9", mr.P1_INPUT, 64, 9),
    ("P1_L8", mr.P1_INPUT, 64, 8),
    ("by_triple_L8", mr.BY_TRIPLE, 64, 8),
    ("by_triple_L7", mr.BY_TRIPLE, 64, 7),
    ("by_triple_L6", mr.BY_TRIPLE, 64, 6),
]


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    rows = []
    for name, path, nx, nl in CASES:
        inp = t3.read_athinput(path)
        pos = np.array([p[3] for p in t3.punctures(inp, nl)])
        for b in (16, 32):
            T = t3.Tree(inp, nx=nx, num_levels=nl, block=b)
            st = T.build(pos, start=True)
            rg = T.build(pos, start=False)
            ov = [f"mesh/nx{a}={nx}" for a in (1, 2, 3)] + \
                 [f"meshblock/nx{a}={b}" for a in (1, 2, 3)] + \
                 [f"mesh_refinement/num_levels={nl}"]
            n_ex, per_ex = mr.athena_m(path, out, f"{name}_b{b}", ov)
            r = dict(case=f"{name}_b{b}", input=path, nx=nx, num_levels=nl, block=b,
                     h_min=T.h(T.lmax), start=t3.total(st), regrid=t3.total(rg),
                     start_levels=st, regrid_levels=rg, athena_m=n_ex,
                     athena_m_equal=(per_ex == st),
                     cells_start_M=t3.total(st) * b ** 3 / 1e6,
                     cells_regrid_M=t3.total(rg) * b ** 3 / 1e6)
            rows.append(r)
            print("%-16s b%d  start %5d  regrid %5d  athena -m %5d %s  cells %.1f / %.1f M  h_min %.4g"
                  % (name, b, r["start"], r["regrid"], n_ex,
                     "equal" if r["athena_m_equal"] else "DIFF", r["cells_start_M"],
                     r["cells_regrid_M"], r["h_min"]))
    json.dump(dict(rows=rows, exe=mr.EXE_CPU), open(os.path.join(out, "bench_cases.json"), "w"),
              indent=1, default=str)


if __name__ == "__main__":
    main()
