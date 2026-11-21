#!/usr/bin/env python3
"""Test T7 of work package dfix: flux sphere centred on a moving puncture tracker.

    runreg.py --purpose "..." --cores 1 -- python3 tracks/core/analysis/dfix/t7_tracker.py \
        --exe <athena> [--fig PREFIX]
    t7_tracker.py --replot RUN --fig PREFIX

Runs problems/tests/accretion_tracker.athinput in $NRPIC_RUN_DIR/run/ with 4000 particles
of rest mass 1e-12 in the shell 1.9 < r < 2.1 about the puncture, half moving inwards and
half outwards, and checks
  (a) the centre written in atr.acc.hst against the tracker file atr.co_0.txt;
  (b) at every record: (number inside now) - (inside at t = 0) = n_in - n_out - n_excised,
      and the same for the rest mass;
  (c) the content of the sphere counted here from each snapshot and the tracker
      position, against the history column at the same time.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import io as nio   # noqa: E402

INPUT = os.path.join(REPO, "problems", "tests", "accretion_tracker.athinput")
C0 = np.array([0.1, -0.2, 0.05])
RAD = 2.0
MP = 1.0e-12


def make(path, n=4000, seed=7):
    rng = np.random.default_rng(seed)
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1)[:, None]
    r = rng.uniform(1.9, 2.1, n)
    sign = np.where(np.arange(n) % 2 == 0, -1.0, 1.0)
    speed = rng.uniform(0.4, 1.2, n)
    nio.write_nrp(path, C0 + r[:, None]*d, (sign*speed)[:, None]*d, np.full(n, MP))


def read_snap(path):
    b = open(path, "rb").read()
    t = float(np.frombuffer(b[8:16], dtype="<f8")[0])
    n = int(np.frombuffer(b[16:24], dtype="<i8")[0])
    rec = np.frombuffer(b[32:32 + 56*n], dtype="<f8").reshape(n, 7)
    return t, rec


def judge(d):
    hst = np.loadtxt(os.path.join(d, "atr.acc.hst"))
    co = np.loadtxt(os.path.join(d, "atr.co_0.txt"))
    res = {"records": int(len(hst)), "t_end": float(hst[-1, 0])}
    # (a) centre against the tracker file (columns: iteration, time, x, y, z, ...)
    dev = 0.0
    for row in hst:
        k = np.argmin(np.abs(co[:, 1] - row[0]))
        dev = max(dev, float(np.abs(co[k, 2:5] - row[2:5]).max()), float(abs(co[k, 1] - row[0])))
    res["centre_minus_tracker_max"] = dev
    # (a') the tracker file labels the position after the step of cycle n with n and
    # t^n (WriteTracker runs before the driver advances ncycle and time): record k >= 1
    # of the history is compared with tracker row k-1, record 0 with the input position
    by_iter = {int(r[0]): r for r in co}
    dpos, dtime = 0.0, 0.0
    for row in hst:
        k = int(round(row[1]))
        if k == 0:
            dpos = max(dpos, float(np.abs(row[2:5] - C0).max()))
            continue
        r = by_iter[k - 1]
        dpos = max(dpos, float(np.abs(r[2:5] - row[2:5]).max()))
        dtime = max(dtime, float(abs(row[0] - r[1] - (hst[1, 0] - hst[0, 0]))))
    res["centre_minus_tracker_row_before_max"] = dpos
    res["record_time_minus_row_time_minus_dt_max"] = dtime
    res["centre_displacement"] = float(np.linalg.norm(hst[-1, 2:5] - hst[0, 2:5]))
    # (b) identities
    res["number_identity_maxerr"] = float(np.abs((hst[:, 15] - hst[0, 15])
                                                 - (hst[:, 17] - hst[:, 20] - hst[:, 5])).max())
    res["mass_identity_maxerr"] = float(np.abs((hst[:, 16] - hst[0, 16])
                                               - (hst[:, 18] - hst[:, 21] - hst[:, 6])).max())
    res["n_inside_start"], res["n_inside_end"] = float(hst[0, 15]), float(hst[-1, 15])
    res["n_in"], res["n_out"], res["n_excised"] = float(hst[-1, 17]), float(hst[-1, 20]), float(hst[-1, 5])
    res["mE_in"], res["mE_out"] = float(hst[-1, 19]), float(hst[-1, 22])
    # (c) content from the snapshots
    res["snapshots"] = []
    for f in sorted(x for x in os.listdir(d) if x.startswith("atr.part.")):
        t, rec = read_snap(os.path.join(d, f))
        k = np.argmin(np.abs(hst[:, 0] - t))
        c = hst[k, 2:5]
        dist = np.linalg.norm(rec[:, 0:3] - c, axis=1)
        res["snapshots"].append({"time": t, "history_time": float(hst[k, 0]),
                                 "inside_counted_here": int(np.sum(dist < RAD)),
                                 "inside_history": float(hst[k, 15]),
                                 "closest_to_sphere": float(np.abs(dist - RAD).min())})
    return res, hst


def figure(res, hst, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.95, wspace=0.26)
    t = hst[:, 0]
    ax[0].plot(t, hst[:, 17], color=fs.PAL["blue"], label="crossed inwards")
    ax[0].plot(t, hst[:, 20], color=fs.PAL["red"], label="crossed outwards")
    ax[0].plot(t, hst[:, 15], color=fs.PAL["yellow"], label="inside")
    ax[0].plot(t, hst[0, 15] + hst[:, 17] - hst[:, 20] - hst[:, 5], **fs.GUIDE)
    for s in res["snapshots"]:
        ax[0].plot([s["time"]], [s["inside_counted_here"]], "o", mfc="none", mec="k", ms=7)
    ax[0].set_xlabel(r"$t/M$")
    ax[0].set_ylabel("particles (sphere on the tracker)")
    ax[0].legend(loc="center right", fontsize=8)
    ax[1].plot(t, (hst[:, 2] - hst[0, 2])*1e3, color=fs.PAL["blue"], label="x")
    ax[1].plot(t, (hst[:, 3] - hst[0, 3])*1e3, color=fs.PAL["red"], label="y")
    ax[1].plot(t, (hst[:, 4] - hst[0, 4])*1e3, color=fs.PAL["yellow"], label="z")
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel(r"$10^3 \times$ displacement of the centre $[M]$")
    ax[1].legend(loc="best", fontsize=8)
    fs.save(fig, out + "_tracker")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe")
    ap.add_argument("--fig")
    ap.add_argument("--replot")
    a = ap.parse_args()
    run = a.replot or os.environ.get("NRPIC_RUN_DIR")
    if not run:
        sys.exit("NRPIC_RUN_DIR is not set (start through runreg.py)")
    d = os.path.join(run, "run")
    if not a.replot:
        os.makedirs(d, exist_ok=True)
        make(os.path.join(d, "atr.nrp"))
        with open(os.path.join(d, "athena.log"), "w") as log:
            rc = subprocess.run([a.exe, "-i", INPUT, "-d", d], cwd=d, stdout=log,
                                stderr=subprocess.STDOUT).returncode
        print("exit", rc, flush=True)
    res, hst = judge(d)
    # a re-judgement of an earlier run writes into its own run directory when it has one
    outdir = os.environ.get("NRPIC_RUN_DIR") or run
    with open(os.path.join(outdir, "t7_tracker.json"), "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    print(json.dumps(res, indent=1))
    if a.fig:
        figure(res, hst, a.fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
