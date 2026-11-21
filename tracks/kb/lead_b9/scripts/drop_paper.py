"""Drop one paper from the working database (decision 0024 item 2: gr-qc/0608095).

Under the kb writer lock and in one transaction: the ingest's own delete_paper (citations it
makes, bibliography, chunks and their FTS rows, equations and their FTS rows, figures, sections),
then the embeddings of its chunks and equations, its downloads row and its papers row. Citation
rows of other papers that pointed at it lose in_corpus. Refuses if a claim or a claim locator
names the paper. Writes before/after counts as JSON to --out. --dry-run counts only.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.environ.get("NRPIC_KB_ROOT", "/data/haiyangw/nrpic/wt/kb"), "kb"))
from kbtool import papers_ingest as PI          # noqa: E402
from kbtool.lock import writer_lock              # noqa: E402
from kbtool.paths import layout                  # noqa: E402
import sqlite3                                    # noqa: E402

TABLES = [("papers", "paper_id"), ("chunks", "paper_id"), ("equations", "paper_id"), ("figures", "paper_id"),
          ("sections", "paper_id"), ("bib_entries", "paper_id"), ("downloads", "paper_id"),
          ("citations", "citing"), ("claims", "paper_id"), ("claim_locators", "paper_id")]


def counts(con, pid):
    out = {f"{t}.{c}": con.execute(f"SELECT count(*) FROM {t} WHERE {c}=?", (pid,)).fetchone()[0] for t, c in TABLES}
    out["citations.cited_arxiv"] = con.execute("SELECT count(*) FROM citations WHERE cited_arxiv=?", (pid,)).fetchone()[0]
    out["embeddings.own"] = con.execute(
        "SELECT count(*) FROM embeddings WHERE (owner_kind='chunk' AND owner_id IN (SELECT chunk_id FROM chunks WHERE "
        "paper_id=?)) OR (owner_kind='equation' AND owner_id IN (SELECT eq_id FROM equations WHERE paper_id=?))",
        (pid, pid)).fetchone()[0]
    out["papers.total"] = con.execute("SELECT count(*) FROM papers").fetchone()[0]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paper_id")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    lay = layout(None)
    os.makedirs(a.out, exist_ok=True)
    with writer_lock(lay, what=f"drop {a.paper_id}"):
        con = sqlite3.connect(lay.db_work)
        before = counts(con, a.paper_id)
        if before["claims.paper_id"] or before["claim_locators.paper_id"]:
            raise SystemExit(f"{a.paper_id}: claims name this paper; not dropped")
        rec = {"paper_id": a.paper_id, "before": before, "dry_run": a.dry_run}
        if not a.dry_run:
            con.execute("BEGIN")
            con.execute("DELETE FROM embeddings WHERE owner_kind='chunk' AND owner_id IN (SELECT chunk_id FROM chunks "
                        "WHERE paper_id=?)", (a.paper_id,))
            con.execute("DELETE FROM embeddings WHERE owner_kind='equation' AND owner_id IN (SELECT eq_id FROM "
                        "equations WHERE paper_id=?)", (a.paper_id,))
            PI.delete_paper(con, a.paper_id)
            con.execute("UPDATE citations SET in_corpus=0 WHERE cited_arxiv=?", (a.paper_id,))
            con.execute("DELETE FROM downloads WHERE paper_id=?", (a.paper_id,))
            con.execute("DELETE FROM papers WHERE paper_id=?", (a.paper_id,))
            con.commit()
            rec["after"] = counts(con, a.paper_id)
        con.close()
    with open(os.path.join(a.out, "drop.json"), "w") as f:
        json.dump(rec, f, indent=1)
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
