#!/usr/bin/env python3
"""Step count of a Newtonian-mode infall run from its matched shell reference (a cost
estimate; decision 0010: no simulation here).

The code's step is dt = min(dtmax, cfl dx/max|v|, sqrt(2 cfl dx/max|g|)) (newton_cfl,
newtonian_mode.md section 4). The largest speed is that of dust passing through the
softened centre. The shell reference gives, at each of its snapshots, the largest |v| of
its shells; a run with 5e5 particles samples the centre more often than 4000 shells, so
the estimate is calibrated on a finished run (its history: dt and p_max per record)
against the shells matched to that run:  dt_run = c * min(dtmax, cfl dx/v_shells), with c
fitted (median ratio), then applied to the new set-up. The acceleration limit is not
binding in the wave-2 runs (checked: the reported p_max reproduces dt = cfl dx/p_max).

Usage: python3 nm_cost.py --calib_hst RUN/infall.newton.hst --calib_shells PREFIX --calib_dx 2.75
            --calib_dtmax 0.5 --shells PREFIX --dx 8.896 --dtmax 2.0 [--spsec 0.66] --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import load_figstyle   # noqa: E402
from nrpic import newton as nw     # noqa: E402


def vmax_of(prefix):
    d = np.load(prefix + ".npz")
    v = np.abs(d["snap_v"]).max(axis=1)
    return d["snap_t"], v, float(d["t_i"])


def dt_model(t, ts, vs, dx, cfl, dtmax):
    v = np.interp(t, ts, vs)
    return np.minimum(dtmax, cfl * dx / v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--calib_hst", required=True)
    ap.add_argument("--calib_shells", required=True)
    ap.add_argument("--calib_dx", type=float, required=True)
    ap.add_argument("--calib_dtmax", type=float, required=True)
    ap.add_argument("--shells", action="append", required=True, help="LABEL:PREFIX of the new set-up")
    ap.add_argument("--dx", type=float, required=True)
    ap.add_argument("--dtmax", type=float, required=True)
    ap.add_argument("--cfl", type=float, default=0.15)
    ap.add_argument("--spsec", type=float, default=0.0, help="measured seconds per step")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    h = nw.read_newton_hst(a.calib_hst)
    k = h["ncycle"] > 0
    th, dth, pm = h["time"][k], h["dt"][k], h["p_max"][k]
    ts, vs, ti = vmax_of(a.calib_shells)
    model = dt_model(th, ts, vs, a.calib_dx, a.cfl, a.calib_dtmax)
    ratio = dth / model
    c = float(np.median(ratio[th > ts[0]]))
    check_pmax = float(np.median(np.abs(dth / np.minimum(a.calib_dtmax, a.cfl * a.calib_dx / pm) - 1)))
    steps_calib_model = float(np.trapezoid(1.0 / (c * dt_model(np.linspace(0, th[-1], 20001), ts, vs,
                                                                   a.calib_dx, a.cfl, a.calib_dtmax)),
                                           np.linspace(0, th[-1], 20001)))
    out = dict(calib=dict(hst=a.calib_hst, shells=a.calib_shells, c=c,
                          ratio_p10_p90=[float(np.percentile(ratio, 10)), float(np.percentile(ratio, 90))],
                          steps_actual=int(h["ncycle"][-1]), steps_model=steps_calib_model,
                          dt_vs_cfl_over_pmax_median_dev=check_pmax), runs={})
    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.5, 3.6))
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.14, top=0.97)
    ax.plot(th, dth, color=fs.PAL["red"], lw=1.2, label="N128Lc: code step")
    ax.plot(th, c * model, color=fs.PAL["red"], ls="--", lw=1.0, label=f"N128Lc: model x {c:.2f}")
    cols = [fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"]]
    for i, spec in enumerate(a.shells):
        lab, pre = spec.split(":", 1)
        ts2, vs2, _ = vmax_of(pre)
        tt = np.linspace(0.0, ts2[-1], 200001)
        dtt = c * dt_model(tt, ts2, vs2, a.dx, a.cfl, a.dtmax)
        steps = float(np.trapezoid(1.0 / dtt, tt))
        steps_at = {}
        for aa in (4.0, 8.0, 16.0, 30.0):
            tc = ti * (aa ** 1.5 - 1.0)
            if tc <= tt[-1] * (1 + 1e-9):
                m = tt <= tc
                steps_at[f"{aa:g}"] = float(np.trapezoid(1.0 / dtt[m], tt[m]))
        out["runs"][lab] = dict(shells=pre, steps=steps, steps_at=steps_at,
                                dt_min=float(dtt.min()), dt_end=float(dtt[-1]),
                                wall_h=steps * a.spsec / 3600.0 if a.spsec else None)
        ax.plot(tt[::200], dtt[::200], color=cols[i % 3], lw=1.0, label=f"{lab}: model x {c:.2f}")
    ax.set_xscale("log")
    ax.set_xlabel("code time $t - t_i$ [$GM/c^3$]")
    ax.set_ylabel("step [$GM/c^3$]")
    ax.legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(a.out, "nm_cost"))
    with open(os.path.join(a.out, "nm_cost.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
