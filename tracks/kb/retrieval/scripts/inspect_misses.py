"""R3: why do golden questions miss the answer location? (kb retrieval package, wave 2b)

For every golden question (kbtool/qa_golden.py) this finds the chunks of the expected paper
whose source range overlaps the answer lines, and reports for each:
  - kind, characters, word pieces of the embedded string (chunk-v1 recipe), and where the
    answer starts inside the chunk (word pieces before it: beyond 512 = cut off by the model);
  - its rank in the BM25 ranking (depth 5000), in the vector ranking (whole corpus) and in
    the hybrid fusion of the depth-100 lists that `kb search` uses;
  - equations of the paper whose context or text sits on the answer lines.
It also records the best rank of any chunk of the paper. Paper text goes only to the run
directory (scratch), never to git.

    kb/.venv/bin/python -I tracks/kb/retrieval/scripts/inspect_misses.py OUT_DIR [--db PATH] [--threads 8]
"""
import argparse
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "kb"))

from kbtool import embed_cli as EC          # noqa: E402
from kbtool import embed_index as X         # noqa: E402
from kbtool import embed_search as S        # noqa: E402
from kbtool import qa_golden as G           # noqa: E402
from kbtool.paths import layout             # noqa: E402


def overlaps(src, q, slack):
    f, a, b = G.parse_source(src or "")
    if not f or f.split("/")[-1].lower() != q["file"].split("/")[-1].lower():
        return False
    return any(a <= hi + slack and b >= lo - slack for lo, hi in q["lines"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--db", default=None)
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lay = layout()
    db = a.db or os.path.realpath(lay.db_current)
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    emb = EC._embedder("bge-small", a.threads)
    model = EC._model_key("bge-small")
    store = S.VectorStore(con, model, "chunk")
    loc = S.Locator(lay)
    report, text_dump = [], []
    for q in G.questions():
        pid = q["paper"]
        rows = con.execute("SELECT c.chunk_id, c.kind, c.char_start, c.char_end, length(c.text), c.text "
                           "FROM chunks c WHERE c.paper_id=? ORDER BY c.char_start", (pid,)).fetchall()
        bm = S.rank_text(con, q["question"], depth=5000)
        bm_rank = {c: r for r, c in enumerate(bm, 1)}
        qv = emb.encode([q["question"]], query=True)[0]
        vids, _ = store.rank(qv, depth=len(store))
        v_rank = {c: r for r, c in enumerate(vids, 1)}
        fused = S.rrf({"bm25": bm[:100], "vector": vids[:100]})
        h_order = sorted(fused, key=lambda i: (-fused[i][0], i))
        h_rank = {c: r for r, c in enumerate(h_order, 1)}
        recipe = dict(X.chunk_texts(con, ids=[r[0] for r in rows]))
        ans = []
        for cid, kind, cs, ce, n, text in rows:
            src = loc.lines(pid, cs, ce)
            if not overlaps(src, q, 0):
                continue
            emb_text = recipe.get(cid)
            pieces = emb.n_tokens([emb_text])[0] if emb_text else None
            # where in the chunk does the answer start? the first flat.tex offset whose line is an answer line
            first = None
            if cs is not None:
                sm = loc.smap(pid)
                if sm:
                    offs, m = sm
                    for off, f, ln in [(e[0], e[1], e[2]) for e in m if cs <= e[0] < (ce or cs)]:
                        if f.split("/")[-1].lower() == q["file"].lower() and any(lo <= ln <= hi for lo, hi in q["lines"]):
                            first = off - cs
                            break
            before = None
            if first is not None and emb_text is not None:
                head = emb_text[: len(emb_text) - len(text or "")]
                before = emb.n_tokens([head + (text or "")[:first]])[0]
            ans.append({"chunk_id": cid, "kind": kind, "source": src, "chars": n, "pieces": pieces,
                        "answer_offset_chars": first, "pieces_before_answer": before,
                        "bm25_rank": bm_rank.get(cid), "vector_rank": v_rank.get(cid),
                        "hybrid_rank": h_rank.get(cid)})
            text_dump.append(f"### {q['id']} chunk {cid} {kind} {src} chars {n} pieces {pieces} "
                             f"answer@{first} pieces_before {before}\n{text}\n")
        pc = [r[0] for r in rows]
        best = lambda rk: min((rk[c] for c in pc if c in rk), default=None)   # noqa: E731
        eqs = []
        for eid, num, cs, ce in con.execute(
                "SELECT eq_id, number, char_start, char_end FROM equations WHERE paper_id=?", (pid,)):
            src = loc.lines(pid, cs, ce)
            if overlaps(src, q, 0):
                eqs.append({"eq_id": eid, "number": num, "source": src})
        report.append({"id": q["id"], "paper": pid, "question": q["question"], "lines": q["lines"],
                       "paper_chunks": len(rows), "answer_chunks": ans, "answer_equations": eqs,
                       "paper_best": {"bm25": best(bm_rank), "vector": best(v_rank), "hybrid": best(h_rank)},
                       "top10_hybrid_papers": [con.execute("SELECT paper_id FROM chunks WHERE chunk_id=?",
                                                           (c,)).fetchone()[0] for c in h_order[:10]]})
    json.dump({"database": db, "model": model, "questions": report}, open(os.path.join(a.out, "misses.json"), "w"),
              indent=1)
    with open(os.path.join(a.out, "answer_chunks.txt"), "w") as f:
        f.write("\n".join(text_dump))
    for r in report:
        best_h = min((x["hybrid_rank"] or 10 ** 9 for x in r["answer_chunks"]), default=None)
        print(r["id"], r["paper"], "paper best", r["paper_best"], "answer chunks",
              [(x["chunk_id"], x["kind"], x["chars"], x["pieces"], x["pieces_before_answer"], x["bm25_rank"],
                x["vector_rank"], x["hybrid_rank"]) for x in r["answer_chunks"]],
              "best hybrid", best_h, "equations on the lines", len(r["answer_equations"]))


if __name__ == "__main__":
    main()
