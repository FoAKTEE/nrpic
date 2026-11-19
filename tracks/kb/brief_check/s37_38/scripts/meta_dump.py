"""Print title, authors and abstract of arXiv ids from the knowledge-base metadata.

Reads kb-data/meta/arxiv-api/<id>.json (written by harness/bin/nrpic-fetch-arxiv) and,
where present, kb-data/meta/inspire/<id>.json. Read-only; standard library only.
Run with: python3 -I meta_dump.py <id> [<id> ...]
"""
import json
import os
import sys

META = "/data/haiyangw/nrpic/kb-data/meta"


def load(kind, aid):
    for name in (aid, aid.replace("/", "_")):
        p = os.path.join(META, kind, name + ".json")
        if os.path.exists(p):
            with open(p) as fh:
                return json.load(fh), p
    return None, None


def main(ids):
    for aid in ids:
        rec, path = load("arxiv-api", aid)
        print("=" * 100)
        print(aid, "->", path)
        if rec is None:
            print("  (no arxiv-api record)")
            continue
        print("  title  :", rec.get("title"))
        au = rec.get("authors") or []
        print("  authors:", "; ".join(au[:8]) + (" ..." if len(au) > 8 else ""))
        for k in ("published", "updated", "journal_ref", "categories", "version"):
            if rec.get(k):
                print("  %-7s:" % k[:7], rec.get(k))
        print("  abstract:", (rec.get("abstract") or "").replace("\n", " "))


if __name__ == "__main__":
    main(sys.argv[1:])
