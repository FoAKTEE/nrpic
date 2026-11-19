#!/usr/bin/env python3
"""Outcome of the test TC of tracks/core/JOURNAL-clump2.md: the cluster at rest and moving
(runs v0, v0.1, v0.3, v0.3s of one batch job). Reads the particle snapshots and the two
history files of every run, prints the measured numbers next to the predicted bands and
writes boost_evolution_check.json and fig_boost_evolution*.{pdf,png} into --out.

    boost_evolution_check.py --run RUN_ID [--out DIR] [--names v0,v0.1,v0.3,v0.3s]
"""
import argparse
import glob
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

FRACS = (0.10, 0.25, 0.50, 0.75, 0.90)
SPEED = {"v0": 0.0, "v0.1": 0.1, "v0.3": 0.3, "v0.3s": 0.3}


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        f.read(8)
        d = np.fromfile(f, dtype=np.float64, count=7 * n).reshape(n, 7)
    return t, d


def table(path):
    rows = [ln.split() for ln in open(path) if not ln.startswith("#") and ln.strip()]
    n = min(len(r) for r in rows)
    a = np.array([r[:n] for r in rows], dtype=float)
    _, idx = np.unique(a[::-1, 0], return_index=True)
    return a[::-1][idx]


def load(d):
    """dict of the histories of one run directory"""
    out = {}
    snaps = sorted(glob.glob(os.path.join(d, "*.part.[0-9]*.bin")))
    ts, xc, rad, sig, npart = [], [], [], [], []
    for p in snaps:
        t, a = read_snapshot(p)
        m = a[:, 6]
        c = (m[:, None] * a[:, 0:3]).sum(0) / m.sum()
        dx = a[:, 0:3] - c
        r = np.sqrt(np.sum(dx * dx, axis=1))
        o = np.argsort(r)
        cm = np.cumsum(m[o]) / m.sum()
        rad.append([float(r[o][np.searchsorted(cm, f)]) for f in FRACS])
        sig.append([float(math.sqrt(np.sum(m * dx[:, k] ** 2) / m.sum())) for k in range(3)])
        ts.append(t)
        xc.append(c)
        npart.append(len(m))
    out["t"] = np.array(ts)
    out["xc"] = np.array(xc)
    out["radii"] = np.array(rad)
    out["sigma"] = np.array(sig)
    out["np"] = np.array(npart)
    h = table(glob.glob(os.path.join(d, "*.nrpic.hst"))[0])
    out["ht"] = h[:, 0]
    out["sum_m"], out["sum_mW"] = h[:, 3], h[:, 4]
    out["sum_mu"] = h[:, 5:8]
    out["alpha_min"] = h[:, 15]
    out["np_hst"] = h[:, 2]
    z = table(glob.glob(os.path.join(d, "*.z4c.user.hst"))[0])
    out["zt"], out["H"], out["M"] = z[:, 0], np.sqrt(z[:, 3]), np.sqrt(z[:, 4])
    return out


def at(t, tt, y):
    return float(np.interp(t, tt, y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--names", default="v0,v0.1,v0.3,v0.3s")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    top = os.path.join(SCRATCH, a.run)
    os.makedirs(a.out, exist_ok=True)
    runs = {}
    for nm in a.names.split(","):
        d = os.path.join(top, nm)
        if glob.glob(os.path.join(d, "*.nrpic.hst")):
            runs[nm] = load(d)
    res = dict(run=a.run, runs={})
    ref = runs.get("v0")
    for nm, R in runs.items():
        v = SPEED[nm.split("_")[0]]
        t, x = R["t"], R["xc"][:, 0]
        tend = float(t[-1])
        o = dict(t_end=tend, t_end_hst=float(R["ht"][-1]), np_start=int(R["np"][0]),
                 np_end=int(R["np"][-1]), xc_end=[float(c) for c in R["xc"][-1]],
                 max_abs_xc_transverse=float(np.max(np.abs(R["xc"][:, 1:]))))
        if v > 0.0:
            o["speed_0_2_over_v"] = (at(2.0, t, x) - x[0]) / 2.0 / v
            o["speed_0_4_over_v"] = (at(4.0, t, x) - x[0]) / 4.0 / v
            if tend >= 49.9:
                o["speed_30_50_over_v"] = (at(50.0, t, x) - at(30.0, t, x)) / 20.0 / v
                o["speed_0_50_over_v"] = (at(50.0, t, x) - x[0]) / 50.0 / v
                o["xc_50_over_vt"] = (at(50.0, t, x) - x[0]) / (50.0 * v)
            o["speed_last_10_over_v"] = (x[-1] - at(tend - 10.0, t, x)) / 10.0 / v
        else:
            o["max_abs_xc"] = float(np.max(np.abs(R["xc"])))
        rr = R["radii"] / R["radii"][0]
        o["radii_start"] = [float(c) for c in R["radii"][0]]
        o["radii_ratio_min"] = [float(c) for c in rr.min(0)]
        o["radii_ratio_max"] = [float(c) for c in rr.max(0)]
        o["radii_ratio_end"] = [float(c) for c in rr[-1]]
        o["sigma_start"] = [float(c) for c in R["sigma"][0]]
        o["sigma_end"] = [float(c) for c in R["sigma"][-1]]
        if ref is not None and nm != "v0":
            n = min(len(t), len(ref["t"]))
            rel = R["radii"][:n] / ref["radii"][:n] - 1.0
            o["radii_vs_rest_max_abs"] = float(np.max(np.abs(rel)))
            tt = R["ht"][R["ht"] <= ref["ht"][-1]]
            dal = np.interp(tt, R["ht"], R["alpha_min"]) - np.interp(tt, ref["ht"],
                                                                      ref["alpha_min"])
            o["alpha_minus_rest_min"] = float(dal.min())
            o["alpha_minus_rest_max"] = float(dal.max())
            for tq in (10.0, 25.0, 30.0, 50.0):
                if tt[-1] >= tq - 1e-9:
                    o[f"alpha_minus_rest_{tq:g}"] = at(tq, tt, dal)
            o["constraint_ratio_max_after_5"] = dict(
                H=float(np.max((np.interp(ref["zt"], R["zt"], R["H"]) / ref["H"])[
                    ref["zt"] >= 5.0])) if ref["zt"][-1] >= 5.0 else None,
                M=float(np.max((np.interp(ref["zt"], R["zt"], R["M"]) / ref["M"])[
                    ref["zt"] >= 5.0])) if ref["zt"][-1] >= 5.0 else None)
        o["alpha_min_start"] = float(R["alpha_min"][0])
        o["alpha_min_min"] = float(R["alpha_min"].min())
        o["alpha_min_max"] = float(R["alpha_min"].max())
        o["alpha_min_end"] = float(R["alpha_min"][-1])
        P0 = float(R["sum_mu"][0, 0])
        o["sum_mux_start"] = P0
        if v > 0.0:
            rel = R["sum_mu"][:, 0] / P0 - 1.0
            o["sum_mux_rel_min"] = float(rel.min())
            o["sum_mux_rel_max"] = float(rel.max())
            o["sum_mux_rel_end"] = float(rel[-1])
            for tq in (2.0, 10.0, 25.0, 50.0):
                if R["ht"][-1] >= tq - 1e-9:
                    o[f"sum_mux_rel_{tq:g}"] = at(tq, R["ht"], rel)
        else:
            o["sum_mu_max_abs"] = float(np.max(np.abs(R["sum_mu"])))
        o["sum_mW_rel_end"] = float(R["sum_mW"][-1] / R["sum_mW"][0] - 1.0)
        o["H_norm"] = [float(R["H"][0]), float(R["H"].max()), float(R["H"][-1])]
        o["M_norm"] = [float(R["M"][0]), float(R["M"].max()), float(R["M"][-1])]
        res["runs"][nm] = o
    if "v0.1" in runs and "v0.3" in runs:
        A, Bq = runs["v0.1"], runs["v0.3"]
        tt = A["ht"][A["ht"] <= Bq["ht"][-1]]
        ra = np.interp(tt, A["ht"], A["sum_mu"][:, 0] / A["sum_mu"][0, 0])
        rb = np.interp(tt, Bq["ht"], Bq["sum_mu"][:, 0] / Bq["sum_mu"][0, 0])
        res["sum_mux_v0.1_minus_v0.3_max_abs"] = float(np.max(np.abs(ra - rb)))

    # ---- figures
    fs.use_style()
    col = {"v0": "k", "v0.1": fs.PAL["blue"], "v0.3": fs.PAL["red"],
           "v0.3s": fs.PAL["orange"]}
    lab = {"v0": "at rest", "v0.1": r"$v = 0.1$", "v0.3": r"$v = 0.3$",
           "v0.3s": r"$v = 0.3$, comoving shift"}
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, wspace=0.26,
                        hspace=0.24)
    for nm, R in runs.items():
        key = nm.split("_")[0]
        v = SPEED[key]
        c = col.get(key, "grey")
        ax[0, 0].plot(R["t"], R["xc"][:, 0], color=c, label=lab.get(key, nm))
        if v > 0:
            ax[0, 0].plot(R["t"], v * R["t"], color=c, ls=":", lw=1.0)
        ax[0, 1].plot(R["ht"], R["alpha_min"], color=c, label=lab.get(key, nm))
        ax[1, 0].plot(R["t"], R["radii"][:, 2] / R["radii"][0, 2], color=c,
                      label=lab.get(key, nm))
        ax[1, 0].plot(R["t"], R["radii"][:, 4] / R["radii"][0, 4], color=c, ls="--")
        ax[1, 0].plot(R["t"], R["radii"][:, 0] / R["radii"][0, 0], color=c, ls=":")
        if v > 0:
            ax[1, 1].plot(R["ht"], R["sum_mu"][:, 0] / R["sum_mu"][0, 0], color=c,
                          label=lab.get(key, nm))
    ax[0, 0].set_ylabel(r"centre of rest mass $x_c/M$")
    ax[0, 1].set_ylabel(r"minimum lapse")
    ax[1, 0].set_ylabel(r"radii of 10, 50, 90 per cent of the mass$/$start")
    ax[1, 1].set_ylabel(r"$\sum m u_x / P$")
    ax[1, 1].axhline(1.0, **fs.GUIDE)
    for a_ in ax.ravel():
        a_.set_xlabel(r"$t/M$")
    ax[0, 0].legend(loc="upper left")
    ax[0, 1].legend(loc="best")
    fs.save(fig, os.path.join(a.out, "fig_boost_evolution" + a.tag))

    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.96, wspace=0.26)
    for nm, R in runs.items():
        key = nm.split("_")[0]
        c = col.get(key, "grey")
        ax[0].plot(R["zt"], R["H"], color=c, label=lab.get(key, nm))
        ax[1].plot(R["zt"], R["M"], color=c, label=lab.get(key, nm))
    ax[0].set_ylabel(r"$H$-norm")
    ax[1].set_ylabel(r"$M$-norm")
    for a_ in ax:
        a_.set_xlabel(r"$t/M$")
        a_.set_yscale("log")
    ax[0].legend(loc="best")
    fs.save(fig, os.path.join(a.out, "fig_boost_evolution_constraints" + a.tag))

    with open(os.path.join(a.out, "boost_evolution_check" + a.tag + ".json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
