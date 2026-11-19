"""The downloaded metadata in the papers table (brief 12.3), and the comparison with brief
section 16.

Sources (written by `harness/bin/nrpic-fetch-arxiv --meta`, read here as data):
  kb-data/meta/arxiv-api/<key>.json   title, authors, abstract, categories, version, licence,
                                      DOI and journal reference as the arXiv API gives them
  kb-data/meta/inspire/<key>.json     the INSPIRE literature record ("record"): control number,
                                      DOIs, publication info, title, authors
What `load` writes into each row of `papers` (inside the writer lock, one transaction):
  title, authors_json, abstract     from the arXiv API (the downloaded data win, brief 12.3);
                                    title_source = 'arxiv-api'. The values the TeX parse had
                                    put there are kept in parse_json.tex_front.
  primary_class, submitted (first version), updated (latest version), license: arXiv API
  doi, journal_ref                  arXiv API, else INSPIRE
  inspire_recid                     INSPIRE control number
  brief_title, brief_authors        the entry of brief section 16
  title_matches_brief               1 when the title agrees after normalisation (class same or
                                    format) and the authors agree (match, or the brief lists
                                    none); 0 otherwise; NULL for a paper not in section 16
  grp, priority                     from the manifest (brief section 17 or arxiv_additions.tsv)
  parse_json.meta                   provenance, latest version, the comparison classes,
                                    similarity of the TeX title and abstract to the metadata
The step is idempotent; it must be repeated after a re-ingest (`kb ingest arxiv` rewrites
title, authors, abstract and parse_json from the TeX).

    python -I -m kbtool.meta_papers load    [--id ID ...] [--out DIR] [--dry-run]
    python -I -m kbtool.meta_papers brief16 [--out DIR]
"""
import argparse
import collections
import contextlib
import json
import os
import re
import sqlite3
import sys

from . import db as _db
from . import meta_brief16 as M16
from . import meta_manifest as MM
from .inventory import id_key
from .lock import writer_lock
from .paths import default_brief, layout
from .pdf_reader import word_similarity

TOOL = "kbtool meta-papers 1"


def _read(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def meta_root(lay):
    return os.path.join(lay.data, "meta")


def load_api(lay, pid):
    d = _read(os.path.join(meta_root(lay), "arxiv-api", id_key(pid) + ".json"))
    if not d or d.get("status") != "ok" or d.get("id") != pid:
        return None
    return d


def load_inspire(lay, pid):
    d = _read(os.path.join(meta_root(lay), "inspire", id_key(pid) + ".json"))
    if not d or d.get("status") != "ok" or not isinstance(d.get("record"), dict):
        return None
    rec = d["record"]
    eps = [e.get("value") for e in rec.get("arxiv_eprints") or [] if isinstance(e, dict)]
    if pid not in eps:
        return None                                    # never trust a record that names another paper
    return d


def pubinfo(rec):
    for p in rec.get("publication_info") or []:
        if p.get("journal_title"):
            parts = [p["journal_title"], str(p.get("journal_volume") or "").strip()]
            s = " ".join(x for x in parts if x)
            if p.get("year"):
                s += f" ({p['year']})"
            art = p.get("artid") or p.get("page_start")
            if art:
                s += f" {art}"
            return s
    return None


def inspire_fields(d):
    rec = d["record"]
    dois = [x.get("value") for x in rec.get("dois") or [] if isinstance(x, dict) and x.get("value")]
    titles = [t.get("title") for t in rec.get("titles") or [] if isinstance(t, dict) and t.get("title")]
    return {"recid": rec.get("control_number"), "doi": dois[0] if dois else None, "journal_ref": pubinfo(rec),
            "title": titles[0] if titles else None,
            "authors": [a.get("full_name") for a in rec.get("authors") or [] if isinstance(a, dict)],
            "texkey": (rec.get("texkeys") or [None])[0], "fetched_utc": d.get("fetched_utc"),
            "document_type": rec.get("document_type")}


def _clean(s):
    return re.sub(r"\s+", " ", s).strip() if isinstance(s, str) else s


def version_num(v):
    m = re.match(r"^v(\d+)$", v or "")
    return int(m.group(1)) if m else None


def section16_index(brief_path=None):
    p = brief_path or default_brief()
    s16 = M16.parse_section16(p)
    return {e["id"]: e for e in s16["entries"]}, s16


def plan_row(row, api, insp, entry, man):
    """New values of one papers row (dict of columns) and its parse_json, from the current
    row (dict), the two metadata records, the section-16 entry and the manifest row."""
    pj = json.loads(row["parse_json"] or "{}") if row["parse_json"] else {}
    if row["title_source"] != "arxiv-api":
        pj["tex_front"] = {"title": row["title"], "authors": json.loads(row["authors_json"] or "[]"),
                           "title_source": row["title_source"]}
    tex = pj.get("tex_front") or {}
    new = {}
    meta = {"loaded_by": TOOL, "loaded_at": _db.utcnow()}
    if api:
        new.update({"title": _clean(api["title"]), "authors_json": json.dumps(api.get("authors") or []),
                    "abstract": _clean(api.get("abstract")), "primary_class": api.get("primary_category"),
                    "submitted": api.get("published"), "updated": api.get("updated"), "license": api.get("license"),
                    "doi": api.get("doi"), "journal_ref": _clean(api.get("journal_ref")), "title_source": "arxiv-api"})
        meta["arxiv_api"] = {"fetched_utc": api.get("fetched_utc"), "batch": api.get("batch"),
                             "latest_version": api.get("version"), "categories": api.get("categories"),
                             "comment": api.get("comment")}
        lv, sv = version_num(api.get("version")), version_num(row["version"])
        meta["version_is_latest"] = (lv == sv) if lv and sv else None
        if tex.get("title"):
            meta["tex_title_vs_metadata"] = M16.compare_title(tex["title"], api["title"])
    if insp:
        f = inspire_fields(insp)
        new["inspire_recid"] = f["recid"]
        if not new.get("doi"):
            new["doi"] = f["doi"]
        if not new.get("journal_ref"):
            new["journal_ref"] = f["journal_ref"]
        meta["inspire"] = {k: f[k] for k in ("recid", "texkey", "fetched_utc", "document_type", "doi", "journal_ref")}
        if api:
            meta["inspire_title_vs_arxiv"] = M16.compare_title(f["title"] or "", api["title"])
    if entry:
        cmp_ = M16.compare_entry(entry, api["title"] if api else None, api.get("authors") if api else None)
        new.update({"brief_title": entry["title"], "brief_authors": entry["authors_raw"],
                    "title_matches_brief": 1 if cmp_["agree"] else 0})
        meta["brief16"] = {"line": entry["line"], "group": entry["group"], "priority": entry["priority"],
                           "title": cmp_["title"], "authors": {k: cmp_["authors"].get(k) for k in
                                                               ("class", "kind", "missing", "n_brief", "n_meta")}}
    else:
        new.update({"brief_title": None, "brief_authors": None, "title_matches_brief": None})
    if man:
        new["grp"], new["priority"] = man["group"], man["priority"]
        meta["manifest"] = {"source": man["source"], **({"requested_by": man.get("requested_by"),
                                                          "decision": man.get("decision")}
                                                         if man["source"] == "addition" else {})}
    pj["meta"] = meta
    new["parse_json"] = json.dumps(pj)
    return new, meta


def abstract_similarity(con, pid, api_abstract):
    r = con.execute("SELECT text FROM chunks WHERE paper_id=? AND kind='abstract' ORDER BY chunk_id LIMIT 1",
                    (pid,)).fetchone()
    if not r or not api_abstract:
        return None
    return round(word_similarity(r[0], api_abstract), 4)


COLS = ["title", "authors_json", "abstract", "primary_class", "submitted", "updated", "license", "doi",
        "journal_ref", "title_source", "inspire_recid", "brief_title", "brief_authors", "title_matches_brief",
        "grp", "priority", "parse_json"]


def load(lay, ids=None, dry_run=False, brief_path=None, manifest_dir=None):
    idx16, s16 = section16_index(brief_path)
    man = {r["id"]: r for r in MM.load_full_manifest(manifest_dir)}
    db = lay.db_work
    rows_out, summary = [], collections.Counter()
    # read and write inside one hold of the writer lock, so that no other writer changes a
    # row (parse_json) between the two
    guard = contextlib.nullcontext() if dry_run else writer_lock(lay, what="meta-papers load")
    with guard:
        con = _db.connect_rw(db) if not dry_run else _db.connect_ro(db)
        con.row_factory = sqlite3.Row
        try:
            _load_rows(lay, con, ids, idx16, man, rows_out, summary, dry_run)
        finally:
            con.close()
    return rows_out, dict(summary), s16


def _load_rows(lay, con, ids, idx16, man, rows_out, summary, dry_run):
    papers = con.execute("SELECT * FROM papers ORDER BY paper_id").fetchall()
    if ids:
        papers = [p for p in papers if p["paper_id"] in set(ids)]
    plans = []
    for row in papers:
        pid = row["paper_id"]
        api, insp = load_api(lay, pid), load_inspire(lay, pid)
        new, meta = plan_row(dict(row), api, insp, idx16.get(pid), man.get(pid))
        sim = abstract_similarity(con, pid, api.get("abstract") if api else None)
        pj = json.loads(new["parse_json"])
        pj["meta"]["abstract_similarity"] = sim
        q = pj.setdefault("quality", {})
        q["abstract_similarity_to_metadata"] = sim
        q.pop("abstract_similarity_note", None)
        new["parse_json"] = json.dumps(pj)
        plans.append((pid, new))
        summary["papers"] += 1
        summary["arxiv_api"] += bool(api)
        summary["inspire"] += bool(insp)
        summary["in_section16"] += pid in idx16
        summary["in_manifest"] += pid in man
        summary["manifest_addition"] += bool(man.get(pid) and man[pid]["source"] == "addition")
        if row["grp"] and man.get(pid) and row["grp"] != man[pid]["group"]:
            summary["group_changed"] += 1
        b16 = meta.get("brief16") or {}
        rows_out.append({
            "id": pid, "grp": new.get("grp", row["grp"]), "priority": new.get("priority", row["priority"]),
            "source_kind": row["source_kind"], "parse_status": row["parse_status"], "version": row["version"],
            "latest_version": (meta.get("arxiv_api") or {}).get("latest_version"),
            "version_is_latest": meta.get("version_is_latest"), "primary_class": new.get("primary_class"),
            "inspire_recid": new.get("inspire_recid"), "has_doi": bool(new.get("doi")),
            "has_journal_ref": bool(new.get("journal_ref")), "license": new.get("license"),
            "tex_title_class": (meta.get("tex_title_vs_metadata") or {}).get("class"),
            "tex_title_ratio": (meta.get("tex_title_vs_metadata") or {}).get("ratio"),
            "inspire_title_class": (meta.get("inspire_title_vs_arxiv") or {}).get("class"),
            "abstract_similarity": sim, "brief_line": b16.get("line"),
            "brief_title_class": (b16.get("title") or {}).get("class"),
            "brief_authors_class": (b16.get("authors") or {}).get("class"),
            "title_matches_brief": new.get("title_matches_brief"),
            "group_source": (meta.get("manifest") or {}).get("source")})
    if not dry_run:
        con.execute("BEGIN")
        for pid, new in plans:
            cols = [c for c in COLS if c in new]
            con.execute(f"UPDATE papers SET {', '.join(c + '=?' for c in cols)} WHERE paper_id=?",
                        [new[c] for c in cols] + [pid])
        _db.log(con, "meta-load", "papers", "ok", json.dumps(dict(summary)))
        con.commit()


def brief16_report(lay, brief_path=None, manifest_dir=None):
    """Every section-16 entry against the arXiv-API record and the section-17 manifest."""
    idx16, s16 = section16_index(brief_path)
    base = {r["id"]: r for r in MM.load_full_manifest(manifest_dir) if r["source"] == "brief17"}
    rows = []
    for e in s16["entries"]:
        api = load_api(lay, e["id"])
        insp = load_inspire(lay, e["id"])
        c = M16.compare_entry(e, api["title"] if api else None, api.get("authors") if api else None)
        ins_c = None
        if insp:
            f = inspire_fields(insp)
            ins_c = M16.compare_authors(e["authors_raw"], f["authors"])["class"] if f["authors"] else None
        m17 = base.get(e["id"])
        rows.append({"id": e["id"], "line": e["line"], "group16": e["group"],
                     "group17": m17["group"] if m17 else None, "priority16": e["priority"],
                     "priority17": m17["priority"] if m17 else None, "title_class": c["title"]["class"],
                     "title_ratio": c["title"]["ratio"], "authors_kind": c["authors"]["kind"],
                     "authors_class": c["authors"]["class"], "authors_class_inspire": ins_c,
                     "missing": "; ".join(c["authors"].get("missing") or []),
                     "n_brief_authors": c["authors"].get("n_brief"), "n_meta_authors": c["authors"].get("n_meta"),
                     "agree": c["agree"], "brief_title": e["title"], "brief_authors": e["authors_raw"],
                     "meta_title": _clean(api["title"]) if api else None,
                     "meta_authors": api.get("authors") if api else None})
    ids16 = set(idx16)
    return {"rows": rows, "problems": s16["problems"], "groups": s16["groups"],
            "only_in_16": sorted(ids16 - set(base)), "only_in_17": sorted(set(base) - ids16),
            "first_line": s16["first_line"], "last_line": s16["last_line"], "brief_sha256": s16["brief_sha256"]}


def write_tsv(path, rows, cols):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join("" if r.get(c) is None else str(r.get(c)).replace("\t", " ") for c in cols) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m kbtool.meta_papers")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("load", help="read meta/arxiv-api and meta/inspire into the papers table")
    p.add_argument("--id", action="append")
    p.add_argument("--out", help="directory for papers_meta.tsv and summary.json")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("brief16", help="compare brief section 16 with the arXiv-API records")
    p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    lay = layout()
    out = a.out or os.environ.get("NRPIC_RUN_DIR")
    if out:
        os.makedirs(out, exist_ok=True)
    if a.cmd == "load":
        rows, summary, s16 = load(lay, ids=a.id, dry_run=a.dry_run)
        print(json.dumps(summary, indent=1))
        if out:
            cols = list(rows[0].keys()) if rows else []
            write_tsv(os.path.join(out, "papers_meta.tsv"), rows, cols)
            with open(os.path.join(out, "load_summary.json"), "w") as f:
                json.dump({"summary": summary, "dry_run": a.dry_run, "tool": TOOL}, f, indent=1)
        return 0
    rep = brief16_report(lay)
    cols = ["id", "line", "group16", "group17", "priority16", "priority17", "title_class", "title_ratio",
            "authors_kind", "authors_class", "authors_class_inspire", "missing", "n_brief_authors", "n_meta_authors",
            "agree"]
    write_tsv(os.path.join(out, "brief16_comparison.tsv"), rep["rows"], cols)
    with open(os.path.join(out, "brief16_full.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, ensure_ascii=False)
    cnt = {"entries": len(rep["rows"]), "problems": rep["problems"], "only_in_16": rep["only_in_16"],
           "only_in_17": rep["only_in_17"],
           "title_class": dict(collections.Counter(r["title_class"] for r in rep["rows"])),
           "authors_class": dict(collections.Counter(r["authors_class"] for r in rep["rows"])),
           "group_differs": [r["id"] for r in rep["rows"] if r["group16"] != r["group17"]],
           "priority_differs": [r["id"] for r in rep["rows"] if r["priority16"] != r["priority17"]],
           "agree": sum(1 for r in rep["rows"] if r["agree"])}
    with open(os.path.join(out, "brief16_summary.json"), "w") as f:
        json.dump(cnt, f, indent=1)
    print(json.dumps(cnt, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
