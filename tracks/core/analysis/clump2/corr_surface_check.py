#!/usr/bin/env python3
"""Is there a surface layer at rbar_s in the second-order correction of psi? (TB3
leftover, tracks/core/JOURNAL-clump2.md). For the y_c = 0.819 cluster:

1. the radial equation of the monopole, lap y0 = sigma y0 - S0, in flux form across a
   small interval [rs - e, rs + e]: J = [r^2 y0']_(rs-e)^(rs+e) - int (sigma y0 - S0) r^2,
   from the Python solution (spline of the solution nodes) and from the written table
   (the code's input; cubic interpolation as in the code); J/rs^2 is the strength of a
   delta function at the surface (zero for a solution);
2. the same flux balance measured in the code: the shell integral of D_H(corr) across
   the surface in the TB runs, converted with H = -8 psi^-5 lap psi to the strength of
   a delta function in lap(dpsi) per unit V^2;
3. the same for the uncorrected D_H(curv) (it must give the continuum flux of the
   second-order source through the shell, nothing singular).

    corr_surface_check.py --tb RUN_ID/tb [--out DIR]
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, HERE)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import boosted_cluster as bc  # noqa: E402
from nrpic import bowen_york as by  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402
from boost_static_check import Case  # noqa: E402


def lagrange4(rg, col, r):
    """four-point Lagrange interpolation on the uniform grid rg (as BYCubic)"""
    dr = rg[1] - rg[0]
    out = np.empty_like(r)
    for k, x in enumerate(r):
        i = int(np.floor(x / dr)) - 1
        i = min(max(i, 0), len(rg) - 4)
        xs = rg[i:i + 4]
        ys = col[i:i + 4]
        s = 0.0
        for a in range(4):
            w = 1.0
            for b in range(4):
                if b != a:
                    w *= (x - xs[b]) / (xs[a] - xs[b])
            s += w * ys[a]
        out[k] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tb", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md = stc.STModel(0.819)
    B = bc.BoostedST(md)
    co = B.correction()
    rs = B.rs
    r, y0, S0, sig = co["r"], co["y0"], co["S0"], co["sigma"]
    spl = CubicSpline(np.log(r), y0)
    Sf = CubicSpline(r, S0)
    sgf = CubicSpline(r, sig)

    def y(x):
        return spl(np.log(x))

    def dy(x):
        return spl(np.log(x), 1) / x

    res = dict(rbar_s=rs, python={}, table={}, code={})
    for e in (0.05, 0.1, 0.2, 0.5):
        lo, hi = rs - e, rs + e
        flux = hi * hi * dy(hi) - lo * lo * dy(lo)
        src = quad(lambda x: (sgf(x) * y(x) - Sf(x)) * x * x, lo, hi, points=[rs],
                   limit=400)[0]
        res["python"][f"e={e}"] = dict(flux=float(flux), source=float(src),
                                       J_over_rs2=float((flux - src) / rs ** 2),
                                       flux_scale=float(abs(flux) / rs ** 2))
    # one-sided derivatives of the solution at rs
    h = 1e-4
    res["python"]["dy0_left"] = float((y(rs) - y(rs - h)) / h)
    res["python"]["dy0_right"] = float((y(rs + h) - y(rs)) / h)

    # the written table of the TB runs (V of v = 0.3), per unit V^2
    top = os.path.join(SCRATCH, a.tb)
    tab = by.read_table(os.path.join(top, "ic", "q0.3_c0_corr.tab"))
    rg = np.asarray(tab["r"])
    c0 = np.asarray(tab["cols"][0])
    with open(os.path.join(top, "ic", "q0.3.json")) as f:
        meta = json.load(f)
    V = np.asarray(meta["clusters"][0]["V_linear_rule"])
    v2 = float(np.sum(V * V))
    t0 = c0 / v2
    for e in (0.1, 0.2, 0.5):
        lo, hi = rs - e, rs + e
        dd = 1e-3
        d_hi = (lagrange4(rg, t0, np.array([hi + dd]))[0] - lagrange4(rg, t0, np.array([hi - dd]))[0]) / (2 * dd)
        d_lo = (lagrange4(rg, t0, np.array([lo + dd]))[0] - lagrange4(rg, t0, np.array([lo - dd]))[0]) / (2 * dd)
        flux = hi * hi * d_hi - lo * lo * d_lo
        src = quad(lambda x: (sgf(x) * lagrange4(rg, t0, np.array([x]))[0] - Sf(x)) * x * x,
                   lo, hi, points=[rs], limit=400)[0]
        res["table"][f"e={e}"] = dict(flux=float(flux), source=float(src),
                                      J_over_rs2=float((flux - src) / rs ** 2))

    # the code: shell integral of D_H across the surface, as a delta strength in
    # lap(dpsi) per unit V^2: int D_H dV = -8 int psi^-5 lap(dpsi) dV
    for n in (32, 64, 128):
        st = Case(top, f"q0_n{n}")
        for c in ("curv", "corr"):
            cs = Case(top, f"q0.3_n{n}_{c}")
            d = cs.H - st.H
            for e in (0.5, 1.0):
                sel = np.abs(st.r - rs) < e
                integ = float(np.sum((d * st.dV)[sel]))
                psi5 = float(np.mean(st.psi[sel] ** 5))
                res["code"][f"n={n},{c},e={e}"] = dict(
                    int_DH_dV=integ,
                    J_over_rs2=float(-integ * psi5 / 8.0 / (4.0 * math.pi * rs ** 2) / v2))
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.HALF_WIDTH if hasattr(fs, "HALF_WIDTH") else 4.0, 3.0))
    xx = np.linspace(rs - 1.0, rs + 1.0, 801)
    lap = (CubicSpline(xx, y(xx))(xx, 2) + 2.0 * dy(xx) / xx)
    ax.plot(xx, lap - (sgf(xx) * y(xx) - Sf(xx)), color="k", label="Python solution")
    tt = lagrange4(rg, t0, xx)
    lt = CubicSpline(xx, tt)
    ax.plot(xx, lt(xx, 2) + 2.0 * lt(xx, 1) / xx - (sgf(xx) * tt - Sf(xx)),
            color=fs.PAL["red"], ls="--", label="written table")
    ax.axvline(rs, **fs.THIN, ls=":")
    ax.set_xlabel(r"$r/M$")
    ax.set_ylabel(r"residual of the $l = 0$ equation")
    ax.legend(loc="best", fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig_corr_surface"))
    with open(os.path.join(a.out, "corr_surface_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
