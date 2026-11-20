#!/usr/bin/env python3
"""Annotations and status refreshes in the claims layer that no kb command records.

    python3 -I tracks/kb/claims_tracks/scripts/annotate.py annotate FILE.tsv [--dry-run]
        FILE.tsv: claim_id <TAB> evidence (one row per annotation; '#' lines skipped).
        Inserts one claim_events row per line (action 'annotate', by 'kb-claims_tracks',
        label and status unchanged, from/to columns carry the current values).
    python3 -I tracks/kb/claims_tracks/scripts/annotate.py refresh ID [ID ...] [--dry-run]
        Hand-added claims (seed_key 'manual-*') are never re-checked by `kb claim check`.
        This recomputes their status from their stored locator string with the knowledge
        base's own check (kbtool.claims_check.check_claim: locators resolve, numbers found),
        writes claim_meta.status and status_detail and the locator rows' resolution, and
        records a claim_events row (action 'check'). Labels are never touched; a status
        'checked' (a person read the passage) is kept.

Writes only to kb-data/db/kb.sqlite, inside the writer lock (kbtool.lock.writer_lock), one
short transaction per call. Refuses claim ids that do not exist. Never deletes a claim.
Uses this worktree's kb/kbtool (read-only import of our own code; nothing under kb-data/raw is
imported or executed, only read as text by claims_check).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "kb"))

from kbtool import claims_check as ck  # noqa: E402
from kbtool import claims_db as cdb  # noqa: E402
from kbtool.lock import writer_lock  # noqa: E402
from kbtool.paths import layout  # noqa: E402

BY = "kb-claims_tracks"


def read_tsv(path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            cid, ev = line.split("\t", 1)
            out.append((int(cid), ev.strip()))
    return out


def cmd_annotate(a):
    rows = read_tsv(a.file)
    lay = layout()
    with writer_lock(lay, what="claims_tracks annotate"):
        con = cdb.connect(lay.db_work)
        try:
            con.execute("BEGIN")
            for cid, ev in rows:
                r = con.execute("SELECT c.label, m.status FROM claims c JOIN claim_meta m USING(claim_id) "
                                "WHERE claim_id=?", (cid,)).fetchone()
                if not r:
                    raise KeyError(f"no claim {cid}")
                cdb.event(con, cid, BY, "annotate", r[0], r[0], r[1], r[1], ev)
                print(f"claim {cid}: annotated ({r[0]}/{r[1]}): {ev[:100]}")
            if a.dry_run:
                con.rollback()
                print("dry run: rolled back")
            else:
                con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    return 0


def cmd_refresh(a):
    lay = layout()
    with writer_lock(lay, what="claims_tracks refresh"):
        con = cdb.connect(lay.db_work)
        store = ck.Store(lay.raw_arxiv, os.path.join(lay.build, "tex"), con)
        try:
            con.execute("BEGIN")
            for cid in a.ids:
                r = con.execute("SELECT c.text, c.locator, c.label, m.status, m.seed_key FROM claims c JOIN claim_meta m "
                                "USING(claim_id) WHERE claim_id=?", (cid,)).fetchone()
                if not r:
                    raise KeyError(f"no claim {cid}")
                text, loc, label, status, key = r
                if not (key or "").startswith("manual-"):
                    raise ValueError(f"claim {cid} is a seeded claim ({key}); use `kb claim check --id {cid}`")
                locs = cdb.parse_locator_string(loc) if loc else []
                new, detail, res = ck.check_claim(text, locs, store)
                keep = status in ("checked", "refuted")
                to = status if keep else new
                for k, (l, rr) in enumerate(zip(locs, res)):
                    con.execute("UPDATE claim_locators SET resolved=?, problem=?, flat_start=?, flat_end=?, "
                                "chunk_ids_json=? WHERE claim_id=? AND ord=?",
                                (int(bool(rr.resolved)), rr.problem, rr.flat_start, rr.flat_end,
                                 json.dumps(rr.chunk_ids), cid, k))
                con.execute("UPDATE claim_meta SET status=?, status_detail=? WHERE claim_id=?",
                            (to, json.dumps(detail), cid))
                cdb.event(con, cid, BY, "check", label, label, status, to,
                          "status refresh of a hand-added claim (claims_tracks/scripts/annotate.py refresh): "
                          + json.dumps(detail)[:1500])
                print(f"claim {cid}: {label} {status} -> {to}; detail {json.dumps(detail)[:300]}")
            if a.dry_run:
                con.rollback()
                print("dry run: rolled back")
            else:
                con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("annotate")
    s.add_argument("file")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_annotate)
    s = sub.add_parser("refresh")
    s.add_argument("ids", type=int, nargs="+")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(fn=cmd_refresh)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
