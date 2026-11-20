"""Step 4 of the KB-G2 verifier: an independent scan of the parse of every paper.

For each paper of the snapshot this counts, with the verifier's own regular expressions,
in build/tex/<id_>/flat.tex (checked against papers.flat_sha256 of the snapshot):
  sections (chapter/section/subsection/subsubsection commands), display equations
  (equation, align, eqnarray, gather, multline, flalign, alignat, displaymath, dmath
  environments, \\[ \\], $$ pairs, and uses of shorthand macros whose definition opens one
  of these environments), \\cite commands and distinct cited keys, \\bibitem entries, and
  the abstract environment;
and in the raw source directory (read as text only): \\bibitem/\\entry rows of .bbl files
and @-entries of the .bib files named by \\bibliography{...}.
It reads the database counts (sections, equations, bib_entries, citations, chunks) and
compares the abstract chunk with papers.abstract (recall of the metadata words).

Definition of "parsed successfully" (the verifier's, for the four kinds of question of
brief 12.1):
  S  sections: the database has >= 1 section, or the source has no sectioning command and
     the text is chunked (>= 1 body chunk);
  E  equations: if the source has display equations, the database has >= 1 equation and at
     least half as many as the verifier counts; PDF-only papers: not applicable (pass);
  B  bibliography: if the paper cites (>= 1 \\cite outside the bibliography), the source has a
     bibliography (.bbl rows, else .bib entries named by \\bibliography, else \\bibitem in
     flat.tex) and the database has >= 1 entry, at least half as many entries as the
     verifier counts in that source, and >= 1 citation row;
  A  abstract: an abstract chunk exists and, when the metadata has an abstract, at least
     half of the metadata's words (>= 3 letters) occur in it.
  success = S and E and B and A. Lenient variant: A' = A or an abstract in papers.abstract.
Writes scan.json and scan.tsv into $NRPIC_RUN_DIR and prints the rates.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402
import locmap as L  # noqa: E402

ENVS = r"(?:equation|align|eqnarray|gather|multline|flalign|alignat|displaymath|dmath|dgroup|IEEEeqnarray)"
RE_SEC = re.compile(r"\\(chapter|section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\])?\s*\{")
RE_ENV = re.compile(r"\\begin\s*\{" + ENVS + r"\*?\}")
RE_DISP = re.compile(r"(?<!\\)\\\[")
RE_DD = re.compile(r"(?<!\\)\$\$")
RE_CITE = re.compile(r"\\(?:[A-Za-z]*cite[a-zA-Z]*|citen|cite)\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}")
RE_BIBITEM = re.compile(r"\\bibitem\b")
RE_ENTRY = re.compile(r"\\entry\s*\{")
RE_BIBREF = re.compile(r"\\(?:bibliography|addbibresource|addglobalbib)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")
RE_BIBENT = re.compile(r"@(?!string\b|comment\b|preamble\b)[A-Za-z]+\s*[{(]\s*([^,\s]+)\s*,", re.I)
RE_THEBIB = re.compile(r"\\begin\s*\{thebibliography\}.*?(?:\\end\s*\{thebibliography\}|$)", re.S)
RE_ABS = re.compile(r"\\begin\s*\{abstract\}(.*?)\\end\s*\{abstract\}", re.S)
RE_ABS2 = re.compile(r"\\abstract\s*\{")
RE_DEF = re.compile(r"\\(?:re)?newcommand\*?\s*\{?\s*(\\[A-Za-z]+)\s*\}?\s*(?:\[\d\])?\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"
                    r"|\\def\s*(\\[A-Za-z]+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
WORD = re.compile(r"[a-z]{3,}")


def shorthand_eq_macros(flat):
    names = set()
    for m in RE_DEF.finditer(flat):
        name, body = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        if body and re.search(r"\\begin\s*\{" + ENVS + r"\*?\}", body):
            names.add(name)
    return names


def count_flat(flat):
    d = {}
    d["sec"] = len(RE_SEC.findall(flat))
    env = len(RE_ENV.findall(flat))
    disp = len(RE_DISP.findall(flat))
    dd = len(RE_DD.findall(flat)) // 2
    sh = 0
    names = shorthand_eq_macros(flat)
    # uses outside the definitions: count the name followed by a non-letter
    for n in names:
        sh += max(0, len(re.findall(re.escape(n) + r"(?![A-Za-z])", flat)) - len(re.findall(r"(?:newcommand\*?\s*\{?\s*|\\def\s*)" + re.escape(n) + r"(?![A-Za-z])", flat)))
    d["eq_env"], d["eq_disp"], d["eq_dd"], d["eq_short"] = env, disp, dd, sh
    d["eq"] = env + disp + dd + sh
    keys = []
    ncmd = 0
    body = RE_THEBIB.sub(" ", flat)          # cites inside the bibliography itself are not citations
    for m in RE_CITE.finditer(body):
        ncmd += 1
        keys.extend(k.strip() for k in m.group(1).split(",") if k.strip())
    d["cite_cmds"] = ncmd
    d["cite_keys"] = len(set(keys))
    d["cite_keyset"] = set(keys)
    d["bibitem_flat"] = len(RE_BIBITEM.findall(flat))
    m = RE_ABS.search(flat)
    d["abstract_env"] = bool(m) or bool(RE_ABS2.search(flat))
    d["abstract_env_len"] = len(m.group(1)) if m else 0
    d["bib_refs"] = [x.strip() for m in RE_BIBREF.finditer(flat) for x in m.group(1).split(",") if x.strip()]
    return d


def count_src(pid, version, bib_refs, cited, main_tex):
    """bbl: rows of the .bbl named like the main file (else the largest one); bib: entries of the
    named .bib files (found by basename anywhere in the source tree) that the paper cites (all of
    them under \\nocite{*})."""
    src = os.path.join(C.RAW_ARXIV, C.id_dir(pid), version or "", "src")
    out = dict(bbl_files=0, bbl_items=0, bib_files=0, bib_entries=0, bib_cited=0, src_exists=os.path.isdir(src))
    if not out["src_exists"]:
        return out
    stem = os.path.splitext(os.path.basename(main_tex or ""))[0]
    best = None
    for p in glob.glob(os.path.join(src, "**", "*.bbl"), recursive=True):
        if os.path.islink(p) or not os.path.isfile(p):
            continue
        t = C.read_text(p, limit=32 << 20)
        out["bbl_files"] += 1
        n = len(RE_BIBITEM.findall(t)) + len(RE_ENTRY.findall(t))
        key = (os.path.splitext(os.path.basename(p))[0] == stem, n)
        if best is None or key > best:
            best = key
    out["bbl_items"] = best[1] if best else 0
    allbib = {}
    for p in glob.glob(os.path.join(src, "**", "*.bib"), recursive=True):
        if os.path.isfile(p) and not os.path.islink(p):
            allbib.setdefault(os.path.basename(p), p)
    keys = set()
    for r in bib_refs:
        b = os.path.basename(r)
        p = allbib.get(b) or allbib.get(b + ".bib")
        if p:
            t = C.read_text(p, limit=64 << 20)
            out["bib_files"] += 1
            ks = [k.strip() for k in RE_BIBENT.findall(t)]
            out["bib_entries"] += len(ks)
            keys.update(ks)
    out["bib_cited"] = len(keys) if "*" in cited else len(keys & cited)
    return out


def words(s):
    return set(WORD.findall((s or "").lower()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=C.SNAP)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    con = C.open_ro(a.db)
    papers = con.execute("select paper_id, version, parse_status, source_kind, flat_sha256, abstract, grp, priority, main_tex "
                         "from papers order by paper_id").fetchall()
    if a.limit:
        papers = papers[:a.limit]

    def cnt(sql):
        return collections.Counter(dict(con.execute(sql).fetchall()))
    db_sec = cnt("select paper_id, count(*) from sections group by 1")
    db_eq = cnt("select paper_id, count(*) from equations group by 1")
    db_bib = cnt("select paper_id, count(*) from bib_entries group by 1")
    db_cit = cnt("select citing, count(*) from citations group by 1")
    db_body = cnt("select paper_id, count(*) from chunks where kind in ('body','appendix') group by 1")
    abs_chunk = collections.defaultdict(str)
    for pid, t in con.execute("select paper_id, text from chunks where kind='abstract' order by chunk_id"):
        abs_chunk[pid] += " " + (t or "")
    rows = []
    for p in papers:
        pid = p["paper_id"]
        r = dict(paper_id=pid, grp=p["grp"], priority=p["priority"], status=p["parse_status"], kind=p["source_kind"])
        fp = L.flat_path(pid)
        r["flat_exists"] = os.path.exists(fp)
        r["flat_sha_ok"] = r["flat_exists"] and L.sha256_file(fp) == p["flat_sha256"]
        f = count_flat(L.flat_text(pid)) if r["flat_exists"] else count_flat("")
        r.update({f"my_{k}": v for k, v in f.items() if k not in ("bib_refs", "cite_keyset")})
        s = count_src(pid, p["version"], f["bib_refs"], f["cite_keyset"], p["main_tex"])
        r.update({f"src_{k}": v for k, v in s.items()})
        r["my_bib"] = s["bbl_items"] or s["bib_cited"] or f["bibitem_flat"]
        r["my_bib_source"] = "bbl" if s["bbl_items"] else ("bib" if s["bib_cited"] else
                                                          ("bibitem" if f["bibitem_flat"] else None))
        r["db_sec"], r["db_eq"], r["db_bib"], r["db_cit"], r["db_body"] = (db_sec[pid], db_eq[pid], db_bib[pid],
                                                                          db_cit[pid], db_body[pid])
        ach = abs_chunk.get(pid, "")
        r["db_abs_chunk"] = bool(ach.strip())
        meta = p["abstract"] or ""
        r["meta_abs"] = bool(meta.strip())
        wm, wc = words(meta), words(ach)
        r["abs_recall"] = round(len(wm & wc) / len(wm), 3) if wm else None
        pdf = p["source_kind"] == "pdf"
        r["S"] = r["db_sec"] >= 1 or (f["sec"] == 0 and r["db_body"] >= 1)
        r["E"] = pdf or f["eq"] == 0 or (r["db_eq"] >= 1 and r["db_eq"] >= 0.5 * f["eq"])
        if pdf:
            r["B"] = r["db_bib"] >= 1 or r["my_bib"] == 0
            r["B_cause"] = None if r["B"] else "pdf: no entries"
        elif f["cite_cmds"] == 0:
            r["B"], r["B_cause"] = True, None
        elif r["my_bib"] == 0:
            r["B"], r["B_cause"] = False, "cites but no bibliography found in the source"
        else:
            r["B"] = r["db_bib"] >= 1 and r["db_bib"] >= 0.5 * r["my_bib"] and r["db_cit"] >= 1
            r["B_cause"] = None if r["B"] else "bibliography in the source not (fully) in the database"
        r["A"] = r["db_abs_chunk"] and (not r["meta_abs"] or (r["abs_recall"] or 0) >= 0.5)
        r["success"] = r["S"] and r["E"] and r["B"] and r["A"]
        # lenient variant: an abstract from the metadata record counts (kb show --abstract)
        r["A_lenient"] = r["A"] or r["meta_abs"]
        r["success_lenient"] = r["S"] and r["E"] and r["B"] and r["A_lenient"]
        rows.append(r)
    rd = C.run_dir()
    n = len(rows)
    by = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        for k in ("S", "E", "B", "A", "success", "A_lenient", "success_lenient"):
            by[r["status"]][k] += bool(r[k])
            by["all"][k] += bool(r[k])
        by[r["status"]]["n"] += 1
        by["all"]["n"] += 1
    summ = dict(n=n, status_ok=sum(r["status"] == "ok" for r in rows),
                status_ok_or_pdf=sum(r["status"] in ("ok", "pdf") for r in rows),
                mine=sum(r["success"] for r in rows),
                mine_lenient=sum(r["success_lenient"] for r in rows),
                flat_sha_mismatch=[r["paper_id"] for r in rows if r["flat_exists"] and not r["flat_sha_ok"]],
                no_flat=[r["paper_id"] for r in rows if not r["flat_exists"]],
                by_status={k: dict(v) for k, v in by.items()})
    summ["rate_status_ok"] = round(summ["status_ok"] / n, 4)
    summ["rate_status_ok_or_pdf"] = round(summ["status_ok_or_pdf"] / n, 4)
    summ["rate_mine"] = round(summ["mine"] / n, 4)
    summ["rate_mine_lenient"] = round(summ["mine_lenient"] / n, 4)
    summ["failures_mine"] = [dict(paper_id=r["paper_id"], status=r["status"],
                                  failed=[k for k in "SEBA" if not r[k]], B_cause=r.get("B_cause")) for r in rows if not r["success"]]
    with open(os.path.join(rd, "scan.json"), "w") as fh:
        json.dump(dict(summary=summ, rows=rows), fh, indent=1)
    keys = list(rows[0].keys())
    with open(os.path.join(rd, "scan.tsv"), "w") as fh:
        fh.write("\t".join(keys) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) for k in keys) + "\n")
    print(json.dumps({k: v for k, v in summ.items() if k != "failures_mine"}, indent=1))
    print("failures under the verifier's definition:", len(summ["failures_mine"]))
    for x in summ["failures_mine"]:
        print("  ", x)


if __name__ == "__main__":
    main()
