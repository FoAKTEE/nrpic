#!/usr/bin/env python3
"""Titles, authors and source kind of a list of arXiv ids from the store's records (kb-data/meta/
arxiv-api/<key>.json, meta/inspire/<key>.json, meta/arxiv/<key>.json); lists the file names of
the extracted source (no file under kb-data/raw is opened). Standard library only.

    python3 -I tracks/kb/ingest4/scripts/meta_table.py --ids FILE --out DIR
"""
import argparse
import json
import os

DATA = "/data/haiyangw/nrpic/kb-data"


def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ids = [l.split("#")[0].strip() for l in open(a.ids) if l.split("#")[0].strip()]
    rows = []
    for i in ids:
        k = i.replace("/", "_")
        api = load(os.path.join(DATA, "meta", "arxiv-api", k + ".json")) or {}
        ins = load(os.path.join(DATA, "meta", "inspire", k + ".json")) or {}
        rec = ins.get("record") or {}
        pub = (rec.get("publication_info") or [{}])[0]
        jref = " ".join(str(pub.get(x, "")) for x in ("journal_title", "journal_volume", "artid", "year")).strip()
        dl = load(os.path.join(DATA, "meta", "arxiv", k + ".json")) or {}
        ver = dl.get("version") or api.get("version") or ""
        src = os.path.join(DATA, "raw", "arxiv", k, ver, "src") if ver else None
        tex = []
        if src and os.path.isdir(src):
            for root, _, files in os.walk(src):
                tex += [f for f in files if f.lower().endswith(".tex")]
        au = api.get("authors") or []
        rows.append((i, api.get("status", "none"), ver, (api.get("title") or "").replace("\n", " "),
                     au[0] if au else "", len(au), api.get("published", "")[:10] if api.get("published") else "",
                     jref, len(tex), dl.get("status", "")))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "meta_table.tsv"), "w", encoding="utf-8") as fh:
        fh.write("id\tapi_status\tversion\ttitle\tfirst_author\tn_authors\tpublished\tjournal\tn_tex_files\t"
                 "download_status\n")
        for r in rows:
            fh.write("\t".join(" ".join(str(x).split()) for x in r) + "\n")
    for r in rows:
        print("\t".join(str(x) for x in r))


if __name__ == "__main__":
    main()
