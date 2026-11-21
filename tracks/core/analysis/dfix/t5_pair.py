#!/usr/bin/env python3
"""Test T5 of work package dfix: common horizon of a pair among three punctures.

    t5_pair.py RUN [RUN ...] --out PREFIX

RUN: run directories of cases/t5_pair_cpu.list (cases new, v03) or of the card list
(case t5_pair). Writes PREFIX.json and PREFIX.png: which of the three waiting surfaces
were searched, and the mass of the pair's common horizon against the expected band.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
BAND = (1.005, 1.030)
EXPECT = (0.5 + 0.5)*(1.0 + 0.5/(2.0*12.0))


def read(d):
    out = {}
    for n in range(3):
        rows = [ln.split() for ln in open(os.path.join(d, f"pair.horizon_summary_{n}.txt"))
                if not ln.startswith("#")]
        out[n] = np.array(rows, dtype=float).reshape(-1, 12) if rows else np.zeros((0, 12))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res, data = {"expected_mass": EXPECT, "band": BAND, "cases": {}}, {}
    for run in a.runs:
        for c in sorted(os.listdir(run)):
            d = os.path.join(run, c)
            if not os.path.isfile(os.path.join(d, "pair.horizon_summary_0.txt")):
                continue
            s = read(d)
            key = os.path.basename(run.rstrip("/")) + "/" + c
            data[key] = s
            res["cases"][key] = {
                "records": {n: int(len(s[n])) for n in range(3)},
                "surface0": [{"time": float(r[1]), "mass": float(r[2]), "h_rms": float(r[8]),
                              "mean_radius": float(r[10]), "min_radius": float(r[11])}
                             for r in s[0]]}
    with open(a.out + ".json", "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    print(json.dumps(res, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.24, right=0.98, bottom=0.18, top=0.95, wspace=0.30)
    keys = list(data)
    for k, key in enumerate(keys):
        col = fs.PAL["blue"] if key.endswith("v03") else fs.PAL["red"]
        for n in range(3):
            got = len(data[key][n]) > 0
            ax[0].plot([n], [len(keys) - 1 - k], "s", ms=11, mfc=col if got else "none", mec=col)
        if len(data[key][0]):
            ax[1].plot(data[key][0][:, 1], data[key][0][:, 2], "o", color=col, ms=5,
                       label=key.split("/")[-1])
    ax[0].set_xticks([0, 1, 2])
    ax[0].set_xticklabels(["pair (0, 1)", "all three", "pair (0, 2)"])
    ax[0].set_yticks(range(len(keys)))
    ax[0].set_yticklabels([k.split("/")[-1] + " (" + k.split("/")[0][-14:] + ")" for k in keys][::-1],
                          fontsize=8)
    ax[0].tick_params(which="minor", left=False, right=False, top=False, bottom=False)
    ax[0].set_xlim(-0.5, 2.5)
    ax[0].set_ylim(-0.6, len(keys) - 0.4)
    ax[0].set_xlabel("surface (filled: searched and found)")
    ax[1].axhspan(BAND[0], BAND[1], color="grey", alpha=0.15)
    ax[1].axhline(EXPECT, **fs.GUIDE)
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel("common-horizon mass, pair (0, 1)")
    ax[1].set_ylim(1.0, 1.035)
    ax[1].set_xlim(-0.005, 0.03)
    ax[1].legend(loc="lower right", fontsize=8)
    fs.save(fig, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
