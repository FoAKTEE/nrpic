#!/usr/bin/env python3
"""Work package newton2: the embedded ellipsoid at 96^3 on a processor against the same
case on a card (merged builds), from the group history of the patch.

    t4d_twin.py --proc DIR --card DIR [--out DIR]

DIR: run directories that hold newton.newton.g1.hst (and newton.newton.hst).  Compared
at every record: columns 38 to 43 (J_ij of the patch in physical coordinates) and
columns 50 to 55 (d2J/dT2), relative to the largest value of each column over the run;
K and W of the history; the record of the first minimum of the short axis
(5 J_xx/M)^(1/2).  Passes within 1e-9 for J (the prediction of the journal), with the
same record of the minimum.
Writes DIR/t4d_twin.json and DIR/t4d_twin.{png,pdf}.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402


def table(path):
    rows, last = [], None
    for ln in open(path):
        if ln.strip() and not ln.startswith("#") and ln != last:
            rows.append(ln.split())
            last = ln
    return np.array(rows, dtype=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proc", required=True)
    ap.add_argument("--card", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    gp = table(os.path.join(a.proc, "newton.newton.g1.hst"))
    gc = table(os.path.join(a.card, "newton.newton.g1.hst"))
    hp = table(os.path.join(a.proc, "newton.newton.hst"))
    hc = table(os.path.join(a.card, "newton.newton.hst"))
    m = min(len(gp), len(gc))
    res = {"proc": a.proc, "card": a.card, "records": [int(len(gp)), int(len(gc))],
           "times_equal": bool(np.array_equal(gp[:m, 0], gc[:m, 0]))}

    def dev(x, y, cols):
        sc = np.abs(y[:, cols]).max(axis=0)
        d = np.abs(x[:m, cols] - y[:m, cols])/np.where(sc > 0, sc, 1.0)
        return d

    dJ = dev(gp, gc, slice(37, 43))
    d2J = dev(gp, gc, slice(49, 55))
    dKW = dev(hp, hc, slice(4, 6))
    res["J_max"] = float(dJ.max())
    res["d2J_max"] = float(d2J.max())
    res["K_max"], res["W_max"] = float(dKW[:, 0].max()), float(dKW[:, 1].max())
    rp = np.sqrt(5.0*gp[:m, 37]/gp[:m, 5])
    rc = np.sqrt(5.0*gc[:m, 37]/gc[:m, 5])

    def first_min(r):
        k = np.nonzero((r[1:-1] < r[:-2]) & (r[1:-1] <= r[2:]))[0]
        return int(k[0] + 1) if len(k) else -1

    res["first_min_record"] = [first_min(rp), first_min(rc)]
    res["first_min_cosmic_time"] = [float(gp[first_min(rp), 3]), float(gc[first_min(rc), 3])]
    res["pass"] = bool(res["times_equal"] and res["J_max"] < 1e-9 and len(gp) == len(gc)
                       and res["first_min_record"][0] == res["first_min_record"][1]
                       and res["first_min_record"][0] > 0)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.95, wspace=0.3)
    T = gp[:m, 3]
    axs[0].plot(T, rp, color=fs.PAL["red"], label="processor")
    axs[0].plot(T, rc, color=fs.PAL["blue"], ls="--", label="card")
    axs[0].set_xlabel(r"cosmic time $T/t_k$ since the turnaround")
    axs[0].set_ylabel(r"short axis $(5 J_{xx}/M)^{1/2}$")
    axs[0].legend(loc="lower left", fontsize=7)
    axs[1].semilogy(T, np.maximum(dJ.max(axis=1), 1e-17), color=fs.PAL["red"], label=r"$J_{ij}$")
    axs[1].semilogy(T, np.maximum(d2J.max(axis=1), 1e-17), color=fs.PAL["blue"],
                    label=r"$d^2J_{ij}/dT^2$")
    axs[1].semilogy(T[:len(dKW)], np.maximum(dKW.max(axis=1), 1e-17), color=fs.PAL["green"],
                    label=r"$K$, $W$")
    axs[1].axhline(1e-9, color="k", lw=1.0, ls=":")
    axs[1].set_xlabel(r"cosmic time $T/t_k$ since the turnaround")
    axs[1].set_ylabel("|processor - card| / largest value")
    axs[1].legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "t4d_twin"))
    with open(os.path.join(a.out, "t4d_twin.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
