"""K9: `kb qa run` -> QA_REPORT.md (+ qa.json for figures), brief 12.9.

Checks, each with its numbers and the ids it concerns (never paper text):
  C1  counts against the manifests (downloads table, papers table)
  C2  an abstract and at least one section for every ingested paper
  C3  parse failures and the review list, with a classification of causes
  C4  30 papers drawn at random, title and authors against INSPIRE (needs kb-data/meta)
  C5  resolution rate of bibliography entries; fraction of in-corpus citation edges
  C6  duplicates among versions of one paper and among papers
  C7  retrieval regression on the golden questions (hit rate within the top 10)
  C8  independent equation count on a random sample of papers (qa_eqcount)
  C9  the claims layer (K8): labels, statuses, who checked
  C10 references of the verification suite (CHARTER section 10) present in the base

Reads the database read-only (default kb.sqlite, the working database, which holds the
claims between snapshots) and the stored sources as text. Standard library only, except C7
in hybrid mode (numpy and the local model of kb/.venv, through kbtool.embed_*).
"""
import collections
import difflib
import json
import os
import random
import re
import sqlite3
import time

from . import brief as _brief
from . import qa_eqcount as _eq
from . import qa_golden as _gold
from .paths import CHECKOUT, kb_manifest_dir

SEED = 20261115


def _ro(path):
    return sqlite3.connect(f"file:{os.path.abspath(path)}?mode=ro", uri=True, timeout=60)


def _key(pid):
    return pid.replace("/", "_")


# ---------------------------------------------------------------- C1, C2
def c1_counts(con):
    # the manifest is brief section 17 plus the additions of decision 0016 item 6
    from . import meta_manifest as _mm
    rows = _mm.load_full_manifest(kb_manifest_dir())
    man = {r["id"]: r for r in rows}
    n_add = sum(1 for r in rows if r.get("source") == "addition")
    dl = {r[0]: r[1:] for r in con.execute("SELECT paper_id, in_manifest, status, source_kind FROM downloads")}
    papers = {r[0]: r[1:] for r in con.execute("SELECT paper_id, parse_status, source_kind FROM papers")}
    by_status = collections.Counter(dl[i][1] if i in dl else "no record" for i in man)
    missing_dl = sorted(i for i in man if i not in dl or dl[i][1] in ("missing", "failed"))
    not_ingested = sorted(i for i in man if i not in papers)
    extras = sorted(i for i in papers if i not in man)
    by_pri = {}
    for p in (3, 2, 1):
        ids = [i for i, r in man.items() if r["priority"] == p]
        by_pri[str(p)] = {"manifest": len(ids), "ingested": sum(1 for i in ids if i in papers),
                          "ok": sum(1 for i in ids if i in papers and papers[i][0] == "ok")}
    return {"manifest": len(man), "manifest_brief17": len(man) - n_add, "manifest_additions": n_add,
            "downloads_by_status": dict(by_status), "missing_downloads": missing_dl,
            "ingested_manifest": len(man) - len(not_ingested), "not_ingested": not_ingested,
            "papers_total": len(papers), "extras_ingested": extras, "by_priority": by_pri,
            "agree": len(not_ingested) == 0 and not missing_dl}


RE_SECTIONING = re.compile(r"\\(?:sub)*section\*?\s*[\[{]|\\chapter\*?\s*[\[{]|\\part\*?\s*[\[{]")


def c2_abstract_sections(con, build_tex=None):
    # papers.abstract holds the arXiv-API abstract once the metadata are loaded (kbtool.meta_papers),
    # so the extraction is judged by the abstract chunk; a paper with neither is `without_abstract`
    no_abs, no_abs_chunk, no_sec = [], [], []
    for pid, abstract, kind in con.execute("SELECT paper_id, abstract, source_kind FROM papers ORDER BY paper_id"):
        has_chunk = bool(con.execute(
            "SELECT 1 FROM chunks WHERE paper_id=? AND kind='abstract' LIMIT 1", (pid,)).fetchone())
        has_abs = bool(abstract and abstract.strip()) or has_chunk
        n_sec = con.execute("SELECT count(*) FROM sections WHERE paper_id=?", (pid,)).fetchone()[0]
        if not has_chunk:
            no_abs_chunk.append(pid)
        if not has_abs:
            no_abs.append(pid)
        if n_sec == 0:
            no_sec.append(pid)
    n = con.execute("SELECT count(*) FROM papers").fetchone()[0]
    # a paper without sections: does its flattened text hold any sectioning command at all?
    no_cmd, missed, no_flat = [], [], []
    for pid in no_sec:
        p = os.path.join(build_tex, _key(pid), "flat.tex") if build_tex else None
        if not p or not os.path.isfile(p):
            no_flat.append(pid)
            continue
        with open(p, "rb") as f:
            t = f.read(64 << 20).decode("utf-8", errors="replace")
        (missed if RE_SECTIONING.search(t) else no_cmd).append(pid)
    return {"papers": n, "without_abstract": no_abs, "without_abstract_chunk": no_abs_chunk, "without_sections": no_sec,
            "with_both": n - len(set(no_abs) | set(no_sec)),
            "sectionless_no_command": no_cmd, "sectionless_extraction_missed": missed,
            "sectionless_no_flat": no_flat}


# ---------------------------------------------------------------- C3
def classify(parse_json, status, source_kind):
    """Causes of a paper that is not 'ok' (several may apply)."""
    try:
        pj = json.loads(parse_json or "{}")
    except ValueError:
        pj = {}
    q = pj.get("quality", {}) or {}
    comp = q.get("components", {}) or {}
    causes = []
    if status == "failed" or source_kind in ("none",):
        causes.append("no TeX source (PostScript or nothing usable)")
    if status == "pdf" or source_kind == "pdf":
        causes.append("PDF only (text extraction, no equations)")
    if pj.get("error"):
        causes.append("parser error")
    if comp.get("title") == 0:
        causes.append("no \\title")
    if comp.get("abstract") == 0:
        causes.append("no abstract environment")
    if comp.get("sections") == 0:
        causes.append("no sections")
    cls = (pj.get("class") or "").lower()
    if not cls and status not in ("failed", "pdf"):
        causes.append("no \\documentclass (plain TeX or fragment)")
    if re.search(r"thesis|report|book|memoir", cls) or (q.get("body_words") or 0) > 60000:
        causes.append("thesis or long document")
    if (comp.get("macros_resolved") is not None and comp.get("macros_resolved") < 0.9):
        causes.append("many unresolved macros")
    if (comp.get("inputs_resolved") is not None and comp.get("inputs_resolved") < 1.0):
        causes.append("unresolved \\input")
    return causes or ["score below threshold, no single cause"]


def c3_failures(con):
    out = []
    for pid, st, sk, pj, score in con.execute(
            "SELECT paper_id, parse_status, source_kind, parse_json, parse_score FROM papers "
            "WHERE parse_status != 'ok' ORDER BY parse_status, paper_id"):
        out.append({"paper_id": pid, "status": st, "score": score, "causes": classify(pj, st, sk)})
    by_cause = collections.Counter(c for r in out for c in r["causes"])
    by_status = collections.Counter(r["status"] for r in out)
    return {"not_ok": len(out), "by_status": dict(by_status), "by_cause": dict(by_cause.most_common()),
            "papers": out}


# ---------------------------------------------------------------- C4
def _norm_title(t):
    t = re.sub(r"\\[A-Za-z]+\s*", " ", t or "")
    t = re.sub(r"[^A-Za-z0-9]+", " ", t).lower()
    return re.sub(r"\s+", " ", t).strip()


_TEX_ACCENT = re.compile(r"""\\[`'^"~=.uvHcdbrtk]\s*\{?\\?([A-Za-z])\}?""")
_GERMAN = {"\u00e4": "ae", "\u00f6": "oe", "\u00fc": "ue", "\u00df": "ss"}


def _name_forms(s):
    """Lower-case ASCII forms of a name string: diacritics dropped (u for u-umlaut) and the
    German transliteration (ue); TeX accent commands are resolved first."""
    import unicodedata
    s = _TEX_ACCENT.sub(lambda m: m.group(1), s or "").replace("{", "").replace("}", "").lower()
    plain = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    german = unicodedata.normalize("NFKD", "".join(_GERMAN.get(ch, ch) for ch in s)).encode("ascii", "ignore").decode()
    return {plain, german}


def compare_meta(tex_title, tex_authors, meta_title, meta_authors):
    """(title ratio, fraction of metadata surnames found among the TeX authors). Names are
    compared in ASCII forms, so a umlaut in one record and 'ue' in the other agree."""
    r = difflib.SequenceMatcher(None, _norm_title(tex_title), _norm_title(meta_title)).ratio() if meta_title else None
    if not meta_authors:
        return r, None
    have = _name_forms(" ".join(tex_authors or []))
    sur = [a.split(",")[0].split()[-1] for a in meta_authors if a.strip()]
    found = sum(1 for s in sur if s and any(f and f in h for f in _name_forms(s) for h in have))
    return r, (found / len(sur) if sur else None)


def _meta_root(meta_dir):
    """The `kb-data/meta` directory. Accepts it directly, or the inventory's `meta/arxiv`
    (what `run()` passed in wave 2), from which the fetch command's directories are siblings."""
    meta_dir = os.path.abspath(meta_dir)
    if os.path.basename(meta_dir) in ("arxiv", "inspire", "arxiv-api") and not any(
            os.path.isdir(os.path.join(meta_dir, d)) for d in ("inspire", "arxiv-api")):
        return os.path.dirname(meta_dir)
    return meta_dir


def _title_authors(d):
    """(title, [author names]) of one metadata record of any of the three layouts, or None."""
    if not isinstance(d, dict):
        return None
    if d.get("status") not in (None, "ok"):                        # INSPIRE 'not-found' and the like
        return None
    md = d.get("record") or d.get("metadata") or d
    if not isinstance(md, dict):
        return None
    title = md.get("title") or ((md.get("titles") or [{}])[0] or {}).get("title")
    auth = md.get("authors") or []
    if isinstance(auth, str):
        auth = [auth]
    auth = [a.get("full_name") or a.get("name") or "" if isinstance(a, dict) else str(a) for a in auth]
    if not title and not auth:
        return None
    return title, auth


def _meta_record(meta_dir, pid):
    """INSPIRE/arXiv metadata on disk: returns (title, [authors], source) or None.

    Order: INSPIRE `meta/inspire/<key>.json` (written by `nrpic-fetch-arxiv --meta`, record
    under "record"), then the arXiv API `meta/arxiv-api/<key>.json`, then the names of wave 1
    `meta/arxiv/<key>.inspire.json` and `<key>.api.json` (never written, kept for old stores)."""
    root = _meta_root(meta_dir)
    k = _key(pid)
    for source, p in (("inspire", os.path.join(root, "inspire", f"{k}.json")),
                      ("arxiv-api", os.path.join(root, "arxiv-api", f"{k}.json")),
                      ("inspire", os.path.join(root, "arxiv", f"{k}.inspire.json")),
                      ("arxiv-api", os.path.join(root, "arxiv", f"{k}.api.json"))):
        if not os.path.isfile(p):
            continue
        try:
            with open(p) as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        ta = _title_authors(d)
        if ta is not None:
            return ta[0], ta[1], source
    return None


TITLE_MIN, AUTHORS_MIN = 0.9, 0.8          # below either: listed as differing, read by a person


def c4_inspire_sample(con, meta_dir, n=30):
    ids = [r[0] for r in con.execute("SELECT paper_id FROM papers WHERE parse_status IN ('ok','review') "
                                     "ORDER BY paper_id")]
    sample = sorted(random.Random(SEED).sample(ids, min(n, len(ids))))
    rows, have, differ = [], 0, []
    has_pj = "parse_json" in {r[1] for r in con.execute("PRAGMA table_info(papers)")}
    for pid in sample:
        if has_pj:
            title, aj, pjs = con.execute("SELECT title, authors_json, parse_json FROM papers WHERE paper_id=?",
                                         (pid,)).fetchone()
        else:
            (title, aj), pjs = con.execute("SELECT title, authors_json FROM papers WHERE paper_id=?",
                                           (pid,)).fetchone(), None
        try:
            authors = json.loads(aj or "[]")
        except ValueError:
            authors = []
        # once the metadata are loaded, title and authors are the arXiv-API values; the TeX
        # extraction that C4 tests is kept in parse_json.tex_front (kbtool.meta_papers)
        try:
            front = (json.loads(pjs or "{}") or {}).get("tex_front")
        except ValueError:
            front = None
        if front:
            title = front.get("title") or ""
            authors = front.get("authors") or []
        m = _meta_record(meta_dir, pid)
        if m is None:
            rows.append({"paper_id": pid, "metadata": False})
            continue
        have += 1
        tr, ar = compare_meta(title, [a if isinstance(a, str) else str(a) for a in authors], m[0], m[1])
        rows.append({"paper_id": pid, "metadata": True, "source": m[2], "title_ratio": tr, "author_fraction": ar})
        if (tr is not None and tr < TITLE_MIN) or (ar is not None and ar < AUTHORS_MIN):
            differ.append(pid)
    by_source = dict(collections.Counter(r["source"] for r in rows if r["metadata"]))
    return {"sample": sample, "seed": SEED, "with_metadata": have, "rows": rows, "by_source": by_source,
            "differ": differ, "title_min": TITLE_MIN, "authors_min": AUTHORS_MIN, "blocked": have == 0}


# ---------------------------------------------------------------- C5
def c5_bibliography(con):
    tot = con.execute("SELECT count(*) FROM bib_entries").fetchone()[0]
    arx = con.execute("SELECT count(*) FROM bib_entries WHERE target_arxiv IS NOT NULL").fetchone()[0]
    doi = con.execute("SELECT count(*) FROM bib_entries WHERE target_doi IS NOT NULL").fetchone()[0]
    anyid = con.execute("SELECT count(*) FROM bib_entries WHERE target_arxiv IS NOT NULL OR target_doi IS NOT NULL "
                        "OR target_recid IS NOT NULL").fetchone()[0]
    by_res = dict(con.execute("SELECT coalesce(resolved_by,'none'), count(*) FROM bib_entries GROUP BY 1"))
    by_src = {s: {"entries": n, "with_id": k} for s, n, k in con.execute(
        "SELECT coalesce(source,'?'), count(*), sum(target_arxiv IS NOT NULL OR target_doi IS NOT NULL) "
        "FROM bib_entries GROUP BY 1")}
    dist = con.execute("SELECT count(*), sum(ic) FROM (SELECT citing, cited_arxiv, max(in_corpus) ic FROM citations "
                       "WHERE cited_arxiv IS NOT NULL GROUP BY 1, 2)").fetchone()
    cit = con.execute("SELECT count(*), sum(in_corpus) FROM citations").fetchone()
    cit_id = con.execute("SELECT count(*), sum(in_corpus) FROM citations WHERE cited_arxiv IS NOT NULL OR "
                         "cited_doi IS NOT NULL").fetchone()
    return {"entries": tot, "with_arxiv": arx, "with_doi": doi, "with_any_id": anyid,
            "rate_any_id": anyid / tot if tot else None, "rate_arxiv": arx / tot if tot else None,
            "by_resolved_by": by_res, "by_source": by_src, "citations": cit[0], "in_corpus": cit[1] or 0,
            "in_corpus_fraction": (cit[1] or 0) / cit[0] if cit[0] else None,
            "citations_with_id": cit_id[0], "in_corpus_fraction_of_identified": (cit_id[1] or 0) / cit_id[0]
            if cit_id[0] else None,
            "distinct_edges_arxiv": dist[0], "distinct_in_corpus": dist[1] or 0,
            "distinct_in_corpus_fraction": (dist[1] or 0) / dist[0] if dist[0] else None}


# ---------------------------------------------------------------- C6
def c6_duplicates(con):
    multi = []
    for pid, vj in con.execute("SELECT paper_id, versions_present_json FROM downloads"):
        try:
            vs = json.loads(vj or "[]")
        except ValueError:
            vs = []
        if len(vs) > 1:
            multi.append({"paper_id": pid, "versions": vs})
    same_flat = [list(g.split(",")) for (g,) in con.execute(
        "SELECT group_concat(paper_id) FROM papers WHERE flat_sha256 IS NOT NULL GROUP BY flat_sha256 "
        "HAVING count(*) > 1")]
    same_src = [list(g.split(",")) for (g,) in con.execute(
        "SELECT group_concat(paper_id) FROM papers WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING count(*) > 1")]
    titles = collections.defaultdict(list)
    for pid, t in con.execute("SELECT paper_id, title FROM papers WHERE title IS NOT NULL AND title != ''"):
        nt = _norm_title(t)
        if len(nt) >= 20:
            titles[nt].append(pid)
    same_title = [v for v in titles.values() if len(v) > 1]
    abstracts = collections.defaultdict(list)
    for pid, a in con.execute("SELECT paper_id, abstract FROM papers WHERE abstract IS NOT NULL"):
        na = _norm_title(a)[:300]
        if len(na) >= 80:
            abstracts[na].append(pid)
    same_abs = [v for v in abstracts.values() if len(v) > 1]
    return {"several_versions_stored": multi, "same_flat_tex": same_flat, "same_source_bytes": same_src,
            "same_title": same_title, "same_abstract_start": same_abs}


# ---------------------------------------------------------------- C7
def c7_retrieval(lay, db_path, hybrid=False, k=10):
    from . import embed_search as S
    out = {"k": k, "questions": len(_gold.QUESTIONS), "modes": {}}
    # Guard (in this process only) for a defect of embed_search.Locator.lines: an empty
    # sourcemap (PDF-only 2201.03458, failed astro-ph/9407016) raises IndexError; such a hit
    # then has no source range. Reported to the lead (tracks/kb/claims/README.md, Requests).
    if not getattr(S.Locator.lines, "_qa_guard", False):
        _orig = S.Locator.lines

        def _lines(self, pid, start, end):
            try:
                return _orig(self, pid, start, end)
            except IndexError:
                out.setdefault("empty_sourcemap_hits", set()).add(pid)
                return None
        _lines._qa_guard = True
        S.Locator.lines = _lines
    # rerank: the second stage over sentence windows (kbtool/search_rerank.py, its default
    # variant; tracks/kb/retrieval/JOURNAL.md R4)
    modes = ["text"] + (["hybrid", "rerank"] if hybrid else [])
    emb, model, store = None, None, None
    if hybrid:
        try:
            from . import embed_cli as EC
            from . import search_rerank as R
            emb = EC._embedder("bge-small")
            model = EC._model_key("bge-small")
            out["rerank_config"] = {"name": R.DEFAULT, **R.CONFIGS[R.DEFAULT]}
        except BaseException as e:                      # no numpy, no model: report and go on
            out["hybrid_error"] = f"{type(e).__name__}: {e}"
            modes = ["text"]
    con = _ro(db_path)
    try:
        nvec = con.execute("SELECT count(*) FROM embeddings WHERE owner_kind='chunk'").fetchone()[0]
        nch = con.execute("SELECT count(*) FROM chunks WHERE kind != 'comment'").fetchone()[0]
        out["vectors"], out["chunks"] = nvec, nch
        if emb is not None:
            store = S.VectorStore(con, model, "chunk")         # loaded once for all questions
        for mode in modes:
            rows = []
            for q in _gold.questions():
                if mode == "rerank":
                    hits, info = R.search(lay, q["question"], k=k, con=con, embedder=emb, model=model, store=store)
                else:
                    hits, info = S.search(lay, q["question"], k=k, mode=mode, con=con, embedder=emb, model=model,
                                          store=store if mode != "text" else None)
                rp, rl = _gold.hit_level(q, hits)
                rows.append({"id": q["id"], "paper": q["paper"], "paper_rank": rp, "locator_rank": rl,
                             "top_papers": [h.get("paper_id") for h in hits[:3]]})
            out["modes"][mode] = {
                "rows": rows, "paper_hits": sum(1 for r in rows if r["paper_rank"]),
                "locator_hits": sum(1 for r in rows if r["locator_rank"]),
                "paper_hit_rate": sum(1 for r in rows if r["paper_rank"]) / len(rows),
                "locator_hit_rate": sum(1 for r in rows if r["locator_rank"]) / len(rows),
                "mrr_paper": sum(1.0 / r["paper_rank"] for r in rows if r["paper_rank"]) / len(rows)}
    finally:
        con.close()
    if "empty_sourcemap_hits" in out:
        out["empty_sourcemap_hits"] = sorted(out["empty_sourcemap_hits"])
    return out


# ---------------------------------------------------------------- C8
def c8_equations(con, lay, n=40, must=("2611.12831",)):
    ids = [r[0] for r in con.execute("SELECT paper_id FROM papers WHERE parse_status IN ('ok','review') AND "
                                     "source_kind='tex' ORDER BY paper_id")]
    rest = [i for i in ids if i not in must]
    sample = list(must) + sorted(random.Random(SEED + 1).sample(rest, min(n, len(rest))))
    rows = []
    for pid in sample:
        r = con.execute("SELECT version, main_tex FROM papers WHERE paper_id=?", (pid,)).fetchone()
        if not r:
            continue
        ver, main = r
        src = os.path.join(lay.raw_arxiv, _key(pid), ver or "", "src")
        flat = os.path.join(lay.build, "tex", _key(pid), "flat.tex")
        text, which = _eq.source_for(src, main, flat)
        if text is None:
            rows.append({"paper_id": pid, "input": which, "error": "no text"})
            continue
        mine = _eq.count_document(text)
        db_rows, db_num = con.execute("SELECT count(*), count(number) FROM equations WHERE paper_id=?",
                                      (pid,)).fetchone()
        rows.append({"paper_id": pid, "input": which, "independent_numbered": mine["numbered"],
                     "independent_displays": mine["displays"], "tagged": mine["tagged"],
                     "db_rows": db_rows, "db_numbered": db_num, "diff": db_num - mine["numbered"],
                     "shorthands": len(mine["shorthands"])})
    ok = [r for r in rows if "diff" in r]
    exact = sum(1 for r in ok if r["diff"] == 0)
    within = sum(1 for r in ok if abs(r["diff"]) <= max(2, 0.02 * max(r["independent_numbered"], 1)))
    tot_i = sum(r["independent_numbered"] for r in ok)
    tot_d = sum(r["db_numbered"] for r in ok)
    return {"sample": sample, "seed": SEED + 1, "rows": rows, "papers": len(ok), "exact": exact,
            "within_2pc_or_2": within, "total_independent": tot_i, "total_db": tot_d,
            "mismatches": [r for r in ok if r["diff"] != 0]}


# ---------------------------------------------------------------- C9, C10
def c9_claims(con):
    from . import claims_cli
    try:
        return claims_cli.stats(con)
    except sqlite3.Error as e:
        return {"error": str(e)}


def c10_suite_references(con):
    path = os.path.join(CHECKOUT, "coord", "CHARTER.md")
    try:
        text = open(path).read()
    except OSError:
        return {"error": f"{path} not readable"}
    m = re.search(r"^## 10\..*?(?=^## |\Z)", text, re.S | re.M)
    sec = m.group(0) if m else ""
    ids = sorted(set(re.findall(r"(?<![\d.])(\d{4}\.\d{4,5}|(?:astro-ph|gr-qc|hep-th|hep-ph)/\d{7})(?![\d])", sec)))
    have = {r[0]: r[1] for r in con.execute("SELECT paper_id, parse_status FROM papers")}
    return {"section_found": bool(sec), "ids": ids, "ingested": [i for i in ids if i in have],
            "missing": [i for i in ids if i not in have],
            "status": {i: have.get(i) for i in ids}}


# ---------------------------------------------------------------- run
def run(lay, db_path=None, hybrid=False, eq_n=40):
    db_path = db_path or lay.db_work
    con = _ro(db_path)
    t0 = time.time()
    try:
        rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "database": os.path.realpath(db_path),
               "snapshot_current": os.path.basename(os.path.realpath(lay.db_current))
               if os.path.exists(lay.db_current) else None}
        rep["C1"] = c1_counts(con)
        rep["C2"] = c2_abstract_sections(con, os.path.join(lay.build, "tex"))
        rep["C3"] = c3_failures(con)
        rep["C4"] = c4_inspire_sample(con, os.path.join(lay.data, "meta"))
        rep["C5"] = c5_bibliography(con)
        rep["C6"] = c6_duplicates(con)
        rep["C8"] = c8_equations(con, lay, n=eq_n)
        rep["C9"] = c9_claims(con)
        rep["C10"] = c10_suite_references(con)
    finally:
        con.close()
    rep["C7"] = c7_retrieval(lay, db_path, hybrid=hybrid)
    rep["seconds"] = round(time.time() - t0, 1)
    return rep


def _pc(x):
    return "n/a" if x is None else f"{100 * x:.1f} %"


def markdown(rep):
    L = []
    a = L.append
    a("# Quality report of the knowledge base (brief 12.9)")
    a("")
    a(f"Written by `kb qa run` (kbtool/qa_report.py) at {rep['at']} from `{rep['database']}`"
      f" (db/current: `{rep['snapshot_current']}`). Ids, counts and our own wording only; no paper text.")
    a("")
    c = rep["C1"]
    a("## C1. Counts against the manifests")
    a("")
    a(f"- Manifest: {c['manifest']} arXiv ids (brief section 17: {c.get('manifest_brief17', c['manifest'])}; "
      f"additions of decision 0016 item 6: {c.get('manifest_additions', 0)}); downloads by status: " +
      ", ".join(f"{k} {v}" for k, v in sorted(c["downloads_by_status"].items())) + ".")
    a(f"- Ingested: {c['ingested_manifest']} of {c['manifest']} manifest ids; {len(c['extras_ingested'])} extras; "
      f"{c['papers_total']} papers in all. Not ingested: {', '.join(c['not_ingested']) or 'none'}.")
    for p, d in c["by_priority"].items():
        a(f"- Priority {p}: {d['ingested']} of {d['manifest']} ingested, {d['ok']} with status ok.")
    a(f"- Missing or failed downloads: {', '.join(c['missing_downloads']) or 'none'}.")
    a(f"- Verdict: {'counts agree' if c['agree'] else 'counts do NOT agree (lists above)'}.")
    a("")
    c = rep["C2"]
    a("## C2. Abstract and at least one section for every paper")
    a("")
    a(f"- {c['with_both']} of {c['papers']} papers have both. Without an abstract ({len(c['without_abstract'])}): "
      f"{', '.join(c['without_abstract']) or 'none'}.")
    if "without_abstract_chunk" in c:
        a(f"- No abstract extracted from the source (no abstract chunk; the metadata abstract may still be there) "
          f"({len(c['without_abstract_chunk'])}): {', '.join(c['without_abstract_chunk']) or 'none'}.")
    a(f"- Without any section ({len(c['without_sections'])}): {', '.join(c['without_sections']) or 'none'}.")
    if "sectionless_no_command" in c:
        a(f"  - of these, no sectioning command at all in flat.tex (letters, plain TeX): "
          f"{len(c['sectionless_no_command'])}; a sectioning command present but no section extracted: "
          f"{len(c['sectionless_extraction_missed'])} ({', '.join(c['sectionless_extraction_missed']) or 'none'}); "
          f"no flat.tex: {', '.join(c['sectionless_no_flat']) or 'none'}.")
    a("")
    c = rep["C3"]
    a("## C3. Parse failures and the review list, by cause")
    a("")
    a(f"- {c['not_ok']} papers not ok: " + ", ".join(f"{k} {v}" for k, v in sorted(c["by_status"].items())) + ".")
    a("- Causes (several per paper possible; from the quality components stored in papers.parse_json):")
    for k, v in c["by_cause"].items():
        a(f"  - {k}: {v}")
    a("")
    a("| paper | status | score | causes |")
    a("|---|---|---|---|")
    for r in c["papers"]:
        a(f"| {r['paper_id']} | {r['status']} | {r['score'] if r['score'] is not None else '-'} | "
          f"{'; '.join(r['causes'])} |")
    a("")
    c = rep["C4"]
    a("## C4. Thirty papers at random against INSPIRE")
    a("")
    a(f"- Sample (random.Random({c['seed']}), from the ingested papers): {', '.join(c['sample'])}.")
    if c["blocked"]:
        a("- **Blocked**: no INSPIRE or arXiv-API record exists under kb-data/meta/inspire or meta/arxiv-api for any "
          "of them (`nrpic-fetch-arxiv --meta` writes them). The comparison code "
          "(`qa_report.compare_meta`: title similarity, surnames found) is tested on synthetic records.")
    else:
        a(f"- {c['with_metadata']} of {len(c['sample'])} have metadata on disk (kb-data/meta/inspire/<key>.json, else "
          f"meta/arxiv-api/<key>.json; written by nrpic-fetch-arxiv --meta); by source: " +
          ", ".join(f"{k} {v}" for k, v in sorted(c.get("by_source", {}).items())) + ".")
        a(f"- Compared: the title and authors the TeX parser stored in `papers` against the metadata record "
          f"(title similarity of normalised strings; fraction of metadata surnames found in the TeX author list). "
          f"Below {c.get('title_min', 0.9)} or {_pc(c.get('authors_min', 0.8))}: "
          f"{', '.join(c.get('differ') or []) or 'none'}.")
        a("")
        a("| paper | source | title ratio | authors found |")
        a("|---|---|---|---|")
        for r in c["rows"]:
            if r["metadata"]:
                tr = "-" if r["title_ratio"] is None else f"{r['title_ratio']:.3f}"
                a(f"| {r['paper_id']} | {r.get('source', '-')} | {tr} | {_pc(r['author_fraction'])} |")
            else:
                a(f"| {r['paper_id']} | none | - | - |")
    a("")
    c = rep["C5"]
    a("## C5. Bibliography resolution and the citation graph")
    a("")
    a(f"- {c['entries']} bibliography entries; with an arXiv id {c['with_arxiv']} ({_pc(c['rate_arxiv'])}), with a "
      f"DOI {c['with_doi']}, with any identifier {c['with_any_id']} ({_pc(c['rate_any_id'])}).")
    a("- By source: " + "; ".join(f"{s} {d['entries']} entries, {d['with_id']} with an id"
                                   for s, d in sorted(c["by_source"].items())) + ".")
    a("- By resolution step: " + ", ".join(f"{k} {v}" for k, v in sorted(c["by_resolved_by"].items())) + ".")
    a(f"- Distinct citation edges (citing paper, cited arXiv id): {c['distinct_edges_arxiv']}, inside the corpus "
      f"{c['distinct_in_corpus']} ({_pc(c['distinct_in_corpus_fraction'])}); the definition of the K3 report.")
    a(f"- Citation rows (one per `\\cite` occurrence): {c['citations']}; in the corpus {c['in_corpus']} "
      f"({_pc(c['in_corpus_fraction'])}); of the {c['citations_with_id']} rows with an identifier, "
      f"{_pc(c['in_corpus_fraction_of_identified'])} in the corpus.")
    a("")
    c = rep["C6"]
    a("## C6. Duplicates")
    a("")
    a(f"- Papers stored in more than one version: {len(c['several_versions_stored'])}" +
      (": " + ", ".join(f"{r['paper_id']} ({'/'.join(r['versions'])})" for r in c["several_versions_stored"])
       if c["several_versions_stored"] else "") + " (the database holds one version per id).")
    a(f"- Different ids with identical flattened text: {c['same_flat_tex'] or 'none'}; identical source bytes: "
      f"{c['same_source_bytes'] or 'none'}.")
    a(f"- Different ids with the same normalised title: {c['same_title'] or 'none'}; same abstract start: "
      f"{c['same_abstract_start'] or 'none'}.")
    a("")
    c = rep["C7"]
    a("## C7. Retrieval regression (golden questions)")
    a("")
    a(f"- {c['questions']} questions (kbtool/qa_golden.py; own wording, answers from KB-G1 and checked claims); "
      f"hit within the top {c['k']} chunks. Vectors stored for {c.get('vectors')} of {c.get('chunks')} chunks.")
    if c.get("hybrid_error"):
        a(f"- Hybrid mode not run: {c['hybrid_error']}.")
    if c.get("rerank_config"):
        rc = c["rerank_config"]
        a(f"- Mode rerank: `kbtool/search_rerank.py`, variant {rc['name']}: the first {rc['pool']} chunks of the "
          f"hybrid list" + (f" plus all chunks of its first {rc['expand']} papers" if rc['expand'] else "") +
          f", cut into windows of {rc['win']} sentences (stride {rc['stride']}), ordered by reciprocal-rank fusion "
          f"of window BM25 and window vectors" + (" and the hybrid order" if rc.get("with_stage1") else "") + ".")
    a("- KB-G2 (decision 0016, item 6): at least 80 % of the golden questions with the right paper in the top ten "
      "(gating); the hit at the answer location is reported, not gating.")
    if c.get("empty_sourcemap_hits"):
        a(f"- Hits of papers with an empty source map (no line range; `embed_search.Locator.lines` raises "
          f"IndexError there, guarded in this run): {', '.join(c['empty_sourcemap_hits'])}.")
    for mode, d in c["modes"].items():
        a(f"- **{mode}**: paper hit rate {d['paper_hits']}/{c['questions']} ({_pc(d['paper_hit_rate'])}), locator "
          f"hit rate {d['locator_hits']}/{c['questions']} ({_pc(d['locator_hit_rate'])}), mean reciprocal rank of "
          f"the paper {d['mrr_paper']:.3f}.")
    a("")
    a("| question | paper | " + " | ".join(f"{m} paper rank | {m} locator rank" for m in c["modes"]) + " |")
    a("|---|---|" + "---|---|" * len(c["modes"]))
    rows = {m: {r["id"]: r for r in d["rows"]} for m, d in c["modes"].items()}
    for q in _gold.questions():
        a(f"| {q['id']} | {q['paper']} | " + " | ".join(
            f"{rows[m][q['id']]['paper_rank'] or '-'} | {rows[m][q['id']]['locator_rank'] or '-'}" for m in rows) + " |")
    a("")
    c = rep["C8"]
    a("## C8. Independent equation count on a sample")
    a("")
    a(f"- {c['papers']} papers (2611.12831 and {c['papers'] - 1} drawn with random.Random({c['seed']})): numbered "
      f"display lines counted by `kbtool/qa_eqcount.py` (a stack scanner written apart from the extractor) "
      f"against the equation rows with a number in the database.")
    a(f"- Agree exactly: {c['exact']} of {c['papers']}; within 2 % or 2 lines: {c['within_2pc_or_2']}. Totals: "
      f"independent {c['total_independent']}, database {c['total_db']}.")
    a("")
    a("| paper | input | independent | database | difference |")
    a("|---|---|---|---|---|")
    for r in c["rows"]:
        if "diff" in r:
            a(f"| {r['paper_id']} | {r['input']} | {r['independent_numbered']} | {r['db_numbered']} | {r['diff']:+d} |")
        else:
            a(f"| {r['paper_id']} | {r['input']} | - | - | {r.get('error')} |")
    a("")
    c = rep["C9"]
    a("## C9. The claims layer (K8)")
    a("")
    if "by_label" in c:
        a(f"- {c['claims']} claims on {c['papers']} papers; labels: " +
          ", ".join(f"{k} {v}" for k, v in sorted(c["by_label"].items(), key=lambda x: str(x[0]))) + "; statuses: " +
          ", ".join(f"{k} {v}" for k, v in sorted(c["by_status"].items(), key=lambda x: str(x[0]))) + ".")
        a(f"- Locators {c['locators'][0]}, resolved {c['locators'][1]}; claims with a chunk {c['with_chunk']}; "
          f"labels set by a person {c['checked_by_person']}.")
        a("- By track (status counts): " + "; ".join(
            f"{t}: " + ", ".join(f"{k} {v}" for k, v in sorted(d.items(), key=lambda x: str(x[0])))
            for t, d in sorted(c["by_track_status"].items(), key=lambda x: str(x[0]))) + ".")
    else:
        a(f"- {c}")
    a("")
    c = rep["C10"]
    a("## C10. References of the verification suite (CHARTER section 10)")
    a("")
    if "error" in c:
        a(f"- {c['error']}")
    else:
        a(f"- {len(c['ids'])} arXiv ids in the section; ingested {len(c['ingested'])}; missing: "
          f"{', '.join(c['missing']) or 'none'}.")
    a("")
    a(f"Run time {rep['seconds']} s.")
    return "\n".join(L) + "\n"
