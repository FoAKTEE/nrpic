"""Step 7 of the KB-G2 verifier: figures from registered runs.

(a) fig_ranks: rank of the right paper and of the first hit at the answer location (200-char
    slack) per question, three modes, held-out and golden sets (score.<set>.json of the
    score runs).
(b) fig_parse: the components S, E, B, A of the verifier's parse definition by recorded
    parse_status, and the verifier's counts of equations and bibliography entries against
    the database's (scan.json of the parse-scan run).
Also prints the counts used in VERIFIER.md, including the papers whose S or B passes only
because the source has no sectioning command or no \\cite (the leniency found in entry 7).
Usage: make_figures.py --heldout SCORE_JSON --golden SCORE_JSON --scan SCAN_JSON --out DIR
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

MODES = [("text", "text-only (BM25)", fs.PAL["blue"], "o", -0.25),
         ("hybrid", "hybrid (BM25 + vectors)", fs.PAL["red"], "s", 0.0),
         ("rerank", "rerank", fs.PAL["green"], "D", 0.25)]
MISS = 12


def rank_panel(ax, rows, qids, key, title, n):
    for mode, label, col, mk, dx in MODES:
        x, y, hits = [], [], 0
        for i, q in enumerate(qids):
            r = rows.get((q, mode), {}).get(key)
            x.append(i + dx)
            y.append(int(r) if r is not None else MISS)
            hits += r is not None
        ax.scatter(x, y, s=22, marker=mk, facecolor=col if key == "paper_rank" else "none", edgecolor=col,
                   lw=1.0, label=f"{label}: {hits}/{n}", zorder=3)
    ax.axhspan(10.5, 13.5, color="grey", alpha=0.12, lw=0)
    ax.set_ylim(13.5, 0.3)
    ax.set_yticks([1, 5, 10, MISS])
    ax.set_yticks([2, 3, 4, 6, 7, 8, 9], minor=True)
    ax.set_yticklabels(["1", "5", "10", "miss"])
    ax.set_xlim(-0.8, len(qids) - 0.2)
    ax.set_xticks(range(len(qids)))
    ax.set_xticklabels(qids, rotation=90, fontsize=7)
    ax.set_ylabel("rank")
    ax.text(0.0, 1.17, title, transform=ax.transAxes, ha="left", va="bottom")
    ax.legend(loc="lower left", ncol=3, frameon=False, fontsize=8, handletextpad=0.2, columnspacing=1.2,
              bbox_to_anchor=(0.0, 1.0), borderaxespad=0.05)


def fig_ranks(sc_h, sc_g, out):
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 10.4))
    h = 1.5
    tops = [9.75, 7.2, 4.65, 2.1]
    panels = [(sc_h, "paper_rank", "Held-out set (verifier's 24 questions): rank of the right paper"),
              (sc_h, "loc_rank_slack", "Held-out set: rank of the first hit at the answer location (200-char slack)"),
              (sc_g, "paper_rank", "Golden set (package's 32 questions): rank of the right paper"),
              (sc_g, "loc_rank_slack", "Golden set: rank of the first hit at the answer location (200-char slack)")]
    for (sc, key, title), top in zip(panels, tops):
        ax = fs.inch_axes(fig, 0.55, top - h, 7.3, h)
        rows = {(r["qid"], r["mode"]): r for r in sc["rows"]}
        qids = [q["qid"] for q in sc["questions"]]
        rank_panel(ax, rows, qids, key, title, len(qids))
    return fs.save(fig, os.path.join(out, "fig_ranks"))


def fig_parse(scan, out):
    rows = scan["rows"]
    stats = ["ok", "review", "pdf"]
    comps = [("S", "S sections"), ("E", "E equations"), ("B", "B bibliography"), ("A", "A abstract chunk"),
             ("A_lenient", "A' abstract any"), ("success", "all (strict)"), ("success_lenient", "all (lenient)")]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax = fs.inch_axes(fig, 0.55, 0.95, 3.0, 2.0)
    w = 0.26
    cols = [fs.PAL["blue"], fs.PAL["yellow"], fs.PAL["green"]]
    for j, st in enumerate(stats):
        rr = [r for r in rows if r["status"] == st]
        frac = [sum(bool(r[c]) for r in rr) / len(rr) for c, _ in comps]
        ax.bar(np.arange(len(comps)) + (j - 1) * w, frac, w, color=cols[j], label=f"{st} ({len(rr)})")
    ax.axhline(0.95, **fs.GUIDE)
    ax.set_xticks(range(len(comps)))
    ax.set_xticklabels([c for _, c in comps], rotation=40, ha="right", fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("fraction of papers passing")
    ax.legend(loc="upper center", ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.5, 1.2))
    for k, (key_my, key_db, label, x0) in enumerate([("my_eq", "db_eq", "display equations", 4.3),
                                                     ("my_bib", "db_bib", "bibliography entries", 6.4)]):
        ax2 = fs.inch_axes(fig, x0, 0.95, 1.5, 2.0)
        ax2.text(0.5, 1.04, label, transform=ax2.transAxes, ha="center", va="bottom")
        for j, st in enumerate(stats):
            rr = [r for r in rows if r["status"] == st]
            x = np.array([r[key_my] for r in rr], float) + 1
            y = np.array([r[key_db] for r in rr], float) + 1
            ax2.scatter(x, y, s=8, color=cols[j], alpha=0.7, lw=0, zorder=3 - j)
        g = np.logspace(0, 4, 10)
        ax2.plot(g, g, **fs.THIN)
        ax2.plot(g, 0.5 * (g - 1) + 1, **fs.GUIDE)
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.set_xlim(0.8, 3e3)
        ax2.set_ylim(0.8, 3e3)
        ax2.set_xlabel("verifier count + 1", labelpad=1)
        ax2.set_ylabel("database count + 1", labelpad=1)
    return fs.save(fig, os.path.join(out, "fig_parse"))


def counts(scan, sc_h, sc_g):
    rows = scan["rows"]
    res = {}
    succ = [r for r in rows if r["success"]]
    res["success"] = len(succ)
    res["success_with_S_by_no_section_command"] = sum(1 for r in succ if r["my_sec"] == 0 and r["db_sec"] == 0)
    res["success_with_B_by_no_cite"] = sum(1 for r in succ if r["my_cite_cmds"] == 0)
    res["success_with_S_or_B_lenient"] = sum(1 for r in succ if (r["my_sec"] == 0 and r["db_sec"] == 0)
                                             or r["my_cite_cmds"] == 0)
    res["lenient_ids"] = sorted(r["paper_id"] for r in succ if (r["my_sec"] == 0 and r["db_sec"] == 0)
                                or r["my_cite_cmds"] == 0)
    res["success_lenient"] = sum(bool(r["success_lenient"]) for r in rows)
    res["fail_components"] = dict(collections.Counter(
        "".join(k for k in "SEBA" if not r[k]) for r in rows if not r["success"]))
    res["fail_components_lenient"] = dict(collections.Counter(
        "".join(k for k in ("S", "E", "B", "A_lenient") if not r[k]) for r in rows if not r["success_lenient"]))
    res["papers_with_db_bib0_and_citations"] = sorted(r["paper_id"] for r in rows if r["db_bib"] == 0
                                                      and r["db_cit"] > 0)
    for name, sc in (("heldout", sc_h), ("golden", sc_g)):
        res[name] = sc["summary"]
        # paper rank 1 and union over modes
        rr = collections.defaultdict(dict)
        for r in sc["rows"]:
            rr[r["qid"]][r["mode"]] = r
        res[name + "_missed_all_modes"] = sorted(q for q, d in rr.items() if all(x["paper_rank"] is None
                                                                               for x in d.values()))
        res[name + "_missed_some_mode"] = {q: [m for m, x in d.items() if x["paper_rank"] is None]
                                           for q, d in rr.items() if any(x["paper_rank"] is None
                                                                         for x in d.values())}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heldout", required=True)
    ap.add_argument("--golden", required=True)
    ap.add_argument("--scan", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fs.use_style()
    sc_h, sc_g = json.load(open(a.heldout)), json.load(open(a.golden))
    scan = json.load(open(a.scan))
    os.makedirs(a.out, exist_ok=True)
    files = fig_ranks(sc_h, sc_g, a.out) + fig_parse(scan, a.out)
    c = counts(scan, sc_h, sc_g)
    with open(os.path.join(a.out, "counts.json"), "w") as f:
        json.dump(c, f, indent=1)
    print(json.dumps(c, indent=1))
    print("figures:", files)


if __name__ == "__main__":
    main()
