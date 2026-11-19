"""Figure of check C4 (R1, R2b, R5): for the 30 papers drawn at random, title similarity and the
fraction of INSPIRE surnames found in the TeX author list; the bars of qa_report (0.9, 0.8)
dashed; papers below a bar named.

    kb/.venv/bin/python -I tracks/kb/retrieval/scripts/fig_c4.py QA_JSON OUT_STEM
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import figstyle as fs                    # noqa: E402


def main(path, stem):
    c = json.load(open(path))["C4"]
    rows = [r for r in c["rows"] if r.get("metadata")]
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.4))
    ax = fig.add_axes([0.16, 0.14, 0.80, 0.72])
    for r in rows:
        x = r["title_ratio"] if r["title_ratio"] is not None else -0.05
        y = r["author_fraction"] if r["author_fraction"] is not None else -0.05
        bad = r["paper_id"] in c.get("differ", [])
        ax.scatter([x], [y], s=26 if bad else 16, color=fs.PAL["red"] if bad else fs.PAL["blue"], zorder=3,
                   alpha=1.0 if bad else 0.6)
        if bad:
            right = x > 0.5
            ax.annotate(r["paper_id"], (x, y), xytext=(-6 if right else 6, -12 if right else 4),
                        textcoords="offset points", fontsize=7, ha="right" if right else "left")
    ax.axvline(c.get("title_min", 0.9), **fs.GUIDE)
    ax.axhline(c.get("authors_min", 0.8), **fs.GUIDE)
    ax.set_xlim(-0.1, 1.08)
    ax.set_ylim(-0.1, 1.08)
    ax.set_xlabel("title similarity (TeX vs INSPIRE)")
    ax.set_ylabel("INSPIRE surnames found in TeX authors")
    ax.set_title(f"C4: {c['with_metadata']} of {len(c['sample'])} with a record; "
                 f"{len(c.get('differ', []))} below a bar", fontsize=8)
    fs.save(fig, stem)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
