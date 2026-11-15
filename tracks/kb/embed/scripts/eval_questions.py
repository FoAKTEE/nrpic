"""Test E4 of the embed package: retrieval of the ten questions and six equation lookups of
tracks/kb/embed/questions10.yaml by text (BM25), vector and hybrid (reciprocal-rank fusion)
search over the whole corpus, through the same functions as `kb search` and `kb eq`.

    kb/.venv/bin/python -I tracks/kb/embed/scripts/eval_questions.py OUT_DIR [--db PATH] [--threads 8]

Writes OUT_DIR/results.json (ids, ranks, locators; no paper text) and prints a summary.
"""
import argparse
import bisect
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(WT, "kb"))

import yaml                                   # noqa: E402
from kbtool import db as _db                  # noqa: E402
from kbtool import embed_model as E           # noqa: E402
from kbtool import embed_search as S          # noqa: E402
from kbtool import eq_search as Q             # noqa: E402
from kbtool.paths import layout               # noqa: E402

MODES = ("text", "vector", "hybrid")
DEPTH = 100


def span(loc, pid, start, end):
    sm = loc.smap(pid)
    if sm is None or start is None:
        return None
    offs, m = sm
    a = m[max(0, bisect.bisect_right(offs, start) - 1)]
    b = m[max(0, bisect.bisect_right(offs, max(start, (end or start) - 1)) - 1)]
    return a[1], a[2], b[1], b[2]


def is_hit(sp, q):
    if sp is None:
        return False
    fa, la, fb, lb = sp
    if fa != q["file"] and fb != q["file"]:
        return False
    lo = la if fa == q["file"] else 1
    hi = lb if fb == q["file"] else 10 ** 9
    return any(lo <= b and a <= hi for a, b in q["lines"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--db")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--questions", default=os.path.join(os.path.dirname(HERE), "questions10.yaml"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lay = layout()
    path = os.path.realpath(_db.open_for_read(lay, a.db))
    qs = yaml.safe_load(open(a.questions))
    emb = E.STEmbedder(threads=a.threads)
    con = _db.connect_ro(path)
    cstore = S.VectorStore(con, emb.key, "chunk")
    estore = S.VectorStore(con, emb.key, "equation")
    loc = S.Locator(lay)
    res = {"database": path, "model": emb.key, "chunk_vectors": len(cstore), "equation_vectors": len(estore),
           "depth": DEPTH, "questions": [], "equations": []}
    for q in qs["questions"]:
        row = {"id": q["id"], "paper": q["paper"], "file": q["file"], "lines": q["lines"], "modes": {}}
        for mode in MODES:
            hits, info = S.search(lay, q["question"], k=DEPTH, mode=mode, depth=DEPTH, embedder=emb,
                                  store=cstore, con=con)
            first, paper_first, top = None, None, []
            for h in hits:
                sp = span(loc, h["paper_id"], h["char_start"], h["char_end"])
                hit = h["paper_id"] == q["paper"] and is_hit(sp, q)
                if hit and first is None:
                    first = h["rank"]
                if h["paper_id"] == q["paper"] and paper_first is None:
                    paper_first = h["rank"]
                if h["rank"] <= 10:
                    top.append({"rank": h["rank"], "chunk_id": h["chunk_id"], "paper_id": h["paper_id"],
                                "kind": h["kind"], "source": h["source"], "ranks": h["ranks"], "hit": hit})
            row["modes"][mode] = {"first_hit": first, "paper_first": paper_first, "top10": top,
                                  "stale_dropped": info.get("stale_dropped", 0)}
        res["questions"].append(row)
    for e in qs["equations"]:
        row = {"id": e["id"], "paper": e["paper"], "label": e["label"], "modes": {}}
        for mode in MODES:
            for scope, paper in (("corpus", None), ("paper", e["paper"])):
                hits, info = Q.search(lay, e["query"], k=DEPTH, mode=mode, paper=paper, depth=DEPTH,
                                      embedder=emb, store=estore, con=con)
                first = next((h["rank"] for h in hits if h["paper_id"] == e["paper"] and h["label"] == e["label"]),
                             None)
                row["modes"][f"{mode}/{scope}"] = {"first_hit": first,
                                                   "top3": [(h["paper_id"], h["label"], h["number"]) for h in hits[:3]]}
        res["equations"].append(row)
    con.close()

    summ = {}
    for mode in MODES:
        ranks = [r["modes"][mode]["first_hit"] for r in res["questions"]]
        summ[mode] = {"hit@10": sum(1 for x in ranks if x and x <= 10), "hit@1": sum(1 for x in ranks if x == 1),
                      "mrr@10": round(sum(1 / x for x in ranks if x and x <= 10) / len(ranks), 3),
                      "paper@10": sum(1 for r in res["questions"] if (r["modes"][mode]["paper_first"] or 99) <= 10),
                      "ranks": ranks}
    for key in [f"{m}/{s}" for m in MODES for s in ("corpus", "paper")]:
        ranks = [r["modes"][key]["first_hit"] for r in res["equations"]]
        summ["eq " + key] = {"hit@10": sum(1 for x in ranks if x and x <= 10), "ranks": ranks}
    res["summary"] = summ
    with open(os.path.join(a.out, "results.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({"database": path, "chunk_vectors": len(cstore), "equation_vectors": len(estore),
                      "summary": summ}, indent=1))


if __name__ == "__main__":
    main()
