"""Read-only queries of the knowledge base used to answer the kb-requests (no writes).

    python3 -I kbq.py eq   <paper> <number>          equation by printed number -> file:line, label
    python3 -I kbq.py fts  "<fts5 query>" [--paper ID] [-k N] [--kinds body,appendix,...]
                                                      chunks by BM25 -> paper, section, file:line
    python3 -I kbq.py grep <paper> "<regex>"          regex over flat.tex of one paper -> file:line
    python3 -I kbq.py bib  "<regex>" [-k N]           bibliography entries whose raw text matches
    python3 -I kbq.py cites <arxiv id>                in-corpus papers that cite an id (with context)
    python3 -I kbq.py title "<regex>"                 papers whose stored title matches

Database: $KBQ_DB or kb-data/db/kb.sqlite (opened read-only). Locators file:line come from
build/tex/<id_>/sourcemap.json. Output lists our identifiers, ids, numbers and at most 160
characters of matched context per hit, for the session's own reading only.
"""
import argparse
import bisect
import json
import os
import re
import sqlite3
import sys

DATA = "/data/haiyangw/nrpic/kb-data"
DB = os.environ.get("KBQ_DB", os.path.join(DATA, "db", "kb.sqlite"))


def con():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=60)


_SM = {}


def where(pid, off):
    if pid not in _SM:
        p = os.path.join(DATA, "build", "tex", pid.replace("/", "_"), "sourcemap.json")
        sm = json.load(open(p)) if os.path.exists(p) else []
        _SM[pid] = ([s for s, *_ in sm], sm)
    starts, sm = _SM[pid]
    i = bisect.bisect_right(starts, off) - 1
    if i < 0:
        return "?"
    return f"{sm[i][1]}:{sm[i][2]}"


def section_of(c, pid, off):
    r = c.execute("SELECT number, title FROM sections WHERE paper_id=? AND char_start<=? AND char_end>? "
                  "ORDER BY char_end-char_start LIMIT 1", (pid, off, off)).fetchone()
    return f"sec {r[0]} '{(r[1] or '')[:40]}'" if r else "sec -"


def cmd_eq(a):
    c = con()
    for r in c.execute("SELECT eq_id, number, label, char_start, char_end FROM equations WHERE paper_id=? "
                       "AND number=?", (a.paper, a.number)):
        print(f"eq_id {r[0]} ({r[1]}) label {r[2]} {where(a.paper, r[3])} .. {where(a.paper, r[4] - 1)} "
              f"{section_of(c, a.paper, r[3])} flat {r[3]}-{r[4]}")


def cmd_fts(a):
    c = con()
    kinds = a.kinds.split(",")
    q = ("SELECT c.chunk_id, c.paper_id, c.kind, c.char_start, snippet(chunks_fts, 0, '[', ']', ' .. ', 18) "
         "FROM chunks_fts JOIN chunks c ON c.chunk_id = chunks_fts.rowid WHERE chunks_fts MATCH ? "
         + ("AND c.paper_id = ? " if a.paper else "")
         + f"AND c.kind IN ({','.join('?' * len(kinds))}) ORDER BY bm25(chunks_fts) LIMIT ?")
    args = [a.query] + ([a.paper] if a.paper else []) + kinds + [a.k]
    for r in c.execute(q, args):
        print(f"{r[1]} chunk {r[0]} {r[2]} {where(r[1], r[3])} {section_of(c, r[1], r[3])} | {r[4][:160]}")


def cmd_grep(a):
    p = os.path.join(DATA, "build", "tex", a.paper.replace("/", "_"), "flat.tex")
    flat = open(p, encoding="utf-8", errors="replace").read()
    c = con()
    for m in re.finditer(a.regex, flat):
        s = max(0, m.start() - 60)
        ctx = flat[s:m.end() + 60].replace("\n", " ")
        print(f"{a.paper} {where(a.paper, m.start())} {section_of(c, a.paper, m.start())} | {ctx[:160]}")


def cmd_bib(a):
    c = con()
    rx = re.compile(a.regex, re.I)
    n = 0
    for r in c.execute("SELECT paper_id, cite_key, target_arxiv, target_doi, eprint, title, raw FROM bib_entries"):
        if rx.search(r[6] or "") or rx.search(r[5] or ""):
            raw = re.sub(r"\s+", " ", r[6] or "")
            print(f"{r[0]} key={r[1]} arxiv={r[2]} doi={r[3]} eprint={r[4]} | {raw[:160]}")
            n += 1
            if n >= a.k:
                break


def cmd_cites(a):
    c = con()
    for r in c.execute("SELECT citing, cite_key, char_start, substr(context,1,160) FROM citations WHERE cited_arxiv=?",
                       (a.id,)):
        print(f"{r[0]} key={r[1]} {where(r[0], r[2]) if r[2] is not None else '?'} | {r[3]}")


def cmd_title(a):
    c = con()
    rx = re.compile(a.regex, re.I)
    for r in c.execute("SELECT paper_id, grp, title FROM papers"):
        if rx.search(r[2] or ""):
            print(f"{r[0]} {r[1]} | {r[2][:140]}")


def main():
    ap = argparse.ArgumentParser()
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("eq"); p.add_argument("paper"); p.add_argument("number")
    p = s.add_parser("fts"); p.add_argument("query"); p.add_argument("--paper"); p.add_argument("-k", type=int, default=10)
    p.add_argument("--kinds", default="abstract,body,appendix,caption,footnote")
    p = s.add_parser("grep"); p.add_argument("paper"); p.add_argument("regex")
    p = s.add_parser("bib"); p.add_argument("regex"); p.add_argument("-k", type=int, default=20)
    p = s.add_parser("cites"); p.add_argument("id")
    p = s.add_parser("title"); p.add_argument("regex")
    a = ap.parse_args()
    {"eq": cmd_eq, "fts": cmd_fts, "grep": cmd_grep, "bib": cmd_bib, "cites": cmd_cites, "title": cmd_title}[a.cmd](a)


if __name__ == "__main__":
    main()
