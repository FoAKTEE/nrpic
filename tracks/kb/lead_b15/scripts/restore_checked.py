#!/usr/bin/env python3
"""Restore checked_by/checked_at of the five successor claims whose provenance the claims3
supersede step (`--to`) overwrote (lead review batch 15): 289, 313, 430, 624, 862.

The values come from snapshot kb-20261124-9872d21 (read-only). One transaction inside the kb
writer lock; an annotate event per claim records the repair. Only claim_meta.checked_by and
checked_at of these five claims are written.

    python -I restore_checked.py OUTDIR [--dry-run]
"""
import json, os, sqlite3, sys

WT = "/data/haiyangw/nrpic/wt/kb"
sys.path.insert(0, os.path.join(WT, "kb"))
from kbtool import claims_db as cdb  # noqa: E402
from kbtool.lock import writer_lock  # noqa: E402
from kbtool.paths import layout  # noqa: E402

SNAP = "/data/haiyangw/nrpic/kb-data/db/kb-20261124-9872d21.sqlite"
WORK = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"
IDS = (289, 313, 430, 624, 862)
BY = "kb-lead-b15"


def main(out, dry):
    os.makedirs(out, exist_ok=True)
    snap = sqlite3.connect(f"file:{SNAP}?mode=ro", uri=True)
    old = {k: snap.execute("SELECT checked_by, checked_at FROM claim_meta WHERE claim_id=?",
                           (k,)).fetchone() for k in IDS}
    rec = {"dry_run": dry, "restore": {}}
    lay = layout()
    with writer_lock(lay, what="lead b15 restore checked_by"):
        con = sqlite3.connect(WORK)
        try:
            con.execute("BEGIN")
            for k in IDS:
                now = con.execute("SELECT checked_by, checked_at FROM claim_meta WHERE claim_id=?",
                                  (k,)).fetchone()
                rec["restore"][k] = {"before": now, "after": old[k]}
                con.execute("UPDATE claim_meta SET checked_by=?, checked_at=? WHERE claim_id=?",
                            (old[k][0], old[k][1], k))
                cdb.event(con, k, BY, "annotate", evidence=(
                    "[lead review b15] checked_by/checked_at restored to the values of snapshot "
                    f"kb-20261124-9872d21 ({old[k][0]}, {old[k][1]}); the claims3 supersede step "
                    f"(--to) had replaced them with ({now[0]}, {now[1]}). Being the successor of a "
                    "superseded claim is not a reading of this claim; the supersedes event stays."))
            n_other = con.execute("SELECT count(*) FROM claim_meta WHERE checked_by='kb-claims3' AND"
                                  " claim_id IN (289,313,430,624,862)").fetchone()[0]
            rec["left_with_claims3_checked_by"] = n_other
            if dry:
                con.execute("ROLLBACK")
            else:
                con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        finally:
            con.close()
    json.dump(rec, open(os.path.join(out, "restore.json"), "w"), indent=1)
    print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], "--dry-run" in sys.argv[2:])
