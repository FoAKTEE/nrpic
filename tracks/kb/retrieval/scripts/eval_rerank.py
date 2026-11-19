"""R4: first stage (hybrid of embed_search) against the window re-ranking of
kbtool/search_rerank.py, on the 32 golden questions (kbtool/qa_golden.py, slack 5 lines, the
design set) and on the ten questions of tracks/kb/embed/questions10.yaml (no slack, held out:
not looked at while designing). Paper rank and answer-location rank within the top K of
every question, mode and configuration; seconds per question.

    kb/.venv/bin/python -I tracks/kb/retrieval/scripts/eval_rerank.py OUT_DIR [--db PATH] [--threads 8]
        [--configs w2,w3,...]
"""
import argparse
import json
import os
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "kb"))

import yaml  # noqa: E402

from kbtool import embed_cli as EC  # noqa: E402
from kbtool import embed_index as X  # noqa: E402
from kbtool import embed_search as S  # noqa: E402
from kbtool import qa_golden as G  # noqa: E402
from kbtool import search_rerank as R  # noqa: E402
from kbtool.paths import layout  # noqa: E402

K = 10


def hit_ranks(q, hits, slack):
    rp = rl = None
    for h in hits:
        if h.get("paper_id") != q["paper"]:
            continue
        rp = rp or h["rank"]
        f, a, b = G.parse_source(h.get("source") or "")
        if f and f.split("/")[-1].lower() == q["file"].split("/")[-1].lower():
            if any(a <= hi + slack and b >= lo - slack for lo, hi in q["lines"]):
                rl = rl or h["rank"]
    return rp, rl


def sets():
    gold = [dict(q, set="golden32", slack=G.SLACK) for q in G.questions()]
    ten = yaml.safe_load(open(os.path.join(WT, "tracks", "kb", "embed", "questions10.yaml")))["questions"]
    ten = [dict(id=q["id"], question=q["question"], paper=str(q["paper"]), file=q["file"],
                lines=[list(x) for x in q["lines"]], set="ten", slack=0) for q in ten]
    return gold + ten


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--db")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--configs", default=",".join(R.CONFIGS))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lay = layout()
    db = a.db or os.path.realpath(lay.db_current)
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    emb = EC._embedder("bge-small", a.threads)
    model = EC._model_key("bge-small")
    store = S.VectorStore(con, model, "chunk")
    configs = [c for c in a.configs.split(",") if c]
    rows = []
    for q in sets():
        t0 = time.time()
        bm = S.rank_text(con, q["question"], depth=100)
        qv = emb.encode([q["question"]], query=True)[0]
        ids, _ = store.rank(qv, depth=100)
        ids, _ = S.drop_stale(con, ids, store, X.chunk_texts)
        fused = S.rrf({"bm25": bm, "vector": ids})
        first = sorted(fused, key=lambda i: (-fused[i][0], i))
        t_first = time.time() - t0
        res = {"id": q["id"], "set": q["set"], "paper": q["paper"], "modes": {}}
        for name, order in (("text", bm), ("hybrid", first)):
            meta = S.describe_chunks(con, lay, order[:K])
            hits = [dict(meta.get(c, {"chunk_id": c}), rank=r) for r, c in enumerate(order[:K], 1)]
            rp, rl = hit_ranks(q, hits, q["slack"])
            res["modes"][name] = {"paper_rank": rp, "locator_rank": rl, "top": [h.get("chunk_id") for h in hits],
                                  "seconds": round(t_first, 2)}
        for c in configs:
            t1 = time.time()
            order, det, info = R.rerank(con, q["question"], first, emb, qvec=qv, **R.CONFIGS[c])
            meta = S.describe_chunks(con, lay, order[:K])
            hits = [dict(meta.get(cid, {"chunk_id": cid}), rank=r) for r, cid in enumerate(order[:K], 1)]
            rp, rl = hit_ranks(q, hits, q["slack"])
            res["modes"][c] = {"paper_rank": rp, "locator_rank": rl, "top": [h.get("chunk_id") for h in hits],
                               "pool": info["pool"], "windows": info["windows"],
                               "expanded": info["expanded_papers"], "seconds": round(time.time() - t1 + t_first, 2)}
        rows.append(res)
        print(q["set"], q["id"], " ".join(f"{m}:{d['paper_rank'] or '-'}/{d['locator_rank'] or '-'}"
                                          for m, d in res["modes"].items()), flush=True)
    summary = {}
    for st in ("golden32", "ten"):
        rs = [r for r in rows if r["set"] == st]
        summary[st] = {}
        for m in rs[0]["modes"]:
            summary[st][m] = {"n": len(rs), "paper_hits": sum(1 for r in rs if r["modes"][m]["paper_rank"]),
                              "locator_hits": sum(1 for r in rs if r["modes"][m]["locator_rank"]),
                              "mrr_locator": round(sum(1.0 / r["modes"][m]["locator_rank"] for r in rs
                                                       if r["modes"][m]["locator_rank"]) / len(rs), 4),
                              "seconds_mean": round(sum(r["modes"][m]["seconds"] for r in rs) / len(rs), 2)}
    out = {"database": db, "model": model, "k": K, "configs": {c: R.CONFIGS[c] for c in configs},
           "summary": summary, "questions": rows}
    json.dump(out, open(os.path.join(a.out, "rerank_eval.json"), "w"), indent=1)
    for st, d in summary.items():
        for m, v in d.items():
            print(f"{st:9s} {m:12s} paper {v['paper_hits']}/{v['n']} locator {v['locator_hits']}/{v['n']} "
                  f"MRR(locator) {v['mrr_locator']} s/question {v['seconds_mean']}")


if __name__ == "__main__":
    main()
