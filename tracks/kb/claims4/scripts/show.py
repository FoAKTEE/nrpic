#!/usr/bin/env python3
"""Print claims with the source lines at each of their locator rows, for reading (terminal only).

    python3 -I show.py ID [ID ...] [--ctx 1] [--width 600] [--siblings] [--db PATH]

For each claim: id, label, status, track, paper, locator, full text, then for every locator row
the lines line_start-ctx .. line_end+ctx of the stored TeX file (kb-data/raw/arxiv/<id>/<v>/src),
read as text, each line cut to --width characters. Nothing is written; nothing under kb-data/raw
is executed, imported or compiled. Standard library only.
"""
import argparse
import os
import sqlite3

RAW = "/data/haiyangw/nrpic/kb-data/raw/arxiv"
DB = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"


def lines_of(pid, ver, fn):
    p = os.path.join(RAW, pid.replace("/", "_"), ver, "src", fn)
    if not os.path.isfile(p):
        return None
    with open(p, errors="replace") as f:
        return f.read().split("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+", type=int)
    ap.add_argument("--ctx", type=int, default=1)
    ap.add_argument("--width", type=int, default=600)
    ap.add_argument("--max-lines", type=int, default=40)
    ap.add_argument("--siblings", action="store_true")
    ap.add_argument("--db", default=DB)
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    for cid in a.ids:
        r = con.execute("SELECT c.label, m.status, m.track, c.paper_id, c.locator, c.text, m.origin_path, "
                        "m.origin_line FROM claims c JOIN claim_meta m USING(claim_id) WHERE claim_id=?",
                        (cid,)).fetchone()
        if not r:
            print(f"== {cid}: no such claim")
            continue
        label, status, track, pid, loc, text, opath, oline = r
        print(f"== {cid} [{label}/{status}] {track} {pid} | origin {opath}:{oline}")
        print(f"   locator: {loc}")
        print(f"   TEXT: {text}")
        if a.siblings and opath:
            for sid, stext, slab, sst in con.execute(
                    "SELECT c.claim_id, c.text, c.label, m.status FROM claims c JOIN claim_meta m USING(claim_id) "
                    "WHERE m.origin_path=? AND m.origin_line=? AND c.claim_id<>? ORDER BY c.claim_id",
                    (opath, oline, cid)):
                print(f"   sibling {sid} [{slab}/{sst}]: {stext[:300]}")
        for lp, lv, lf, l0, l1 in con.execute(
                "SELECT paper_id, version, file, line_start, line_end FROM claim_locators WHERE claim_id=? "
                "ORDER BY ord", (cid,)):
            src = lines_of(lp, lv, lf) if lp and lv and lf else None
            if src is None or not l0:
                print(f"   -- {lp}{lv}:{lf}:L{l0}-{l1}: (file not found)")
                continue
            l1 = l1 or l0
            lo, hi = max(1, l0 - a.ctx), min(len(src), l1 + a.ctx)
            if hi - lo + 1 > a.max_lines:
                hi = lo + a.max_lines - 1
            print(f"   -- {lp}{lv}:{lf}:L{l0}-{l1}")
            for i in range(lo, hi + 1):
                mark = ">" if l0 <= i <= l1 else " "
                print(f"   {mark}{i}: {src[i - 1][:a.width]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
