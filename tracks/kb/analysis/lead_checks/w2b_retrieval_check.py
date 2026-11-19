"""Lead check B2 (wave 2b): independent rescoring of the retrieval helper's results.

Read-only, own code (no kbtool import). Inputs: the helper's registered outputs
  - rerank_eval.json of run kb-20261119-142613-942f713 (R4: top-10 chunk ids per question and
    mode, six modes, 32 golden + 10 held-out questions, snapshot kb-20261115-a848a06);
  - qa.json of run kb-20261119-151500-2721f64 (R5: final kb qa run, ranks per question and mode);
and the question sets as data: tracks/kb/claims/golden_questions.yaml (slack 5 lines) and
tracks/kb/embed/questions10.yaml (no slack), read by a minimal reader of that YAML layout.
  1. For every question and mode: is a top-10 chunk from the expected paper (paper hit), and does
     one of them map, through build/tex/<key>/sourcemap.json and my own bisection, to the expected
     file with lines overlapping the expected ranges widened by the slack (location hit).
  2. The final run's rerank ranks against R4's w2-noexpand, question by question.
  3. C4 of the final run: for the 30 sampled papers, the INSPIRE record file exists, and my own
     title comparison (lower-case word sequence, difflib ratio) of the snapshot title against the
     INSPIRE titles.
Writes retrieval_check.json into OUTDIR.
Usage: python3 -I w2b_retrieval_check.py NRPIC_HOME WORKTREE R4_JSON QA_JSON [--out D]
"""
import bisect
import collections
import difflib
import json
import os
import re
import sqlite3
import sys

args = sys.argv[1:]
out = os.environ.get("NRPIC_RUN_DIR")
if "--out" in args:
    i = args.index("--out")
    out = args[i + 1]
    args = args[:i] + args[i + 2:]
home, wt, r4p, qap = args[:4]
os.makedirs(out, exist_ok=True)
kbdata = os.path.join(home, "kb-data")
R4 = json.load(open(r4p))
QA = json.load(open(qap))
db = R4["database"]
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def read_questions(path):
    """Minimal reader of the question YAML layout (id, paper, file, lines)."""
    qs, cur = [], None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\s*-\s+id:\s*(\S+)", line)
        if m:
            cur = {"id": m.group(1).strip('"')}
            qs.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"\s+(paper|file):\s*(.+)$", line)
        if m:
            cur[m.group(1)] = m.group(2).strip().strip('"')
            continue
        m = re.match(r"\s+lines:\s*(\[.*\])\s*$", line)
        if m:
            cur["lines"] = json.loads(m.group(1))
    return qs


gold = {q["id"]: q for q in read_questions(os.path.join(wt, "tracks/kb/claims/golden_questions.yaml"))}
ten = {q["id"]: q for q in read_questions(os.path.join(wt, "tracks/kb/embed/questions10.yaml"))}
_maps = {}


def lines_of(paper, a, b):
    if paper not in _maps:
        p = os.path.join(kbdata, "build", "tex", paper.replace("/", "_"), "sourcemap.json")
        try:
            m = json.load(open(p))
        except (OSError, ValueError):
            m = []
        _maps[paper] = ([e[0] for e in m], m)
    offs, m = _maps[paper]
    if not m or a is None:
        return None
    i = max(0, bisect.bisect_right(offs, a) - 1)
    j = max(0, bisect.bisect_right(offs, max(a, (b or a) - 1)) - 1)
    f0, l0 = m[i][1], m[i][2]
    lines = [m[k][2] for k in range(i, j + 1) if m[k][1] == f0]
    return f0, l0, max(lines) if lines else l0


def score(q, top, slack):
    paper_rank = loc_rank = None
    for r, cid in enumerate(top[:10], 1):
        row = c.execute("select paper_id, char_start, char_end from chunks where chunk_id=?", (cid,)).fetchone()
        if not row or row[0] != q["paper"]:
            continue
        paper_rank = paper_rank or r
        loc = lines_of(row[0], row[1], row[2])
        if loc and loc[0] == q["file"] and any(loc[1] <= hi + slack and loc[2] >= lo - slack
                                               for lo, hi in q["lines"]):
            loc_rank = loc_rank or r
    return paper_rank, loc_rank


lead = collections.defaultdict(lambda: collections.Counter())
helper = collections.defaultdict(lambda: collections.Counter())
disagree = []
per_q = {}
for qq in R4["questions"]:
    s = qq["set"]
    q = gold.get(qq["id"]) if s == "golden32" else ten.get(qq["id"])
    slack = 5 if s == "golden32" else 0
    if q is None or q.get("paper") != qq["paper"]:
        disagree.append((s, qq["id"], "question not found or paper differs"))
        continue
    for mode, md in qq["modes"].items():
        pr, lr = score(q, md["top"], slack)
        lead[(s, mode)]["paper"] += pr is not None
        lead[(s, mode)]["loc"] += lr is not None
        helper[(s, mode)]["paper"] += md["paper_rank"] is not None and md["paper_rank"] <= 10
        helper[(s, mode)]["loc"] += md["locator_rank"] is not None and md["locator_rank"] <= 10
        per_q[(s, qq["id"], mode)] = (pr, lr)
        if (pr is None) != (md["paper_rank"] is None) or (lr is None) != (md["locator_rank"] is None):
            disagree.append((s, qq["id"], mode, (pr, lr), (md["paper_rank"], md["locator_rank"])))
res = {"rescoring": {f"{s}/{m}": {"lead": dict(lead[(s, m)]), "helper": dict(helper[(s, m)])}
                     for (s, m) in sorted(lead)},
       "disagreements": disagree}

# 2. final run against R4
fin = QA["C7"]["modes"]
cmp_rows, diffs = 0, []
for mode_fin, mode_r4 in (("text", "text"), ("hybrid", "hybrid"), ("rerank", "w2-noexpand")):
    for row in fin[mode_fin]["rows"]:
        r4 = next(x for x in R4["questions"] if x["set"] == "golden32" and x["id"] == row["id"])
        m = r4["modes"][mode_r4]
        cmp_rows += 1
        if (row["paper_rank"], row["locator_rank"]) != (m["paper_rank"], m["locator_rank"]):
            diffs.append((mode_fin, row["id"], (row["paper_rank"], row["locator_rank"]),
                          (m["paper_rank"], m["locator_rank"])))
res["final_vs_r4"] = {"rows": cmp_rows, "differences": diffs,
                      "final_counts": {m: {"paper": sum(1 for r in fin[m]["rows"] if r["paper_rank"]),
                                           "loc": sum(1 for r in fin[m]["rows"] if r["locator_rank"])}
                                       for m in fin}}
res["missed_location_rerank"] = [r["id"] for r in fin["rerank"]["rows"] if not r["locator_rank"]]
res["missed_paper_rerank"] = [r["id"] for r in fin["rerank"]["rows"] if not r["paper_rank"]]


# 3. C4
def words(s):
    return re.findall(r"[a-z0-9]+", (s or "").lower())


c4 = []
for row in QA["C4"]["rows"]:
    pid = row["paper_id"]
    p = os.path.join(kbdata, "meta", "inspire", pid.replace("/", "_") + ".json")
    rec = {}
    try:
        j = json.load(open(p))
        rec = j.get("record", {}) if j.get("status") == "ok" else {}
    except (OSError, ValueError):
        pass
    t_db = c.execute("select title from papers where paper_id=?", (pid,)).fetchone()
    titles = [t.get("title", "") for t in rec.get("titles", [])]
    best = max((difflib.SequenceMatcher(None, words(t_db[0] if t_db else ""), words(t), autojunk=False).ratio()
                for t in titles), default=0.0)
    c4.append({"paper": pid, "inspire_ok": bool(rec), "lead_title_ratio": round(best, 3),
               "helper_title_ratio": row.get("title_ratio"), "helper_authors": row.get("author_fraction")})
res["c4"] = {"rows": c4, "with_record": sum(r["inspire_ok"] for r in c4),
             "lead_below_0.9": [r["paper"] for r in c4 if r["lead_title_ratio"] < 0.9],
             "helper_differ": QA["C4"].get("differ")}
res["parse_status_snapshot"] = dict(c.execute("select parse_status, count(*) from papers group by 1").fetchall())
with open(os.path.join(out, "retrieval_check.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:5000])
