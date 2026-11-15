#!/usr/bin/env python3
"""Run one INSPIRE literature query, keep the raw JSON, print one line per record.

Usage: python3 -I inspire_query.py <outdir> <query> [size]

The query is sent as given (generic physics terms only; nothing about the project or
its users goes into a request). The raw response is saved as <outdir>/response.json and
the query text as <outdir>/query.txt, so every hit in NOVELTY.md can be traced back.
Output columns: arXiv id | year | citations | title.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://inspirehep.net/api/literature"
FIELDS = "control_number,titles,arxiv_eprints,citation_count,preprint_date,earliest_date"


def main():
    outdir, query = sys.argv[1], sys.argv[2]
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    os.makedirs(outdir, exist_ok=True)
    url = API + "?" + urllib.parse.urlencode(
        {"q": query, "size": size, "sort": "mostcited", "fields": FIELDS})
    req = urllib.request.Request(url, headers={"User-Agent": "generic-literature-client/1.0",
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    with open(os.path.join(outdir, "response.json"), "wb") as f:
        f.write(raw)
    with open(os.path.join(outdir, "query.txt"), "w") as f:
        f.write(query + "\n" + url + "\n" + time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n")
    d = json.loads(raw)
    print(f"# total={d['hits']['total']} shown={len(d['hits']['hits'])} query={query}")
    for h in d["hits"]["hits"]:
        m = h["metadata"]
        ax = m.get("arxiv_eprints", [{}])[0].get("value", "-")
        yr = (m.get("earliest_date") or m.get("preprint_date") or "----")[:4]
        title = m["titles"][0]["title"].replace("\n", " ")
        print(f"{ax:>18} | {yr} | {m.get('citation_count', 0):5d} | {title}")
    time.sleep(1.0)


if __name__ == "__main__":
    main()
