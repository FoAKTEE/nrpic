#!/usr/bin/env python3
"""Step-size test of the anisotropic TOV residual of check_equilibria.check_model (JOURNAL.md
entry 5, prediction T1): the residual dp/dr + mu'(rho + p) + 2(p - p_T)/r of the solved
profiles, with dp/dr by central differences of step h = f (R - r_in), for f = 1e-4 (the
check's value), 5e-5, 2.5e-5. A residual from the finite difference falls as h^2.

    python3 tov_check.py [--out DIR]
"""

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import evstatic_b as evb  # noqa: E402
import model_set as ms  # noqa: E402


def tov_residual(md, f):
    r = np.linspace(md.r_in, md.R, 2001)[1:-1]
    r = r[(r > md.r_in + 0.02 * (md.R - md.r_in)) & (r < md.R - 0.02 * (md.R - md.r_in))]
    mo = md.matter_areal(r)
    h = f * (md.R - md.r_in)
    pp = md.matter_areal(r + h, ("p",))["p"]
    pm = md.matter_areal(r - h, ("p",))["p"]
    dp = (pp - pm) / (2 * h)
    y, m, N, I = md._state(r)
    mup = (m / r ** 2 + 4 * math.pi * r * mo["p"]) / (1 - 2 * m / r)
    tov = dp + mup * (mo["rho"] + mo["p"]) + 2 * (mo["p"] - mo["pT"]) / r
    scale = float(np.max(np.abs(mup * (mo["rho"] + mo["p"]))))
    return float(np.max(np.abs(tov)) / scale)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for spec in ms.model_set():
        md = evb.Equilibrium(ms.FAMILIES[spec["family"]], spec["y0"])
        v = [tov_residual(md, f) for f in (1e-4, 5e-5, 2.5e-5)]
        res[spec["tag"]] = dict(f=[1e-4, 5e-5, 2.5e-5], residual=v,
                                ratios=[v[0] / v[1], v[1] / v[2]])
        print(f"{spec['tag']}: " + ", ".join(f"{x:.2e}" for x in v)
              + f"; ratios {v[0] / v[1]:.2f}, {v[1] / v[2]:.2f}", flush=True)
    with open(os.path.join(a.out, "tov_check.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
