#!/usr/bin/env python3
"""R-split of threshold_ball (JOURNAL entry 18, batch 34): the SCOPE section-3 x-line ratio
||H|| / ||16 pi E|| (edge_compare.py's and c3_first_step.py's weight x^2 dx over 0 < x < xmax, E normalised
over the same range) split into the parts of H from the matter (x < 4.5), the edge and taper (4.5-6.5), the
vacuum (6.5-13) and the outermost cells (13 to the outer face); the squares of the parts add up to the
square of the total.

    ratio_split.py --out DIR NAME=RUNDIR[@XMAX] [NAME=RUNDIR ...] [--xmax 16] [--tmax 5]

RUNDIR holds tab/ball.con.*.tab and tab/ball.tmunu.*.tab. Writes DIR/ratio_split.json and
DIR/fig_ratio_split.{pdf,png}.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [("matter x<4.5", 0.0, 4.5), ("edge 4.5-6.5", 4.5, 6.5), ("vacuum 6.5-13", 6.5, 13.0),
         ("outer 13-face", 13.0, 1e9)]


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def split(rd, xmax):
    out = []
    for f in sorted(glob.glob(os.path.join(rd, "tab", "ball.con.*.tab"))):
        g = f.replace(".con.", ".tmunu.")
        if not os.path.isfile(g):
            continue
        t, c = read_tab(f)
        _, m = read_tab(g)
        x = c["x1v"]
        o = np.argsort(x)
        x, H, E = x[o], c["con_H"][o], 16.0 * math.pi * m["tmunu_E"][o]
        s = (x > 0) & (x < xmax)
        x, H, E = x[s], H[s], E[s]
        w = x * x * np.gradient(x)
        nE = math.sqrt(np.sum(w * E * E))
        rec = dict(t=t, total=math.sqrt(np.sum(w * H * H)) / nE)
        for name, lo, hi in BANDS:
            q = (x >= lo) & (x < hi)
            rec[name] = math.sqrt(np.sum(w[q] * H[q] ** 2)) / nE
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("members", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--xmax", type=float, default=16.0)
    ap.add_argument("--tmax", type=float, default=5.0)
    ap.add_argument("--edges", default=None, help="band edges, e.g. 3.5,4.5,6.5,13 (default 4.5,6.5,13)")
    a = ap.parse_args()
    global BANDS
    if a.edges:
        e = [0.0] + [float(v) for v in a.edges.split(",")] + [1e9]
        BANDS = [("x %g-%g" % (e[i], e[i + 1]) if e[i + 1] < 1e8 else "x %g-face" % e[i], e[i], e[i + 1])
                 for i in range(len(e) - 1)]
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for m in a.members:
        name, d = m.split("=", 1)
        xmax = a.xmax
        if "@" in d:                      # NAME=RUNDIR@XMAX: own outer face
            d, xs = d.rsplit("@", 1)
            xmax = float(xs)
        res[name] = [r for r in split(d, xmax) if r["t"] <= a.tmax + 1e-9]
        for r in res[name]:
            print("%-10s t=%5.2f total %.4f  " % (name, r["t"], r["total"])
                  + "  ".join("%s %.4f" % (b[0], r[b[0]]) for b in BANDS))
    json.dump(dict(xmax=a.xmax, bands=BANDS, members=res), open(os.path.join(a.out, "ratio_split.json"), "w"),
              indent=1)

    sys.path.insert(0, os.path.join(HERE, "..", "..", "note", "scripts"))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    n = len(res)
    fig, ax = plt.subplots(1, n, figsize=(fs.FULL_WIDTH, 2.6), sharey=True)
    ax = np.atleast_1d(ax)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.18, top=0.86, wspace=0.12)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
    for k, (name, rows) in enumerate(res.items()):
        t = [r["t"] for r in rows]
        ax[k].plot(t, [r["total"] for r in rows], color="k", lw=1.4, label="total")
        for j, (b, _, _) in enumerate(BANDS):
            ax[k].plot(t, [r[b] for r in rows], color=cols[j], lw=1.0, marker="o", ms=2.5, label=b)
        ax[k].axhline(0.1, color="0.6", lw=0.8, ls="--")
        ax[k].set_title(name, fontsize=8)
        ax[k].set_xlabel(r"$t/M$")
        ax[k].set_yscale("log")
        ax[k].set_ylim(1e-4, 1.0)
    ax[0].set_ylabel(r"part of $\|H\|/\|16\pi E\|$ on the $x$ line")
    ax[0].legend(fontsize=5.5, loc="lower right")
    fs.save(fig, os.path.join(a.out, "fig_ratio_split"))


if __name__ == "__main__":
    main()
