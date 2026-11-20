#!/usr/bin/env python3
"""Check of the reader adopted into gw_diag (gwdiag/binio.py, wave 3 round 1): on real dumps
of registered runs it returns the same arrays, bit for bit, as the two readers it merges
(waves/wlib/measure.read_bin and first_source/fslib/binread.read_bin, both read only here)
and, for single-precision files, as gw_diag's old readers.read_bin.

    python3 check_readers.py <bin file> [...]      (through nrpic-run; JSON to stdout and
                                                    $NRPIC_RUN_DIR/check_readers.json)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from wlib import TRACK, measure  # noqa: E402
sys.path.insert(0, os.path.join(TRACK, "first_source"))
from fslib import binread  # noqa: E402
from gwdiag import binio, readers  # noqa: E402


def main():
    out = {}
    for p in sys.argv[1:]:
        new = binio.read_bin(p)
        newz = binio.read_bin(p, strip_prefix=True)
        a = measure.read_bin(p)
        b = binread.read_bin(p)
        r = {"var_size": new["var_size"], "nblocks": new["nblocks"], "shape": new["shape"],
             "time": new["time"], "variables": len(new["variables"])}
        r["equal_first_source"] = all(np.array_equal(new[n], b[n]) for n in new["variables"])
        r["equal_waves_measure"] = all(np.array_equal(newz[n[4:] if n.startswith("z4c_") else n],
                                                      a[n[4:] if n.startswith("z4c_") else n])
                                       for n in new["variables"])
        r["grid_equal"] = (new["grid"].n == a["grid"].n == b["grid"].n
                           and np.allclose(new["grid"].L, a["grid"].L))
        if new["var_size"] == 4:
            g = readers.read_bin(p)
            r["equal_gwdiag_old"] = all(np.array_equal(new[n], g[n]) for n in new["variables"])
        else:
            try:
                g = readers.read_bin(p)
                r["old_reader_misreads"] = not all(np.array_equal(new[n], g[n]) for n in new["variables"])
            except Exception as e:  # noqa: BLE001
                r["old_reader_misreads"] = f"raises {type(e).__name__}"
        out[p] = r
    txt = json.dumps(out, indent=1)
    print(txt)
    if "NRPIC_RUN_DIR" in os.environ:
        with open(os.path.join(os.environ["NRPIC_RUN_DIR"], "check_readers.json"), "w") as f:
            f.write(txt)
    ok = all(v["equal_first_source"] and v["equal_waves_measure"] and v["grid_equal"]
             and v.get("equal_gwdiag_old", True) for v in out.values())
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
