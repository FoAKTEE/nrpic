#!/usr/bin/env python3
"""SC0d: a circular binary moving uniformly in flat space (M = 0) under HRNA (2404 Eq.
CoordtEqs), under the diagnostic hrna_sym and under Newton; with --hrna-py also under the
track's driver geodesic_binary/hrna.py (needs numba). Usage:
    flat_binary.py <outdir> [--hrna-py]
Writes flat_binary.json; the figure is made by figures.py."""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import models as mdl  # noqa: E402

m1 = m2 = 0.05
a0 = 3.0
V = 0.28
T = 300.0
X0 = np.array([1000.0, 0.0, 0.0])     # far from the origin (M = 0 anyway; avoids r = 0)


def y0():
    mb = m1 + m2
    w = math.sqrt(mb / a0 ** 3)
    e = np.array([1.0, 0.0, 0.0])
    et = np.array([0.0, 1.0, 0.0])
    vc = np.array([V, 0.0, 0.0])
    return np.concatenate([X0 + (m2 / mb) * a0 * e, vc + (m2 / mb) * a0 * w * et,
                           X0 - (m1 / mb) * a0 * e, vc - (m1 / mb) * a0 * w * et])


def cm_track(ts, Y):
    mb = m1 + m2
    xc = (m1 * Y[0:3] + m2 * Y[6:9]) / mb
    return xc


def mine(law):
    sol = solve_ivp(mdl.rhs_two, (0, T), y0(), method="DOP853", rtol=1e-12, atol=1e-14,
                    args=(law, 0.0, m1, m2, True, True), dense_output=True)
    ts = np.linspace(0, T, 3001)
    Y = sol.sol(ts)
    return ts, cm_track(ts, Y), Y


def theirs():
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "geodesic_binary"))
    import hrna
    wk = hrna._work()
    status, t, y, diag, rec_t, rec_y, nrec, nsteps, nrej = hrna.integrate(
        hrna.LAW_HRNA, hrna.COORDS_SCH, hrna.PAIR_GRAVITY, 0.0, 0.0, m1, m2, 0.0, 0.0, y0(),
        1.0, 1e-12, 1e-14, 1e300, 1e300, 0.0, T, 10_000_000, a0, 200000,
        hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, wk)
    rt = np.array(rec_t[:nrec])
    ry = np.array(rec_y[:nrec]).T
    return rt, cm_track(rt, ry), ry


def summary(ts, xc):
    dy = xc[1] - xc[1][0]
    dx = xc[0] - (xc[0][0] + V * ts)
    # least-squares fit y = a t^2 / 2 (the CM starts with zero y-velocity)
    a_fit = float(np.sum(dy * ts ** 2 / 2) / np.sum((ts ** 2 / 2) ** 2))
    return dict(dy_end=float(dy[-1]), dx_end=float(dx[-1]), a_fit=a_fit)


def main(out, with_hrna_py):
    os.makedirs(out, exist_ok=True)
    mb = m1 + m2
    w = math.sqrt(mb / a0 ** 3)
    pred = (m1 * m2 / mb) * (w / a0) * V
    res = dict(V=V, a0=a0, m1=m1, m2=m2, T=T, predicted_acc=-pred,
               predicted_dy_end=-0.5 * pred * T ** 2)
    curves = {}
    for law in ("hrna", "hrna_sym", "newton"):
        ts, xc, _ = mine(law)
        res[law] = summary(ts, xc)
        curves[law] = (ts.tolist(), (xc[1] - xc[1][0]).tolist())
    if with_hrna_py:
        ts, xc, _ = theirs()
        res["hrna_py"] = summary(ts, xc)
        curves["hrna_py"] = (ts.tolist(), (xc[1] - xc[1][0]).tolist())
    print(json.dumps(res, indent=1))
    json.dump(dict(summary=res, curves=curves), open(os.path.join(out, "flat_binary.json"), "w"))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else os.environ["NRPIC_RUN_DIR"]
    main(out, "--hrna-py" in sys.argv)
