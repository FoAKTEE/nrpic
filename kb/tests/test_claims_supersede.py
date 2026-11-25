"""`kb claim supersede` (package tracks/kb/claims3, item 2): a claim whose own text is wrong, or
holds no statement, is closed with a pointer to the claim that replaces it, with history.

Uses the synthetic store of test_claims.py (a 2609.14218 source of 1103 lines)."""
import os
import sqlite3

import pytest

from kbtool import claims_check as ck
from kbtool import claims_cli
from kbtool import claims_db as cdb

from test_claims import store  # noqa: F401  (fixture)

SCHEMA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql")


def _db(tmp_path):
    con = cdb.connect(str(tmp_path / "kb.sqlite"))
    con.executescript(open(SCHEMA).read())
    cdb.ensure(con)
    return con


def _claim(con, text="misworded statement (L2)", label="fulltext", loc="2609.14218v1:MDPBH.tex:L2"):
    return cdb.add_claim(con, text, "result", "2609.14218", loc, label, "seeder", "tracks/A/note.md:1", "A-emd-pbh")


def _state(con, cid):
    return con.execute("SELECT c.label, m.status FROM claims c JOIN claim_meta m USING(claim_id) WHERE claim_id=?",
                       (cid,)).fetchone()


def test_supersede_with_new_text_links_history_and_locator_rows(store, tmp_path):  # noqa: F811
    st, _ = store
    con = _db(tmp_path)
    old = _claim(con)
    new = cdb.supersede(con, old, "kb-helper", "L2 says 'abstract one order below', not what the text says.",
                        text="The abstract line (L2) says the effect is one order below.",
                        locator="2609.14218v1:MDPBH.tex:L2", store=st)
    assert new != old
    assert _state(con, old) == ("refuted", "superseded")
    assert _state(con, new) == ("fulltext", "checked")
    # kind, paper and track come from the old claim
    assert con.execute("SELECT kind, paper_id, track_tags FROM claims WHERE claim_id=?", (new,)).fetchone() == \
        ("result", "2609.14218", "A-emd-pbh")
    # locator rows written at once, resolved, chunk set
    rows = con.execute("SELECT resolved, line_start FROM claim_locators WHERE claim_id=?", (new,)).fetchall()
    assert rows == [(1, 2)]
    assert con.execute("SELECT chunk_id FROM claims WHERE claim_id=?", (new,)).fetchone()[0] is not None
    # link and events both ways
    ln = cdb.links(con, old)
    assert len(ln) == 1 and ln[0]["relation"] == "superseded_by" and (ln[0]["from_id"], ln[0]["to_id"]) == (old, new)
    assert cdb.links(con, new) == ln
    ev_old = con.execute("SELECT action, from_label, to_label, to_status, evidence FROM claim_events "
                         "WHERE claim_id=? ORDER BY event_id", (old,)).fetchall()
    assert [e[0] for e in ev_old] == ["add", "supersede"]
    assert ev_old[-1][1:4] == ("fulltext", "refuted", "superseded") and f"claim {new}" in ev_old[-1][4]
    ev_new = [r[0] for r in con.execute("SELECT action FROM claim_events WHERE claim_id=? ORDER BY event_id", (new,))]
    assert ev_new == ["add", "supersedes"]
    # the old text is kept, never edited
    assert con.execute("SELECT text FROM claims WHERE claim_id=?", (old,)).fetchone()[0] == "misworded statement (L2)"


def test_supersede_by_existing_claim_and_refused_cases(store, tmp_path):  # noqa: F811
    st, _ = store
    con = _db(tmp_path)
    frag = _claim(con, text="and L2", loc="2609.14218v1:MDPBH.tex:L2")
    whole = _claim(con, text="The abstract line says one order below (L2).")
    other = _claim(con, text="another")
    assert cdb.supersede(con, frag, "kb-helper", "fragment: no statement; the row's sentence is claim %d" % whole,
                         to=whole) == whole
    assert _state(con, frag) == ("refuted", "superseded")
    assert _state(con, whole) == ("fulltext", "checked")
    with pytest.raises(ValueError, match="already superseded"):
        cdb.supersede(con, frag, "x", "again", to=other)
    with pytest.raises(ValueError, match="itself"):
        cdb.supersede(con, other, "x", "e", to=other)
    with pytest.raises(ValueError, match="cannot replace"):
        cdb.supersede(con, other, "x", "e", to=frag)              # a superseded claim replaces nothing
    with pytest.raises(ValueError, match="exactly one"):
        cdb.supersede(con, other, "x", "e")
    with pytest.raises(ValueError, match="exactly one"):
        cdb.supersede(con, other, "x", "e", text="t", to=whole)
    with pytest.raises(ValueError, match="evidence"):
        cdb.supersede(con, other, "x", "  ", to=whole)
    with pytest.raises(KeyError):
        cdb.supersede(con, 99999, "x", "e", to=whole)
    with pytest.raises(KeyError):
        cdb.supersede(con, other, "x", "e", to=99999)
    with pytest.raises(ValueError, match="does not resolve"):
        cdb.supersede(con, other, "x", "e", text="t", locator="2609.14218v1:MDPBH.tex:L5000", store=st)
    with pytest.raises(ValueError, match="needs a locator"):
        cdb.supersede(con, other, "x", "e", text="t")             # fulltext without a locator
    # nothing of the refused calls was written: `other` untouched, one link only
    assert _state(con, other) == ("fulltext", "checked")
    assert con.execute("SELECT count(*) FROM claim_links").fetchone()[0] == 1
    # a superseded claim can be neither verified nor refuted again
    with pytest.raises(ValueError):
        cdb.verify(con, frag, "x", "read")
    with pytest.raises(ValueError, match="superseded"):
        cdb.refute(con, frag, "x", "counter")


def test_refuted_claim_can_be_superseded_backfill_682(store, tmp_path):  # noqa: F811
    """The first case: 682 was refuted as worded and a new claim 862 written by hand (lead b13);
    supersede --to records the link and the status without touching the new claim's label."""
    st, _ = store
    con = _db(tmp_path)
    old = _claim(con)
    new = _claim(con, text="right wording")
    cdb.refute(con, old, "lead", "wrong as worded; superseded by claim %d" % new)
    assert _state(con, old) == ("refuted", "refuted")
    assert cdb.supersede(con, old, "kb-helper", "link of the lead's correction", to=new) == new
    assert _state(con, old) == ("refuted", "superseded")
    assert _state(con, new) == ("fulltext", "checked")


def test_cli_supersede_and_show(store, tmp_path, monkeypatch, capsys):  # noqa: F811
    """The subcommand writes through the writer lock into the working database and `show`
    names the claim that replaces the old one."""
    st, _ = store
    con = _db(tmp_path)
    old = _claim(con)
    con.commit()
    con.close()

    class Lay:
        db_work = str(tmp_path / "kb.sqlite")
        lock = str(tmp_path / "locks" / "kb-writer.lock")
    monkeypatch.setattr(claims_cli, "layout", lambda root=None: Lay)
    monkeypatch.setattr(claims_cli, "_store", lambda lay, con: st)
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root")
    sub = ap.add_subparsers(dest="cmd")
    claims_cli.register(sub)
    a = ap.parse_args(["claim", "--db", Lay.db_work, "supersede", str(old), "--by", "kb-helper", "--evidence",
                       "misworded", "--text", "right wording (L2)", "--locator", "2609.14218v1:MDPBH.tex:L2"])
    assert a.fn(a) == 0
    out = capsys.readouterr().out
    assert f"claim {old} superseded by claim" in out and "resolved 1" in out
    a = ap.parse_args(["claim", "--db", Lay.db_work, "show", str(old)])
    assert a.fn(a) == 0
    import json
    shown = json.loads(capsys.readouterr().out)
    assert shown["label"] == "refuted" and shown["status"] == "superseded"
    assert shown["superseded_by"] == [old + 1] and shown["links"][0]["relation"] == "superseded_by"
    # refusal: exit 1, nothing written
    a = ap.parse_args(["claim", "--db", Lay.db_work, "supersede", str(old), "--by", "x", "--evidence", "e",
                       "--to", str(old + 1)])
    assert a.fn(a) == 1
    c2 = sqlite3.connect(Lay.db_work)
    assert c2.execute("SELECT count(*) FROM claim_links").fetchone()[0] == 1
    assert ck is not None


def test_withdraw_a_heading_and_abstract_label_checked(store, tmp_path):  # noqa: F811
    """A heading split from a note row ("Abstract: line 171") is withdrawn, not superseded; a
    superseding claim labelled abstract with resolved locators is status checked (O4)."""
    st, _ = store
    con = _db(tmp_path)
    head = _claim(con, text="Abstract: line 2")
    cdb.withdraw(con, head, "kb-helper", "heading of the note row; the row has no statement on the abstract")
    assert _state(con, head) == ("refuted", "withdrawn")
    assert [r[0] for r in con.execute("SELECT action FROM claim_events WHERE claim_id=? ORDER BY event_id",
                                      (head,))] == ["add", "withdraw"]
    with pytest.raises(ValueError, match="already withdrawn"):
        cdb.withdraw(con, head, "x", "again")
    with pytest.raises(ValueError):
        cdb.supersede(con, head, "x", "e", text="t", locator="2609.14218v1:MDPBH.tex:L2", store=st)
    with pytest.raises(ValueError, match="withdrawn"):
        cdb.refute(con, head, "x", "counter")
    with pytest.raises(ValueError, match="evidence"):
        cdb.withdraw(con, _claim(con, text="x"), "x", "")
    frag = _claim(con, text="Abstract")
    new = cdb.supersede(con, frag, "kb-helper", "heading only; the row's sentence", label="abstract",
                        text="The abstract (L2) says the effect is one order below.",
                        locator="2609.14218v1:MDPBH.tex:L2", store=st)
    assert _state(con, new) == ("abstract", "checked")
    assert con.execute("SELECT verified_by FROM claims WHERE claim_id=?", (new,)).fetchone()[0] == "kb-helper"


def test_superseding_judgement_with_resolved_locator_is_located(store, tmp_path):  # noqa: F811
    st, _ = store
    con = _db(tmp_path)
    old = _claim(con, text="which are the X weights [JUDGEMENT]")
    new = cdb.supersede(con, old, "kb-helper", "cut text, judgement stored as fulltext", label="judgement",
                        text="The weights at L2 are the X weights [JUDGEMENT].",
                        locator="2609.14218v1:MDPBH.tex:L2", store=st)
    assert _state(con, new) == ("judgement", "located")


def test_supersede_to_existing_keeps_successor_checked_by(store, tmp_path):  # noqa: F811
    """Lead review batch 15: `--to` must not rewrite who checked the successor and when."""
    st, _ = store
    con = _db(tmp_path)
    old = _claim(con)
    succ = _claim(con, text="the sibling statement (L2)")
    con.execute("UPDATE claim_meta SET checked_by='first-reader', checked_at='2026-11-15T00:00:00Z'"
                " WHERE claim_id=?", (succ,))
    cdb.supersede(con, old, "kb-helper", "fragment; the sibling carries the row.", to=succ)
    assert con.execute("SELECT checked_by, checked_at FROM claim_meta WHERE claim_id=?",
                       (succ,)).fetchone() == ("first-reader", "2026-11-15T00:00:00Z")
    assert _state(con, old)[1] == "superseded"
    assert con.execute("SELECT count(*) FROM claim_events WHERE claim_id=? AND action='supersedes'",
                       (succ,)).fetchone()[0] == 1
