#!/usr/bin/env python3
"""Test U of tracks/core/JOURNAL-scalar3.md: the inflection (ultra-slow-roll) case of
arXiv:2512.14649 from the initial slice at N* with the stochastic sources.

    python3 u1_usr.py --exe EXE [--out DIR] [--n 32] [--nmax2 64] [--tlim 10.5]
                      [--workers 9] [--only a,b,...]

Runs problems/scalar/usr_stochastic.athinput (geodesic slicing, Courant 0.25) with the
background, the potential and the mode file of nrpic.sf_inflation given on the command
line:
  p1, m1      mode scale s = +1, -1
  p01, m01    s = +0.1, -0.1 (first-order part without the higher orders)
  z0          s = 0 (homogeneous universe: residual of the time integration)
  c0125       s = +1, Courant 0.125
  z0c0125     s = 0, Courant 0.125
  ctl         s = +1, noise_pi_sign = -1 (negative control), to t = 3.2
Dumps every 0.5 with the metric and the constraint fields; records every step.  The
analysis is u2_usr_analysis.py.  Writes DIR/runs.json (wall times, options)."""
import argparse
import os

import s3
from s3 import common

INP = os.path.join(common.PROB, "usr_stochastic.athinput")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out")
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--nmax2", type=int, default=64)
    ap.add_argument("--tlim", type=float, default=10.5)
    ap.add_argument("--tctl", type=float, default=3.2)
    ap.add_argument("--workers", type=int, default=9)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    case = s3.case("usr", a.nmax2)
    base = common.write_case(case, out) + common.mesh_args(a.n) + [
        f"scalar_field/noise_nmax2={a.nmax2}", f"time/tlim={a.tlim}"]
    spec = {
        "p1": [],
        "m1": ["scalar_field/noise_mode_scale=-1.0"],
        "p01": ["scalar_field/noise_mode_scale=0.1"],
        "m01": ["scalar_field/noise_mode_scale=-0.1"],
        "z0": ["scalar_field/noise_mode_scale=0.0"],
        "c0125": ["time/cfl_number=0.125"],
        "z0c0125": ["scalar_field/noise_mode_scale=0.0", "time/cfl_number=0.125"],
        "ctl": ["scalar_field/noise_pi_sign=-1.0", f"time/tlim={a.tctl}"],
    }
    if a.only:
        spec = {k: v for k, v in spec.items() if k in a.only.split(",")}
    cases = [(os.path.join(out, k), INP, base + x) for k, x in spec.items()]
    walls = common.run_many(os.path.abspath(a.exe), cases, a.workers)
    common.dump_json(dict(exe=os.path.abspath(a.exe), n=a.n, nmax2=a.nmax2,
                          tlim=a.tlim, base=base, spec=spec,
                          wall_s=dict(zip(spec, walls)),
                          case={k: case[k] for k in ("phi0", "pi0", "lambda", "vev",
                                                     "eps1", "eps2", "h_star_planck")}),
                     os.path.join(out, "runs.json"))
    print("U runs done:", out)


if __name__ == "__main__":
    main()
