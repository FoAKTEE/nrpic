#!/usr/bin/env python3
"""Trajectories of the two P1 baselines over t = 0-300 M, for the figures of package p1.

Same construction as nr_first/scripts/baselines_p1.py (E6), which keeps only summary numbers:
  newton  full Newtonian three-body problem from the input state (hole free);
          lead_checks.newton_full (DOP853, rtol 1e-12)
  hrna    geodesic baseline of 2404.16270 (hole fixed at the origin, Schwarzschild
          coordinates) from the coordinate state relative to M; lead_checks.hrna_from_state
  nfix    the same driver with a Newtonian point mass fixed at the origin
Writes <out>/baseline_tracks.npz and baseline_tracks.json (summary to check against
nr_first/results/baselines_p1.json). Needs numba: run with scratch/F-hills/venv-gb/bin/python.
Usage: baselines_tracks.py [--out=<dir>]   (default $NRPIC_RUN_DIR)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402

sys.path.insert(0, os.path.join(p1lib.WT, "tracks", "F-hills", "stage", "G0", "checks"))
import lead_checks as lc  # noqa: E402

T_END = 300.0


def main():
    out = p1lib.out_dir(sys.argv)
    m, x, p = lc.read_athinput(p1lib.INPUT)       # comp0 = m1, comp1 = m2, comp2 = M
    M, m1, m2 = m[2], m[0], m[1]
    mb = m1 + m2
    a0 = p1lib.A0
    rt = a0 * (M / mb) ** (1 / 3)
    v = p / m[:, None]
    ts, Y = lc.newton_full(m, x, p, t_end=T_END, nout=int(T_END / 0.05) + 1)
    X = Y[:, :9].reshape(-1, 3, 3)
    V = Y[:, 9:].reshape(-1, 3, 3)
    y0 = np.concatenate([x[0] - x[2], v[0] - v[2], x[1] - x[2], v[1] - v[2]])
    hrna = lc.hrna_mod()
    arrs = dict(newton_t=ts, newton_X=X, newton_V=V, masses=m, x0=x, p0=p)
    summ = {}
    for law, key in (("hrna", "hrna"), ("newton", "nfix")):
        s, rt_, ry = lc.hrna_from_state(hrna, law, y0, m1, m2, a0, rt)
        keep = rt_ <= T_END
        arrs[f"{key}_t"] = rt_[keep]
        arrs[f"{key}_y"] = ry[keep]
        r1 = np.linalg.norm(ry[:, 0:3], axis=1)
        r2 = np.linalg.norm(ry[:, 6:9], axis=1)
        summ[key] = dict(E1_u=float(s["E1_u"]), E2_u=float(s["E2_u"]), rmin_1=float(r1.min()),
                         rmin_2=float(r2.min()), n_rec=int(keep.sum()),
                         r_1M_280=float(np.interp(280.0, rt_, r1)),
                         r_2M_280=float(np.interp(280.0, rt_, r2)))
    r1M = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
    r2M = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)
    xc = (m1 * X[:, 0] + m2 * X[:, 1]) / mb
    rc = np.linalg.norm(xc - X[:, 2], axis=1)
    summ["newton"] = dict(rmin_1M=float(r1M.min()), rmin_2M=float(r2M.min()),
                          t_cm_peri=float(ts[np.argmin(rc)]), rc_min=float(rc.min()),
                          r_1M_280=float(np.interp(280.0, ts, r1M)),
                          r_2M_280=float(np.interp(280.0, ts, r2M)))
    np.savez_compressed(os.path.join(out, "baseline_tracks.npz"), **arrs)
    json.dump(summ, open(os.path.join(out, "baseline_tracks.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
