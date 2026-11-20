#!/usr/bin/env python3
"""Ledger rows of a batch (read-only on kb.sqlite).

    python3 -I ledger.py snapshot decisions/<name>.tsv            > before.json
    python3 -I ledger.py rows decisions/<name>.tsv before.json RUN_ID > ledger_rows.tsv

Row columns (LEDGER.tsv): claim_id, track, label_before, status_before, label_after,
status_after, locator (after), evidence, reason, run_id. Standard library only.
"""
import json
import sqlite3
import sys

DB = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"


def decisions(path):
    out = []
    with open(path) as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t") + [""] * 5
            out.append((int(p[0]), p[1].strip(), p[2].strip(), p[3].strip(), p[4].strip()))
    return out


def state(ids):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=60)
    out = {}
    for cid in ids:
        r = con.execute("SELECT m.track, c.label, m.status, c.locator FROM claims c JOIN claim_meta m USING(claim_id) "
                        "WHERE claim_id=?", (cid,)).fetchone()
        out[str(cid)] = dict(zip(("track", "label", "status", "locator"), r)) if r else None
    con.close()
    return out


def clean(s):
    return (s or "").replace("\t", " ").replace("\n", " ")


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    dec = decisions(path)
    if cmd == "snapshot":
        json.dump(state([d[0] for d in dec]), sys.stdout, indent=1)
        return 0
    before = json.load(open(sys.argv[3]))
    run_id = sys.argv[4]
    after = state([d[0] for d in dec])
    for cid, action, loc, ev, reason in dec:
        b, a = before.get(str(cid)) or {}, after.get(str(cid)) or {}
        print("\t".join(clean(str(x)) for x in (cid, a.get("track"), b.get("label"), b.get("status"), a.get("label"),
                                                a.get("status"), a.get("locator") or "", f"[{action}] {ev}", reason,
                                                run_id)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
