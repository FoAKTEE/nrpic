"""Figure of the locator check of the served statements.

    kb/.venv/bin/python -I fig_serve.py <checked.jsonl> <claim_ids.tsv> <out stem>

(a) claims per requesting track by final label; (b) statements that quote numbers: all
numbers in the located lines, all within three lines, some not found.
"""
import collections
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

OWNERS = ["A-emd-pbh", "B-emd-gw", "C-sidm", "D-bh-dress", "E-stoch-inf", "F-hills"]
LABELS = [("fulltext", fs.PAL["blue"]), ("to_verify", fs.PAL["yellow"]),
          ("judgement", fs.PAL["green"]), ("refuted", fs.PAL["red"])]


def main(checked, ids, stem):
    fs.use_style()
    rows = [json.loads(l) for l in open(checked) if l.strip()]
    lab = {}
    with open(ids) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            lab[p[0]] = p[2]
    cnt = collections.Counter((r["owner"], lab.get(r["key"], "?")) for r in rows)
    num = collections.Counter()
    for r in rows:
        n = r["numbers"]
        if not n.get("n"):
            continue
        k = "exact" if n["found"] == n["n"] else ("near" if n["near"] == n["n"] else "missing")
        num[(r["owner"], k)] += 1
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2), sharey=True)
    y = list(range(len(OWNERS)))[::-1]
    ax = axes[0]
    left = [0] * len(OWNERS)
    for name, col in LABELS:
        w = [cnt[(o, name)] for o in OWNERS]
        ax.barh(y, w, left=left, color=col, label=name, height=0.6)
        left = [a + b for a, b in zip(left, w)]
    for yy, tot in zip(y, left):
        ax.text(tot + 2, yy, str(tot), va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels(OWNERS)
    ax.set_xlabel("claims loaded")
    ax.set_xlim(0, max(left) * 1.15 + 1)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("(a) final label per requester", fontsize=10)
    ax = axes[1]
    left = [0] * len(OWNERS)
    for name, col in (("exact", fs.PAL["blue"]), ("near", fs.PAL["orange"]), ("missing", fs.PAL["red"])):
        w = [num[(o, name)] for o in OWNERS]
        ax.barh(y, w, left=left, color=col, label={"exact": "all in the lines", "near": "all within 3 lines",
                                                    "missing": "some not found"}[name], height=0.6)
        left = [a + b for a, b in zip(left, w)]
    for yy, tot in zip(y, left):
        ax.text(tot + 1, yy, str(tot), va="center", fontsize=8)
    ax.set_xlabel("statements quoting numbers")
    ax.set_xlim(0, max(left) * 1.2 + 1)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_title("(b) numbers found at the locator", fontsize=10)
    fig.tight_layout()
    print(fs.save(fig, stem))


if __name__ == "__main__":
    main(*sys.argv[1:4])
