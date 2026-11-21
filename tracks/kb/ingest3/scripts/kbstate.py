"""Read-only state of the knowledge base for package ingest3 (wave 3, round 1).

Counts per paper of a list (bibliography entries, citation rows, sections, equations, chunks,
claims whose chunk lies in the paper, claim locator rows, dangling chunk references) and over
the whole database (parse_status, TeX papers without a bibliography entry, the "ok but cites
and has no entry" papers, the recorded and the strict parse success rate, citation edges).
Opens the database read-only; writes only into the output directory.

Usage: python3 -I kbstate.py --db PATH --ids FILE [--ids FILE ...] --out DIR [--tag before]
"""
import argparse
import json
import os
import sqlite3


def per_paper(con, pid):
    r = con.execute("SELECT parse_status, parse_score, source_kind, version, flat_sha256, parse_json, grp, title, "
                    "title_source, inspire_recid FROM papers WHERE paper_id=?", (pid,)).fetchone()
    if r is None:
        return {"paper_id": pid, "in_db": False}
    pj = json.loads(r[5] or "{}")
    q = lambda sql: con.execute(sql, (pid,)).fetchone()[0]
    chunk_ids = {x[0] for x in con.execute("SELECT chunk_id FROM chunks WHERE paper_id=?", (pid,))}
    claims_chunk = [x[0] for x in con.execute(
        "SELECT claim_id FROM claims WHERE chunk_id IN (SELECT chunk_id FROM chunks WHERE paper_id=?)", (pid,))]
    claims_pid = [x[0] for x in con.execute("SELECT claim_id FROM claims WHERE paper_id=?", (pid,))]
    locs = con.execute("SELECT loc_id, claim_id, resolved, flat_start, flat_end, chunk_ids_json FROM claim_locators "
                       "WHERE paper_id=?", (pid,)).fetchall()
    dangling_loc = 0
    for _, _, _, _, _, cj in locs:
        for c in json.loads(cj or "[]"):
            if c not in chunk_ids:
                dangling_loc += 1
    dangling_claim = q("SELECT count(*) FROM claims WHERE paper_id=? AND chunk_id IS NOT NULL AND chunk_id NOT IN "
                       "(SELECT chunk_id FROM chunks)")
    return {
        "paper_id": pid, "in_db": True, "parse_status": r[0], "parse_score": r[1], "source_kind": r[2],
        "version": r[3], "flat_sha256": r[4], "grp": r[6], "title_source": r[8], "inspire_recid": r[9],
        "bib_source": pj.get("bib_source"), "bib_notes": pj.get("bib_notes"), "bib_review_reason":
            (pj.get("bib_review") or {}).get("reason") if isinstance(pj.get("bib_review"), dict) else pj.get("bib_review"),
        "bib_entries": q("SELECT count(*) FROM bib_entries WHERE paper_id=?"),
        "bib_with_arxiv": q("SELECT count(*) FROM bib_entries WHERE paper_id=? AND target_arxiv IS NOT NULL"),
        "citations": q("SELECT count(*) FROM citations WHERE citing=?"),
        "citations_with_entry": q("SELECT count(*) FROM citations WHERE citing=? AND bib_id IS NOT NULL"),
        "citations_in_corpus": q("SELECT count(*) FROM citations WHERE citing=? AND in_corpus=1"),
        "cited_by_in_corpus": con.execute("SELECT count(*) FROM citations WHERE cited_arxiv=? AND in_corpus=1",
                                          (pid,)).fetchone()[0],
        "sections": q("SELECT count(*) FROM sections WHERE paper_id=?"),
        "equations": q("SELECT count(*) FROM equations WHERE paper_id=?"),
        "equations_numbered": q("SELECT count(*) FROM equations WHERE paper_id=? AND number IS NOT NULL"),
        "equations_tagged": q("SELECT count(*) FROM equations WHERE paper_id=? AND tags_json IS NOT NULL "
                              "AND tags_json NOT IN ('[]', 'null')"),
        "chunks": q("SELECT count(*) FROM chunks WHERE paper_id=? AND kind!='comment'"),
        "chunks_all": len(chunk_ids),
        "chunk_vectors": q("SELECT count(*) FROM embeddings WHERE owner_kind='chunk' AND owner_id IN "
                           "(SELECT chunk_id FROM chunks WHERE paper_id=?)"),
        "equation_vectors": q("SELECT count(*) FROM embeddings WHERE owner_kind='equation' AND owner_id IN "
                              "(SELECT eq_id FROM equations WHERE paper_id=?)"),
        "claims_by_chunk": sorted(claims_chunk), "claims_by_paper": sorted(claims_pid),
        "claim_locator_rows": len(locs), "claim_locator_rows_resolved": sum(1 for l in locs if l[2]),
        "dangling_locator_chunk_refs": dangling_loc, "dangling_claim_chunk": dangling_claim,
    }


def overall(con):
    n = lambda sql: con.execute(sql).fetchone()[0]
    st = dict(con.execute("SELECT coalesce(parse_status,'?'), count(*) FROM papers GROUP BY 1").fetchall())
    papers = n("SELECT count(*) FROM papers")
    zero = con.execute(
        "SELECT p.paper_id, p.parse_status, (SELECT count(*) FROM citations c WHERE c.citing=p.paper_id) "
        "FROM papers p WHERE p.source_kind='tex' AND NOT EXISTS (SELECT 1 FROM bib_entries b WHERE "
        "b.paper_id=p.paper_id) ORDER BY p.paper_id").fetchall()
    ok_cites_noentry = [z[0] for z in zero if z[1] == "ok" and z[2] > 0]
    ok_noentry = [z[0] for z in zero if z[1] == "ok"]
    ok = st.get("ok", 0)
    pdf = st.get("pdf", 0)
    out = {
        "papers": papers, "parse_status": st, "tex_papers": n("SELECT count(*) FROM papers WHERE source_kind='tex'"),
        "zero_bib_tex": [{"paper_id": z[0], "parse_status": z[1], "citation_rows": z[2]} for z in zero],
        "zero_bib_tex_count": len(zero), "zero_bib_ok": ok_noentry, "ok_cites_no_entry": ok_cites_noentry,
        "rate_recorded_ok": round(ok / papers, 5) if papers else None,
        "rate_recorded_ok_pdf": round((ok + pdf) / papers, 5) if papers else None,
        "rate_strict_ok": round((ok - len(ok_cites_noentry)) / papers, 5) if papers else None,
        "rate_strict_ok_pdf": round((ok + pdf - len(ok_cites_noentry)) / papers, 5) if papers else None,
        "rate_strict_ok_noentry_any": round((ok - len(ok_noentry)) / papers, 5) if papers else None,
        "bib_entries": n("SELECT count(*) FROM bib_entries"),
        "bib_with_arxiv": n("SELECT count(*) FROM bib_entries WHERE target_arxiv IS NOT NULL"),
        "citations": n("SELECT count(*) FROM citations"),
        "citations_in_corpus": n("SELECT count(*) FROM citations WHERE in_corpus=1"),
        "chunks": n("SELECT count(*) FROM chunks"), "equations": n("SELECT count(*) FROM equations"),
        "sections": n("SELECT count(*) FROM sections"),
        "chunk_vectors": n("SELECT count(*) FROM embeddings WHERE owner_kind='chunk'"),
        "equation_vectors": n("SELECT count(*) FROM embeddings WHERE owner_kind='equation'"),
        "claims": n("SELECT count(*) FROM claims"),
        "claims_with_chunk": n("SELECT count(*) FROM claims WHERE chunk_id IS NOT NULL"),
        "claims_dangling_chunk": n("SELECT count(*) FROM claims WHERE chunk_id IS NOT NULL AND chunk_id NOT IN "
                                   "(SELECT chunk_id FROM chunks)"),
        "claim_locators": n("SELECT count(*) FROM claim_locators"),
        "claim_status": dict(con.execute("SELECT coalesce(status,'?'), count(*) FROM claim_meta GROUP BY 1")),
    }
    dl = 0
    all_chunks = {x[0] for x in con.execute("SELECT chunk_id FROM chunks")}
    for (cj,) in con.execute("SELECT chunk_ids_json FROM claim_locators"):
        dl += sum(1 for c in json.loads(cj or "[]") if c not in all_chunks)
    out["claim_locator_dangling_chunk_refs"] = dl
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--ids", action="append", default=[], help="file with one id per line (repeatable)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="state")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True, timeout=60)
    lists = {}
    for f in a.ids:
        ids = [l.split()[0] for l in open(f) if l.strip() and not l.startswith("#")]
        lists[os.path.splitext(os.path.basename(f))[0]] = [per_paper(con, i) for i in ids]
    res = {"db": a.db, "tag": a.tag, "overall": overall(con), "lists": lists}
    # every claim touching a listed paper (by paper, chunk or locator row) with its rows, for the
    # before/after comparison of the chunk remap
    pids = sorted({r["paper_id"] for rows in lists.values() for r in rows})
    cids = set()
    for pid in pids:
        cids |= {x[0] for x in con.execute(
            "SELECT claim_id FROM claims WHERE paper_id=? OR chunk_id IN (SELECT chunk_id FROM chunks WHERE paper_id=?) "
            "UNION SELECT claim_id FROM claim_locators WHERE paper_id=?", (pid, pid, pid))}
    det = []
    for cid in sorted(cids):
        c = con.execute("SELECT c.claim_id, c.paper_id, c.chunk_id, c.quote_start, c.quote_end, c.label, m.status, "
                        "m.seed_key, (SELECT paper_id FROM chunks WHERE chunk_id=c.chunk_id) FROM claims c "
                        "LEFT JOIN claim_meta m USING(claim_id) WHERE c.claim_id=?", (cid,)).fetchone()
        rows = con.execute("SELECT loc_id, ord, paper_id, version, file, line_start, line_end, resolved, flat_start, "
                           "flat_end, chunk_ids_json FROM claim_locators WHERE claim_id=? ORDER BY ord", (cid,)).fetchall()
        det.append({"claim_id": c[0], "paper_id": c[1], "chunk_id": c[2], "quote_start": c[3], "quote_end": c[4],
                    "label": c[5], "status": c[6], "seed_key": c[7], "chunk_paper": c[8],
                    "locators": [dict(zip(("loc_id", "ord", "paper_id", "version", "file", "line_start", "line_end",
                                           "resolved", "flat_start", "flat_end", "chunk_ids_json"), r)) for r in rows]})
    res["claims"] = det
    con.close()
    with open(os.path.join(a.out, f"{a.tag}.json"), "w") as f:
        json.dump(res, f, indent=1)
    cols = ["paper_id", "parse_status", "parse_score", "bib_source", "bib_entries", "bib_with_arxiv", "citations",
            "citations_with_entry", "sections", "equations", "equations_numbered", "chunks", "chunk_vectors",
            "claim_locator_rows", "dangling_locator_chunk_refs"]
    for name, rows in lists.items():
        with open(os.path.join(a.out, f"{a.tag}_{name}.tsv"), "w") as f:
            f.write("\t".join(cols + ["claims_by_chunk"]) + "\n")
            for r in rows:
                f.write("\t".join(str(r.get(c, "")) for c in cols) + "\t" +
                        ",".join(map(str, r.get("claims_by_chunk", []))) + "\n")
    o = res["overall"]
    print(json.dumps({k: o[k] for k in ("papers", "parse_status", "tex_papers", "zero_bib_tex_count", "zero_bib_ok",
                                        "ok_cites_no_entry", "rate_recorded_ok", "rate_strict_ok",
                                        "rate_recorded_ok_pdf", "rate_strict_ok_pdf", "bib_entries", "citations",
                                        "citations_in_corpus", "claims", "claims_with_chunk", "claims_dangling_chunk",
                                        "claim_locator_dangling_chunk_refs", "claim_status")}, indent=1))
    for name, rows in lists.items():
        print(f"## {name}")
        print(open(os.path.join(a.out, f"{a.tag}_{name}.tsv")).read())
    print(f"## claims touching the listed papers: {len(res['claims'])}")
    for c in res["claims"]:
        print(c["claim_id"], c["paper_id"], c["chunk_id"], c["chunk_paper"], c["label"], c["status"],
              [(l["paper_id"], l["file"], l["line_start"], l["line_end"], l["flat_start"], l["chunk_ids_json"])
               for l in c["locators"]])


if __name__ == "__main__":
    main()
