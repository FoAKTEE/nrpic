#!/usr/bin/env python3
"""Lead check of claims5 (batch 37): draw five verdicts with the lead's own seed and print each
claim at its stored locator rows for reading; recount the T census and its interval from the
verdict files; draw a figure of the census by verdict.

    python check5.py --seed 3720261127 --out DIR

Draw: stratified, 3 of the rows counted right and 2 of the rows counted not right of
tracks/kb/claims5/work/verdicts_T.tsv (131 rows), so that both directions of a verdict are tested.
Reading: tracks/kb/claims5/scripts/show.py (read-only on the database; text of kb-data/raw is read
as text, nothing there is executed). Census: claims5's 131 rows plus claims4's 13 T rows
(tracks/kb/claims4/work/verdicts_TR.tsv, cls T). Writes drawn.tsv, show.txt, census.json and
fig_census.png/.pdf into DIR.
"""
import argparse
import csv
import json
import os
import random
import subprocess
import sys

from scipy.stats import beta

HERE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.abspath(os.path.join(HERE, "..", ".."))
V5 = os.path.join(KB, "claims5", "work", "verdicts_T.tsv")
V4 = os.path.join(KB, "claims4", "work", "verdicts_TR.tsv")
SHOW = os.path.join(KB, "claims5", "scripts", "show.py")


def rows(path, cls=None):
    with open(path) as f:
        r = list(csv.DictReader(f, delimiter="\t"))
    return [x for x in r if cls is None or x["cls"] == cls]


def cp(k, n, a=0.05):
    lo = beta.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0
    return [float(lo), float(hi)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    t5 = rows(V5)
    t4 = rows(V4, "T")
    rng = random.Random(a.seed)
    right = [x for x in t5 if x["right"] == "1"]
    notr = [x for x in t5 if x["right"] == "0"]
    drawn = rng.sample(right, 3) + rng.sample(notr, 2)
    with open(os.path.join(a.out, "drawn.tsv"), "w") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["k", "claim_id", "verdict", "right", "borderline", "action", "note"])
        for x in drawn:
            w.writerow([x["k"], x["claim_id"], x["verdict"], x["right"], x["borderline"], x["action"], x["note"]])
    ids = [x["claim_id"] for x in drawn]
    out = subprocess.run([sys.executable, "-I", SHOW, *ids, "--siblings", "--ctx", "2"],
                         capture_output=True, text=True, check=True).stdout
    with open(os.path.join(a.out, "show.txt"), "w") as f:
        f.write(out)

    k5 = sum(x["right"] == "1" for x in t5)
    k4 = sum(x["right"] == "1" for x in t4)
    n, k = len(t5) + len(t4), k5 + k4
    byv = {}
    for x in t5 + t4:
        byv[x["verdict"]] = byv.get(x["verdict"], 0) + 1
    census = {"seed": a.seed, "drawn": ids, "claims5": [k5, len(t5)], "claims4_T": [k4, len(t4)],
              "census": [k, n], "rate": k / n, "cp95": cp(k, n), "claims5_cp95": cp(k5, len(t5)),
              "by_verdict": byv,
              "borderline_right": sum(x["right"] == "1" and x["borderline"] == "1" for x in t5 + t4)}
    with open(os.path.join(a.out, "census.json"), "w") as f:
        json.dump(census, f, indent=1)
    print(json.dumps(census, indent=1))

    sys.path.insert(0, HERE)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle  # copy of python/nrpic/figstyle.py
    figstyle.use_style()
    order = sorted(byv, key=lambda v: -byv[v])
    fig, ax = plt.subplots(figsize=(figstyle.COLUMN_WIDTH + 0.6, 2.8))
    cols = [figstyle.PAL["blue"] if v in ("right", "right_locator") else figstyle.PAL["red"] for v in order]
    ax.bar(range(len(order)), [byv[v] for v in order], color=cols)
    for i, v in enumerate(order):
        ax.text(i, byv[v] + 1, str(byv[v]), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("claims of class T")
    ax.set_ylim(0, max(byv.values()) * 1.18)
    ax.set_title(f"T census {k}/{n} right as worded (CP 95 %: {census['cp95'][0]:.3f}-{census['cp95'][1]:.3f})",
                 fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, f"fig_census.{ext}"), dpi=160)


if __name__ == "__main__":
    main()
