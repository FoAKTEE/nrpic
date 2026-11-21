#!/usr/bin/env python3
"""Tests G1 and G2 of tracks/core/JOURNAL-scalar3.md: the stochastic sources with a
lapse that is not geodesic.

    python3 g1_gauge.py --exe EXE [--exe-gauge EXE] [--out DIR] [--n 32] [--workers 3]
                        [--only a,b]

Runs problems/scalar/sr_stochastic_gauge.athinput (quadratic case, nmax2 = 64):
  geo    lapse_harmonic = 0 (geodesic slicing), to t = 3.3
  harm   lapse_harmonic = 0.05 (d_t alpha = -0.05 alpha^2 Khat), to t = 2.6
  kdrv   lapse_harmonic = 0, lapse_kdriver = 2, to t = 3.3
with dumps (metric) every 0.3 of coordinate time; and (test G5, only when named in
--only; cap needs --exe-gauge, an executable with the relaxation term lapse_leak of
branch core/gauge):
  geoc   geodesic slicing at Courant 1/32 (the step of a 256^3 run at Courant 0.25), to
         t = 3.3, dumps every 0.3
  cap    conformal-time lapse (lapse_harmonic = 1/3) capped at alpha_0 = 8 by lapse_leak =
         50 (T = 0.02), Courant 1/32, to t = 1.0 (3.3 e-folds), dumps every 0.025
The input of these two is a copy of the example with the lines lapse_leak and
lapse_leak_alpha added (a command line may override only parameters the file has; an
executable without the term ignores them).  The analysis is g2_gauge_analysis.py.
Writes DIR/runs.json."""
import argparse
import os

import s3
from s3 import common

INP = os.path.join(common.PROB, "sr_stochastic_gauge.athinput")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--exe-gauge", help="executable with lapse_leak (case cap)")
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
    g5 = {
        "geoc": ["z4c/lapse_harmonic=0.0", "time/cfl_number=0.03125", "time/tlim=3.3"],
        "cap": ["z4c/lapse_harmonic=0.3333333333333333", "z4c/lapse_leak=50.0",
                "z4c/lapse_leak_alpha=8.0", "time/cfl_number=0.03125", "time/tlim=1.0",
                "scalar_field/dump_dt=0.025"],
    }
    only = a.only.split(",") if a.only else list(spec)
    spec = {k: v for k, v in {**spec, **g5}.items() if k in only}
    inp_g5 = os.path.join(out, "sr_stochastic_gauge_leak.athinput")
    if set(spec) & set(g5):
        lines = []
        for ln in open(INP).read().splitlines():
            lines.append(ln)
            if ln.split("=")[0].strip() == "lapse_advect":
                lines += ["lapse_leak       = 0.0     # core/gauge: 1/T",
                          "lapse_leak_alpha = 1.0     # core/gauge: alpha_0"]
        assert any(x.startswith("lapse_leak_alpha") for x in lines)
        with open(inp_g5, "w") as fp:
            fp.write("\n".join(lines) + "\n")
    exes = {k: os.path.abspath(a.exe) for k in spec}
    if "cap" in spec:
        if not a.exe_gauge:
            raise SystemExit("case cap needs --exe-gauge")
        exes["cap"] = os.path.abspath(a.exe_gauge)
    walls = {}
    for exe in sorted(set(exes.values())):
        ks = [k for k in spec if exes[k] == exe]
        cases = [(os.path.join(out, k), inp_g5 if k in g5 else INP, base + spec[k])
                 for k in ks]
        walls.update(zip(ks, common.run_many(exe, cases, a.workers)))
    common.dump_json(dict(exe=exes, n=a.n, nmax2=a.nmax2, base=base,
                          spec=spec, wall_s=walls), os.path.join(out, "runs.json"))
    print("G1/G2 runs done:", out)


if __name__ == "__main__":
    main()
