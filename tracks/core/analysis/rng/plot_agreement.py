#!/usr/bin/env python3
"""Figure of the agreement test (run_agreement.py).

Top: for every implementation and every column of the table, the number of values whose
bits differ from the Python twin (the test passes only if all are zero).
Bottom: what the bit-identical construction costs in accuracy: the normal deviates of
the table against the same deviates computed with the library logarithm,
z = v sqrt(-2 ln(s) / s), in units of the last place of z.

Usage: plot_agreement.py --out FIG.png AGREEMENT_DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, HERE)
from nrpic import rng  # noqa: E402
from nrpic import figstyle  # noqa: E402
from compare_table import INT_COLS, REAL_COLS, read_table, twin  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("dir")
    args = ap.parse_args()
    res = json.load(open(os.path.join(args.dir, "agreement.json")))
    paths = list(res["tables"].keys())
    labels = []
    for p in paths:
        base = os.path.basename(p)
        if base.startswith("table_"):
            labels.append("standalone " + base[6:-4].replace("_", " "))
        else:
            labels.append("code, " + ("card" if "115230" in p or "gpu" in p else "processor"))
    keys, ints0, reals0, _ = read_table(paths[0])
    tints, treals = twin(keys)
    ndiff = np.zeros((len(paths), 15), dtype=np.int64)
    for i, p in enumerate(paths):
        _, ints, reals, _ = read_table(p)
        ndiff[i, :6] = np.count_nonzero(ints != tints, axis=0)
        ndiff[i, 6:] = np.count_nonzero(np.ascontiguousarray(reals).view(np.uint64)
                                        != np.ascontiguousarray(treals).view(np.uint64),
                                        axis=0)

    figstyle.use_style()
    fig = plt.figure(figsize=(8.0, 6.4))
    ax0 = fig.add_axes([0.30, 0.50, 0.68, 0.40])
    ax1 = fig.add_axes([0.10, 0.09, 0.88, 0.27])
    ax0.imshow(ndiff, cmap="Greys", vmin=0, vmax=1, aspect="auto")
    for i in range(ndiff.shape[0]):
        for j in range(ndiff.shape[1]):
            ax0.text(j, i, str(ndiff[i, j]), ha="center", va="center",
                     color="k" if ndiff[i, j] == 0 else "w", fontsize=8)
    ax0.set_yticks(range(len(labels)))
    ax0.set_yticklabels(labels)
    ax0.set_xticks(range(15))
    ax0.set_xticklabels(INT_COLS + REAL_COLS, rotation=60, ha="left")
    ax0.xaxis.tick_top()
    ax0.tick_params(which="both", length=0)
    ax0.set_xlabel(f"values with bits different from the Python twin, of {keys.shape[0]} keys")

    # normal deviates with the library logarithm on the same lattice points
    v1, v2, s, _, _ = rng._disk(keys[:, 0], keys[:, 1], keys[:, 2], keys[:, 4], keys[:, 5],
                                keys[:, 3], rng.KIND_NORMAL)
    f = np.sqrt(-2.0 * np.log(s.astype(np.float64) * 2.0**-52) / s.astype(np.float64))
    zl = np.concatenate([v1 * f, v2 * f])
    zt = np.concatenate([reals0[:, 4], reals0[:, 5]])
    ulp = np.spacing(np.abs(zl))
    d = (zt - zl) / ulp
    ax1.hist(np.clip(d, -200, 200), bins=np.linspace(-200, 200, 201),
             color=figstyle.PAL["red"], histtype="stepfilled", alpha=0.6)
    ax1.set_yscale("log")
    ax1.set_xlim(-200, 200)
    ax1.set_xlabel("normal deviate of the table minus the one from the library logarithm,"
                   " in units of the last place")
    ax1.set_ylabel("deviates")
    fig.savefig(args.out, dpi=200)
    print(json.dumps({"max_abs_ulp": float(np.abs(d).max()),
                      "median_abs_ulp": float(np.median(np.abs(d))),
                      "max_rel": float(np.max(np.abs(zt - zl) / np.abs(zl))),
                      "all_zero": bool(ndiff.sum() == 0)}))


if __name__ == "__main__":
    main()
