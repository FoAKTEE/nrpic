"""Figure of the locator check of the served statements.

    kb/.venv/bin/python -I fig_serve.py <served_claims.tsv> <out stem>

(a) served statements per requesting track: covered by a claim of the K8 seed, not yet
covered (by the label the K8 rules would give), or without a paper locator; (b) statements that quote numbers:
all numbers in the located lines, all within three lines, some not found.
"""
import collections
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

OWNERS = ["A-emd-pbh", "B-emd-gw", "C-sidm", "D-bh-dress", "E-stoch-inf", "F-hills"]
CATS = [("K8 claim exists", "#7F7F7F"), ("no K8 claim: fulltext", fs.PAL["blue"]),
        ("no K8 claim: to_verify", fs.PAL["yellow"]), ("no K8 claim: judgement", fs.PAL["green"]),
        ("no paper locator", fs.PAL["red"])]


def main(table, stem):
    fs.use_style()
    rows = []
    with open(table) as f:
        hdr = next(f).rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(hdr, line.rstrip("\n").split("\t"))))
    cnt, num = collections.Counter(), collections.Counter()
    for r in rows:
        src = r["source"]
        cat = ("K8 claim exists" if src == "k8" else "no paper locator" if src == "no-locator"
               else f"no K8 claim: {r['labels']}")
        cnt[(r["owner"], cat)] += 1
        n = r["numbers_found/near/n"]
        if n != "-":
            fo, ne, tot = (int(x) for x in n.split("/"))
            num[(r["owner"], "exact" if fo == tot else "near" if ne == tot else "missing")] += 1
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 4.0), sharey=True)
    y = list(range(len(OWNERS)))[::-1]
    for ax, cats, counter, title, xl in (
            (axes[0], CATS, cnt, "(a) served statements and their claims", "statements"),
            (axes[1], [("exact", fs.PAL["blue"]), ("near", fs.PAL["orange"]), ("missing", fs.PAL["red"])], num,
             "(b) quoted numbers found at the locator", "statements quoting numbers")):
        left = [0] * len(OWNERS)
        for name, col in cats:
            w = [counter[(o, name)] for o in OWNERS]
            lab = {"exact": "all in the cited lines", "near": "all within 3 lines",
                   "missing": "some not found"}.get(name, name)
            ax.barh(y, w, left=left, color=col, label=lab, height=0.6)
            left = [a + b for a, b in zip(left, w)]
        for yy, tot in zip(y, left):
            ax.text(tot + 1.5, yy, str(tot), va="center", fontsize=8)
        ax.set_xlim(0, max(left) * 1.15 + 1)
        ax.set_xlabel(xl)
        ax.set_title(title, fontsize=10)
        ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(OWNERS)
    fig.tight_layout()
    print(fs.save(fig, stem))


if __name__ == "__main__":
    main(*sys.argv[1:3])
