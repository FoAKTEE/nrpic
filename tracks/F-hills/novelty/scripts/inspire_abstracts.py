#!/usr/bin/env python3
"""Fetch INSPIRE records (title, first authors, date, abstract) for arXiv ids or a query.

Usage: python3 -I inspire_abstracts.py <outdir> <arxiv_id> [<arxiv_id> ...]
       python3 -I inspire_abstracts.py <outdir> --q "<inspire query>"

Saves the raw response as <outdir>/response.json; prints a readable block per record.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://inspirehep.net/api/literature"
FIELDS = "control_number,titles,arxiv_eprints,authors.full_name,abstracts,earliest_date,citation_count,publication_info"


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    if sys.argv[2] == "--q":
        q = sys.argv[3]
    else:
        q = " or ".join(f"arxiv:{a}" for a in sys.argv[2:])
    url = API + "?" + urllib.parse.urlencode({"q": q, "size": 100, "fields": FIELDS})
    req = urllib.request.Request(url, headers={"User-Agent": "generic-literature-client/1.0",
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    with open(os.path.join(outdir, "response.json"), "wb") as f:
        f.write(raw)
    with open(os.path.join(outdir, "query.txt"), "w") as f:
        f.write(q + "\n" + url + "\n" + time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n")
    d = json.loads(raw)
    for h in d["hits"]["hits"]:
        m = h["metadata"]
        ax = m.get("arxiv_eprints", [{}])[0].get("value", "-")
        au = [a["full_name"] for a in m.get("authors", [])]
        aus = "; ".join(au[:6]) + (" et al." if len(au) > 6 else "")
        ab = m.get("abstracts", [{}])[0].get("value", "(no abstract)")
        pub = m.get("publication_info", [{}])[0]
        pubs = " ".join(str(pub.get(k, "")) for k in ("journal_title", "journal_volume", "artid", "year")).strip()
        print(f"=== arXiv:{ax} | {m.get('earliest_date', '')} | cites {m.get('citation_count', 0)} | {pubs}")
        print(f"TITLE: {m['titles'][0]['title']}")
        print(f"AUTHORS: {aus}")
        print(f"ABSTRACT: {ab}\n")
    time.sleep(1.0)


if __name__ == "__main__":
    main()
