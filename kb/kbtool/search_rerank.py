"""Retrieval at the answer location: a second stage over sentence windows (kb, wave 2b).

Why (tracks/kb/retrieval/JOURNAL.md, R3, run kb-20261119-141041-69232a4): of the nine golden
questions whose answer location the hybrid search of `kbtool.embed_search` missed, five had
the right paper in the top ten but ranked other chunks of it higher, and the answer chunks
are long (median about 550 word pieces) and mix topics (the end of a conclusion, future work
and acknowledgements in one chunk). One whole-chunk vector and one whole-chunk BM25 score
dilute a one-sentence answer; in one case the answer lay beyond the 512 word pieces the model
reads.

What this does, on top of the unchanged first stage (BM25 and chunk vectors fused by
reciprocal rank, depth 100, `embed_search`):
1. Pool: the first POOL chunks of the fused ranking (default 100), optionally plus every chunk
   (of the allowed kinds) of the first EXPAND papers of that ranking. The default has no
   expansion: in run kb-20261119-142613-942f713 expanding the first three papers crowded the
   pool with chunks of papers that came first by one chunk and cost paper hits (JOURNAL R4,
   R4b).
2. Windows: each pool chunk is cut into windows of WIN sentences (default 2), stride STRIDE
   (default 1), a window
   longer than MAX_CHARS cut again into slices; each window is prefixed with the chunk's
   section heading (as recipe chunk-v1 does), so no part of a chunk is beyond the model's
   512 word pieces.
3. Two window rankings of the pool chunks: BM25 of the windows (an in-memory FTS5 table with
   the main index's tokenizer, `porter unicode61`, and the same OR query), a chunk taking its
   best window; and the cosine of the query vector with the window vectors (same model, query
   instruction on the query only), a chunk taking its best window.
4. The pool is ordered by reciprocal-rank fusion (constant K_RRF of embed_search) of the
   window rankings, optionally with the first-stage fused order as a third ranking.
Window vectors are computed on the fly (nothing is written to the database) and cached in
the process by the sha256 of the embedded string.

Every hit carries the chunk's locator as `embed_search.describe_chunks` gives it, so the hit
level of the golden questions is judged exactly as for the first stage, plus the text offset
and a snippet of its best window.

    kb/.venv/bin/python -I kb/kbtool/search_rerank.py "QUESTION" [-k 10] [--paper ID] [--db PATH]
"""
import os
import re
import sqlite3
import sys

if __name__ == "__main__" and not __package__:                      # run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from kbtool import search_rerank as _self                       # noqa: E402
    sys.exit(_self.main())

from . import embed_index as X  # noqa: E402
from . import embed_search as S  # noqa: E402

POOL = 100
EXPAND = 0
WIN = 2
STRIDE = 1
MAX_CHARS = 1200
SLICE_OVERLAP = 200
K_RRF = S.K_RRF
CONFIGS = {
    # the four variants written down before the first evaluation (JOURNAL R4); DEFAULT is the
    # one chosen on the 32 golden questions and checked on the ten held-out questions
    # (run kb-20261119-142613-942f713: locator hits on the 32 golden questions 22, 22, 23, 25;
    # hybrid 23; on the ten held out 6, 6, 6, 6; hybrid 5)
    "w2": {"pool": 50, "expand": 3, "win": 2, "stride": 1, "with_stage1": False},
    "w3": {"pool": 50, "expand": 3, "win": 3, "stride": 2, "with_stage1": False},
    "w2+stage1": {"pool": 50, "expand": 3, "win": 2, "stride": 1, "with_stage1": True},
    "w2-noexpand": {"pool": 100, "expand": 0, "win": 2, "stride": 1, "with_stage1": False},
}
DEFAULT = "w2-noexpand"

RE_SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\\$(\[])|\n\s*\n")


def sentence_spans(text):
    """[(start, end)] character spans of the sentences of `text` (end exclusive), in order,
    covering every non-blank character."""
    spans, start = [], 0
    for m in RE_SENT_END.finditer(text):
        if text[start:m.start()].strip():
            spans.append((start, m.start()))
        start = m.end()
    if text[start:].strip():
        spans.append((start, len(text)))
    return spans


def window_spans(text, win=WIN, stride=STRIDE, max_chars=MAX_CHARS, overlap=SLICE_OVERLAP):
    """Windows of `win` sentences every `stride` sentences, the last one ending at the last
    sentence; a window longer than `max_chars` is cut into slices of that length with
    `overlap` characters in common. Every character of every sentence is in some window."""
    sents = sentence_spans(text)
    if not sents:
        return []
    out, n = [], len(sents)
    s = 0
    while True:
        e = min(n, s + win)
        a, b = sents[s][0], sents[e - 1][1]
        if b - a <= max_chars:
            out.append((a, b))
        else:
            step = max(1, max_chars - overlap)
            x = a
            while True:
                out.append((x, min(b, x + max_chars)))
                if x + max_chars >= b:
                    break
                x += step
        if e >= n:
            break
        s += stride
    return out


_CACHE = {}


def _window_vectors(embedder, strings):
    import numpy as np
    keys = [X.sha(t) for t in strings]
    todo = [(k, t) for k, t in zip(keys, strings) if k not in _CACHE]
    seen = set()
    todo = [(k, t) for k, t in todo if not (k in seen or seen.add(k))]
    if todo:
        vecs = embedder.encode([t for _, t in todo])
        for (k, _), v in zip(todo, vecs):
            _CACHE[k] = v
    return np.stack([_CACHE[k] for k in keys]) if keys else np.zeros((0, embedder.dim), dtype=np.float32)


def _pool_rows(con, ids):
    out = {}
    for k in range(0, len(ids), 900):
        part = list(ids[k:k + 900])
        q = ("SELECT c.chunk_id, c.paper_id, c.kind, c.text, s.number, s.title FROM chunks c "
             "LEFT JOIN sections s ON s.section_id = c.section_id "
             f"WHERE c.chunk_id IN ({','.join('?' * len(part))})")
        for cid, pid, kind, text, num, title in con.execute(q, part):
            out[cid] = (pid, kind, text or "", X._heading(num, title, kind))
    return out


def _expand(con, order, n_papers, flt):
    """Chunk ids (allowed kinds and filters) of the first `n_papers` papers of `order`."""
    if n_papers <= 0 or not order:
        return [], []
    papers = []
    for k in range(0, len(order), 900):
        part = order[k:k + 900]
        pid = dict(con.execute(f"SELECT chunk_id, paper_id FROM chunks WHERE chunk_id IN ({','.join('?' * len(part))})",
                               part).fetchall())
        for c in part:
            p = pid.get(c)
            if p and p not in papers:
                papers.append(p)
                if len(papers) == n_papers:
                    break
        if len(papers) == n_papers:
            break
    where, args = S._filters(**flt)
    ids = [r[0] for r in con.execute(
        "SELECT c.chunk_id FROM chunks c JOIN papers p ON p.paper_id = c.paper_id "
        f"WHERE {where} AND c.paper_id IN ({','.join('?' * len(papers))}) ORDER BY c.chunk_id", args + papers)]
    return ids, papers


def _window_bm25(query, windows):
    """Rank (1 best) of each window index under BM25 over the windows, or None if no term matches."""
    fq = S.fts_query(query)
    if not fq or not windows:
        return {}
    mem = sqlite3.connect(":memory:")
    try:
        mem.execute("CREATE VIRTUAL TABLE w USING fts5(text, tokenize='porter unicode61')")
        mem.executemany("INSERT INTO w(rowid, text) VALUES (?, ?)", [(i + 1, t) for i, t in enumerate(windows)])
        rows = mem.execute("SELECT rowid FROM w WHERE w MATCH ? ORDER BY bm25(w)", (fq,)).fetchall()
    finally:
        mem.close()
    return {r[0] - 1: k for k, r in enumerate(rows, 1)}


def rerank(con, query, first_order, embedder, qvec=None, pool=POOL, expand=EXPAND, with_stage1=False, flt=None,
           win=WIN, stride=STRIDE):
    """Order the pool built from `first_order` (first-stage chunk ids, best first) by the
    window rankings. Returns (ordered chunk ids, {chunk_id: details}, info)."""
    flt = flt or {"kind": "all", "paper": None, "group": None}
    base = list(first_order[:pool])
    extra, papers = _expand(con, list(first_order), expand, flt)
    in_base = set(base)
    ids = base + [c for c in extra if c not in in_base]
    rows = _pool_rows(con, ids)
    ids = [c for c in ids if c in rows]
    wins, owner, offs = [], [], []
    for c in ids:
        pid, kind, text, head = rows[c]
        for a, b in window_spans(text, win=win, stride=stride):
            wins.append(f"{head}\n{text[a:b]}" if head else text[a:b])
            owner.append(c)
            offs.append((a, b))
    info = {"pool": len(ids), "expanded_papers": papers, "windows": len(wins)}
    if not wins:
        return list(first_order), {}, info
    if qvec is None:
        qvec = embedder.encode([query], query=True)[0]
    W = _window_vectors(embedder, wins)
    cos = W @ qvec.astype(W.dtype)
    best_v, best_b = {}, {}
    for i, c in enumerate(owner):
        if c not in best_v or cos[i] > cos[best_v[c]]:
            best_v[c] = i
    for i, r in _window_bm25(query, wins).items():
        c = owner[i]
        if c not in best_b or r < best_b[c][1]:
            best_b[c] = (i, r)
    rankings = {"wvec": sorted(best_v, key=lambda c: (-float(cos[best_v[c]]), c)),
                "wbm25": sorted(best_b, key=lambda c: (best_b[c][1], c))}
    if with_stage1:
        rankings["stage1"] = [c for c in first_order if c in rows]
    fused = S.rrf(rankings, k0=K_RRF)
    order = sorted(fused, key=lambda c: (-fused[c][0], c))
    det = {}
    for c in order:
        i = best_v[c]
        det[c] = {"rrf": round(fused[c][0], 6), "ranks": fused[c][1], "window_cosine": round(float(cos[i]), 4),
                  "window_chars": list(offs[i]), "window_snippet": re.sub(r"\s+", " ", wins[i])[:240]}
    return order, det, info


def search(lay, query, k=10, config=DEFAULT, kind="all", paper=None, group=None, depth=100, db=None,
           embedder=None, model=None, store=None, con=None):
    """Hits best first (the fields of embed_search.search plus the best window). Returns (hits, info)."""
    from . import db as _db
    cfg = CONFIGS[config]
    own = con is None
    if own:
        path = _db.open_for_read(lay, db)
        if not os.path.exists(path):
            raise SystemExit(f"no database at {path}")
        con = _db.connect_ro(path)
    try:
        flt = {"kind": kind, "paper": paper, "group": group}
        rankings = {"bm25": S.rank_text(con, query, depth=depth, **flt)}
        if store is None:
            store = S.VectorStore(con, model or embedder.key, "chunk")
        qv = embedder.encode([query], query=True)[0]
        info = {"mode": f"rerank:{config}", "model": store.model, "vectors": len(store), "stale_dropped": 0}
        if len(store):
            allowed = S.allowed_ids(con, **flt) if (paper or group or kind not in (None, "all")) else None
            ids, _ = store.rank(qv, depth=depth, allowed=allowed)
            ids_ok, n_stale = S.drop_stale(con, ids, store, X.chunk_texts)
            info["stale_dropped"] = n_stale
            rankings["vector"] = ids_ok
        fused = S.rrf(rankings)
        first = sorted(fused, key=lambda i: (-fused[i][0], i))
        order, det, rinfo = rerank(con, query, first, embedder, qvec=qv, flt=flt, **cfg)
        info.update(rinfo)
        order = order[:k]
        meta = S.describe_chunks(con, lay, order)
        first_rank = {c: r for r, c in enumerate(first, 1)}
        hits = []
        for r, c in enumerate(order, 1):
            h = dict(meta.get(c, {"chunk_id": c}))
            d = det.get(c, {})
            h.update({"rank": r, "rrf": d.get("rrf"), "ranks": dict(d.get("ranks", {}))})
            if c in first_rank:
                h["ranks"]["first_stage"] = first_rank[c]
            for key in ("window_cosine", "window_chars", "window_snippet"):
                if key in d:
                    h[key] = d[key]
            hits.append(h)
        return hits, info
    finally:
        if own:
            con.close()


def main(argv=None):
    import argparse
    from . import embed_cli as EC
    from .paths import layout
    ap = argparse.ArgumentParser(prog="search_rerank")
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=10)
    ap.add_argument("--config", default=DEFAULT, choices=sorted(CONFIGS))
    ap.add_argument("--kind", default="all")
    ap.add_argument("--paper")
    ap.add_argument("--group")
    ap.add_argument("--db")
    ap.add_argument("--threads", type=int, default=None)
    a = ap.parse_args(argv)
    emb = EC._embedder("bge-small", a.threads)
    hits, info = search(layout(), a.query, k=a.k, config=a.config, kind=a.kind, paper=a.paper, group=a.group,
                        db=a.db, embedder=emb, model=EC._model_key("bge-small"))
    for h in hits:
        h.setdefault("rrf", 0.0)
    sys.stdout.write(S.format_hits([dict(h, rrf=h.get("rrf") or 0.0) for h in hits], info))
    return 0
