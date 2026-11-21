#!/usr/bin/env python3
"""Fates of the bisection runs of the monoenergetic cluster sequence (ladder row 4) and
their place on the binding-energy curve.

Fate rule (verify/JOURNAL.md, 15:30Z, fixed before the runs):
  COLLAPSE   an apparent horizon is found, or the central lapse (probe at the origin,
             history column 13) falls below 0.3;
  STABLE     neither by the end (300 M) and the mean central lapse over 200-300 M is
             within 0.03 of the equilibrium alpha_c;
  UNDECIDED  otherwise.
Also: radius enclosing 50 and 90 percent of the particle rest mass (coordinate radius
from the snapshots), drift of the mean central lapse, largest swing.

    cluster_fate.py RUN_DIR[:label] ... [--earlier] [--out DIR]

RUN_DIR holds st.nrpic.hst, st.horizon_summary_0.txt, st.part.*.bin and the
make_ic json (looked up through the particle_file of the log's command line).
--earlier adds the earlier sequence runs of /data/haiyangw/nrpic/runs/st (yc0900_v4,
yc0819_v4, yc0756_unpert, yc0605_v5, yc0500_v5; finer or different meshes) for
comparison. Writes cluster_fate.json into --out (default: the working directory) and
the figure tracks/core/verify/figs/cluster_threshold.{pdf,png}.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "analysis", "diag"))
sys.dont_write_bytecode = True
from nrpic import figstyle as fs  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402
from common import read_snapshot  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIGS = os.path.join(WT, "tracks", "core", "verify", "figs")
EARLIER = [("yc0900_v4", 0.900, "kick, M/2 static"), ("yc0819_v4", 0.819, "kick, M/2 static"),
           ("yc0756_unpert", 0.756, "no kick, M/2 static"),
           ("yc0605_v5", 0.605, "kick, AMR to M/16"), ("yc0500_v5", 0.500, "kick, AMR to M/16")]


def read_hst(path):
    rows = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        v = line.split()
        rows[float(v[0])] = [float(x) for x in v]
    return np.array([rows[t] for t in sorted(rows)])


def read_ah(path):
    out = []
    if not os.path.exists(path):
        return np.zeros((0, 3))
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        x = line.split()
        if x[2] != "nan":
            out.append([float(x[1]), float(x[2]), float(x[10])])
    return np.array(out) if out else np.zeros((0, 3))


def yc_of(d):
    m = re.search(r"yc0p(\d+)", d)
    return float("0." + m.group(1)) if m else None


def mass_radii(d, every=4):
    files = sorted(glob.glob(os.path.join(d, "st.part.*.bin")))[::every]
    t, r50, r90 = [], [], []
    for f in files:
        tt, a, tag, sp = read_snapshot(f)
        if len(a) < 10:
            continue
        r = np.sqrt(np.sum(a[:, :3] ** 2, axis=1))
        o = np.argsort(r)
        cm = np.cumsum(a[o, 6]) / a[:, 6].sum()
        t.append(tt)
        r50.append(float(r[o][np.searchsorted(cm, 0.5)]))
        r90.append(float(r[o][np.searchsorted(cm, 0.9)]))
    return dict(t=t, r50=r50, r90=r90)


def analyse(d, yc, label):
    h = read_hst(os.path.join(d, "st.nrpic.hst"))
    t, ac, npart = h[:, 0], h[:, 12], h[:, 2]
    ah = read_ah(os.path.join(d, "st.horizon_summary_0.txt"))
    g = stc.st_global(yc)
    a0 = float(g["alpha_c"])
    low = np.nonzero(ac < 0.3)[0]
    t_ah = float(ah[0, 0]) if len(ah) else None
    t_low = float(t[low[0]]) if len(low) else None
    late = (t >= 200.0) & (t <= 300.0)
    mean_late = float(ac[late].mean()) if late.any() else None
    if t_ah is not None or t_low is not None:
        fate = "COLLAPSE"
    elif t[-1] >= 299.0 and mean_late is not None and abs(mean_late - a0) <= 0.03:
        fate = "STABLE"
    else:
        fate = "UNDECIDED"
    pre = t < (min(x for x in (t_ah, t_low, 1e9) if x is not None))
    res = dict(dir=d, label=label, yc=yc, alpha_c_eq=a0, Eb_over_M0=float(g["Eb_over_M0"]),
               zc=float(g["zc"]), t_end=float(t[-1]), fate=fate, t_first_AH=t_ah,
               M_AH_first=float(ah[0, 1]) if len(ah) else None,
               M_AH_last=float(ah[-1, 1]) if len(ah) else None,
               t_alpha_below_0p3=t_low, mean_alpha_200_300=mean_late,
               alpha_min_before_collapse=float(ac[pre].min()),
               alpha_max_before_collapse=float(ac[pre].max()),
               np0=int(npart[0]), np_end=int(npart[-1]),
               t=t[::10].tolist(), alpha_c=ac[::10].tolist())
    # mean central lapse in 50 M windows (drift)
    win = []
    for t0 in np.arange(0.0, t[-1], 50.0):
        m = (t >= t0) & (t < t0 + 50.0)
        if m.any():
            win.append([float(t0), float(ac[m].mean()), float(ac[m].min()), float(ac[m].max())])
    res["windows50"] = win
    # added after the round-1 runs (JOURNAL 15:56Z): departure from equilibrium and, on the
    # unstable side of the turning point, the equal-binding member it may migrate to
    last = t >= t[-1] - 50.0
    res["mean_alpha_last50"] = float(ac[last].mean())
    res["departure_last50"] = float(ac[last].mean() / a0 - 1.0)
    tp = stc.binding_energy_maximum()["yc"]
    if yc < tp:
        mt = stc.migration_target(yc)
        res["migration_target"] = dict(yc=float(mt["yc"]), alpha_c=float(mt["alpha_c"]))
    # migration criterion of JOURNAL.md 16:07Z (fixed before round 2 was read): the
    # 200-300 M mean of the central lapse lies nearer the equal-binding partner's alpha_c
    # than the model's own
    try:
        pt = stc.migration_target(yc)
        res["partner"] = dict(yc=float(pt["yc"]), alpha_c=float(pt["alpha_c"]))
        if mean_late is not None:
            res["migrated"] = bool(abs(mean_late - pt["alpha_c"]) < abs(mean_late - a0))
    except Exception as err:          # no partner found in the scan range
        res["partner"] = dict(error=str(err))
    res["radii"] = mass_radii(d)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--earlier", action="store_true")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    tp = stc.binding_energy_maximum()
    res = dict(turning_point={k: float(v) for k, v in tp.items()}, runs=[], earlier=[])
    for spec in a.runs:
        d, _, lab = spec.partition(":")
        yc = yc_of(d)
        r = analyse(d, yc, lab or "kick, M/4")
        res["runs"].append(r)
        print(f"y_c={yc:.3f} {r['fate']:9s} t_end={r['t_end']:.1f} AH={r['t_first_AH']} "
              f"M_AH={r['M_AH_last']} alpha<0.3 at {r['t_alpha_below_0p3']} "
              f"mean alpha 200-300={r['mean_alpha_200_300']} (eq {r['alpha_c_eq']:.4f}) "
              f"range before collapse [{r['alpha_min_before_collapse']:.3f}, "
              f"{r['alpha_max_before_collapse']:.3f}]; last 50 M mean {r['mean_alpha_last50']:.4f}"
              f" (departure {r['departure_last50']:+.4f})"
              + (f"; migration target alpha_c {r['migration_target']['alpha_c']:.4f}"
                 if 'migration_target' in r else "")
              + f"; partner {r['partner']}; migrated (16:07Z criterion): {r.get('migrated')}")
    if a.earlier:
        for name, yc, lab in EARLIER:
            d = os.path.join("/data/haiyangw/nrpic/runs/st", name)
            r = analyse(d, yc, lab)
            r["earlier"] = name
            res["earlier"].append(r)
            print(f"earlier {name}: y_c={yc:.3f} {r['fate']} t_end={r['t_end']:.0f} "
                  f"AH={r['t_first_AH']} mean alpha 200-300={r['mean_alpha_200_300']}")
    stab = [r["yc"] for r in res["runs"] if r["fate"] == "STABLE"]
    coll = [r["yc"] for r in res["runs"] if r["fate"] == "COLLAPSE"]
    br = dict(lowest_stable=min(stab) if stab else None, highest_collapse=max(coll) if coll else None)
    res["bracket_this_mesh"] = br
    print("bracket on this mesh:", br, " turning point y_c* =", round(tp["yc"], 4))
    with open(os.path.join(a.out, "cluster_fate.json"), "w") as f:
        json.dump(res, f)
    figure(res)


def figure(res):
    fs.use_style()
    os.makedirs(FIGS, exist_ok=True)
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.16, top=0.90, wspace=0.42)
    runs = sorted(res["runs"], key=lambda r: -r["yc"])
    cols = fs.series_colors(len(runs), cmap="coolwarm")
    for r, c in zip(runs, cols):
        lab = r"$y_c=%.3g$" % r["yc"]
        ax[0].plot(r["t"], np.array(r["alpha_c"]) / r["alpha_c_eq"], color=c, lw=1.2, label=lab)
        if r["t_first_AH"] is not None:
            ax[0].axvline(r["t_first_AH"], color=c, ls=":", lw=1.0)
        if "migration_target" in r:
            ax[0].axhline(r["migration_target"]["alpha_c"] / r["alpha_c_eq"], color=c, ls=":",
                          lw=1.0)
        rr = r["radii"]
        ax[1].plot(rr["t"], rr["r50"], color=c, lw=1.2)
        ax[1].plot(rr["t"], rr["r90"], color=c, lw=1.2, ls="--")
    lo = min(0.85, min(np.nanmin(np.array(r["alpha_c"]) / r["alpha_c_eq"]) for r in runs) - 0.02)
    ax[0].set_ylim(max(lo, 0.0), 1.22)
    ax[0].text(0.03, 0.97, "dotted: equal-binding (migration) target", transform=ax[0].transAxes,
               ha="left", va="top", fontsize=6.5)
    ax[0].set_xlabel(r"$t/M$", labelpad=-2)
    ax[0].set_ylabel(r"central lapse / equilibrium value")
    ax[0].legend(fontsize=6.5, loc="lower left", ncol=2)
    ax[1].set_xlabel(r"$t/M$", labelpad=-2)
    ax[1].set_ylabel(r"$r_{50}$ (solid), $r_{90}$ (dashed) [$M$]")
    ax[1].set_ylim(0.0, None)
    # late mean central lapse against y_c, with the equilibrium alpha_c of the model and of
    # its equal-binding partner (the member a migrating model would settle at)
    ys = np.linspace(0.585, 0.765, 37)
    own = np.array([float(stc.st_global(v)["alpha_c"]) for v in ys])
    par = []
    for v in ys:
        try:
            par.append(float(stc.migration_target(v)["alpha_c"]))
        except Exception:
            par.append(np.nan)
    ax[2].plot(ys, own, color="k", lw=1.2, label=r"own equilibrium $\alpha_c$")
    ax[2].plot(ys, par, color="k", lw=1.0, ls=":", label=r"equal-binding partner")
    ax[2].axvline(res["turning_point"]["yc"], **fs.GUIDE)
    mk = dict(STABLE="o", COLLAPSE="s", UNDECIDED="^")
    for r in res["runs"]:
        if r["mean_alpha_200_300"] is not None:
            ax[2].plot(r["yc"], r["mean_alpha_200_300"], mk[r["fate"]], color=fs.PAL["blue"], ms=6,
                       mfc="none")
    ax[2].plot([], [], "o", color=fs.PAL["blue"], mfc="none", label="this work, rule: stable")
    ax[2].plot([], [], "^", color=fs.PAL["blue"], mfc="none", label="this work, rule: undecided")
    ax[2].set_xlim(0.765, 0.585)
    ax[2].set_xlabel(r"central $y_c$", labelpad=-2)
    ax[2].set_ylabel(r"mean central lapse, 200-300 $M$")
    ax[2].legend(fontsize=6.3, loc="upper left")
    fs.save(fig, os.path.join(FIGS, "cluster_threshold"))
    plt.close(fig)


if __name__ == "__main__":
    main()
