"""Stage K4 (brief 12.6): vectors of chunks and equation contexts in the `embeddings` table.

The float32 blobs in `embeddings` are the source of truth (brief 12.2); `embeddings.model` is
`<model name>@<revision7>` (kbtool.embed_model.model_key), so a new model or revision adds a
new set of rows and keeps the old one. Migration 0006 adds per row the sha256 of the exact
string embedded (`text_sha256`), its word-piece count and a truncation flag, and the table
`embed_models` (name, revision, weights hash, licence, recipes, runtime).

Recipes (the string embedded for one owner; changing a recipe changes the hashes, so the next
`kb embed` re-embeds exactly the rows it affects):
- chunk-v1: "<section number> <section title>\\n" + chunks.text, for the kinds abstract, body,
  appendix, caption, footnote (comments are never embedded, brief 12.4 item 3); the heading of
  an abstract is "Abstract", of a chunk without section nothing.
- eq-v1: "<section number> <section title>\\n" + equations.context + "\\n" + tex_norm (first 400
  characters).

Writing: the vectors are computed outside the writer lock; each batch is written inside it,
after re-reading the owners' current text, so a row whose text changed meanwhile (a
re-ingest) is skipped rather than stored with the wrong vector.
"""
import hashlib
import json
import os
import time

from . import __version__
from . import db as _db
from .lock import writer_lock

EMBED_CHUNK_KINDS = ("abstract", "body", "appendix", "caption", "footnote")
RECIPES = {
    "chunk": "chunk-v1: '<section number> <section title>\\n' + chunks.text; kinds abstract, body, appendix, "
             "caption, footnote; abstract heading 'Abstract'",
    "equation": "eq-v1: '<section number> <section title>\\n' + equations.context + '\\n' + tex_norm[:400]",
}
OWNER_KINDS = ("chunk", "equation")
EQ_TEX_CHARS = 400


def _heading(number, title, kind=None):
    if kind == "abstract":
        return "Abstract"
    return " ".join(x for x in (number, title) if x).strip()


def _join(head, *parts):
    body = "\n".join(p for p in parts if p)
    return f"{head}\n{body}" if head else body


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _in_clause(ids):
    return ",".join("?" * len(ids))


def chunk_texts(con, ids=None, paper=None):
    """[(chunk_id, string to embed)] in chunk_id order (recipe chunk-v1)."""
    q = ("SELECT c.chunk_id, c.kind, c.text, s.number, s.title FROM chunks c "
         "LEFT JOIN sections s ON s.section_id = c.section_id "
         f"WHERE c.kind IN ({_in_clause(EMBED_CHUNK_KINDS)})")
    args = list(EMBED_CHUNK_KINDS)
    if paper:
        q += " AND c.paper_id = ?"
        args.append(paper)
    out = []
    if ids is not None:
        ids = list(ids)
        for k in range(0, len(ids), 900):
            part = ids[k:k + 900]
            out += con.execute(q + f" AND c.chunk_id IN ({_in_clause(part)})", args + part).fetchall()
        out.sort()
    else:
        out = con.execute(q + " ORDER BY c.chunk_id", args).fetchall()
    return [(cid, _join(_heading(num, title, kind), text)) for cid, kind, text, num, title in out]


def equation_texts(con, ids=None, paper=None):
    """[(eq_id, string to embed)] in eq_id order (recipe eq-v1)."""
    q = ("SELECT e.eq_id, e.context, e.tex_norm, s.number, s.title FROM equations e "
         "LEFT JOIN sections s ON s.section_id = e.section_id WHERE 1=1")
    args = []
    if paper:
        q += " AND e.paper_id = ?"
        args.append(paper)
    out = []
    if ids is not None:
        ids = list(ids)
        for k in range(0, len(ids), 900):
            part = ids[k:k + 900]
            out += con.execute(q + f" AND e.eq_id IN ({_in_clause(part)})", args + part).fetchall()
        out.sort()
    else:
        out = con.execute(q + " ORDER BY e.eq_id", args).fetchall()
    return [(eid, _join(_heading(num, title), ctx or "", (tn or "")[:EQ_TEX_CHARS])) for eid, ctx, tn, num, title in out]


TEXTS = {"chunk": chunk_texts, "equation": equation_texts}


def has_schema(con):
    cols = {r[1] for r in con.execute("PRAGMA table_info(embeddings)")}
    tabs = _db.tables(con)
    return "text_sha256" in cols and "embed_models" in tabs


def register_model(con, emb, runtime):
    m = emb.m
    try:
        from .embed_model import weights_sha256
        wsha = weights_sha256(m) if m.get("name") != "test/hash" else None
    except Exception:
        wsha = None
    con.execute("INSERT INTO embed_models(model, name, revision, dim, pooling, normalized, max_seq_length, "
                "query_prefix, weights_sha256, license, source, recipe_json, runtime_json, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(model) DO UPDATE SET recipe_json=excluded.recipe_json, "
                "runtime_json=excluded.runtime_json, weights_sha256=excluded.weights_sha256",
                (emb.key, m["name"], m["revision"], emb.dim, m.get("pooling"), int(bool(m.get("normalize"))),
                 m.get("max_seq_length"), m.get("query_prefix"), wsha, m.get("license"), m.get("source"),
                 json.dumps(RECIPES, sort_keys=True), json.dumps(runtime, sort_keys=True), _db.utcnow()))


def stored(con, model, owner_kind):
    """{owner_id: text_sha256} of the stored vectors of one model and owner kind."""
    return dict(con.execute("SELECT owner_id, text_sha256 FROM embeddings WHERE model = ? AND owner_kind = ?",
                            (model, owner_kind)))


def plan(con, model, owner_kind, paper=None):
    """What `embed` would do: (todo [(id, text, sha)], orphans [ids], unchanged count)."""
    cur = [(i, t, sha(t)) for i, t in TEXTS[owner_kind](con, paper=paper)]
    have = stored(con, model, owner_kind)
    todo = [(i, t, s) for i, t, s in cur if have.get(i) != s]
    if paper:
        orphans = []                                   # only a full run decides what is orphaned
    else:
        ids = {i for i, _, _ in cur}
        orphans = [i for i in have if i not in ids]
    return todo, orphans, len(cur) - len(todo)


def embed(lay, emb, owner_kinds=OWNER_KINDS, paper=None, batch=256, limit=None, log=print, runtime=None):
    """Embed what is missing or changed; delete vectors whose owner no longer exists. Returns stats."""
    import numpy as np
    _db.init_db(lay)                                    # applies migration 0006 if needed (under the lock)
    runtime = runtime or {}
    with writer_lock(lay, what=f"embed register {emb.key}"):
        con = _db.connect_rw(lay.db_work)
        try:
            register_model(con, emb, runtime)
            con.commit()
        finally:
            con.close()
    stats = {"model": emb.key, "at": _db.utcnow(), "kinds": {}}
    for ok in owner_kinds:
        t0 = time.time()
        ro = _db.connect_ro(lay.db_work)
        try:
            todo, orphans, unchanged = plan(ro, emb.key, ok, paper=paper)
        finally:
            ro.close()
        if limit:
            todo = todo[:limit]
        st = {"todo": len(todo), "unchanged": unchanged, "written": 0, "skipped_changed": 0,
              "truncated": 0, "orphans_deleted": 0}
        log(f"{ok}: {len(todo)} to embed, {unchanged} unchanged, {len(orphans)} orphaned")
        for k in range(0, len(todo), batch):
            part = todo[k:k + batch]
            texts = [t for _, t, _ in part]
            ntok = emb.n_tokens(texts)
            vecs = emb.encode(texts)
            assert vecs.shape == (len(part), emb.dim) and vecs.dtype == np.float32
            with writer_lock(lay, what=f"embed {ok} {emb.key}"):
                con = _db.connect_rw(lay.db_work)
                try:
                    now = {i: sha(t) for i, t in TEXTS[ok](con, ids=[i for i, _, _ in part])}
                    rows = []
                    for (i, t, s), n, v in zip(part, ntok, vecs):
                        if now.get(i) != s:
                            st["skipped_changed"] += 1
                            continue
                        trunc = int(n > (emb.m.get("max_seq_length") or 10 ** 9))
                        st["truncated"] += trunc
                        rows.append((ok, i, emb.key, emb.dim, v.tobytes(), s, n, trunc, _db.utcnow()))
                    con.executemany("INSERT OR REPLACE INTO embeddings(owner_kind, owner_id, model, dim, vec, "
                                    "text_sha256, n_tokens, truncated, at) VALUES (?,?,?,?,?,?,?,?,?)", rows)
                    con.commit()
                    st["written"] += len(rows)
                finally:
                    con.close()
            done = min(k + batch, len(todo))
            el = time.time() - t0
            log(f"  {ok}: {done}/{len(todo)} in {el:.0f} s ({done / max(el, 1e-9):.1f}/s)")
        if orphans and not limit and not paper:
            with writer_lock(lay, what=f"embed orphans {emb.key}"):
                con = _db.connect_rw(lay.db_work)
                try:                                           # recomputed inside the lock
                    cur_ids = {i for i, _ in TEXTS[ok](con)}
                    gone = [i for i in stored(con, emb.key, ok) if i not in cur_ids]
                    con.executemany("DELETE FROM embeddings WHERE model=? AND owner_kind=? AND owner_id=?",
                                    [(emb.key, ok, i) for i in gone])
                    con.commit()
                    st["orphans_deleted"] = len(gone)
                finally:
                    con.close()
        st["seconds"] = round(time.time() - t0, 1)
        stats["kinds"][ok] = st
    with writer_lock(lay, what="embed log"):
        con = _db.connect_rw(lay.db_work)
        try:
            _db.log(con, "embed", emb.key, "ok", json.dumps(stats, sort_keys=True))
            con.commit()
        finally:
            con.close()
    return stats


def check(con, model, owner_kind):
    """Coverage and staleness of one set: counts of current owners, stored vectors, missing,
    stale (text changed since embedding) and orphaned rows."""
    cur = {i: sha(t) for i, t in TEXTS[owner_kind](con)}
    have = stored(con, model, owner_kind)
    return {"owners": len(cur), "vectors": len(have),
            "missing": sum(1 for i in cur if i not in have),
            "stale": sum(1 for i, s in cur.items() if i in have and have[i] != s),
            "orphaned": sum(1 for i in have if i not in cur)}


def load_vectors(con, model, owner_kind, ids=None):
    """(ids list, float32 matrix, {id: text_sha256}) of stored vectors, optionally restricted."""
    import numpy as np
    q = "SELECT owner_id, vec, text_sha256, dim FROM embeddings WHERE model = ? AND owner_kind = ?"
    rows = con.execute(q, (model, owner_kind)).fetchall()
    if ids is not None:
        ids = set(ids)
        rows = [r for r in rows if r[0] in ids]
    if not rows:
        return [], np.zeros((0, 0), dtype=np.float32), {}
    dim = rows[0][3]
    mat = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.float32).reshape(len(rows), dim)
    return [r[0] for r in rows], mat, {r[0]: r[2] for r in rows}


def models(con):
    try:
        return [dict(zip(("model", "name", "revision", "dim", "created_at"), r)) for r in
                con.execute("SELECT model, name, revision, dim, created_at FROM embed_models ORDER BY created_at")]
    except Exception:
        return []


def tool():
    return f"kbtool {__version__} embed_index"


def env_threads(default=8):
    try:
        return max(1, min(16, int(os.environ.get("KB_EMBED_THREADS", default))))
    except ValueError:
        return default
