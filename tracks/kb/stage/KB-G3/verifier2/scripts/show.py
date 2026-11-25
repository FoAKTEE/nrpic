#!/usr/bin/env python3
"""Terminal reader: a claim, its locator lines from the raw source (or chunk text), events, links.

    python3 -I show.py [--window N] [--brief] CLAIM_ID [CLAIM_ID ...]

Paper text is printed to the terminal only; nothing is written. Read-only.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2lib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", type=int, nargs="+")
    ap.add_argument("--window", type=int, default=0)
    ap.add_argument("--maxloc", type=int, default=6)
    ap.add_argument("--width", type=int, default=400)
    ap.add_argument("--brief", action="store_true", help="no events")
    a = ap.parse_args()
    con = v2lib.connect()
    for cid in a.ids:
        d = v2lib.claim(con, cid)
        if d is None:
            print(f"=== {cid}: not in store")
            continue
        print(f"=== {cid} [{d['label']}/{d['status']}] track={d['track']} set_by={d['label_set_by']} "
              f"checked_by={d['checked_by']} kind={d['kind']} paper={d['paper_id']}")
        print("TEXT:", d["text"])
        if d.get("evidence"):
            print("EVIDENCE:", (d["evidence"] or "")[:a.width])
        for L in d["locators"][:a.maxloc]:
            print(f"  LOC {L['written']} resolved={L['resolved']} {L['problem'] or ''}")
            lines = v2lib.read_lines(L["paper_id"], L["version"], L["file"], L["line_start"] or 1,
                                     L["line_end"] or L["line_start"] or 1, a.window)
            if lines is None:
                for i, pid, kind, txt in v2lib.chunk_text(con, L["chunk_ids_json"]):
                    print(f"    [chunk {i} {kind}] {txt[:a.width * 2]}")
            else:
                for i, s in lines:
                    print(f"    {i:5d}: {s[:a.width]}")
        if len(d["locators"]) > a.maxloc:
            print(f"  ... {len(d['locators']) - a.maxloc} more locators")
        if not a.brief:
            for e in d["events"]:
                print(f"  EV {e['at']} {e['by']} {e['action']} {e['from_label']}->{e['to_label']} "
                      f"{e['from_status']}->{e['to_status']}: {(e['evidence'] or '')[:a.width]}")
        if d["links"]:
            print("  LINKS", d["links"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
