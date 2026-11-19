"""kbtool.meta_brief16, kbtool.meta_manifest, kbtool.meta_papers: brief section 16 read by
script, the comparison classes, the manifest additions, and the metadata written into the
papers table (idempotent, TeX values kept) on a synthetic store."""
import json
import os
import sqlite3

import pytest

from kbtool import brief, meta_brief16 as M16, meta_manifest as MM, meta_papers as MP, paths

BRIEF = paths.default_brief()


@pytest.mark.skipif(BRIEF is None, reason="brief not in the checkout")
def test_section16_is_section17():
    s16 = M16.parse_section16(BRIEF)
    assert s16["problems"] == []
    assert len(s16["entries"]) == 684 and sorted(s16["groups"]) == [f"G{k:02d}" for k in range(1, 22)]
    rows = brief.load_arxiv_manifest(os.path.join(paths.kb_manifest_dir(), "arxiv.tsv"))
    m17 = {r["id"]: (r["group"], r["priority"]) for r in rows}
    assert {e["id"]: (e["group"], e["priority"]) for e in s16["entries"]} == m17
    first = s16["entries"][0]
    assert first["id"] == "2611.12831" and first["authors_raw"] == "Wu, Most" and first["line"] == 1783


def test_title_classes():
    assert M16.compare_title("A New formalism", "A New formalism")["class"] == "same"
    assert M16.compare_title("The $\\Lambda$CDM model: tests", "The ΛCDM Model -- Tests")["class"] == "format"
    assert M16.compare_title("Gravitational waves from the early matter era",
                             "Gravitational waves from an early matter era")["class"] == "minor"
    r = M16.compare_title("Supermassive black hole seeds", "Ringdown and lensing of triple systems")
    assert r["class"] == "differs" and r["ratio"] < 0.9
    assert M16.compare_title("x", None)["class"] == "no-metadata"


@pytest.mark.parametrize("brief_raw,meta,cls", [
    ("Wu, Most", ["Jiaxi Wu", "Elias R. Most"], "match"),
    ("Bona, Massó, Seidel, Stela", ["C. Bona", "J. Masso", "E. Seidel", "J. Stela"], "match"),
    ("Most, Wu", ["Jiaxi Wu", "Elias R. Most"], "order"),
    ("Wu", ["Jiaxi Wu", "Elias R. Most"], "incomplete"),
    ("Stone et al.", ["James M. Stone", "Patrick D. Mullen"], "match"),
    ("Mullen et al.", ["James M. Stone", "Patrick D. Mullen"], "order"),
    ("Yu (first author)", ["Qingjuan Yu", "Scott Tremaine"], "match"),
    ("(authors include J. Wu and E. R. Most)", ["A. B", "Jiaxi Wu", "Elias R. Most"], "match"),
    ("van Meter, Baker", ["James R. van Meter", "John G. Baker"], "match"),
    ("Martín-García, Gundlach", ["Jose M. Martin-Garcia", "Carsten Gundlach"], "match"),
    ("Smith, Jones", ["A. Smith", "B. Brown"], "mismatch"),
    ("", ["A. Smith"], "not-checked"),
    ("Evans", ["Charles R. Evans Jr."], "match"),
    ("Bernuzzi, Hilditch", ["Bernuzzi, Sebastiano", "Hilditch, David"], "match"),
])
def test_author_classes(brief_raw, meta, cls):
    assert M16.compare_authors(brief_raw, meta)["class"] == cls


def test_additions_file_is_valid():
    rows = MM.load_additions()
    base = {r["id"] for r in brief.load_arxiv_manifest(os.path.join(paths.kb_manifest_dir(), "arxiv.tsv"))}
    groups = {f"G{k:02d}" for k in range(1, 22)}
    assert len(rows) == 26 and MM.check_additions(rows, base, groups) == []
    full = MM.load_full_manifest()
    assert len(full) == 684 + 26 and len({r["id"] for r in full}) == 710


def test_additions_checks(tmp_path):
    p = tmp_path / "arxiv_additions.tsv"
    p.write_text("# c\nid\tgroup\tpriority\trequested_by\tdecision\tnote\n"
                 "2611.12831\tG01\t2\tX\t0016-6\tdup of base\n1234.5678\tG99\t5\t\t\t\n1707.06302\tG18\t2\tD\t0016-6\t\n")
    rows = MM.load_additions(str(p))
    probs = MM.check_additions(rows, {"2611.12831"}, {f"G{k:02d}" for k in range(1, 22)})
    assert any("already in the brief" in x for x in probs)
    assert any("G99" in x for x in probs) and any("bad priority" in x for x in probs)
    assert any("requested_by and decision" in x for x in probs)
    assert len(probs) == 4


# ------------------------------------------------------------------ load into papers
def _setup(store, monkeypatch):
    from kbtool import cli
    import kbtool.cli as c
    store.manifest([("gr-qc/9412071", "G01", "1"), ("2611.12831", "G01", "3")])
    with open(os.path.join(store.mdir, "arxiv_additions.tsv"), "w") as f:
        f.write("id\tgroup\tpriority\trequested_by\tdecision\tnote\n1707.06302\tG18\t2\tD-bh-dress\t0016-6\tspikes\n")
    monkeypatch.setattr(c, "kb_manifest_dir", lambda: store.mdir)
    monkeypatch.setattr(MM, "kb_manifest_dir", lambda: store.mdir)
    from kbtool import db as _db
    os.makedirs(store.layout.db_dir, exist_ok=True)
    _db.init_db(store.layout)
    con = sqlite3.connect(store.layout.db_work)
    for pid, grp, title, authors in (("2611.12831", "G01", "Numerical relativity PIC", ["J. Wu", "E. Most"]),
                                     ("1707.06302", None, "Dark matter spikes", ["F. Ferrer"])):
        con.execute("INSERT INTO papers(paper_id, title, authors_json, abstract, grp, priority, version, source_kind, "
                    "parse_status, title_source, parse_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (pid, title, json.dumps(authors), "tex abstract", grp, 3 if grp else None, "v1", "tex", "ok",
                     "tex", json.dumps({"quality": {"score": 0.9, "abstract_similarity_note": "none yet"}})))
        con.execute("INSERT INTO chunks(paper_id, kind, text, n_tokens) VALUES (?,?,?,?)",
                    (pid, "abstract", "We present a numerical relativity particle in cell method.", 9))
    con.commit()
    con.close()
    meta = os.path.join(store.data, "meta")
    os.makedirs(os.path.join(meta, "arxiv-api"))
    os.makedirs(os.path.join(meta, "inspire"))
    api = {"id": "2611.12831", "status": "ok", "version": "v2",
           "title": "Numerical-Relativity Particle-in-Cell Simulations: Self-Gravitating Collisionless Matter in "
                    "Dynamical Spacetimes", "authors": ["Jiaxi Wu", "Elias R. Most"],
           "abstract": "We present a numerical-relativity particle-in-cell method.", "published": "2026-11-09T18:30:08Z",
           "updated": "2026-11-09T18:30:08Z", "primary_category": "gr-qc", "categories": ["gr-qc"], "doi": None,
           "journal_ref": None, "license": None}
    json.dump(api, open(os.path.join(meta, "arxiv-api", "2611.12831.json"), "w"))
    json.dump({**api, "id": "1707.06302", "title": "Dark matter spikes in the vicinity of Kerr black holes",
               "authors": ["Francesc Ferrer", "Augusto Medeiros da Rosa", "Clifford M. Will"], "version": "v1"},
              open(os.path.join(meta, "arxiv-api", "1707.06302.json"), "w"))
    json.dump({"id": "2611.12831", "status": "ok", "fetched_utc": "2026-11-15T18:27:51Z",
               "record": {"control_number": 3226709, "arxiv_eprints": [{"value": "2611.12831"}],
                          "titles": [{"title": api["title"]}], "authors": [{"full_name": "Wu, Jiaxi"}],
                          "dois": [{"value": "10.1103/x.1"}],
                          "publication_info": [{"journal_title": "Phys.Rev.D", "journal_volume": "1", "year": 2027,
                                                "artid": "1"}]}},
              open(os.path.join(meta, "inspire", "2611.12831.json"), "w"))
    # an INSPIRE record that names another paper is ignored
    json.dump({"id": "1707.06302", "status": "ok", "record": {"control_number": 1, "arxiv_eprints": [{"value": "9999.99999"}]}},
              open(os.path.join(meta, "inspire", "1707.06302.json"), "w"))


@pytest.mark.skipif(BRIEF is None, reason="brief not in the checkout")
def test_load_into_papers(store, monkeypatch):
    _setup(store, monkeypatch)
    rows, summary, _ = MP.load(store.layout)
    assert summary["papers"] == 2 and summary["arxiv_api"] == 2 and summary["inspire"] == 1
    assert summary["manifest_addition"] == 1
    con = sqlite3.connect(store.layout.db_work)
    q = ("SELECT title, authors_json, abstract, primary_class, doi, inspire_recid, journal_ref, title_source, grp, "
         "priority, brief_title, brief_authors, title_matches_brief, parse_json FROM papers WHERE paper_id=?")
    r = con.execute(q, ("2611.12831",)).fetchone()
    assert r[0].startswith("Numerical-Relativity Particle-in-Cell") and json.loads(r[1]) == ["Jiaxi Wu", "Elias R. Most"]
    assert r[2] == "We present a numerical-relativity particle-in-cell method."
    assert r[3:10] == ("gr-qc", "10.1103/x.1", 3226709, "Phys.Rev.D 1 (2027) 1", "arxiv-api", "G01", 3)
    assert r[11] == "Wu, Most" and r[12] == 1
    pj = json.loads(r[13])
    assert pj["tex_front"]["title"] == "Numerical relativity PIC"
    assert pj["meta"]["version_is_latest"] is False and pj["meta"]["arxiv_api"]["latest_version"] == "v2"
    assert pj["meta"]["brief16"]["line"] == 1783 and pj["quality"]["abstract_similarity_to_metadata"] > 0.5
    assert "abstract_similarity_note" not in pj["quality"] and pj["quality"]["score"] == 0.9
    r2 = con.execute(q, ("1707.06302",)).fetchone()
    assert r2[5] is None                                          # INSPIRE record of another paper: ignored
    assert r2[8:13] == ("G18", 2, None, None, None)               # an addition: group from the file, no brief entry
    # idempotent: a second load changes nothing but the load time
    before = con.execute("SELECT * FROM papers ORDER BY paper_id").fetchall()
    con.close()
    MP.load(store.layout)
    con = sqlite3.connect(store.layout.db_work)
    after = con.execute("SELECT * FROM papers ORDER BY paper_id").fetchall()
    strip = lambda rows: [tuple(json.dumps({**json.loads(v), "meta": {k: x for k, x in json.loads(v)["meta"].items()  # noqa: E731
                                                                     if k != "loaded_at"}}) if isinstance(v, str) and v.startswith('{"') and '"meta"' in v else v
                                for v in row) for row in rows]
    assert strip(before) == strip(after)
    assert json.loads(con.execute("SELECT parse_json FROM papers WHERE paper_id='2611.12831'").fetchone()[0]
                      )["tex_front"]["title"] == "Numerical relativity PIC"
    con.close()


@pytest.mark.skipif(BRIEF is None, reason="brief not in the checkout")
def test_brief16_report_on_store(store, monkeypatch):
    _setup(store, monkeypatch)
    rep = MP.brief16_report(store.layout, manifest_dir=store.mdir)
    by = {r["id"]: r for r in rep["rows"]}
    assert len(rep["rows"]) == 684
    assert by["2611.12831"]["title_class"] == "same" and by["2611.12831"]["authors_class"] == "match"
    assert by["2611.12831"]["agree"] is True
    assert by["0912.2920"]["title_class"] == "no-metadata"
