"""`kb claim ...` (brief 12.8, 12.10): the evidence queue.

    kb claim seed [--source TRACK ...] [--dry-run] [--tsv PATH]   notes of wave 1 -> claims, checked
    kb claim check [--id N ...]           re-run the locator and number check (auto labels only)
    kb claim list [--track T] [--paper ID] [--label L] [--status S] [--json] [--limit N]
    kb claim show N                       one claim: locators, check detail, history
    kb claim add --text T --paper ID [--locator L] --label L --by WHO [--kind K] [--track T]
    kb claim verify N --by WHO --evidence TEXT [--locator L]     a person read the passage
    kb claim refute N --by WHO --evidence TEXT                   prints the tracks to notify
    kb claim stats [--json]
    kb claim seed-brief [--dry-run] [--tsv PATH] [--join PKG ...] [--annotate TSV] [--defects] [--recheck]
                                          the brief's labelled statements (12.8); kbtool/claims_brief.py

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
        r["links"] = _cdb.links(con, a.claim_id)
        sup = [l["to_id"] for l in r["links"] if l["relation"] == _cdb.SUPERSEDED_BY and l["from_id"] == a.claim_id]
        if sup:
            r["superseded_by"] = sup
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

    def fn(con):
        _cdb.verify(con, a.claim_id, a.by, a.evidence, a.locator)
        if a.locator:                       # the locator rows follow the new string (wave-2b defect: claim 25)
            return _cdb.relocate(con, a.claim_id, a.locator, _store(lay, con), a.by, "verify")
        return None
    try:
        n = _write(lay, "claim verify", fn)
    except (ValueError, KeyError) as e:
        print(f"claim {a.claim_id}: {e}", file=sys.stderr)
        return 1
    print(f"claim {a.claim_id}: fulltext, checked by {a.by}" + (f"; locator rows {n[0]}, resolved {n[1]}" if n else ""))
    return 0


def cmd_relocate(a):
    """Rewrite the locator rows of a claim from a locator string (labels and statuses stay)."""
    lay = layout(a.data_root)
    try:
        n, ok = _write(lay, "claim relocate",
                       lambda con: _cdb.relocate(con, a.claim_id, a.locator, _store(lay, con), a.by, a.evidence or ""))
    except (ValueError, KeyError) as e:
        print(f"claim {a.claim_id}: {e}", file=sys.stderr)
        return 1
    print(f"claim {a.claim_id}: {n} locator rows, {ok} resolved")
    return 0 if ok == n else 1


def cmd_refute(a):
    lay = layout(a.data_root)
    try:
        tracks = _write(lay, "claim refute", lambda con: _cdb.refute(con, a.claim_id, a.by, a.evidence))
    except KeyError as e:
        print(f"no claim {e}", file=sys.stderr)
        return 1
    print(f"claim {a.claim_id}: refuted by {a.by}; notify: {', '.join(tracks) or 'nobody recorded'}")
    return 0


def cmd_supersede(a):
    """Close a claim whose text is wrong (or holds no statement) with a pointer to the claim that
    replaces it: a new claim (--text) or an existing one (--to). claims_db.supersede."""
    lay = layout(a.data_root)

    def fn(con):
        new = _cdb.supersede(con, a.claim_id, a.by, a.evidence, text=a.text, to=a.to, label=a.label,
                             kind=a.kind, paper_id=a.paper, locator=a.locator, track=a.track, origin=a.origin,
                             store=_store(lay, con) if a.locator else None, allow_unresolved=a.allow_unresolved)
        n = con.execute("SELECT count(*), coalesce(sum(resolved), 0) FROM claim_locators WHERE claim_id=?",
                        (new,)).fetchone()
        return new, n
    try:
        new, (n, ok) = _write(lay, "claim supersede", fn)
    except (ValueError, KeyError) as e:
        print(f"claim {a.claim_id}: {e}", file=sys.stderr)
        return 1
    print(f"claim {a.claim_id} superseded by claim {new} ({'existing' if a.to else 'new'}); "
          f"locator rows {n}, resolved {ok}")
    return 0


def cmd_withdraw(a):
    """Close a claim that holds no statement and that nothing replaces (claims_db.withdraw)."""
    lay = layout(a.data_root)
    try:
        _write(lay, "claim withdraw", lambda con: _cdb.withdraw(con, a.claim_id, a.by, a.evidence))
    except (ValueError, KeyError) as e:
        print(f"claim {a.claim_id}: {e}", file=sys.stderr)
        return 1
    print(f"claim {a.claim_id}: withdrawn by {a.by}")
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


def cmd_seed_brief(a):
    """`kb claim seed-brief`: the labelled statements of the brief's main text as seeds (brief
    12.8; kbtool/claims_brief.py), and the helpers of package tracks/kb/claims_brief:
    --join (CHECK.md rows of the brief check against the seeds, read only), --annotate FILE
    (outcomes that change no label), --defects (defects of cited papers), --recheck (their
    locators again)."""
    from . import claims_brief as _cb
    from .paths import default_brief
    lay = layout(a.data_root)
    by = a.by or _cb.BY_DEFAULT
    path = a.brief or default_brief()
    if not path or not os.path.exists(path):
        print("brief not found; pass --brief", file=sys.stderr)
        return 2
    dbp = _db_path(lay, a)
    if a.annotate:
        rows = [ln.rstrip("\n").split("\t") for ln in open(a.annotate) if ln.strip() and not ln.startswith("#")]
        n = collections.Counter()
        for r in rows:
            cid, evidence = int(r[0]), r[1]
            status = r[2] if len(r) > 2 and r[2] else None
            n["written" if _write(lay, "claim seed-brief annotate",
                                  lambda con: _cb.annotate(con, cid, by, evidence, status)) else "same"] += 1
        print("annotated: " + ", ".join(f"{k} {v}" for k, v in sorted(n.items())))
        return 0
    if a.defects or a.recheck:
        if a.dry_run:
            for d in _cb.defect_rows():
                print(f"{d.key}\t{d.paper_id}\t{d.row}\trefute={d.refute}\tright={'yes' if d.right else 'no'}")
            print(f"# {len(_cb.defect_rows())} defects")
            return 0

        def fn(con):
            st = _store(lay, con)
            if a.recheck:
                return _cb.recheck_defects(con, st, by)
            return [(d.key, _cb.add_defect(con, d, st, by)) for d in _cb.defect_rows()]
        out = _write(lay, "claim seed-brief defects", fn)
        if a.recheck:
            for cid, key, status, ok, probs in out:
                print(f"{cid}\t{key}\t{status}\t{'resolved' if ok else 'unresolved'}\t{'; '.join(probs)}")
            print(f"# {len(out)} defect claims with locators, {sum(1 for x in out if not x[3])} unresolved")
            return 0
        cnt = collections.Counter()
        for key, res in out:
            for part, v in res.items():
                if v:
                    cnt[v[1]] += 1
                    print(f"{key}\t{part}\tclaim {v[0]}\t{v[1]}")
        print("defects: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
        return 0
    con = _cdb.connect(dbp, ro=True) if os.path.exists(dbp) else None
    try:
        statements, info = _cb.extract(path)
        _cb.assign_tracks(statements, _cb.track_usage(con), _cb.sheet_ids(path))
        if a.join:
            rows, problems = [], []
            for pkg in a.join:
                if a.check_dir:
                    md = open(os.path.join(a.check_dir, pkg, "CHECK.md"), encoding="utf-8").read()
                else:
                    md, commit = read_note(_cp.SourceSpec("kb", a.check_ref, f"tracks/kb/brief_check/{pkg}/CHECK.md"))
                    print(f"{pkg}: CHECK.md at {a.check_ref} {commit[:10]}")
                r, p = _cb.parse_check(md, pkg)
                rows += r
                problems += p
            seeds = {}
            if con is not None and _cdb.has_tables(con):
                seeds = dict(con.execute("SELECT seed_key, claim_id FROM claim_meta WHERE seed_key LIKE ?",
                                         (_cb.SEED_PREFIX + "%",)).fetchall())
            out = _cb.join_rows(rows, statements)
            cols = ("package", "n", "brief_line", "label_col", "row_label", "verdict", "seed_key", "claim_id",
                    "seed_label", "how", "overlap", "tex_locators")
            lines = ["\t".join(cols)]
            for r, s, how, sc in out:
                lines.append("\t".join(str(x) for x in (
                    r.package, r.n, r.brief_line, r.label_col, r.label, r.verdict, s.seed_key() if s else "",
                    seeds.get(s.seed_key(), "") if s else "", s.label if s else "", how, f"{sc:.2f}",
                    "; ".join(f"{p}{v}:{f}:L{x}-{y}" for p, v, f, x, y in r.tex_locators()))))
            if a.tsv:
                os.makedirs(os.path.dirname(os.path.abspath(a.tsv)), exist_ok=True)
                open(a.tsv, "w").write("\n".join(lines) + "\n")
            c = collections.Counter(how for _, _, how, _ in out)
            print(f"rows {len(rows)} (problems {len(problems)}): " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
            for p in problems:
                print("problem: " + p, file=sys.stderr)
            return 0
        rows = _cb.seed_rows(statements)
        if a.dry_run:
            if a.tsv:
                write_rows(a.tsv, rows)
            _brief_summary(statements, info)
            return 0
    finally:
        if con is not None:
            con.close()
    with writer_lock(lay, what="claims seed-brief"):
        con = _cdb.connect(lay.db_work)
        try:
            _cdb.ensure(con)
            con.execute("BEGIN")
            counts = collections.Counter()
            for s in statements:
                cid, what = _cb.upsert(con, s, info["brief_sha256"], by)
                counts[what] += 1
                for r in rows:
                    if r["seed_key"] == s.seed_key():
                        r["claim_id"] = cid
            con.execute("INSERT INTO ingest_log(at, step, target, status, message, tool_version) VALUES (?,?,?,?,?,?)",
                        (_cdb.utcnow(), "claims-seed-brief", os.path.basename(path), "ok", json.dumps(dict(counts)),
                         TOOL))
            con.commit()
        finally:
            con.close()
    print("seeded from the brief: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if a.tsv:
        write_rows(a.tsv, rows)
    _brief_summary(statements, info)
    return 0


def write_rows(path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    cols = list(rows[0].keys()) if rows else []
    if rows and "claim_id" not in cols:
        cols = ["claim_id"] + cols
    with open(path, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")


def _brief_summary(statements, info):
    by_sec = collections.defaultdict(collections.Counter)
    for s in statements:
        by_sec[s.section][s.label] += 1
    for sec in sorted(by_sec):
        print(f"section {sec:2d}: " + " ".join(f"{k}={v}" for k, v in sorted(by_sec[sec].items())))
    lab = collections.Counter(s.label for s in statements)
    print(f"main text {len(statements)} statements: " + ", ".join(f"{k} {v}" for k, v in sorted(lab.items())) +
          f" | all labels by section {dict(sorted((str(k), v) for k, v in info['labels_by_section'].items()))}")


def register(sub):
    p = sub.add_parser("claim", help="K8: evidence queue (seed, check, list, show, add, verify, relocate, refute, supersede, withdraw, stats)")
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
    s = cs.add_parser("seed-brief", help="the labelled statements of the brief's main text as seeds (brief 12.8)")
    s.add_argument("--brief", help="the brief (default: the checkout's copy)")
    s.add_argument("--dry-run", action="store_true", help="extract and print counts, write nothing")
    s.add_argument("--tsv", help="write a table of the seeds (or of --join) here")
    s.add_argument("--by")
    s.add_argument("--join", nargs="+", metavar="PACKAGE",
                   help="read only: join the CHECK.md rows of these brief-check packages to the seeds")
    s.add_argument("--check-ref", default="kb/brief-check", help="git ref of the brief-check packages")
    s.add_argument("--check-dir", help="read <dir>/<package>/CHECK.md instead of the git ref (tests)")
    s.add_argument("--annotate", metavar="TSV", help="claim_id TAB evidence [TAB status]: outcomes without a label change")
    s.add_argument("--defects", action="store_true", help="enter the defects of cited papers (claims_brief.DEFECTS)")
    s.add_argument("--recheck", action="store_true", help="resolve the locators of the defect claims again")
    s.set_defaults(fn=cmd_seed_brief)
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
    s = cs.add_parser("relocate", help="rewrite the locator rows of a claim from a locator string")
    s.add_argument("claim_id", type=int)
    s.add_argument("--locator", required=True, help="'<id><vN>:<file>:L<a>[-<b>]; ...'")
    s.add_argument("--by", required=True)
    s.add_argument("--evidence")
    s.set_defaults(fn=cmd_relocate)
    s = cs.add_parser("refute")
    s.add_argument("claim_id", type=int)
    s.add_argument("--by", required=True)
    s.add_argument("--evidence", required=True)
    s.set_defaults(fn=cmd_refute)
    s = cs.add_parser("supersede", help="close a claim whose text is wrong with a pointer to the claim that "
                                         "replaces it (new: --text; existing: --to); old -> refuted/superseded")
    s.add_argument("claim_id", type=int)
    s.add_argument("--by", required=True)
    s.add_argument("--evidence", required=True, help="what is wrong with the old text, with locators")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="text of the new claim")
    g.add_argument("--to", type=int, help="an existing claim that already carries the statement")
    s.add_argument("--label", default="fulltext", choices=[l for l in _cdb.LABELS if l != "refuted"])
    s.add_argument("--kind", help="default: the old claim's kind")
    s.add_argument("--paper", help="default: the old claim's paper")
    s.add_argument("--locator", help="'<id><vN>:<file>:L<a>[-<b>]; ...' (rows written at once)")
    s.add_argument("--track", help="default: the old claim's track")
    s.add_argument("--origin")
    s.add_argument("--allow-unresolved", action="store_true", help="write a locator part that does not resolve")
    s.set_defaults(fn=cmd_supersede)

    s = cs.add_parser("withdraw", help="close a claim that holds no statement (a heading or a locator split "
                                        "from a note row) and that no claim replaces; -> refuted/withdrawn")
    s.add_argument("claim_id", type=int)
    s.add_argument("--by", required=True)
    s.add_argument("--evidence", required=True)
    s.set_defaults(fn=cmd_withdraw)

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
