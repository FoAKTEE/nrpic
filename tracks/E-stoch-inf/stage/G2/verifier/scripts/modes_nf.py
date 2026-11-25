"""Coefficients of R^NR on the band modes (|n|^2 <= 4096) at N_f (dump 20) of every
256/320 release run, and at t = 0 of U256ap and U256bp (extraction check V3). One
variable of one dump in memory at a time. Writes <label>_d<k>.npz caches.

python3 modes_nf.py --out DIR [--labels ...]
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

DEFAULT = ["U256ap", "U256am", "U256bp", "U256bm", "U256hp", "U256hm", "U256qp", "U256qm",
           "U320ap", "U320am"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--labels", nargs="*", default=DEFAULT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    n = vlib.hemisphere(4096)
    np.save(os.path.join(a.out, "modes_n.npy"), n)
    jobs = [(lab, 20) for lab in a.labels] + [("U256ap", 0), ("U256bp", 0)]
    log = {}
    for lab, k in jobs:
        t0 = time.time()
        p = vlib.dump_path(lab, k)
        full = (k == 20)
        r = vlib.rnr_from_dump(p, n, want_full=full, want_parts=True)
        np.savez(os.path.join(a.out, f"{lab}_d{k:02d}.npz"), c=r["c"], c_phi=r["c_phi"],
                 c_chi=r["c_chi"], c_gt=r["c_gt"])
        meta = {kk: v for kk, v in r.items() if not kk.startswith("c")}
        meta["wall_s"] = time.time() - t0
        log[f"{lab}_d{k:02d}"] = meta
        print(lab, k, json.dumps(meta), flush=True)
        json.dump(log, open(os.path.join(a.out, "modes_nf.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
