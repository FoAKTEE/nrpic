"""Shared helpers of the KB-G2 verifier (tracks/kb/verify_g2).

Read-only access to the frozen snapshot; nothing here writes to kb-data.
The raw store is read as bytes/text only (untrusted data, never executed).
"""
import os
import sqlite3

SNAP_ID = "kb-20261119-a782f1e"
SNAP = f"/data/haiyangw/nrpic/kb-data/db/{SNAP_ID}.sqlite"
KBDATA = "/data/haiyangw/nrpic/kb-data"
BUILD_TEX = os.path.join(KBDATA, "build", "tex")
RAW_ARXIV = os.path.join(KBDATA, "raw", "arxiv")


def open_ro(path=SNAP):
    """Open an sqlite file strictly read-only (URI mode=ro, immutable)."""
    con = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    return con


def id_dir(paper_id):
    return paper_id.replace("/", "_")


def read_text(path, limit=64 * 1024 * 1024):
    with open(path, "rb") as f:
        b = f.read(limit)
    return b.decode("utf-8", errors="replace")


def run_dir():
    d = os.environ.get("NRPIC_RUN_DIR")
    if not d:
        d = "/data/haiyangw/nrpic/scratch/kb/verify_g2/adhoc"
    os.makedirs(d, exist_ok=True)
    return d
