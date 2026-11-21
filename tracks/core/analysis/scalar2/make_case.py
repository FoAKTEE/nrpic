#!/usr/bin/env python3
"""Writes the mode file of a test case of arXiv:2512.14649 in the units of the code and
prints the options of the input file (background at N*, potential, box).

    python3 make_case.py --case quadratic --nmax2 64 --out DIR [--name modes.txt]

Reference: python/nrpic/sf_inflation.py (Friedmann background in e-folds from the
Bunch-Davies time N0, Mukhanov-Sasaki equation per shell).  For the 256^3 production
set-up (nmax2 = 4096, 3413 shells) pass --kstart 100: each mode then starts from
Bunch-Davies data where k/(aH) = 100 instead of at N0."""
import argparse
import json
import os

import common
from common import inf, np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="quadratic", choices=["quadratic", "inflection"])
    ap.add_argument("--nmax2", type=int, default=64)
    ap.add_argument("--kstart", type=float, default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="modes.txt")
    a = ap.parse_args()
    model = inf.quadratic_model() if a.case == "quadratic" else inf.inflection_model()
    case = inf.code_case(model, a.nmax2, kstart=a.kstart)
    args = common.write_case(case, a.out, a.name)
    summ = {k: case[k] for k in ("model", "potential", "length", "sigma", "phi0", "pi0",
                                 "h_star_planck", "eps1", "eps2", "dn_star", "dn_sim")}
    for k in ("mass", "lambda", "vev"):
        if k in case:
            summ[k] = case[k]
    summ["nshell"] = int(case["n2"].size)
    summ["R_first_shell"] = [case["R"][0].real, case["R"][0].imag]
    summ["dR_first_shell"] = [case["dR"][0].real, case["dR"][0].imag]
    # dimensionless spectrum k^3 |R_k|^2/(2 pi^2) of the first and last shell at N*
    k = 2.0*np.pi*np.sqrt(case["n2"])/case["length"]
    delta = k**3*np.abs(case["R"])**2/(2.0*np.pi**2)
    summ["Delta_R_first_last"] = [delta[0], delta[-1]]
    common.dump_json(summ, os.path.join(a.out, "case.json"))
    print(json.dumps(summ, indent=1, default=float))
    print("options:", " ".join(args))


if __name__ == "__main__":
    main()
