"""R4b: why the window re-ranking does not lift the answer chunk of the within-paper misses.
For the named questions: first-stage papers expanded, whether the answer chunks are in the
pool, their window-BM25 and window-vector ranks within the pool, and the best windows of the
answer chunk and of the top three pool chunks (text to the run directory only).

    kb/.venv/bin/python -I tracks/kb/retrieval/scripts/diag_rerank.py OUT_DIR --ids q06,q07 [--config w2]
"""
import argparse
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "kb"))
sys.path.insert(0, HERE)

from kbtool import embed_cli as EC  # noqa: E402
from kbtool import embed_index as X  # noqa: E402
from kbtool import embed_search as S  # noqa: E402
from kbtool import search_rerank as R  # noqa: E402
from kbtool.paths import layout  # noqa: E402
import eval_rerank as EV  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--ids", required=True)
    ap.add_argument("--config", default="w2")
    ap.add_argument("--db")
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lay = layout()
    db = a.db or os.path.realpath(lay.db_current)
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    emb = EC._embedder("bge-small", a.threads)
    store = S.VectorStore(con, EC._model_key("bge-small"), "chunk")
    loc = S.Locator(lay)
    want = set(a.ids.split(","))
    report, dump = [], []
    for q in EV.sets():
        if q["id"] not in want or q["set"] != "golden32":
            continue
        bm = S.rank_text(con, q["question"], depth=100)
        qv = emb.encode([q["question"]], query=True)[0]
        ids, _ = store.rank(qv, depth=100)
        fused = S.rrf({"bm25": bm, "vector": ids})
        first = sorted(fused, key=lambda i: (-fused[i][0], i))
        order, det, info = R.rerank(con, q["question"], first, emb, qvec=qv, **R.CONFIGS[a.config])
        pool_papers = {}
        for c in first[:50]:
            p = con.execute("SELECT paper_id FROM chunks WHERE chunk_id=?", (c,)).fetchone()[0]
            pool_papers.setdefault(p, 0)
            pool_papers[p] += 1
        ans = []
        for cid, cs, ce in con.execute("SELECT chunk_id, char_start, char_end FROM chunks WHERE paper_id=? AND "
                                       "kind != 'comment'", (q["paper"],)):
            src = loc.lines(q["paper"], cs, ce)
            f, x, y = EV.G.parse_source(src or "")
            if f and f.lower() == q["file"].lower() and any(x <= hi and y >= lo for lo, hi in q["lines"]):
                d = det.get(cid)
                ans.append({"chunk_id": cid, "in_pool": d is not None, "final_rank": order.index(cid) + 1
                            if cid in order else None, "ranks": d["ranks"] if d else None,
                            "window_cosine": d["window_cosine"] if d else None})
                if d:
                    dump.append(f"### {q['id']} answer chunk {cid} best window (cos {d['window_cosine']}): "
                                f"{d['window_snippet']}")
        for c in order[:3]:
            dump.append(f"### {q['id']} top chunk {c} ranks {det[c]['ranks']} cos {det[c]['window_cosine']}: "
                        f"{det[c]['window_snippet']}")
        report.append({"id": q["id"], "paper": q["paper"], "expanded": info["expanded_papers"],
                       "pool": info["pool"], "windows": info["windows"],
                       "first50_papers": sorted(pool_papers.items(), key=lambda x: -x[1])[:6], "answer": ans})
        print(json.dumps(report[-1]), flush=True)
    json.dump(report, open(os.path.join(a.out, "diag.json"), "w"), indent=1)
    open(os.path.join(a.out, "windows.txt"), "w").write("\n".join(dump) + "\n")


if __name__ == "__main__":
    main()
