"""K8 storage: the claims table of brief 12.2 plus three side tables.

The schema's `claims` table holds the statement, its kind, paper, locator, chunk, quote
range, label, origin, track tags and who verified it when. A track's note gives several
locators for one statement, a status of the knowledge base's own check and a history of
changes; these live beside it (created here with IF NOT EXISTS, so that no migration
number is taken; the lead may move CLAIMS_DDL into kb/migrations/):

    claim_meta      one row per claim: stable seed key, the label as the note wrote it,
                    track, origin (ref, commit, path, line), status of the check and who
                    set the label
    claim_locators  every locator of a claim, resolved or not, with its flat.tex range
    claim_events    seed, check, verify, refute, stale: who, when, from and to

Labels (brief 12.8): fulltext, abstract, title_only, background, judgement, to_verify,
refuted. A judgement is never upgraded to fulltext. Statuses of the check: located (every
locator resolves and every quoted number is in the cited lines), partial (locators
resolve, some number not found), unresolved (a locator does not resolve), unlocated (no
locator), checked (a person read the passage), refuted, stale (gone from its note).

Every write happens inside the caller's writer lock (kbtool.lock.writer_lock).
"""
import json
import sqlite3
import time

CLAIMS_DDL = """
CREATE TABLE IF NOT EXISTS claim_meta(
  claim_id INTEGER PRIMARY KEY REFERENCES claims(claim_id),
  seed_key TEXT UNIQUE, source_label TEXT, track TEXT,
  origin_ref TEXT, origin_commit TEXT, origin_path TEXT, origin_line INTEGER, section TEXT,
  evidence TEXT, status TEXT, status_detail TEXT, label_set_by TEXT,
  checked_by TEXT, checked_at TEXT, seeded_at TEXT);
CREATE TABLE IF NOT EXISTS claim_locators(
  loc_id INTEGER PRIMARY KEY, claim_id INTEGER NOT NULL REFERENCES claims(claim_id), ord INTEGER,
  paper_id TEXT, version TEXT, file TEXT, line_start INTEGER, line_end INTEGER, written TEXT,
  resolved INTEGER, problem TEXT, flat_start INTEGER, flat_end INTEGER, chunk_ids_json TEXT);
CREATE TABLE IF NOT EXISTS claim_events(
  event_id INTEGER PRIMARY KEY, claim_id INTEGER NOT NULL REFERENCES claims(claim_id), at TEXT, by TEXT,
  action TEXT, from_label TEXT, to_label TEXT, from_status TEXT, to_status TEXT, evidence TEXT);
CREATE INDEX IF NOT EXISTS claim_locators_claim ON claim_locators(claim_id);
CREATE INDEX IF NOT EXISTS claim_locators_paper ON claim_locators(paper_id);
CREATE INDEX IF NOT EXISTS claim_events_claim ON claim_events(claim_id);
CREATE INDEX IF NOT EXISTS claims_paper ON claims(paper_id);
"""

LABELS = ("fulltext", "abstract", "title_only", "background", "judgement", "to_verify", "refuted")
STATUSES = ("located", "partial", "unresolved", "unlocated", "checked", "refuted", "stale")
SOURCE_TO_LABEL = {"BACKGROUND": "background", "JUDGEMENT": "judgement", "TO VERIFY": "to_verify",
                   "UNLABELLED": "to_verify", "UNLOCATED": "to_verify"}
AUTO = "auto"


def utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure(con):
    con.executescript(CLAIMS_DDL)


def label_for(source_label, status):
    """Label the automatic check may give. A statement the track read at the source
    becomes fulltext only when the knowledge base's own check located it."""
    if source_label.startswith("VERIFIED"):
        return "fulltext" if status == "located" else "to_verify"
    return SOURCE_TO_LABEL.get(source_label, "to_verify")


def locator_string(locs):
    return "; ".join(f"{l.paper_id}{l.version}:{l.file}:L{l.line_start}" +
                     (f"-{l.line_end}" if l.line_end != l.line_start else "") for l in locs)


def event(con, cid, by, action, from_label=None, to_label=None, from_status=None, to_status=None, evidence=""):
    con.execute("INSERT INTO claim_events(claim_id, at, by, action, from_label, to_label, from_status, to_status, "
                "evidence) VALUES (?,?,?,?,?,?,?,?,?)",
                (cid, utcnow(), by, action, from_label, to_label, from_status, to_status, evidence))


def upsert_seed(con, seed, commit, checked, by, tool):
    """Insert or refresh one seed with its check. checked = (status, detail, [LocResult]).
    Returns (claim_id, 'new' | 'same' | 'changed')."""
    status, detail, res = checked
    key = seed.seed_key()
    row = con.execute("SELECT m.claim_id, c.label, m.status, m.label_set_by FROM claim_meta m "
                      "JOIN claims c USING(claim_id) WHERE m.seed_key=?", (key,)).fetchone()
    first = next((r for r in res if r.resolved), None)
    chunk = first.chunk_ids[0] if first and first.chunk_ids else None
    qs, qe = (first.flat_start, first.flat_end) if first else (None, None)
    pid = (first.paper_id if first else seed.paper_id) or None
    locs_resolved = []
    for l, r in zip(seed.locators, res or [None] * len(seed.locators)):
        if r is not None and r.resolved:
            l2 = type(l)(r.paper_id, r.version, r.file, l.line_start, l.line_end, l.raw, l.pos)
            locs_resolved.append(l2)
        else:
            locs_resolved.append(l)
    loc_text = locator_string(locs_resolved) or None
    now = utcnow()
    origin = f"{seed.origin_ref}@{commit[:7]}:{seed.origin_path}:{seed.origin_line}"
    if row is None:
        label = label_for(seed.label, status)
        verified_by = f"{seed.track} (read at the source); {tool}" if label == "fulltext" else None
        cur = con.execute(
            "INSERT INTO claims(text, kind, paper_id, locator, chunk_id, quote_start, quote_end, label, origin, "
            "track_tags, verified_by, verified_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (seed.text, seed.kind, pid, loc_text, chunk, qs, qe, label, origin, seed.track, verified_by,
             now if verified_by else None))
        cid = cur.lastrowid
        con.execute("INSERT INTO claim_meta(claim_id, seed_key, source_label, track, origin_ref, origin_commit, "
                    "origin_path, origin_line, section, evidence, status, status_detail, label_set_by, checked_by, "
                    "checked_at, seeded_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, key, seed.label, seed.track, seed.origin_ref, commit, seed.origin_path, seed.origin_line,
                     seed.section, seed.evidence, status, json.dumps(detail), AUTO, by, now, now))
        event(con, cid, by, "seed", None, label, None, status, origin)
        what = "new"
    else:
        cid, old_label, old_status, set_by = row
        con.execute("UPDATE claim_meta SET origin_commit=?, origin_line=?, section=?, checked_by=?, checked_at=? "
                    "WHERE claim_id=?", (commit, seed.origin_line, seed.section, by, now, cid))
        what = "same"
        if set_by == AUTO:
            label = label_for(seed.label, status)
            if (label, status) != (old_label, old_status):
                verified_by = f"{seed.track} (read at the source); {tool}" if label == "fulltext" else None
                con.execute("UPDATE claims SET label=?, verified_by=?, verified_at=?, locator=?, chunk_id=?, "
                            "quote_start=?, quote_end=?, paper_id=? WHERE claim_id=?",
                            (label, verified_by, now if verified_by else None, loc_text, chunk, qs, qe, pid, cid))
                con.execute("UPDATE claim_meta SET status=?, status_detail=? WHERE claim_id=?",
                            (status, json.dumps(detail), cid))
                event(con, cid, by, "check", old_label, label, old_status, status, json.dumps(detail)[:2000])
                what = "changed"
        con.execute("DELETE FROM claim_locators WHERE claim_id=?", (cid,))
    for k, (l, r) in enumerate(zip(seed.locators, res or [None] * len(seed.locators))):
        con.execute("INSERT INTO claim_locators(claim_id, ord, paper_id, version, file, line_start, line_end, written, "
                    "resolved, problem, flat_start, flat_end, chunk_ids_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, k, (r.paper_id if r and r.paper_id else l.paper_id), (r.version if r else l.version),
                     (r.file if r and r.file else l.file), l.line_start, l.line_end, l.raw,
                     int(bool(r and r.resolved)), (r.problem if r else "not checked"),
                     (r.flat_start if r else None), (r.flat_end if r else None),
                     json.dumps(r.chunk_ids if r else [])))
    return cid, what


def mark_stale(con, origin_path, keep_keys, by):
    """Claims of a note that are no longer in it: status stale (never deleted)."""
    n = 0
    for cid, key, st in con.execute("SELECT claim_id, seed_key, status FROM claim_meta WHERE origin_path=?",
                                    (origin_path,)).fetchall():
        if key not in keep_keys and st != "stale":
            con.execute("UPDATE claim_meta SET status='stale' WHERE claim_id=?", (cid,))
            event(con, cid, by, "stale", None, None, st, "stale", "no longer in the note")
            n += 1
    return n


def add_claim(con, text, kind, paper_id, locator, label, by, origin, track, evidence=""):
    """A statement added by hand (`kb claim add`): status unlocated until checked."""
    if label not in LABELS:
        raise ValueError(f"label must be one of {LABELS}")
    if label == "fulltext" and not locator:
        raise ValueError("a fulltext claim needs a locator")
    now = utcnow()
    cur = con.execute("INSERT INTO claims(text, kind, paper_id, locator, label, origin, track_tags, verified_by, "
                      "verified_at) VALUES (?,?,?,?,?,?,?,?,?)",
                      (text, kind, paper_id, locator, label, origin, track,
                       by if label == "fulltext" else None, now if label == "fulltext" else None))
    cid = cur.lastrowid
    con.execute("INSERT INTO claim_meta(claim_id, seed_key, source_label, track, origin_path, evidence, status, "
                "status_detail, label_set_by, checked_by, checked_at, seeded_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid, f"manual-{cid}", label.upper(), track, origin, evidence,
                 "checked" if label == "fulltext" else "unlocated", "{}", by, by, now, now))
    event(con, cid, by, "add", None, label, None, None, evidence)
    return cid


def verify(con, cid, by, evidence, locator=None):
    """A person read the passage and it supports the claim: fulltext, status checked."""
    row = con.execute("SELECT c.label, m.status, m.source_label, c.locator FROM claims c JOIN claim_meta m "
                      "USING(claim_id) WHERE claim_id=?", (cid,)).fetchone()
    if not row:
        raise KeyError(cid)
    label, status, src, loc = row
    if label == "judgement" or src == "JUDGEMENT":
        raise ValueError("a judgement is never upgraded to fulltext (brief 12.8); computed results decide it")
    if label == "refuted":
        raise ValueError("refuted claim: add a new claim that supersedes it")
    loc = locator or loc
    if not loc:
        raise ValueError("verify needs a locator")
    now = utcnow()
    con.execute("UPDATE claims SET label='fulltext', locator=?, verified_by=?, verified_at=? WHERE claim_id=?",
                (loc, by, now, cid))
    con.execute("UPDATE claim_meta SET status='checked', label_set_by=?, checked_by=?, checked_at=? WHERE claim_id=?",
                (by, by, now, cid))
    event(con, cid, by, "verify", label, "fulltext", status, "checked", evidence)


def refute(con, cid, by, evidence):
    """A counter-example was found: refuted. Returns the tracks to notify."""
    row = con.execute("SELECT c.label, m.status, c.track_tags FROM claims c JOIN claim_meta m USING(claim_id) "
                      "WHERE claim_id=?", (cid,)).fetchone()
    if not row:
        raise KeyError(cid)
    label, status, tracks = row
    now = utcnow()
    con.execute("UPDATE claims SET label='refuted', verified_by=?, verified_at=? WHERE claim_id=?", (by, now, cid))
    con.execute("UPDATE claim_meta SET status='refuted', label_set_by=?, checked_by=?, checked_at=? WHERE claim_id=?",
                (by, by, now, cid))
    event(con, cid, by, "refute", label, "refuted", status, "refuted", evidence)
    return sorted({t for t in (tracks or "").split(",") if t})


def rows(con, where="", args=()):
    sql = ("SELECT c.claim_id, c.label, m.status, m.source_label, c.kind, c.paper_id, c.locator, m.track, "
           "c.verified_by, c.verified_at, c.chunk_id, m.origin_path, m.origin_line, c.text, m.status_detail, "
           "m.checked_by, m.evidence FROM claims c LEFT JOIN claim_meta m USING(claim_id) ")
    if where:
        sql += "WHERE " + where
    sql += " ORDER BY c.claim_id"
    cols = ("claim_id", "label", "status", "source_label", "kind", "paper_id", "locator", "track", "verified_by",
            "verified_at", "chunk_id", "origin_path", "origin_line", "text", "status_detail", "checked_by", "evidence")
    return [dict(zip(cols, r)) for r in con.execute(sql, args)]


def has_tables(con):
    names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    return {"claims", "claim_meta", "claim_locators", "claim_events"} <= names


def connect(path, ro=False):
    if ro:
        return sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=60)
    con = sqlite3.connect(path, timeout=120)
    con.execute("PRAGMA foreign_keys = ON")
    return con
