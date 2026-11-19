"""List the hits of INSPIRE query records written by harness/bin/nrpic-fetch-arxiv --inspire-query.

Usage: python3 -I inspire_list.py [--abstracts] <query-json> [<query-json> ...]
Each argument is a file kb-data/meta/inspire/query/<sha16>.json (untrusted data: only parsed
as JSON, nothing in it is executed). Prints the query, the total number of hits, and one line
per hit: arXiv id, citation count, year, first author, title; with --abstracts the first 900
characters of the abstract as well. Standard library only; read-only.
"""
import json
import sys


def first(lst, key, default=""):
    if not lst:
        return default
    v = lst[0]
    return v.get(key, default) if isinstance(v, dict) else default


def main(argv):
    abstracts = "--abstracts" in argv
    files = [a for a in argv if a != "--abstracts"]
    for f in files:
        with open(f) as fh:
            d = json.load(fh)
        print("=" * 100)
        print("file   :", f)
        print("query  :", d.get("query"))
        print("fetched:", d.get("fetched_utc"), " hits_total:", d.get("hits_total"),
              " returned:", len(d.get("hits") or []))
        for h in d.get("hits") or []:
            m = h.get("metadata", h)
            aid = first(m.get("arxiv_eprints"), "value", "-")
            title = first(m.get("titles"), "title", "?").replace("\n", " ")
            au = first(m.get("authors"), "full_name", "?")
            nau = len(m.get("authors") or [])
            year = ""
            pi = m.get("publication_info") or []
            if pi and isinstance(pi[0], dict):
                year = str(pi[0].get("year", ""))
            cit = m.get("citation_count", "")
            print("  %-16s cit=%-5s %-5s %-28s %s" % (aid, cit, year,
                  (au + (" et al." if nau > 1 else ""))[:28], title[:150]))
            if abstracts:
                ab = first(m.get("abstracts"), "value", "").replace("\n", " ")
                print("      ", ab[:900])


if __name__ == "__main__":
    main(sys.argv[1:])
