"""Ingestion of papers from a stored PDF (brief 12.4 step 6), for the e-prints whose TeX is
unusable: an e-print that is a PDF, gzipped PostScript, or a tar of PostScript files.

    python -I -m kbtool.pdf_ingest [--id ID ...] [--all] [--dry-run] [--vocab FILE] [--out DIR]

`--all` takes every paper of the store (manifest and additions) whose download is a PDF, or
whose e-print holds no TeX file while a checked PDF exists. For each paper: choose and check
the PDF (kbtool.pdf_reader.choose_pdf), pdftotext in an empty directory under --out, repairs,
structure; then, inside the writer lock, the build files (kb-data/build/tex/<key>/flat.tex is
the repaired text; pdf_raw.txt the text as pdftotext gave it; pdf_edits.json every repair with
its offsets; doc.json) and the rows of papers (parse_status 'pdf', source_kind 'pdf'),
sections, chunks, figures, bib_entries and citations through papers_ingest.write_paper. The
metadata step (kbtool.meta_papers load --id) runs for the paper afterwards. A per-paper summary
without paper text is written to --out/pdf_ingest.json.

Afterwards (not done here): `kb resolve-bib`, `kb embed`, `kb snapshot`.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time

from . import db as _db
from . import inventory as _inv
from . import meta_manifest as MM
from . import meta_papers as MP
from . import papers_ingest as PI
from . import pdf_reader as P
from .lock import writer_lock
from .paths import layout

TOOL = "kbtool pdf-ingest 1"


def _has_tex(src):
    for root, _dirs, files in os.walk(src):
        for f in files:
            if f.lower().endswith((".tex", ".ltx", ".latex")):
                return True
            if f == "main.tex":
                return True
    return False


def postscript_only(lay, pid, chk):
    """True when the e-print holds no usable TeX: gzipped PostScript stored as src/main.tex, or
    a tree without any .tex file."""
    if chk.get("status") not in ("ok", "problem") or not chk.get("current"):
        return False
    src = os.path.join(lay.raw_arxiv, chk["key"], chk["current"], "src")
    main = os.path.join(src, "main.tex")
    if os.path.isfile(main):
        with open(main, "rb") as f:
            head = f.read(4096)
        if head.startswith(b"%!PS") or b"%!PS-Adobe" in head[:200]:
            return True
    return os.path.isdir(src) and not _has_tex(src)


def select(lay, ids=None, take_all=False):
    man = {r["id"]: r for r in MM.load_full_manifest()}
    if ids:
        want = list(ids)
    elif take_all:
        want = sorted(set(man) | set(_inv.key_to_id(k) for k in os.listdir(lay.raw_arxiv)))
    else:
        want = []
    out = []
    for pid in want:
        chk = _inv.check_paper(lay, pid, man.get(pid))
        reason = None
        if chk.get("source_kind") == "pdf" or chk.get("sniffed_kind") == "pdf":
            reason = "e-print is a PDF"
        elif postscript_only(lay, pid, chk):
            reason = "e-print holds no TeX (PostScript)"
        if reason or ids:
            out.append({"id": pid, "row": man.get(pid), "chk": chk, "reason": reason or "requested by --id"})
    return out


def load_vocab(lay, path):
    if path and os.path.exists(path):
        with open(path) as f:
            return json.load(f), "cache " + path
    con = _db.connect_ro(lay.db_work)
    try:
        v = P.vocab_from_db(con)
    finally:
        con.close()
    if path:
        with open(path, "w") as f:
            json.dump(v, f)
    return v, "built from kb.sqlite"


def ingest_one(lay, item, vocab, workdir, dry_run=False):
    pid, row = item["id"], item["row"] or {}
    rep = {"id": pid, "reason": item["reason"], "group": row.get("group"), "priority": row.get("priority")}
    good, checks = P.choose_pdf(lay, pid)
    rep["pdf_checks"] = [{k: c.get(k) for k in ("kind", "version", "bytes", "sha256", "ok", "problems")}
                         for c in checks]
    if not good:
        rep["status"] = "no usable PDF"
        return rep
    t0 = time.time()
    raw = P.extract_text(good["path"], workdir)
    text, edits, counts = P.repair(raw, vocab)
    o0, n0 = P.oov_fraction(raw, vocab)
    o1, n1 = P.oov_fraction(text, vocab)
    api = MP.load_api(lay, pid)
    doc = P.analyse_text(text, api)
    vdir = os.path.dirname(good["path"]) if good["kind"] == "source.pdf" else \
        os.path.dirname(os.path.dirname(good["path"]))
    doc["main"] = {"main": os.path.relpath(good["path"], vdir), "reason": item["reason"], "pdf": good["kind"]}
    doc["parse_seconds"] = round(time.time() - t0, 3)
    doc["quality"].update({"oov_fraction_raw": round(o0, 5) if o0 is not None else None,
                           "oov_fraction_repaired": round(o1, 5) if o1 is not None else None,
                           "alpha_tokens": n1, "repairs": counts})
    rep.update({"status": "pdf", "pdf": {k: good[k] for k in ("kind", "version", "bytes", "sha256")},
                "pages": len(doc["pages"]), "chars": len(text), "repairs": counts,
                "oov_raw": doc["quality"]["oov_fraction_raw"], "oov_repaired": doc["quality"]["oov_fraction_repaired"],
                "abstract_similarity": doc["quality"]["abstract_similarity_to_metadata"],
                "sections": len(doc["sections"]),
                "section_kinds": sorted({s["kind"] for s in doc["sections"]}),
                "chunks": {k: sum(1 for c in doc["chunks"] if c["kind"] == k)
                           for k in sorted({c["kind"] for c in doc["chunks"]})},
                "figures": len(doc["figures"]), "bib_entries": len(doc["bib"]["entries"]),
                "bib_with_arxiv": sum(1 for e in doc["bib"]["entries"] if e["arxiv"]),
                "bib_with_doi": sum(1 for e in doc["bib"]["entries"] if e["doi"]),
                "citations": sum(len(c["keys"]) for c in doc["cites"]), "score": doc["quality"]["score"],
                "metadata": bool(api)})
    if dry_run:
        return rep
    chk = {"group": row.get("group"), "priority": row.get("priority"), "version": good["version"],
           "source_kind": "pdf", "sha256": good["sha256"]}
    flat_sha = hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()
    with writer_lock(lay, what=f"pdf-ingest {pid}"):
        con = _db.connect_rw(lay.db_work)
        try:
            con.execute("BEGIN")
            PI.write_build(lay, pid, doc, text, None)
            d = PI.build_dir(lay, pid)
            for name, body in (("pdf_raw.txt", raw), ("pdf_edits.json", json.dumps(edits, ensure_ascii=False))):
                tmp = os.path.join(d, f".{name}.tmp-{os.getpid()}")
                with open(tmp, "w", encoding="utf-8", errors="surrogatepass") as f:
                    f.write(body)
                os.replace(tmp, os.path.join(d, name))
            PI.write_paper(con, pid, chk, doc, flat_sha, "pdf")
            con.execute("UPDATE papers SET tool_version=? WHERE paper_id=?", (TOOL + " / " + P.TOOL, pid))
            _db.log(con, "ingest-pdf", pid, "pdf", json.dumps({k: rep[k] for k in (
                "pages", "sections", "chunks", "bib_entries", "citations", "score", "repairs", "oov_raw",
                "oov_repaired", "abstract_similarity")}))
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    rows, summary, _ = MP.load(lay, ids=[pid])
    rep["meta_loaded"] = summary
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m kbtool.pdf_ingest")
    ap.add_argument("--id", action="append", help="paper id (repeatable)")
    ap.add_argument("--all", action="store_true", help="every paper of the store without usable TeX")
    ap.add_argument("--dry-run", action="store_true", help="read and analyse, write nothing to kb-data")
    ap.add_argument("--vocab", help="cache file of the corpus vocabulary (JSON); built from kb.sqlite if absent")
    ap.add_argument("--out", help="output directory (default $NRPIC_RUN_DIR)")
    a = ap.parse_args(argv)
    if not a.id and not a.all:
        ap.error("--id or --all")
    out = a.out or os.environ.get("NRPIC_RUN_DIR")
    if not out:
        ap.error("--out or $NRPIC_RUN_DIR")
    os.makedirs(out, exist_ok=True)
    workdir = os.path.join(out, "pdftotext_cwd")
    os.makedirs(workdir, exist_ok=True)
    lay = layout()
    items = select(lay, ids=a.id, take_all=a.all)
    vocab, vsrc = load_vocab(lay, a.vocab or os.path.join(out, "vocab.json"))
    reports = []
    for it in items:
        try:
            r = ingest_one(lay, it, vocab, workdir, dry_run=a.dry_run)
        except Exception as e:                                  # recorded, never fatal for the list
            r = {"id": it["id"], "status": "failed", "error": f"{type(e).__name__}: {e}"[:500]}
        reports.append(r)
        print(json.dumps({k: r.get(k) for k in ("id", "status", "pages", "sections", "bib_entries", "score",
                                                 "oov_raw", "oov_repaired", "abstract_similarity")}))
    with open(os.path.join(out, "pdf_ingest.json"), "w") as f:
        json.dump({"tool": TOOL, "reader": P.TOOL, "vocab": {"source": vsrc, "words": len(vocab)},
                   "dry_run": a.dry_run, "papers": reports}, f, indent=1)
    return 0 if all(r.get("status") == "pdf" for r in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
