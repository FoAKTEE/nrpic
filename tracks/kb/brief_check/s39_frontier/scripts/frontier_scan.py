"""Scan the INSPIRE query results of work package s39_frontier for papers the brief does not cite.

Usage: python3 -I frontier_scan.py <queries.tsv> [<queries.tsv> ...] --out <dir>
Each queries.tsv (written by run_inspire.py) lists <tag>\t<query>\t<result json>\t<status>.
For every hit with an arXiv id the script records: id, arXiv month, title, first authors,
document type, citation count, the query tags that found it, whether the id occurs anywhere
in the brief (regex over the brief text, read as data) and whether the knowledge-base store
has its source. Writes candidates.tsv (all distinct hits), abstracts.tsv (id, title, abstract
as served by INSPIRE), queries_summary.tsv (per query:
hits_total, returned, not in brief, recent), fwd_counts.json (forward citations per cited id
split by in-brief), and prints a summary. Standard library only; the result files are data.
"""
import json
import os
import re
import sys

ROOT = "/data/haiyangw/nrpic"
BRIEF = os.path.join(ROOT, "einstein_vlasov_pic_cosmology_agent_brief.en.md")
RAW = os.path.join(ROOT, "kb-data/raw/arxiv")
ID_RX = re.compile(r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})")


def brief_ids():
    with open(BRIEF, encoding="utf-8") as fh:
        text = fh.read()
    return set(m.group(1) for m in ID_RX.finditer(text))


def yymm(aid):
    m = re.match(r"(\d{2})(\d{2})\.", aid)
    if m:
        return "20%s-%s" % m.groups()
    m = re.search(r"/(\d{2})(\d{2})", aid)
    return ("19" if int(m.group(1)) > 50 else "20") + "%s-%s" % m.groups() if m else "?"


def main(argv):
    out = argv[argv.index("--out") + 1]
    tsvs = [a for a in argv[:argv.index("--out")]]
    os.makedirs(out, exist_ok=True)
    bids = brief_ids()
    cand = {}
    qsum = []
    fwd = {}
    for tsv in tsvs:
        with open(tsv) as fh:
            rows = [l.rstrip("\n").split("\t") for l in fh if l.strip()]
        for tag, q, path, status in rows:
            if status != "0" or not os.path.exists(path):
                qsum.append((tag, q, "FAILED", 0, 0, 0))
                continue
            with open(path) as fh:
                d = json.load(fh)
            hits = d.get("hits", [])
            n_new = n_recent = 0
            ids_here = []
            for h in hits:
                ep = h.get("arxiv_eprints") or []
                if not ep:
                    continue
                aid = ep[0].get("value")
                if not aid:
                    continue
                ids_here.append(aid)
                titles = h.get("titles") or [{}]
                au = [a.get("full_name", "") for a in (h.get("authors") or [])]
                c = cand.setdefault(aid, {
                    "id": aid, "month": yymm(aid), "title": titles[0].get("title", "").replace("\n", " "),
                    "authors": "; ".join(au[:3]) + (" et al." if len(au) > 3 else ""),
                    "n_authors": len(au), "doc": ",".join(h.get("document_type") or []),
                    "cites": h.get("citation_count", 0), "tags": [], "in_brief": aid in bids,
                    "in_store": os.path.isdir(os.path.join(RAW, aid.replace("/", "_"))),
                    "abstract": ((h.get("abstracts") or [{}])[0].get("value") or "").replace("\n", " ").replace("\t", " ")})
                if tag not in c["tags"]:
                    c["tags"].append(tag)
                if aid not in bids:
                    n_new += 1
                    if c["month"] >= "2026-10":
                        n_recent += 1
            qsum.append((tag, q, d.get("hits_total"), len(hits), n_new, n_recent))
            if tag.startswith("fwd "):
                cited = tag.split()[1]
                f = fwd.setdefault(cited, {"in_brief": 0, "not_in_brief": 0, "hits_total": 0, "returned": 0})
                f["hits_total"] += d.get("hits_total") or 0
                f["returned"] += len(hits)
                for aid in ids_here:
                    f["in_brief" if aid in bids else "not_in_brief"] += 1
    with open(os.path.join(out, "candidates.tsv"), "w") as fo:
        fo.write("id\tmonth\tin_brief\tin_store\tcites\tdoc\ttags\tauthors\ttitle\n")
        for c in sorted(cand.values(), key=lambda c: (c["month"], c["id"]), reverse=True):
            fo.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                c["id"], c["month"], int(c["in_brief"]), int(c["in_store"]), c["cites"], c["doc"],
                ",".join(c["tags"]), c["authors"], c["title"]))
    with open(os.path.join(out, "abstracts.tsv"), "w") as fo:
        for c in sorted(cand.values(), key=lambda c: c["id"]):
            fo.write("%s\t%s\t%s\n" % (c["id"], c["title"], c["abstract"]))
    with open(os.path.join(out, "queries_summary.tsv"), "w") as fo:
        fo.write("tag\tquery\thits_total\treturned\tnot_in_brief\tnot_in_brief_since_2026-10\n")
        for r in qsum:
            fo.write("\t".join(str(x) for x in r) + "\n")
    with open(os.path.join(out, "fwd_counts.json"), "w") as fo:
        json.dump(fwd, fo, indent=1, sort_keys=True)
    n_all = len(cand)
    n_nb = sum(1 for c in cand.values() if not c["in_brief"])
    n_rec = sum(1 for c in cand.values() if not c["in_brief"] and c["month"] >= "2026-10")
    n_nov = sum(1 for c in cand.values() if not c["in_brief"] and c["month"] >= "2026-11")
    trunc = [r for r in qsum if isinstance(r[2], int) and r[2] > r[3]]
    print("queries: %d (failed %d, truncated at 25: %d)" % (
        len(qsum), sum(1 for r in qsum if r[2] == "FAILED"), len(trunc)))
    for r in trunc:
        print("  truncated:", r[0], r[1], r[2], r[3])
    print("distinct papers with arXiv id: %d; not cited in the brief: %d; of these since 2026-10: %d, "
          "in 2026-11: %d" % (n_all, n_nb, n_rec, n_nov))


if __name__ == "__main__":
    main(sys.argv[1:])
