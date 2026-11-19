"""K3 (brief 12.5): resolution of bibliography entries against the corpus, the citation graph,
`kb frontier` and `kb cites`.

Resolution order for an entry: arXiv id written in it (or in its eprint field, or arXiv's DOI
10.48550/arXiv.<id>) -> DOI equal to the DOI of a corpus paper -> fuzzy title match against the
corpus titles (similarity ratio >= TITLE_MIN of the normalised strings; below that no edge is drawn). INSPIRE look-ups
(by DOI or title) need network access that kb does not have yet (README, Request 2); entries
that would need them are counted as unresolved.
"""
import re
from collections import Counter, defaultdict

try:
    from rapidfuzz import fuzz as _fuzz

    def title_score(a, b):
        return _fuzz.ratio(a, b) / 100.0
    FUZZY = "rapidfuzz ratio (normalised Indel similarity of lower-cased titles)"
except Exception:                                    # pragma: no cover
    import difflib

    def title_score(a, b):
        return difflib.SequenceMatcher(None, a, b).ratio()
    FUZZY = "difflib ratio"

TITLE_MIN = 0.93                                     # [JUDGEMENT]; checked in tests on known pairs
TITLE_MIN_LEN = 25                                   # characters; shorter titles are not matched


def norm_title(t):
    t = re.sub(r"\\[A-Za-z]+", " ", t or "")
    t = re.sub(r"[^A-Za-z0-9 ]+", " ", t).lower()
    return re.sub(r"\s+", " ", t).strip()


def norm_arxiv(a):
    if not a:
        return None
    a = re.sub(r"v\d+$", "", a.strip())
    return a.lower() if "/" in a else a


def resolve_corpus(con):
    """Second pass over all bibliography entries, after the corpus has changed. The caller
    holds the writer lock and commits. Returns counts."""
    corpus = {r[0]: (r[1] or "", r[2]) for r in con.execute("SELECT paper_id, title, doi FROM papers")}
    by_doi = {d.lower(): pid for pid, (_, d) in corpus.items() if d}
    titles = [(pid, norm_title(t)) for pid, (t, _) in corpus.items() if len(norm_title(t)) >= TITLE_MIN_LEN]
    n_doi = n_title = 0
    rows = con.execute("SELECT bib_id, paper_id, target_arxiv, target_doi, title, resolved_by FROM bib_entries "
                       "WHERE target_arxiv IS NULL OR resolved_by IN ('doi-corpus', 'title-fuzzy-corpus')").fetchall()
    for bid, citing, arx, doi, title, how in rows:
        if how in ("doi-corpus", "title-fuzzy-corpus"):          # recompute from scratch
            con.execute("UPDATE bib_entries SET target_arxiv=NULL, resolved_by=?, confidence=? WHERE bib_id=?",
                        ("doi" if doi else None, 0.9 if doi else None, bid))
        if doi and doi.lower() in by_doi and by_doi[doi.lower()] != citing:
            con.execute("UPDATE bib_entries SET target_arxiv=?, resolved_by='doi-corpus', confidence=0.95 "
                        "WHERE bib_id=?", (by_doi[doi.lower()], bid))
            n_doi += 1
            continue
        nt = norm_title(title)
        if len(nt) >= TITLE_MIN_LEN and titles:
            best, score = None, 0.0
            for pid, t in titles:
                if pid == citing:
                    continue
                s = title_score(nt, t)
                if s > score:
                    best, score = pid, s
            if best and score >= TITLE_MIN:
                con.execute("UPDATE bib_entries SET target_arxiv=?, resolved_by='title-fuzzy-corpus', confidence=? "
                            "WHERE bib_id=?", (best, round(score, 3), bid))
                n_title += 1
    # normalise ids, then propagate to the citations and mark in-corpus edges
    for bid, a in con.execute("SELECT bib_id, target_arxiv FROM bib_entries WHERE target_arxiv IS NOT NULL").fetchall():
        na = norm_arxiv(a)
        if na != a:
            con.execute("UPDATE bib_entries SET target_arxiv=? WHERE bib_id=?", (na, bid))
    con.execute("UPDATE citations SET cited_arxiv = (SELECT target_arxiv FROM bib_entries b WHERE b.bib_id = "
                "citations.bib_id), cited_doi = (SELECT target_doi FROM bib_entries b WHERE b.bib_id = "
                "citations.bib_id) WHERE bib_id IS NOT NULL")
    con.execute("UPDATE citations SET in_corpus = CASE WHEN cited_arxiv IN (SELECT paper_id FROM papers) "
                "THEN 1 ELSE 0 END")
    return {"doi_corpus": n_doi, "title_fuzzy_corpus": n_title, "fuzzy": FUZZY}


def bib_stats(con):
    r = con.execute("SELECT count(*), sum(target_arxiv IS NOT NULL), sum(target_arxiv IS NULL AND target_doi IS NOT "
                    "NULL), sum(target_arxiv IS NULL AND target_doi IS NULL) FROM bib_entries").fetchone()
    by = dict(con.execute("SELECT coalesce(resolved_by,'unresolved'), count(*) FROM bib_entries GROUP BY 1"))
    src = dict(con.execute("SELECT coalesce(source,'none'), count(DISTINCT paper_id) FROM bib_entries GROUP BY 1"))
    c = con.execute("SELECT count(*), sum(bib_id IS NULL), sum(cited_arxiv IS NOT NULL), sum(in_corpus = 1) "
                    "FROM citations").fetchone()
    edges = con.execute("SELECT count(*), sum(in_corpus) FROM (SELECT citing, cited_arxiv, max(in_corpus) AS "
                        "in_corpus FROM citations WHERE cited_arxiv IS NOT NULL GROUP BY citing, cited_arxiv)").fetchone()
    return {"bib_entries": r[0] or 0, "with_arxiv": r[1] or 0, "doi_only": r[2] or 0, "no_identifier": r[3] or 0,
            "resolved_by": by, "papers_by_bib_source": src,
            "citations": c[0] or 0, "citations_without_bib_entry": c[1] or 0, "citations_with_arxiv": c[2] or 0,
            "citations_in_corpus": c[3] or 0, "edges": edges[0] or 0, "edges_in_corpus": edges[1] or 0}


def frontier(con, n=50, manifest=None):
    """Works cited by many corpus papers but absent from the corpus (by arXiv id), with the
    number of distinct citing papers, whether the manifest of brief section 17 lists them and
    their last download status (table downloads of kb verify-downloads)."""
    status = dict(con.execute("SELECT paper_id, status FROM downloads WHERE in_manifest = 1").fetchall()) \
        if _has(con, "downloads") else {}
    man = {k: status.get(k) for k in (manifest or status)}
    rows = con.execute("SELECT cited_arxiv, count(DISTINCT citing) AS k FROM citations WHERE in_corpus = 0 AND "
                       "cited_arxiv IS NOT NULL GROUP BY cited_arxiv ORDER BY k DESC, cited_arxiv LIMIT ?",
                       (n,)).fetchall()
    out = []
    for a, k in rows:
        title = con.execute("SELECT title FROM bib_entries WHERE target_arxiv = ? AND title IS NOT NULL LIMIT 1",
                            (a,)).fetchone()
        out.append({"arxiv": a, "cited_by": k, "in_manifest": a in man, "download_status": man.get(a),
                    "title_in_bib": title[0] if title else None})
    return out


def _has(con, table):
    return con.execute("SELECT 1 FROM sqlite_master WHERE name = ?", (table,)).fetchone() is not None


def cites(con, pid, direction="out", with_context=False):
    if direction == "out":
        q = ("SELECT c.cite_key, c.cited_arxiv, c.cited_doi, c.in_corpus, c.context, c.char_start FROM citations c "
             "WHERE c.citing = ? ORDER BY c.char_start")
        rows = con.execute(q, (pid,)).fetchall()
        out = [{"key": r[0], "arxiv": r[1], "doi": r[2], "in_corpus": r[3], "char_start": r[5],
                **({"context": r[4]} if with_context else {})} for r in rows]
    else:
        q = ("SELECT c.citing, c.cite_key, c.context, c.char_start FROM citations c WHERE c.cited_arxiv = ? "
             "ORDER BY c.citing, c.char_start")
        rows = con.execute(q, (pid,)).fetchall()
        out = [{"citing": r[0], "key": r[1], "char_start": r[3], **({"context": r[2]} if with_context else {})}
               for r in rows]
    return out


def group_matrix(con):
    """In-corpus citation edges (distinct citing-cited pairs) counted by (group of citing,
    group of cited), from the manifest groups of brief section 17. Returns (groups, matrix dict)."""
    rows = con.execute("SELECT DISTINCT c.citing, c.cited_arxiv, p1.grp, p2.grp FROM citations c "
                       "JOIN papers p1 ON p1.paper_id = c.citing JOIN papers p2 ON p2.paper_id = c.cited_arxiv "
                       "WHERE c.in_corpus = 1 AND c.citing != c.cited_arxiv").fetchall()
    m = Counter((r[2], r[3]) for r in rows)
    groups = sorted({g for pair in m for g in pair if g})
    return groups, dict(m)


def group_check(con):
    """For each corpus paper with in-corpus out-edges: the group its out-edges point to most,
    compared with its own manifest group (brief 12.5, last item)."""
    rows = con.execute("SELECT DISTINCT c.citing, p1.grp, c.cited_arxiv, p2.grp FROM citations c "
                       "JOIN papers p1 ON p1.paper_id = c.citing JOIN papers p2 ON p2.paper_id = c.cited_arxiv "
                       "WHERE c.in_corpus = 1 AND c.citing != c.cited_arxiv").fetchall()
    per = defaultdict(Counter)
    own = {}
    for citing, g1, cited, g2 in rows:
        per[citing][g2] += 1
        own[citing] = g1
    out = []
    for pid, cnt in per.items():
        top, k = cnt.most_common(1)[0]
        out.append({"paper": pid, "group": own[pid], "edges": sum(cnt.values()), "top_cited_group": top,
                    "top_share": round(k / sum(cnt.values()), 3), "own_share": round(cnt[own[pid]] / sum(cnt.values()), 3)})
    return sorted(out, key=lambda d: (d["own_share"], -d["edges"]))
