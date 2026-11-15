#!/usr/bin/env python3
"""Smoke run: learn the output formats of the release executable (collision history
header, dump, snapshots) on a tiny box before the tests. Not a test; no criterion.

    python3 smoke.py            (writes into $NRPIC_RUN_DIR)
"""
import json
import os

import numpy as np

import boxlib as bl


def main():
    out = bl.outdir()
    rd = os.path.join(out, "smoke")
    meta = bl.make_box(rd, "mj", n=10000, theta=0.1, sigma=10.0, seed=3)
    ov = bl.mesh_overrides(4) + ["particles/dt=0.01", "time/nlim=20",
                                  "particles/coll_sigma=10.0", "particles/snap_dt=0.05",
                                  "particles/coll_dump_cycle=5", "job/rng_seed=7"]
    r = bl.run_athena(rd, ov)
    print(json.dumps(dict(rc=r["rc"], wall=r["wall"]), indent=1))
    print(sorted(os.listdir(rd)))
    with open(os.path.join(rd, "box.coll.hst")) as fh:
        print("".join(fh.readlines()[:4]))
    with open(os.path.join(rd, "box.nrpic.hst")) as fh:
        print("".join(fh.readlines()[:3]))
    dumps = sorted(p for p in os.listdir(rd) if "coll_dump" in p)
    for p in dumps:
        d = bl.read_dump(os.path.join(rd, p))
        print(p, {k: v for k, v in d.items() if np.isscalar(v)})
        print(" levels", np.unique(d["level"]), "nsub", np.unique(d["nsub"]),
              "nupd", np.bincount(d["nupd"]), "tags", d["tag"].min(), d["tag"].max())
        print(" alpha", np.unique(d["alpha"]), "vol", np.unique(d["vol"]))
        print(" gam", np.unique(d["gam"], axis=0))
    h = bl.coll_history(rd)
    print({k: v[:3].tolist() for k, v in h.items()})


if __name__ == "__main__":
    main()
