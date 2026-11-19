"""Figure of the kb lead's wave-2b review (tracks/kb/stage/REVIEW-wave2.md, section wave 2b).

(a) Hits in the top 10 on the 32 golden questions per retrieval mode: the retrieval helper's
    counts against the lead's own rescoring of the same ranked lists (run
    kb-20261119-155310-e600e38, retrieval_check.json); filled bars answer location, open bars paper.
(b) The lead's reading of PDF-reader repairs (run kb-20261119-155134-17d6704; verdicts in
    analysis/lead_checks/w2b_repair_verdicts.tsv): word repairs and the 'cmmi-greek' mapping.
(c) TeX papers with no bibliography entry in snapshot kb-20261115-a848a06 by the cause the lead's
    patterns find (run kb-20261119-155315-b2c7420, verifier_check.json), parse status ok or review.
(d) Parameter-index rows of this repository before (a1c2237, snapshot a848a06) and after the
    re-index at main (snapshot kb-20261119-a782f1e, run kb-20261119-161451-e15d1b8), and the
    literal (block, name) pairs of four files absent from the index before and after.
Output: note/figures/fig_w2b_review.{png,pdf}.
"""
import csv
import json
import os
import re
import sqlite3
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/kb"
HOME = "/data/haiyangw/nrpic"
HERE = os.path.dirname(os.path.abspath(__file__))
RET = f"{S}/kb-20261119-155310-e600e38/retrieval_check.json"
VER = f"{S}/kb-20261119-155315-b2c7420/verifier_check.json"
VERD = os.path.join(HERE, "..", "..", "analysis", "lead_checks", "w2b_repair_verdicts.tsv")
NEW = f"{HOME}/kb-data/db/kb-20261119-a782f1e.sqlite"
OLD = f"{HOME}/kb-data/db/kb-20261115-a848a06.sqlite"
OUT = os.path.join(HERE, "..", "figures", "fig_w2b_review")

fig, axs = plt.subplots(1, 4, figsize=(15.5, 3.6), gridspec_kw={"width_ratios": [1.5, 0.8, 1.3, 1.2]})
cols = fs.series_colors(4)

# (a)
R = json.load(open(RET))["rescoring"]
modes = ["text", "hybrid", "w2", "w3", "w2+stage1", "w2-noexpand"]
x = np.arange(len(modes))
for off, who, c in ((-0.18, "helper", cols[0]), (0.18, "lead", cols[1])):
    loc = [R[f"golden32/{m}"][who]["loc"] for m in modes]
    pap = [R[f"golden32/{m}"][who]["paper"] for m in modes]
    axs[0].bar(x + off, loc, width=0.34, color=c, label=f"{who}: answer location")
    axs[0].bar(x + off, pap, width=0.34, fill=False, edgecolor=c, lw=1.2, label=f"{who}: paper")
axs[0].axhline(0.8 * 32, color="0.5", ls="--", lw=1)
axs[0].text(-0.45, 0.8 * 32 + 0.3, "KB-G2 bar (paper)", ha="left", va="bottom", fontsize=7, color="0.4")
axs[0].set_xticks(x)
axs[0].set_xticklabels(modes, rotation=30, ha="right")
axs[0].set_ylim(0, 40)
axs[0].set_ylabel("golden questions hit (of 32)")
axs[0].set_title("(a) retrieval rescored", fontsize=10)
axs[0].legend(fontsize=7, loc="upper left", ncol=2, frameon=False)

# (b)
rows = [r for r in csv.reader((l for l in open(VERD) if not l.startswith("#")), delimiter="\t")][1:]
for i, pool in enumerate(("word", "greek")):
    ok = sum(1 for r in rows if r[1] == pool and r[2] == "right")
    bad = sum(1 for r in rows if r[1] == pool and r[2] == "wrong")
    axs[1].bar(i, ok, color=cols[0], width=0.6, label="right" if i == 1 else None)
    axs[1].bar(i, bad, bottom=ok, color=cols[1], width=0.6, label="wrong" if i == 1 else None)
    axs[1].text(i, ok + bad + 0.3, f"{ok}/{ok + bad}", ha="center", fontsize=9)
axs[1].set_xticks([0, 1])
axs[1].set_xticklabels(["word\nrepairs", "cmmi\nGreek"])
axs[1].set_ylim(0, 27)
axs[1].set_ylabel("repairs read by the lead")
axs[1].set_title("(b) PDF reader", fontsize=10)
axs[1].legend(fontsize=7, loc="upper left", ncol=2, frameon=False)

# (c)
V = json.load(open(VER))


def cause(l):
    if l.get("harvarditem"):
        return "\\harvarditem (.bbl)"
    if l.get("reference"):
        return "AASTeX \\reference"
    if l.get("bi_macro"):
        return "macro for \\bibitem"
    if l.get("begin_references"):
        return "references env."
    if l.get("plain_ref"):
        return "plain TeX \\ref"
    if l.get("bibitem"):
        return "\\bibitem not reached"
    return "no list found"


cats = ["references env.", "AASTeX \\reference", "macro for \\bibitem", "\\harvarditem (.bbl)",
        "plain TeX \\ref", "\\bibitem not reached", "no list found"]
okc = {k: 0 for k in cats}
revc = {k: 0 for k in cats}
for z in V["zero_bib_verifier_list"]:
    (okc if z["status"] == "ok" else revc)[cause(z["lead"])] += 1
y = np.arange(len(cats))
axs[2].barh(y, [okc[k] for k in cats], color=cols[1], label="status ok")
axs[2].barh(y, [revc[k] for k in cats], left=[okc[k] for k in cats], color="0.7", label="status review")
axs[2].set_yticks(y)
axs[2].set_yticklabels(cats, fontsize=8)
axs[2].invert_yaxis()
axs[2].set_xlabel("TeX papers with no bibliography entry")
axs[2].set_title(f"(c) {len(V['zero_bib_verifier_list'])} of {V['tex_papers']} TeX papers", fontsize=10)
axs[2].legend(fontsize=7, loc="lower right")

# (d)
files = ["athenak/src/particles/nrpic_collide.cpp", "athenak/src/scalar_field/scalar_field.cpp",
         "athenak/src/particles/nrpic_kick.cpp", "athenak/src/pgen/nrpic/nrpic_cf.cpp"]
new = sqlite3.connect(f"file:{NEW}?mode=ro", uri=True)
old = sqlite3.connect(f"file:{OLD}?mode=ro", uri=True)
rev = new.execute("SELECT commit_sha FROM repos WHERE repo_id='local/nrpic'").fetchone()[0]
before, after = [], []
for fpath in files:
    txt = subprocess.run(["git", "-C", HOME, "show", f"{rev}:{fpath}"], capture_output=True, text=True).stdout
    pairs = set(re.findall(r'->Get\w*\(\s*"([^"]+)"\s*,\s*"([^"]+)"', txt))
    for con, lst in ((old, before), (new, after)):
        have = set(con.execute("SELECT block, name FROM params WHERE repo_id='local/nrpic'").fetchall())
        lst.append(len(pairs - have))
xx = np.arange(len(files))
axs[3].bar(xx - 0.18, before, width=0.34, color=cols[1], label="index at a1c2237")
axs[3].bar(xx + 0.18, after, width=0.34, color=cols[0], label=f"index at {rev[:7]}")
for i, v in enumerate(after):
    axs[3].text(xx[i] + 0.18, v + 0.2, str(v), ha="center", fontsize=8, color=cols[0])
axs[3].set_xticks(xx)
axs[3].set_xticklabels([os.path.basename(f).replace(".cpp", "") for f in files], rotation=30, ha="right")
axs[3].set_ylabel("pairs read in the source,\nabsent from the index")
n_old = old.execute("SELECT count(*) FROM params WHERE repo_id='local/nrpic'").fetchone()[0]
n_new = new.execute("SELECT count(*) FROM params WHERE repo_id='local/nrpic'").fetchone()[0]
axs[3].set_title(f"(d) parameter rows {n_old} -> {n_new}", fontsize=10)
axs[3].legend(fontsize=7)
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT + ".png", dpi=150)
fig.savefig(OUT + ".pdf")
print(json.dumps({"before": before, "after": after, "rows": [n_old, n_new], "rev": rev,
                  "zero_bib": {"ok": okc, "review": revc}}))
