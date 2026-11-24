#!/usr/bin/env python3
"""Finder re-search of the long runs' restart dumps (g2long/JOURNAL.md entry 10, test FP).

A thin wrapper of tracks/D-bh-dress/puncture_drift/tools/probe_finder.py (D-pre-4, wave 1):
each dump is restarted for exactly one cycle on a processor executable with three horizons
centred on the origin,
  h0  production stopping (mass_tol 1e-5, 400 iterations) from the radius stored in the dump,
  h1  tight stopping (mass_tol 1e-9, 4000 iterations) from r = 1.0 M,
  h2  production stopping from outside, r = 2.0 M,
on the production finder grid (A16: ntheta 16, lmax 8) and, optionally, the finer one (A32:
ntheta 32, lmax 16). The only change to probe_finder.py: its summary reader looked for
`punc.horizon_summary_<n>.txt` (the basename of D-pre-4's runs); here the files carry the
basename of the dump (v1l, es1l, ...), so the reader takes the one `*.horizon_summary_<n>.txt`
of the probe directory.

    probe_long.py RST [RST ...] --out DIR --tag NAME [--variants A16 A32] [--threads 2]
                  [--jobs 3] [--exe PATH]

Output: DIR/NAME/probes.json and one directory per (dump, variant), as probe_finder.py.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "puncture_drift", "tools"))
import probe_finder as pf  # noqa: E402

_orig = pf.read_summary


def read_summary_any(path):
    d = os.path.dirname(path)
    n = os.path.basename(path).rsplit("_", 1)[1]          # "<n>.txt"
    hits = sorted(glob.glob(os.path.join(d, f"*.horizon_summary_{n}")))
    if len(hits) > 1:
        raise SystemExit(f"more than one horizon summary {n} in {d}: {hits}")
    return _orig(hits[0]) if hits else []


pf.read_summary = read_summary_any

if __name__ == "__main__":
    pf.main()
