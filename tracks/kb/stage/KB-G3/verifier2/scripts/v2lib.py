"""Read-only access to the frozen snapshot for the second KB-G3 verifier (own code).

Opens kb-data/db/kb-20261125-2f97258.sqlite with mode=ro&immutable=1, reads raw TeX under
kb-data/raw/arxiv/<id with / -> _>/<version>/src/<file> as plain text (never executed), and
falls back to the chunk text of the store when a locator's file is not on disk (PDF papers).
Standard library only.
"""
import json
import os
import sqlite3

HOME = "/data/haiyangw/nrpic"
SNAP_ID = "kb-20261125-2f97258"
DB = os.path.join(HOME, "kb-data", "db", SNAP_ID + ".sqlite")
RAW = os.path.join(HOME, "kb-data", "raw", "arxiv")

POSITIVE = ("fulltext", "abstract", "title_only")
# label_set_by values of pipeline steps (claims3 README item 3; I keep the same four names)
PIPELINE_SETTERS = {"auto": "M", "kb-claims_tracks": "Q", "kb-claims_brief": "Q",
                    "kb-claims_brief (12.8 map)": "Q"}
# `by` values of events that record a person's reading of a claim against its own wording
PERSON_READ_BY = ("kb claims helper (manual read, audit P2)", "kb lead (wave 2), read at the source",
                  "kb lead (wave 2b)", "kb-lead-b13", "kb-claims3")
AUDIT_PREFIX = "[audit 2026-11-21"

# Item 1 of the task: claims written or changed since the first verifier
ITEM1 = {
    "A_new": list(range(862, 882)),
    "B_superseded_withdrawn": [29, 81, 84, 85, 126, 171, 179, 187, 192, 213, 277, 290, 314, 424,
                               431, 482, 549, 572, 619, 620, 621, 622, 623, 625, 682],
    "C_siblings": [289, 313, 430, 624],
    "D_seeds_named": [803, 805, 790, 409, 447, 449, 450, 452, 781, 804, 714, 809],
}


def connect(db=DB):
    return sqlite3.connect(f"file:{db}?mode=ro&immutable=1", uri=True)


def raw_path(paper_id, version, fname):
    return os.path.join(RAW, paper_id.replace("/", "_"), version or "", "src", fname or "")


def read_lines(paper_id, version, fname, a, b, window=0):
    p = raw_path(paper_id, version, fname)
    if not os.path.isfile(p):
        return None
    with open(p, "rb") as f:
        lines = f.read().decode("utf-8", "replace").splitlines()
    lo, hi = max(1, a - window), min(len(lines), b + window)
    return [(i, lines[i - 1]) for i in range(lo, hi + 1)]


def claim(con, cid):
    cols = ("claim_id", "text", "kind", "paper_id", "locator", "label", "origin", "track_tags",
            "verified_by", "verified_at", "supersedes")
    r = con.execute("SELECT %s FROM claims WHERE claim_id=?" % ",".join(cols), (cid,)).fetchone()
    if r is None:
        return None
    d = dict(zip(cols, r))
    mcols = ("status", "status_detail", "label_set_by", "checked_by", "checked_at", "track",
             "evidence", "source_label", "seed_key", "origin_path", "origin_line")
    m = con.execute("SELECT %s FROM claim_meta WHERE claim_id=?" % ",".join(mcols), (cid,)).fetchone()
    d.update(dict(zip(mcols, m)) if m else {})
    d["locators"] = [dict(zip(("ord", "paper_id", "version", "file", "line_start", "line_end",
                               "written", "resolved", "problem", "chunk_ids_json"), x))
                     for x in con.execute("SELECT ord,paper_id,version,file,line_start,line_end,written,"
                                          "resolved,problem,chunk_ids_json FROM claim_locators "
                                          "WHERE claim_id=? ORDER BY ord", (cid,))]
    d["events"] = [dict(zip(("at", "by", "action", "from_label", "to_label", "from_status",
                             "to_status", "evidence"), x))
                   for x in con.execute("SELECT at,by,action,from_label,to_label,from_status,to_status,"
                                        "evidence FROM claim_events WHERE claim_id=? ORDER BY event_id",
                                        (cid,))]
    d["links"] = con.execute("SELECT from_id,to_id,relation,by FROM claim_links WHERE from_id=? OR to_id=?",
                             (cid, cid)).fetchall()
    return d


def chunk_text(con, ids_json):
    try:
        ids = json.loads(ids_json or "[]")
    except ValueError:
        return []
    out = []
    for i in ids:
        r = con.execute("SELECT paper_id, kind, text FROM chunks WHERE chunk_id=?", (i,)).fetchone()
        if r:
            out.append((i, r[0], r[1], r[2]))
    return out


def person_read_ids(con):
    q = ("SELECT DISTINCT claim_id FROM claim_events WHERE by IN (%s) OR evidence LIKE ?"
         % ",".join("?" * len(PERSON_READ_BY)))
    return {r[0] for r in con.execute(q, PERSON_READ_BY + (AUDIT_PREFIX + "%",))}
