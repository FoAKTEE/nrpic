#!/usr/bin/env python3
"""Check of the gauge piece adopted into gw_diag (gwdiag/gauge.py, wave 3 round 1): on real
dumps it returns the same G and G_tot as first_source/fslib/gauge.py (read only here), and
tt_strain's corrected strain is Lambda h - G_tot.

    python3 check_gauge.py <z4c bin file> [...]     (through nrpic-run; JSON to stdout and
                                                     $NRPIC_RUN_DIR/check_gauge.json)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from wlib import TRACK  # noqa: E402
sys.path.insert(0, os.path.join(TRACK, "first_source"))
from fslib import gauge as fs_gauge  # noqa: E402
from gwdiag import binio, gauge, readers  # noqa: E402


def rms(x):
    return float(np.sqrt(np.mean(np.einsum("ab...,ab...->...", x, x))))


def main():
    out = {}
    for p in sys.argv[1:]:
        d = binio.read_bin(p, strip_prefix=True)
        g = d["grid"]
        _, gt, _, _, _, _ = readers.z4c_tensors(d)
        h = gt - np.eye(3)[:, :, None, None, None]
        s = gauge.tt_strain(h, g)
        G_old = fs_gauge.gauge_piece_total(h, g)
        G1_old = fs_gauge.gauge_piece(h, g)
        G1_new = gauge.gauge_piece(h, g)
        out[p] = {"time": d["time"], "n": g.n, "var_size": d["var_size"],
                  "G_tot_equal_first_source": bool(np.array_equal(s["G"], G_old)),
                  "G_equal_first_source": bool(np.array_equal(G1_new, G1_old)),
                  "max_abs_diff_G_tot": float(np.max(np.abs(s["G"] - G_old))),
                  "rms_raw": rms(s["raw"]), "rms_G_tot": rms(s["G"]),
                  "rms_corrected": rms(s["corrected"]),
                  "corrected_is_raw_minus_G": bool(np.array_equal(s["corrected"], s["raw"] - s["G"]))}
    txt = json.dumps(out, indent=1)
    print(txt)
    if "NRPIC_RUN_DIR" in os.environ:
        with open(os.path.join(os.environ["NRPIC_RUN_DIR"], "check_gauge.json"), "w") as f:
            f.write(txt)
    ok = all(v["G_tot_equal_first_source"] and v["G_equal_first_source"] and v["corrected_is_raw_minus_G"]
             for v in out.values())
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
