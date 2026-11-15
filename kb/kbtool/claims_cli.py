"""`kb claim ...` (brief 12.8, 12.10): the evidence queue.

    kb claim seed [--source TRACK ...] [--dry-run] [--tsv PATH]   notes of wave 1 -> claims, checked
    kb claim check [--id N ...]           re-run the locator and number check (auto labels only)
    kb claim list [--track T] [--paper ID] [--label L] [--status S] [--json] [--limit N]
    kb claim show N                       one claim: locators, check detail, history
    kb claim add --text T --paper ID [--locator L] --label L --by WHO [--kind K] [--track T]
    kb claim verify N --by WHO --evidence TEXT [--locator L]     a person read the passage
    kb claim refute N --by WHO --evidence TEXT                   prints the tracks to notify
    kb claim stats [--json]

Writes go to kb-data/db/kb.sqlite inside the writer lock; reads use --db, else kb.sqlite
(the working database holds the queue between snapshots). Runs without the `kb` wiring as
    python3 -I kb/kbtool/claims_cli.py claim <subcommand> ...
"""
import os
import sys

if __name__ == "__main__" and not __package__:                      # run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from kbtool import claims_cli as _self                          # noqa: E402
    sys.exit(_self.main())

import argparse  # noqa: E402
import collections  # noqa: E402
import json  # noqa: E402
import sqlite3  # noqa: E402
import subprocess  # noqa: E402

from . import __version__  # noqa: E402
from . import claims_check as _ck  # noqa: E402
from . import claims_curated as _cur  # noqa: E402
from . import claims_db as _cdb  # noqa: E402
from . import claims_parse as _cp  # noqa: E402
from .lock import writer_lock  # noqa: E402
from .paths import CHECKOUT, layout  # noqa: E402

CLAIMS = {"claim"}
TOOL = f"kb claims_check {__version__}"


def _git(*args):
    return subprocess.run(["git", "-C", CHECKOUT] + list(args), capture_output=True, text=True, check=True).stdout


def read_note(spec):
    """(text, commit) of a note at its ref, read through git (the other owners' branches)."""
    commit = _git("rev-parse", spec.ref).strip()
    text = _git("show", f"{commit}:{spec.path}")
    return text, commit


def collect(specs, store, only=None):
    """[(spec, commit, [(seed, checked)])] for the notes."""
    out = []
    for spec in specs:
        if only and spec.track not in only:
            continue
        try:
            md, commit = read_note(spec)
        except subprocess.CalledProcessError as e:
            print(f"cannot read {spec.ref}:{spec.path}: {e.stderr.strip()}", file=sys.stderr)
            continue
        seeds = _cp.parse_note(md, spec, spec.ref)
        out.append((spec, commit, [(s, _ck.check_claim(s.text, s.locators, store)) for s in seeds]))
    # the errata requests, transcribed (claims_curated); the request must still exist at its ref
    refs = {t: r for t, r, _ in _cur.SPECS}
    cur = _cur.seeds(refs)
    for track, ref, path in _cur.SPECS:
        if only and track not in only:
            continue
        spec = _cp.SourceSpec(track, ref, path, default_label="JUDGEMENT", kind_hint="erratum",
                              note="transcribed in claims_curated")
        try:
            _, commit = read_note(spec)
        except subprocess.CalledProcessError as e:
            print(f"cannot read {ref}:{path}: {e.stderr.strip()}", file=sys.stderr)
            continue
        items = [s for s in cur if s.origin_path == path]
        out.append((spec, commit, [(s, _ck.check_claim(s.text, s.locators, store)) for s in items]))
    return out


def _store(lay, con):
    return _ck.Store(lay.raw_arxiv, os.path.join(lay.build, "tex"), con)


def _db_path(lay, a):
    return getattr(a, "db", None) or lay.db_work


def write_tsv(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    cols = ("claim_id", "track", "source_label", "label", "status", "kind", "paper_id", "locator", "numbers",
            "missing", "origin_path", "origin_line", "text")
    with open(path, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "") if r.get(c) is not None else "").replace("\t", " ").replace("\n", " ")
                              for c in cols) + "\n")


def cmd_seed(a):
    lay = layout(a.data_root)
    specs = _cp.wave1_sources()
    if a.dry_run:
        con = _cdb.connect(_db_path(lay, a), ro=True) if os.path.exists(_db_path(lay, a)) else None
        res = collect(specs, _store(lay, con), a.source)
        rows = []
        for spec, commit, items in res:
            for s, (st, det, _) in items:
                rows.append({"track": s.track, "source_label": s.label, "label": _cdb.label_for(s.label, st),
                             "status": st, "kind": s.kind, "paper_id": s.paper_id,
                             "locator": _cdb.locator_string(s.locators), "numbers": det.get("numbers", 0),
                             "missing": ",".join(det.get("missing", [])), "origin_path": s.origin_path,
                             "origin_line": s.origin_line, "text": s.text})
        _summary(rows)
        if a.tsv:
            write_tsv(a.tsv, rows)
        return 0
    by = a.by or "kb (claims seed)"
    with writer_lock(lay, what="claims seed"):
        con = _cdb.connect(lay.db_work)
        try:
            _cdb.ensure(con)
            con.commit()
            if a.rebuild:
                why = rebuild_refused(lay, con)
                if why:
                    print(f"--rebuild refused: {why}", file=sys.stderr)
                    return 1
                own = [(r[0],) for r in con.execute("SELECT claim_id FROM claim_meta WHERE " + _cdb.OWN_SEED)]
                for t in ("claim_events", "claim_locators", "claim_meta", "claims"):
                    con.executemany(f"DELETE FROM {t} WHERE claim_id=?", own)
                con.commit()
                print(f"rebuild: {len(own)} claims of the K8 seed removed; rows of other writers kept")
            res = collect(specs, _store(lay, con), a.source)
            counts = collections.Counter()
            con.execute("BEGIN")
            for spec, commit, items in res:
                keys = set()
                for s, chk in items:
                    cid, what = _cdb.upsert_seed(con, s, commit, chk, by, TOOL)
                    keys.add(s.seed_key())
                    counts[what] += 1
                counts["stale"] += _cdb.mark_stale(con, spec.path, keys, by)
            con.execute("INSERT INTO ingest_log(at, step, target, status, message, tool_version) VALUES (?,?,?,?,?,?)",
                        (_cdb.utcnow(), "claims-seed", ",".join(sorted({s.path for s, _, _ in res})), "ok",
                         json.dumps(dict(counts)), TOOL))
            con.commit()
        finally:
            con.close()
    print("seeded: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    con = _cdb.connect(lay.db_work, ro=True)
    try:
        rows = _cdb.rows(con)
    finally:
        con.close()
    for r in rows:
        det = json.loads(r["status_detail"] or "{}")
        r["numbers"] = det.get("numbers", 0)
        r["missing"] = ",".join(det.get("missing", []))
    _summary(rows)
    if a.tsv:
        write_tsv(a.tsv, rows)
    return 0


def rebuild_refused(lay, con):
    """Reason not to empty the claim tables, or ''. Claim ids are stable once published
    (a snapshot holds them) or once a person has set a label."""
    n = con.execute("SELECT count(*) FROM claim_meta WHERE label_set_by != 'auto' AND " + _cdb.OWN_SEED).fetchone()[0]
    if n:
        return f"{n} claims of the seed carry a label set by a person"
    if os.path.exists(lay.db_current):
        snap = _cdb.connect(os.path.realpath(lay.db_current), ro=True)
        try:
            k = snap.execute("SELECT count(*) FROM claims").fetchone()[0]
        except sqlite3.Error:
            k = 0
        finally:
            snap.close()
        if k:
            return f"snapshot {os.path.basename(os.path.realpath(lay.db_current))} already holds {k} claims"
    return ""


def _summary(rows):
    by_t = collections.defaultdict(collections.Counter)
    for r in rows:
        by_t[str(r["track"])][str(r["status"])] += 1
        by_t[str(r["track"])]["label:" + str(r["label"])] += 1
    for t in sorted(by_t):
        c = by_t[t]
        print(f"{t:12s} " + " ".join(f"{k}={v}" for k, v in sorted(c.items())))
    tot = collections.Counter(str(r["status"]) for r in rows)
    lab = collections.Counter(str(r["label"]) for r in rows)
    print(f"total {len(rows)}: " + ", ".join(f"{k} {v}" for k, v in sorted(tot.items())) +
          " | labels " + ", ".join(f"{k} {v}" for k, v in sorted(lab.items(), key=lambda x: str(x[0]))))


def cmd_check(a):
    """Re-check the locators of seeded claims (auto labels only; people's labels stay)."""
    lay = layout(a.data_root)
    specs = _cp.wave1_sources()
    with writer_lock(lay, what="claims check"):
        con = _cdb.connect(lay.db_work)
        try:
            _cdb.ensure(con)
            res = collect(specs, _store(lay, con), None)
            con.execute("BEGIN")
            counts = collections.Counter()
            want = set(a.id or [])
            for spec, commit, items in res:
                for s, chk in items:
                    row = con.execute("SELECT claim_id FROM claim_meta WHERE seed_key=?", (s.seed_key(),)).fetchone()
                    if row and (not want or row[0] in want):
                        _, what = _cdb.upsert_seed(con, s, commit, chk, a.by or "kb (claims check)", TOOL)
                        counts[what] += 1
            con.commit()
        finally:
            con.close()
    print("checked: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


def _ro(lay, a):
    path = _db_path(lay, a)
    con = _cdb.connect(path, ro=True)
    if not _cdb.has_tables(con):
        print(f"{path}: no claim tables yet (run `kb claim seed`)", file=sys.stderr)
        con.close()
        return None
    return con


def cmd_list(a):
    lay = layout(a.data_root)
    con = _ro(lay, a)
    if con is None:
        return 1
    where, args = [], []
    for col, val in (("m.track", a.track), ("c.paper_id", a.paper), ("c.label", a.label), ("m.status", a.status)):
        if val:
            where.append(f"{col}=?")
            args.append(val)
    try:
        rows = _cdb.rows(con, " AND ".join(where), tuple(args))
    finally:
        con.close()
    if a.limit:
        rows = rows[:a.limit]
    if a.json:
        json.dump(rows, sys.stdout, indent=1)
        sys.stdout.write("\n")
        return 0
    for r in rows:
        print(f"{r['claim_id']:5d} {r['label']:10s} {str(r['status']):10s} {str(r['track']):11s} "
              f"{str(r['locator'] or '-')[:48]:48s} {r['text'][:90]}")
    print(f"# {len(rows)} claims")
    return 0


def cmd_show(a):
    lay = layout(a.data_root)
    con = _ro(lay, a)
    if con is None:
        return 1
    try:
        rows = _cdb.rows(con, "c.claim_id=?", (a.claim_id,))
        if not rows:
            print(f"no claim {a.claim_id}", file=sys.stderr)
            return 1
        r = rows[0]
        r["status_detail"] = json.loads(r["status_detail"] or "{}")
        r["locators"] = [dict(zip(("paper_id", "version", "file", "line_start", "line_end", "written", "resolved",
                                   "problem", "flat_start", "flat_end", "chunk_ids"), x)) for x in con.execute(
            "SELECT paper_id, version, file, line_start, line_end, written, resolved, problem, flat_start, flat_end, "
            "chunk_ids_json FROM claim_locators WHERE claim_id=? ORDER BY ord", (a.claim_id,))]
        r["events"] = [dict(zip(("at", "by", "action", "from_label", "to_label", "from_status", "to_status",
                                 "evidence"), x)) for x in con.execute(
            "SELECT at, by, action, from_label, to_label, from_status, to_status, substr(evidence,1,300) "
            "FROM claim_events WHERE claim_id=? ORDER BY event_id", (a.claim_id,))]
    finally:
        con.close()
    json.dump(r, sys.stdout, indent=1)
    sys.stdout.write("\n")
    return 0


def _write(lay, what, fn):
    with writer_lock(lay, what=what):
        con = _cdb.connect(lay.db_work)
        try:
            _cdb.ensure(con)
            con.execute("BEGIN")
            out = fn(con)
            con.commit()
            return out
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()


def cmd_add(a):
    lay = layout(a.data_root)
    cid = _write(lay, "claim add", lambda con: _cdb.add_claim(
        con, a.text, a.kind, a.paper, a.locator, a.label, a.by, a.origin or f"added by {a.by}", a.track or a.by,
        a.evidence or ""))
    print(f"claim {cid} added")
    return 0


def cmd_verify(a):
    lay = layout(a.data_root)
    try:
        _write(lay, "claim verify", lambda con: _cdb.verify(con, a.claim_id, a.by, a.evidence, a.locator))
    except (ValueError, KeyError) as e:
        print(f"claim {a.claim_id}: {e}", file=sys.stderr)
        return 1
    print(f"claim {a.claim_id}: fulltext, checked by {a.by}")
    return 0


def cmd_refute(a):
    lay = layout(a.data_root)
    try:
        tracks = _write(lay, "claim refute", lambda con: _cdb.refute(con, a.claim_id, a.by, a.evidence))
    except KeyError as e:
        print(f"no claim {e}", file=sys.stderr)
        return 1
    print(f"claim {a.claim_id}: refuted by {a.by}; notify: {', '.join(tracks) or 'nobody recorded'}")
    return 0


def stats(con):
    """Counts for the QA report and `kb claim stats`."""
    out = {"claims": con.execute("SELECT count(*) FROM claims").fetchone()[0]}
    if not _cdb.has_tables(con):
        return out
    out["by_label"] = dict(con.execute("SELECT label, count(*) FROM claims GROUP BY 1").fetchall())
    out["by_status"] = dict(con.execute("SELECT status, count(*) FROM claim_meta GROUP BY 1").fetchall())
    out["by_track_status"] = {}
    for t, s, n in con.execute("SELECT track, status, count(*) FROM claim_meta GROUP BY 1, 2"):
        out["by_track_status"].setdefault(t, {})[s] = n
    out["by_source_label"] = dict(con.execute("SELECT source_label, count(*) FROM claim_meta GROUP BY 1").fetchall())
    out["locators"] = con.execute("SELECT count(*), sum(resolved) FROM claim_locators").fetchone()
    out["papers"] = con.execute("SELECT count(DISTINCT paper_id) FROM claims WHERE paper_id IS NOT NULL").fetchone()[0]
    out["with_chunk"] = con.execute("SELECT count(*) FROM claims WHERE chunk_id IS NOT NULL").fetchone()[0]
    out["checked_by_person"] = con.execute("SELECT count(*) FROM claim_meta WHERE label_set_by != 'auto'").fetchone()[0]
    return out


def cmd_stats(a):
    lay = layout(a.data_root)
    con = _ro(lay, a)
    if con is None:
        return 1
    try:
        st = stats(con)
    finally:
        con.close()
    json.dump(st, sys.stdout, indent=1, default=str)
    sys.stdout.write("\n")
    return 0


def register(sub):
    p = sub.add_parser("claim", help="K8: evidence queue (seed, check, list, show, add, verify, refute, stats)")
    p.add_argument("--db", help="database to read (default kb.sqlite, the working database)")
    cs = p.add_subparsers(dest="claim_cmd", required=True)
    s = cs.add_parser("seed", help="parse the tracks' wave-1 notes into claims and check their locators")
    s.add_argument("--source", nargs="+", help="only these owner ids")
    s.add_argument("--dry-run", action="store_true", help="parse and check, write nothing")
    s.add_argument("--tsv", help="write a table of the claims here")
    s.add_argument("--by")
    s.add_argument("--rebuild", action="store_true",
                   help="empty the claim tables first; refused once a snapshot holds claims or a person set a label")
    s.set_defaults(fn=cmd_seed)
    s = cs.add_parser("check", help="re-check locators (automatic labels only)")
    s.add_argument("--id", type=int, nargs="+")
    s.add_argument("--by")
    s.set_defaults(fn=cmd_check)
    s = cs.add_parser("list")
    for o in ("--track", "--paper", "--label", "--status"):
        s.add_argument(o)
    s.add_argument("--json", action="store_true")
    s.add_argument("--limit", type=int)
    s.set_defaults(fn=cmd_list)
    s = cs.add_parser("show")
    s.add_argument("claim_id", type=int)
    s.set_defaults(fn=cmd_show)
    s = cs.add_parser("add")
    s.add_argument("--text", required=True)
    s.add_argument("--paper")
    s.add_argument("--locator")
    s.add_argument("--label", required=True, choices=_cdb.LABELS)
    s.add_argument("--kind", default="result",
                   choices=("result", "method", "limitation", "open_question", "number", "definition"))
    s.add_argument("--by", required=True)
    s.add_argument("--track")
    s.add_argument("--origin")
    s.add_argument("--evidence")
    s.set_defaults(fn=cmd_add)
    s = cs.add_parser("verify")
    s.add_argument("claim_id", type=int)
    s.add_argument("--by", required=True)
    s.add_argument("--evidence", required=True)
    s.add_argument("--locator")
    s.set_defaults(fn=cmd_verify)
    s = cs.add_parser("refute")
    s.add_argument("claim_id", type=int)
    s.add_argument("--by", required=True)
    s.add_argument("--evidence", required=True)
    s.set_defaults(fn=cmd_refute)
    s = cs.add_parser("stats")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_stats)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="kb")
    ap.add_argument("--data-root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    register(sub)
    a = ap.parse_args(argv)
    return a.fn(a)
