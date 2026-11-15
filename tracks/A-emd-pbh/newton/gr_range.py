#!/usr/bin/env python3
"""Proposed parameter range of the full-relativity scan from the Newtonian precursor.

    gr_range.py --results <analysis run>/newton_results.json --out DIR

For each shape (e, p) of the first scan: the Newtonian hoop amplitude delta_L,th = h_1
delta_L (the amplitude at which the hoop ratio h of the pancake at the first collapse is
one; h scales as 1/delta_L, ellipsoid.py and JOURNAL P7) from the isolated-ellipsoid
reference and from the AthenaK runs (128^3, lattice 0.025, delta_L = 0.2); at that
amplitude: the end-point special-relativistic delay of t_1 (ellipsoid.evolve sr=True,
an estimate), the infall speed of the short axis at t_1 (|dA_1/dt|, units of c), t_1/t_0
and t_1/t_k, the largest ball radius of the expanding-ball set-up at the start
a0 = 1/(2 lambda_1) (R_ball H_0 < 1: delta_L (1 + 3e + p) < 1.5 (R_L/R_ball)^2, SCAN.md
section 3), and the start a0' at which a ball of radius 1.5 R_L fits (a0' > (1.5 R_L)^2,
from the exact ellipsoid state). Seeds of the bisection: delta_L,th x {0.5, 0.7, 1, 1.4, 2}.
Writes gr_scan_range.csv and fig_newton_gr_range.{png,pdf}.
"""
import argparse
import csv
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import ellipsoid as el  # noqa: E402
import tophat as th  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

SHAPES = [(0.05, 0.0), (0.1, 0.0), (0.2, 0.0), (0.3, 0.0), (0.2, 0.2), (0.2, -0.2)]
SEEDS = (0.5, 0.7, 1.0, 1.4, 2.0)


def infall_speed(dL, e, p):
    lams = el.abg_from_dep(dL, e, p)
    r = el.evolve(lams, model="isolated", n_collapse=1)
    c = r["collapses"][0]
    t, A = r["t"], r["A"]
    m = t <= c["t"]
    ax = c["axis"]
    # one-sided slope over the last 0.2 percent of t_1 before the collapse
    sel = m & (t >= c["t"] * (1 - 2e-3))
    if sel.sum() < 3:
        sel = m
        sel[:-4] = False
    slope = np.polyfit(t[sel], A[sel, ax], 1)[0]
    return abs(float(slope)), r["t0"], c["t"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"),
                    help="output directory (default: $NRPIC_RUN_DIR of a registered run)")
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: --out or NRPIC_RUN_DIR")
    with open(a.results) as f:
        res = json.load(f)
    runs = [r for r in res.get("scan", []) if r.get("complete") and r["nx"] == 128
            and r["hxi"] == 0.025 and r.get("rotate") is None and abs(r["deltaL"] - 0.2) < 1e-12]
    rows = []
    for e, p in SHAPES:
        ref1 = el.first_collapse(1.0, e, p)
        dth_ref = ref1["h1"] * 1.0
        run = [r for r in runs if abs(r["e"] - e) < 1e-9 and abs(r["p"] - p) < 1e-9]
        dth_run = run[0]["h1_deltaL"] if run else float("nan")
        t1_rel_run = run[0]["t1_vertex_rel"] if run else float("nan")
        rn = el.first_collapse(dth_ref, e, p)
        rs = el.first_collapse(dth_ref, e, p, sr=True)
        v1, t0, t1 = infall_speed(dth_ref, e, p)
        rball = np.sqrt(1.5 / (dth_ref * (1 + 3 * e + p)))
        lam1 = max(el.abg_from_dep(dth_ref, e, p))
        a0 = 0.5 / lam1
        a1 = float(th.a_of_t(t1))
        # resolution of the 128^3 run, carried to the threshold amplitude: cells across the
        # short semi-axis at the start, and that cell in units of the patch mass M = r_g/2
        lam02 = np.asarray(el.abg_from_dep(0.2, e, p))
        a002 = 0.5 / lam02.max()
        A1_02 = float((a002 * (1.0 - a002 * lam02)).min())
        cells = A1_02 / run[0]["dx"] if run else float("nan")
        A1_th_over_M = 2.0 * A1_02 * 0.2 / dth_ref
        rows.append(dict(e=e, p=p, deltaL_th_ref=dth_ref, deltaL_th_run=dth_run,
                         run_over_ref=dth_run / dth_ref - 1, t1_rel_run=t1_rel_run,
                         sr_delay_t1=rs["t1_over_tk"] / rn["t1_over_tk"] - 1,
                         v1_infall=v1, t1_over_t0=t1 / t0, t1_over_tk=t1 / th.T_K,
                         a0=a0, a1=a1, Rball_max_over_RL=rball,
                         Rball_max_at_t1_over_RL=float(np.sqrt(a1)),
                         cells_short_axis_run=cells, A1_start_th_over_M=A1_th_over_M,
                         dx_over_M_same_cells=A1_th_over_M / cells,
                         seeds=" ".join(f"{s * dth_ref:.3f}" for s in SEEDS)))
    os.makedirs(a.out, exist_ok=True)
    keys = list(rows[0].keys())
    with open(os.path.join(a.out, "gr_scan_range.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(keys)
        for r in rows:
            w.writerow([f"{r[k]:.6g}" if isinstance(r[k], float) else r[k] for k in keys])
    # figure: hoop line with seeds, ball-radius limits, SR delay
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.7))
    ax = fs.inch_axes(fig, 0.7, 0.5, 2.6, 1.95)
    ee = np.linspace(0.01, 0.35, 70)
    hl = np.array([el.first_collapse(1.0, x, 0.0)["h1"] for x in ee])
    for s in SEEDS:
        ax.plot(ee, s * hl, color="grey", lw=0.6, ls=":" if s != 1.0 else "-")
    ax.plot(ee, hl, **fs.GUIDE, label=r"hoop line, ellipsoid ($p=0$)")
    for R, col in zip((1.0, 1.5, 2.0), (fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"])):
        ax.plot(ee, 1.5 / R ** 2 / (1 + 3 * ee), color=col, lw=1.2,
                label=f"ball limit, $R_{{\\rm ball}}={R:g}R_L$")
    pr = [r for r in rows if r["p"] == 0.0]
    ax.plot([r["e"] for r in pr], [r["deltaL_th_run"] for r in pr], "o", color="k", ms=4,
            label=r"AthenaK $h_1\delta_L$ ($128^3$)")
    for r in rows:
        if r["p"] != 0.0:
            ax.plot(r["e"], r["deltaL_th_run"], "^" if r["p"] > 0 else "v", color="k", ms=4,
                    mfc="none")
    ax.set_yscale("log")
    ax.set_xlabel("$e$")
    ax.set_ylabel(r"$\delta_L$")
    ax.set_xlim(0, 0.35)
    ax.set_ylim(0.05, 3)
    ax.legend(loc="lower right", fontsize=5.5)
    ax2 = fs.inch_axes(fig, 4.0, 0.5, 1.6, 1.95)
    ax2.plot([r["e"] for r in pr], [100 * r["sr_delay_t1"] for r in pr], "o-", color=fs.PAL["blue"],
             ms=3, label="SR delay of $t_1$ [%]")
    ax2.plot([r["e"] for r in pr], [100 * r["v1_infall"] for r in pr], "s-", color=fs.PAL["red"],
             ms=3, label=r"$|\dot A_1|(t_1)$ [% of $c$]")
    ax2.set_xlabel("$e$ (at $\\delta_{L,\\rm th}$)")
    ax2.set_ylim(0, 140)
    ax2.legend(loc="center right", fontsize=5.5)
    ax3 = fs.inch_axes(fig, 6.15, 0.5, 1.6, 1.95)
    ax3.plot([r["e"] for r in pr], [r["t1_over_t0"] for r in pr], "o-", color="k", ms=3)
    ax3.set_xlabel("$e$")
    ax3.set_ylabel("$t_1/t_0$")
    fs.save(fig, os.path.join(a.out, "fig_newton_gr_range"))
    plt.close(fig)
    for r in rows:
        print(json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()}))


if __name__ == "__main__":
    main()
