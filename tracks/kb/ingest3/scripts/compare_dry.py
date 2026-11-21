"""Compare a dry-run parse of every paper (summaries of `kb ingest arxiv --dry-run`) with the rows
in the database (read-only): what a re-ingest with the current code would change, per paper.

Usage: python3 -I compare_dry.py --db PATH --dry DIR --out DIR [--skip FILE ...]
Writes compare.tsv (every paper with a difference) and compare.json (counts) into --out.
"""
import argparse
import glob
import json
import os
import sqlite3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--dry", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip", action="append", default=[], help="id lists re-ingested today (reported apart)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    skip = set()
    for f in a.skip:
        skip |= {l.split()[0] for l in open(f) if l.strip() and not l.startswith("#")}
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True, timeout=60)
    rows, n = [], 0
    changed = {"status": 0, "bib_entries": 0, "cited_keys": 0, "sections": 0, "equations": 0, "chunks": 0}
    lost = {"bib_entries": [], "sections": [], "equations": [], "cited_keys": []}
    for p in sorted(glob.glob(os.path.join(a.dry, "*.json"))):
        d = json.load(open(p))
        pid = d["paper_id"]
        r = con.execute("SELECT parse_status FROM papers WHERE paper_id=?", (pid,)).fetchone()
        if r is None:
            continue
        n += 1
        q = lambda sql: con.execute(sql, (pid,)).fetchone()[0]
        db = {"status": r[0], "bib_entries": q("SELECT count(*) FROM bib_entries WHERE paper_id=?"),
              "cited_keys": q("SELECT count(DISTINCT cite_key) FROM citations WHERE citing=?"),
              "sections": q("SELECT count(*) FROM sections WHERE paper_id=?"),
              "equations": q("SELECT count(*) FROM equations WHERE paper_id=?"),
              "chunks": q("SELECT count(*) FROM chunks WHERE paper_id=? AND kind!='comment'")}
        dr = {"status": d["status"], "bib_entries": d["bib_entries"], "cited_keys": d.get("cited_keys"),
              "sections": d["sections"], "equations": d["equations"], "chunks": d.get("chunks_noncomment")}
        diff = [k for k in db if db[k] != dr[k] and not (k == "cited_keys" and dr[k] is None)]
        if not diff:
            continue
        group = "reingested-today" if pid in skip else "other"
        if group == "other":
            for k in diff:
                changed[k] += 1
            for k in lost:
                if dr[k] is not None and db[k] is not None and dr[k] < db[k]:
                    lost[k].append(pid)
        rows.append([pid, group, ",".join(diff)] + [f"{db[k]}->{dr[k]}" for k in db])
    con.close()
    with open(os.path.join(a.out, "compare.tsv"), "w") as f:
        f.write("paper_id\tgroup\tdiffers\tstatus\tbib_entries\tcited_keys\tsections\tequations\tchunks\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    other = [r for r in rows if r[1] == "other"]
    res = {"papers_compared": n, "papers_with_a_difference": len(rows), "other_papers_with_a_difference": len(other),
           "other_changed_by_field": changed, "other_losing": {k: v for k, v in lost.items()}}
    with open(os.path.join(a.out, "compare.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
