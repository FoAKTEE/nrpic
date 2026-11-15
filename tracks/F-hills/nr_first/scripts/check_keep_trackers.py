#!/usr/bin/env python3
"""Checks of E5 (nr_first/JOURNAL.md) on the output of test_keep_trackers.sh, with the row
convention AthenaK actually has: the tracker writes the row of cycle n at the start of that
cycle (CompactObjectTracker::WriteTracker before the step), so a segment that stops at
nlim = N holds rows 0..N-1, and a segment restarted at cycle N writes row N first.
(The first check in test_keep_trackers.sh expected rows 0..12 after 12 cycles; the data
have 0..11, which is complete under this convention.)
Usage: check_keep_trackers.py <run directory of test_keep_trackers.sh> [outdir]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nrread as nr  # noqa: E402

N1, N2 = 8, 12                     # nlim of segment 1 and of the restarted segment 2


def main():
    top = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("NRPIC_RUN_DIR", top)
    d = os.path.join(top, "run")
    res = []

    def check(name, ok, det):
        res.append(dict(test=name, ok=bool(ok), detail=det))
        print(("PASS " if ok else "FAIL ") + name + ": " + det)

    live = nr.read_tracker(os.path.join(d, "single.co_0.txt"))
    seg1 = nr.read_tracker(os.path.join(top, "seg1_co_0.txt"))
    check("segment 1 wrote rows 0..N1-1", list(seg1["iter"]) == list(range(N1)),
          f"{seg1['iter'].tolist()}")
    check("live file after the restart holds only segment 2 (truncated): rows N1..N2-1",
          list(live["iter"]) == list(range(N1, N2)), f"{live['iter'].tolist()}")
    files = nr.tracker_files(d, 0)
    check("wrapper kept one copy of segment 1", len(files) == 2,
          f"{[os.path.relpath(f, d) for f in files]}")
    kept = nr.read_tracker(files[0])
    check("kept copy equals segment 1 byte for byte in the values",
          np.array_equal(kept["x"], seg1["x"]) and np.array_equal(kept["t"], seg1["t"]),
          f"{len(kept['t'])} rows")
    m = nr.read_trackers(d)[0]
    check("merged tracker: rows 0..N2-1 once each, time increasing",
          list(m["iter"]) == list(range(N2)) and bool(np.all(np.diff(m["t"]) > 0)),
          f"{m['iter'].tolist()}")
    dt = np.diff(m["t"])
    check("merged tracker: constant step across the restart", float(np.ptp(dt)) < 1e-12,
          f"steps {np.unique(np.round(dt, 12)).tolist()}")
    # continuity of the position across the junction: a quadratic through rows 5-7 of
    # segment 1 predicts row 8 of segment 2 to the size of the third difference
    x = m["x"][:, 0]
    pred = 3 * x[7] - 3 * x[6] + x[5]
    third = abs(x[7] - 3 * x[6] + 3 * x[5] - x[4])
    check("position continuous across the junction (extrapolation error below 3 x the "
          "third difference)", abs(x[8] - pred) <= 3 * third + 1e-15,
          f"row 8 {x[8]:.6e}, extrapolated {pred:.6e}, third difference {third:.1e}")
    json.dump(res, open(os.path.join(out, "check_keep_trackers.json"), "w"), indent=1)
    sys.exit(0 if all(r["ok"] for r in res) else 1)


if __name__ == "__main__":
    main()
