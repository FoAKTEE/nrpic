#!/usr/bin/env python3
"""Figure of the two-puncture tracker test (restart_test.py --only-by-binary).

    python tracker_fig.py --by DIR/by --out DIR

Reads the tracker files of the uninterrupted run (A), of the continued run of the new
build (B) and of the release (B_ref), and plots the x position of both punctures against
the cycle.  Writes DIR/fig_tracker_restart.{pdf,png} and DIR/summary.json (records per
file, largest difference of a value between A and B).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import restart_test as rt          # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--by", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    by, out = os.path.abspath(a.by), os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.985, bottom=0.17, top=0.95, wspace=0.3)
    res = {}
    for n, ax in enumerate(axs):
        tab = {}
        for d in ("A", "B", "B_ref"):
            f = os.path.join(by, d, "by2.co_%d.txt" % n)
            t = rt.tracker_table(f)
            tab[d] = np.array([[c] + v[:2] for c, v in t])
            res["co_%d %s" % (n, d)] = dict(records=len(t), header_lines=rt.header_count(f),
                                           first_cycle=t[0][0] if t else None)
        same = tab["A"].shape == tab["B"].shape
        res["co_%d max |A - B|" % n] = float(np.max(np.abs(tab["A"] - tab["B"]))) if same else None
        ax.plot(tab["A"][:, 0], tab["A"][:, 2], color=fs.PAL["blue"], marker="o", ms=5,
                mfc="none", label="uninterrupted")
        ax.plot(tab["B_ref"][:, 0], tab["B_ref"][:, 2], color=fs.PAL["yellow"], marker="s",
                ms=4, ls="none", label="v0.7, cut at cycle 4")
        ax.plot(tab["B"][:, 0], tab["B"][:, 2], color=fs.PAL["red"], marker="x", ms=5,
                ls="--", label="new, cut at cycle 4")
        ax.axvline(3.5, **fs.MASK_LINE)
        ax.set_xlabel("cycle of the record"); ax.set_ylabel("x of puncture %d" % n)
        ax.ticklabel_format(axis="y", useOffset=False)
        ax.legend(loc="best", fontsize=7)
    res["figures"] = fs.save(fig, os.path.join(out, "fig_tracker_restart"))
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
