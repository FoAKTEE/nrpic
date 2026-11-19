"""K7: paper-code links (brief 12.7, table impl_links of 12.2).

Two kinds:
  curated   kb/curated/paper_code_links.tsv: a statement of a paper's method (paper id,
            line range of the stored TeX source, equation label if any, a short description
            in our own words, never paper text) and the function of an indexed repository
            that implements it (repo, qualified name, path), with the run parameters that
            switch it, the evidence and the tests named for it. Each link starts as
            `claimed`; `verified` needs a test attached by the owner who ran it.
  explicit  repository addresses (github.com/<owner>/<repo>) that occur in the stored paper
            sources, matched against the repository manifest.

`kb link check` re-derives every curated link from the data: the line range exists in the
stored source and contains the label; the symbol is in the code index at that path (its
line range is reported); each named parameter is read by the code with that block and
name. `kb link load` writes the links into impl_links (symbol ids re-resolved, so a new
`kb ingest repo` only needs a new `kb link load`).
"""
import csv
import glob
import json
import os
import re
import time

from .db import connect_ro, connect_rw, log as db_log, open_for_read
from .lock import writer_lock
from .paths import KB_DIR

CURATED = os.path.join(KB_DIR, "curated", "paper_code_links.tsv")
COLUMNS = ["link_key", "paper_id", "lines", "eq_label", "statement", "repo_id", "symbol", "path", "params",
           "relation", "status", "evidence", "tests"]
GITHUB_RE = re.compile(rb"github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)")


def read_curated(path=None):
    rows = []
    with open(path or CURATED, newline="") as f:
        for r in csv.DictReader((ln for ln in f if not ln.startswith("#")), delimiter="\t"):
            rows.append({k: (r.get(k) or "").strip() for k in COLUMNS})
    return rows


def paper_source(lay, paper_id):
    """(path of the main TeX file of the newest stored version, version) or (None, None)."""
    base = os.path.join(lay.raw_arxiv, paper_id.replace("/", "_"))
    vers = sorted((d for d in os.listdir(base) if re.match(r"^v\d+$", d)), key=lambda v: int(v[1:])) \
        if os.path.isdir(base) else []
    for v in reversed(vers):
        src = os.path.join(base, v, "src")
        cands = [p for p in glob.glob(os.path.join(src, "*.tex")) if os.path.isfile(p) and not os.path.islink(p)]
        for p in sorted(cands, key=lambda p: (os.path.basename(p) != "main.tex", p)):
            head = open(p, "rb").read(1 << 20)
            if b"\\documentclass" in head and b"\\begin{document}" in head:
                return p, v
    return None, None


def parse_lines(spec):
    """'L410-417,L445' -> [(410, 417), (445, 445)]."""
    out = []
    for part in spec.replace(" ", "").split(","):
        m = re.match(r"^L?(\d+)(?:-L?(\d+))?$", part)
        if m:
            a = int(m.group(1))
            out.append((a, int(m.group(2) or a)))
    return out


def find_symbol(con, repo_id, qualname, path):
    rows = con.execute("SELECT s.sym_id, s.qualname, s.kind, s.line_start, s.line_end, f.path FROM symbols s "
                       "JOIN code_files f USING(file_id) WHERE f.repo_id = ? AND (s.qualname = ? OR "
                       "s.qualname LIKE '%::' || ? OR s.name = ?) AND s.kind != 'prototype' "
                       "ORDER BY (f.path = ?) DESC, (s.qualname = ?) DESC, s.line_start",
                       (repo_id, qualname, qualname, qualname, path, qualname)).fetchall()
    if path:
        rows = [r for r in rows if r[5] == path] or rows
    return rows


def find_param(con, repo_id, spec):
    """spec '<block> name' -> rows (block, name, type, default, path, line)."""
    m = re.match(r"^<([^>]+)>\s*(\S+)$", spec.strip())
    if not m:
        return None
    return con.execute("SELECT p.block, p.name, p.type, p.default_value, f.path, p.line FROM params p "
                       "JOIN code_files f USING(file_id) WHERE p.repo_id = ? AND p.block = ? AND p.name = ? "
                       "ORDER BY f.path, p.line", (repo_id, m.group(1), m.group(2))).fetchall()


def check_links(lay, path=None, db=None):
    rows = read_curated(path)
    dbp = open_for_read(lay, db)
    con = connect_ro(dbp)
    out = {"database": os.path.realpath(dbp), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "links": [], "n_bad": 0}
    srcs = {}
    try:
        for r in rows:
            res = {"link_key": r["link_key"], "problems": [], "row": r}
            pid = r["paper_id"]
            if pid not in srcs:
                srcs[pid] = paper_source(lay, pid)
            sp, ver = srcs[pid]
            res["paper_source"] = os.path.relpath(sp, lay.data) if sp else None
            if not sp:
                res["problems"].append("paper source not in the store")
            else:
                text = open(sp, encoding="utf-8", errors="replace").read().splitlines()
                spans = parse_lines(r["lines"])
                if not spans:
                    res["problems"].append(f"unreadable line range {r['lines']!r}")
                for a, b in spans:
                    if not (1 <= a <= b <= len(text)):
                        res["problems"].append(f"lines {a}-{b} outside the source ({len(text)} lines)")
                labels = [x for x in r["eq_label"].split(",") if x and x != "-"]
                for lab in labels:
                    hit = [i for i, ln in enumerate(text, 1) if "\\label{" + lab + "}" in ln]
                    if not hit:
                        res["problems"].append(f"label {lab} not in the source")
                    elif not any(a - 3 <= h <= b + 3 for h in hit for a, b in spans):
                        res["problems"].append(f"label {lab} at line {hit[0]}, outside {r['lines']}")
                    res.setdefault("label_lines", {})[lab] = hit
            sym = find_symbol(con, r["repo_id"], r["symbol"], r["path"])
            if not sym:
                res["problems"].append(f"symbol {r['symbol']} not in the index of {r['repo_id']}")
            else:
                s = sym[0]
                res["symbol"] = {"sym_id": s[0], "qualname": s[1], "kind": s[2], "line_start": s[3],
                                 "line_end": s[4], "path": s[5], "candidates": len(sym)}
                if r["path"] and s[5] != r["path"]:
                    res["problems"].append(f"symbol found in {s[5]}, not in {r['path']}")
            res["params"] = []
            for spec in [x for x in r["params"].split(";") if x.strip() and x.strip() != "-"]:
                pr = find_param(con, r["repo_id"], spec)
                if pr is None:
                    res["problems"].append(f"unreadable parameter {spec!r}")
                elif not pr:
                    res["problems"].append(f"parameter {spec.strip()} not read by {r['repo_id']}")
                else:
                    res["params"].append({"param": spec.strip(), "type": pr[0][2], "default": pr[0][3],
                                          "read_at": [f"{x[4]}:{x[5]}" for x in pr]})
            if r["status"] not in ("claimed", "verified", "refuted"):
                res["problems"].append(f"status {r['status']!r}")
            out["n_bad"] += bool(res["problems"])
            out["links"].append(res)
    finally:
        con.close()
    return out


def format_check(rep):
    L = [f"kb link check: {len(rep['links'])} links, {rep['n_bad']} with problems (database {rep['database']})"]
    for x in rep["links"]:
        s = x.get("symbol") or {}
        L.append(f"{x['link_key']:5s} {'OK ' if not x['problems'] else 'BAD'} {x['row']['paper_id']} {x['row']['lines']:<14s} "
                 f"-> {x['row']['repo_id']} {s.get('qualname', x['row']['symbol'])} "
                 f"{s.get('path', '')}:{s.get('line_start', '')}-{s.get('line_end', '')}")
        for p in x["problems"]:
            L.append(f"      problem: {p}")
    return "\n".join(L) + "\n"


def eq_id_for(con, paper_id, label):
    try:
        r = con.execute("SELECT eq_id FROM equations WHERE paper_id = ? AND label = ?", (paper_id, label)).fetchone()
        return r[0] if r else None
    except Exception:
        return None


def load_curated(lay, path=None):
    """Replace the curated links of owner kb in impl_links (inside the writer lock)."""
    rep = check_links(lay, path, db=lay.db_work)
    n = 0
    with writer_lock(lay, what="link load"):
        con = connect_rw(lay.db_work)
        try:
            con.execute("BEGIN")
            con.execute("DELETE FROM impl_links WHERE by_owner = 'kb' AND evidence LIKE '{\"source\": \"curated%'")
            for x in rep["links"]:
                r = x["row"]
                labels = [v for v in r["eq_label"].split(",") if v and v != "-"]
                ev = {"source": "curated " + os.path.relpath(path or CURATED, KB_DIR), "link_key": r["link_key"],
                      "lines": r["lines"], "eq_label": labels, "statement": r["statement"], "symbol": r["symbol"],
                      "path": r["path"], "params": x["params"], "evidence": r["evidence"], "tests": r["tests"],
                      "check_problems": x["problems"], "paper_source": x.get("paper_source"),
                      "symbol_lines": [x.get("symbol", {}).get("line_start"), x.get("symbol", {}).get("line_end")]}
                con.execute("INSERT INTO impl_links(paper_id, eq_id, repo_id, sym_id, relation, status, evidence, "
                            "by_owner, at) VALUES (?,?,?,?,?,?,?,?,?)",
                            (r["paper_id"], eq_id_for(con, r["paper_id"], labels[0]) if labels else None,
                             r["repo_id"], (x.get("symbol") or {}).get("sym_id"), r["relation"], r["status"],
                             json.dumps(ev, sort_keys=False), "kb", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
                n += 1
            db_log(con, "link-load", path or CURATED, "ok", json.dumps({"links": n, "with_problems": rep["n_bad"]}))
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    return n


def add_link(lay, paper, eq, repo, symbol, relation, status, evidence, by_owner):
    with writer_lock(lay, what="link add"):
        con = connect_rw(lay.db_work)
        try:
            sym = find_symbol(con, repo, symbol, None)
            ev = {"source": "kb link add", "symbol": symbol, "evidence": evidence, "eq_label": eq}
            cur = con.execute("INSERT INTO impl_links(paper_id, eq_id, repo_id, sym_id, relation, status, evidence, "
                              "by_owner, at) VALUES (?,?,?,?,?,?,?,?,?)",
                              (paper, eq_id_for(con, paper, eq) if eq else None, repo, sym[0][0] if sym else None,
                               relation, status, json.dumps(ev), by_owner,
                               time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()


def list_links(lay, paper=None, db=None):
    con = connect_ro(open_for_read(lay, db))
    try:
        q = ("SELECT l.link_id, l.paper_id, json_extract(l.evidence, '$.lines'), l.repo_id, "
             "COALESCE(s.qualname, json_extract(l.evidence, '$.symbol')), f.path, s.line_start, l.relation, l.status, "
             "json_extract(l.evidence, '$.statement') FROM impl_links l LEFT JOIN symbols s ON s.sym_id = l.sym_id "
             "LEFT JOIN code_files f ON f.file_id = s.file_id")
        args = ()
        if paper:
            q += " WHERE l.paper_id = ?"
            args = (paper,)
        return con.execute(q + " ORDER BY l.link_id", args).fetchall()
    finally:
        con.close()


def explicit_links(lay, repos):
    """Repository addresses in the stored paper sources: [(paper_id, version, file, line, owner/repo, in_manifest)].
    Files are read as bytes (.tex, .bbl, .bib, .txt); nothing is run."""
    want = {r.lower(): r for r in repos}
    out = []
    for vdir in sorted(glob.glob(os.path.join(lay.raw_arxiv, "*", "v*", "src"))):
        key = vdir.split(os.sep)[-3]
        ver = vdir.split(os.sep)[-2]
        pid = re.sub(r"^([a-z\-]+(?:\.[A-Z]{2})?)_(\d{7})$", r"\1/\2", key)
        for root, dirs, files in os.walk(vdir, followlinks=False):
            for fn in files:
                if not fn.lower().endswith((".tex", ".bbl", ".bib", ".txt")):
                    continue
                p = os.path.join(root, fn)
                if os.path.islink(p) or os.path.getsize(p) > 16 << 20:
                    continue
                data = open(p, "rb").read()
                for m in GITHUB_RE.finditer(data):
                    owner = m.group(1).decode()
                    name = re.sub(r"(\.git|[.\-_}]+)$", "", m.group(2).decode())
                    rid = f"{owner}/{name}"
                    line = data.count(b"\n", 0, m.start()) + 1
                    out.append((pid, ver, os.path.relpath(p, vdir), line, rid, want.get(rid.lower())))
    return out
