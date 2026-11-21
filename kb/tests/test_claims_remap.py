"""Claim-safe re-ingest (kbtool.claims_remap, `kb ingest arxiv --remap-claims`): after a re-ingest
that moves every offset of flat.tex and renumbers the chunks, each claim's locator rows, chunk
and quote range equal what an independent resolution of its (file, lines) gives on the new
state; a claim with a chunk but no locator row follows its source lines; labels and statuses
stay; a claim_events row records each remap. Synthetic paper only."""
import json
import sqlite3

from conftest import make_tar
from kbtool import claims_check as CK
from kbtool import claims_db as CDB
from kbtool import papers_ingest as P
from kbtool.claims_parse import Locator
from test_papers_ingest import run

LONG = " ".join(f"w{k}" for k in range(500))
PAPER = ("\\documentstyle[aps]{revtex}\n\\begin{document}\n\\title{Remap test}\n"
         "\\section{First}\n" + LONG + "\n"                         # line 5
         "The answer is 42 \\cite{r1}.\n"                           # line 6
         + LONG + "\n"
         "\\section{Second}\n" + LONG + "\n"
         "A second number 17 \\cite{r2}.\n"                         # line 10
         "\\begin{references}\n\\bibitem{r1} R. One, arXiv:1707.00001.\n\\bibitem{r2} R. Two.\n"
         "\\end{references}\n\\end{document}\n")
PID = "1707.09999"
FILLER = "1707.09998"           # ingested after PID, so PID's new chunk ids are not its old ones (SQLite
                                # reuses the highest rowids after a delete)


def setup_store(store):
    store.manifest([(PID, "G01", "2"), (FILLER, "G01", "2")])
    store.add(PID, make_tar([("main.tex", PAPER.encode())]), "v1")
    store.add(FILLER, make_tar([("main.tex", PAPER.replace("Remap test", "Filler").encode())]), "v1")


def shifted_flatten(orig):
    def f(root, main):
        fl = orig(root, main)
        fl["flat"] = "\n\n\n\n\n" + fl["flat"]       # a different flat.tex: every offset moves by 5
        fl["source_map"].starts = [s + 5 for s in fl["source_map"].starts]
        return fl
    return f


def resolve(con, lay, file, a, b):
    st = CK.Store(lay.raw_arxiv, lay.build + "/tex", con)
    return st.resolve(Locator(PID, "v1", file, a, b, f"{PID}v1:{file}:L{a}-{b}", 0))


def add_claim(con, lay, line, text, with_row=True):
    r = resolve(con, lay, "main.tex", line, line)
    assert r.resolved and r.chunk_ids
    cur = con.execute("INSERT INTO claims(text, kind, paper_id, locator, chunk_id, quote_start, quote_end, label, "
                      "origin) VALUES (?,?,?,?,?,?,?,?,?)",
                      (text, "number", PID, f"{PID}v1:main.tex:L{line}", r.chunk_ids[0], r.flat_start, r.flat_end,
                       "to_verify", "test"))
    cid = cur.lastrowid
    con.execute("INSERT INTO claim_meta(claim_id, seed_key, source_label, status, label_set_by) VALUES (?,?,?,?,?)",
                (cid, f"test-{cid}", "TO VERIFY", "located", "auto"))
    if with_row:
        con.execute("INSERT INTO claim_locators(claim_id, ord, paper_id, version, file, line_start, line_end, written, "
                    "resolved, problem, flat_start, flat_end, chunk_ids_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, 0, PID, "v1", "main.tex", line, line, f"L{line}", 1, "", r.flat_start, r.flat_end,
                     json.dumps(r.chunk_ids)))
    return cid


def state(con, cid):
    c = con.execute("SELECT chunk_id, quote_start, quote_end, label FROM claims WHERE claim_id=?", (cid,)).fetchone()
    rows = con.execute("SELECT flat_start, flat_end, chunk_ids_json FROM claim_locators WHERE claim_id=?",
                       (cid,)).fetchall()
    st = con.execute("SELECT status FROM claim_meta WHERE claim_id=?", (cid,)).fetchone()[0]
    return c, rows, st


def test_remap_follows_lines_through_a_changed_flat(store, monkeypatch, capsys):
    setup_store(store)
    lay = store.layout
    # 1. the "old" ingest: a flat.tex shifted by 5 characters
    orig = P.F.flatten
    monkeypatch.setattr(P.F, "flatten", shifted_flatten(orig))
    assert run(store, ["ingest", "arxiv", "--id", PID, "--jobs", "1", "--no-meta"], monkeypatch) == 0
    monkeypatch.setattr(P.F, "flatten", orig)
    assert run(store, ["ingest", "arxiv", "--id", FILLER, "--jobs", "1", "--no-meta"], monkeypatch) == 0
    con = sqlite3.connect(lay.db_work)
    CDB.ensure(con)
    old_chunks = {r[0] for r in con.execute("SELECT chunk_id FROM chunks WHERE paper_id=?", (PID,))}
    old_sha = con.execute("SELECT flat_sha256 FROM papers WHERE paper_id=?", (PID,)).fetchone()[0]
    c1 = add_claim(con, lay, 6, "The answer is 42.")
    c2 = add_claim(con, lay, 10, "A second number is 17.")
    c3 = add_claim(con, lay, 10, "Served claim with a chunk and no locator row.", with_row=False)
    con.commit()
    before = {c: state(con, c) for c in (c1, c2, c3)}
    con.close()

    # 2. re-ingest with the real flattening and the remap
    out = store.data + "/remap-out"
    assert run(store, ["ingest", "arxiv", "--id", PID, "--jobs", "1", "--no-meta", "--remap-claims", "--out", out],
               monkeypatch) == 0
    printed = capsys.readouterr().out
    assert f"remap {PID}: 3 claims" in printed
    rep = json.load(open(out + "/remap.json"))[PID]
    assert rep["identical_flat"] is False and rep["rows"] == 2 and rep["rows_changed"] == 2

    con = sqlite3.connect(lay.db_work)
    new_sha = con.execute("SELECT flat_sha256 FROM papers WHERE paper_id=?", (PID,)).fetchone()[0]
    new_chunks = {r[0] for r in con.execute("SELECT chunk_id FROM chunks WHERE paper_id=?", (PID,))}
    assert new_sha != old_sha and not (new_chunks & old_chunks)
    for cid, line in ((c1, 6), (c2, 10)):
        (chunk, qs, qe, label), rows, st = state(con, cid)
        ref = resolve(con, lay, "main.tex", line, line)            # independent resolution on the new state
        assert rows == [(ref.flat_start, ref.flat_end, json.dumps(ref.chunk_ids))]
        assert (chunk, qs, qe) == (ref.chunk_ids[0], ref.flat_start, ref.flat_end)
        assert ref.flat_start == before[cid][0][1] - 5                # the offsets moved back by 5
        assert (label, st) == (before[cid][0][3], before[cid][2])    # label and status untouched
    (chunk3, qs3, qe3, _), rows3, _ = state(con, c3)
    ref = resolve(con, lay, "main.tex", 10, 10)
    assert rows3 == [] and chunk3 == ref.chunk_ids[0] and (qs3, qe3) == (ref.flat_start, ref.flat_end)
    ev = con.execute("SELECT claim_id, action, evidence FROM claim_events WHERE action='remap' ORDER BY claim_id"
                     ).fetchall()
    assert [e[0] for e in ev] == [c1, c2, c3]
    assert json.loads(ev[2][2])["how"].startswith("old chunk range through")
    # nothing points at a chunk that no longer exists
    assert con.execute("SELECT count(*) FROM claims WHERE chunk_id IS NOT NULL AND chunk_id NOT IN "
                       "(SELECT chunk_id FROM chunks)").fetchone()[0] == 0
    con.close()

    # 3. again with a byte-identical flat.tex: same ranges, chunk ids follow the new rows
    assert run(store, ["ingest", "arxiv", "--id", PID, "--jobs", "1", "--no-meta", "--remap-claims"],
               monkeypatch) == 0
    capsys.readouterr()
    con = sqlite3.connect(lay.db_work)
    rep = P.result_remap[PID]
    assert rep["identical_flat"] is True and rep["claims"] == 3
    for cid, line in ((c1, 6), (c2, 10)):
        (chunk, qs, qe, _), rows, _ = state(con, cid)
        ref = resolve(con, lay, "main.tex", line, line)
        assert rows == [(ref.flat_start, ref.flat_end, json.dumps(ref.chunk_ids))] and chunk == ref.chunk_ids[0]
    con.close()


def test_without_remap_the_chunks_dangle(store, monkeypatch, capsys):
    """The control: a plain re-ingest leaves claims pointing at deleted chunks."""
    setup_store(store)
    lay = store.layout
    assert run(store, ["ingest", "arxiv", "--id", PID, "--jobs", "1", "--no-meta"], monkeypatch) == 0
    assert run(store, ["ingest", "arxiv", "--id", FILLER, "--jobs", "1", "--no-meta"], monkeypatch) == 0
    con = sqlite3.connect(lay.db_work)
    CDB.ensure(con)
    add_claim(con, lay, 6, "The answer is 42.")
    con.commit()
    con.close()
    assert run(store, ["ingest", "arxiv", "--id", PID, "--jobs", "1", "--no-meta"], monkeypatch) == 0
    capsys.readouterr()
    con = sqlite3.connect(lay.db_work)
    assert con.execute("SELECT count(*) FROM claims WHERE chunk_id NOT IN (SELECT chunk_id FROM chunks)"
                       ).fetchone()[0] == 1
    con.close()
