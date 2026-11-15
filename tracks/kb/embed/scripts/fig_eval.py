"""Figure of test E4: rank of the first correct chunk for each of the ten questions under text
(BM25), vector and hybrid search (left; above the top band = not in the first 100), and the
fraction of questions answered within the top k (right).

    kb/.venv/bin/python -I tracks/kb/embed/scripts/fig_eval.py RESULTS_JSON OUT_STEM
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                       # noqa: E402
import matplotlib                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import figstyle as fs                    # noqa: E402

STYLE = {"text": (fs.PAL["blue"], "o", "text (BM25)"), "vector": (fs.PAL["yellow"], "s", "vector"),
         "hybrid": (fs.PAL["red"], "D", "hybrid (RRF)")}
MISS = 160


def main(path, stem):
    r = json.load(open(path))
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
    ax = fig.add_axes([0.08, 0.14, 0.52, 0.80])
    qs = r["questions"]
    x = np.arange(len(qs))
    for k, (mode, (c, m, lab)) in enumerate(STYLE.items()):
        y = [q["modes"][mode]["first_hit"] or MISS for q in qs]
        ax.scatter(x + (k - 1) * 0.22, y, color=c, marker=m, s=28, label=lab, zorder=3)
    ax.axhline(10.5, **fs.GUIDE)
    ax.axhspan(110, 250, color="grey", alpha=0.15, lw=0)
    ax.text(len(qs) - 0.6, MISS, "not in top 100", ha="right", va="center", fontsize=8)
    ax.set_yscale("log")
    ax.set_ylim(0.7, 250)
    ax.set_xlim(-0.6, len(qs) - 0.4)
    ax.set_xticks(x)
    ax.set_xticklabels([q["id"] for q in qs], rotation=0, fontsize=8)
    ax.minorticks_off()
    ax.set_yticks([1, 2, 5, 10, 20, 50, 100])
    ax.set_yticklabels(["1", "2", "5", "10", "20", "50", "100"])
    ax.set_ylabel("rank of the first correct chunk")
    ax.legend(loc="upper left", ncol=3, fontsize=8)
    ax2 = fig.add_axes([0.70, 0.14, 0.28, 0.80])
    ks = np.arange(1, 21)
    for mode, (c, m, lab) in STYLE.items():
        ranks = [q["modes"][mode]["first_hit"] for q in qs]
        ax2.plot(ks, [sum(1 for v in ranks if v and v <= kk) / len(ranks) for kk in ks], color=c, label=lab,
                 drawstyle="steps-post")
    ax2.axvline(10, **fs.MASK_LINE)
    ax2.set_xlabel("k")
    ax2.set_ylabel("questions answered in the top k")
    ax2.set_ylim(0, 1.05)
    ax2.set_xlim(1, 20)
    ax2.set_title(f"{r['chunk_vectors']} chunk vectors, whole corpus", fontsize=9)
    fs.save(fig, stem)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
