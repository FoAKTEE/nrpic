"""The `kb` command (brief 12.10). Stages K0 and K1 are implemented; the other subcommands
are stubs that name the stage that fills them and exit with status 3.

Exit codes: 0 success; 1 the check found problems (verify-downloads) or an error;
2 usage; 3 not implemented yet.
"""
import argparse
import json
import os
import shutil
import sys
import time

from . import SCHEMA_VERSION, __version__
from . import brief as _brief
from . import db as _db
from . import inventory as _inv
from .lock import writer_lock
from .paths import KB_DIR, default_brief, fetch_command, kb_manifest_dir, layout
from . import code_cli as _code_cli          # K6-K7: fetch-repos, ingest repo, code, link, watch
from . import papers_cli as _papers_cli      # K2-K3: ingest arxiv, resolve-bib, frontier, cites, export, show views

NOT_YET = 3

# subcommand -> (stage that fills it, one-line purpose); see brief 12.10
STUBS = {
    "search": ("K4-K5", "hybrid retrieval: full text, vectors, structured filters"),
    "code": ("K6", "symbols, code chunks and run parameters of the indexed repositories"),
    "frontier": ("K3", "works cited often by the corpus but absent from it"),
    "ingest": ("K2-K6", "TeX flattening, structure extraction, chunking; code index"),
    "resolve-bib": ("K3", "bibliography entries to arXiv id / DOI / INSPIRE record"),
    "embed": ("K4", "local embedding model over chunks, equations, code"),
    "eq": ("K5", "equation index search"),
    "cites": ("K3", "citation graph queries"),
    "link": ("K7", "paper-code links"),
    "claim": ("K8", "evidence queue seeded from the labelled statements of the brief"),
    "export": ("K2", "flattened text with section numbers"),
    "qa": ("K9", "integrity checks and golden-question retrieval test"),
}


def _out(obj, as_json):
    if as_json:
        json.dump(obj, sys.stdout, indent=1, sort_keys=True)
        sys.stdout.write("\n")
    else:
        for k, v in obj.items():
            print(f"{k:22s} {v}")


# ---------------------------------------------------------------- K0
def cmd_init(a):
    lay = layout(a.data_root)
    with writer_lock(lay, what="init-dirs"):
        for d in lay.dirs():
            os.makedirs(d, exist_ok=True)
        for name in ("arxiv.tsv", "github.tsv", "SOURCE.json"):
            shutil.copyfile(os.path.join(kb_manifest_dir(), name), os.path.join(lay.manifests, name))
    created, applied = _db.init_db(lay)
    print(f"data root {lay.data}: directories in place; manifests copied")
    print(f"database {lay.db_work}: {'created' if created else 'exists'}; migrations applied {applied or 'none'}; "
          f"schema version {_db.latest_version()}")
    return 0


def cmd_manifests(a):
    path = a.brief or default_brief()
    if not path:
        print("brief not found; pass --brief", file=sys.stderr)
        return 1
    if a.check:
        arxiv, github, prov = _brief.extract_manifests(path)
        same = True
        for name, rows in (("arxiv.tsv", arxiv), ("github.tsv", github)):
            have = open(os.path.join(kb_manifest_dir(), name)).read()
            want = "".join("\t".join(r) + "\n" for r in rows)
            ok = have == want
            same &= ok
            print(f"{name}: {'identical to' if ok else 'DIFFERS FROM'} the brief ({len(rows)} rows)")
        return 0 if same else 1
    arxiv, github, prov = _brief.write_manifests(path, kb_manifest_dir())
    print(f"wrote {len(arxiv)} arXiv rows (brief lines {prov['arxiv']['first_line']}-{prov['arxiv']['last_line']}) "
          f"and {len(github)} repositories (lines {prov['github']['first_line']}-{prov['github']['last_line']}) "
          f"to {kb_manifest_dir()}")
    return 0


# ---------------------------------------------------------------- K1
def cmd_verify(a):
    lay = layout(a.data_root)
    inv = _inv.verify(lay, a.manifests or kb_manifest_dir())
    md = _inv.report_md(inv)
    if not a.no_record:
        if not os.path.exists(lay.db_work):
            _db.init_db(lay)
        with writer_lock(lay, what="verify-downloads"):
            os.makedirs(lay.manifests, exist_ok=True)
            for name in ("arxiv.tsv", "github.tsv"):
                src = os.path.join(a.manifests or kb_manifest_dir(), name)
                shutil.copyfile(src, os.path.join(lay.manifests, name))
            _atomic_write(os.path.join(lay.manifests, "SHA256SUMS"),
                          "\n".join(_inv.sha256sums(inv, lay.data)) + "\n")
            _atomic_write(os.path.join(lay.manifests, "inventory.json"), json.dumps(inv, indent=1) + "\n")
            os.makedirs(lay.logs, exist_ok=True)
            _atomic_write(os.path.join(lay.logs, "verify-downloads-%s.md" % inv["checked_at"].replace(":", "")), md)
            _db.record_inventory(lay, inv)
    if a.report:
        os.makedirs(os.path.dirname(os.path.abspath(a.report)), exist_ok=True)
        _atomic_write(a.report, md)
    if a.json:
        json.dump(inv, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        s = inv["arxiv"]["status"]
        print(f"arXiv: {inv['arxiv']['manifest_rows']} in manifest; " +
              ", ".join(f"{k} {s.get(k, 0)}" for k in _inv.STATUS_ORDER) +
              f"; extra {inv['arxiv']['extra']}")
        for pri in ("3", "2", "1"):
            d = inv["arxiv"]["by_priority"].get(pri, {})
            print(f"  priority {pri}: " + ", ".join(f"{k} {d.get(k, 0)}" for k in _inv.STATUS_ORDER))
        print(f"GitHub: {inv['github']['manifest_rows']} in manifest; " +
              ", ".join(f"{k} {v}" for k, v in sorted(inv["github"]["status"].items())))
        for p in inv["papers"] + inv["extras"]:
            for x in p["problems"]:
                print(f"PROBLEM {p['id']}: {x}")
        if not a.no_record:
            print(f"recorded: {lay.manifests}/SHA256SUMS, inventory.json; table downloads in {lay.db_work}")
        if a.report:
            print(f"report: {a.report}")
    bad = inv["arxiv"]["status"].get("problem", 0) + sum(1 for p in inv["extras"] if p["status"] == "problem")
    return 1 if bad else 0


def cmd_fetch_missing(a):
    """Fetch the missing (and failed) manifest entries of one priority through the one
    download command of the machine. Replaces this process with that command (os.execv), so
    the process id stays the same and there is exactly one download process."""
    lay = layout(a.data_root)
    inv = _inv.verify(lay, a.manifests or kb_manifest_dir())
    ids = []                                   # priorities in the order given (brief 17: 3, then 2, then 1)
    for pri in a.priority:
        ids += [i for i in _inv.missing_ids(inv, priority=pri, include_failed=not a.skip_failed) if i not in ids]
    if a.limit:
        ids = ids[:a.limit]
    if a.ids_file:
        os.makedirs(os.path.dirname(os.path.abspath(a.ids_file)), exist_ok=True)
        _atomic_write(a.ids_file, "".join(i + "\n" for i in ids))
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"# kb fetch-missing {stamp} pid {os.getpid()}: {len(ids)} ids of priority "
          f"{' then '.join(map(str, a.priority))}: {' '.join(ids)}",
          flush=True)
    if a.dry_run or not ids:
        return 0
    cmd = fetch_command()
    if not os.path.isfile(cmd):
        print(f"fetch command not found: {cmd}", file=sys.stderr)
        return 1
    sys.stdout.flush()
    sys.stderr.flush()
    os.execv(sys.executable, [sys.executable, "-I", cmd] + ids)


# ---------------------------------------------------------------- status, snapshot, show
def status_dict(lay):
    st = {"tool": f"kbtool {__version__}", "data_root": lay.data,
          "schema_version_code": _db.latest_version(), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rows = _brief.load_arxiv_manifest(os.path.join(kb_manifest_dir(), "arxiv.tsv"))
    st["manifest_arxiv"] = len(rows)
    st["manifest_arxiv_by_priority"] = {str(p): sum(1 for r in rows if r["priority"] == p) for p in (3, 2, 1)}
    st["manifest_github"] = len(_brief.load_github_manifest(os.path.join(kb_manifest_dir(), "github.tsv")))
    try:
        st["raw_arxiv_entries"] = len([n for n in os.listdir(lay.raw_arxiv) if not n.startswith(".")])
    except FileNotFoundError:
        st["raw_arxiv_entries"] = 0
    try:
        st["raw_github_entries"] = len(os.listdir(lay.raw_github))
    except FileNotFoundError:
        st["raw_github_entries"] = 0
    st["snapshot"] = os.readlink(lay.db_current) if os.path.islink(lay.db_current) else None
    path = lay.db_work if os.path.exists(lay.db_work) else None
    st["database"] = path
    if path:
        con = _db.connect_ro(path)
        try:
            st["schema_version_db"] = _db.schema_version(con)
            counts = {}
            for t in ("papers", "chunks", "equations", "bib_entries", "citations", "repos", "code_files",
                      "params", "claims", "embeddings", "downloads", "repo_downloads"):
                try:
                    counts[t] = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                except Exception:
                    counts[t] = None
            st["rows"] = counts
            st.update(_papers_cli.status_counts(con))          # K2-K3 (kbtool/papers_cli.py)
            try:
                st["downloads_by_status"] = dict(con.execute(
                    "SELECT status, count(*) FROM downloads WHERE in_manifest=1 GROUP BY status").fetchall())
                st["downloads_checked_at"] = con.execute("SELECT max(checked_at) FROM downloads").fetchone()[0]
                pass
            except Exception:
                pass
        finally:
            con.close()
    return st


def cmd_status(a):
    lay = layout(a.data_root)
    st = status_dict(lay)
    if a.write_state:
        _atomic_write(os.path.join(KB_DIR, "STATE.json"), json.dumps(st, indent=1, sort_keys=True) + "\n")
    _out(st, a.json)
    return 0


def cmd_snapshot(a):
    lay = layout(a.data_root)
    final, sha = _db.snapshot(lay)
    print(f"snapshot {final} (sha256 {sha}); current -> {os.path.basename(final)}")
    return 0


def cmd_show(a):
    """K1 part: the manifest row and the download check of one paper. The text views
    (--abstract, --section, --eq, --fig) come with K2."""
    if a.abstract or a.section or a.eq or a.fig:
        return _papers_cli.show_views(a)                        # K2 (kbtool/papers_cli.py)
    lay = layout(a.data_root)
    rows = {r["id"]: r for r in _brief.load_arxiv_manifest(os.path.join(kb_manifest_dir(), "arxiv.tsv"))}
    pid = a.paper_id.replace("arXiv:", "")
    res = _inv.check_paper(lay, pid, rows.get(pid))
    json.dump(res, sys.stdout, indent=1)
    sys.stdout.write("\n")
    return 0


def cmd_stub(a):
    if a.cmd == "ingest" and a.args[:1] == ["repo"]:            # K6 (kbtool.code_cli)
        return _code_cli.cmd_ingest_repo(a.args[1:], data_root=a.data_root)
    if a.cmd == "ingest" and a.args[:1] == ["arxiv"]:           # K2-K3 (kbtool.papers_cli)
        return _papers_cli.cmd_ingest_arxiv(a.args[1:], data_root=a.data_root)
    stage, what = STUBS[a.cmd]
    print(f"kb {a.cmd}: {what}; filled by stage {stage} of brief section 12, not built yet", file=sys.stderr)
    return NOT_YET


def _atomic_write(path, text):
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def parser():
    p = argparse.ArgumentParser(prog="kb", description="knowledge base of the NRPIC-cosmology program")
    p.add_argument("--data-root", help="kb-data directory (default $NRPIC_HOME/kb-data or $KB_DATA_ROOT)")
    p.add_argument("--version", action="version", version=f"kbtool {__version__} (schema {SCHEMA_VERSION}+)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="K0: create the kb-data directories and the database")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("manifests", help="extract the manifests of brief section 17 into kb/manifests")
    s.add_argument("--brief")
    s.add_argument("--check", action="store_true", help="compare kb/manifests with the brief, write nothing")
    s.set_defaults(fn=cmd_manifests)

    s = sub.add_parser("status", help="counts, schema version, snapshot id")
    s.add_argument("--json", action="store_true")
    s.add_argument("--write-state", action="store_true", help="also write kb/STATE.json")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("verify-downloads", help="K1: manifests <-> kb-data/raw")
    s.add_argument("--json", action="store_true")
    s.add_argument("--no-record", action="store_true", help="write nothing into kb-data")
    s.add_argument("--report", help="also write the markdown report here")
    s.add_argument("--manifests", help="directory with arxiv.tsv and github.tsv (default kb/manifests)")
    s.set_defaults(fn=cmd_verify)

    s = sub.add_parser("fetch-missing", help="fetch missing manifest entries through harness/bin/nrpic-fetch-arxiv")
    s.add_argument("--priority", type=int, choices=(1, 2, 3), required=True, nargs="+",
                   help="one or more priorities, fetched in the order given (e.g. 3 2 1)")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--skip-failed", action="store_true", help="do not retry entries whose last attempt failed")
    s.add_argument("--limit", type=int)
    s.add_argument("--ids-file", help="write the list of ids here")
    s.add_argument("--manifests")
    s.set_defaults(fn=cmd_fetch_missing)

    s = sub.add_parser("snapshot", help="freeze kb.sqlite -> kb-YYYYMMDD-<sha>.sqlite, move `current`")
    s.set_defaults(fn=cmd_snapshot)

    s = sub.add_parser("show", help="one paper (K1: manifest row and download check)")
    s.add_argument("paper_id")
    s.add_argument("--abstract", action="store_true")
    s.add_argument("--section")
    s.add_argument("--eq")
    s.add_argument("--fig")
    s.add_argument("--max-chars", type=int)
    s.add_argument("--db", help="text views: database file (default db/current, else kb.sqlite)")
    s.add_argument("--work", action="store_true", help="text views: read the working database kb.sqlite")
    s.set_defaults(fn=cmd_show)

    _code_cli.register(sub)                    # fetch-repos, code, link, watch (kbtool/code_cli.py)
    _papers_cli.register(sub)                  # resolve-bib, frontier, cites, export (kbtool/papers_cli.py)

    for name, (stage, what) in STUBS.items():
        if name in _code_cli.CLAIMS or name in _papers_cli.CLAIMS:
            continue
        s = sub.add_parser(name, help=f"[{stage}, not built] {what}")
        s.add_argument("args", nargs=argparse.REMAINDER)
        s.set_defaults(fn=cmd_stub)
    return p


def main(argv=None):
    a = parser().parse_args(argv)
    return a.fn(a)
