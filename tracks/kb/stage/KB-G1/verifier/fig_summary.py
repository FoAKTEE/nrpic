"""Summary figure of the KB-G1 verifier (tests P, C, K, Q).

Usage: python3 fig_summary.py <outdir>  (reads verdicts.tsv next to this script and
<outdir>/params.json, <outdir>/answers.json; writes <outdir>/fig_summary.{pdf,png})
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    rows = list(csv.DictReader(open(os.path.join(HERE, "verdicts.tsv")), delimiter="\t"))
    params = json.load(open(os.path.join(out, "params.json")))
    answers = json.load(open(os.path.join(out, "answers.json")))
    fs.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 7.0))
    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.08, top=0.95, wspace=0.75, hspace=0.42)

    # top left: verdicts per test
    ax = axes[0, 0]
    tests = ["P", "C", "K", "Q"]
    names = {"P": "P papers", "C": "C claims", "K": "K params", "Q": "Q questions"}
    kinds = [("CONFIRMED", fs.PAL["blue"]), ("NOT CONFIRMED", fs.PAL["yellow"]),
             ("WRONG", fs.PAL["red"])]
    left = np.zeros(len(tests))
    for k, col in kinds:
        n = np.array([sum(1 for r in rows if r["test"] == t and r["verdict"] == k) for t in tests])
        ax.barh(np.arange(len(tests)), n, left=left, color=col, label=k.lower())
        for i, v in enumerate(n):
            if v:
                ax.text(left[i] + v / 2, i, str(v), ha="center", va="center", color="white", fontsize=9)
        left += n
    ax.set_yticks(np.arange(len(tests)))
    ax.set_yticklabels([names[t] for t in tests])
    ax.invert_yaxis()
    ax.set_xlabel("items")
    ax.set_title("verdicts")
    ax.legend(loc="lower right", fontsize=8)
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())

    # top right: parameter index staleness on today's main
    ax = axes[0, 1]
    by = params["stale"]["by_file"]
    items = sorted(by.items(), key=lambda kv: -len(kv[1]))
    lab = [p.replace("athenak/src/", "") for p, _ in items]
    val = [len(v) for _, v in items]
    ax.barh(np.arange(len(val)), val, color=fs.PAL["red"])
    ax.set_yticks(np.arange(len(val)))
    ax.set_yticklabels(lab, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("(block, name) pairs read on main,\nabsent from the index")
    rc = params["recall"]
    ax.set_title("K: index at %s vs main %s" % (params["indexed_commit"][:7], params["main"][:7]),
                 fontsize=10)
    ax.text(0.35, 0.04, "recall at the indexed\ncommit, particles/ and\npgen/nrpic/: %d/%d calls"
            % (sum(r["calls"] for r in rc) - sum(len(r["missed"]) for r in rc), sum(r["calls"] for r in rc)),
            transform=ax.transAxes, fontsize=7)
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())

    # bottom left: equation numbers of the four papers of the first questions
    ax = axes[1, 0]
    eq = answers["equations"]
    pids = list(eq)
    agree = [eq[p]["common"] - len(eq[p]["differ"]) for p in pids]
    differ = [len(eq[p]["differ"]) for p in pids]
    ax.bar(np.arange(len(pids)), agree, color=fs.PAL["blue"], label="number equal")
    ax.bar(np.arange(len(pids)), differ, bottom=agree, color=fs.PAL["red"], label="number differs")
    ax.set_xticks(np.arange(len(pids)))
    ax.set_xticklabels(pids, rotation=20, fontsize=8)
    ax.set_ylabel("labelled equations")
    ax.set_title("Q: equation numbers, KB vs mine")
    ax.set_ylim(0, max(np.array(agree) + np.array(differ)) * 1.35)
    ax.legend(loc="upper right", fontsize=8)
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())

    # bottom right: cited locators per question
    ax = axes[1, 1]
    qs = list(range(1, 10))
    tot = [sum(1 for x in answers["locators"] + answers["code"] if x["q"] == q) for q in qs]
    ok = [sum(1 for x in answers["locators"] + answers["code"] if x["q"] == q and x["ok"]) for q in qs]
    ax.bar(np.arange(len(qs)), ok, color=fs.PAL["blue"], label="token found in range")
    ax.bar(np.arange(len(qs)), np.array(tot) - np.array(ok), bottom=ok, color=fs.PAL["red"],
           label="not found")
    ax.set_xticks(np.arange(len(qs)))
    ax.set_xticklabels([f"Q{q}" for q in qs])
    ax.set_ylabel("cited locators checked")
    ax.set_title("Q: cited locators")
    ax.set_ylim(0, max(tot) * 1.45)
    ax.legend(loc="upper left", fontsize=8, ncol=1)
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    fs.save(fig, os.path.join(out, "fig_summary"))


if __name__ == "__main__":
    main()
