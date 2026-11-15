"""`kb eq "LATEX or keywords"` (stage K5, brief 12.6): equation search by text matching and
context vectors together.

- text: BM25 of `equations_fts` (columns tex_norm and context). A query that looks like TeX
  (a backslash, ^, _ or =) is first normalized with the same function as the stored tex_norm
  (kbtool.tex_text.normalize_equation: \\dfrac -> \\frac, {\\rm x} -> \\mathrm{x}, spacing
  removed), then split into the alphanumeric runs the FTS tokenizer (unicode61) indexes, so
  query and stored tex_norm are cut the same way, joined by OR; keywords are reduced to
  content words.
- vector: cosine between the query vector and the stored equation vectors (recipe eq-v1:
  section heading, context, tex_norm).
- fused by reciprocal rank (k = 60); filters --tag (equations.tags_json), --paper, --group.
"""
import json
import os
import re

from . import db as _db
from . import embed_index as X
from . import embed_search as S

TEXISH = re.compile(r"[\\^_=]")


def fts_query(q):
    if TEXISH.search(q):
        try:
            from .tex_text import normalize_equation
            q = normalize_equation(q)
        except Exception:
            pass
        seen, toks = set(), []
        for t in re.findall(r"[A-Za-z0-9]+", q):          # the runs FTS5 unicode61 indexes
            if t not in seen:
                seen.add(t)
                toks.append(t)
        return " OR ".join(f'"{t}"' for t in toks) if toks else None
    return S.fts_query(q)


def _filters(tag=None, paper=None, group=None):
    where, args = ["1=1"], []
    if tag:
        where.append("e.tags_json LIKE ?")
        args.append(f'%"{tag}"%')
    if paper:
        where.append("e.paper_id = ?")
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
    sql = ("SELECT e.eq_id FROM equations_fts JOIN equations e ON e.eq_id = equations_fts.rowid "
           "JOIN papers p ON p.paper_id = e.paper_id "
           f"WHERE equations_fts MATCH ? AND {where} ORDER BY bm25(equations_fts) LIMIT ?")
    return [r[0] for r in con.execute(sql, [fq] + args + [depth])]


def allowed_ids(con, **flt):
    where, args = _filters(**flt)
    return [r[0] for r in con.execute("SELECT e.eq_id FROM equations e JOIN papers p ON p.paper_id = e.paper_id "
                                      f"WHERE {where}", args)]


def describe(con, lay, ids, tex_chars=160):
    loc = S.Locator(lay)
    out = {}
    for k in range(0, len(ids), 900):
        part = list(ids[k:k + 900])
        q = ("SELECT e.eq_id, e.paper_id, p.version, p.grp, e.env, e.label, e.number, s.number, s.title, "
             "e.char_start, e.char_end, e.tex_norm, e.tags_json FROM equations e "
             "JOIN papers p ON p.paper_id = e.paper_id LEFT JOIN sections s ON s.section_id = e.section_id "
             f"WHERE e.eq_id IN ({','.join('?' * len(part))})")
        for (eid, pid, ver, grp, env, label, num, snum, stitle, cs, ce, tn, tags) in con.execute(q, part):
            tn = tn or ""
            out[eid] = {"eq_id": eid, "paper_id": pid, "version": ver, "group": grp, "env": env, "label": label,
                        "number": num, "section": " ".join(x for x in (snum, stitle) if x) or None,
                        "char_start": cs, "char_end": ce, "source": loc.lines(pid, cs, ce),
                        "tex_norm": tn[:tex_chars] + (" ..." if len(tn) > tex_chars else ""),
                        "tags": json.loads(tags) if tags else []}
    return out


def search(lay, query, k=10, mode="hybrid", tag=None, paper=None, group=None, depth=100, db=None,
           embedder=None, model=None, store=None, con=None):
    own = con is None
    if own:
        path = _db.open_for_read(lay, db)
        if not os.path.exists(path):
            raise SystemExit(f"no database at {path}")
        con = _db.connect_ro(path)
    info = {"mode": mode, "database": os.path.realpath(_db.open_for_read(lay, db)) if own else None,
            "stale_dropped": 0, "fts_query": fts_query(query)}
    try:
        flt = {"tag": tag, "paper": paper, "group": group}
        rankings, scores = {}, {}
        if mode in ("hybrid", "text"):
            rankings["bm25"] = rank_text(con, query, depth=depth, **flt)
        if mode in ("hybrid", "vector"):
            if store is None:
                store = S.VectorStore(con, model or embedder.key, "equation")
            info["model"], info["vectors"] = store.model, len(store)
            if len(store) == 0:
                info["note"] = f"no equation vectors of model {store.model}: run kb embed; text ranking only"
            else:
                qv = embedder.encode([query], query=True)[0]
                allowed = allowed_ids(con, **flt) if (tag or paper or group) else None
                ids, sc = store.rank(qv, depth=depth, allowed=allowed)
                ids_ok, info["stale_dropped"] = S.drop_stale(con, ids, store, X.equation_texts)
                rankings["vector"] = ids_ok
                scores = dict(zip(ids, sc))
        fused = S.rrf(rankings)
        order = sorted(fused, key=lambda i: (-fused[i][0], i))[:k]
        meta = describe(con, lay, order)
        hits = []
        for r, i in enumerate(order, 1):
            h = dict(meta.get(i, {"eq_id": i}))
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
        num = f"Eq. ({h['number']})" if h.get("number") else "unnumbered"
        out.append(f"{h['rank']:2d}. {h.get('paper_id')}{h.get('version') or ''} {num} {h.get('label') or ''} "
                   f"[{', '.join(h.get('tags') or []) or 'no tag'}] {h.get('section') or '-'}\n"
                   f"    {h.get('source') or '-'} | eq {h['eq_id']} | {rk} | rrf {h['rrf']:.4f}"
                   + (f" | cos {h['cosine']:.3f}" if "cosine" in h else "") +
                   f"\n    {h.get('tex_norm', '')}")
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
