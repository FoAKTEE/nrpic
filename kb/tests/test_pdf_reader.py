"""kbtool.pdf_reader and kbtool.pdf_ingest: PDF checks, pdftotext under limits, repairs of
Type-3 ligature loss, structure, and an end-to-end ingestion of a PostScript-only e-print
from its stored PDF on a synthetic store. The PDFs are written here by hand (Helvetica text)."""
import gzip
import hashlib
import json
import os
import shutil
import sqlite3

import pytest

from kbtool import pdf_reader as P

VOCAB = {"first": 500, "fluid": 300, "flux": 200, "field": 900, "significant": 150, "inflationary": 120,
         "define": 100, "definition": 80, "difficulty": 40, "effective": 400, "different": 600, "framework": 50,
         "the": 10000, "of": 9000, "in": 8000, "de": 300, "and": 9000, "is": 5000, "a": 9000, "we": 3000,
         "ux": 20, "uid": 2, "office": 30, "fine": 25, "five": 25, "ne": 30, "sitter": 200, "for": 4000,
         "method": 300, "methods": 300, "equations": 300, "slicing": 60, "this": 3000, "new": 900, "formalism": 40,
         "numerical": 400, "relativity": 300, "einstein": 300, "hyperbolic": 50, "form": 300, "flow": 90}


# ------------------------------------------------------------------ hand-made PDFs
def _esc(s):
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(pages):
    """A valid PDF: each page a list of lines; '' makes a paragraph gap."""
    objs = {1: b"<< /Type /Catalog /Pages 2 0 R >>",
            3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"}
    kids = []
    n = 4
    for lines in pages:
        ops = ["BT /F1 10 Tf 72 740 Td 12 TL"]
        for line in lines:
            ops.append("T* T* T*" if line == "" else f"({_esc(line)}) Tj T*")
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1")
        objs[n] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> "
                   f"/Contents {n + 1} 0 R >>").encode()
        objs[n + 1] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
        kids.append(n)
        n += 2
    objs[2] = ("<< /Type /Pages /Kids [" + " ".join(f"{k} 0 R" for k in kids) + f"] /Count {len(kids)} >>").encode()
    out = bytearray(b"%PDF-1.4\n")
    offs = {}
    for k in sorted(objs):
        offs[k] = len(out)
        out += b"%d 0 obj\n" % k + objs[k] + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for k in sorted(objs):
        out += b"%010d 00000 n \n" % offs[k]
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


ABSTRACT = ("We present a new formulation of the Einstein equations that casts them in an explicitly first "
            "order flux conservative hyperbolic form for a wide class of slicing conditions.")
PAGES = [["A New Formalism for Numerical Relativity", "C. Bona, J. Masso, E. Seidel and J. Stela", "",
          "We present a new formulation of the Einstein equations that casts them in an",
          "explicitly first order flux conservative hyperbolic form for a wide class of",
          "slicing conditions.", "",
          "Introduction. For decades the standard approach [1] to numerical relativity has",
          "been based on the 3+1 formulation [2,3]. Fluid methods [1-3] are mature.", "",
          "FIG. 1. Comparison between the two approaches."],
         ["Conclusion. We have presented a new formulation that can be used with many",
          "slicings, including maximal slicing.", "",
          "[1] J. W. York, in Sources of Gravitational Radiation (1979).",
          "[2] R. Arnowitt, S. Deser, and C. W. Misner, arXiv:gr-qc/0405109.",
          "[3] C. Bona and J. Masso, Phys. Rev. D 40, 1022 (1989), doi:10.1103/PhysRevD.40.1022"]]

needs_pdftotext = pytest.mark.skipif(not os.path.exists(P.PDFTOTEXT), reason="poppler pdftotext not installed")


# ------------------------------------------------------------------ repairs
def test_repair_ligatures_ot1_and_hyphens():
    raw = ("The rst order uid ux and the signi cant in ationary de nition; di\x0eculty of Mass\x13o "
           "[5{7] \\ad hoc\" frame-\nwork.\x0cNext page \x1e = 2.")
    text, edits, counts = P.repair(raw, VOCAB)
    assert "first order fluid flux" in text
    assert "significant inflationary definition" in text
    assert "difficulty" in text and "Masso" in text
    assert "[5–7]" in text and "“ad hoc" in text
    assert "framework" in text
    assert "\x0cNext page" in text                         # the page break is kept
    assert "φ = 2" in text                            # cmmi phi
    assert counts["ligature-dropped"] >= 3 and counts["ligature-split"] >= 3
    assert counts["ot1-ligature"] == 1 and counts["accent-dropped"] == 1
    # every edit is recorded with its offsets in the text it was made on
    for a, b, old, new, kind in edits["step1_on_raw"]:
        assert raw[a:b] == old


def test_repair_leaves_words_and_acronyms_alone():
    text, _, counts = P.repair("The CFD method of the new formalism is fine and five.", VOCAB)
    assert text == "The CFD method of the new formalism is fine and five."
    assert counts == {}
    assert P.best_repair("ne", VOCAB) is None              # fine (25) vs ne (30): not 10 times as frequent
    assert P.best_repair("rst", VOCAB) == "first"
    assert P.best_repair("Rst", VOCAB) == "First"
    assert P.best_repair("UX", VOCAB) is None              # short capitals: an acronym


def test_oov_fraction_counts_rare_tokens():
    f, n = P.oov_fraction("the rst uid field", VOCAB)
    assert n == 4 and f == pytest.approx(0.5)


# ------------------------------------------------------------------ structure
def test_headings_roman_lettered_numbered_sequence():
    text = ("I. INTRODUCTION\n\nText.\n\nII. BASIC EQUATIONS AND THE\nSCALAR FIELD\n\nA. Massive case\n\nB. General case\n\n"
            "D. Skipped letter\n\nIII. DISCUSSION\n\nACKNOWLEDGMENTS\n\nREFERENCES\n")
    h = P.find_headings(text)
    assert [(x[3], x[5]) for x in h] == [("I", "roman"), ("II", "roman"), ("A", "lettered"), ("B", "lettered"),
                                         ("III", "roman"), ("", "unnumbered"), ("", "unnumbered")]
    assert h[1][4] == "BASIC EQUATIONS AND THE SCALAR FIELD"
    text2 = "1 Introduction\n\n2 H2\n\n2 Methods\n\n2.1 Grid setup\n\n7 Random line\n\n3 Results\n"
    assert [x[3] for x in P.find_headings(text2)] == ["1", "2", "2.1", "3"]


def test_runin_standalone_references_citations():
    text = ("PACS numbers: 04.25.Dm\n\nIntroduction. For decades [1].\nThe remaining equations form the system.\n"
            "A new class of gauge conditions. We are\n")
    assert [x[4] for x in P.find_runin(text)] == ["Introduction", "A new class of gauge conditions"]
    alone = P.find_standalone("Intro text.\n\nStatement of Need\nThe code is needed.\n")
    assert [x[4] for x in alone] == ["Statement of Need"]
    refs = "x\n" * 40 + "[1] A. Author, Phys. Rev. D 1, 1 (1990).\n[2] B. Author,\narXiv:2611.12831.\n\nFIG. 1. x\n"
    entries, spans = P.find_references(refs)
    assert [e["key"] for e in entries] == ["1", "2"] and entries[1]["raw"] == "[2] B. Author, arXiv:2611.12831."
    ay = ("x\n" * 40 + "References\n\nAasi, J., & others. (2015). Advanced LIGO. https:\n//doi.org/10.1088/0264-9381/32/7/074001\n"
          "Abbott, B. P., & others. (2016). Observation. Phys. Rev. Lett.\n")
    e2, _ = P.find_references(ay)
    assert len(e2) == 2 and e2[0]["style"] == "author-year" and "https://doi.org/10.1088/0264-9381/32/7/074001" in e2[0]["raw"]
    cites = P.numeric_citations("as in [1] and [2,3] or [1–3] but not [9]", [], 3)
    assert [c[2] for c in cites] == [["1"], ["2", "3"], ["1", "2", "3"]]


def test_analyse_text_sections_abstract_chunks():
    body = " ".join(["Some ordinary words of the body text."] * 30)
    text = ("Title line\nAuthors\n\n" + ABSTRACT + "\n\nIntroduction. " + body + " [1]\n\nFIG. 1. A caption here.\n\n"
            "Conclusion. " + body + "\n\n[1] A. Author, arXiv:2611.12831.\n[2] B. Author (2000).\n[3] C. Author.\n")
    doc = P.analyse_text(text, {"title": "A New Formalism", "authors": ["C. Bona"], "abstract": ABSTRACT})
    assert [s["title"] for s in doc["sections"]] == ["Introduction", "Conclusion"]
    kinds = [c["kind"] for c in doc["chunks"]]
    assert kinds[0] == "abstract" and "caption" in kinds and "body" in kinds
    ab = doc["chunks"][0]
    assert text[ab["start"]:ab["end"]].strip() == ABSTRACT and doc["quality"]["abstract_similarity_to_metadata"] > 0.99
    body_text = " ".join(c["text"] for c in doc["chunks"] if c["kind"] == "body")
    assert "A caption here" not in body_text and "arXiv:2611.12831" not in body_text
    assert [e["arxiv"] for e in doc["bib"]["entries"]] == ["2611.12831", None, None]
    assert doc["cites"][0]["keys"] == ["1"] and doc["equations"] == []


# ------------------------------------------------------------------ PDFs: checks and text
def _store_pdf(store, aid, version, blob, record=True, sha=None):
    key = aid.replace("/", "_")
    vdir = os.path.join(store.data, "raw", "arxiv", key, version)
    os.makedirs(vdir, exist_ok=True)
    p = os.path.join(vdir, "source.pdf")
    with open(p, "wb") as f:
        f.write(blob)
    if record:
        d = os.path.join(store.data, "meta", "arxiv-pdf")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, key + ".json"), "w") as f:
            json.dump({"id": aid, "status": "ok", "version": version, "bytes": len(blob),
                       "sha256": sha or hashlib.sha256(blob).hexdigest(), "pdf": p}, f)
    return p


def test_check_pdf_good_and_bad(store):
    good = make_pdf(PAGES)
    store.add("gr-qc/9412071", gzip.compress(b"%!PS-Adobe-2.0\n%%EOF\n", mtime=0), "v2")
    _store_pdf(store, "gr-qc/9412071", "v2", good)
    chosen, checks = P.choose_pdf(store.layout, "gr-qc/9412071")
    assert chosen and chosen["ok"] and chosen["kind"] == "source.pdf"
    _store_pdf(store, "gr-qc/9412071", "v2", good, sha="0" * 64)
    chosen, checks = P.choose_pdf(store.layout, "gr-qc/9412071")
    assert chosen is None and "sha256 differs from the --pdf record" in checks[0]["problems"]
    _store_pdf(store, "gr-qc/9412071", "v2", good.replace(b"%%EOF", b"%%XXX"))
    chosen, checks = P.choose_pdf(store.layout, "gr-qc/9412071")
    assert chosen is None and "no %%EOF in the last 2 KiB" in checks[0]["problems"]


@needs_pdftotext
def test_extract_text_pages(tmp_path):
    p = tmp_path / "a.pdf"
    p.write_bytes(make_pdf(PAGES))
    work = tmp_path / "cwd"
    work.mkdir()
    t = P.extract_text(str(p), str(work))
    assert t.count("\x0c") == 2
    assert "Introduction. For decades the standard approach [1]" in t
    assert os.listdir(work) == []                           # the parser wrote nothing


# ------------------------------------------------------------------ end to end
@needs_pdftotext
def test_pdf_ingest_end_to_end(store, monkeypatch, tmp_path):
    from kbtool import cli, meta_manifest, pdf_ingest
    import kbtool.cli as c
    aid = "gr-qc/9412071"
    store.manifest([(aid, "G01", "1"), ("2111.05282", "G01", "3")])
    monkeypatch.setattr(c, "kb_manifest_dir", lambda: store.mdir)
    monkeypatch.setattr(meta_manifest, "kb_manifest_dir", lambda: store.mdir)
    monkeypatch.setenv("KB_NO_REEXEC", "1")
    from kbtool import db as _db
    os.makedirs(store.layout.db_dir, exist_ok=True)
    _db.init_db(store.layout)
    store.add(aid, gzip.compress(b"%!PS-Adobe-2.0\n%%Pages: 2\n%%EOF\n", mtime=0), "v2")
    _store_pdf(store, aid, "v2", make_pdf(PAGES))
    api = os.path.join(store.data, "meta", "arxiv-api")
    os.makedirs(api)
    with open(os.path.join(api, "gr-qc_9412071.json"), "w") as f:
        json.dump({"id": aid, "status": "ok", "version": "v2", "title": "A New formalism for numerical relativity",
                   "authors": ["C. Bona", "J. Masso", "E. Seidel", "J. Stela"], "abstract": ABSTRACT,
                   "published": "1994-12-23T00:00:00Z", "updated": "1995-08-01T00:00:00Z",
                   "primary_category": "gr-qc", "categories": ["gr-qc"], "doi": "10.1103/PhysRevLett.75.600",
                   "journal_ref": "Phys.Rev.Lett. 75 (1995) 600-603", "license": None}, f)
    vocab = tmp_path / "vocab.json"
    vocab.write_text(json.dumps(VOCAB))
    out = tmp_path / "out"
    assert pdf_ingest.main(["--id", aid, "--vocab", str(vocab), "--out", str(out)]) == 0
    rep = json.load(open(out / "pdf_ingest.json"))["papers"][0]
    assert rep["status"] == "pdf" and rep["pages"] == 2 and rep["bib_entries"] == 3
    con = sqlite3.connect(store.layout.db_work)
    row = con.execute("SELECT title, source_kind, parse_status, version, grp, priority, primary_class, doi, "
                      "title_source, title_matches_brief, brief_title, main_tex FROM papers WHERE paper_id=?",
                      (aid,)).fetchone()
    assert row == ("A New formalism for numerical relativity", "pdf", "pdf", "v2", "G01", 1, "gr-qc",
                   "10.1103/PhysRevLett.75.600", "arxiv-api", 1, "A New formalism for numerical relativity",
                   "source.pdf")
    secs = [r[0] for r in con.execute("SELECT title FROM sections WHERE paper_id=? ORDER BY char_start", (aid,))]
    assert secs == ["Introduction", "Conclusion"]
    bib = con.execute("SELECT cite_key, target_arxiv, target_doi FROM bib_entries WHERE paper_id=? ORDER BY bib_id",
                      (aid,)).fetchall()
    assert bib == [("1", None, None), ("2", "gr-qc/0405109", None), ("3", None, "10.1103/PhysRevD.40.1022")]
    keys = sorted(r[0] for r in con.execute("SELECT cite_key FROM citations WHERE citing=?", (aid,)))
    assert keys == ["1", "1", "2", "2", "3", "3"]
    hits = con.execute("SELECT c.paper_id FROM chunks_fts f JOIN chunks c ON c.chunk_id=f.rowid "
                       "WHERE chunks_fts MATCH 'maximal'").fetchall()
    assert (aid,) in hits
    # build files: flat.tex is the repaired text the char ranges point into
    bdir = os.path.join(store.data, "build", "tex", "gr-qc_9412071")
    flat = open(os.path.join(bdir, "flat.tex"), encoding="utf-8").read()
    s0, s1 = con.execute("SELECT char_start, char_end FROM chunks WHERE paper_id=? AND kind='abstract'", (aid,)).fetchone()
    assert flat[s0:s1].split() == ABSTRACT.split()
    assert os.path.exists(os.path.join(bdir, "pdf_raw.txt")) and os.path.exists(os.path.join(bdir, "pdf_edits.json"))
    assert con.execute("SELECT status FROM ingest_log WHERE step='ingest-pdf'").fetchone() == ("pdf",)
    # re-ingesting replaces the rows (no duplicates)
    shutil.rmtree(out)
    assert pdf_ingest.main(["--id", aid, "--vocab", str(vocab), "--out", str(out)]) == 0
    assert con.execute("SELECT count(*) FROM sections WHERE paper_id=?", (aid,)).fetchone()[0] == 2
    con.close()
