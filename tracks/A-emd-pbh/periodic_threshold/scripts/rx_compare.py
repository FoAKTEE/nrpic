#!/usr/bin/env python3
"""RX reader (periodic_threshold JOURNAL 2026-11-27 23:47 PST): rows of peak.nrpic.hst of the straight run A and of
the run B continued from A's restart file, matched by cycle, for the cycles after the restart.

  rx_compare.py --run RUNDIR --out OUTDIR      (RUNDIR/v06/{A,B}, RUNDIR/v08/{A,B} from rx_run.sh)
Writes OUTDIR/rx_compare.json and fig_rx.{png,pdf}: largest relative difference over all columns per cycle.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def hst(path):
    names = None
    with open(path) as f:
        for ln in f:
            if ln.startswith("# [1]"):
                names = [w.split("=")[1] for w in ln[1:].split()]
    return names, np.loadtxt(path, comments="#", ndmin=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    curves = {}
    for v in ("v06", "v08"):
        names, A = hst(os.path.join(a.run, v, "A", "peak.nrpic.hst"))
        _, B = hst(os.path.join(a.run, v, "B", "peak.nrpic.hst"))
        c0 = int(B[0, 1])
        ia = {int(c): i for i, c in enumerate(A[:, 1])}
        rows = []
        for j in range(len(B)):
            c = int(B[j, 1])
            if c <= c0 or c not in ia:
                continue
            x, y = A[ia[c]], B[j]
            den = np.maximum(np.abs(x), 1e-300)
            rel = np.where((x == 0) & (y == 0), 0.0, np.abs(x - y) / den)
            k = int(np.argmax(rel))
            rows.append(dict(cycle=c, t=float(x[0]), maxrel=float(rel.max()), worst=names[k],
                             alpha_min_rel=float(rel[15]), int_E_rel=float(rel[8]), identical=bool(np.all(x == y))))
        res[v] = dict(restart_cycle=c0, n_rows=len(rows), all_identical=all(r["identical"] for r in rows),
                      maxrel=max((r["maxrel"] for r in rows), default=None), rows=rows)
        curves[v] = rows
        print(v, "restart cycle", c0, "rows", len(rows), "all identical", res[v]["all_identical"],
              "max rel", res[v]["maxrel"])
        for r in rows:
            print("   cycle %3d t %.5f maxrel %.3e (%s) alpha_min %.3e int_E %.3e" % (
                r["cycle"], r["t"], r["maxrel"], r["worst"], r["alpha_min_rel"], r["int_E_rel"]))
    json.dump(res, open(os.path.join(a.out, "rx_compare.json"), "w"), indent=1)

    sys.path.insert(0, HERE)
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for v, col in (("v06", fs.PAL["blue"]), ("v08", fs.PAL["red"])):
        r = curves[v]
        ax.semilogy([q["cycle"] for q in r], [max(q["maxrel"], 1e-18) for q in r], "o-", ms=3, color=col,
                    label="core-%s.%s (zero plotted at 1e-18)" % (v[1], v[2:]))
    ax.axhline(1e-14, color="k", lw=0.8)
    ax.set_xlabel("cycle after the restart file")
    ax.set_ylabel("largest relative difference, B vs A")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_rx"))


if __name__ == "__main__":
    main()
