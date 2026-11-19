"""Lead check W4 (wave 2): independent recheck of the claims helper's K8/K9 numbers.

Read-only on a snapshot (db/current) and the raw store; own SQL and own counting code (no
kbtool import). Writes into OUTDIR (default $NRPIC_RUN_DIR):
  recount.json  - C3 (papers not ok), C5 (bibliography entries with an arXiv id; distinct
                  (citing, cited arXiv id) edges and the fraction inside the corpus), C9 (claims
                  by label and status), C6 (several versions of one id);
  eqcount.tsv   - C8 third count: for each paper of the helper's C8 sample whose source is one
                  .tex file without \\input/\\include, numbered display lines by the lead's
                  counter (rules of tracks/kb/analysis/lead_checks/eqcount.py after the W3 fix)
                  against the database (equations with a number) and the helper's count;
  audit.txt     - 10 fulltext claims not yet checked by a person, drawn with seed 20261116,
                  with their cited lines, for the lead's reading (scratch only, paper text).
Usage: python3 -I w2_claims_check.py DB KB_DATA QA_JSON [OUTDIR]
"""
import collections
import json
import os
import random
import re
import sqlite3
import sys

db, kbdata, qa_json = sys.argv[1:4]
out = sys.argv[4] if len(sys.argv) > 4 else os.environ["NRPIC_RUN_DIR"]
os.makedirs(out, exist_ok=True)
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
qa = json.load(open(qa_json))

rec = {}
rec["papers"] = c.execute("select count(*) from papers").fetchone()[0]
rec["C3_not_ok"] = dict(c.execute(
    "select coalesce(parse_status,'null'), count(*) from papers where coalesce(parse_status,'') != 'ok' "
    "group by parse_status").fetchall())
n_bib = c.execute("select count(*) from bib_entries").fetchone()[0]
n_arx = c.execute("select count(*) from bib_entries where coalesce(target_arxiv,'') != ''").fetchone()[0]
rec["C5_bib_entries"] = n_bib
rec["C5_with_arxiv"] = n_arx
rec["C5_rate_arxiv"] = n_arx / n_bib
corpus = {r[0] for r in c.execute("select paper_id from papers")}
edges = {(a, b) for a, b in c.execute(
    "select citing, cited_arxiv from citations where coalesce(cited_arxiv,'') != ''")}
inside = sum(1 for a, b in edges if b in corpus)
rec["C5_distinct_edges"] = len(edges)
rec["C5_edges_in_corpus"] = inside
rec["C5_in_corpus_fraction"] = inside / len(edges) if edges else None
rec["C9_by_label"] = dict(c.execute("select label, count(*) from claims group by label").fetchall())
rec["C9_by_status"] = dict(c.execute("select status, count(*) from claim_meta group by status").fetchall())
vers = collections.defaultdict(list)
raw = os.path.join(kbdata, "raw", "arxiv")
for key in os.listdir(raw):
    vs = [v for v in os.listdir(os.path.join(raw, key)) if re.fullmatch(r"v\d+", v)]
    if len(vs) > 1:
        vers[key] = sorted(vs)
rec["C6_several_versions"] = dict(vers)

# ---- C8 third count -------------------------------------------------------------------------
NUM = ("equation", "align", "gather", "multline", "eqnarray", "flalign", "alignat")
INNER = ("aligned", "split", "cases", "array", "matrix", "pmatrix", "bmatrix", "gathered",
         "alignedat", "smallmatrix", "vmatrix")
PAT = re.compile(r"\\begin\{(" + "|".join(NUM) + r")(\*?)\}(.*?)\\end\{\1\2\}", re.S)


def count_numbered(src):
    src = re.sub(r"(?<!\\)%.*", "", src)
    if "\\begin{document}" in src:
        src = src.split("\\begin{document}", 1)[1]
    src = src.split("\\end{document}", 1)[0]
    total = 0
    for m in PAT.finditer(src):
        env, star, inner = m.groups()
        if star:
            continue
        if env in ("equation", "multline"):
            rows = [inner]
        else:
            s = inner
            for e in INNER:
                s = re.sub(r"\\begin\{" + e + r"\*?\}.*?\\end\{" + e + r"\*?\}",
                           lambda k: " " * len(k.group(0)), s, flags=re.S)
            cuts = [k.start() for k in re.finditer(r"\\\\", s)]
            rows, prev = [], 0
            for cut in cuts:
                rows.append(inner[prev:cut])
                prev = cut + 2
            rows.append(inner[prev:])
        for r in rows:
            if "\\nonumber" in r or "\\notag" in r or "\\tag" in r:
                continue
            total += 1
    return total


helper_rows = {r["paper_id"]: r for r in qa["C8"].get("rows", [])}
lines = ["paper\tfile\tlead\tdatabase\thelper_independent\thelper_database\thelper_shorthands"]
agree = collections.Counter()
for pid in qa["C8"]["sample"]:
    key = pid.replace("/", "_")
    meta = json.load(open(os.path.join(kbdata, "meta", "arxiv", key + ".json")))
    src = meta.get("src", "")
    if not os.path.isdir(src):
        continue
    texs = []
    for root, _d, files in os.walk(src):
        texs += [os.path.join(root, f) for f in files if f.lower().endswith(".tex")]
    if len(texs) != 1:
        continue
    body = open(texs[0], encoding="utf-8", errors="replace").read()
    stripped = re.sub(r"(?<!\\)%.*", "", body)
    if re.search(r"\\(input|include|subfile|import)\b", stripped):
        continue
    mine = count_numbered(body)
    dbn = c.execute("select count(*) from equations where paper_id=? and number is not null "
                    "and coalesce(env,'') not like '%tag%'", (pid,)).fetchone()[0]
    h = helper_rows.get(pid, {})
    hi, hd, hs = h.get("independent_numbered", ""), h.get("db_numbered", ""), h.get("shorthands", "")
    lines.append(f"{pid}\t{os.path.relpath(texs[0], src)}\t{mine}\t{dbn}\t{hi}\t{hd}\t{hs}")
    agree["equal" if mine == dbn else "differ"] += 1
with open(os.path.join(out, "eqcount.tsv"), "w") as f:
    f.write("\n".join(lines) + "\n")
rec["C8_lead_single_file_papers"] = dict(agree)

# ---- reading audit -------------------------------------------------------------------------
ids = [r[0] for r in c.execute(
    "select c.claim_id from claims c join claim_meta m using(claim_id) "
    "where c.label='fulltext' and m.status != 'checked' order by c.claim_id")]
rng = random.Random(20261116)
pick = sorted(rng.sample(ids, 10))
with open(os.path.join(out, "audit.txt"), "w") as f:
    for cid in pick:
        text, = c.execute("select text from claims where claim_id=?", (cid,)).fetchone()
        f.write(f"=== claim {cid}: {text}\n")
        for pid, ver, fn, a, b in c.execute(
                "select paper_id, version, file, line_start, line_end from claim_locators "
                "where claim_id=? order by ord", (cid,)):
            if not fn or a is None:
                f.write(f"--- {pid} (no file locator)\n")
                continue
            p = os.path.join(raw, pid.replace("/", "_"), ver, "src", fn)
            L = open(p, encoding="utf-8", errors="replace").read().split("\n")
            b = b or a
            f.write(f"--- {pid} {fn}:{a}-{b}\n")
            for i in range(max(1, a - 1), min(len(L), b + 1) + 1):
                f.write(f"{i:5d}| {L[i - 1][:300]}\n")
rec["audit_claim_ids"] = pick
with open(os.path.join(out, "recount.json"), "w") as f:
    json.dump(rec, f, indent=1)
print(json.dumps(rec, indent=1))
