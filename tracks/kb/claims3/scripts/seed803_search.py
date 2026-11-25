#!/usr/bin/env python3
"""Seed 803 (brief item 20 of section 7): which papers of the store touch the stability of
FLRW-type cosmologies under Einstein-Vlasov? Read-only search of the working database.

    python3 -I seed803_search.py [--db PATH] [--out DIR]

Two lists, written to DIR/seed803_hits.tsv:
  title   papers whose title has stabil/Milne/Einstein-de Sitter/FLRW/Friedmann together with
          Vlasov, or stabil together with Einstein-de Sitter, FLRW, Friedmann or matter dominated;
  chunks  papers with at least one text chunk that has 'Vlasov', one of FLRW / Friedmann /
          de Sitter / Robertson, and 'stab' (counts of such chunks).
Every paper of the union is read by the package at its abstract or the cited lines (JOURNAL.md
entry 3); this script only finds them. Standard library only.
"""
import argparse
import os
import sqlite3

DB = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    title = {}
    for pid, t in con.execute("SELECT paper_id, title FROM papers"):
        tl = (t or "").lower()
        cosmo = any(w in tl for w in ("milne", "einstein-de sitter", "einstein--de sitter", "flrw", "friedmann",
                                      "matter dominated", "matter-dominated"))
        if ("vlasov" in tl and ("stabil" in tl or cosmo)) or ("stabil" in tl and cosmo):
            title[pid] = t
    chunks = {}
    for (pid,) in con.execute(
            "SELECT paper_id FROM chunks WHERE text LIKE '%Vlasov%' AND (text LIKE '%FLRW%' OR text LIKE "
            "'%Friedmann%' OR text LIKE '%de Sitter%' OR text LIKE '%Robertson%') AND text LIKE '%stab%'"):
        chunks[pid] = chunks.get(pid, 0) + 1
    rows = []
    for pid in sorted(set(title) | set(chunks)):
        t = con.execute("SELECT title FROM papers WHERE paper_id=?", (pid,)).fetchone()[0]
        rows.append((pid, "title" if pid in title else "", chunks.get(pid, 0), (t or "").replace("\t", " ")))
    out = os.path.join(a.out, "seed803_hits.tsv") if a.out else None
    lines = ["paper_id\tby_title\tchunks\ttitle"] + [f"{p}\t{b}\t{n}\t{t}" for p, b, n, t in rows]
    if out:
        with open(out, "w") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"# {len(rows)} papers ({len(title)} by title, {len(chunks)} by chunks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
