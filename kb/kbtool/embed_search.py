"""Hybrid retrieval over paper chunks (stage K4, brief 12.6 and 12.10, `kb search`).

Two rankings of the same candidate set (non-comment chunks, narrowed by the structured
filters --kind, --group, --paper):
- text: BM25 of the full-text index `chunks_fts` (FTS5 `bm25()`), the query reduced to its
  content words joined by OR;
- vector: cosine between the query vector (with the model's query instruction) and the stored
  chunk vectors of one model (exhaustive, numpy).
They are fused by reciprocal rank, score(d) = sum over rankings of 1 / (K_RRF + rank), ranks
from 1, K_RRF = 10 (chosen over the usual 60 on the K9 golden questions, 23 against 21 hits in
the top 10, and confirmed on the ten held-out questions, 5 against 4; run
kb-20261115-164430-5aca10c, tracks/kb/embed/JOURNAL.md, test E7). A vector candidate whose stored text hash no longer matches its chunk
(re-ingested since embedding) is dropped and counted as stale.

Every hit carries its locator: paper id and version, chunk kind, section number and title,
the character range in build/tex/<id_>/flat.tex and the source file and line range through
build/tex/<id_>/sourcemap.json.

Text-only search needs the standard library only; vector and hybrid search need numpy and
the model (kb/.venv).
"""
import bisect
import json
import os
import re

from . import db as _db
from . import embed_index as X

K_RRF = 10
KINDS = {"text": ("abstract", "body", "appendix", "footnote"), "caption": ("caption",),
         "all": X.EMBED_CHUNK_KINDS}
STOP = set("""a an the of in on at to for from by with and or is are was were be been being it its this that these
those which what how where when who whom whose why do does did can could would should will shall may might must as
into than then there their our we you they he she them his her not no yes if so such about over under between
using use used any all each per via also whether one two other paper papers""".split())


def fts_query(q):
    """Content words of the query as an FTS5 OR query (quoted, so no FTS syntax gets through)."""
    seen, toks = set(), []
    for t in re.findall(r"[A-Za-z0-9]+", q.lower()):
        if t in STOP or (len(t) < 2 and not t.isdigit()) or t in seen:
            continue
        seen.add(t)
        toks.append(t)
    return " OR ".join(f'"{t}"' for t in toks) if toks else None


def _filters(kind="all", paper=None, group=None):
    kinds = KINDS.get(kind or "all")
    if kinds is None:
        raise ValueError(f"unknown kind {kind!r} (one of {sorted(KINDS)})")
    where = [f"c.kind IN ({','.join('?' * len(kinds))})"]
    args = list(kinds)
    if paper:
        where.append("c.paper_id = ?")
        args.append(paper.replace("arXiv:", ""))
    if group:
        where.append("p.grp = ?")
        args.append(group)
    return " AND ".join(where), args


def rank_text(con, q, depth=100, **flt):
    fq = fts_query(q)
    if not fq:
        return []
    where, args = _filters(**flt)
    sql = ("SELECT c.chunk_id FROM chunks_fts JOIN chunks c ON c.chunk_id = chunks_fts.rowid "
           "JOIN papers p ON p.paper_id = c.paper_id "
           f"WHERE chunks_fts MATCH ? AND {where} ORDER BY bm25(chunks_fts) LIMIT ?")
    return [r[0] for r in con.execute(sql, [fq] + args + [depth])]


def allowed_ids(con, **flt):
    where, args = _filters(**flt)
    return [r[0] for r in con.execute("SELECT c.chunk_id FROM chunks c JOIN papers p ON p.paper_id = c.paper_id "
                                      f"WHERE {where}", args)]


class VectorStore:
    """Stored vectors of one model and owner kind, loaded once per process."""

    def __init__(self, con, model, owner_kind):
        import numpy as np
        self.np = np
        self.model, self.owner_kind = model, owner_kind
        self.schema = X.has_schema(con)                 # a snapshot older than migration 0006 has none
        if self.schema:
            self.ids, self.mat, self.sha = X.load_vectors(con, model, owner_kind)
        else:
            self.ids, self.mat, self.sha = [], np.zeros((0, 0), dtype=np.float32), {}
        self.row = {i: k for k, i in enumerate(self.ids)}

    def __len__(self):
        return len(self.ids)

    def rank(self, qvec, depth=100, allowed=None):
        np = self.np
        if not len(self.ids):
            return [], []
        if allowed is not None:
            rows = np.array(sorted(self.row[i] for i in allowed if i in self.row), dtype=np.int64)
        else:
            rows = np.arange(len(self.ids))
        if rows.size == 0:
            return [], []
        s = self.mat[rows] @ qvec.astype(np.float32)
        n = min(depth, rows.size)
        top = np.argpartition(-s, n - 1)[:n]
        top = top[np.argsort(-s[top], kind="stable")]
        return [self.ids[rows[t]] for t in top], [float(s[t]) for t in top]


def drop_stale(con, ids, store, texts_fn):
    """Remove candidates whose current recipe text differs from the text that was embedded."""
    now = {i: X.sha(t) for i, t in texts_fn(con, ids=ids)}
    keep = [i for i in ids if now.get(i) is not None and now[i] == store.sha.get(i)]
    return keep, len(ids) - len(keep)


def rrf(rankings, k0=K_RRF):
    """{id: (score, {name: rank})} for rankings {name: [ids best first]}."""
    out = {}
    for name, ids in rankings.items():
        for r, i in enumerate(ids, 1):
            s, ranks = out.get(i, (0.0, {}))
            ranks[name] = r
            out[i] = (s + 1.0 / (k0 + r), ranks)
    return out


# ------------------------------------------------------------------ locators
class Locator:
    def __init__(self, lay):
        self.lay = lay
        self._maps = {}

    def smap(self, pid):
        if pid not in self._maps:
            p = os.path.join(self.lay.build, "tex", pid.replace("/", "_"), "sourcemap.json")
            try:
                m = json.load(open(p))
                self._maps[pid] = ([e[0] for e in m], m) if m else None    # empty for PDF-only papers
            except (OSError, ValueError):
                self._maps[pid] = None
        return self._maps[pid]

    def lines(self, pid, start, end):
        """'file:Lx-Ly' (or 'fileA:Lx-fileB:Ly') of a flat.tex character range, or None."""
        sm = self.smap(pid)
        if sm is None or start is None:
            return None
        offs, m = sm
        a = m[max(0, bisect.bisect_right(offs, start) - 1)]
        b = m[max(0, bisect.bisect_right(offs, max(start, (end or start) - 1)) - 1)]
        if a[1] == b[1]:
            return f"{a[1]}:L{a[2]}" + (f"-{b[2]}" if b[2] != a[2] else "")
        return f"{a[1]}:L{a[2]}-{b[1]}:L{b[2]}"


def describe_chunks(con, lay, ids, snippet=240):
    loc = Locator(lay)
    out = {}
    for k in range(0, len(ids), 900):
        part = list(ids[k:k + 900])
        q = ("SELECT c.chunk_id, c.paper_id, p.version, p.grp, c.kind, s.number, s.title, c.char_start, c.char_end, "
             "c.text FROM chunks c JOIN papers p ON p.paper_id = c.paper_id "
             "LEFT JOIN sections s ON s.section_id = c.section_id "
             f"WHERE c.chunk_id IN ({','.join('?' * len(part))})")
        for cid, pid, ver, grp, kind, num, title, cs, ce, text in con.execute(q, part):
            t = re.sub(r"\s+", " ", text or "").strip()
            out[cid] = {"chunk_id": cid, "paper_id": pid, "version": ver, "group": grp, "kind": kind,
                        "section": " ".join(x for x in (num, title) if x) or None,
                        "char_start": cs, "char_end": ce, "source": loc.lines(pid, cs, ce),
                        "snippet": t[:snippet] + (" ..." if len(t) > snippet else "")}
    return out


# ------------------------------------------------------------------ search
def search(lay, query, k=10, mode="hybrid", kind="all", paper=None, group=None, depth=100, db=None,
           embedder=None, model=None, store=None, con=None):
    """Hits best first, each with its locator, its rank in each ranking and the fused score.
    mode: 'hybrid', 'text' or 'vector'. Returns (hits, info)."""
    own = con is None
    if own:
        path = _db.open_for_read(lay, db)
        if not os.path.exists(path):
            raise SystemExit(f"no database at {path}")
        con = _db.connect_ro(path)
    info = {"mode": mode, "database": os.path.realpath(_db.open_for_read(lay, db)) if own else None,
            "stale_dropped": 0}
    try:
        flt = {"kind": kind, "paper": paper, "group": group}
        rankings, scores = {}, {}
        if mode in ("hybrid", "text"):
            rankings["bm25"] = rank_text(con, query, depth=depth, **flt)
        if mode in ("hybrid", "vector"):
            if store is None:
                store = VectorStore(con, model or embedder.key, "chunk")
            info["model"] = store.model
            info["vectors"] = len(store)
            if len(store) == 0:
                info["note"] = f"no vectors of model {store.model}: run kb embed; text ranking only"
            else:
                qv = embedder.encode([query], query=True)[0]
                allowed = allowed_ids(con, **flt) if (paper or group or kind not in (None, "all")) else None
                ids, sc = store.rank(qv, depth=depth, allowed=allowed)
                ids_ok, n_stale = drop_stale(con, ids, store, X.chunk_texts)
                info["stale_dropped"] = n_stale
                rankings["vector"] = ids_ok
                scores = dict(zip(ids, sc))
        fused = rrf(rankings)
        order = sorted(fused, key=lambda i: (-fused[i][0], i))[:k]
        meta = describe_chunks(con, lay, order)
        hits = []
        for r, i in enumerate(order, 1):
            h = dict(meta.get(i, {"chunk_id": i}))
            h.update({"rank": r, "rrf": round(fused[i][0], 6), "ranks": fused[i][1]})
            if i in scores:
                h["cosine"] = round(scores[i], 4)
            hits.append(h)
        return hits, info
    finally:
        if own:
            con.close()


def format_hits(hits, info):
    out = []
    for h in hits:
        rk = " ".join(f"{n} #{r}" for n, r in sorted(h["ranks"].items()))
        ver = h.get("version") or ""
        out.append(f"{h['rank']:2d}. {h.get('paper_id')}{ver} [{h.get('kind')}] {h.get('section') or '-'}\n"
                   f"    {h.get('source') or 'flat.tex chars %s-%s' % (h.get('char_start'), h.get('char_end'))}"
                   f" | chunk {h['chunk_id']} | {rk} | rrf {h['rrf']:.4f}"
                   + (f" | cos {h['cosine']:.3f}" if "cosine" in h else "") +
                   f"\n    {h.get('snippet', '')}")
    if not hits:
        out.append("no match")
    tail = f"({info.get('mode')}"
    if info.get("model"):
        tail += f", model {info['model']}, {info.get('vectors')} vectors"
    if info.get("stale_dropped"):
        tail += f", {info['stale_dropped']} stale vectors dropped"
    if info.get("database"):
        tail += f", database {info['database']}"
    out.append(tail + ")")
    if info.get("note"):
        out.append("note: " + info["note"])
    return "\n".join(out) + "\n"
