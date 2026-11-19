"""Figure of tests E1-E2: word pieces per chunk kind against the model's limit of 512 (left),
and the cosine scores of the E1 ordering check (right).

    kb/.venv/bin/python -I tracks/kb/embed/scripts/fig_bench.py BENCH_JSON OUT_STEM
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


def main(path, stem):
    r = json.load(open(path))
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.55, 0.78])
    bins = np.logspace(np.log10(5), np.log10(4000), 50)
    for k, (kind, c) in enumerate(zip(("body", "appendix", "abstract", "caption", "footnote"), fs.SERIES)):
        d = r["tokens"][kind]
        ax.hist(d["counts"], bins=bins, histtype="step", color=c, lw=1.5,
                label=f"{kind} ({100 * d['truncated_fraction']:.0f}% > 512)")
    ax.axvline(512, **fs.GUIDE)
    ax.set_xscale("log")
    ax.set_xlabel("word pieces per chunk (sample of %d per kind)" % r["tokens"]["body"]["n"])
    ax.set_ylabel("chunks")
    ax.legend(loc="upper left", fontsize=8)
    ax2 = fig.add_axes([0.72, 0.15, 0.26, 0.78])
    names = list(r["e1_scores"])
    vals = [r["e1_scores"][n] for n in names]
    ax2.bar(range(len(names)), vals, color=[fs.PAL["red"] if n == "cic" else "grey" for n in names])
    ax2.set_xticks(range(len(names)))
    ax2.set_xticklabels(["deposition\n(target)", "gauge", "CMB"][:len(names)])
    ax2.set_ylabel("cosine to the deposition query")
    ax2.set_ylim(0.4, 0.75)
    ax2.minorticks_off()
    ax2.set_title(f"{r['timing']['chunks_per_s']:.0f} body chunks/s, {r['threads']} threads", fontsize=9)
    fs.save(fig, stem)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
