#!/usr/bin/env python3
"""T16 of the work package cosmo-amr: the finder's hmean_tol in the cosmological box
(prediction: tracks/core/JOURNAL-cosmo-amr.md).  Track A's S1 data at t = 0 on the uniform
64^3 mesh, two cycles, a search every cycle from a sphere of coordinate radius 2:

    t16_hmean.py --exe EXE --data DIR --out DIR

  tol100   hmean_tol_0 = 100 (the value of the track's decks)
  tolbig   hmean_tol_0 = 1e30 (the example input now)
Writes DIR/t16_summary.json (the status lines of both cases)."""
import argparse
import json
import os
import sys

import amrlib as A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    a.out, a.exe, a.data = (os.path.abspath(a.out), os.path.abspath(a.exe),
                            os.path.abspath(a.data))
    os.makedirs(a.out, exist_ok=True)
    deck = A.Inp(os.path.join(A.ROOT, "problems/cosmo_amr/peak_amr.athinput"))
    common = ["time/nlim=2", f"problem/id_file={a.data}/fields.bin",
              f"particles/particle_file={a.data}/particles.nrp", "fastflow/start_time_0=0.0",
              "fastflow/find_every=1", "mesh_refinement/max_nmb_per_rank=100",
              "output7/dt=100.0", "fastflow/flow_iterations_0=400"]
    cases = {"tol100": ["fastflow/hmean_tol_0=100.0"], "tolbig": ["fastflow/hmean_tol_0=1.0e30"]}
    rcs = A.run_many([(a.exe, deck, os.path.join(a.out, n), "peak", tuple(common + cases[n]),
                       None) for n in cases], 2)
    res = {}
    for n, rc in zip(cases, rcs):
        rows = []
        with open(os.path.join(a.out, n, "peak.horizon_status_0.txt")) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                w = line.split("#")
                v = [float(x) for x in w[0].split()]
                rows.append({"cycle": int(v[0]), "time": v[1], "found": int(v[2]),
                             "reason": int(v[3]), "flow_iterations": int(v[4]), "area": v[5],
                             "area_mass": v[6], "mean_radius": v[7], "min_radius": v[8],
                             "expansion_integral": v[9], "min_abs_expansion_integral": v[10],
                             "points_outside": int(v[11]), "words": w[1].strip()})
        res[n] = {"exit": rc[0], "wall_s": rc[1], "searches": rows}
        for r in rows:
            print(n, json.dumps(r))
    with open(os.path.join(a.out, "t16_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
