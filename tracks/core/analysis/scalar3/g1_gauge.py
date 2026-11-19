#!/usr/bin/env python3
"""Tests G1 and G2 of tracks/core/JOURNAL-scalar3.md: the stochastic sources with a
lapse that is not geodesic.

    python3 g1_gauge.py --exe EXE [--out DIR] [--n 32] [--workers 3] [--only a,b]

Runs problems/scalar/sr_stochastic_gauge.athinput (quadratic case, nmax2 = 64):
  geo    lapse_harmonic = 0 (geodesic slicing), to t = 3.3
  harm   lapse_harmonic = 0.05 (d_t alpha = -0.05 alpha^2 Khat), to t = 2.6
  kdrv   lapse_harmonic = 0, lapse_kdriver = 2, to t = 3.3
with dumps (metric) every 0.3 of coordinate time.  The analysis is g2_gauge_analysis.py.
Writes DIR/runs.json."""
import argparse
import os

import s3
from s3 import common

INP = os.path.join(common.PROB, "sr_stochastic_gauge.athinput")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out")
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--nmax2", type=int, default=64)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    case = s3.case("sr", a.nmax2)
    base = common.write_case(case, out) + common.mesh_args(a.n) + [
        f"scalar_field/noise_nmax2={a.nmax2}", "scalar_field/dump_dt=0.3"]
    spec = {
        "geo": ["z4c/lapse_harmonic=0.0", "time/tlim=3.3"],
        "harm": ["z4c/lapse_harmonic=0.05", "time/tlim=2.6"],
        "kdrv": ["z4c/lapse_harmonic=0.0", "z4c/lapse_kdriver=2.0", "time/tlim=3.3"],
    }
    if a.only:
        spec = {k: v for k, v in spec.items() if k in a.only.split(",")}
    cases = [(os.path.join(out, k), INP, base + x) for k, x in spec.items()]
    walls = common.run_many(os.path.abspath(a.exe), cases, a.workers)
    common.dump_json(dict(exe=os.path.abspath(a.exe), n=a.n, nmax2=a.nmax2, base=base,
                          spec=spec, wall_s=dict(zip(spec, walls))),
                     os.path.join(out, "runs.json"))
    print("G1/G2 runs done:", out)


if __name__ == "__main__":
    main()
