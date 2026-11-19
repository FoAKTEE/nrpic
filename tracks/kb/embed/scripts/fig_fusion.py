"""Figure of test E7: questions answered in the top 10 for each fusion variant (k of the
reciprocal rank, weight w of the vector ranking; w = 0 is text alone), on the K9 golden set
(left, used to choose) and on questions10 (right, held out). The chosen cell is outlined.

    kb/.venv/bin/python -I tracks/kb/embed/scripts/fig_fusion.py FUSION_JSON OUT_STEM
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                       # noqa: E402
import matplotlib                        # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
import figstyle as fs                    # noqa: E402


def main(path, stem):
    d = json.load(open(path))
    ks, ws = d["k_grid"], d["w_grid"]
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    for j, (name, title, n) in enumerate((("k9", "K9 golden set (choice)", 32), ("ten", "questions10 (held out)", 10))):
        ax = fig.add_axes([0.08 + j * 0.47, 0.17, 0.36, 0.70])
        g = np.array([[d["grid"][name][f"k={k} w={w}"]["hit@10"] for w in ws] for k in ks], dtype=float)
        base = d["grid"][name]["k=60 w=0.0"]["hit@10"]
        im = ax.imshow(g - base, cmap="RdBu_r", vmin=-3, vmax=3, aspect="auto", origin="lower")
        for a in range(len(ks)):
            for b in range(len(ws)):
                ax.text(b, a, f"{int(g[a, b])}", ha="center", va="center", fontsize=8)
        kb, wb = d["chosen_on_k9"].split()
        a = ks.index(int(kb[2:]))
        b = ws.index(float(wb[2:]))
        ax.add_patch(Rectangle((b - 0.5, a - 0.5), 1, 1, fill=False, lw=1.5, ec="k"))
        ax.set_xticks(range(len(ws)))
        ax.set_xticklabels([f"{w:g}" for w in ws])
        ax.set_yticks(range(len(ks)))
        ax.set_yticklabels([str(k) for k in ks])
        ax.minorticks_off()
        ax.set_xlabel("weight of the vector ranking $w$ (0 = text only)")
        ax.set_ylabel("$k$ of the reciprocal rank")
        ax.set_title(f"{title}: hits in top 10 of {n}", fontsize=9)
        if j == 1:
            cax = fig.add_axes([0.92, 0.17, 0.015, 0.70])
            cb = fig.colorbar(im, cax=cax)
            cb.set_label("hits minus text only")
    fs.save(fig, stem)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
