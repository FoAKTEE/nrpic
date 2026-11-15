"""The `kb` command: implemented subcommands on a synthetic store, stubs exit 3."""
import json
import os
import sqlite3
import subprocess
import sys

import pytest

from conftest import KB_DIR, TEX, make_tar
from kbtool import cli, db

KB = os.path.join(KB_DIR, "bin", "kb")


def run(argv):
    return cli.main(argv)


def test_no_stub_left():
    """Every subcommand of brief 12.10 is built (claim and qa wired in wave 2 by the lead)."""
    p = cli.parser()
    names = set(p._subparsers._group_actions[0].choices)
    assert {"claim", "qa", "search", "embed", "eq", "ingest"} <= names
    for name in ("claim", "qa"):
        a = p.parse_args([name] + (["stats"] if name == "claim" else ["golden"]))
        assert a.fn is not cli.cmd_stub
# `code`, `link`, `watch upstream`, `fetch-repos` and `ingest repo` are built (K6-K7):
# tests in test_code_*.py. `ingest arxiv`, `resolve-bib`, `frontier`, `cites`, `export` and the
# text views of `show` are built (K2-K3): tests in test_papers_*.py, test_tex_*.py, test_bib_*.py
# `embed`, `search` and `eq` are built (K4-K5): tests in test_embed_*.py
# `claim` (K8) and `qa` (K9) are built: tests in test_claims.py, test_qa_*.py


def test_init_verify_status_snapshot(store, capsys):
    store.manifest([("2611.12831", "G01", "3"), ("2111.05282", "G01", "3")], [("a/b", "ref", "-", "d")])
    store.add("2611.12831", make_tar([("main.tex", TEX)]), "v2")
    assert run(["--data-root", store.data, "init"]) == 0
    assert run(["--data-root", store.data, "verify-downloads", "--manifests", store.mdir,
                "--report", os.path.join(store.data, "rep.md")]) == 0
    out = capsys.readouterr().out
    assert "ok 1" in out and "missing 1" in out
    sums = open(os.path.join(store.data, "manifests", "SHA256SUMS")).read().split()
    assert sums[1] == "raw/arxiv/2611.12831/v2/source.bin"
    con = sqlite3.connect(store.layout.db_work)
    rows = dict(con.execute("SELECT paper_id, status FROM downloads").fetchall())
    assert rows == {"2611.12831": "ok", "2111.05282": "missing"}
    assert con.execute("SELECT status FROM repo_downloads").fetchone()[0] == "missing"
    assert con.execute("SELECT count(*) FROM ingest_log WHERE step='verify-downloads'").fetchone()[0] == 1
    con.close()
    assert run(["--data-root", store.data, "snapshot"]) == 0
    capsys.readouterr()
    assert run(["--data-root", store.data, "status", "--json"]) == 0
    st = json.loads(capsys.readouterr().out)
    assert st["schema_version_db"] == db.latest_version() and st["snapshot"].startswith("kb-")
    assert st["raw_arxiv_entries"] == 1 and st["rows"]["downloads"] == 2


def test_verify_exit_1_on_problem_and_no_record_writes_nothing(store, capsys):
    store.manifest([("2611.12831", "G01", "3")])
    vd = store.add("2611.12831", make_tar([("main.tex", TEX)]), "v1")
    with open(os.path.join(vd, "source.bin"), "ab") as f:
        f.write(b"x")
    assert run(["--data-root", store.data, "verify-downloads", "--manifests", store.mdir, "--no-record"]) == 1
    assert "PROBLEM 2611.12831" in capsys.readouterr().out
    assert not os.path.exists(os.path.join(store.data, "db"))
    assert not os.path.exists(os.path.join(store.data, "manifests"))


def test_fetch_missing_dry_run(store, capsys, tmp_path):
    store.manifest([("2611.12831", "G01", "3"), ("2111.05282", "G01", "3"), ("1109.0546", "G01", "2")])
    store.add("2611.12831", make_tar([("main.tex", TEX)]), "v1")
    ids = tmp_path / "ids.txt"
    assert run(["--data-root", store.data, "fetch-missing", "--priority", "3", "--dry-run",
                "--manifests", store.mdir, "--ids-file", str(ids)]) == 0
    assert ids.read_text() == "2111.05282\n"
    assert "1 ids of priority 3: 2111.05282" in capsys.readouterr().out


def test_show_download_record(store, capsys):
    store.manifest([("2611.12831", "G01", "3")])
    store.add("2611.12831", make_tar([("main.tex", TEX)]), "v1")
    # show reads the committed manifest for the row; the synthetic store gives the check
    assert run(["--data-root", store.data, "show", "arXiv:2611.12831"]) == 0
    res = json.loads(capsys.readouterr().out)
    assert res["status"] == "ok" and res["group"] == "G01" and res["priority"] == 3
    # the text views are K2 (kbtool.papers_cli); a paper that is not ingested gives exit 1
    assert run(["--data-root", store.data, "show", "2611.12831", "--abstract"]) == 1


def test_wrapper_runs_isolated_from_any_directory(store, tmp_path):
    out = subprocess.run([KB, "--version"], cwd=str(tmp_path), capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.startswith("kbtool ")
    out = subprocess.run([KB, "manifests", "--check"], cwd=str(tmp_path), capture_output=True, text=True)
    assert out.returncode == 0 and "identical" in out.stdout
