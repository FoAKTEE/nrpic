#!/usr/bin/env python3
"""List the hits of INSPIRE query records written by nrpic-fetch-arxiv --inspire-query
(kb-data/meta/inspire/query/<sha16>.json; untrusted data, only parsed). Run with python3 -I.
Usage: inspire_list.py <record.json> [...]  ->  one line per hit:
  control_number | arXiv id | year | first author | citations | title"""
import json
import sys


def main(paths):
    for p in paths:
        d = json.load(open(p))
        print(f"## {d.get('query')!r}  fetched {d.get('fetched_utc')}  status {d.get('status')}  "
              f"hits_total {d.get('hits_total')}  shown {len(d.get('hits') or [])}")
        for h in d.get("hits") or []:
            ax = ",".join(e.get("value", "") for e in h.get("arxiv_eprints", []) or [])
            ti = (h.get("titles") or [{}])[0].get("title", "").replace("\n", " ")
            au = (h.get("authors") or [{}])[0].get("full_name", "")
            yr = ""
            for pi in h.get("publication_info") or []:
                yr = pi.get("year", yr)
            print(f"{h.get('control_number')} | {ax} | {yr} | {au} | {h.get('citation_count')} | "
                  f"{ti[:150]}")


if __name__ == "__main__":
    main(sys.argv[1:])
