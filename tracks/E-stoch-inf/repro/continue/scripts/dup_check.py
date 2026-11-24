#!/usr/bin/env python3
"""Are the cycles that an original run recorded twice identical? (package repro/continue)

A chain segment that resumed from an earlier restart file recorded some cycles a second time
(RSF256: segments 1 and 2 both from t = 0; CL256S and AL2S: segment 2 from the t = 0 restart
after segment 1 had run on). Comparing the two records of the same cycle tests what prediction
J2 assumes: that a card run of this code repeats bit for bit from the same state, across jobs.
Uses the readers of join_check.py. Writes dup_check.json into the output directory.

    python3 dup_check.py --out DIR
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from join_check import read_blocks, compare_lines, vals, SCRATCH  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    runs = json.load(open(os.path.join(HERE, "runs.json")))
    res = {}
    for lab, r in runs.items():
        O = os.path.join(SCRATCH, r["orig"])
        res[lab] = {}
        for kind in ("sf.hst", "sf.con.hst"):
            _, bo = read_blocks(os.path.join(O, f"{r['base']}.{kind}"))
            out = []
            for i in range(len(bo)):
                for j in range(i + 1, len(bo)):
                    cyc = sorted(set(bo[i]) & set(bo[j]))
                    if cyc:
                        d = compare_lines(bo[i], bo[j], cyc)
                        d["blocks"] = [i, j]
                        d.pop("max_rel_diff_per_column")
                        out.append(d)
            res[lab][kind] = {"blocks": [[min(b), max(b)] for b in bo], "duplicates": out}
            print(lab, kind, "blocks", res[lab][kind]["blocks"], "duplicates",
                  [(d["cycles"], d["n"], d["identical"], d["max_rel_diff"]) for d in out])
    json.dump(res, open(os.path.join(a.out, "dup_check.json"), "w"), indent=1)

    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    labs = [l for l in res if res[l]["sf.con.hst"]["duplicates"]]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    w = 0.86 / len(labs)
    for i, lab in enumerate(labs):
        r = runs[lab]
        _, bo = read_blocks(os.path.join(SCRATCH, r["orig"], f"{r['base']}.sf.con.hst"))
        ax = fig.add_axes([0.09 + i * w, 0.16, w - 0.06, 0.72])
        for k, (b, col, ls) in enumerate(zip(bo, (fs.PAL["blue"], fs.PAL["red"]), ("-", "--"))):
            cyc = np.array(sorted(b))
            ax.plot(cyc, [vals(b[c])[3] for c in cyc], color=col, ls=ls,
                    label=f"segment {k + 1}")
        d = res[lab]["sf.con.hst"]["duplicates"][0]
        ax.set_title(f"{lab}: {d['identical']} of {d['n']} identical", fontsize=9)
        ax.set_xlim(0, max(max(b) for b in bo[:1]) * 1.15)
        ax.set_yscale("log")
        ax.set_xlabel("cycle", labelpad=-1)
        if i == 0:
            ax.set_ylabel(r"record $\langle|H|/[H]\rangle$")
            ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_dup"))


if __name__ == "__main__":
    main()
