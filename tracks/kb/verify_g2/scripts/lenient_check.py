"""Step 4c of the KB-G2 verifier: the papers whose S or B verdict passed only because the source
has no sectioning command (S) or no \\cite (B) -- the leniency found in the source check
(JOURNAL entry 7). For each such paper this looks in flat.tex (the verifier's regular
expressions, text only) for headings written without \\section (bold, small caps, centred or
numbered "I. Introduction"-style lines, \\paragraph) and for reference lists without \\cite
(\\bibitem, a `references` environment, \\item or \\ref lines after a References heading), and
prints them next to the database counts. A paper is a "structure gap" when headings exist but
the database has no section, or a reference list exists but the database has no bibliography.
Usage: lenient_check.py --scan SCAN_JSON
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402
import locmap as L  # noqa: E402

KEYW = r"(?:Introduction|INTRODUCTION|Conclusions?|CONCLUSIONS?|Discussion|DISCUSSION|Summary|SUMMARY|Results|" \
       r"RESULTS|Acknowledge?ments?|ACKNOWLEDGE?MENTS?|Appendix|APPENDIX|Methods?|Model|Setup|Simulations?)"
RE_HEAD = [
    re.compile(r"\{\s*\\(?:bf|textbf|bfseries|sc|scshape|large|Large|it|em)\b[^{}\n]{0,60}" + KEYW),
    re.compile(r"\\(?:textbf|textsc|centerline|noindent\s*\\textbf)\s*\{[^{}\n]{0,60}" + KEYW),
    re.compile(r"^\s*(?:[IVX]{1,4}|\d{1,2})\.\s+" + KEYW, re.M),
    re.compile(r"\\(?:paragraph|subparagraph)\*?\s*\{"),
    re.compile(r"\\(?:rma|rmb|rmm|rmw|rmz)\b[^{}\n]{0,60}" + KEYW),
]
RE_REFHEAD = re.compile(r"(?:\{\s*\\(?:bf|large|Large|sc)\b[^{}\n]{0,20}|\\centerline\s*\{[^{}\n]{0,30}|^\s*)"
                        r"(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)", re.M)


def look(flat):
    heads = []
    for rx in RE_HEAD:
        heads += [m.group(0).strip()[:60] for m in rx.finditer(flat)]
    refpos = [m.start() for m in RE_REFHEAD.finditer(flat)]
    tail = flat[refpos[-1]:] if refpos else ""
    return dict(n_heads=len(heads), heads=heads[:6],
                bibitem=len(re.findall(r"\\bibitem\b", flat)),
                references_env=bool(re.search(r"\\begin\s*\{references\}", flat)),
                ref_heading=len(refpos),
                items_after_refs=len(re.findall(r"\\item\b", tail)),
                ref_lines_after_refs=len(re.findall(r"^\\ref\b", tail, re.M)),
                words=len(re.findall(r"[A-Za-z]{3,}", flat)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    a = ap.parse_args()
    rows = json.load(open(a.scan))["rows"]
    out = []
    for r in rows:
        if not r["success"]:
            continue
        s_len = r["my_sec"] == 0 and r["db_sec"] == 0
        b_len = r["my_cite_cmds"] == 0
        if not (s_len or b_len):
            continue
        lk = look(L.flat_text(r["paper_id"]))
        s_gap = s_len and lk["n_heads"] >= 2
        b_gap = b_len and r["db_bib"] == 0 and (lk["bibitem"] > 0 or lk["references_env"] or lk["items_after_refs"] >= 3
                                               or lk["ref_lines_after_refs"] >= 3)
        rec = dict(paper_id=r["paper_id"], status=r["status"], S_lenient=s_len, B_lenient=b_len, db_sec=r["db_sec"],
                   db_bib=r["db_bib"], db_cit=r["db_cit"], db_eq=r["db_eq"], **lk, S_gap=s_gap, B_gap=b_gap)
        out.append(rec)
        print(json.dumps(rec))
    n_gap = sum(1 for x in out if x["S_gap"] or x["B_gap"])
    summ = dict(n=len(out), S_lenient=sum(x["S_lenient"] for x in out), B_lenient=sum(x["B_lenient"] for x in out),
                S_gap=sum(x["S_gap"] for x in out), B_gap=sum(x["B_gap"] for x in out), any_gap=n_gap,
                gap_ids=[x["paper_id"] for x in out if x["S_gap"] or x["B_gap"]])
    print(json.dumps(summ, indent=1))
    with open(os.path.join(C.run_dir(), "lenient.json"), "w") as f:
        json.dump(dict(summary=summ, rows=out), f, indent=1)


if __name__ == "__main__":
    main()
