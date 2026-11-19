"""Wave-2b lead changes: claim locator rows follow a new locator string (claim 25 defect found by
the KB-G1 verifier), and the wiring of `kb meta`, `kb ingest pdf` and `kb search --rerank`."""
import sqlite3

import pytest

from kbtool import claims_check as CK
from kbtool import claims_db as CDB
from kbtool import cli


class FakeStore:
    """Resolves every locator of paper P to a flat range of 100 characters per line."""

    def resolve(self, loc):
        return CK.LocResult(paper_id=loc.paper_id, version=loc.version or "v1", file=loc.file,
                            line_start=loc.line_start, line_end=loc.line_end, resolved=loc.paper_id == "2609.14218",
                            problem="" if loc.paper_id == "2609.14218" else "not in store",
                            flat_start=100 * loc.line_start, flat_end=100 * (loc.line_end + 1), chunk_ids=[7])


def _db():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE claims(claim_id INTEGER PRIMARY KEY, text TEXT, kind TEXT, paper_id TEXT, locator TEXT,"
                " chunk_id INTEGER, quote_start INTEGER, quote_end INTEGER, label TEXT, origin TEXT, track_tags TEXT,"
                " verified_by TEXT, verified_at TEXT, supersedes INTEGER)")
    CDB.ensure(con)
    con.execute("INSERT INTO claims(claim_id, text, label, locator) VALUES (25, 'x', 'fulltext', "
                "'2609.14218v1:MDPBH.tex:L1101-1103')")
    con.execute("INSERT INTO claim_locators(claim_id, ord, paper_id, version, file, line_start, line_end, written, "
                "resolved) VALUES (25, 0, '2609.14218', 'v1', 'MDPBH.tex', 1101, 1103, 'L1101-1103', 1)")
    return con


def test_parse_locator_string_both_id_forms():
    locs = CDB.parse_locator_string("2609.14218v1:MDPBH.tex:L1084; gr-qc/9412071:main.tex:L3-5")
    assert [(l.paper_id, l.version, l.file, l.line_start, l.line_end) for l in locs] == [
        ("2609.14218", "v1", "MDPBH.tex", 1084, 1084), ("gr-qc/9412071", "", "main.tex", 3, 5)]
    with pytest.raises(ValueError):
        CDB.parse_locator_string("MDPBH.tex line 1084")


def test_relocate_rewrites_rows_and_keeps_label():
    con = _db()
    n, ok = CDB.relocate(con, 25, "2609.14218v1:MDPBH.tex:L1084; 2609.14218v1:MDPBH.tex:L1101-1103",
                         FakeStore(), "test")
    assert (n, ok) == (2, 2)
    rows = con.execute("SELECT ord, line_start, line_end, resolved, flat_start FROM claim_locators "
                       "WHERE claim_id=25 ORDER BY ord").fetchall()
    assert rows == [(0, 1084, 1084, 1, 108400), (1, 1101, 1103, 1, 110100)]
    assert con.execute("SELECT label, locator FROM claims WHERE claim_id=25").fetchone() == (
        "fulltext", "2609.14218v1:MDPBH.tex:L1084; 2609.14218v1:MDPBH.tex:L1101-1103")
    assert con.execute("SELECT action FROM claim_events WHERE claim_id=25").fetchall() == [("relocate",)]


def test_relocate_unknown_claim_and_unresolved_part():
    con = _db()
    with pytest.raises(KeyError):
        CDB.relocate(con, 99, "2609.14218v1:MDPBH.tex:L1", FakeStore(), "test")
    n, ok = CDB.relocate(con, 25, "2609.14218v1:MDPBH.tex:L1; 1111.11111v1:a.tex:L2", FakeStore(), "test")
    assert (n, ok) == (2, 1)


def test_cli_parses_new_commands():
    p = cli.parser()
    a = p.parse_args(["meta", "load", "--id", "gr-qc/9412071"])
    assert a.fn is cli.cmd_stub and a.args == ["load", "--id", "gr-qc/9412071"]
    a = p.parse_args(["search", "--rerank", "deposition order"])
    assert a.rerank and a.query == "deposition order"
    a = p.parse_args(["claim", "relocate", "25", "--locator", "2609.14218v1:MDPBH.tex:L1084", "--by", "t"])
    assert a.claim_id == 25
