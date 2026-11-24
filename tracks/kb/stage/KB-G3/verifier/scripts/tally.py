"""Rates with binomial intervals and the four figures of the KB-G3 verifier.

.venv/bin/python -I tally.py --draw DRAW_RUN --parse PARSE_RUN --bib BIB_RUN --verdicts DIR --out DIR
Inputs: DRAW_RUN/sample/allocation.json; verdicts/{sample_verdicts,refutations,code_verdicts}.tsv;
PARSE_RUN/parse_papers.tsv; BIB_RUN/{bib_verdicts_auto.tsv,bib_summary.json}.
Writes DIR/tally.json and DIR/fig_{sample,refutations,bib,parse}.{pdf,png}.
"""
import argparse
import collections
import csv
import json
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import beta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402


def cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


def read_tsv(p):
    csv.field_size_limit(10 ** 7)
    return list(csv.DictReader(open(p), delimiter="\t"))


def main():
    ap = argparse.ArgumentParser()
    for k in ("draw", "parse", "bib", "verdicts", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    out = {}

    # ---------------- item 1
    alloc = json.load(open(os.path.join(a.draw, "sample", "allocation.json")))
    sv = read_tsv(os.path.join(a.verdicts, "sample_verdicts.tsv"))
    per = collections.defaultdict(lambda: [0, 0])
    cell = collections.defaultdict(lambda: [0, 0])
    for r in sv:
        per[r["stratum"]][0] += int(r["correct"])
        per[r["stratum"]][1] += 1
        cell[(r["stratum"], r["track"])][0] += int(r["correct"])
        cell[(r["stratum"], r["track"])][1] += 1
    item1 = {}
    for s in sorted(per):
        k, n = per[s]
        item1[s] = {"k": k, "n": n, "rate": k / n, "cp95": cp(k, n), "N": alloc["strata"][s]["size"]}
    K = sum(v[0] for v in per.values())
    N = sum(v[1] for v in per.values())
    item1["all"] = {"k": K, "n": N, "rate": K / N, "cp95": cp(K, N)}
    # population estimate weighted by cell sizes, with a stratified variance (cells with n = 1 add 0)
    tot = 0.0
    var = 0.0
    Npop = 0
    for (s, tr), (k, n) in cell.items():
        Nc = alloc["strata"][s]["cells"][tr]["N"]
        p = k / n
        tot += Nc * p
        Npop += Nc
        if n > 1:
            var += Nc ** 2 * (1 - n / Nc) * p * (1 - p) / (n - 1)
    item1["weighted_population"] = {"estimate": tot / Npop, "se": math.sqrt(var) / Npop, "N": Npop}
    item1["reading_counts"] = dict(collections.Counter(r["reading"] for r in sv))
    out["item1"] = item1

    # ---------------- item 2
    rv = read_tsv(os.path.join(a.verdicts, "refutations.tsv"))

    def cls(v):
        v = v.upper()
        if v.startswith("NOT CONFIRMED"):
            return "not confirmed"
        if v.startswith("NOT CHECKED"):
            return "not checked"
        if v.startswith("PARTLY"):
            return "partly checked"
        if "(" in v:
            return "confirmed, qualified"
        return "confirmed"
    groups = {"brief seed": "brief seeds", "defect": "printed defects", "superseding": "superseding"}
    item2 = {g: dict(collections.Counter(cls(r["verdict"]) for r in rv if r["group"] == g)) for g in groups}
    out["item2"] = item2

    # ---------------- item 3
    bsum = json.load(open(os.path.join(a.bib, "bib_summary.json")))
    out["item3"] = {"drawn_total": bsum["drawn_total"], "whole_snapshot": bsum["whole_snapshot"]}
    d = bsum["drawn_total"]
    printed_n = d.get("MATCH", 0) + d.get("MISSED", 0) + d.get("WRONG", 0) + d.get("DOI_PRINTED_ARXIV_TARGET", 0)
    resolved = d.get("MATCH", 0) + d.get("DOI_PRINTED_ARXIV_TARGET", 0)
    out["item3"]["drawn_printed_id"] = {"n": printed_n, "resolved": resolved, "rate": resolved / printed_n, "cp95": cp(resolved, printed_n)}
    w = bsum["whole_snapshot"]
    wp = w.get("MATCH", 0) + w.get("MISSED", 0) + w.get("WRONG", 0) + w.get("DOI_PRINTED_ARXIV_TARGET", 0)
    out["item3"]["whole_printed_id"] = {"n": wp, "missed": w.get("MISSED", 0), "missed_frac": w.get("MISSED", 0) / wp,
                                       "missed_frac_of_all": w.get("MISSED", 0) / w["entries"]}

    # ---------------- item 4
    cv = read_tsv(os.path.join(a.verdicts, "code_verdicts.tsv"))
    out["item4"] = {k: dict(collections.Counter(r["verdict"].split(" ")[0] for r in cv if r["kind"] == k)) for k in ("param", "link")}

    # ---------------- item 5
    pp = read_tsv(os.path.join(a.parse, "parse_papers.tsv"))
    k5 = sum(int(r["parsed"]) for r in pp)
    out["item5"] = {"parsed": k5, "n": len(pp), "rate": k5 / len(pp), "cp95_if_sample": cp(k5, len(pp)),
                    "fails": dict(collections.Counter(f for r in pp for f in r["fails"].split(",") if f))}
    with open(os.path.join(a.out, "tally.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))

    # ---------------- figures
    red, blue, grey = fs.PAL["red"], fs.PAL["blue"], "0.55"
    # fig_sample
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.0))
    ax = fig.add_axes([0.16, 0.2, 0.8, 0.72])
    labels = ["S1\nchecked", "S2\nmachine", "S3\nto_verify", "S4\njudgement", "all 60"]
    keys = ["S1", "S2", "S3", "S4", "all"]
    for i, s in enumerate(keys):
        v = item1[s]
        lo, hi = v["cp95"]
        ax.errorbar([i], [v["rate"]], yerr=[[v["rate"] - lo], [hi - v["rate"]]], fmt="o", color=red, ms=5, capsize=3, lw=1.5)
        ax.text(i + 0.12, v["rate"] - 0.005, "%d/%d" % (v["k"], v["n"]), fontsize=8, va="top")
    ax.axhline(item1["weighted_population"]["estimate"], **fs.GUIDE)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.minorticks_off()
    ax.set_xlim(-0.5, len(keys) - 0.3)
    ax.set_ylim(0.25, 1.05)
    ax.set_ylabel("fraction correct (95% CP)")
    fs.save(fig, os.path.join(a.out, "fig_sample"))
    plt.close(fig)

    # fig_refutations
    cats = ["confirmed", "confirmed, qualified", "partly checked", "not checked", "not confirmed"]
    colors = [fs.PAL["green"], fs.PAL["yellow"], fs.PAL["orange"], grey, red]
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 2.6))
    ax = fig.add_axes([0.3, 0.4, 0.64, 0.55])
    for j, g in enumerate(groups):
        left = 0
        for c, col in zip(cats, colors):
            n = item2[g].get(c, 0)
            if n:
                ax.barh([j], [n], left=left, color=col, edgecolor="k", lw=0.5, label=c if j == 0 or c not in item2[list(groups)[0]] else None)
                ax.text(left + n / 2, j, str(n), ha="center", va="center", fontsize=8)
            left += n
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([groups[g] for g in groups], fontsize=8)
    ax.minorticks_off()
    ax.set_xlabel("claims")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
    ax.legend(handles, cats, fontsize=7, ncol=2, loc="upper center", bbox_to_anchor=(0.3, -0.33))
    ax.invert_yaxis()
    fs.save(fig, os.path.join(a.out, "fig_refutations"))
    plt.close(fig)

    # fig_bib
    bv = read_tsv(os.path.join(a.bib, "bib_verdicts_auto.tsv"))
    papers = []
    for r in bv:
        if r["paper_id"] not in papers:
            papers.append(r["paper_id"])
    vcat = ["MATCH", "DOI_PRINTED_ARXIV_TARGET", "MISSED", "WRONG", "NONE_PRINTED", "NONE_PRINTED_DB_HAS"]
    vcol = [fs.PAL["green"], fs.PAL["yellow"], red, "k", "0.8", fs.PAL["orange"]]
    vlab = ["printed id = target", "DOI printed, arXiv target", "printed id, no target", "printed id, other target", "no id printed", "no id printed, target set"]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.07, 0.3, 0.6, 0.52])
    cnt = {p: collections.Counter(r["id_verdict"] for r in bv if r["paper_id"] == p) for p in papers}
    for i, p in enumerate(papers):
        bottom = 0
        for c, col in zip(vcat, vcol):
            n = cnt[p].get(c, 0)
            if n:
                ax.bar([i], [n], bottom=bottom, color=col, edgecolor="k", lw=0.4)
            bottom += n
    ax.set_xticks(range(len(papers)))
    ax.set_xticklabels(papers, rotation=60, ha="right", fontsize=7)
    ax.minorticks_off()
    ax.set_ylabel("drawn cited keys")
    ax.set_ylim(0, 10.5)
    ax2 = fig.add_axes([0.76, 0.3, 0.2, 0.52])
    bottom = 0
    for c, col in zip(vcat, vcol):
        n = w.get(c, 0) / w["entries"]
        ax2.bar([0], [n], bottom=bottom, color=col, edgecolor="k", lw=0.4)
        bottom += n
    ax2.set_xticks([0])
    ax2.set_xticklabels(["all %d\nentries" % w["entries"]], fontsize=8)
    ax2.minorticks_off()
    ax2.set_ylabel("fraction")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in vcol]
    ax.legend(handles, vlab, fontsize=7, ncol=3, loc="upper left", bbox_to_anchor=(0.0, 1.27), frameon=False)
    fs.save(fig, os.path.join(a.out, "fig_bib"))
    plt.close(fig)

    # fig_parse
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.9))
    specs = [("my_words", "db_body_words", "words: my flattening", "words: body chunks", 0.5),
             ("my_displays", "db_equations", "display blocks: my count", "equation rows", 0.7),
             ("my_sections", "db_sections", "(sub)sections: my count", "section rows", 0.7)]
    for j, (xk, yk, xl, yl, frac) in enumerate(specs):
        ax = fig.add_axes([0.07 + j * 0.33, 0.18, 0.25, 0.72])
        xs = np.array([float(r[xk] or 0) for r in pp]) + 1
        ys = np.array([float(r[yk] or 0) for r in pp]) + 1
        bad = np.array([r["parsed"] == "0" for r in pp])
        ax.scatter(xs[~bad], ys[~bad], s=4, color=grey, alpha=0.5, lw=0, rasterized=True)
        ax.scatter(xs[bad], ys[bad], s=10, color=red, lw=0, label="fails my definition")
        lim = [1, max(xs.max(), ys.max()) * 1.5]
        ax.plot(lim, lim, **fs.GUIDE)
        ax.plot(lim, [l * frac for l in lim], color="k", lw=1.0, ls=":")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.set_xlabel(xl + " + 1")
        ax.set_ylabel(yl + " + 1")
        if j == 0:
            ax.legend(fontsize=7, loc="upper left")
    fs.save(fig, os.path.join(a.out, "fig_parse"))
    plt.close(fig)


if __name__ == "__main__":
    main()
