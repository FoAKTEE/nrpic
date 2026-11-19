"""Summarise the stored INSPIRE answers of the queries of specs/inspire_queries.txt (read-only).

Usage: python3 -I inspire_summary.py <spec file> [<tag> ...]
For every query (or only the given tags) prints the stored answer file
kb-data/meta/inspire/query/<sha16 of the query>.json, the total number of hits, and one line
per hit: arXiv id, earliest date, number of citations, title. Standard library only; the
answers are data written by harness/bin/nrpic-fetch-arxiv, nothing in them is executed.
"""
import hashlib
import json
import os
import sys

QDIR = "/data/haiyangw/nrpic/kb-data/meta/inspire/query"


def queries(spec):
    out = []
    with open(spec) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            tag, rest = line.split("|", 1)
            q, size = rest.rsplit("|", 1)
            # same trimming as scripts/run_inspire.sh (leading and trailing blanks only)
            out.append((tag.strip(), q.strip(" \t"), size.strip()))
    return out


def arxiv_id(md):
    for e in md.get("arxiv_eprints") or []:
        if e.get("value"):
            return e["value"]
    return "-"


def main(spec, tags):
    for tag, q, _size in queries(spec):
        if tags and tag not in tags:
            continue
        path = os.path.join(QDIR, hashlib.sha256(q.encode()).hexdigest()[:16] + ".json")
        if not os.path.exists(path):
            # a query written in a spec file shortened at its end: take the stored query that
            # starts with it (first in name order), so that reused answers can be named briefly
            for name in sorted(os.listdir(QDIR)):
                with open(os.path.join(QDIR, name)) as fh:
                    if json.load(fh).get("query", "").startswith(q):
                        path = os.path.join(QDIR, name)
                        break
        print("=" * 100)
        print("%s | %s | %s" % (tag, q, path))
        if not os.path.exists(path):
            print("  (no stored answer)")
            continue
        with open(path) as fh:
            doc = json.load(fh)
        if doc.get("status") != "ok":
            print("  status", doc.get("status"), doc.get("error"))
            continue
        print("  hits_total %s, fetched %s" % (doc.get("hits_total"), doc.get("fetched_utc")))
        for md in doc.get("hits") or []:
            if not md:
                continue
            title = ((md.get("titles") or [{}])[0].get("title") or "").replace("\n", " ")
            date = md.get("earliest_date") or md.get("preprint_date") or "-"
            nc = md.get("citation_count", "-")
            print("  %-18s %-10s c=%-4s %s" % (arxiv_id(md), date, nc, title[:150]))


if __name__ == "__main__":
    main(sys.argv[1], set(sys.argv[2:]))
