"""Subcommands of stages K4-K5: `kb embed`, `kb search`, `kb eq` (brief 12.6, 12.10).

    kb embed [--only chunks|equations] [--paper ID] [--limit N] [--batch N] [--threads N]
             [--model bge-small|hash] [--fetch-model] [--check] [--json]
    kb search "QUERY" [-k 10] [--kind all|text|caption|eq|code] [--group G14] [--paper ID]
              [--hybrid | --text-only | --vector-only] [--depth 100] [--json] [--db PATH | --work]
    kb eq "LATEX or keywords" [-k 10] [--tag TAG] [--paper ID] [--group G] [--hybrid | --text-only |
          --vector-only] [--json]
    kb eq --apply-tags [--rules FILE] [--paper ID] [--dry-run]     K5 tagging into equations.tags_json
    kb eq --list-tags

Vector work needs numpy, torch and the model in kb/.venv: when a command that needs them runs
under the system python3, it re-executes itself under kb/.venv/bin/python -I (as `kb ingest
arxiv` does). Exit codes: 0 hits / success, 1 no hit or a check failed, 2 usage.
"""
import json
import os
import sys

from .paths import KB_DIR, layout

CLAIMS = ("search", "embed", "eq")
VENV_PY = os.path.join(KB_DIR, ".venv", "bin", "python")


def _ensure_venv():
    """Re-execute under kb/.venv when numpy is missing (system python3 -I)."""
    try:
        import numpy  # noqa: F401
        return
    except ImportError:
        pass
    if os.path.exists(VENV_PY) and os.environ.get("KB_NO_REEXEC") != "1" \
            and os.path.realpath(sys.prefix) != os.path.realpath(os.path.join(KB_DIR, ".venv")):
        kb_bin = os.path.join(KB_DIR, "bin", "kb")
        sys.stdout.flush()
        os.execv(VENV_PY, [VENV_PY, "-I", kb_bin] + sys.argv[1:])
    raise SystemExit("numpy is not available: create kb/.venv (kb/EMBEDDING.md) or use --text-only")


def _embedder(name, threads=None):
    from . import embed_index as X
    from . import embed_model as E
    if name == "hash":
        return E.HashEmbedder()
    if name in ("bge-small", E.model_key(), E.MODEL["name"]):
        return E.STEmbedder(threads=threads or X.env_threads())
    raise SystemExit(f"unknown model {name!r} (bge-small or hash)")


def _model_key(name):
    from . import embed_model as E
    return "hash64@test" if name == "hash" else E.model_key()


def _runtime(threads, batch):
    rt = {"threads": threads, "batch": batch, "python": sys.version.split()[0]}
    for mod in ("torch", "sentence_transformers", "transformers", "tokenizers", "numpy"):
        try:
            rt[mod] = __import__(mod).__version__
        except Exception:
            pass
    return rt


# ---------------------------------------------------------------- kb embed
def cmd_embed(a):
    from . import embed_model as E
    lay = layout(a.data_root)
    if a.fetch_model:
        rec = E.fetch()
        print(json.dumps({"model_dir": E.model_dir(), "revision": rec["revision"],
                          "weights_sha256": rec["files"]["model.safetensors"]["sha256"]}, indent=1))
        return 0
    _ensure_venv()
    from . import db as _db
    from . import embed_index as X
    kinds = {"chunks": ("chunk",), "equations": ("equation",), None: X.OWNER_KINDS}[a.only]
    if a.check:
        path = _db.open_for_read(lay, a.db or (lay.db_work if a.work else None))
        con = _db.connect_ro(path)
        try:
            if not X.has_schema(con):
                print(f"{path}: no embedding schema (migration 0006 not applied)")
                return 1
            key = _model_key(a.model)
            rep = {ok: X.check(con, key, ok) for ok in kinds}
            rep["model"] = key
            rep["models"] = X.models(con)
            rep["database"] = os.path.realpath(path)
        finally:
            con.close()
        print(json.dumps(rep, indent=1))
        bad = sum(rep[ok]["missing"] + rep[ok]["stale"] + rep[ok]["orphaned"] for ok in kinds)
        return 1 if bad else 0
    threads = a.threads or X.env_threads()
    emb = _embedder(a.model, threads)
    stats = X.embed(lay, emb, owner_kinds=kinds, paper=a.paper, batch=a.batch, limit=a.limit,
                    runtime=_runtime(threads, a.batch), log=lambda s: print(s, flush=True))
    print(json.dumps(stats, indent=1, sort_keys=True))
    return 0


# ---------------------------------------------------------------- kb search
def _mode(a):
    if a.text_only:
        return "text"
    if a.vector_only:
        return "vector"
    return "hybrid"


def cmd_search(a):
    lay = layout(a.data_root)
    if a.kind == "code":
        from . import code_query
        hits = code_query.search(lay, a.query, kind="text", k=a.k, db=a.db)
        if a.json:
            json.dump(hits, sys.stdout, indent=1)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(code_query.format_hits(hits))
        return 0 if hits else 1
    if a.kind == "eq":
        a.tag = None
        return cmd_eq(a)
    mode = _mode(a)
    from . import embed_search as S
    emb = None
    if mode != "text" or getattr(a, "rerank", False):
        _ensure_venv()
        emb = _embedder(a.model, a.threads)
    db = a.db or (lay.db_work if a.work else None)
    if getattr(a, "rerank", False):
        # second stage over the first 100 hybrid chunks (kbtool/search_rerank.py, config w2-noexpand;
        # chosen in tracks/kb/retrieval/JOURNAL.md R4)
        if mode != "hybrid":
            print("kb search: --rerank works on the hybrid first stage only", file=sys.stderr)
            return 2
        from . import search_rerank as RR
        hits, info = RR.search(lay, a.query, k=a.k, kind=a.kind, paper=a.paper, group=a.group, depth=a.depth,
                               db=db, embedder=emb, model=_model_key(a.model))
        hits = [dict(h, rrf=h.get("rrf") or 0.0) for h in hits]
        if a.json:
            json.dump({"hits": hits, "info": info}, sys.stdout, indent=1)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(S.format_hits(hits, info))
        return 0 if hits else 1
    hits, info = S.search(lay, a.query, k=a.k, mode=mode, kind=a.kind, paper=a.paper, group=a.group,
                          depth=a.depth, db=db, embedder=emb, model=_model_key(a.model) if emb else None)
    if a.json:
        json.dump({"hits": hits, "info": info}, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(S.format_hits(hits, info))
    return 0 if hits else 1


# ---------------------------------------------------------------- kb eq
def cmd_eq(a):
    lay = layout(a.data_root)
    from . import eq_tags as T
    if getattr(a, "list_tags", False):
        rules = T.load_rules(a.rules)
        for name, r in rules["tags"].items():
            print(f"{name:22s} {r.get('description', '')}")
        return 0
    if getattr(a, "apply_tags", False):
        rep = T.apply(lay, rules_path=a.rules, paper=a.paper, dry_run=a.dry_run)
        print(json.dumps(rep, indent=1, sort_keys=True))
        return 0
    if not a.query:
        raise SystemExit("kb eq: give a query, --apply-tags or --list-tags")
    mode = _mode(a)
    from . import eq_search as Q
    emb = None
    if mode != "text":
        _ensure_venv()
        emb = _embedder(a.model, a.threads)
    db = a.db or (lay.db_work if a.work else None)
    hits, info = Q.search(lay, a.query, k=a.k, mode=mode, tag=getattr(a, "tag", None), paper=a.paper,
                          group=a.group, depth=a.depth, db=db, embedder=emb,
                          model=_model_key(a.model) if emb else None)
    if a.json:
        json.dump({"hits": hits, "info": info}, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(Q.format_hits(hits, info))
    return 0 if hits else 1


def _common(s):
    s.add_argument("-k", type=int, default=10)
    s.add_argument("--paper")
    s.add_argument("--group")
    s.add_argument("--depth", type=int, default=100, help="candidates taken from each ranking before fusion")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--hybrid", action="store_true", help="BM25 and vectors fused by reciprocal rank (default)")
    g.add_argument("--text-only", action="store_true", help="BM25 of the full-text index only (standard library)")
    g.add_argument("--vector-only", action="store_true", help="vector neighbours only")
    s.add_argument("--model", default="bge-small", help="bge-small (default) or hash (tests)")
    s.add_argument("--threads", type=int, default=4)
    s.add_argument("--json", action="store_true")
    s.add_argument("--db", help="database file (default db/current, else kb.sqlite)")
    s.add_argument("--work", action="store_true", help="read the working database kb.sqlite")


def register(sub):
    s = sub.add_parser("embed", help="K4: vectors of chunks and equation contexts with the local model")
    s.add_argument("--only", choices=("chunks", "equations"))
    s.add_argument("--paper")
    s.add_argument("--limit", type=int)
    s.add_argument("--batch", type=int, default=256)
    s.add_argument("--threads", type=int, help="processor threads (default $KB_EMBED_THREADS or 8, at most 16)")
    s.add_argument("--model", default="bge-small", help="bge-small (default) or hash (tests)")
    s.add_argument("--fetch-model", action="store_true", help="download the pinned model once (kb/EMBEDDING.md)")
    s.add_argument("--check", action="store_true", help="coverage and staleness of the stored vectors")
    s.add_argument("--db")
    s.add_argument("--work", action="store_true")
    s.set_defaults(fn=cmd_embed)

    s = sub.add_parser("search", help="K4: hybrid retrieval (BM25 + vectors, reciprocal-rank fusion)")
    s.add_argument("query")
    s.add_argument("--kind", default="all", choices=("all", "text", "caption", "eq", "code"))
    s.add_argument("--rerank", action="store_true",
                   help="re-rank the first 100 hybrid chunks by sentence windows (slower; better answer location)")
    _common(s)
    s.set_defaults(fn=cmd_search, tag=None)

    s = sub.add_parser("eq", help="K5: equation index (normalized TeX, tags, context vectors)")
    s.add_argument("query", nargs="?")
    s.add_argument("--tag", help="only equations with this tag (kb eq --list-tags)")
    s.add_argument("--apply-tags", action="store_true", help="tag every equation by kb/curated/equation_tags.yaml")
    s.add_argument("--list-tags", action="store_true")
    s.add_argument("--rules", help="tag rules (default kb/curated/equation_tags.yaml)")
    s.add_argument("--dry-run", action="store_true")
    _common(s)
    s.set_defaults(fn=cmd_eq)
