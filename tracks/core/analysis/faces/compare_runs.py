#!/usr/bin/env python3
"""Compare the output files of pairs of cases of one run directory byte for byte.

    compare_runs.py <run directory> [--a __new] [--b __rel] [--out results/x.json]
                    [--fig figs/x]

Cases are paired by name: <name><a> against <name><b>.  Every file of the two case
directories is compared by its sha256, except athena.log (wall-clock times).  In the
field dumps and history files the header repeats the input parameters, which are the
same in both cases.  Exit status 1 if any file differs or is missing on one side.
"""

import argparse
import hashlib
import json
import os
import sys


def tree(d):
    out = {}
    for root, _, files in os.walk(d):
        for f in files:
            if f == "athena.log":
                continue
            p = os.path.join(root, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, d)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def figure(res, stem, la, lb):
    """bars: files compared and files identical, per case"""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "python"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    names = list(res)
    n = [res[k]["files"] for k in names]
    same = [res[k]["identical"] for k in names]
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH * 0.6, 2.6))
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.2, top=0.9)
    x = range(len(names))
    ax.bar([q - 0.2 for q in x], n, 0.4, color="0.7", label="output files compared")
    ax.bar([q + 0.2 for q in x], same, 0.4, color=fs.PAL["blue"], label="byte-identical")
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylabel("files")
    ax.set_title(f"<case>{la} against <case>{lb}", fontsize=9)
    ax.legend(fontsize=8)
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
        ta, tb = tree(da), tree(db)
        diff = sorted(k for k in set(ta) | set(tb) if ta.get(k) != tb.get(k))
        res[name] = {"files": len(ta), "identical": len(ta) - len([k for k in diff if k in ta]),
                     "different": diff}
        print(f"{name}: {len(ta)} files, {len(diff)} differ" +
              ("" if not diff else ": " + ", ".join(diff[:8])))
        bad = bad or bool(diff) or not ta
    if a.out:
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1)
    if a.fig and res:
        figure(res, a.fig, a.a, a.b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
