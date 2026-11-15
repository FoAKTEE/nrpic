#!/usr/bin/env python3
"""Finder-independent horizon mass of restart dumps: the Misner-Sharp mass of the slice
(analysis/diag/slicemass.py of this repository, imported, not copied).

    slice_masses.py --out FILE.json RST [RST ...]

Per dump: time, cycle, M_H = R_H/2 at the outermost 2m/R = 1 (16 shells per factor 2)
with its two uncertainties (shell choice, angular spread of m), the asymptotic mass
m_inf, and the shell medians of m interpolated at areal radius R = 3, 5, 10, 20 M.
Records are appended to FILE.json (a dump already in it is skipped).
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/analysis/diag")
import slicemass as sm  # noqa: E402

R_PROBE = (3.0, 5.0, 10.0, 20.0)


def one(path):
    h = sm.rst_open(path, strict=True)
    t0 = time.time()
    A = sm.analyse(h)
    X = A["X"][sm.NPER2_H]
    P = A["P"][sm.NPER2_PRINT]
    rec = dict(rst=os.path.abspath(path),
               run=os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(path)))),
               dump=os.path.basename(path), time=float(A["time"]), ncycle=int(A["ncycle"]),
               nmb=int(A["nmb"]), dx_min=float(A["dx_min"]), m_inf=float(A["m_inf"]),
               flat=bool(A["flat"]), wall_s=None)
    if X is not None and np.isfinite(X["RH"]):
        rec.update(M_H=float(X["RH"] / 2), dMH_shell=float(A["dMH_shell"]),
                   dMH_spread=float(A["dMH_spread"]))
    ok = np.isfinite(P["R"]) & np.isfinite(P["m"])
    s = sm.outer_sheet(P)
    s = s[ok[s]]
    R, m = P["R"][s], P["m"][s]
    o = np.argsort(R)
    for Rq in R_PROBE:
        rec[f"m_R{Rq:g}"] = float(np.interp(Rq, R[o], m[o])) if R.min() < Rq < R.max() \
            else None
    rec["wall_s"] = time.time() - t0
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rst", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = json.load(open(a.out)) if os.path.exists(a.out) else []
    have = {r["rst"] for r in res}
    for p in a.rst:
        if os.path.abspath(p) in have:
            continue
        r = one(p)
        res.append(r)
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1)
        print(f"{r['run']}/{r['dump']} t={r['time']:.3f} M_H={r.get('M_H', float('nan')):.6f}"
              f" +- {r.get('dMH_shell', float('nan')):.1e} +- "
              f"{r.get('dMH_spread', float('nan')):.1e} m_inf={r['m_inf']:.6f} "
              f"m(R=3)={r['m_R3']} m(R=10)={r['m_R10']} ({r['wall_s']:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
