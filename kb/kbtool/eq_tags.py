"""Stage K5 (brief 12.6): tags of the equation index from kb/curated/equation_tags.yaml.

`kb eq --apply-tags` evaluates the rules (format in the YAML file's header) on label, context
and tex_norm of every equation and writes the sorted tag list into equations.tags_json (JSON
list, [] when no rule matches), in batches inside the writer lock. tex_norm and the symbol set
(symbols_json) are computed at ingestion (kbtool/tex_text.py: normalize_equation, symbols).

Note: `kb ingest arxiv` rewrites the equations of a paper with tags_json NULL, so the tags are
re-applied after every ingest (`kb eq --apply-tags --paper ID` or a full run).
"""
import hashlib
import json
import os
import re

from . import db as _db
from .lock import writer_lock
from .paths import KB_DIR

RULES = os.path.join(KB_DIR, "curated", "equation_tags.yaml")
FIELDS = ("label", "context", "before", "after", "tex", "not_label", "not_context", "not_before", "not_tex")
NEAR = 250            # characters of context on each side of the [EQ] marker that `before`/`after` see


def load_rules(path=None):
    import yaml
    path = path or RULES
    raw = open(path, encoding="utf-8").read()
    r = yaml.safe_load(raw)
    if not isinstance(r, dict) or "tags" not in r:
        raise ValueError(f"{path}: no 'tags' mapping")
    compiled = {}
    for name, spec in r["tags"].items():
        clauses = []
        for cl in spec.get("any", []):
            unknown = set(cl) - set(FIELDS)
            if unknown:
                raise ValueError(f"{path}: tag {name}: unknown fields {sorted(unknown)}")
            c = {}
            for f, v in cl.items():
                pats = v if isinstance(v, list) else [v]
                flags = 0 if f.endswith("tex") else re.IGNORECASE
                c[f] = [re.compile(p, flags) for p in pats]
            clauses.append(c)
        if not clauses:
            raise ValueError(f"{path}: tag {name} has no clause")
        compiled[name] = {"description": spec.get("description", ""), "clauses": clauses}
    return {"version": r.get("version"), "sha256": hashlib.sha256(raw.encode()).hexdigest(), "path": path,
            "tags": compiled}


def _field(f, label, context, tex):
    base = f[4:] if f.startswith("not_") else f
    if base in ("before", "after"):
        ctx = context or ""
        if "[EQ]" not in ctx:
            return ctx
        pre, post = ctx.split("[EQ]", 1)
        return pre[-NEAR:] if base == "before" else post[:NEAR]
    return {"label": label, "context": context, "tex": tex}[base] or ""


def match_clause(cl, label, context, tex):
    for f, pats in cl.items():
        s = _field(f, label, context, tex)
        if f.startswith("not_"):
            if any(p.search(s) for p in pats):
                return False
        elif not all(p.search(s) for p in pats):
            return False
    return True


def tags_for(rules, label, context, tex):
    return sorted(name for name, t in rules["tags"].items()
                  if any(match_clause(cl, label, context, tex) for cl in t["clauses"]))


def apply(lay, rules_path=None, paper=None, dry_run=False, batch=5000):
    """Tag all equations (or one paper's). Returns counts per tag and the number of rows changed."""
    rules = load_rules(rules_path)
    ro = _db.connect_ro(lay.db_work)
    try:
        q = "SELECT eq_id, label, context, tex_norm, tags_json FROM equations"
        rows = ro.execute(q + (" WHERE paper_id = ?" if paper else ""), (paper,) if paper else ()).fetchall()
    finally:
        ro.close()
    counts = {name: 0 for name in rules["tags"]}
    updates, tagged = [], 0
    for eid, label, ctx, tn, old in rows:
        tg = tags_for(rules, label, ctx, tn)
        for t in tg:
            counts[t] += 1
        tagged += bool(tg)
        new = json.dumps(tg)
        if new != old:
            updates.append((new, eid))
    rep = {"rules": os.path.relpath(rules["path"], os.path.dirname(KB_DIR)), "rules_sha256": rules["sha256"],
           "rules_version": rules["version"], "paper": paper, "equations": len(rows), "tagged": tagged,
           "per_tag": counts, "changed": len(updates), "dry_run": dry_run}
    if dry_run:
        return rep
    for k in range(0, len(updates), batch):
        with writer_lock(lay, what="eq tags"):
            con = _db.connect_rw(lay.db_work)
            try:
                con.executemany("UPDATE equations SET tags_json = ? WHERE eq_id = ?", updates[k:k + batch])
                con.commit()
            finally:
                con.close()
    with writer_lock(lay, what="eq tags log"):
        con = _db.connect_rw(lay.db_work)
        try:
            _db.log(con, "eq-tags", paper or "all", "ok", json.dumps(rep, sort_keys=True))
            con.commit()
        finally:
            con.close()
    return rep
