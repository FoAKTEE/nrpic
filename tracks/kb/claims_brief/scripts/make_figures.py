#!/usr/bin/env python3
"""Figures of package claims_brief from the outputs of make_ledger.py and the review sample.

  fig_seeds_by_section  brief seeds per section of the brief, split by outcome
  fig_check_review      left: CHECK.md rows per package, joined to a seed or not;
                        right: review sample per package, agree or disagree
Usage: python3 -I make_figures.py --ledger-run DIR --review REVIEW_SAMPLE.md --out DIR
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_ORDER = ["verified", "refuted", "annotated, located", "annotated, partial", "judgement, annotated",
             "judgement, no CHECK row", "open, no CHECK row"]
OUT_COL = {"verified": figstyle.PAL["green"], "refuted": figstyle.PAL["red"],
           "annotated, located": figstyle.PAL["blue"], "annotated, partial": figstyle.PAL2["sky"],
           "judgement, annotated": figstyle.PAL["orange"], "judgement, no CHECK row": figstyle.PAL["yellow"],
           "open, no CHECK row": "0.75"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger-run", required=True)
    ap.add_argument("--review", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    figstyle.use_style()
    c = json.load(open(os.path.join(a.ledger_run, "counts.json")))
    os.makedirs(a.out, exist_ok=True)

    # 1: seeds by section and outcome
    secs = list(c["outcomes_by_section"].keys())
    fig, ax = plt.subplots(figsize=(figstyle.FULL_WIDTH, 3.4))
    bottom = [0] * len(secs)
    x = range(len(secs))
    for o in OUT_ORDER:
        vals = [c["outcomes_by_section"][s].get(o, 0) for s in secs]
        if not any(vals):
            continue
        ax.bar(x, vals, bottom=bottom, color=OUT_COL[o], label=f"{o} ({sum(vals)})", width=0.7)
        bottom = [b + v for b, v in zip(bottom, vals)]
    for i, b in enumerate(bottom):
        ax.text(i, b + 0.8, str(b), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"§{s}" for s in secs])
    ax.set_xlabel("section of the brief (main text)")
    ax.set_ylabel("labelled statements (seeds)")
    ax.set_ylim(0, max(bottom) * 1.18)
    ax.legend(frameon=False, fontsize=7, ncol=2, loc="upper right")
    ax.set_title(f"{c['seeds']} seeds of the brief: outcome after the brief-check join and review", fontsize=9)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(a.out, "fig_seeds_by_section"))
    plt.close(fig)

    # 2: CHECK.md rows joined per package, and the review sample
    pk = c["check_rows_by_package"]
    names = list(pk.keys())
    rev = collections.defaultdict(lambda: [0, 0])
    for line in open(a.review, encoding="utf-8"):
        m = re.match(r"^\| \d+ \| (\S+) #\d+ \|.*\| (agree|disagree) \|", line)
        if m:
            rev[m.group(1)][0 if m.group(2) == "agree" else 1] += 1
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.4), gridspec_kw={"width_ratios": [1.6, 1]})
    j = [pk[n]["joined"] for n in names]
    u = [pk[n]["rows"] - pk[n]["joined"] for n in names]
    y = range(len(names))
    a1.barh(y, j, color=figstyle.PAL["blue"], label=f"joined to a seed ({sum(j)})")
    a1.barh(y, u, left=j, color="0.75", label=f"not joined ({sum(u)})")
    a1.set_yticks(list(y))
    a1.set_yticklabels(names, fontsize=8)
    a1.invert_yaxis()
    a1.set_xlabel("CHECK.md rows")
    a1.set_xlim(0, 118)
    a1.legend(frameon=False, fontsize=7, loc="lower right")
    a1.set_title(f"{c['check_rows']} rows of the brief check", fontsize=9)
    ag = [rev[n][0] for n in names]
    dg = [rev[n][1] for n in names]
    a2.barh(y, ag, color=figstyle.PAL["green"], label=f"agree ({sum(ag)})")
    a2.barh(y, dg, left=ag, color=figstyle.PAL["red"], label=f"disagree ({sum(dg)})")
    a2.set_yticks(list(y))
    a2.set_yticklabels([])
    a2.invert_yaxis()
    a2.set_xlim(0, 4)
    a2.set_xlabel("rows reviewed")
    a2.legend(frameon=False, fontsize=7, loc="lower right")
    a2.set_title("second-agent review (seed 20261121)", fontsize=9)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(a.out, "fig_check_review"))
    plt.close(fig)
    print("figures written to", a.out)


if __name__ == "__main__":
    main()
