#!/usr/bin/env python3
"""Two card runs of the same list (scripts/gpu_batch.sh), made with two card executables
of the same source (release build against release candidate), compared file by file.

    card_pair.py --a CARD_RUN_DIR --b CARD_RUN_DIR --out DIR [--cases s3g,usr,...]

Every file that both case directories hold is compared, except the logs and the card
memory records (athena*.log, *.gpumem.csv) and the copied decks (*.athinput).  A file is
'identical' when its bytes are; otherwise histories (*.hst) report the largest column
difference over the largest magnitude of that column, separately for the columns above
1e-6 of the largest column of the file and for the others (card_v05.hst_columns), and
other files report their size and the share of differing bytes.
Prediction: tracks/core/JOURNAL.md, entry of 2026-11-21T07:47Z.
Writes DIR/card_pair.json and DIR/fig_card_pair.{pdf,png}.  Nothing is run here."""
import argparse
import filecmp
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
from card_v05 import CASES, hst_columns, status   # noqa: E402

SKIP = (".log", ".gpumem.csv", ".athinput")


def files(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "**", "*"), recursive=True)):
        if os.path.isfile(p) and not os.path.islink(p) and not p.endswith(SKIP):
            out.append(os.path.relpath(p, d))
    return out


def byte_share(p, q):
    x = np.fromfile(p, dtype=np.uint8)
    y = np.fromfile(q, dtype=np.uint8)
    if x.size != y.size:
        return None
    return float(np.count_nonzero(x != y))/max(x.size, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="first card run (the release build)")
    ap.add_argument("--b", required=True, help="second card run (the candidate)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases", default=",".join(CASES))
    a = ap.parse_args()
    A, B, out = (os.path.abspath(v) for v in (a.a, a.b, a.out))
    os.makedirs(out, exist_ok=True)
    ra, rb = status(A), status(B)
    res = {"a": A, "b": B, "cases": {}}
    worst = {}
    for n in a.cases.split(","):
        da, db = os.path.join(A, n), os.path.join(B, n)
        fa, fb = set(files(da)), set(files(db))
        c = {"exit": [ra.get(n), rb.get(n)], "only_a": sorted(fa - fb),
             "only_b": sorted(fb - fa), "files": {}}
        w = 0.0
        for f in sorted(fa & fb):
            p, q = os.path.join(da, f), os.path.join(db, f)
            if filecmp.cmp(p, q, shallow=False):
                c["files"][f] = "identical"
                continue
            if f.endswith(".hst"):
                h = hst_columns(p, q)
                c["files"][f] = h
                if h and "max_rel_large_columns" in h:
                    w = max(w, h["max_rel_large_columns"])
            else:
                c["files"][f] = {"size": os.path.getsize(p),
                                 "share_of_bytes_differing": byte_share(p, q)}
        c["n_files"] = len(fa & fb)
        c["n_identical"] = sum(1 for v in c["files"].values() if v == "identical")
        worst[n] = w
        res["cases"][n] = c
        print("%-8s exit %s/%s  files %3d  identical %3d  worst history column %.2e%s"
              % (n, ra.get(n), rb.get(n), c["n_files"], c["n_identical"], w,
                 "  only in one: %s" % (c["only_a"] + c["only_b"])
                 if c["only_a"] or c["only_b"] else ""))
    with open(os.path.join(out, "card_pair.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    names = list(res["cases"])
    x = np.arange(len(names))
    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.3))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.90, wspace=0.28)
    nf = [res["cases"][n]["n_files"] for n in names]
    ni = [res["cases"][n]["n_identical"] for n in names]
    ax[0].bar(x, nf, width=0.6, color=fs.SERIES[1], label="files compared")
    ax[0].bar(x, ni, width=0.6, color=fs.SERIES[0], label="byte-identical")
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(names, fontsize=7)
    ax[0].set_ylabel("files")
    ax[0].legend(frameon=False, fontsize=7)
    ax[0].set_title("(a) release card build against the candidate", fontsize=9)
    ax[1].bar(x, [max(worst[n], 1e-18) for n in names], width=0.55, color=fs.SERIES[0])
    ax[1].set_yscale("log")
    ax[1].set_ylim(1e-18, 1.0)
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(names, fontsize=7)
    ax[1].set_ylabel("histories: largest column difference / column")
    ax[1].set_title("(b) where files differ (floor 1e-18: none)", fontsize=9)
    fs.save(fig, os.path.join(out, "fig_card_pair"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
