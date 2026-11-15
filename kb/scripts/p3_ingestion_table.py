#!/usr/bin/env python3
"""Ingestion state of the priority-3 papers (gate KB-G1, brief 12.10), from a read-only
database: one row per manifest id of priority 3 with download status, version, parse status
and score, and the row counts of the K2-K3 tables. Ids and counts only, no paper text.

    python3 -I kb/scripts/p3_ingestion_table.py DB OUT.tsv
"""
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(os.path.dirname(HERE), "manifests", "arxiv.tsv")


def main(db, out):
    man = [l.rstrip("\n").split("\t") for l in open(MANIFEST) if l.strip() and not l.startswith(("#", "id\t"))]
    p3 = [(m[0], m[1]) for m in man if m[2] == "3"]
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    q = lambda s, a: con.execute(s, a).fetchone()
    cols = ["paper_id", "group", "download", "version", "source_kind", "parse_status", "parse_score", "has_title",
            "has_abstract", "sections", "equations", "equations_labelled", "figures_tables", "bib_entries",
            "citations", "citations_in_corpus", "body_chunks"]
    rows = []
    for pid, grp in p3:
        d = q("SELECT status FROM downloads WHERE paper_id = ?", (pid,))
        p = q("SELECT version, source_kind, parse_status, parse_score, title IS NOT NULL AND title <> '', "
              "abstract IS NOT NULL AND abstract <> '' FROM papers WHERE paper_id = ?", (pid,))
        if not p:
            rows.append([pid, grp, d[0] if d else "absent"] + ["-"] * (len(cols) - 3))
            continue
        n = lambda s: q(s, (pid,))[0]
        rows.append([pid, grp, d[0] if d else "absent", p[0], p[1], p[2], f"{p[3]:.3f}" if p[3] is not None else "-",
                     int(p[4]), int(p[5]),
                     n("SELECT count(*) FROM sections WHERE paper_id = ?"),
                     n("SELECT count(*) FROM equations WHERE paper_id = ?"),
                     n("SELECT count(*) FROM equations WHERE paper_id = ? AND label IS NOT NULL"),
                     n("SELECT count(*) FROM figures WHERE paper_id = ?"),
                     n("SELECT count(*) FROM bib_entries WHERE paper_id = ?"),
                     n("SELECT count(*) FROM citations WHERE citing = ?"),
                     n("SELECT count(*) FROM citations WHERE citing = ? AND in_corpus = 1"),
                     n("SELECT count(*) FROM chunks WHERE paper_id = ? AND kind IN ('body', 'appendix')")])
    with open(out, "w") as f:
        f.write(f"# priority-3 ingestion state; database {db}\n")
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    st = {}
    for r in rows:
        st[r[5]] = st.get(r[5], 0) + 1
    print(f"{len(rows)} priority-3 ids; parse status {st}; written {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
