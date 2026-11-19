"""Figure of test R4: answer-location rank of every question under the first stage (text,
hybrid) and the window re-ranking variants, for the 32 golden questions (design set) and the
ten held-out questions (left, centre); hits in the top 10 per mode (right).

    kb/.venv/bin/python -I tracks/kb/retrieval/scripts/fig_rerank.py RESULTS_JSON OUT_STEM [--chosen w2]
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

MISS = 14
MARK = ["o", "D", "s", "^", "v", "P", "X"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("stem")
    ap.add_argument("--chosen", default="w2")
    a = ap.parse_args()
    r = json.load(open(a.results))
    modes = list(r["summary"]["golden32"])
    colors = dict(zip(modes, [fs.PAL["blue"], fs.PAL["red"]] + fs.series_colors(max(1, len(modes) - 2))))
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.7))
    axes = [fig.add_axes([0.07, 0.15, 0.50, 0.72]), fig.add_axes([0.60, 0.15, 0.17, 0.72])]
    for ax, st in zip(axes, ("golden32", "ten")):
        qs = [q for q in r["questions"] if q["set"] == st]
        x = np.arange(len(qs))
        show = ["hybrid", a.chosen] if st == "golden32" else modes
        for k, m in enumerate(show):
            y = [q["modes"][m]["locator_rank"] or MISS for q in qs]
            off = (k - (len(show) - 1) / 2) * (0.30 if st == "golden32" else 0.12)
            ax.scatter(x + off, y, color=colors[m], marker=MARK[modes.index(m) % len(MARK)], s=18, zorder=3,
                       label=m if st == "golden32" else None)
        ax.axhline(10.5, **fs.GUIDE)
        ax.axhspan(11.5, 16, color="grey", alpha=0.15, lw=0)
        ax.set_ylim(0.5, 15)
        ax.invert_yaxis()
        ax.set_xlim(-0.7, len(qs) - 0.3)
        ax.set_xticks(x)
        ax.set_xticklabels([q["id"] for q in qs], rotation=90, fontsize=6)
        ax.set_yticks([1, 2, 5, 10, MISS])
        ax.set_yticklabels(["1", "2", "5", "10", "miss"] if st == "golden32" else [])
        ax.minorticks_off()
        ax.set_title(f"{'32 golden questions (design set), slack 5 lines' if st == 'golden32' else 'ten held out, no slack'}",
                     fontsize=8)
    axes[0].set_ylabel("rank of the first chunk at the answer location")
    axes[0].legend(loc="lower left", bbox_to_anchor=(0.0, 1.07), ncol=2, fontsize=7)
    ax = fig.add_axes([0.83, 0.15, 0.15, 0.72])
    y = np.arange(len(modes))
    for st, dy, alpha in (("golden32", -0.18, 1.0), ("ten", 0.18, 0.45)):
        n = r["summary"][st][modes[0]]["n"]
        v = [r["summary"][st][m]["locator_hits"] / n for m in modes]
        ax.barh(y + dy, v, height=0.34, color=[colors[m] for m in modes], alpha=alpha,
                label=f"{st} ({n})")
    ax.axvline(0.8, **fs.MASK_LINE)
    ax.set_yticks(y)
    ax.set_yticklabels(modes, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("locator hits, top 10")
    ax.legend(loc="lower left", bbox_to_anchor=(-0.2, 1.0), fontsize=6, ncol=1)
    fs.save(fig, a.stem)


if __name__ == "__main__":
    main()
