"""Tests E1 and E2 of the embed package (tracks/kb/embed/JOURNAL.md).

E1: the model loads offline, gives unit vectors of 384 components, and ranks a passage about
cloud-in-cell deposition above two unrelated passages for a deposition query.
E2: word-piece counts of a random sample of chunks of each kind (truncation at 512) and the
encoding throughput on the processors.

    kb/.venv/bin/python -I tracks/kb/embed/scripts/bench_model.py OUT_DIR [--threads 16] [--n 400]

Reads kb-data/db/kb.sqlite read-only; writes OUT_DIR/bench.json only (no paper text).
"""
import argparse
import json
import os
import random
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(WT, "kb"))

from kbtool import embed_model as E          # noqa: E402
from kbtool import embed_index as X          # noqa: E402
from kbtool.paths import layout              # noqa: E402

# our own sentences (no paper text)
QUERY = "order of the shape function used to deposit particles on the grid"
PASSAGES = {
    "cic": "Each particle is spread over the eight nearest cell centres with linear cloud-in-cell weights "
           "that sum to one, a first-order B-spline shape function for the deposition of the sources.",
    "shift": "The shift vector follows a Gamma-driver condition with a damping parameter eta, and the lapse "
             "obeys the one-plus-log slicing.",
    "cmb": "The temperature anisotropies of the cosmic microwave background constrain the baryon density "
           "and the spectral index of the primordial fluctuations.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--n", type=int, default=400, help="sampled chunks per kind for the token counts")
    ap.add_argument("--n-time", type=int, default=256, help="body chunks encoded for the timing")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"threads": a.threads}

    t0 = time.time()
    emb = E.STEmbedder(threads=a.threads)
    res["load_s"] = round(time.time() - t0, 2)
    q = emb.encode([QUERY], query=True)
    p = emb.encode(list(PASSAGES.values()))
    import numpy as np
    res["dim"] = int(q.shape[1])
    res["norms"] = [float(x) for x in np.linalg.norm(np.vstack([q, p]), axis=1)]
    res["e1_scores"] = {k: float(p[i] @ q[0]) for i, k in enumerate(PASSAGES)}
    res["e1_pass"] = bool(res["dim"] == 384 and max(abs(n - 1) for n in res["norms"]) < 1e-5
                          and res["e1_scores"]["cic"] > max(res["e1_scores"]["shift"], res["e1_scores"]["cmb"]))

    lay = layout()
    con = sqlite3.connect(f"file:{lay.db_work}?mode=ro", uri=True)
    rng = random.Random(20261115)
    res["tokens"] = {}
    for kind in ("abstract", "body", "appendix", "caption", "footnote"):
        ids = [r[0] for r in con.execute("SELECT chunk_id FROM chunks WHERE kind=?", (kind,))]
        pick = sorted(rng.sample(ids, min(a.n, len(ids))))
        texts = [t for _, t in X.chunk_texts(con, ids=pick)]
        n = emb.n_tokens(texts)
        res["tokens"][kind] = {"n": len(n), "counts": n,
                               "truncated_fraction": sum(1 for x in n if x > E.MODEL["max_seq_length"]) / len(n)}
    body = [r[0] for r in con.execute("SELECT chunk_id FROM chunks WHERE kind='body'")]
    pick = sorted(rng.sample(body, a.n_time))
    texts = [t for _, t in X.chunk_texts(con, ids=pick)]
    emb.encode(texts[:32])                                # warm-up
    t0 = time.time()
    emb.encode(texts)
    dt = time.time() - t0
    res["timing"] = {"n": len(texts), "seconds": round(dt, 2), "chunks_per_s": round(len(texts) / dt, 2)}
    con.close()
    with open(os.path.join(a.out, "bench.json"), "w") as f:
        json.dump(res, f, indent=1)
    summ = {k: v for k, v in res.items() if k != "tokens"}
    summ["truncated"] = {k: round(v["truncated_fraction"], 3) for k, v in res["tokens"].items()}
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
