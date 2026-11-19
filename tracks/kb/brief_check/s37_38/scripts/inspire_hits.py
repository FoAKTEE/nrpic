"""Print the hits of stored INSPIRE query results (kb-data/meta/inspire/query/<sha>.json).

Usage: python3 -I inspire_hits.py <query-file> [...]
For each hit: arXiv id, earliest date, first author, title (and the abstract with -a).
Read-only; standard library only; the files are data written by harness/bin/nrpic-fetch-arxiv.
"""
import json
import sys


def hits_of(d):
    for key in ("response", "result", "data"):
        if isinstance(d.get(key), dict):
            d = d[key]
    h = d.get("hits")
    if isinstance(h, dict):
        return h.get("total"), h.get("hits") or []
    return None, h or []


def main(args):
    show_abs = "-a" in args
    for path in [a for a in args if a != "-a"]:
        d = json.load(open(path))
        q = d.get("query") or d.get("q")
        total, hits = hits_of(d)
        print("=" * 90)
        print(path.split("/")[-1], "| query:", q, "| total:", total, "| in file:", len(hits))
        for h in hits:
            m = h.get("metadata", h)
            ids = [e.get("value") for e in m.get("arxiv_eprints", [])]
            title = (m.get("titles") or [{}])[0].get("title", "")
            au = (m.get("authors") or [{}])[0].get("full_name", "")
            date = m.get("earliest_date") or m.get("preprint_date") or ""
            print("  %-12s %-10s %-24s %s" % (ids[0] if ids else "-", date, au[:24], title[:150]))
            if show_abs:
                ab = (m.get("abstracts") or [{}])[0].get("value", "")
                print("      ", ab[:900].replace("\n", " "))


if __name__ == "__main__":
    main(sys.argv[1:])
