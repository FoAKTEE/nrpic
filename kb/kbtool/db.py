"""The database: creation from kb/schema.sql, connections, snapshots.

Writers (the kb session only) open db/kb.sqlite inside the writer lock; readers open
db/current (a frozen snapshot) read-only. A snapshot is a copy made with the SQLite backup
API, named kb-YYYYMMDD-<sha7>.sqlite after the sha256 of its bytes, made read-only, and
`current` is moved to it atomically.
"""
import hashlib
import json
import os
import re
import sqlite3
import time

from . import SCHEMA_VERSION, __version__
from .lock import writer_lock
from .paths import migrations_dir, schema_path

EXPECTED_TABLES = {
    "schema_version", "papers", "sections", "chunks", "chunks_fts", "equations", "equations_fts",
    "figures", "bib_entries", "citations", "repos", "code_files", "symbols", "code_chunks",
    "code_fts", "params", "impl_links", "claims", "embeddings", "ingest_log"}
MIGRATION_TABLES = {"downloads", "repo_downloads"}       # migration 0002


def utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def connect_rw(path):
    con = sqlite3.connect(path, timeout=60)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def connect_ro(path):
    con = sqlite3.connect(f"file:{os.path.abspath(path)}?mode=ro", uri=True, timeout=60)
    return con


def tables(con):
    return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table')")}


def schema_version(con):
    try:
        r = con.execute("SELECT max(version) FROM schema_version").fetchone()
        return r[0]
    except sqlite3.Error:
        return None


def migrations():
    """[(version, path)] of kb/migrations/NNNN_*.sql, version > 1, in order."""
    out = []
    d = migrations_dir()
    for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        m = re.match(r"^(\d{4})_[A-Za-z0-9_]+\.sql$", n)
        if m and int(m.group(1)) > 1:
            out.append((int(m.group(1)), os.path.join(d, n)))
    return out


def latest_version():
    return max([SCHEMA_VERSION] + [v for v, _ in migrations()])


def migrate(con):
    """Apply the migrations newer than the database. Returns the versions applied."""
    have = schema_version(con) or 0
    done = []
    for v, path in migrations():
        if v <= have:
            continue
        con.executescript("BEGIN;\n" + open(path).read() +
                          f"\nINSERT INTO schema_version(version, applied_at) VALUES ({v}, '{utcnow()}');\nCOMMIT;")
        log(con, "migrate", os.path.basename(path), "ok", f"schema version {v}")
        con.commit()
        done.append(v)
    return done


def init_db(lay):
    """Create kb.sqlite from kb/schema.sql (version 1) and apply kb/migrations. Idempotent.
    Returns (created, versions applied)."""
    os.makedirs(lay.db_dir, exist_ok=True)
    with writer_lock(lay, what="init-db"):
        con = connect_rw(lay.db_work)
        try:
            if "schema_version" not in tables(con):
                con.executescript(open(schema_path()).read())
                con.execute("INSERT INTO schema_version(version, applied_at) VALUES (?, ?)",
                            (SCHEMA_VERSION, utcnow()))
                log(con, "init-db", lay.db_work, "ok", f"schema version {SCHEMA_VERSION}")
                con.commit()
                created = True
            else:
                created = False
            applied = migrate(con)
            missing = (EXPECTED_TABLES | MIGRATION_TABLES) - tables(con)
            if missing:
                raise RuntimeError(f"database {lay.db_work} lacks tables {sorted(missing)}")
            return created, applied
        finally:
            con.close()


def record_inventory(lay, inv):
    """Rewrite the downloads and repo_downloads tables from an inventory, in one
    transaction. The CALLER holds the writer lock (flock is per open file, so taking it
    again here from a second descriptor would block on ourselves)."""
    tv = f"kbtool {__version__}"
    con = connect_rw(lay.db_work)
    try:
        con.execute("BEGIN")
        con.execute("DELETE FROM downloads")
        con.execute("DELETE FROM repo_downloads")
        for p in inv["papers"] + inv["extras"]:
            path = (os.path.join("raw", "arxiv", p["key"], p["current"], "source.bin")
                    if p.get("current") else None)
            con.execute(
                "INSERT INTO downloads(paper_id, in_manifest, grp, priority, status, version, version_source, "
                "versions_present_json, path, sha256, bytes, sniffed_kind, source_kind, n_files, src_bytes, "
                "problems_json, notes_json, fetched_utc, checked_at, tool_version) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (p["id"], int(p["in_manifest"]), p["group"], p["priority"], p["status"],
                 p.get("version"), p.get("version_source"), json.dumps(p["versions_present"]),
                 path, p.get("sha256"), p.get("bytes"), p.get("sniffed_kind"), p.get("source_kind"),
                 p.get("n_files"), p.get("src_bytes"), json.dumps(p["problems"]), json.dumps(p["notes"]),
                 p.get("fetched_utc"), inv["checked_at"], tv))
        for r in inv["repos"]:
            con.execute("INSERT INTO repo_downloads(repo_id, role, owners, status, commit_sha, head_ref, "
                        "license_spdx_guess, problems_json, notes_json, checked_at, tool_version) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (r["repo"], r["role"], r["owners"], r["status"], r.get("commit_sha"),
                         r.get("head_ref"), r.get("license_spdx_guess"), json.dumps(r["problems"]),
                         json.dumps(r["notes"]), inv["checked_at"], tv))
        a = inv["arxiv"]["status"]
        log(con, "verify-downloads", lay.data, "ok",
            json.dumps({"arxiv": a, "extra": inv["arxiv"]["extra"], "github": inv["github"]["status"]}))
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def log(con, step, target, status, message):
    con.execute("INSERT INTO ingest_log(at, step, target, status, message, tool_version) "
                "VALUES (?, ?, ?, ?, ?, ?)", (utcnow(), step, target, status, message,
                                               f"kbtool {__version__}"))


def open_for_read(lay, which=None):
    """Path of the database a reader uses: `which` if given, else db/current, else kb.sqlite."""
    if which:
        return which
    if os.path.exists(lay.db_current):
        return lay.db_current
    return lay.db_work


def snapshot(lay):
    """Freeze kb.sqlite into kb-YYYYMMDD-<sha7>.sqlite and point `current` at it."""
    if not os.path.exists(lay.db_work):
        raise FileNotFoundError(lay.db_work)
    with writer_lock(lay, what="snapshot"):
        tmp = os.path.join(lay.db_dir, f".snapshot-{os.getpid()}.sqlite")
        src = connect_rw(lay.db_work)
        dst = sqlite3.connect(tmp)
        try:
            src.backup(dst)
            dst.execute("PRAGMA journal_mode = DELETE")     # a snapshot is a single file
            dst.commit()
        finally:
            dst.close()
            src.close()
        sha = hashlib.sha256(open(tmp, "rb").read()).hexdigest()
        name = f"kb-{time.strftime('%Y%m%d', time.gmtime())}-{sha[:7]}.sqlite"
        final = os.path.join(lay.db_dir, name)
        if os.path.exists(final):
            os.remove(tmp)
        else:
            os.replace(tmp, final)
            os.chmod(final, 0o444)
        link_tmp = os.path.join(lay.db_dir, f".current-{os.getpid()}")
        if os.path.lexists(link_tmp):
            os.remove(link_tmp)
        os.symlink(name, link_tmp)
        os.replace(link_tmp, lay.db_current)
        con = connect_rw(lay.db_work)
        try:
            log(con, "snapshot", name, "ok", f"sha256 {sha}")
            con.commit()
        finally:
            con.close()
        return final, sha
