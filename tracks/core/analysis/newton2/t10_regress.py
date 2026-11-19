#!/usr/bin/env python3
"""Test T10 of work package newton2: judgement of the byte regression of cases.py t10.

    t10_regress.py --run RUNDIR_OF_cases.py_t10 [--out DIR]

Reads RUNDIR/t10.json (files identical and differing per case, this branch against the
branch start and against release core-v0.3) and, for every file that differs, the text
lines around the differing bytes in both versions; a file passes against the release only
if every differing line is the stored `last_time` of an output block (the deliberate
correction 2 of the branch start, tracks/core/interfaces/REQUESTS_ADF.md).
Writes DIR/t10_regress.json and DIR/t10_regress.{png,pdf}.
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


def differing_lines(fa, fb):
    a, b = open(fa, "rb").read(), open(fb, "rb").read()
    if len(a) != len(b):
        return None
    idx = [i for i in range(len(a)) if a[i] != b[i]] if len(a) < 5_000_000 else None
    if idx is None:
        return None
    lines, seen = [], set()
    for i in idx:
        s = a.rfind(b"\n", 0, i) + 1
        if s in seen:
            continue
        seen.add(s)
        e = a.find(b"\n", i)
        e2 = b.find(b"\n", i)
        lines.append((a[s:e].decode(errors="replace"), b[s:e2].decode(errors="replace")))
    return dict(bytes=len(idx), lines=lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    rep = json.load(open(os.path.join(a.run, "t10.json")))
    res = {"cases": {}, "pass_base": True, "pass_release": True}
    for case, r in rep.items():
        out = dict(base_identical=r["base"]["identical"], base_differ=r["base"]["differ"],
                   rel_identical=r["rel"]["identical"], rel_differ=r["rel"]["differ"],
                   log_results_equal_base=r["log_results_equal_base"], rel_details={})
        if r["base"]["differ"] or not r["log_results_equal_base"]:
            res["pass_base"] = False
        for f in r["rel"]["differ"]:
            dl = differing_lines(os.path.join(a.run, case, "new", f),
                                 os.path.join(a.run, case, "rel", f))
            ok = bool(dl) and all(x.split("=")[0].strip() == "last_time" and
                                  y.split("=")[0].strip() == "last_time"
                                  for x, y in dl["lines"])
            out["rel_details"][f] = dict(dl or {}, only_last_time=ok)
            if not ok:
                res["pass_release"] = False
        res["cases"][case] = out
    names = list(res["cases"])
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.27, top=0.95)
    c = res["cases"]
    ax.bar(x - 0.3, [c[n]["base_identical"] for n in names], 0.3, color=fs.PAL["blue"],
           label="identical to the branch start")
    ax.bar(x, [c[n]["rel_identical"] for n in names], 0.3, color=fs.PAL["green"],
           label="identical to release core-v0.3")
    ax.bar(x + 0.3, [len(c[n]["rel_differ"]) for n in names], 0.3, color=fs.PAL["red"],
           label=r"differ from the release (only last\_time)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, fontsize=8)
    ax.set_ylabel("output files")
    ax.legend(loc="upper right", fontsize=7)
    fs.save(fig, os.path.join(a.out, "t10_regress"))
    with open(os.path.join(a.out, "t10_regress.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(dict(pass_base=res["pass_base"], pass_release=res["pass_release"],
                          details={k: v["rel_details"] for k, v in c.items() if v["rel_details"]}),
                     indent=1))


if __name__ == "__main__":
    main()
