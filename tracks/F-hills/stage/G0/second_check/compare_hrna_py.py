#!/usr/bin/env python3
"""SC2: the track's driver geodesic_binary/hrna.py (laws newton and hrna, 2404 data, release
4 r_t, stop 30 r_t) at the same 180 phases as scan.py for r_p = 8 and 13 M, q = 10. Needs numba
(the uv environment scratch/F-hills/venv-gb). Usage: compare_hrna_py.py <outdir> [nproc]
Writes hrna_py.jsonl; the comparison with scan.jsonl is made by figures.py."""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "geodesic_binary"))


def one(args):
    law, rp, phase = args
    sys.path.insert(0, GB)
    import hrna
    o = hrna.run_encounter(law=law, mb=0.1, q12=1.0, a0=3.0, rp=rp, phase=phase, sense=1,
                           r0_rt=4.0, rf_rt=30.0)
    return dict(law=law, rp=rp, phase=phase, outcome=int(o["outcome"]),
                separated=bool(o["separated"]), plunged=int(o["plunged"]),
                E1_u=float(o["E1_u"]), E2_u=float(o["E2_u"]), status=int(o["status"]),
                r_peri=float(o["r_peri"]))


def main(out, nproc):
    os.makedirs(out, exist_ok=True)
    phases = np.linspace(0.0, 2 * math.pi, 180, endpoint=False)
    jobs = [(law, rp, float(ph)) for law in ("newton", "hrna") for rp in (8.0, 13.0)
            for ph in phases]
    with Pool(nproc) as pool, open(os.path.join(out, "hrna_py.jsonl"), "w") as fh:
        for r in pool.imap_unordered(one, jobs, chunksize=4):
            r = {k: (None if isinstance(v, float) and not math.isfinite(v) else v)
                 for k, v in r.items()}
            fh.write(json.dumps(r) + "\n")
    print("done", len(jobs))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir", nargs="?", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--nproc", type=int, default=4)
    a = ap.parse_args()
    main(a.outdir, a.nproc)
