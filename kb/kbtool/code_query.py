"""`kb code "SYMBOL or text"` (brief 12.10): answers from the code index of every indexed
repository, upstream AthenaK and this repository (`local/nrpic`, alias `this`) alike.

Order of the answer: exact symbol names (name or qualified name, also `Class::name` and
`module.name` suffixes); run parameters (`name`, `block/name` or `<block> name`); file paths;
symbol names that begin with the query; then the full text of the code chunks (FTS5, BM25).
Read-only: opens db/current unless --db is given.
"""
import os
import re
import sqlite3

from .db import connect_ro, open_for_read

ALIASES = {"this": "local/nrpic", "local": "local/nrpic", "athenak": "IAS-Astrophysics/athenak",
           "upstream": "IAS-Astrophysics/athenak"}
SYMBOL_KINDS = {"function": ("function", "method", "subroutine"), "class": ("class", "struct", "union", "enum"),
                "symbol": None}


def _repo(r):
    return ALIASES.get(r, r) if r else None


def _fts_query(q):
    toks = re.findall(r"[A-Za-z0-9_]+", q)
    return " ".join(f'"{t}"' for t in toks) if toks else None


def search(lay, q, repo=None, kind="any", k=20, db=None):
    path = open_for_read(lay, db)
    if not os.path.exists(path):
        return []
    con = connect_ro(path)
    con.row_factory = sqlite3.Row
    repo = _repo(repo)
    hits, seen = [], set()

    def add(row, how, extra=None):
        key = (how, row["repo_id"], row["path"], row["line"], row["label"])
        if key in seen or len(hits) >= k:
            return
        seen.add(key)
        d = dict(row)
        d["match"] = how
        if extra:
            d.update(extra)
        hits.append(d)

    rfilter = " AND f.repo_id = :repo" if repo else ""
    args = {"q": q, "repo": repo, "k": k}
    try:
        if kind in ("any", "function", "class", "symbol"):
            kinds = SYMBOL_KINDS.get(kind)
            kf = (" AND s.kind IN (%s)" % ",".join("'%s'" % x for x in kinds)) if kinds else ""
            base = ("SELECT f.repo_id, f.path, s.line_start AS line, s.line_end, s.kind, s.qualname AS label, "
                    "s.signature, s.sym_id FROM symbols s JOIN code_files f USING(file_id) WHERE ")
            order = (" ORDER BY CASE s.kind WHEN 'prototype' THEN 1 WHEN 'macro' THEN 2 ELSE 0 END, "
                     "f.repo_id, f.path, s.line_start LIMIT :k")
            for row in con.execute(base + "(s.name = :q OR s.qualname = :q OR s.qualname LIKE '%::' || :q "
                                   "OR s.qualname LIKE '%.' || :q)" + kf + rfilter + order, args):
                add(row, "symbol")
        if kind in ("any", "param"):
            blk, nm = None, q
            m = re.match(r"^<?\s*([\w/\-\.]+?)\s*>?\s*[/ ]\s*([\w\-\.]+)$", q.strip())
            if m and ("/" in q or "<" in q or " " in q.strip()):
                blk, nm = m.group(1), m.group(2)
            pf = " AND p.repo_id = :repo" if repo else ""
            sql = ("SELECT p.repo_id, f.path, p.line, NULL AS line_end, 'param' AS kind, "
                   "'<' || p.block || '> ' || p.name AS label, p.type || COALESCE(' default ' || p.default_value, "
                   "' (required)') AS signature, NULL AS sym_id FROM params p JOIN code_files f USING(file_id) "
                   "WHERE p.name = :nm" + (" AND (p.block = :blk OR p.block LIKE '{%')" if blk else "") + pf +
                   " ORDER BY p.repo_id, p.block, f.path, p.line LIMIT :k")
            for row in con.execute(sql, dict(args, nm=nm, blk=blk)):
                add(row, "param")
            if blk is None and kind == "param":
                for row in con.execute(sql.replace("p.name = :nm", "p.block = :nm"), dict(args, nm=nm)):
                    add(row, "param-block")
        if kind in ("any", "file") and len(hits) < k and (("/" in q or "." in q) or kind == "file"):
            for row in con.execute("SELECT f.repo_id, f.path, NULL AS line, f.loc AS line_end, 'file' AS kind, "
                                   "f.path AS label, f.lang AS signature, NULL AS sym_id FROM code_files f "
                                   "WHERE f.path LIKE '%' || :q || '%'" + rfilter +
                                   " ORDER BY length(f.path) LIMIT :k", args):
                add(row, "file")
        if kind in ("any", "function", "class", "symbol") and len(hits) < k and re.match(r"^[\w:~\.]+$", q):
            kinds = SYMBOL_KINDS.get(kind)
            kf = (" AND s.kind IN (%s)" % ",".join("'%s'" % x for x in kinds)) if kinds else ""
            for row in con.execute("SELECT f.repo_id, f.path, s.line_start AS line, s.line_end, s.kind, "
                                   "s.qualname AS label, s.signature, s.sym_id FROM symbols s JOIN code_files f "
                                   "USING(file_id) WHERE s.name LIKE :q || '%' AND s.kind != 'prototype'" + kf +
                                   rfilter + " ORDER BY length(s.name), f.repo_id LIMIT :k", args):
                add(row, "symbol-prefix")
        if kind in ("any", "text") and len(hits) < k:
            fq = _fts_query(q)
            if fq:
                for row in con.execute("SELECT f.repo_id, f.path, c.line_start AS line, c.line_end, 'text' AS kind, "
                                       "COALESCE(s.qualname, f.path) AS label, "
                                       "snippet(code_fts, 0, '[', ']', ' ... ', 12) AS signature, c.sym_id "
                                       "FROM code_fts JOIN code_chunks c ON c.cc_id = code_fts.rowid "
                                       "JOIN code_files f ON f.file_id = c.file_id "
                                       "LEFT JOIN symbols s ON s.sym_id = c.sym_id "
                                       "WHERE code_fts MATCH :fq" + rfilter + " ORDER BY bm25(code_fts) LIMIT :k",
                                       dict(args, fq=fq)):
                    add(row, "text")
    finally:
        con.close()
    for h in hits:
        h["database"] = os.path.realpath(path)
    return hits


def format_hits(hits):
    if not hits:
        return "no match\n"
    out = []
    for h in hits:
        loc = f"{h['path']}" + (f":{h['line']}" if h.get("line") else "") + \
              (f"-{h['line_end']}" if h.get("line_end") and h["kind"] not in ("file",) else "")
        out.append(f"{h['repo_id']:<34s} {h['kind']:<10s} {h['label']}\n    {loc}\n    {h.get('signature') or ''}")
    out.append(f"(database {hits[0]['database']})")
    return "\n".join(out) + "\n"
