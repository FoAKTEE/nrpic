"""K9 C4: the reader of the 30-paper comparison against INSPIRE must read the metadata where
`harness/bin/nrpic-fetch-arxiv --meta` writes it (decision 0016, item 6):
`kb-data/meta/inspire/<key>.json` (the record under "record") and, as a fallback,
`kb-data/meta/arxiv-api/<key>.json`. Synthetic records only; no real kb-data."""
import json
import sqlite3

from kbtool import qa_report


def _db(path, rows):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE papers(paper_id TEXT PRIMARY KEY, title TEXT, authors_json TEXT, parse_status TEXT)")
    con.executemany("INSERT INTO papers VALUES (?,?,?,?)", rows)
    con.commit()
    return con


def _store(tmp_path):
    meta = tmp_path / "kb-data" / "meta"
    (meta / "inspire").mkdir(parents=True)
    (meta / "arxiv-api").mkdir(parents=True)
    (meta / "arxiv").mkdir(parents=True)             # the inventory's directory: must not be required
    # INSPIRE, status ok: the layout of the fetch command (record.titles, record.authors.full_name)
    (meta / "inspire" / "2611.12831.json").write_text(json.dumps({
        "id": "2611.12831", "status": "ok", "n_matches": 1,
        "record": {"titles": [{"title": "Numerical-Relativity Particle-in-Cell Simulations"}],
                   "authors": [{"full_name": "Doe, Jane"}, {"full_name": "Roe, Richard"}]}}))
    # old-style id with a slash: key with an underscore; INSPIRE not found -> arXiv API record
    (meta / "inspire" / "gr-qc_9804040.json").write_text(json.dumps(
        {"id": "gr-qc/9804040", "status": "not-found", "n_matches": 0}))
    (meta / "arxiv-api" / "gr-qc_9804040.json").write_text(json.dumps(
        {"id": "gr-qc/9804040", "status": "ok", "title": "A Title of the Old Paper",
         "authors": ["Alice Smith", "Bob van der Berg"]}))
    return meta


def test_c4_reads_the_fetch_layout(tmp_path):
    meta = _store(tmp_path)
    con = _db(str(tmp_path / "p.sqlite"), [
        ("2611.12831", "Numerical-relativity particle-in-cell simulations",
         json.dumps(["Jane Doe", "Richard Roe"]), "ok"),
        ("gr-qc/9804040", "A title of the old paper", json.dumps(["A. Smith", "B. van der Berg"]), "ok"),
        ("1234.5678", "No metadata at all", "[]", "ok")])
    r = qa_report.c4_inspire_sample(con, str(meta), n=30)
    assert not r["blocked"]
    assert r["with_metadata"] == 2
    rows = {x["paper_id"]: x for x in r["rows"]}
    assert rows["2611.12831"]["metadata"] and rows["2611.12831"]["source"] == "inspire"
    assert rows["2611.12831"]["title_ratio"] == 1.0 and rows["2611.12831"]["author_fraction"] == 1.0
    assert rows["gr-qc/9804040"]["source"] == "arxiv-api"           # INSPIRE not found -> arXiv API
    assert rows["gr-qc/9804040"]["title_ratio"] == 1.0 and rows["gr-qc/9804040"]["author_fraction"] == 1.0
    assert rows["1234.5678"]["metadata"] is False


def test_c4_accepts_the_inventory_dir_as_before(tmp_path):
    """`run()` of wave 2 passed lay.meta_arxiv (kb-data/meta/arxiv); the reader must still find
    the sibling directories inspire/ and arxiv-api/ from there."""
    meta = _store(tmp_path)
    con = _db(str(tmp_path / "p.sqlite"), [
        ("2611.12831", "Numerical-relativity particle-in-cell simulations", json.dumps(["Jane Doe"]), "ok")])
    r = qa_report.c4_inspire_sample(con, str(meta / "arxiv"), n=30)
    assert r["with_metadata"] == 1 and r["rows"][0]["source"] == "inspire"


def test_c4_flags_disagreements(tmp_path):
    meta = _store(tmp_path)
    con = _db(str(tmp_path / "p.sqlite"), [
        ("2611.12831", "Something else entirely", json.dumps(["Nobody"]), "ok")])
    r = qa_report.c4_inspire_sample(con, str(meta), n=30)
    assert r["differ"] == ["2611.12831"]
