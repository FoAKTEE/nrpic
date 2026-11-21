#!/usr/bin/env python3
"""Compare the DATA of pairs of cases of one run directory, value for value.

    compare_data.py <run directory> [--a __new] [--b __rel] [--out results/x.json]
                    [--fig figs/x]

Cases are paired by name: <name><a> against <name><b>.  For two executables whose
parameter dumps differ (new options with defaults), the output files cannot be equal
byte for byte: their headers repeat the parameters.  So the arrays are compared:

  *.bin  every variable of every MeshBlock (read with flib.Dump), exact equality and the
         largest absolute difference; time and cycle of the dump
  text   (history files and the like) the lines that do not start with '#', as text;
         if they differ, the largest absolute difference of the numbers

athena.log is skipped (wall-clock times).  Exit status 1 if any value differs or a file
is missing on one side.
"""

import argparse
import json
import os
import sys

import numpy as np

import flib


def files(d):
    out = []
    for root, _, fs in os.walk(d):
        for f in fs:
            if f != "athena.log":
                out.append(os.path.relpath(os.path.join(root, f), d))
    return sorted(out)


def cmp_bin(pa, pb):
    """(arrays compared, arrays identical, largest |difference|)"""
    try:
        da, db = flib.Dump(pa), flib.Dump(pb)
    except Exception:  # not a field dump of the mesh (a dump of another module): bytes
        with open(pa, "rb") as f, open(pb, "rb") as g:
            same = f.read() == g.read()
        return 1, int(same), 0.0 if same else float("inf")
    if da.time != db.time or da.cycle != db.cycle or da.names != db.names:
        return 1, 0, float("inf")
    ba = {da.key(b): b for b in da.blocks}
    bb = {db.key(b): b for b in db.blocks}
    if set(ba) != set(bb):
        return 1, 0, float("inf")
    n = same = 0
    worst = 0.0
    for k, b in ba.items():
        for v in da.names:
            x, y = b["data"][v], bb[k]["data"][v]
            n += 1
            if x.shape == y.shape and np.array_equal(x, y, equal_nan=True):
                same += 1
            elif x.shape != y.shape:
                worst = float("inf")
            else:
                with np.errstate(invalid="ignore"):
                    d = np.abs(x - y)
                worst = max(worst, float(np.nanmax(d)) if np.isfinite(d).any()
                            else float("inf"))
    return n, same, worst


def cmp_text(pa, pb):
    """(1, 1 if the data lines are the same text, largest |difference| of the numbers)"""
    def data(p):
        with open(p, errors="replace") as f:
            return [ln.rstrip() for ln in f if not ln.startswith("#")]
    la, lb = data(pa), data(pb)
    if la == lb:
        return 1, 1, 0.0
    worst = float("inf")
    if len(la) == len(lb):
        try:
            xa = np.array([[float(q) for q in ln.split()] for ln in la])
            xb = np.array([[float(q) for q in ln.split()] for ln in lb])
            if xa.shape == xb.shape:
                worst = float(np.nanmax(np.abs(xa - xb)))
        except ValueError:
            pass
    return 1, 0, worst


def figure(res, stem, la, lb):
    """bars: arrays (and text files) compared and identical, per case"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    names = list(res)
    n = [res[k]["compared"] for k in names]
    same = [res[k]["identical"] for k in names]
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH * 0.6, 2.6))
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.2, top=0.88)
    x = range(len(names))
    ax.bar([q - 0.2 for q in x], n, 0.4, color="0.7", label="arrays and tables compared")
    ax.bar([q + 0.2 for q in x], same, 0.4, color=fs.PAL["blue"], label="identical")
    for q, k in zip(x, names):
        ax.text(q, max(n) * 1.02, "max diff %.1e" % res[k]["max_abs_diff"], ha="center",
                fontsize=7)
    ax.set_ylim(0, max(n) * 1.25)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylabel("count")
    ax.set_title(f"data of <case>{la} against <case>{lb}", fontsize=9)
    ax.legend(fontsize=8, loc="lower right")
    fs.save(fig, stem)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("rundir")
    p.add_argument("--a", default="__new")
    p.add_argument("--b", default="__rel")
    p.add_argument("--out", default="")
    p.add_argument("--fig", default="")
    a = p.parse_args()
    res = {}
    bad = False
    for c in sorted(os.listdir(a.rundir)):
        if not c.endswith(a.a):
            continue
        name = c[:-len(a.a)]
        da, db = os.path.join(a.rundir, c), os.path.join(a.rundir, name + a.b)
        if not os.path.isdir(db):
            continue
        fa, fb = files(da), files(db)
        r = {"files": len(fa), "missing": sorted(set(fa) ^ set(fb)), "compared": 0,
             "identical": 0, "max_abs_diff": 0.0, "different": []}
        for f in fa:
            if f not in fb:
                continue
            fn = cmp_bin if f.endswith(".bin") else cmp_text
            n, same, worst = fn(os.path.join(da, f), os.path.join(db, f))
            r["compared"] += n
            r["identical"] += same
            r["max_abs_diff"] = max(r["max_abs_diff"], worst)
            if same != n:
                r["different"].append(f)
        res[name] = r
        print(f"{name}: {r['files']} files, {r['compared']} arrays and tables, "
              f"{r['compared'] - r['identical']} differ, largest difference "
              f"{r['max_abs_diff']:.3e}" +
              ("" if not r["missing"] else "; missing: " + ", ".join(r["missing"][:6])))
        bad = bad or r["compared"] != r["identical"] or bool(r["missing"]) or not fa
    if a.out:
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1)
    if a.fig and res:
        figure(res, a.fig, a.a, a.b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
