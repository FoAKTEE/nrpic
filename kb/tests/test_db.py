"""T5-T7: database creation and migration, snapshots, the writer lock."""
import hashlib
import multiprocessing as mp
import os
import sqlite3
import stat
import time

import pytest

from kbtool import db, lock


def test_init_creates_brief_schema_and_migrations(store):
    created, applied = db.init_db(store.layout)
    assert created and applied == [v for v, _ in db.migrations()]      # 2, 3, ...
    con = sqlite3.connect(store.layout.db_work)
    names = db.tables(con)
    assert db.EXPECTED_TABLES <= names and db.MIGRATION_TABLES <= names
    assert [r[0] for r in con.execute("SELECT version FROM schema_version ORDER BY version")] == \
        [1] + [v for v, _ in db.migrations()]
    assert con.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    # the FTS5 tables of the brief work
    con.execute("INSERT INTO papers(paper_id, title) VALUES ('2611.12831', 't')")
    con.execute("INSERT INTO chunks(paper_id, kind, text) VALUES ('2611.12831', 'body', 'Vlasov deposition onto the mesh')")
    con.execute("INSERT INTO chunks_fts(rowid, text) SELECT chunk_id, text FROM chunks")
    assert con.execute("SELECT count(*) FROM chunks_fts WHERE chunks_fts MATCH 'deposit'").fetchone()[0] == 1
    con.rollback()
    con.close()
    created, applied = db.init_db(store.layout)               # idempotent
    assert not created and applied == []
    con = sqlite3.connect(store.layout.db_work)
    assert con.execute("SELECT count(*) FROM schema_version").fetchone()[0] == 1 + len(db.migrations())
    con.close()


def test_foreign_keys_enforced(store):
    db.init_db(store.layout)
    con = db.connect_rw(store.layout.db_work)
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO sections(paper_id, title) VALUES ('nope', 'x')")
    con.close()


def test_snapshot_is_frozen_and_current_moves(store):
    db.init_db(store.layout)
    final, sha = db.snapshot(store.layout)
    name = os.path.basename(final)
    assert name.startswith("kb-" + time.strftime("%Y%m%d", time.gmtime())) and name.endswith(sha[:7] + ".sqlite")
    assert hashlib.sha256(open(final, "rb").read()).hexdigest() == sha
    assert stat.S_IMODE(os.stat(final).st_mode) == 0o444
    assert os.readlink(store.layout.db_current) == name
    ro = db.connect_ro(store.layout.db_current)
    assert ro.execute("SELECT max(version) FROM schema_version").fetchone()[0] == db.latest_version()
    with pytest.raises(sqlite3.OperationalError):
        ro.execute("INSERT INTO ingest_log(step) VALUES ('x')")
    ro.close()
    # a change in the working database gives a new snapshot; current follows
    con = db.connect_rw(store.layout.db_work)
    con.execute("INSERT INTO papers(paper_id, title) VALUES ('2611.12831', 't')")
    con.commit()
    con.close()
    final2, sha2 = db.snapshot(store.layout)
    assert sha2 != sha and os.readlink(store.layout.db_current) == os.path.basename(final2)
    assert os.path.exists(final)                                   # old snapshots are kept


def _hold(lay, ready, release):
    with lock.writer_lock(lay, what="test-holder"):
        ready.set()
        release.wait(30)


def test_writer_lock_excludes_second_writer(store):
    ctx = mp.get_context("fork")
    ready, release = ctx.Event(), ctx.Event()
    p = ctx.Process(target=_hold, args=(store.layout, ready, release))
    p.start()
    try:
        assert ready.wait(10)
        t0 = time.monotonic()
        with pytest.raises(lock.LockTimeout) as e:
            with lock.writer_lock(store.layout, timeout=1.0, poll=0.1):
                pass
        assert time.monotonic() - t0 >= 1.0
        assert f"pid {p.pid}" in str(e.value) and "test-holder" in str(e.value)
    finally:
        release.set()
        p.join(10)
    with lock.writer_lock(store.layout, timeout=5.0):
        pass
