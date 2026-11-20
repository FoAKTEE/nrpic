#!/usr/bin/env python3
"""Read-only reader for the claims_tracks package: print one or more claims with their
locator rows, history, and the cited lines (+- WINDOW) of the stored source.

    python3 -I tracks/kb/claims_tracks/scripts/read_claim.py [--window N] [--db PATH] ID [ID ...]

The source files under kb-data/raw are read as text only (never executed, imported or
compiled). What this prints stays in the terminal; it is never written to git.
Standard library only.
"""
import argparse
import json
import os
import re
import sqlite3
import sys

HOME = "/data/haiyangw/nrpic"
RAW = os.path.join(HOME, "kb-data", "raw", "arxiv")
DB = os.path.join(HOME, "kb-data", "db", "kb.sqlite")


def key_of(pid):
    return pid.replace("/", "_")


def versions(pid):
    d = os.path.join(RAW, key_of(pid))
    try:
        return sorted((v for v in os.listdir(d) if re.fullmatch(r"v\d+", v)), key=lambda v: int(v[1:]))
    except FileNotFoundError:
        return []


def lines_of(pid, ver, rel):
    if not pid or not rel or ".." in rel.split("/") or rel.startswith("/"):
        return None
    p = os.path.join(RAW, key_of(pid), ver or (versions(pid) or [""])[-1], "src", rel)
    if not os.path.isfile(p) or os.path.islink(p):
        return None
    with open(p, "rb") as f:
        return f.read(64 << 20).decode("utf-8", errors="replace").split("\n")


def show(con, cid, window):
    r = con.execute("SELECT c.claim_id, c.label, m.status, m.source_label, m.track, c.kind, c.paper_id, c.locator, "
                    "m.origin_ref, m.origin_path, m.origin_line, m.evidence, m.status_detail, m.label_set_by, "
                    "c.text FROM claims c JOIN claim_meta m USING(claim_id) WHERE claim_id=?", (cid,)).fetchone()
    if not r:
        print(f"== no claim {cid}")
        return
    (cid, label, status, src, track, kind, pid, loc, oref, opath, oline, ev, det, setby, text) = r
    print(f"== claim {cid} [{track}] label={label} status={status} source={src} kind={kind} set_by={setby}")
    print(f"   paper={pid} locator={loc}")
    print(f"   origin={oref}:{opath}:{oline}")
    if ev:
        print(f"   evidence(note)={ev[:400]}")
    try:
        d = json.loads(det or "{}")
        if d:
            print(f"   detail: numbers={d.get('numbers')} found={d.get('found')} missing={d.get('missing')} "
                  f"rounded={d.get('rounded')} notes={d.get('notes')} unresolved={d.get('unresolved')}")
    except ValueError:
        pass
    print(f"   TEXT: {text}")
    for ev_ in con.execute("SELECT at, by, action, from_label, to_label, from_status, to_status, substr(evidence,1,200) "
                           "FROM claim_events WHERE claim_id=? ORDER BY event_id", (cid,)):
        print(f"   event: {ev_}")
    for lr in con.execute("SELECT ord, paper_id, version, file, line_start, line_end, resolved, problem FROM "
                          "claim_locators WHERE claim_id=? ORDER BY ord", (cid,)):
        ordn, lp, lv, lf, a, b, ok, prob = lr
        print(f"   -- loc {ordn}: {lp}{lv}:{lf}:L{a}-{b} resolved={ok} problem={prob}")
        ls = lines_of(lp, lv, lf)
        if ls is None:
            print("      (file not readable)")
            continue
        lo = max(1, (a or 1) - window)
        hi = min(len(ls), (b or a or 1) + window)
        for k in range(lo, hi + 1):
            mark = ">" if a <= k <= b else " "
            print(f"   {mark}{k:5d}| {ls[k - 1][:400]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", type=int, nargs="+")
    ap.add_argument("--window", type=int, default=3)
    ap.add_argument("--db", default=DB)
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True, timeout=60)
    for cid in a.ids:
        show(con, cid, a.window)
    return 0


if __name__ == "__main__":
    sys.exit(main())
