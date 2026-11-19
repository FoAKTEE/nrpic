"""Figure of test R4: answer-location rank of every question under the first stage (hybrid)
and the chosen window re-ranking variant, for the 32 golden questions (design set, left) and
the ten held-out questions (centre); right: fraction of the 32 golden questions with the right
paper (open bars) and with the answer location (filled bars) in the top 10, for every mode.

    kb/.venv/bin/python -I tracks/kb/retrieval/scripts/fig_rerank.py RESULTS_JSON OUT_STEM [--chosen w2-noexpand]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                       # noqa: E402
import matplotlib                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import figstyle as fs                    # noqa: E402

MISS = 22
COL = {"text": "#7f7f7f", "hybrid": fs.PAL["red"], "w2": fs.PAL["blue"], "w3": fs.PAL["orange"],
       "w2+stage1": fs.PAL["yellow"], "w2-noexpand": fs.PAL["green"]}
MRK = {"hybrid": "D", "w2-noexpand": "P"}


def strip(ax, qs, modes, title, show_y):
    x = np.arange(len(qs))
    for k, m in enumerate(modes):
        y = [q["modes"][m]["locator_rank"] or MISS for q in qs]
        ax.scatter(x + (k - 0.5) * 0.32, y, color=COL.get(m, "k"), marker=MRK.get(m, "o"), s=20, zorder=3, label=m)
    ax.axhline(10.5, **fs.GUIDE)
    ax.axhspan(14, 40, color="grey", alpha=0.15, lw=0)
    ax.set_yscale("log")
    ax.set_ylim(30, 0.75)
    ax.set_xlim(-0.7, len(qs) - 0.3)
    ax.set_xticks(x)
    ax.set_xticklabels([q["id"] for q in qs], rotation=90, fontsize=6)
    ax.set_yticks([1, 2, 5, 10, MISS])
    ax.set_yticklabels(["1", "2", "5", "10", "miss"] if show_y else [])
    ax.minorticks_off()
    ax.set_title(title, fontsize=8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("stem")
    ap.add_argument("--chosen", default="w2-noexpand")
    a = ap.parse_args()
    r = json.load(open(a.results))
    S = r["summary"]
    modes = list(S["golden32"])
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.8))
    ax1 = fig.add_axes([0.075, 0.16, 0.47, 0.70])
    ax2 = fig.add_axes([0.565, 0.16, 0.16, 0.70])
    show = ["hybrid", a.chosen]
    g = [q for q in r["questions"] if q["set"] == "golden32"]
    t = [q for q in r["questions"] if q["set"] == "ten"]
    strip(ax1, g, show, "32 golden questions (design set), slack 5 lines\nanswer location in the top 10: " +
          ", ".join(f"{m} {S['golden32'][m]['locator_hits']}" for m in show), True)
    strip(ax2, t, show, "ten held out, no slack\n" + ", ".join(f"{S['ten'][m]['locator_hits']}" for m in show),
          False)
    ax1.set_ylabel("rank of the first chunk at the answer location")
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.09), ncol=2, fontsize=7)
    ax3 = fig.add_axes([0.85, 0.16, 0.14, 0.70])
    y = np.arange(len(modes))
    n = S["golden32"][modes[0]]["n"]
    ax3.barh(y, [S["golden32"][m]["paper_hits"] / n for m in modes], height=0.7, color="none",
             edgecolor=[COL.get(m, "k") for m in modes], lw=1.2, label="paper")
    ax3.barh(y, [S["golden32"][m]["locator_hits"] / n for m in modes], height=0.45,
             color=[COL.get(m, "k") for m in modes], label="answer location")
    ax3.axvline(0.8, **fs.MASK_LINE, label="KB-G2 (paper)")
    ax3.set_yticks(y)
    ax3.set_yticklabels(modes, fontsize=7)
    ax3.set_ylim(len(modes) - 0.5, -0.6)
    ax3.set_xlim(0.5, 1.0)
    ax3.set_xticks([0.5, 0.75, 1.0])
    ax3.set_xticklabels(["0.5", "0.75", "1"])
    ax3.set_xlabel("golden questions\nhit in the top 10", fontsize=8)
    ax3.legend(loc="lower left", bbox_to_anchor=(-0.95, 1.0), fontsize=6, ncol=1)
    fs.save(fig, a.stem)


if __name__ == "__main__":
    main()
