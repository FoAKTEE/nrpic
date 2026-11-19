"""`kb ingest arxiv` (brief 12.4 K2 and 12.5 K3 for one paper at a time).

For each paper whose download is verified (kbtool.inventory.check_paper says ok): find the
main file, flatten with a source map, strip comments, collect macros, extract the structure,
convert to plain text, chunk, normalise equations, score the parse; then parse the
bibliography and record the citations. Results go to
  kb-data/build/tex/<id_>/{flat.tex, doc.json, sourcemap.json}
and to the tables papers, sections, chunks(+fts), equations(+fts), figures, bib_entries,
citations of kb.sqlite. Parsing runs outside the writer lock; the writes of one paper run
inside it, in one transaction. Re-ingesting a paper replaces its rows (new row ids).
"""
import hashlib
import json
import os
import re
import subprocess
import time
import traceback

from . import __version__
from . import bib_parse as B
from . import db as _db
from . import inventory as _inv
from . import tex_files as F
from . import tex_macros as M
from . import tex_structure as S
from . import tex_text as T
from .lock import writer_lock

TOOL = f"kbtool {__version__} papers-k2k3 1"
REVIEW_THRESHOLD = 0.75          # parse_score below this -> parse_status 'review' [JUDGEMENT]
FRONT_MATTER_RE = re.compile(r"\\(title|author|affiliation|affil|email|thanks|address|altaffiliation|"
                             r"collaboration|date|keywords|pacs|preprint|correspondingauthor|orcid|"
                             r"institute|inst|received|accepted|journal|volume|pubyear|pagerange|"
                             r"shorttitle|shortauthors|submitjournal)(?![A-Za-z@])\*?")


def _sha(text):
    return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()


def _mask(flat, spans):
    """Copy of flat with the given spans blanked (newlines kept), so offsets stay valid."""
    chars = list(flat)
    for a, b in spans:
        for k in range(max(0, a), min(len(chars), b)):
            if chars[k] != "\n":
                chars[k] = " "
    return "".join(chars)


def front_matter_spans(flat, start, end):
    out = []
    for m in FRONT_MATTER_RE.finditer(flat, start, end):
        a = S.command_args(flat, m.end(), 1, 1)
        if a:
            out.append((m.start(), a[2]))
    for m in re.finditer(r"\\maketitle(?![A-Za-z@])", flat[start:end]):
        out.append((start + m.start(), start + m.end()))
    return out


def quality(st, words_body, unresolved_frac, n_unresolved_inputs):
    comp = {
        "title": 1.0 if st["title"] else 0.0,
        "abstract": 1.0 if st["abstract_words"] >= 20 else 0.0,
        "sections": min(1.0, st["n_sections"] / 3.0),
        "equations": min(1.0, st["n_equations"] / 5.0),
        "macros_resolved": 1.0 - min(1.0, 4.0 * unresolved_frac),
        "inputs_resolved": 1.0 if n_unresolved_inputs == 0 else 0.5,
        "body_text": min(1.0, words_body / 1000.0),
    }
    w = {"title": .15, "abstract": .15, "sections": .15, "equations": .10, "macros_resolved": .15,
         "inputs_resolved": .10, "body_text": .20}
    score = sum(w[k] * comp[k] for k in w)
    return round(score, 4), comp


def parse_tex(src_root):
    """Everything K2 and K3 derive from one extracted source tree. Returns the doc dict
    (with 'flat', 'source_map' objects that the writer stores separately)."""
    t0 = time.time()
    mainf = F.find_main(src_root)
    if not mainf["main"]:
        raise ValueError("no TeX file in the source")
    fl = F.flatten(src_root, mainf["main"])
    flat = fl["flat"]
    macros = M.collect(flat)
    st = S.extract(flat, macros)
    labels = st["labels"]
    conv_cache = {}

    def conv(tex):
        r = conv_cache.get(tex)
        if r is None:
            r = T.to_text(tex, labels, macros)
            if len(conv_cache) < 20000:
                conv_cache[tex] = r
        return r

    body_start, body_end = st["body_start"], st["body_end"]
    bib_at = st["bibliography_at"] if st["bibliography_at"] is not None else body_end
    excluded = [(f["start"], f["end"]) for f in st["figures"]]
    excluded += [(f["start"], f["end"]) for f in st["footnotes"]]
    if st["abstract"]:
        excluded.append((st["abstract"]["start"], st["abstract"]["end"]))
    excluded += front_matter_spans(flat, body_start, bib_at)
    excluded.append((bib_at, body_end))
    masked = _mask(flat, excluded)
    protected = [(m["start"], m["end"]) for m in st["math_spans"] if m["kind"] == "display"]

    # ---- chunks by section
    chunks = []
    secs = st["sections"]
    first_sec = secs[0]["start"] if secs else bib_at
    regions = [(None, body_start, min(first_sec, bib_at))]
    for k, s in enumerate(secs):
        regions.append((k, s["cmd_end"], min(s["own_end"], bib_at)))
    words_body = 0
    for k, a, b in regions:
        if b <= a:
            continue
        kind = "appendix" if (k is not None and secs[k]["appendix"]) or \
            (st["appendix_at"] is not None and a > st["appendix_at"]) else "body"
        for c in T.chunk_section(masked, a, b, protected, conv, kind):
            c["section"] = k
            c["tex"] = flat[c["start"]:c["end"]]
            chunks.append(c)
            words_body += c["n_tokens"]
    abstract_text = None
    if st["abstract"]:
        abstract_text = conv(st["abstract"]["tex"])
        chunks.insert(0, {"kind": "abstract", "start": st["abstract"]["inner_start"],
                          "end": st["abstract"]["inner_end"], "text": abstract_text,
                          "tex": st["abstract"]["tex"], "n_tokens": T.ntok(abstract_text), "section": None})
    for f in st["figures"]:
        if f["caption_tex"]:
            txt = conv(f["caption_tex"])
            f["caption"] = txt
            chunks.append({"kind": "caption", "start": f["caption_start"], "end": f["caption_end"], "text": txt,
                           "tex": f["caption_tex"], "n_tokens": T.ntok(txt), "section": f["section"]})
        else:
            f["caption"] = None
    for fn in st["footnotes"]:
        txt = conv(fn["tex"])
        chunks.append({"kind": "footnote", "start": fn["start"], "end": fn["end"], "text": txt, "tex": fn["tex"],
                       "n_tokens": T.ntok(txt), "section": fn["section"]})
    for cb in F.group_comments(fl["comments"]):
        txt = cb["text"].strip()
        if len(txt) < 3:
            continue
        chunks.append({"kind": "comment", "start": None, "end": None, "text": txt,
                       "tex": f"%% {cb['file']}:{cb['line_start']}-{cb['line_end']}\n" + cb["text"],
                       "n_tokens": T.ntok(txt), "section": None})

    # ---- equations
    eqs = []
    for e in st["equations"]:
        raw = flat[e["start"]:e["end"]]
        inner = flat[e["inner_start"]:e["inner_end"]]
        norm = T.normalize_equation(inner, macros)
        lo = secs[e["section"]]["start"] if e["section"] is not None else body_start
        before, after = T.context(masked, e["start"], e["end"], conv, lo=lo, hi=bib_at)
        eqs.append({"env": e["env"], "label": e["labels"][0] if e["labels"] else None, "labels": e["labels"],
                    "number": e["number"], "tex_raw": raw, "tex_norm": norm, "symbols": T.symbols(norm),
                    "context": (before + " [EQ] " + after).strip(), "start": e["start"], "end": e["end"],
                    "section": e["section"]})

    # ---- citations (context sentence around each \cite)
    cites = []
    for c in st["cites"]:
        if c["nocite"]:
            continue
        lo = secs[c["section"]]["start"] if c["section"] is not None else body_start
        w0 = max(lo, c["start"] - 800)
        w1 = min(bib_at if c["start"] < bib_at else body_end, c["end"] + 800)
        marked = masked[w0:c["start"]] + "CITEMARK" + masked[c["end"]:w1]
        txt = conv(marked)
        sent = next((s for s in T.sentences(txt) if "CITEMARK" in s), "")
        cites.append({**c, "context": sent.replace("CITEMARK", "[cit.]").strip()[:1200]})

    # ---- title, authors, quality
    title = conv(st["title"]["tex"]) if st["title"] else ""
    title = re.sub(r"\s+", " ", title).strip()
    authors = []
    for a in st["authors"]:
        t = re.sub(r"\s+", " ", conv(a["tex"])).strip()
        if t:
            authors.append(t[:300])
    used = set()
    total_occ, unknown_occ = 0, 0
    known = T.known_macros() | set(macros)
    unknown_names = {}
    for w in M.control_words(masked[body_start:bib_at]):
        total_occ += 1
        used.add(w)
        if w not in known and "@" not in w:
            unknown_occ += 1
            unknown_names[w] = unknown_names.get(w, 0) + 1
    unresolved_frac = unknown_occ / total_occ if total_occ else 0.0
    counts = {"title": bool(title), "abstract_words": T.ntok(abstract_text or ""),
              "n_sections": sum(1 for s in secs if s["number"]), "n_equations": len(eqs)}
    score, comp = quality(counts, words_body, unresolved_frac, len(fl["unresolved"]))
    doc = {
        "main": mainf, "files": fl["files"], "unresolved_inputs": fl["unresolved"], "flatten_notes": fl["notes"],
        "class": st["class"], "class_options": st["class_options"], "revtex": st["revtex"],
        "numberwithin_section": st["numberwithin_section"],
        "title": title, "authors": authors, "abstract": abstract_text,
        "sections": [{"level": s["level"], "number": s["number"], "title": re.sub(r"\s+", " ", conv(s["title_tex"])),
                      "label": s["label"], "start": s["start"], "end": s["end"], "parent": s["parent"],
                      "appendix": s["appendix"], "starred": s["starred"]} for s in secs],
        "equations": eqs, "figures": st["figures"], "footnotes": len(st["footnotes"]), "cites": cites,
        "labels": st["labels"], "chunks": chunks, "env_aliases": st["aliases"],
        "macros": {k: {"nargs": v["nargs"], "body": v["body"][:300], "kind": v["kind"]} for k, v in macros.items()},
        "quality": {"score": score, "components": comp, "unresolved_macro_fraction": round(unresolved_frac, 5),
                    "unresolved_macros_top": sorted(unknown_names.items(), key=lambda x: -x[1])[:25],
                    "body_words": words_body, "abstract_similarity_to_metadata": None,
                    "abstract_similarity_note": "no arXiv/INSPIRE metadata yet (README Request 2)",
                    "threshold": REVIEW_THRESHOLD},
        "converter": T.CONVERTER, "parse_seconds": None,
        "bibliography_files": st["bibliography_files"], "bibliography_at": st["bibliography_at"],
        "appendix_at": st["appendix_at"],
    }
    bib = B.bibliography(src_root, mainf["main"], flat, st)
    doc["bib"] = {"source": bib["source"], "files": bib["files"], "notes": bib["notes"],
                  "entries": [{k: e.get(k) for k in ("cite_key", "raw", "arxiv", "doi", "eprint", "n_arxiv_ids",
                                                      "title")} for e in bib["entries"]]}
    doc["parse_seconds"] = round(time.time() - t0, 3)
    return doc, flat, fl["source_map"]


def parse_pdf(pdf_path, timeout=120):
    """PDF-only paper: text by pdftotext (poppler), run from outside the tree on a copy-free
    path, with a timeout; no equations (brief 12.4 step 6)."""
    out = subprocess.run(["pdftotext", "-enc", "UTF-8", "-nopgbrk", pdf_path, "-"], capture_output=True,
                         timeout=timeout, cwd="/", stdin=subprocess.DEVNULL)
    text = out.stdout.decode("utf-8", "replace")
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur, pos = [], [], 0
    offs = []
    for p in paras:
        k = text.find(p, pos)
        offs.append((k, k + len(p)))
        pos = k + len(p)
    for (a, b), p in zip(offs, paras):
        cur.append((a, b, p))
        if sum(T.ntok(x[2]) for x in cur) >= T.TARGET_MIN:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out_chunks = [{"kind": "body", "start": c[0][0], "end": c[-1][1], "text": " ".join(x[2] for x in c),
                   "tex": None, "n_tokens": sum(T.ntok(x[2]) for x in c), "section": None} for c in chunks]
    words = sum(c["n_tokens"] for c in out_chunks)
    doc = {"main": {"main": os.path.basename(pdf_path), "reason": "pdf only"}, "title": "", "authors": [],
           "abstract": None, "sections": [], "equations": [], "figures": [], "cites": [], "chunks": out_chunks,
           "labels": {}, "quality": {"score": round(0.2 * min(1.0, words / 1000.0), 4), "body_words": words},
           "converter": "pdftotext", "bib": {"source": None, "files": [], "notes": [], "entries": []}}
    return doc, text, None


# ------------------------------------------------------------------ database
def delete_paper(con, pid):
    con.execute("DELETE FROM citations WHERE citing = ?", (pid,))
    con.execute("DELETE FROM bib_entries WHERE paper_id = ?", (pid,))
    for cid, text in con.execute("SELECT chunk_id, text FROM chunks WHERE paper_id = ?", (pid,)).fetchall():
        con.execute("INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES('delete', ?, ?)", (cid, text))
    con.execute("DELETE FROM chunks WHERE paper_id = ?", (pid,))
    for eid, tn, ctx in con.execute("SELECT eq_id, tex_norm, context FROM equations WHERE paper_id = ?",
                                    (pid,)).fetchall():
        con.execute("INSERT INTO equations_fts(equations_fts, rowid, tex_norm, context) VALUES('delete', ?, ?, ?)",
                    (eid, tn, ctx))
    con.execute("DELETE FROM equations WHERE paper_id = ?", (pid,))
    con.execute("DELETE FROM figures WHERE paper_id = ?", (pid,))
    con.execute("DELETE FROM sections WHERE paper_id = ?", (pid,))


def write_paper(con, pid, chk, doc, flat_sha, status):
    """Rows of one paper; the caller holds the writer lock and commits."""
    delete_paper(con, pid)
    q = doc["quality"]
    parse_json = {"quality": q, "main": doc.get("main"), "converter": doc.get("converter"),
                  "unresolved_inputs": doc.get("unresolved_inputs", []), "class": doc.get("class"),
                  "bib_source": doc["bib"]["source"], "bib_files": doc["bib"]["files"],
                  "bib_notes": doc["bib"]["notes"], "flatten_notes": doc.get("flatten_notes", []),
                  "parse_seconds": doc.get("parse_seconds"), "error": doc.get("error")}
    con.execute("INSERT INTO papers(paper_id, title, authors_json, abstract, grp, priority, version, source_kind, "
                "main_tex, parse_status, parse_score, sha256, ingested_at, flat_sha256, title_source, parse_json, "
                "tool_version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(paper_id) DO UPDATE SET title=excluded.title, authors_json=excluded.authors_json, "
                "abstract=excluded.abstract, grp=excluded.grp, priority=excluded.priority, version=excluded.version, "
                "source_kind=excluded.source_kind, main_tex=excluded.main_tex, parse_status=excluded.parse_status, "
                "parse_score=excluded.parse_score, sha256=excluded.sha256, ingested_at=excluded.ingested_at, "
                "flat_sha256=excluded.flat_sha256, title_source=excluded.title_source, "
                "parse_json=excluded.parse_json, tool_version=excluded.tool_version",
                (pid, doc.get("title") or "", json.dumps(doc.get("authors", [])), doc.get("abstract"),
                 chk.get("group"), chk.get("priority"), chk.get("version"), chk.get("source_kind"),
                 (doc.get("main") or {}).get("main"), status, q.get("score"), chk.get("sha256"), _db.utcnow(),
                 flat_sha, "tex" if doc.get("title") else "none", json.dumps(parse_json), TOOL))
    sec_ids = []
    for s in doc["sections"]:
        parent = sec_ids[s["parent"]] if s["parent"] is not None else None
        cur = con.execute("INSERT INTO sections(paper_id, parent_id, level, number, title, label, char_start, char_end) "
                          "VALUES (?,?,?,?,?,?,?,?)", (pid, parent, s["level"], s["number"], s["title"], s["label"],
                                                      s["start"], s["end"]))
        sec_ids.append(cur.lastrowid)

    def sid(k):
        return sec_ids[k] if k is not None and k < len(sec_ids) else None

    chunk_rows = []
    for c in doc["chunks"]:
        cur = con.execute("INSERT INTO chunks(paper_id, section_id, kind, text, tex, n_tokens, char_start, char_end) "
                          "VALUES (?,?,?,?,?,?,?,?)", (pid, sid(c["section"]), c["kind"], c["text"], c["tex"],
                                                      c["n_tokens"], c["start"], c["end"]))
        con.execute("INSERT INTO chunks_fts(rowid, text) VALUES (?, ?)", (cur.lastrowid, c["text"]))
        chunk_rows.append((cur.lastrowid, c))
    for e in doc["equations"]:
        cur = con.execute("INSERT INTO equations(paper_id, section_id, env, label, number, tex_raw, tex_norm, "
                          "symbols_json, context, tags_json, char_start, char_end) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (pid, sid(e["section"]), e["env"], e["label"], e["number"], e["tex_raw"], e["tex_norm"],
                           json.dumps(e["symbols"]), e["context"], None, e["start"], e["end"]))
        con.execute("INSERT INTO equations_fts(rowid, tex_norm, context) VALUES (?, ?, ?)",
                    (cur.lastrowid, e["tex_norm"], e["context"]))
    for f in doc["figures"]:
        con.execute("INSERT INTO figures(paper_id, label, number, caption, files_json, kind, section_id, char_start, "
                    "char_end) VALUES (?,?,?,?,?,?,?,?,?)",
                    (pid, f["label"], f["number"], f.get("caption"), json.dumps(f["files"]), f["kind"],
                     sid(f["section"]), f["start"], f["end"]))
    # K3: bibliography entries and citations
    bib_ids = {}
    for e in doc["bib"]["entries"]:
        resolved = "arxiv-id" if e["arxiv"] else ("doi" if e["doi"] else None)
        conf = 1.0 if e["arxiv"] else (0.9 if e["doi"] else None)
        if e["arxiv"] and e.get("n_arxiv_ids", 1) > 1:
            conf = 0.8                                  # several ids in one entry: the first is taken
        cur = con.execute("INSERT INTO bib_entries(paper_id, cite_key, raw, target_arxiv, target_doi, target_recid, "
                          "resolved_by, confidence, source, title, eprint) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          (pid, e["cite_key"], e["raw"][:4000], e["arxiv"], e["doi"], None, resolved, conf,
                           doc["bib"]["source"], e.get("title"), e.get("eprint")))
        bib_ids.setdefault(e["cite_key"], (cur.lastrowid, e))
    body_chunks = sorted([(c["start"], c["end"], cid) for cid, c in chunk_rows
                          if c["kind"] in ("body", "appendix", "footnote", "caption", "abstract")
                          and c["start"] is not None], key=lambda x: (x[0], -x[1]))
    for c in doc["cites"]:
        chunk_id = None
        for a, b, cid in body_chunks:
            if a <= c["start"] < b:
                chunk_id = cid
                break
        for k in c["keys"]:
            bid, e = bib_ids.get(k, (None, None))
            con.execute("INSERT INTO citations(citing, cited_arxiv, cited_doi, bib_id, chunk_id, context, in_corpus, "
                        "cite_key, char_start) VALUES (?,?,?,?,?,?,?,?,?)",
                        (pid, e["arxiv"] if e else None, e["doi"] if e else None, bid, chunk_id, c["context"],
                         None, k, c["start"]))


def build_dir(lay, pid):
    return os.path.join(lay.build, "tex", _inv.id_key(pid))


def write_build(lay, pid, doc, flat, smap):
    d = build_dir(lay, pid)
    os.makedirs(d, exist_ok=True)
    for name, text in (("flat.tex", flat), ("doc.json", json.dumps(doc, indent=1, ensure_ascii=False)),
                       ("sourcemap.json", json.dumps(smap.to_json() if smap else []))):
        tmp = os.path.join(d, f".{name}.tmp-{os.getpid()}")
        with open(tmp, "w", encoding="utf-8", errors="surrogatepass") as f:
            f.write(text)
        os.replace(tmp, os.path.join(d, name))


def analyse(lay, pid, row):
    """Parse one paper (no writes). Returns (pid, chk, doc, flat, smap, status)."""
    chk = _inv.check_paper(lay, pid, row)
    if chk["status"] != "ok":
        return pid, chk, None, None, None, "download-" + chk["status"]
    vdir = os.path.join(lay.raw_arxiv, chk["key"], chk["current"])
    src = os.path.join(vdir, "src")
    try:
        if chk.get("source_kind") == "pdf" or chk.get("sniffed_kind") == "pdf":
            pdfs = [f for f in F.list_files(src) if f.lower().endswith(".pdf")]
            doc, flat, smap = parse_pdf(os.path.join(src, pdfs[0]) if pdfs else os.path.join(vdir, "source.bin"))
            chk["source_kind"] = "pdf"
        else:
            doc, flat, smap = parse_tex(src)
        status = "ok" if doc["quality"]["score"] >= REVIEW_THRESHOLD else "review"
        if chk.get("source_kind") == "pdf":
            status = "pdf"
        return pid, chk, doc, flat, smap, status
    except Exception as e:                                         # a failure is recorded, never fatal
        tb = traceback.format_exc(limit=4)
        doc = {"title": "", "authors": [], "abstract": None, "sections": [], "equations": [], "figures": [],
               "cites": [], "chunks": [], "quality": {"score": 0.0}, "error": f"{type(e).__name__}: {e}"[:500],
               "traceback": tb[-2000:], "bib": {"source": None, "files": [], "notes": [], "entries": []}}
        return pid, chk, doc, "", None, "failed"


def store(lay, result):
    """Write one analysed paper (build files and rows) under the writer lock."""
    pid, chk, doc, flat, smap, status = result
    with writer_lock(lay, what=f"ingest {pid}"):
        con = _db.connect_rw(lay.db_work)
        try:
            con.execute("BEGIN")
            if doc is None:
                _db.log(con, "ingest-arxiv", pid, "skipped", f"download status {chk['status']}")
            else:
                write_build(lay, pid, doc, flat, smap)
                write_paper(con, pid, chk, doc, _sha(flat) if flat else None, status)
                _db.log(con, "ingest-arxiv", pid, status,
                        json.dumps({"score": doc["quality"].get("score"), "sections": len(doc["sections"]),
                                    "equations": len(doc["equations"]), "chunks": len(doc["chunks"]),
                                    "bib": len(doc["bib"]["entries"]), "bib_source": doc["bib"]["source"],
                                    "error": doc.get("error")}))
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    return status
