"""Figure of the KB-G2 thresholds (decision 0016 item 6) on snapshot kb-20261119-a782f1e.

(a) Parse success of the 710 ingested papers under three readings: status ok only; ok or pdf;
    ok minus the 11 papers with status ok and no bibliography entry (KB-G1 verifier, lead's
    recount run kb-20261119-155315-b2c7420). The dashed line is the 95 per cent bar.
(b) Golden questions (32) with the right paper in the top ten, and with the answer location in
    the top ten (reported, not gating), per retrieval mode; dashed line the 80 per cent bar.
(c) Rank of the first chunk at the answer location per question, hybrid against rerank.
Input: qa.json of run kb-20261119-161633-1d05960 (Q1). Output: note/figures/fig_kbg2.{png,pdf}.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/kb"
Q = json.load(open(f"{S}/kb-20261119-161633-1d05960/qa.json"))
V = json.load(open(f"{S}/kb-20261119-155315-b2c7420/verifier_check.json"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "fig_kbg2")
cols = fs.series_colors(4)

n = Q["C1"]["papers_total"]
st = Q["C3"]["by_status"]
n_ok = n - Q["C3"]["not_ok"]
n_pdf = st.get("pdf", 0)
n_lost = len(V["zero_bib_ok"])
readings = [("status ok", n_ok), ("ok or pdf", n_ok + n_pdf), ("ok minus lost\nbibliographies", n_ok - n_lost),
            ("ok or pdf minus\nlost bibliographies", n_ok + n_pdf - n_lost)]
fig, axs = plt.subplots(1, 3, figsize=(14, 3.8), gridspec_kw={"width_ratios": [1.2, 1.0, 1.6]})
for i, (lab, k) in enumerate(readings):
    r = 100.0 * k / n
    axs[0].bar(i, r, color=cols[0] if r >= 95 else cols[1], width=0.6)
    axs[0].text(i, r + 0.15, f"{k}/{n}\n{r:.1f}%", ha="center", va="bottom", fontsize=8)
axs[0].axhline(95, color="0.4", ls="--", lw=1)
axs[0].set_ylim(90, 100)
axs[0].set_xticks(range(len(readings)))
axs[0].set_xticklabels([r[0] for r in readings], fontsize=7)
axs[0].set_ylabel("parse success (%)")
axs[0].set_title("(a) parse success, 95 % bar", fontsize=10)

modes = ["text", "hybrid", "rerank"]
rows = {m: Q["C7"]["modes"][m]["rows"] for m in modes}
nq = len(rows["text"])
x = np.arange(len(modes))
pap = [100.0 * sum(1 for r in rows[m] if r["paper_rank"]) / nq for m in modes]
loc = [100.0 * sum(1 for r in rows[m] if r["locator_rank"]) / nq for m in modes]
axs[1].bar(x - 0.18, pap, width=0.34, color=cols[0], label="paper in top 10 (gating)")
axs[1].bar(x + 0.18, loc, width=0.34, color=cols[2], label="answer location (reported)")
for i in range(len(modes)):
    axs[1].text(x[i] - 0.18, pap[i] + 1, f"{pap[i]:.1f}", ha="center", fontsize=8)
    axs[1].text(x[i] + 0.18, loc[i] + 1, f"{loc[i]:.1f}", ha="center", fontsize=8)
axs[1].axhline(80, color="0.4", ls="--", lw=1)
axs[1].set_xticks(x)
axs[1].set_xticklabels(modes)
axs[1].set_ylim(0, 115)
axs[1].set_ylabel(f"golden questions hit (% of {nq})")
axs[1].set_title("(b) retrieval, 80 % bar", fontsize=10)
axs[1].legend(fontsize=7, loc="upper left", frameon=False)

ids = [r["id"] for r in rows["hybrid"]]
miss = 13
for m, c, mk, off in (("hybrid", cols[1], "D", -0.15), ("rerank", cols[0], "P", 0.15)):
    y = [r["locator_rank"] or miss for r in rows[m]]
    axs[2].scatter(np.arange(nq) + off, y, color=c, marker=mk, s=22, label=m)
axs[2].axhline(10.5, color="0.4", ls="--", lw=1)
axs[2].set_yscale("log")
axs[2].set_yticks([1, 2, 5, 10, miss])
axs[2].set_yticklabels(["1", "2", "5", "10", "miss"])
axs[2].invert_yaxis()
axs[2].set_xticks(np.arange(nq))
axs[2].set_xticklabels(ids, rotation=90, fontsize=6)
axs[2].set_ylabel("rank at the answer location")
axs[2].set_title("(c) per question (snapshot a782f1e)", fontsize=10)
axs[2].legend(fontsize=7, loc="lower left")
fig.tight_layout()
fig.savefig(OUT + ".png", dpi=150)
fig.savefig(OUT + ".pdf")
print(json.dumps({"readings": readings, "paper_pct": pap, "loc_pct": loc}))
