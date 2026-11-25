#!/usr/bin/env python3
"""Criterion C1 of KB-G3 recounted (own SQL): to_verify claims per track and their processing events.

    python3 -I queue_check.py --out DIR      # writes queue.json, queue_unprocessed.tsv

"Processed" here is my own reading of the gate (JOURNAL.md entry 1): an event whose action
changes or annotates the claim (anything but the seed itself). I list the actions found so the
package's narrower list (verify, refute, annotate, relocate, check, supersede, supersedes,
withdraw) can be compared. Also: db/current target, snapshot file sha256 prefix. Read-only.
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2lib  # noqa: E402

PKG_ACTIONS = ("verify", "refute", "annotate", "relocate", "check", "supersede", "supersedes", "withdraw")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--sha", action="store_true", help="hash the snapshot file (1 GB)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    con = v2lib.connect()
    actions = dict(con.execute("SELECT action, count(*) FROM claim_events GROUP BY action").fetchall())
    rows = con.execute("SELECT c.claim_id, m.track, m.status, c.text FROM claims c JOIN claim_meta m "
                       "USING(claim_id) WHERE c.label='to_verify' ORDER BY c.claim_id").fetchall()
    per_track, unproc = {}, []
    for cid, track, status, text in rows:
        acts = [r[0] for r in con.execute("SELECT action FROM claim_events WHERE claim_id=?", (cid,))]
        pkg = [x for x in acts if x in PKG_ACTIONS]
        t = per_track.setdefault(track, {"to_verify": 0, "processed_pkg_actions": 0, "any_event": 0})
        t["to_verify"] += 1
        t["processed_pkg_actions"] += bool(pkg)
        t["any_event"] += bool(acts)
        if not pkg:
            unproc.append((cid, track, status, ",".join(sorted(set(acts))) or "-", (text or "")[:140]))
    labels = {}
    for track, label, n in con.execute("SELECT m.track, c.label, count(*) FROM claims c JOIN claim_meta m "
                                       "USING(claim_id) GROUP BY 1,2"):
        labels.setdefault(track, {})[label] = n
    status = dict(con.execute("SELECT status, count(*) FROM claim_meta GROUP BY status").fetchall())
    cur = os.path.realpath(os.path.join(v2lib.HOME, "kb-data", "db", "current"))
    info = {"snapshot": v2lib.SNAP_ID, "db_current_target": cur,
            "n_claims": con.execute("SELECT count(*) FROM claims").fetchone()[0],
            "n_papers": con.execute("SELECT count(*) FROM papers").fetchone()[0],
            "event_actions": actions, "to_verify_per_track": per_track,
            "labels_per_track": labels, "status_counts": status,
            "unprocessed_ids": [u[0] for u in unproc]}
    if a.sha:
        h = hashlib.sha256()
        with open(v2lib.DB, "rb") as f:
            for blk in iter(lambda: f.read(1 << 22), b""):
                h.update(blk)
        info["snapshot_sha256"] = h.hexdigest()
    with open(os.path.join(a.out, "queue.json"), "w") as f:
        json.dump(info, f, indent=1)
    with open(os.path.join(a.out, "queue_unprocessed.tsv"), "w") as f:
        f.write("claim_id\ttrack\tstatus\tactions\ttext140\n")
        for u in unproc:
            f.write("\t".join(str(x).replace("\t", " ").replace("\n", " ") for x in u) + "\n")
    print(json.dumps({k: info[k] for k in ("db_current_target", "n_claims", "n_papers", "to_verify_per_track",
                                            "status_counts", "unprocessed_ids")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
