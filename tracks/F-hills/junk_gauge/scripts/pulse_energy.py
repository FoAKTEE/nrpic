#!/usr/bin/env python3
"""J3c: energy from the window's start u0 = -15 to u_c (8 and 10 m: the end of the pulse in
S2g's r psi4), per method, at each radius (J3 curves) and extrapolated (J3b curves). A reading
of curves already computed; no new integration.
Usage: pulse_energy.py <out | -> <J3 run dir> <J3b run dir>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import junk_lib as jl  # noqa: E402


def upto(u, rate, a, b):
    return jl.window_integral(u, rate, a, b)


def main():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    c3 = np.load(os.path.join(sys.argv[2], "single_junk_curves.npz"))
    res = {"finite": {}, "extrapolated": {}}
    for R in (30, 40, 50):
        u = c3[f"R{R}_u"]
        res["finite"][str(R)] = {f"{k}_to_{uc}": upto(u, c3[f"R{R}_dE_{k}"], -15.0, uc)
                                 for k in ("ffi0.1", "ffi0.2", "ffi0.3", "td") for uc in (8.0, 10.0)}
    for tag in ("S2g", "S2g_o2"):
        c = np.load(os.path.join(sys.argv[3], f"{tag}_extrap_curves.npz"))
        u = c["u"]
        res["extrapolated"][tag] = {f"{k}_to_{uc}": upto(u, c[f"A_dE_{k}"], -15.0, uc)
                                    for k in ("ffi0.1", "ffi0.2", "ffi0.3", "td") for uc in (8.0, 10.0)}
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(out, "pulse_energy.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
