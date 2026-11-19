"""Figure of test P: knowledge base against my own TeX count for the twenty sampled papers.

Usage: python3 fig_papers.py <outdir>   (reads <outdir>/papers.json, writes fig_papers.{pdf,png})
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    d = json.load(open(os.path.join(out, "papers.json")))
    P = d["papers"]
    fs.use_style()

    def my_bib(r):
        b = r["mine"]["bib"]
        if r["kb_bib_source"]:
            return b.get(r["kb_bib_source"], 0)
        return max([b.get(k, 0) for k in ("bbl", "bib", "thebibliography",
                                            "aastex_references", "plain_ref_items")])

    panels = [
        ("display-equation records", [r["mine"]["n_rec_rule"] for r in P], [r["kb"]["n_eq"] for r in P],
         [r["mine"]["n_eq"] for r in P]),
        ("numbered equations", [r["mine"]["n_numbered"] for r in P], [r["kb"]["n_numbered"] for r in P], None),
        ("sections (levels 1-3)", [sum(r["mine"]["n_sec_by_level"].values()) for r in P],
         [sum(r["kb"]["n_sec_by_level"].values()) for r in P], None),
        ("bibliography entries", [my_bib(r) for r in P], [r["kb"]["n_bib"] for r in P], None),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 7.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.95, wspace=0.28, hspace=0.32)
    for ax, (title, mine, kb, envs) in zip(axes.flat, panels):
        mine = np.asarray(mine, float)
        kb = np.asarray(kb, float)
        lo, hi = 0.7, max(mine.max(), kb.max()) * 1.6
        ax.plot([lo, hi], [lo, hi], **fs.GUIDE, label="equal")
        x = np.clip(mine, lo * 1.05, None)
        y = np.clip(kb, lo * 1.05, None)
        agree = np.isclose(mine, kb)
        ax.scatter(x[agree], y[agree], s=22, color=fs.PAL["blue"], zorder=3, label="agree")
        ax.scatter(x[~agree], y[~agree], s=30, marker="s", color=fs.PAL["red"], zorder=4,
                   label="differ")
        if envs is not None:
            ax.scatter(np.clip(np.asarray(envs, float), lo * 1.05, None), y, s=12, marker="x",
                       color="grey", alpha=0.6, zorder=2, label="my environment count")
        k = 0
        for xi, yi, r, a in zip(x, y, P, agree):
            if not a:
                ax.annotate(r["paper_id"], (xi, yi), xytext=(-20, 8 + 11 * k),
                            textcoords="offset points", fontsize=7)
                k += 1
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_title(title)
        ax.set_xlabel("my count from the TeX source")
        ax.set_ylabel("knowledge base")
        n_ag = int(agree.sum())
        ax.text(0.04, 0.92, f"{n_ag}/{len(P)} equal", transform=ax.transAxes)
        ax.text(0.04, 0.84, "zeros drawn at the lower edge", transform=ax.transAxes, fontsize=7,
                color="grey")
        ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_papers"))


if __name__ == "__main__":
    main()
