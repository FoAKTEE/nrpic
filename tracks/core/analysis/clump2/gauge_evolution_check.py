#!/usr/bin/env python3
"""Outcome of test TF of tracks/core/JOURNAL-clump2.md: the moving cluster of test TC with
other damping parameters of the shift (z4c/shift_eta), with the comoving initial shift,
and with four times the particles. Compares any number of runs, each given as
label=RUN_ID/name (a directory under scratch/core), against one run at rest.

    gauge_evolution_check.py --runs "eta2=RUN/v0.3,eta0.3=RUN2/v0.3_e03,..." \
        --rest "rest=RUN/v0" [--rest2 "rest_e01=RUN2/v0_e01"] [--v 0.3] [--out DIR]

Per run: speed of the rest-mass centre over several intervals, its position at the end,
the rms extent along and across the motion, the radii that enclose 10 to 90 per cent of
the rest mass, sum m u_x, the minimum lapse, the constraint norms. Writes
gauge_evolution_check.json and fig_gauge_evolution.{pdf,png} into --out.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, HERE)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from boost_evolution_check import at, load  # noqa: E402


def pairs(text):
    out = []
    for item in text.split(","):
        label, path = item.split("=", 1)
        out.append((label, os.path.join(SCRATCH, path)))
    return out


def measure(R, v, ref):
    t, x = R["t"], R["xc"][:, 0]
    tend = float(t[-1])
    o = dict(t_end=tend, np_start=int(R["np"][0]), np_end=int(R["np"][-1]),
             xc_end=float(x[-1]), max_abs_xc_transverse=float(np.max(np.abs(R["xc"][:, 1:]))))
    if v > 0.0:
        for t0, t1 in ((0, 2), (0, 4), (0, 10), (10, 30), (30, 50), (40, 50), (0, 50)):
            if tend >= t1 - 1e-9:
                o[f"speed_{t0}_{t1}_over_v"] = (at(t1, t, x) - at(t0, t, x)) / (t1 - t0) / v
        o["lag_end"] = v * tend - (float(x[-1]) - float(x[0]))
        P0 = float(R["sum_mu"][0, 0])
        rel = R["sum_mu"][:, 0] / P0 - 1.0
        for tq in (2.0, 10.0, 25.0, 30.0, 50.0):
            if R["ht"][-1] >= tq - 1e-9:
                o[f"sum_mux_rel_{tq:g}"] = at(tq, R["ht"], rel)
        if R["ht"][-1] >= 50.0 - 1e-9:
            o["sum_mux_rel_change_30_50"] = at(50.0, R["ht"], rel) - at(30.0, R["ht"], rel)
            o["sum_mux_rel_change_25_50"] = at(50.0, R["ht"], rel) - at(25.0, R["ht"], rel)
        o["sum_mux_rel_min"], o["sum_mux_rel_max"] = float(rel.min()), float(rel.max())
    else:
        o["max_abs_xc"] = float(np.max(np.abs(R["xc"])))
        o["sum_mu_max_abs"] = float(np.max(np.abs(R["sum_mu"])))
    sg = R["sigma"] / R["sigma"][0]
    o["sigma_ratio_end"] = [float(c) for c in sg[-1]]
    o["sigma_ratio_max"] = [float(c) for c in sg.max(0)]
    rr = R["radii"] / R["radii"][0]
    o["radii_ratio_end"] = [float(c) for c in rr[-1]]
    o["radii_ratio_min"] = [float(c) for c in rr.min(0)]
    o["radii_ratio_max"] = [float(c) for c in rr.max(0)]
    o["alpha_min"] = [float(R["alpha_min"][0]), float(R["alpha_min"].min()),
                      float(R["alpha_min"].max()), float(R["alpha_min"][-1])]
    o["H_norm_end"], o["M_norm_end"] = float(R["H"][-1]), float(R["M"][-1])
    if ref is not None:
        n = min(len(t), len(ref["t"]))
        o["radii_vs_rest_max_abs"] = float(np.max(np.abs(R["radii"][:n] / ref["radii"][:n]
                                                         - 1.0)))
        o["sigma_end_minus_rest"] = [float(c) for c in
                                     (sg[n - 1] - (ref["sigma"] / ref["sigma"][0])[n - 1])]
        tt = R["ht"][R["ht"] <= ref["ht"][-1]]
        dal = np.interp(tt, R["ht"], R["alpha_min"]) - np.interp(tt, ref["ht"],
                                                                  ref["alpha_min"])
        o["alpha_minus_rest_min"], o["alpha_minus_rest_max"] = float(dal.min()), float(dal.max())
        for tq in (10.0, 25.0, 50.0):
            if tt[-1] >= tq - 1e-9:
                o[f"alpha_minus_rest_{tq:g}"] = at(tq, tt, dal)
        w = ref["zt"] >= 5.0
        w &= ref["zt"] <= R["zt"][-1]
        if np.any(w):
            o["H_ratio_max_after_5"] = float(np.max(np.interp(ref["zt"][w], R["zt"], R["H"])
                                                    / ref["H"][w]))
            o["M_ratio_max_after_5"] = float(np.max(np.interp(ref["zt"][w], R["zt"], R["M"])
                                                    / ref["M"][w]))
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--rest", required=True)
    ap.add_argument("--rest2", default=None, help="further runs at rest, compared with --rest")
    ap.add_argument("--v", type=float, default=0.3)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    (rlab, rdir), = pairs(a.rest)
    ref = load(rdir)
    res = dict(v=a.v, rest={rlab: measure(ref, 0.0, None)}, runs={})
    data = {}
    for lab, d in pairs(a.runs):
        data[lab] = load(d)
        res["runs"][lab] = measure(data[lab], a.v, ref)
        res["runs"][lab]["dir"] = os.path.relpath(d, SCRATCH)
    rest2 = {}
    if a.rest2:
        for lab, d in pairs(a.rest2):
            rest2[lab] = load(d)
            res["rest"][lab] = measure(rest2[lab], 0.0, ref)

    fs.use_style()
    cols = fs.series_colors(max(len(data), 2))
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.09, top=0.94, wspace=0.42,
                        hspace=0.33)
    sref = ref["sigma"] / ref["sigma"][0]
    for c, (lab, R) in zip(cols, data.items()):
        t, x = R["t"], R["xc"][:, 0]
        tm = 0.5 * (t[1:] + t[:-1])
        ax[0, 0].plot(tm, np.diff(x) / np.diff(t) / a.v, color=c, label=lab)
        ax[0, 1].plot(t, a.v * t - (x - x[0]), color=c)
        ax[0, 2].plot(R["ht"], R["sum_mu"][:, 0] / R["sum_mu"][0, 0], color=c)
        n = min(len(t), len(ref["t"]))
        sg = R["sigma"] / R["sigma"][0]
        ax[1, 0].plot(t[:n], sg[:n, 0] - sref[:n, 0], color=c)
        ax[1, 0].plot(t[:n], sg[:n, 1] - sref[:n, 1], color=c, ls="--")
        tt = R["ht"][R["ht"] <= ref["ht"][-1]]
        ax[1, 1].plot(tt, np.interp(tt, R["ht"], R["alpha_min"])
                      - np.interp(tt, ref["ht"], ref["alpha_min"]), color=c)
        ax[1, 2].plot(R["zt"], R["H"], color=c)
    for lab, R in rest2.items():
        tt = R["ht"][R["ht"] <= ref["ht"][-1]]
        ax[1, 1].plot(tt, np.interp(tt, R["ht"], R["alpha_min"])
                      - np.interp(tt, ref["ht"], ref["alpha_min"]), color="grey", ls=":")
        ax[1, 2].plot(R["zt"], R["H"], color="grey", ls=":")
    ax[1, 2].plot(ref["zt"], ref["H"], color="k", lw=1.0)
    ax[0, 0].axhline(1.0, **fs.GUIDE)
    ax[0, 2].axhline(1.0, **fs.GUIDE)
    ax[0, 0].set_ylabel(r"speed of the centre$/v$")
    ax[0, 1].set_ylabel(r"lag $v t - x_c$ $(M)$")
    ax[0, 2].set_ylabel(r"$\sum m u_x / P$")
    ax[1, 0].set_ylabel(r"$\sigma/\sigma(0)$ $-$ rest")
    ax[1, 0].set_title("rms extent: $x$ (solid), $y$ (dashed)", fontsize=9)
    ax[1, 1].set_ylabel(r"$\alpha_{\min}$ $-$ rest")
    ax[1, 1].set_title("minimum lapse", fontsize=9)
    ax[1, 2].set_ylabel(r"$H$-norm")
    ax[1, 2].set_title("black: at rest", fontsize=9)
    ax[1, 2].set_yscale("log")
    for a_ in ax.ravel():
        a_.set_xlabel(r"$t/M$")
    ax[0, 0].legend(loc="lower right", fontsize=8, ncol=2, columnspacing=0.8,
                    handlelength=1.2)
    fs.save(fig, os.path.join(a.out, "fig_gauge_evolution"))

    with open(os.path.join(a.out, "gauge_evolution_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
