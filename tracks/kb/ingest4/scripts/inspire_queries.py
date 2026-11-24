#!/usr/bin/env python3
"""Run INSPIRE literature queries one after the other through harness/bin/nrpic-fetch-arxiv
(the only sanctioned client: one lock for the machine, three seconds between requests, generic
client name) and tabulate the hits. Standard library only; nothing under kb-data/raw is read.

    python3 -I tracks/kb/ingest4/scripts/inspire_queries.py --queries FILE --out DIR [--size 25]
    python3 -I tracks/kb/ingest4/scripts/inspire_queries.py --queries FILE --out DIR --no-fetch

FILE: lines `<tag> TAB <INSPIRE query>`; '#' starts a comment. Writes DIR/hits.tsv (one row per
query and hit: tag, query, rank, arXiv id, year, first author, n authors, title, DOI, journal,
document type) and DIR/queries.tsv (tag, query, status, hits_total, record file).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FETCH = os.path.join(WT, "harness", "bin", "nrpic-fetch-arxiv")


def data_root():
    out = subprocess.run(["git", "-C", WT, "rev-parse", "--git-common-dir"], capture_output=True, text=True,
                         check=True).stdout.strip()
    return os.path.dirname(os.path.abspath(os.path.join(WT, out)))


def record_path(root, query):
    return os.path.join(root, "kb-data", "meta", "inspire", "query",
                        hashlib.sha256(query.encode()).hexdigest()[:16] + ".json")


def clean(s):
    return " ".join(str(s or "").split()).replace("\t", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=25)
    ap.add_argument("--no-fetch", action="store_true", help="tabulate stored records only")
    a = ap.parse_args()
    root = data_root()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    with open(a.queries, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            tag, q = line.split("\t", 1)
            rows.append((tag.strip(), q.strip()))
    qrows, hrows = [], []
    for tag, q in rows:
        if not a.no_fetch:
            r = subprocess.run([sys.executable, "-I", FETCH, "--inspire-query", q, "--size", str(a.size)],
                               capture_output=True, text=True)
            sys.stdout.write(f"## {tag}: {q}\n{r.stdout}{r.stderr}exit {r.returncode}\n")
        p = record_path(root, q)
        if not os.path.exists(p):
            qrows.append((tag, q, "missing", "", p))
            continue
        d = json.load(open(p, encoding="utf-8"))
        qrows.append((tag, q, d.get("status"), d.get("hits_total"), p))
        for k, h in enumerate(d.get("hits") or [], 1):
            arx = ";".join(e.get("value", "") for e in h.get("arxiv_eprints") or [])
            au = h.get("authors") or []
            pub = (h.get("publication_info") or [{}])[0]
            year = pub.get("year", "")
            jr = " ".join(str(pub.get(x, "")) for x in ("journal_title", "journal_volume", "page_start")).strip()
            title = (h.get("titles") or [{}])[0].get("title", "")
            doi = ";".join(x.get("value", "") for x in h.get("dois") or [])
            hrows.append((tag, q, k, arx, year, clean(au[0]["full_name"]) if au else "", len(au), clean(title), doi,
                          clean(jr), ";".join(h.get("document_type") or [])))
    with open(os.path.join(a.out, "queries.tsv"), "w", encoding="utf-8") as fh:
        fh.write("tag\tquery\tstatus\thits_total\trecord\n")
        for r in qrows:
            fh.write("\t".join(clean(x) for x in r) + "\n")
    with open(os.path.join(a.out, "hits.tsv"), "w", encoding="utf-8") as fh:
        fh.write("tag\tquery\trank\tarxiv\tyear\tfirst_author\tn_authors\ttitle\tdoi\tjournal\tdoc_type\n")
        for r in hrows:
            fh.write("\t".join(clean(x) for x in r) + "\n")
    print(f"{len(qrows)} queries, {len(hrows)} hits -> {a.out}")


if __name__ == "__main__":
    main()
