"""Figure of the kb lead's wave-2 review (tracks/kb/stage/REVIEW-wave2.md).

Left: the serve helper's number verdicts against the lead's own matcher (run
kb-20261115-181544-94f68f2, rows.tsv), 330 statements. Middle: numbered display lines of the
single-file papers of the K9 sample, lead counter against the database (run
kb-20261115-181916-08ebad9, eqcount.tsv); open symbols are papers whose shorthand macros the lead
counter does not expand. Right: hits in the top 10 per retrieval mode, helper against the lead's
rescoring of the same ranked lists (run kb-20261115-182238-b86d2b5, rescoring.json).
Inputs are run outputs under scratch/kb/ (absolute paths); output note/figures/fig_w2_review.*.
"""
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/kb"
ROWS = f"{S}/kb-20261115-181544-94f68f2/rows.tsv"
EQ = f"{S}/kb-20261115-181916-08ebad9/eqcount.tsv"
RES = f"{S}/kb-20261115-182238-b86d2b5/rescoring.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "fig_w2_review")

classes = ["exact", "near", "missing", "none"]
M = np.zeros((4, 4), int)
with open(ROWS) as f:
    for r in csv.DictReader(f, delimiter="\t"):
        M[classes.index(r["helper"]), classes.index(r["lead"])] += 1

eq = list(csv.DictReader(open(EQ), delimiter="\t"))
res = json.load(open(RES))

fig = plt.figure(figsize=(8.0, 2.9))
fig.subplots_adjust(left=0.115, right=0.985, bottom=0.22, top=0.86, wspace=0.6)
ax1, ax2, ax3 = fig.add_subplot(131), fig.add_subplot(132), fig.add_subplot(133)

im = ax1.imshow(np.log10(M + 1), cmap="Blues", vmin=0, vmax=np.log10(M.max() + 1))
for i in range(4):
    for j in range(4):
        if M[i, j]:
            ax1.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=8,
                     color="white" if M[i, j] > 40 else "black")
ax1.set_xticks(range(4), classes, rotation=30)
ax1.set_yticks(range(4), classes)
ax1.set_xlabel("lead matcher", labelpad=1)
ax1.set_ylabel("serve helper")
ax1.minorticks_off()
ax1.set_title("numbers at the locator", fontsize=10)

lead = np.array([int(r["lead"]) for r in eq])
dbn = np.array([int(r["database"]) for r in eq])
short = np.array([(r["helper_shorthands"] or "0") != "0" for r in eq])
m = np.array([1, 400])
ax2.plot(m, m, **fs.GUIDE, label="equality")
ax2.scatter(dbn[~short] + 1, lead[~short] + 1, s=14, color=fs.PAL["red"], label="no shorthand", zorder=3)
ax2.scatter(dbn[short] + 1, lead[short] + 1, s=18, facecolors="none", edgecolors=fs.PAL["blue"],
            label="shorthand macros", zorder=3)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlim(0.8, 400)
ax2.set_ylim(0.8, 400)
ax2.set_xlabel("database lines + 1", labelpad=1)
ax2.set_ylabel("lead counter + 1")
ax2.legend(loc="upper left", fontsize=7, frameon=False)
ax2.set_title(f"numbered lines, {len(eq)} papers", fontsize=10)

labels, hv, lv = [], [], []
for st in ("ten", "k9"):
    for mode in ("text", "vector", "hybrid"):
        labels.append({"text": "txt", "vector": "vec", "hybrid": "hyb"}[mode])
        hv.append(res[st]["helper_hits@10"][mode])
        lv.append(res[st]["lead_hits@10"][mode])
x = np.arange(len(labels))
ax3.bar(x - 0.2, hv, 0.4, color=fs.PAL["blue"], label="helper")
ax3.bar(x + 0.2, lv, 0.4, color=fs.PAL["red"], label="lead rescoring")
ax3.set_xticks(x, labels, fontsize=8)
ax3.text(1, -0.21, "10 questions", transform=ax3.get_xaxis_transform(), ha="center", fontsize=8)
ax3.text(4, -0.21, "32 questions", transform=ax3.get_xaxis_transform(), ha="center", fontsize=8)
ax3.minorticks_off()
ax3.set_ylabel("hits in the top 10")
ax3.set_ylim(0, 27)
ax3.legend(loc="upper left", fontsize=7, frameon=False)
ax3.set_title("retrieval, two sets", fontsize=10)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
fs.save(fig, OUT)
print(OUT)
