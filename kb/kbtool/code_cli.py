"""Subcommands of the code stages K6-K7 (brief 12.7, 12.10), registered into `kb` by
kbtool.cli:

    kb fetch-repos [--repo R ...] [--refresh] [--dry-run] [--work DIR]
    kb ingest repo [--repo R ... | --all] [--this [--ref REF]]     (routed from `kb ingest`)
    kb code "SYMBOL or text" [--repo R] [--kind function|class|param|file|text] [-k N] [--db PATH]
    kb link add|list|check|load|explicit ...
    kb watch upstream [--no-fetch]
"""
import argparse
import json
import os
import sys
import time

from .paths import layout

CLAIMS = ("code", "link")          # stub names this module replaces in kbtool.cli


def _work_dir(a, lay, what):
    if a.work:
        return os.path.abspath(a.work)
    run_dir = os.environ.get("RUN_DIR")
    if run_dir:
        return os.path.join(run_dir, "work")
    return os.path.join(lay.home, "scratch", "kb", "tmp", f"{what}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")


# ---------------------------------------------------------------- fetch-repos
def cmd_fetch_repos(a):
    from . import code_fetch
    lay = layout(a.data_root)
    work = _work_dir(a, lay, "fetch-repos")
    recs = code_fetch.fetch_repos(lay, work, repos=a.repo, refresh=a.refresh, dry_run=a.dry_run,
                                  log=lambda s: print(s, flush=True))
    if a.dry_run:
        return 0
    by = {}
    for r in recs:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print("summary: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())), flush=True)
    for r in recs:
        if r["status"] != "ok":
            print(f"NOT CLONED {r['repo']}: {r['status']}: {r.get('error')}", flush=True)
    return 0 if all(r["status"] == "ok" for r in recs) else 1


# ---------------------------------------------------------------- ingest repo
def cmd_ingest_repo(argv, data_root=None):
    from . import code_index
    p = argparse.ArgumentParser(prog="kb ingest repo")
    p.add_argument("--repo", action="append", help="owner/name of a cloned manifest repository")
    p.add_argument("--all", action="store_true", help="every cloned repository with a record")
    p.add_argument("--this", action="store_true", help="this repository (athenak/src, python/nrpic, cosmo)")
    p.add_argument("--ref", default="main", help="git ref of this repository to index (default main)")
    p.add_argument("--no-chunks", action="store_true", help="files, symbols and params only")
    a = p.parse_args(argv)
    lay = layout(data_root)
    if not (a.repo or a.all or a.this):
        p.error("give --repo, --all or --this")
    res = code_index.ingest(lay, repos=a.repo, all_repos=a.all, this=a.this, ref=a.ref,
                            chunks=not a.no_chunks, log=lambda s: print(s, flush=True))
    bad = [r for r in res if r.get("status") != "ok"]
    for r in bad:
        print(f"NOT INDEXED {r['repo_id']}: {r.get('error')}", flush=True)
    return 1 if bad else 0


# ---------------------------------------------------------------- kb code
def cmd_code(a):
    from . import code_query
    lay = layout(a.data_root)
    hits = code_query.search(lay, a.query, repo=a.repo, kind=a.kind, k=a.k, db=a.db)
    if a.json:
        json.dump(hits, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(code_query.format_hits(hits))
    return 0 if hits else 1


# ---------------------------------------------------------------- kb link
def cmd_link(a):
    from . import links_paper_code as L
    lay = layout(a.data_root)
    if a.action == "load":
        n = L.load_curated(lay, a.file)
        print(f"loaded {n} links from {a.file or L.CURATED}")
        return 0
    if a.action == "check":
        rep = L.check_links(lay, a.file, db=a.db)
        sys.stdout.write(L.format_check(rep))
        return 0 if rep["n_bad"] == 0 else 1
    if a.action == "explicit":
        from .brief import load_github_manifest
        from .paths import kb_manifest_dir
        repos = [r["repo"] for r in load_github_manifest(os.path.join(kb_manifest_dir(), "github.tsv"))]
        rows = L.explicit_links(lay, repos)
        print("paper_id\tversion\tfile\tline\trepository\tin_manifest")
        for r in rows:
            print("\t".join(str(x) if x is not None else "" for x in r[:5]) + "\t" + ("yes" if r[5] else "no"))
        return 0
    if a.action == "list":
        rows = L.list_links(lay, paper=a.paper, db=a.db)
        for r in rows:
            print("\t".join("" if v is None else str(v) for v in r))
        return 0
    if a.action == "add":
        if not (a.paper and a.symbol and a.repo):
            print("kb link add needs --paper, --repo and --symbol", file=sys.stderr)
            return 2
        lid = L.add_link(lay, paper=a.paper, eq=a.eq, repo=a.repo, symbol=a.symbol, relation=a.relation,
                         status=a.status, evidence=a.evidence, by_owner=a.by)
        print(f"link {lid} added")
        return 0
    return 2


# ---------------------------------------------------------------- kb watch upstream
def cmd_watch(a):
    from . import code_watch
    if a.what != "upstream":
        print("usage: kb watch upstream", file=sys.stderr)
        return 2
    lay = layout(a.data_root)
    work = _work_dir(a, lay, "watch")
    rep = code_watch.watch(lay, work, fetch=not a.no_fetch, out_md=a.report, log=lambda s: print(s, flush=True))
    print(rep["summary"])
    return 0


def register(sub, data_root_getter=None):
    """Add the K6-K7 subcommands to the `kb` subparsers."""
    s = sub.add_parser("fetch-repos", help="K6: shallow clones of the repository manifest into kb-data/raw/github")
    s.add_argument("--repo", action="append", help="only this manifest repository (repeatable)")
    s.add_argument("--refresh", action="store_true", help="move an existing clone aside and clone again")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--work", help="work directory for the clones before they move into kb-data")
    s.set_defaults(fn=cmd_fetch_repos)

    s = sub.add_parser("code", help="K6: symbols, run parameters, files and code text of the indexed repositories")
    s.add_argument("query")
    s.add_argument("--repo", help="owner/name, or 'this' for this repository")
    s.add_argument("--kind", choices=("any", "function", "class", "symbol", "param", "file", "text"), default="any")
    s.add_argument("-k", type=int, default=20)
    s.add_argument("--db", help="database file (default db/current, else kb.sqlite)")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_code)

    s = sub.add_parser("link", help="K7: paper-code links (impl_links)")
    s.add_argument("action", choices=("add", "list", "check", "load", "explicit"))
    s.add_argument("--paper")
    s.add_argument("--eq", help="equation label or number in the paper")
    s.add_argument("--repo")
    s.add_argument("--symbol")
    s.add_argument("--relation", default="implements")
    s.add_argument("--status", default="claimed", choices=("claimed", "verified", "refuted"))
    s.add_argument("--evidence")
    s.add_argument("--by", default="kb")
    s.add_argument("--file", help="curated TSV (default kb/curated/paper_code_links.tsv)")
    s.add_argument("--db")
    s.set_defaults(fn=cmd_link)

    s = sub.add_parser("watch", help="K6: upstream watch (git ls-remote of AthenaK, inspection of particle branches)")
    s.add_argument("what", nargs="?", default="upstream")
    s.add_argument("--no-fetch", action="store_true", help="compare branch tips only; clone no branch")
    s.add_argument("--report", help="also write the markdown report here")
    s.add_argument("--work")
    s.set_defaults(fn=cmd_watch)
