#!/usr/bin/env python3
"""Restart check of puncture_setup: compares the registered runs psr_full (eight cycles)
and psr_restart (cycles 5 to 8 from the dump of cycle 4): tracker, horizon summary,
particle history and Z4c history at the common times."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mp_common as mc  # noqa: E402


def common(a, b, tcol):
    ta, tb = a[:, tcol], b[:, tcol]
    ia = [i for i, t in enumerate(ta) if np.any(np.abs(tb - t) < 1e-12)]
    ib = [int(np.argmin(np.abs(tb - ta[i]))) for i in ia]
    return a[ia], b[ib]


def main():
    f = mc.run_by_label("psr_full")
    r = mc.run_by_label("psr_restart")
    print("uninterrupted:", f["run_id"], " restarted:", r["run_id"])
    worst = 0.0
    for name, tcol in (("psr.co_0.txt", 1), ("psr.horizon_summary_0.txt", 1),
                       ("psr.nrpic.hst", 0), ("psr.z4c.user.hst", 0)):
        a = mc.read_table_file(os.path.join(f["output_directory"], name))
        b = mc.read_table_file(os.path.join(r["output_directory"], name))
        n = min(a.shape[1], b.shape[1])
        ca, cb = common(a[:, :n], b[:, :n], tcol)
        # the restarted run starts at cycle 4: compare the later rows only
        sel = ca[:, tcol] > 4.5 * 0.03125 if name != "psr.horizon_summary_0.txt" \
            else ca[:, tcol] > 0.13
        ca, cb = ca[sel], cb[sel]
        scale = np.maximum(np.abs(ca), 1e-30)
        rel = np.abs(ca - cb) / scale
        rel[np.abs(ca) < 1e-12] = np.abs(ca - cb)[np.abs(ca) < 1e-12]
        k = np.unravel_index(np.argmax(rel), rel.shape) if rel.size else (0, 0)
        mx = float(rel.max()) if rel.size else float("nan")
        worst = max(worst, mx) if rel.size else worst
        print(f"{name:28s} rows compared {len(ca)}, largest relative difference {mx:.2e}"
              f" (column {k[1] + 1})")
    print("tracker of the restarted run, first row:",
          mc.read_table_file(os.path.join(r["output_directory"], "psr.co_0.txt"))[0, :5])
    print("largest difference:", worst)


if __name__ == "__main__":
    main()
