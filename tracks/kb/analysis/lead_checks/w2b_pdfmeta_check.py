"""Lead check B1 (wave 2b): independent recheck of the pdf_meta helper's results.

Read-only, own code (imports neither kbtool nor the helper's scripts). Opens kb-data/db/kb.sqlite
read-only (the working database the helper wrote; db/current is still kb-20261115-a848a06).
  1. the three PDF papers: parse status, sections, chunks, captions, bibliography entries,
     citation rows (outgoing, incoming) counted by SQL;
  2. abstract of gr-qc/9412071: word-sequence similarity (difflib) of its abstract chunk against
     the arXiv-API abstract in kb-data/meta/arxiv-api/<key>.json;
  3. metadata columns of the papers table (title source, INSPIRE record, DOI, journal reference,
     licence, version against the API's latest version, title_matches_brief, groups);
     the title of 25 random papers (seed 20261120) against the arXiv-API record, compared by me;
  4. kb/manifests/arxiv_additions.tsv against the rows of papers that are not in arxiv.tsv;
  5. vectors: one per non-comment chunk, no orphan;
  6. reading samples (scratch only, paper text): 20 word repairs not in the helper's sample
     (seed 20261120) and 20 'cmmi-greek' repairs, a kind the helper's audit left out;
  7. the three author errata of brief section 16: the brief line the helper's table names,
     printed with the arXiv-API and INSPIRE author lists for my reading.
Writes pdfmeta_check.json, repair_reading.tsv, errata_reading.txt into OUTDIR.
Usage: python3 -I w2b_pdfmeta_check.py NRPIC_HOME WORKTREE HELPER_SAMPLE_TSV [--out D]
"""
import csv
import difflib
import json
import os
import random
import re
import sqlite3
import sys

args = sys.argv[1:]
out = os.environ.get("NRPIC_RUN_DIR")
if "--out" in args:
    i = args.index("--out")
    out = args[i + 1]
    args = args[:i] + args[i + 2:]
home, wt, helper_sample = args[:3]
os.makedirs(out, exist_ok=True)
kbdata = os.path.join(home, "kb-data")
c = sqlite3.connect(f"file:{kbdata}/db/kb.sqlite?mode=ro", uri=True)
R = {}


def q1(sql, *a):
    return c.execute(sql, a).fetchone()[0]


# 1. the three PDF papers
pdfp = {}
for pid in ("gr-qc/9412071", "astro-ph/9407016", "2201.03458"):
    row = c.execute("select parse_status, source_kind, title_source, version from papers where paper_id=?",
                    (pid,)).fetchone()
    pdfp[pid] = {
        "row": row,
        "sections": q1("select count(*) from sections where paper_id=?", pid),
        "chunks": q1("select count(*) from chunks where paper_id=?", pid),
        "chunks_by_kind": dict(c.execute("select kind, count(*) from chunks where paper_id=? group by kind",
                                         (pid,)).fetchall()),
        "figures": q1("select count(*) from figures where paper_id=?", pid),
        "bib_entries": q1("select count(*) from bib_entries where paper_id=?", pid),
        "citations_out": q1("select count(*) from citations where citing=?", pid),
        "distinct_cite_keys_out": q1("select count(distinct cite_key) from citations where citing=?", pid),
        "citations_in": q1("select count(*) from citations where cited_arxiv=?", pid),
        "equations": q1("select count(*) from equations where paper_id=?", pid),
        "vectors": q1("select count(*) from embeddings e join chunks ch on e.owner_kind='chunk' "
                      "and e.owner_id=ch.chunk_id where ch.paper_id=?", pid),
    }
R["pdf_papers"] = pdfp


def words(s):
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def api(pid):
    p = os.path.join(kbdata, "meta", "arxiv-api", pid.replace("/", "_") + ".json")
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return None


def inspire(pid):
    p = os.path.join(kbdata, "meta", "inspire", pid.replace("/", "_") + ".json")
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return None


# 2. abstract similarity
absim = {}
for pid in pdfp:
    a = api(pid) or {}
    api_abs = a.get("abstract") or a.get("summary") or ""
    ch = c.execute("select text from chunks where paper_id=? and kind='abstract' order by chunk_id limit 1",
                   (pid,)).fetchone()
    absim[pid] = {
        "api_abstract_words": len(words(api_abs)),
        "chunk_words": len(words(ch[0])) if ch else 0,
        "ratio": round(difflib.SequenceMatcher(None, words(ch[0]) if ch else [], words(api_abs),
                                               autojunk=False).ratio(), 4),
        "api_keys": sorted(a.keys())[:20],
    }
R["abstract_similarity"] = absim

# 3. metadata columns
cols = {}
cols["papers"] = q1("select count(*) from papers")
for col in ("primary_class", "submitted", "updated", "doi", "inspire_recid", "journal_ref", "license",
            "grp", "brief_title"):
    cols[f"{col}_nonempty"] = q1(f"select count(*) from papers where {col} is not null and {col} != ''")
cols["title_source"] = dict(c.execute("select title_source, count(*) from papers group by 1").fetchall())
cols["title_matches_brief"] = {str(k): v for k, v in c.execute(
    "select title_matches_brief, count(*) from papers group by 1").fetchall()}
cols["parse_status"] = dict(c.execute("select parse_status, count(*) from papers group by 1").fetchall())
cols["grp"] = dict(c.execute("select grp, count(*) from papers group by 1").fetchall())
# version against the API's latest version
vers_bad, api_missing, title_cmp = [], [], []
ids = [r[0] for r in c.execute("select paper_id from papers order by paper_id")]
for pid in ids:
    a = api(pid)
    if not a:
        api_missing.append(pid)
        continue
    v = c.execute("select version from papers where paper_id=?", (pid,)).fetchone()[0]
    latest = a.get("version") or a.get("latest_version")
    if latest is None:
        m = re.search(r"v(\d+)$", a.get("id", "") or a.get("arxiv_id", ""))
        latest = f"v{m.group(1)}" if m else None
    if latest and v and str(latest).lstrip("v") != str(v).lstrip("v"):
        vers_bad.append((pid, v, latest))
cols["api_record_missing"] = api_missing
cols["version_differs_from_api"] = vers_bad
rng = random.Random(20261120)
for pid in sorted(rng.sample(ids, 25)):
    a = api(pid) or {}
    t_db = c.execute("select title from papers where paper_id=?", (pid,)).fetchone()[0]
    t_api = a.get("title") or ""
    norm = lambda s: " ".join(words(s))  # noqa: E731
    title_cmp.append((pid, norm(t_db) == norm(t_api), t_db[:90]))
cols["title_vs_api_sample25"] = title_cmp
R["metadata"] = cols

# 4. additions file
man = set()
with open(os.path.join(wt, "kb", "manifests", "arxiv.tsv")) as f:
    for row in csv.reader(f, delimiter="\t"):
        if row and not row[0].startswith("#") and row[0] != "arxiv_id" and row[0] != "id":
            man.add(row[0].strip())
add = {}
with open(os.path.join(wt, "kb", "manifests", "arxiv_additions.tsv")) as f:
    rows = [r for r in csv.reader(f, delimiter="\t") if r and not r[0].startswith("#")]
hdr = rows[0]
for r in rows[1:]:
    add[r[0].strip()] = dict(zip(hdr, r))
db_extra = set(ids) - man
R["additions"] = {
    "manifest_ids": len(man), "additions_rows": len(add), "db_rows_not_in_manifest": len(db_extra),
    "same_set": set(add) == db_extra, "only_in_file": sorted(set(add) - db_extra),
    "only_in_db": sorted(db_extra - set(add)),
    "group_db_equals_file": all(
        c.execute("select grp from papers where paper_id=?", (p,)).fetchone()[0] == add[p].get("group", add[p].get("grp"))
        for p in add if p in db_extra),
    "header": hdr,
}

# 5. vectors
R["vectors"] = {
    "chunks_non_comment": q1("select count(*) from chunks where kind != 'comment'"),
    "chunk_vectors": q1("select count(*) from embeddings where owner_kind='chunk'"),
    "chunks_without_vector": q1("select count(*) from chunks ch where ch.kind != 'comment' and not exists "
                                "(select 1 from embeddings e where e.owner_kind='chunk' and e.owner_id=ch.chunk_id)"),
    "orphan_chunk_vectors": q1("select count(*) from embeddings e where e.owner_kind='chunk' and not exists "
                               "(select 1 from chunks where chunk_id=e.owner_id)"),
    "equations": q1("select count(*) from equations"),
    "equation_vectors": q1("select count(*) from embeddings where owner_kind='equation'"),
}

# 6. repair reading samples
seen = set()
with open(helper_sample, encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        seen.add((r["paper"], r["old"].strip("'"), r["new"].strip("'"), r["context"][:60]))
WORD = ("ligature-dropped", "ligature-split", "ot1-ligature", "dehyphen")
pool_w, pool_g = [], []
for pid in ("gr-qc/9412071", "astro-ph/9407016"):
    key = pid.replace("/", "_")
    ed = json.load(open(os.path.join(kbdata, "build", "tex", key, "pdf_edits.json"), encoding="utf-8"))
    raw = open(os.path.join(kbdata, "build", "tex", key, "pdf_raw.txt"), encoding="utf-8").read()
    parts, pos = [], 0
    for a, b, old, new, kind in sorted(ed["step1_on_raw"], key=lambda e: e[0]):
        parts += [raw[pos:a], new]
        pos = b
    parts.append(raw[pos:])
    t1 = "".join(parts)
    for step, text in (("step1_on_raw", raw), ("step2_on_step1", t1)):
        for a, b, old, new, kind in ed[step]:
            ctx = (text[max(0, a - 40):a] + "[[" + repr(old) + "=>" + new + "]]" + text[b:b + 40])
            ctx = ctx.replace("\n", " ").replace("\t", " ")
            item = (pid, kind, old, new, ctx)
            if kind in WORD:
                pool_w.append(item)
            elif kind == "cmmi-greek":
                pool_g.append(item)
rng = random.Random(20261120)
fresh = [x for x in pool_w if (x[0], x[2], x[3]) not in {(s[0], s[1], s[2]) for s in seen}]
samp_w = rng.sample(fresh, min(20, len(fresh)))
samp_g = rng.sample(pool_g, min(20, len(pool_g)))
with open(os.path.join(out, "repair_reading.tsv"), "w", encoding="utf-8") as f:
    f.write("k\tpool\tpaper\tkind\told\tnew\tcontext\tverdict\n")
    for k, (pid, kind, old, new, ctx) in enumerate(samp_w + samp_g, 1):
        f.write(f"{k}\t{'word' if k <= len(samp_w) else 'greek'}\t{pid}\t{kind}\t{old!r}\t{new!r}\t{ctx}\t\n")
# cmmi-greek outside display mathematics: a Greek letter between two Latin letters
inside_word = [x for x in pool_g if re.search(r"[A-Za-z]$", x[4].split("[[")[0])
               and re.match(r"[A-Za-z]", x[4].split("]]", 1)[1] if "]]" in x[4] else "")]
R["repairs"] = {"word_pool": len(pool_w), "word_pool_not_in_helper_sample": len(fresh),
                "greek_pool": len(pool_g), "greek_inside_a_word": len(inside_word),
                "greek_inside_a_word_examples": [(x[0], repr(x[2]), x[3]) for x in inside_word[:12]]}

# 7. the three author errata
tsv = {}
with open(os.path.join(wt, "tracks", "kb", "pdf_meta", "brief16_comparison.tsv"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        tsv[r["id"]] = r
brief = os.path.join(home, "einstein_vlasov_pic_cosmology_agent_brief.en.md")
blines = open(brief, encoding="utf-8").read().split("\n")
with open(os.path.join(out, "errata_reading.txt"), "w", encoding="utf-8") as f:
    for pid in ("2310.00776", "2107.06306", "2204.13098", "1203.6185"):
        r = tsv.get(pid, {})
        ln = int(r.get("line") or 0)
        f.write(f"=== {pid} table: authors_class={r.get('authors_class')} inspire={r.get('authors_class_inspire')} "
                f"missing={r.get('missing')} agree={r.get('agree')}\n")
        f.write(f"brief line {ln}: {blines[ln - 1] if ln else ''}\n")
        a = api(pid) or {}
        f.write("arxiv-api authors: " + "; ".join(str(x) for x in a.get("authors", [])) + "\n")
        ins = inspire(pid) or {}
        rec = ins.get("record", ins)
        f.write("inspire authors: " + "; ".join(x.get("full_name", "") for x in rec.get("authors", [])[:12]) + "\n")
R["table_agree"] = {k: sum(1 for r in tsv.values() if r.get(k) == "True") for k in ("agree", "agree_arxiv")}
R["table_rows"] = len(tsv)
with open(os.path.join(out, "pdfmeta_check.json"), "w") as f:
    json.dump(R, f, indent=1, default=str)
print(json.dumps(R, indent=1, default=str)[:6000])
