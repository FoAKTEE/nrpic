"""Lead check W5 (wave 2): independent recheck of the embed helper's K4-K5 results.

Read-only. Own code (no kbtool import):
  1. rescoring of the helper's registered retrieval results (results.json of runs
     kb-20261115-164540-5aca10c, ten questions, and kb-20261115-164558-5aca10c, K9 set): for every
     top-10 chunk, paper and character range are read from the database by chunk id and mapped to
     source lines through build/tex/<id_>/sourcemap.json with my own bisection; a hit is the right
     paper and file with lines overlapping the expected ranges widened by the set's slack;
  2. vector integrity: one vector per non-comment chunk and per equation for the model, the stored
     dimension, and the norm of 300 random vectors (unit vectors expected);
  3. sha256 of the model weights against the value in kb/EMBEDDING.md;
  4. tag reading sample: 2 tagged equations per tag (seed 20261116) with raw TeX and context, for
     the lead's reading (scratch only).
Writes rescoring.json, integrity.json, tags_sample.txt into OUTDIR (default $NRPIC_RUN_DIR).
Usage: python3 -I w2_embed_check.py DB KB_DATA MODEL_FILE EXPECTED_SHA RESULTS_JSON... [--out D]
"""
import array
import bisect
import collections
import hashlib
import json
import math
import os
import random
import sqlite3
import sys

args = sys.argv[1:]
out = os.environ.get("NRPIC_RUN_DIR")
if "--out" in args:
    i = args.index("--out")
    out = args[i + 1]
    args = args[:i] + args[i + 2:]
db, kbdata, model_file, expected_sha = args[:4]
results = args[4:]
os.makedirs(out, exist_ok=True)
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)

_maps = {}


def lines_of(paper, a, b):
    """(file, first line, last line) of flat.tex characters [a, b) by the paper's source map."""
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


resc = {}
for rp in results:
    R = json.load(open(rp))
    slack = R.get("slack_lines", 0)
    tag = R.get("set", os.path.basename(os.path.dirname(rp)))
    per = collections.Counter()
    helper = collections.Counter()
    disagree = []
    for q in R["questions"]:
        want = [(a - slack, b + slack) for a, b in q["lines"]]
        for mode, md in q["modes"].items():
            fh = md.get("first_hit")
            if fh is not None and fh <= 10:
                helper[mode] += 1
            hit = False
            for e in md["top10"][:10]:
                row = c.execute("select paper_id, char_start, char_end from chunks where chunk_id=?",
                                (e["chunk_id"],)).fetchone()
                if not row or row[0] != q["paper"]:
                    continue
                loc = lines_of(row[0], row[1], row[2])
                if loc and loc[0] == q["file"] and any(not (loc[2] < a or loc[1] > b) for a, b in want):
                    hit = True
                    break
            per[mode] += hit
            if hit != (fh is not None and fh <= 10):
                disagree.append((q["id"], mode, fh))
    resc[tag] = {"slack": slack, "questions": len(R["questions"]), "lead_hits@10": dict(per),
                 "helper_hits@10": dict(helper), "disagreements": disagree}

integ = {}
models = c.execute("select model, owner_kind, count(*), min(dim), max(dim) from embeddings "
                   "group by model, owner_kind").fetchall()
integ["vectors_by_model_kind"] = [list(r) for r in models]
integ["chunks_non_comment"] = c.execute("select count(*) from chunks where kind != 'comment'").fetchone()[0]
integ["equations"] = c.execute("select count(*) from equations").fetchone()[0]
integ["chunks_without_vector"] = c.execute(
    "select count(*) from chunks ch where ch.kind != 'comment' and not exists (select 1 from embeddings e "
    "where e.owner_kind='chunk' and e.owner_id=ch.chunk_id)").fetchone()[0]
integ["equations_without_vector"] = c.execute(
    "select count(*) from equations q where not exists (select 1 from embeddings e "
    "where e.owner_kind='equation' and e.owner_id=q.eq_id)").fetchone()[0]
integ["vectors_without_owner"] = c.execute(
    "select count(*) from embeddings e where (e.owner_kind='chunk' and not exists (select 1 from chunks "
    "where chunk_id=e.owner_id)) or (e.owner_kind='equation' and not exists (select 1 from equations "
    "where eq_id=e.owner_id))").fetchone()[0]
rng = random.Random(20261116)
n = c.execute("select count(*) from embeddings").fetchone()[0]
norms = []
for off in sorted(rng.sample(range(n), 300)):
    blob, dim = c.execute("select vec, dim from embeddings limit 1 offset ?", (off,)).fetchone()
    v = array.array("f")
    v.frombytes(blob)
    norms.append(math.sqrt(sum(x * x for x in v)))
integ["norm_min"], integ["norm_max"] = min(norms), max(norms)
h = hashlib.sha256()
with open(model_file, "rb") as f:
    for blk in iter(lambda: f.read(1 << 20), b""):
        h.update(blk)
integ["model_sha256"] = h.hexdigest()
integ["model_sha256_matches"] = h.hexdigest() == expected_sha

tags = collections.defaultdict(list)
for eid, tj in c.execute("select eq_id, tags_json from equations where tags_json not in ('[]','null') "
                         "and tags_json is not null"):
    try:
        for t in json.loads(tj):
            tags[t].append(eid)
    except ValueError:
        pass
integ["tagged_by_tag"] = {t: len(v) for t, v in sorted(tags.items())}
with open(os.path.join(out, "tags_sample.txt"), "w") as f:
    for t in sorted(tags):
        for eid in sorted(rng.sample(tags[t], min(2, len(tags[t])))):
            pid, lab, num, raw, ctx = c.execute(
                "select paper_id, label, number, tex_raw, context from equations where eq_id=?",
                (eid,)).fetchone()
            f.write(f"=== [{t}] eq {eid} {pid} ({num}) {lab}\nTEX: {raw[:500]}\nCTX: {(ctx or '')[:700]}\n")
with open(os.path.join(out, "rescoring.json"), "w") as f:
    json.dump(resc, f, indent=1)
with open(os.path.join(out, "integrity.json"), "w") as f:
    json.dump(integ, f, indent=1)
print(json.dumps({"rescoring": resc, "integrity": integ}, indent=1))
