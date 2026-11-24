"""Item 3: ten cited keys per paper of ingest3's twenty, drawn from my own reading of the raw
source, printed next to the source entry and the database row for a reading by hand.

python3 -I draw_bib.py --seed SEED --ids FILE --out DIR
Writes DIR/bib_draw.tsv (one row per drawn key: source entry text, database row, automatic
identifier comparison) and DIR/bib_papers.tsv (per paper: my cited keys, my entry count,
database entries). The verdicts by hand go into verdicts/bib_verdicts.tsv.
"""
import argparse
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcommon as vc  # noqa: E402

ARX_NEW = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(?:v\d+)?")
ARX_OLD = re.compile(r"\b((?:astro-ph|gr-qc|hep-th|hep-ph|hep-lat|hep-ex|nucl-th|physics|quant-ph|cond-mat|math-ph|math)(?:\.[A-Z]{2})?/\d{7})")
DOI = re.compile(r"\b(10\.\d{4,9}/[^\s{}\"'<>,;]+)")


def aliases(flat_raw):
    """Macros defined as \\cite or \\bibitem (own detection, from the definitions)."""
    cite, item = set(), set()
    dpat = re.compile(r"\\(?:def|(?:re)?newcommand\*?\s*\{?|NewDocumentCommand\s*\{?)\\([A-Za-z]+)")
    ms = list(dpat.finditer(flat_raw))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else m.end() + 300
        body = flat_raw[m.end():min(end, m.end() + 300)]
        if re.search(r"\\cite\s*(\{#1\}|\})", body) or re.search(r"^\s*\{\\cite\}", body):
            cite.add(m.group(1))
        if re.search(r"\\bibitem\s*(\{#1\}|\})", body):
            item.add(m.group(1))
    cite.discard("cite")
    item.discard("bibitem")
    return sorted(cite), sorted(item)


def strip_defs(flat):
    return "\n".join(l for l in flat.split("\n")
                     if not re.search(r"\\(def|newcommand|renewcommand|NewDocumentCommand|DeclareRobustCommand)\b", l))


NOT_CITATIONS = ("citestyle", "citeproctext", "citeauthoryear", "citename", "bibliographystyle")


def my_cited_keys(flat):
    body = strip_defs(flat)
    # commands inside the reference list (\bibitem[\citeauthoryear{..}{..}]) are not citations
    for marker in ("\\begin{thebibliography}", "\\begin{references}"):
        i = body.find(marker)
        if i >= 0:
            body = body[:i]
    ca, _ = aliases(flat)
    keys = []
    pats = [vc.CITE] + [re.compile(r"\\%s\*?\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}" % re.escape(a)) for a in ca]
    for p in pats:
        for m in p.finditer(body):
            g = m.group(m.lastindex)
            if p is vc.CITE and m.group(1).lower() in NOT_CITATIONS:
                continue
            for k in g.split(","):
                k = k.strip()
                if k and "#" not in k and k not in keys:
                    keys.append(k)
    return keys, ca


def source_entries(paper, version, flat):
    """key -> entry text, from \\bibitem (and aliases) in the flattened text, any .bbl, any
    .bib, and AASTeX \\reference (keys #1, #2, ... by order)."""
    ent = {}
    _, ia = aliases(flat)
    texts = [flat]
    sdir = vc.src_dir(paper, version)
    for dp, _dn, fn in os.walk(sdir):
        for f in fn:
            if f.lower().endswith(".bbl"):
                texts.append(vc.strip_comments(vc.read_text(os.path.join(dp, f))))
    names = ["bibitem"] + ia
    pat = re.compile(r"\\(%s|harvarditem\s*(?:\[[^\]]*\])?\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}\s*\{[^}]*\})\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}"
                     % "|".join(re.escape(n) for n in names))
    for t in texts:
        t2 = strip_defs(t)
        ms = list(pat.finditer(t2))
        for i, m in enumerate(ms):
            end = ms[i + 1].start() if i + 1 < len(ms) else min(len(t2), m.end() + 1500)
            seg = t2[m.end():end]
            seg = seg.split("\\end{thebibliography}")[0]
            ent.setdefault(m.group(2).strip(), " ".join(seg.split())[:600])
    refs = list(re.finditer(r"\\reference\b", flat))
    for i, m in enumerate(refs):
        end = refs[i + 1].start() if i + 1 < len(refs) else min(len(flat), m.end() + 800)
        ent.setdefault("#%d" % (i + 1), " ".join(flat[m.end():end].split("\\end{references}")[0].split())[:600])
    for dp, _dn, fn in os.walk(sdir):
        for f in fn:
            if f.lower().endswith(".bib"):
                t = vc.read_text(os.path.join(dp, f))
                ms = list(re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,", t))
                for i, m in enumerate(ms):
                    end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
                    ent.setdefault(m.group(1), " ".join(t[m.end():end].split())[:600])
    return ent


def ids_in(text):
    ax = set(m.group(1) for m in ARX_NEW.finditer(text)) | set(m.group(1) for m in ARX_OLD.finditer(text))
    doi = set(m.group(1).rstrip(".}") .lower() for m in DOI.finditer(text))
    return sorted(ax), sorted(doi)


def clean(s):
    return (s or "").replace("\t", " ").replace("\n", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = random.Random(a.seed)
    c = vc.connect()
    corpus = set(r[0] for r in c.execute("select paper_id from papers"))
    pap = open(os.path.join(a.out, "bib_papers.tsv"), "w")
    pap.write("paper_id\tversion\tmy_main\tdb_main\tparse_status\tmy_cited_keys\tcite_aliases\tmy_source_entries\tdb_entries\tdb_distinct_keys\tmy_cited_without_db_entry\n")
    out = open(os.path.join(a.out, "bib_draw.tsv"), "w")
    out.write("paper_id\tkey\tsrc_entry\tsrc_arxiv\tsrc_doi\tdb_n\tdb_raw\tdb_target_arxiv\tdb_target_doi\tdb_resolved_by\tdb_confidence\tdb_eprint\tdb_title\tauto_arxiv\tauto_doi\ttarget_title\n")
    for pid in open(a.ids).read().split():
        v, st, dbm = c.execute("select version, parse_status, main_tex from papers where paper_id=?", (pid,)).fetchone()
        main, flat = vc.own_flat(pid, v)
        flat = flat or ""
        keys, ca = my_cited_keys(flat)
        ents = source_entries(pid, v, flat)
        db = {}
        for r in c.execute("select cite_key, raw, target_arxiv, target_doi, resolved_by, confidence, eprint, title"
                           " from bib_entries where paper_id=? order by bib_id", (pid,)):
            db.setdefault(r[0], []).append(r)
        nodb = [k for k in keys if k not in db]
        pool = sorted(keys) if keys else sorted(k for k in ents if k.startswith("#"))
        pap.write("%s\t%s\t%s\t%s\t%s\t%d\t%s\t%d\t%d\t%d\t%s\n" % (
            pid, v, main, dbm, st, len(keys), ",".join(ca), len(ents),
            sum(len(x) for x in db.values()), len(db), ",".join(nodb[:20])))
        draw = rng.sample(pool, min(a.n, len(pool))) if pool else []
        for k in draw:
            se = ents.get(k, "")
            sax, sdoi = ids_in(se)
            rows = db.get(k, [])
            r = rows[0] if rows else (k, "", None, None, None, None, None, None)
            tax, tdoi = r[2], (r[3] or "").lower() or None
            if sax:
                auto_ax = "match" if tax in sax else ("db_none" if not tax else "differ")
            else:
                auto_ax = "src_none" + ("/db_has" if tax else "")
            if sdoi:
                auto_doi = "match" if tdoi in sdoi else ("db_none" if not tdoi else "differ")
            else:
                auto_doi = "src_none" + ("/db_has" if tdoi else "")
            tt = ""
            if tax and tax in corpus:
                tt = c.execute("select title from papers where paper_id=?", (tax,)).fetchone()[0]
            out.write("\t".join(clean(str(x)) for x in [
                pid, k, se, ",".join(sax), ",".join(sdoi), len(rows), (r[1] or "")[:600], tax or "", tdoi or "",
                r[4] or "", r[5] if r[5] is not None else "", r[6] or "", r[7] or "", auto_ax, auto_doi, tt]) + "\n")
    pap.close()
    out.close()


if __name__ == "__main__":
    main()
