#!/usr/bin/env python3
"""Reference tables for the first scan: first collapse of the homogeneous ellipsoid and
its Zel'dovich counterpart over ellipticity e and prolateness p.

    python3 scan_refs.py --out <dir>

Writes <dir>/ellipsoid_first_collapse.csv, <dir>/tophat.csv, <dir>/sr_estimate.csv and
the figures <dir>/fig_scan_*.{pdf,png}.

Scaling (validated as P7): with the start a0 = 1/(2 alpha) of arXiv:2605.04487 every
Newtonian model is scale free, so the tables are computed at delta_L(t_k) = 1 and hold
for any amplitude through
    t / t_k  ->  (t / t_k)|_1 * delta_L^(-3/2),     lengths / r_g, h  ->  (...)|_1 / delta_L.
The hoop threshold of the amplitude at fixed shape is therefore delta_L,th = h|_1.
"""
import argparse
import csv
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import ellipsoid as el  # noqa: E402
import tophat as th  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

E_GRID = [0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
P_FRAC = [-1.0, -0.5, 0.0, 0.5, 1.0]          # p = P_FRAC * e  (|p| <= e)
MCOL = {"isolated": fs.PAL["yellow"], "embedded": fs.PAL["green"], "added": fs.PAL["red"],
        "ZA": fs.PAL["blue"]}


def ellipsoid_table():
    rows = []
    for e in E_GRID:
        for pf in P_FRAC:
            p = pf * e
            al, be, ga = el.abg_from_dep(1.0, e, p)
            t0 = (0.5 / al) ** 1.5
            ac = 1.0 / al
            Az = el.za_axes((al, be, ga), ac)
            base = dict(e=e, p=p, alpha=al, beta=be, gamma=ga, t0_over_tk=t0)
            rows.append(dict(base, model="ZA", t1_over_tk=ac ** 1.5, a1=ac, axis=0,
                             t2_over_tk=(1.0 / be) ** 1.5 if be > 0 else np.inf,
                             A2_over_rg=Az[1], A3_over_rg=Az[2],
                             h1=el.h_za_closed(al, be, ga)))
            for m in el.MODELS:
                r = el.evolve((al, be, ga), model=m, n_collapse=2)
                c = r["collapses"]
                s = sorted(c[0]["A"])
                rows.append(dict(base, model=m, t1_over_tk=c[0]["t_over_tk"], a1=c[0]["a"],
                                 axis=c[0]["axis"],
                                 t2_over_tk=c[1]["t_over_tk"] if len(c) > 1 else np.nan,
                                 A2_over_rg=s[1], A3_over_rg=s[2], h1=c[0]["h"]))
    return rows


def sr_table():
    """End-point SR estimate against Newtonian, p = 0, three amplitudes (breaks scaling)."""
    rows = []
    for d in (0.05, 0.1, 0.3, 1.0):
        for e in (0.05, 0.2, 0.4):
            for m in ("isolated", "added"):
                rn = el.first_collapse(d, e, 0.0, model=m)
                rs = el.first_collapse(d, e, 0.0, model=m, sr=True)
                rows.append(dict(deltaL=d, e=e, p=0.0, model=m, t1_newton=rn["t1_over_tk"],
                                 t1_sr=rs["t1_over_tk"],
                                 rel=rs["t1_over_tk"] / rn["t1_over_tk"] - 1,
                                 v_end0=0.5 * (0.5 / rn["alpha"]) ** -0.5))
    return rows


def tophat_table():
    rows = []
    for d in (0.01, 0.03, 0.1, 0.3, 1.0):
        lam = d / 3.0
        r = th.za_tophat_summary(lam)                  # start at turnaround a0 = 1/(2 lam)
        rl = th.za_tophat_summary(lam, a0=1e-3 / lam)  # early start, growing mode
        rows.append(dict(deltaL=d, start="turnaround", t0_over_tk=r["t0"] / th.T_K,
                         t_ta_over_tk=r["t_ta_over_tk"], t_c_over_tk=r["t_c_over_tk"],
                         R_max_over_rg=r["R_max"], t_c_za_over_tk=r["t_c_za_over_tk"]))
        rows.append(dict(deltaL=d, start="a0*lam=1e-3", t0_over_tk=rl["t0"] / th.T_K,
                         t_ta_over_tk=rl["t_ta_over_tk"], t_c_over_tk=rl["t_c_over_tk"],
                         R_max_over_rg=rl["R_max"], t_c_za_over_tk=rl["t_c_za_over_tk"]))
    return rows


def write_csv(path, rows):
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.10g}" if isinstance(v, float) else v) for k, v in r.items()})


def figures(rows, out):
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax1 = fs.inch_axes(fig, 0.7, 0.55, 3.0, 2.6)
    ax2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.6)
    for m in ("ZA", "isolated", "embedded", "added"):
        for pf, ls in ((-1.0, ":"), (0.0, "-"), (1.0, "--")):
            sel = [r for r in rows if r["model"] == m and r["p"] == pf * r["e"]]
            e = np.array([r["e"] for r in sel])
            h = np.array([r["h1"] for r in sel])
            t1 = np.array([r["t1_over_tk"] / r["t0_over_tk"] for r in sel])
            lab = m if pf == 0.0 else None
            ax1.loglog(e, h, color=MCOL[m], ls=ls, label=lab)
            ax2.semilogx(e, t1, color=MCOL[m], ls=ls, label=lab)
    ax1.axhline(1.0, **fs.MASK_LINE)
    ax1.set_xlabel(r"ellipticity $e$")
    ax1.set_ylabel(r"$\delta_{L,\rm th}=h\,\delta_L$ (hoop at first collapse)")
    ax1.legend(loc="upper left")
    ax2.set_xlabel(r"ellipticity $e$")
    ax2.set_ylabel(r"$t_1/t_0$ (first collapse / start)")
    ax2.text(0.03, 0.05, r"solid $p=0$, dashed $p=e$, dotted $p=-e$", transform=ax2.transAxes)
    fs.save(fig, os.path.join(out, "fig_scan_hoop_time"))
    plt.close(fig)

    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.2))
    ax = fs.inch_axes(fig, 0.75, 0.55, 3.05, 2.5)
    za = {(r["e"], r["p"]): r["h1"] for r in rows if r["model"] == "ZA"}
    for m in ("isolated", "embedded", "added"):
        sel = [r for r in rows if r["model"] == m and r["p"] == 0.0]
        e = np.array([r["e"] for r in sel])
        ratio = np.array([r["h1"] / za[(r["e"], r["p"])] for r in sel])
        ax.semilogx(e, ratio, color=MCOL[m], label=m)
    ax.axhline(1.0, **fs.GUIDE)
    ax.set_xlabel(r"ellipticity $e$ ($p=0$)")
    ax.set_ylabel(r"$h_{\rm ellipsoid}/h_{\rm ZA}$")
    ax.legend(loc="upper right")
    fs.save(fig, os.path.join(out, "fig_scan_hoop_ratio"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    rows = ellipsoid_table()
    write_csv(os.path.join(a.out, "ellipsoid_first_collapse.csv"), rows)
    write_csv(os.path.join(a.out, "sr_estimate.csv"), sr_table())
    write_csv(os.path.join(a.out, "tophat.csv"), tophat_table())
    figures(rows, a.out)
    for r in rows:
        if r["p"] == 0.0:
            print(f"{r['model']:9s} e={r['e']:<6g} t0={r['t0_over_tk']:.4f} "
                  f"t1={r['t1_over_tk']:.4f} t2={r['t2_over_tk']:.4f} axis={r['axis']} "
                  f"A2={r['A2_over_rg']:.4g} A3={r['A3_over_rg']:.4g} h1={r['h1']:.4g}")


if __name__ == "__main__":
    main()
