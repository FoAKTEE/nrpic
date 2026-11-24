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
from join_check import read_blocks, compare_lines, SCRATCH  # noqa: E402


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


if __name__ == "__main__":
    main()
