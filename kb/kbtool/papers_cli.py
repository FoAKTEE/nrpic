"""Subcommands of stages K2-K3 (papers): `kb ingest arxiv`, `kb resolve-bib`, `kb frontier`,
`kb cites`, `kb export`, the text views of `kb show`, and the paper counts of `kb status`.

`kb ingest arxiv` needs pylatexenc for the plain-text conversion; when the command runs under
the system python3 without it and kb/.venv exists, it re-executes itself under
kb/.venv/bin/python -I (the converter is recorded per paper either way).
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

from . import bib_resolve as R
from . import brief as _brief
from . import db as _db
from . import inventory as _inv
from .lock import writer_lock
from .paths import KB_DIR, kb_manifest_dir, layout

CLAIMS = ("resolve-bib", "frontier", "cites", "export")   # stub names this module replaces in kbtool.cli
VENV_PY = os.path.join(KB_DIR, ".venv", "bin", "python")
MAX_JOBS = 16                                             # CLAUDE.md: at most 16 cores per session


def _ensure_converter():
    from . import tex_text as T
    if T.LatexNodes2Text is None and os.path.exists(VENV_PY) and os.environ.get("KB_NO_REEXEC") != "1" \
            and os.path.realpath(sys.executable) != os.path.realpath(VENV_PY):
        kb_bin = os.path.join(KB_DIR, "bin", "kb")
        sys.stdout.flush()
        os.execv(VENV_PY, [VENV_PY, "-I", kb_bin] + sys.argv[1:])


def _manifest_rows():
    return {r["id"]: r for r in _brief.load_arxiv_manifest(os.path.join(kb_manifest_dir(), "arxiv.tsv"))}


def _analyse(args):
    from . import papers_ingest as P
    lay, pid, row = args
    return P.analyse(lay, pid, row)


def select_ids(lay, a, rows):
    """Ids to ingest, in priority order 3, 2, 1, then manifest order; extras (not in the
    manifest) only with --id or --extras."""
    store = []
    if os.path.isdir(lay.meta_arxiv):
        store = sorted(_inv.key_to_id(n[:-5]) for n in os.listdir(lay.meta_arxiv) if n.endswith(".json"))
    order = {pid: (-r["priority"], k) for k, (pid, r) in enumerate(rows.items())}
    if a.id:
        ids = [i.replace("arXiv:", "") for i in a.id]
    else:
        ids = [p for p in store if p in rows]
        if a.extras:
            ids += [p for p in store if p not in rows]
        if a.priority:
            ids = [p for p in ids if p in rows and rows[p]["priority"] in a.priority]
        elif not (a.all or a.new):
            raise SystemExit("kb ingest arxiv: give --id, --priority, --all or --new")
    ids = sorted(set(ids), key=lambda p: order.get(p, (0, 10 ** 6)))
    if a.new:
        con = _db.connect_ro(lay.db_work)
        try:
            have = {r[0]: r[1] for r in con.execute("SELECT paper_id, sha256 FROM papers")}
        finally:
            con.close()
        ids = [p for p in ids if p not in have]
    if a.limit:
        ids = ids[:a.limit]
    return ids


def cmd_ingest_arxiv(argv, data_root=None):
    p = argparse.ArgumentParser(prog="kb ingest arxiv")
    p.add_argument("--id", action="append", help="arXiv id (repeatable)")
    p.add_argument("--priority", type=int, action="append", choices=(1, 2, 3))
    p.add_argument("--all", action="store_true", help="every manifest paper in the store")
    p.add_argument("--new", action="store_true", help="only papers not yet in the papers table")
    p.add_argument("--extras", action="store_true", help="also store entries not in the manifest")
    p.add_argument("--jobs", type=int, default=8, help="parallel parsers (writes stay serial); at most 16")
    p.add_argument("--limit", type=int)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    _ensure_converter()
    from . import papers_ingest as P
    from . import tex_text as T
    lay = layout(data_root)
    _db.init_db(lay)
    rows = _manifest_rows()
    ids = select_ids(lay, a, rows)
    jobs = max(1, min(a.jobs, MAX_JOBS))
    t0 = time.time()
    print(f"# kb ingest arxiv: {len(ids)} papers, {jobs} parser processes, converter {T.CONVERTER}", flush=True)
    summary = {}
    work = [(lay, pid, rows.get(pid)) for pid in ids]
    if jobs == 1:
        results = map(_analyse, work)
    else:
        ex = ProcessPoolExecutor(max_workers=jobs)
        results = ex.map(_analyse, work, chunksize=1)
    for k, res in enumerate(results, start=1):
        status = P.store(lay, res)
        doc = res[2] or {}
        summary[res[0]] = status
        q = (doc.get("quality") or {}).get("score")
        print(f"{k:4d}/{len(ids)} {res[0]:18s} {status:16s} score {q if q is not None else '-'} "
              f"sec {len(doc.get('sections', []))} eq {len(doc.get('equations', []))} "
              f"chunks {len(doc.get('chunks', []))} bib {len((doc.get('bib') or {}).get('entries', []))} "
              f"({(doc.get('bib') or {}).get('source')}) {doc.get('error') or ''}", flush=True)
    if jobs != 1:
        ex.shutdown()
    with writer_lock(lay, what="resolve-bib"):
        con = _db.connect_rw(lay.db_work)
        try:
            r = R.resolve_corpus(con)
            _db.log(con, "resolve-bib", "all", "ok", json.dumps(r))
            con.commit()
        finally:
            con.close()
    counts = {}
    for s in summary.values():
        counts[s] = counts.get(s, 0) + 1
    print(f"# done in {time.time() - t0:.1f} s: {json.dumps(counts, sort_keys=True)}; corpus resolution {json.dumps(r)}")
    return 0 if not counts.get("failed") else 1


def cmd_resolve_bib(a):
    lay = layout(a.data_root)
    with writer_lock(lay, what="resolve-bib"):
        con = _db.connect_rw(lay.db_work)
        try:
            r = R.resolve_corpus(con)
            _db.log(con, "resolve-bib", a.paper or "all", "ok", json.dumps(r))
            con.commit()
            st = R.bib_stats(con)
        finally:
            con.close()
    print(json.dumps({"resolution": r, "stats": st}, indent=1))
    return 0


def _ro(a):
    lay = layout(a.data_root)
    path = _db.open_for_read(lay, getattr(a, "db", None) or (lay.db_work if getattr(a, "work", False) else None))
    if not os.path.exists(path):
        raise SystemExit(f"no database at {path} (run kb init and kb ingest arxiv)")
    return _db.connect_ro(path)


def cmd_frontier(a):
    con = _ro(a)
    try:
        rows = R.frontier(con, a.n, manifest=_manifest_rows())
    finally:
        con.close()
    if a.json:
        print(json.dumps(rows, indent=1))
    else:
        for r in rows:
            print(f"{r['cited_by']:4d}  {r['arxiv']:18s} {'manifest:' + str(r['download_status']) if r['in_manifest'] else 'not in manifest':22s} "
                  f"{(r['title_in_bib'] or '')[:80]}")
    return 0


def cmd_cites(a):
    con = _ro(a)
    try:
        rows = R.cites(con, a.paper_id.replace("arXiv:", ""), "in" if a.incoming else "out", a.context)
    finally:
        con.close()
    print(json.dumps(rows, indent=1, ensure_ascii=False))
    return 0


def cmd_export(a):
    con = _ro(a)
    pid = a.paper_id.replace("arXiv:", "")
    try:
        p = con.execute("SELECT title, abstract, version FROM papers WHERE paper_id = ?", (pid,)).fetchone()
        if not p:
            print(f"{pid}: not ingested", file=sys.stderr)
            return 1
        secs = {r[0]: r[1:] for r in con.execute("SELECT section_id, number, title, level FROM sections "
                                                 "WHERE paper_id = ?", (pid,))}
        out = [f"# {p[0]} (arXiv:{pid}{p[2] or ''})", "", "## Abstract", "", p[1] or "", ""]
        last = None
        for sid, kind, text in con.execute("SELECT section_id, kind, text FROM chunks WHERE paper_id = ? AND kind IN "
                                           "('body', 'appendix') ORDER BY char_start", (pid,)):
            if sid != last and sid in secs:
                num, title, level = secs[sid]
                out += ["", "#" * (1 + min(level or 1, 4)) + f" {num + ' ' if num else ''}{title}", ""]
                last = sid
            out.append(text)
            out.append("")
    finally:
        con.close()
    text = "\n".join(out)
    if a.max_chars:
        text = text[:a.max_chars]
    print(text)
    return 0


def show_views(a):
    """`kb show ID --abstract | --section N | --eq LABEL | --fig N` (K2)."""
    try:
        con = _ro(a)
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 1
    pid = a.paper_id.replace("arXiv:", "")
    try:
        if a.abstract:
            r = con.execute("SELECT abstract FROM papers WHERE paper_id = ?", (pid,)).fetchone()
            out = r[0] if r else None
        elif a.section:
            r = con.execute("SELECT section_id, title, char_start, char_end FROM sections WHERE paper_id = ? AND "
                            "(number = ? OR label = ?)", (pid, a.section, a.section)).fetchone()
            if r:
                texts = [t for (t,) in con.execute(
                    "SELECT text FROM chunks WHERE paper_id = ? AND kind IN ('body','appendix') AND char_start >= ? "
                    "AND char_start < ? ORDER BY char_start", (pid, r[2], r[3]))]
                out = f"{a.section} {r[1]}  [chars {r[2]}-{r[3]} of flat.tex]\n\n" + "\n\n".join(texts)
            else:
                out = None
        elif a.eq:
            r = con.execute("SELECT number, label, env, tex_raw, context, char_start, char_end FROM equations WHERE "
                            "paper_id = ? AND (label = ? OR number = ?)", (pid, a.eq, a.eq)).fetchone()
            out = (f"({r[0]}) label {r[1]} env {r[2]}  [chars {r[5]}-{r[6]} of flat.tex]\n{r[3]}\n\ncontext: {r[4]}"
                   if r else None)
        else:
            r = con.execute("SELECT kind, number, label, caption, files_json FROM figures WHERE paper_id = ? AND "
                            "(number = ? OR label = ?) ORDER BY kind = 'table'", (pid, a.fig, a.fig)).fetchone()
            out = f"{r[0]} {r[1]} label {r[2]} files {r[4]}\n{r[3]}" if r else None
    finally:
        con.close()
    if out is None:
        print(f"{pid}: nothing found", file=sys.stderr)
        return 1
    print(out[:a.max_chars] if a.max_chars else out)
    return 0


def status_counts(con):
    """Paper counts for `kb status` (K2-K3)."""
    st = {}
    try:
        st["papers_by_parse_status"] = dict(con.execute(
            "SELECT coalesce(parse_status,'?'), count(*) FROM papers GROUP BY 1").fetchall())
        st["papers_by_priority"] = {str(k): v for k, v in con.execute(
            "SELECT priority, count(*) FROM papers GROUP BY 1").fetchall()}
        st["parse_failures"] = [r[0] for r in con.execute(
            "SELECT paper_id FROM papers WHERE parse_status = 'failed' ORDER BY paper_id")]
        st["parse_review"] = [r[0] for r in con.execute(
            "SELECT paper_id FROM papers WHERE parse_status = 'review' ORDER BY parse_score")]
        r = con.execute("SELECT count(*), avg(parse_score), min(parse_score) FROM papers").fetchone()
        st["parse_score_mean"] = round(r[1], 4) if r[1] is not None else None
        st["rows_k2"] = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                         for t in ("sections", "chunks", "equations", "figures")}
        st["chunks_by_kind"] = dict(con.execute("SELECT kind, count(*) FROM chunks GROUP BY kind").fetchall())
        st["equations_labelled"] = con.execute("SELECT count(*) FROM equations WHERE label IS NOT NULL").fetchone()[0]
        b = R.bib_stats(con)
        st["bib"] = b
        st["bib_resolution_rate"] = round(b["with_arxiv"] / b["bib_entries"], 4) if b["bib_entries"] else None
        st["bib_identifier_rate"] = (round((b["with_arxiv"] + b["doi_only"]) / b["bib_entries"], 4)
                                     if b["bib_entries"] else None)
        st["edges_in_corpus_fraction"] = round(b["edges_in_corpus"] / b["edges"], 4) if b["edges"] else None
    except Exception as e:                                  # schema older than migration 0003
        st["papers_error"] = str(e)
    return st


def register(sub):
    s = sub.add_parser("resolve-bib", help="K3: resolve bibliography entries against the corpus; citation edges")
    s.add_argument("--paper")
    s.set_defaults(fn=cmd_resolve_bib)
    for name, fn, helptext in (("frontier", cmd_frontier, "K3: works cited often by the corpus but absent from it"),
                               ("cites", cmd_cites, "K3: citation graph of one paper"),
                               ("export", cmd_export, "K2: flattened text with section numbers (markdown)")):
        s = sub.add_parser(name, help=helptext)
        s.add_argument("--db", help="database file (default db/current, else kb.sqlite)")
        s.add_argument("--work", action="store_true", help="read the working database kb.sqlite")
        if name == "frontier":
            s.add_argument("-n", type=int, default=50)
            s.add_argument("--json", action="store_true")
        else:
            s.add_argument("paper_id")
        if name == "cites":
            g = s.add_mutually_exclusive_group()
            g.add_argument("--in", dest="incoming", action="store_true")
            g.add_argument("--out", dest="outgoing", action="store_true")
            s.add_argument("--context", action="store_true")
        if name == "export":
            s.add_argument("--format", default="md", choices=("md",))
            s.add_argument("--max-chars", type=int)
        s.set_defaults(fn=fn)
