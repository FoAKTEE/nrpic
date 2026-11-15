"""Figures of the quality report and the claims layer (project style python/nrpic/figstyle.py).

    kb/.venv/bin/python -I kb/kbtool/qa_figures.py <qa.json> <out_dir>

fig_qa_claims:     claims per track by status (stacked bars) and by label
fig_qa_eqcount:    independent count of numbered display lines against the database, per
                   sampled paper (log-log, with the line of equality), and the differences
fig_qa_retrieval:  rank of the expected paper and of the expected locator per golden
                   question, text (BM25) and hybrid where run
"""
import json
import os
import sys

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STATUS_ORDER = ["checked", "located", "partial", "unresolved", "unlocated", "refuted", "stale"]
STATUS_COLOR = {"checked": fs.PAL["blue"], "located": "#8fb3d9", "partial": fs.PAL["yellow"],
                "unresolved": fs.PAL["red"], "unlocated": "0.75", "refuted": "k", "stale": "0.5"}


def fig_claims(rep, out):
    c = rep["C9"]
    tracks = sorted(c["by_track_status"], key=str)
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fig.add_axes([0.08, 0.17, 0.56, 0.75])
    x = np.arange(len(tracks))
    bottom = np.zeros(len(tracks))
    for s in STATUS_ORDER:
        v = np.array([c["by_track_status"][t].get(s, 0) for t in tracks], float)
        if v.sum() == 0:
            continue
        ax.bar(x, v, 0.75, bottom=bottom, color=STATUS_COLOR[s], label=s, edgecolor="none")
        bottom += v
    ax.set_xticks(x)
    ax.set_xticklabels([str(t) for t in tracks], rotation=30, ha="right")
    ax.set_ylabel("claims")
    ax.minorticks_off()
    ax.tick_params(axis="y", which="minor", left=True, right=True)
    ax.legend(ncol=2, loc="upper right")
    ax2 = fig.add_axes([0.73, 0.17, 0.25, 0.75])
    labs = sorted(c["by_label"], key=lambda k: -c["by_label"][k])
    ax2.barh(np.arange(len(labs)), [c["by_label"][k] for k in labs], color=fs.PAL["blue"], height=0.6)
    ax2.set_yticks(np.arange(len(labs)))
    ax2.set_yticklabels(labs)
    ax2.invert_yaxis()
    ax2.set_xlabel("claims by label")
    ax2.set_xscale("log")
    fs.save(fig, out)
    plt.close(fig)


def fig_eqcount(rep, out):
    rows = [r for r in rep["C8"]["rows"] if "diff" in r]
    ind = np.array([r["independent_numbered"] for r in rows], float)
    db = np.array([r["db_numbered"] for r in rows], float)
    raw = np.array([r["input"] == "raw main file" for r in rows])
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.6))
    ax = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    lo, hi = 0.8, max(ind.max(), db.max()) * 1.5
    ax.plot([lo, hi], [lo, hi], ls="--", color="k", lw=1.0, label="equality")
    ax.scatter(ind[raw] + 1, db[raw] + 1, s=18, color=fs.PAL["red"], label="raw main file", zorder=3)
    ax.scatter(ind[~raw] + 1, db[~raw] + 1, s=18, facecolor="none", edgecolor=fs.PAL["red"],
               label="flat.tex (multi-file)", zorder=3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("independent count + 1")
    ax.set_ylabel("database rows with a number + 1")
    ax.legend(loc="upper left")
    ax2 = fig.add_axes([0.57, 0.15, 0.41, 0.78])
    d = db - ind
    order = np.argsort(d)
    ax2.bar(np.arange(len(d)), d[order], color=[fs.PAL["red"] if v else "0.7" for v in d[order]], width=0.8)
    ax2.axhline(0, color="k", lw=1.0)
    ax2.set_xlabel("sampled papers (sorted)")
    ax2.set_ylabel("database - independent")
    ax2.set_title(f"{int((d == 0).sum())} of {len(d)} agree exactly", fontsize=10)
    fs.save(fig, out)
    plt.close(fig)


def fig_retrieval(rep, out):
    c = rep["C7"]
    modes = list(c["modes"])
    q = [r["id"] for r in c["modes"][modes[0]]["rows"]]
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fig.add_axes([0.08, 0.17, 0.9, 0.73])
    x = np.arange(len(q))
    miss = c["k"] + 1.5
    colors = {"text": fs.PAL["blue"], "hybrid": fs.PAL["red"]}
    off = {m: (i - (len(modes) - 1) / 2) * 0.3 for i, m in enumerate(modes)}
    for m in modes:
        rows = c["modes"][m]["rows"]
        pr = np.array([r["paper_rank"] or miss for r in rows], float)
        lr = np.array([r["locator_rank"] or miss for r in rows], float)
        ax.scatter(x + off[m], pr, marker="o", s=22, color=colors.get(m, "k"),
                   label=f"{m}: paper ({c['modes'][m]['paper_hits']}/{len(q)})")
        ax.scatter(x + off[m], lr, marker="x", s=22, color=colors.get(m, "k"),
                   label=f"{m}: locator ({c['modes'][m]['locator_hits']}/{len(q)})")
    ax.axhline(c["k"] + 0.5, color="k", ls="--", lw=1.0)
    ax.text(len(q) - 0.5, c["k"] + 0.9, "not in the top 10", ha="right", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(q, rotation=90, fontsize=7)
    ax.set_ylabel("rank of first hit")
    ax.set_ylim(miss + 1, 0)
    ax.minorticks_off()
    ax.legend(ncol=2, loc="lower left", fontsize=8)
    fs.save(fig, out)
    plt.close(fig)


def main(argv=None):
    argv = argv or sys.argv[1:]
    rep = json.load(open(argv[0]))
    d = argv[1]
    os.makedirs(d, exist_ok=True)
    fig_claims(rep, os.path.join(d, "fig_qa_claims"))
    fig_eqcount(rep, os.path.join(d, "fig_qa_eqcount"))
    fig_retrieval(rep, os.path.join(d, "fig_qa_retrieval"))
    print(f"figures -> {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
