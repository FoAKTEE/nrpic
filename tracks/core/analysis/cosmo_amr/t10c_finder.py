#!/usr/bin/env python3
"""T10c of the work package cosmo-amr: the last stretch of the scouting run again, from
its restart file at t = 10, with four finder surfaces that can flow (prediction:
tracks/core/JOURNAL-cosmo-amr.md, entry of 2026-11-20 22:23).  Nothing is run here.

    t10c_finder.py --run RESTART_CASEDIR --base T10B_CASEDIR --out DIR

Writes DIR/t10c_summary.json and DIR/fig_t10c_finder.{pdf,png}: the searches of every
finder (reason, iterations, radius, area mass), and the restarted run against the
uninterrupted one (a restart on a refined mesh on a card)."""
import argparse
import glob
import json
import os
import sys

import numpy as np

import amrlib as A
from t10_scout import read_status, read_log

REASON = ["found", "area not finite", "expansion not finite", "expansion above hmean_tol",
          "mean radius negative", "area mass below 1e-10", "iteration limit"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    a.out = os.path.abspath(a.out)
    os.makedirs(a.out, exist_ok=True)
    res = {}
    lg = read_log(os.path.join(a.run, "athena.log"))
    h = A.read_hst(os.path.join(a.run, "peak.nrpic.hst"), like=os.path.join(a.base, "peak.nrpic.hst"))
    hb = A.read_hst(os.path.join(a.base, "peak.nrpic.hst"))
    sane = (np.isfinite(h["alpha_min"]) & (h["alpha_min"] > 0) & (h["np"] > 0)
            & (h["alpha_max"] < 1e6))
    res["run"] = {"exit": lg.get("exit"), "terminating": lg.get("terminating"),
                  "end": lg.get("end"), "amr": lg.get("amr_line"),
                  "gpu_mem_peak_MiB": lg.get("gpu_mem_peak_MiB"),
                  "first_record": [float(h["time"][0]), int(h["ncycle"][0]), int(h["nmb"][0])],
                  "last_sane_record": [float(h["time"][sane][-1]), int(h["ncycle"][sane][-1]),
                                       int(h["nmb"][sane][-1])],
                  "wall_s_last_report": float(lg["elapsed"][-1, 0]) if len(lg["elapsed"]) else None}
    gp = os.path.join(a.run, "peak.guard.txt")
    if os.path.exists(gp):
        with open(gp) as f:
            res["run"]["guard"] = [x[:300] for x in f.read().splitlines() if x.strip()][:4]
    # the restarted run against the uninterrupted one, record by record (paired by cycle)
    cb = {int(c): i for i, c in enumerate(hb["ncycle"])}
    pairs = [(i, cb[int(c)]) for i, c in enumerate(h["ncycle"]) if int(c) in cb and sane[i]]
    if pairs:
        i, j = np.array(pairs).T
        cmpr = {"records_paired": int(len(i))}
        for k in ("time", "alpha_min", "alpha_max", "E_max", "int_E", "proper_volume",
                  "mean_K"):
            d = np.abs(h[k][i]/hb[k][j] - 1.0)
            cmpr[k + "_max_rel"] = float(np.max(d))
            cmpr[k + "_rel_after_32_cycles"] = float(d[min(32, len(d)-1)])
        cmpr["nmb_equal"] = bool(np.array_equal(h["nmb"][i], hb["nmb"][j]))
        cmpr["np_equal"] = bool(np.array_equal(h["np"][i], hb["np"][j]))
        res["restart_vs_uninterrupted"] = cmpr
    fnd = {}
    files = sorted(glob.glob(os.path.join(a.run, "peak.horizon_status_*.txt")))
    for p in files:
        st = read_status(p)
        k = os.path.basename(p).split("_")[-1].split(".")[0]
        if not len(st):
            fnd[k] = {"searches": 0}
            continue
        f = {"searches": int(len(st)), "centre": [float(st[0, 12]), float(st[0, 13]),
                                                  float(st[0, 14])],
             "reasons": {REASON[int(q)]: int(np.sum(st[:, 3] == q)) for q in np.unique(st[:, 3])},
             "found": int(np.sum(st[:, 2] > 0)),
             "flow_iterations_min_max": [int(st[:, 4].min()), int(st[:, 4].max())],
             "points_outside_mesh_max": int(st[:, 11].max()),
             "rows": [{"cycle": int(r[0]), "time": float(r[1]), "found": int(r[2]),
                       "reason": int(r[3]), "iterations": int(r[4]), "area": float(r[5]),
                       "area_mass": float(r[6]), "mean_radius": float(r[7]),
                       "min_radius": float(r[8]), "expansion_integral": float(r[9]),
                       "min_abs_expansion_integral": float(r[10])} for r in st]}
        g = st[st[:, 2] > 0]
        if len(g):
            f["first_found"] = {"cycle": int(g[0, 0]), "time": float(g[0, 1]),
                                "area_mass": float(g[0, 6]), "mean_radius": float(g[0, 7]),
                                "min_radius": float(g[0, 8])}
            f["last_found"] = {"cycle": int(g[-1, 0]), "time": float(g[-1, 1]),
                               "area_mass": float(g[-1, 6]), "mean_radius": float(g[-1, 7]),
                               "min_radius": float(g[-1, 8])}
        fnd[k] = f
        print("finder", k, "centre", f["centre"], "searches", f["searches"], "found",
              f["found"], f["reasons"], "iterations", f["flow_iterations_min_max"],
              f.get("first_found"))
    res["finder"] = fnd
    with open(os.path.join(a.out, "t10c_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps(res["run"])[:900])
    print(json.dumps(res.get("restart_vs_uninterrupted")))

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.2))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.15, top=0.93, wspace=0.30)
    for i, k in enumerate(fnd):
        if not fnd[k]["searches"]:
            continue
        rows = fnd[k]["rows"]
        t = np.array([r["time"] for r in rows])
        c = fs.SERIES[i % len(fs.SERIES)]
        lab = "finder %s (%.2g, %.2g, %.2g)" % ((k,) + tuple(fnd[k]["centre"]))
        ax[0].plot(t, [r["reason"] for r in rows], "o", ms=3 + i, mfc="none", color=c,
                   label=lab)
        ok = np.array([r["found"] > 0 for r in rows])
        mr = np.array([r["mean_radius"] for r in rows])
        am = np.array([r["area_mass"] for r in rows])
        ax[1].plot(t[ok], mr[ok], "o-", ms=3, color=c, label=lab)
        ax[1].plot(t[~ok], np.abs(mr[~ok]), "x", ms=4, color=c, alpha=0.4)
        if ok.any():
            ax[2].semilogy(t[ok], am[ok], "o-", ms=3, color=c, label=lab)
    ax[0].set_yticks(range(7))
    ax[0].set_yticklabels(["found", "area nan", "exp. nan", "hmean tol", "radius < 0",
                           "mass < 1e-10", "iter. limit"], fontsize=7)
    ax[0].legend(frameon=False, fontsize=6, loc="center left")
    ax[1].set_ylabel("mean coordinate radius (o found, x |last radius| of a failed search)",
                     fontsize=7)
    ax[2].set_ylabel(r"area mass $\sqrt{A/16\pi}$ of found surfaces")
    for q in ax:
        q.set_xlabel("conformal time")
    fs.save(fig, os.path.join(a.out, "fig_t10c_finder"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
