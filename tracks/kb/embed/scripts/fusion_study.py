"""Test E7 of the embed package: variants of the rank fusion of `kb search`, chosen on one
question set and checked on the other.

For every question of the K9 golden set (kbtool/qa_golden.py, 32 questions, slack 5 lines) and
of questions10.yaml (10 questions, no slack): the BM25 ranking and the vector ranking (200
candidates each, the same functions as `kb search`), and which candidates are hits. Fusion
variants: weighted reciprocal rank, score = w_text / (k + rank_text) + w_vec / (k + rank_vec),
k in K_GRID, w_vec in W_GRID (w_text = 1). The variant with the most hits in the top 10 on
the K9 set (ties: higher MRR@10, then the current default k=60, w=1) is then scored on the ten.

    kb/.venv/bin/python -I tracks/kb/embed/scripts/fusion_study.py OUT_DIR [--db PATH] [--threads 8]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eval_questions as EQ                     # noqa: E402  (also puts kb/ on sys.path)
import yaml                                     # noqa: E402
from kbtool import db as _db                    # noqa: E402
from kbtool import embed_index as X             # noqa: E402
from kbtool import embed_model as E             # noqa: E402
from kbtool import embed_search as S            # noqa: E402
from kbtool import qa_golden                    # noqa: E402
from kbtool.paths import layout                 # noqa: E402

K_GRID = (5, 10, 20, 60, 100)
W_GRID = (0.0, 0.25, 0.5, 0.75, 1.0, 1.5)
DEPTH = 200


def fuse(text, vec, k, w):
    sc = {}
    for r, i in enumerate(text, 1):
        sc[i] = sc.get(i, 0.0) + 1.0 / (k + r)
    if w > 0:
        for r, i in enumerate(vec, 1):
            sc[i] = sc.get(i, 0.0) + w / (k + r)
    return sorted(sc, key=lambda i: (-sc[i], i))


def first_hit(order, hits, n=10):
    for r, i in enumerate(order[:n], 1):
        if i in hits:
            return r
    return None


def score(rows, k, w):
    ranks = [first_hit(fuse(r["text"], r["vector"], k, w), r["hits"]) for r in rows]
    return {"hit@10": sum(1 for x in ranks if x), "mrr@10": round(sum(1 / x for x in ranks if x) / len(rows), 4),
            "ranks": ranks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--db")
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lay = layout()
    path = os.path.realpath(_db.open_for_read(lay, a.db))
    sets = {"k9": (qa_golden.questions(), qa_golden.SLACK),
            "ten": (yaml.safe_load(open(os.path.join(os.path.dirname(HERE), "questions10.yaml")))["questions"], 0)}
    emb = E.STEmbedder(threads=a.threads)
    con = _db.connect_ro(path)
    store = S.VectorStore(con, emb.key, "chunk")
    loc = S.Locator(lay)
    data = {}
    for name, (qs, slack) in sets.items():
        rows = []
        for q in qs:
            text = S.rank_text(con, q["question"], depth=DEPTH)
            ids, _ = store.rank(emb.encode([q["question"]], query=True)[0], depth=DEPTH)
            vec, _ = S.drop_stale(con, ids, store, X.chunk_texts)
            cand = sorted(set(text) | set(vec))
            meta = S.describe_chunks(con, lay, cand)
            hits = {i for i in cand if meta[i]["paper_id"] == q["paper"]
                    and EQ.is_hit(EQ.span(loc, q["paper"], meta[i]["char_start"], meta[i]["char_end"]), q, slack)}
            rows.append({"id": q["id"], "text": text, "vector": vec, "hits": hits})
        data[name] = rows
    con.close()
    grid = {name: {f"k={k} w={w}": score(rows, k, w) for k in K_GRID for w in W_GRID} for name, rows in data.items()}
    for name, rows in data.items():
        grid[name]["text only"] = score([dict(r, vector=[]) for r in rows], 60, 0.0)
        grid[name]["vector only"] = score([dict(r, text=[]) for r in rows], 60, 1.0)
    order = sorted(grid["k9"], key=lambda v: (-grid["k9"][v]["hit@10"], -grid["k9"][v]["mrr@10"],
                                              v != "k=60 w=1.0"))
    best = next(v for v in order if v.startswith("k="))
    res = {"database": path, "model": emb.key, "depth": DEPTH, "chosen_on_k9": best,
           "chosen": {"k9": grid["k9"][best], "ten": grid["ten"][best]},
           "default": {"k9": grid["k9"]["k=60 w=1.0"], "ten": grid["ten"]["k=60 w=1.0"]},
           "text_only": {s: grid[s]["text only"] for s in grid}, "vector_only": {s: grid[s]["vector only"] for s in grid},
           "grid": {s: {v: {kk: vv for kk, vv in g.items() if kk != "ranks"} for v, g in grid[s].items()} for s in grid},
           "k_grid": K_GRID, "w_grid": W_GRID}
    with open(os.path.join(a.out, "fusion.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "grid"}, indent=1))


if __name__ == "__main__":
    main()
