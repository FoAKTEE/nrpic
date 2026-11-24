"""Item 3 tally: identifiers printed in the drawn entries against the database targets, and the
same test over every bibliography entry of the snapshot.

python3 -I bib_tally.py --draw DRAW_DIR/bib_draw.tsv --out DIR
Writes DIR/bib_verdicts_auto.tsv (one row per drawn key) and DIR/bib_summary.json.
My reading of an identifier: new-style ids anywhere (also inside \\arXiv{...}); old-style
archive/number also with a space or in capitals ("HEP-PH 9610477"); DOIs also inside
https://doi.org/ URLs. The raw-text comparison is done by hand (verdicts/bib_verdicts.tsv).
"""
import argparse
import collections
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcommon as vc  # noqa: E402

NEW = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5})(?:v\d+)?(?![\d])")
OLD = re.compile(r"\b(astro-ph|gr-qc|hep-th|hep-ph|hep-lat|hep-ex|nucl-th|quant-ph|math-ph|cond-mat|physics)\s*[/ ]\s*(\d{7})\b", re.I)
DOI = re.compile(r"(10\.\d{4,9}/[^\s{}\"'<>,;\\]+)")


def printed(text):
    t = text or ""
    ids = set(m.group(1) for m in NEW.finditer(t))
    ids |= set("%s/%s" % (m.group(1).lower(), m.group(2)) for m in OLD.finditer(t))
    dois = set(m.group(1).rstrip(".}").lower() for m in DOI.finditer(t))
    return ids, dois


def verdict(ids, dois, tax, tdoi):
    if ids:
        if tax and tax in ids:
            return "MATCH"
        return "WRONG" if tax else "MISSED"
    if dois:
        if tdoi and tdoi.lower() in dois:
            return "MATCH"
        if tax:
            return "DOI_PRINTED_ARXIV_TARGET"
        return "WRONG" if tdoi else "MISSED"
    return "NONE_PRINTED" + ("_DB_HAS" if (tax or tdoi) else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draw", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    csv.field_size_limit(10 ** 7)
    rows = list(csv.DictReader(open(a.draw), delimiter="\t"))
    per_paper = collections.defaultdict(collections.Counter)
    with open(os.path.join(a.out, "bib_verdicts_auto.tsv"), "w") as f:
        f.write("paper_id\tkey\tdb_rows\tprinted_ids\tprinted_dois\tdb_target_arxiv\tdb_target_doi\tdb_resolved_by\tid_verdict\n")
        for r in rows:
            ids, dois = printed(r["db_raw"] or r["src_entry"])
            v = verdict(ids, dois, r["db_target_arxiv"], r["db_target_doi"])
            per_paper[r["paper_id"]][v] += 1
            per_paper[r["paper_id"]]["drawn"] += 1
            per_paper[r["paper_id"]]["present"] += int(r["db_n"] != "0")
            f.write("\t".join([r["paper_id"], r["key"], r["db_n"], ",".join(sorted(ids)), ",".join(sorted(dois)),
                               r["db_target_arxiv"], r["db_target_doi"], r["db_resolved_by"], v]) + "\n")
    # the same test over the whole snapshot
    c = vc.connect()
    whole = collections.Counter()
    by_paper_missed = collections.Counter()
    for pid, raw, tax, tdoi in c.execute("select paper_id, raw, target_arxiv, target_doi from bib_entries"):
        ids, dois = printed(raw)
        v = verdict(ids, dois, tax, tdoi)
        whole[v] += 1
        if v == "MISSED":
            by_paper_missed[pid] += 1
    whole["entries"] = sum(v for k, v in whole.items())
    whole["with_target_doi"] = c.execute("select count(*) from bib_entries where target_doi is not null and target_doi != ''").fetchone()[0]
    summ = {"snapshot": vc.SNAPSHOT, "drawn_by_paper": {k: dict(v) for k, v in per_paper.items()},
            "drawn_total": dict(sum(per_paper.values(), collections.Counter())),
            "whole_snapshot": dict(whole),
            "whole_missed_top_papers": by_paper_missed.most_common(15)}
    with open(os.path.join(a.out, "bib_summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
