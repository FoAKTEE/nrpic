#!/usr/bin/env python3
"""Write the verdicts of LINKS.tsv (output of link_evidence.py) into the status and
evidence columns of kb/curated/paper_code_links.tsv, and nothing else: comment lines, the
header and every other column are copied byte for byte. The kb verdict is appended to the
existing evidence text after ' | ', and replaces an earlier kb verdict of the same form.

    python3 -I apply_verdicts.py LINKS.tsv RUN_ID kb/curated/paper_code_links.tsv
"""
import csv
import sys

MARK = " | kb verdict "


def main(links, run_id, curated):
    v = {}
    with open(links, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            v[r["link_key"]] = r
    lines = open(curated, newline="").read().split("\n")
    out, header, n = [], None, 0
    for ln in lines:
        if not ln or ln.startswith("#"):
            out.append(ln)
            continue
        cells = ln.split("\t")
        if header is None:
            header = cells
            out.append(ln)
            continue
        row = dict(zip(header, cells))
        r = v.get(row["link_key"])
        if r is None:
            out.append(ln)
            continue
        ev = row["evidence"].split(MARK)[0]
        parts = [f"{r['verdict']} ({run_id})", f"test {r['test_entries']}"]
        if r["records"] != "-":
            parts.append(f"record {r['records']}")
        if r["reach"] != "-":
            parts.append(f"reach {r['reach']}@47ab19ab")
        if r["outcome"] != "-":
            parts.append(f"outcome: {r['outcome']}")
        if r["note"] != "-":
            parts.append(f"note: {r['note']}")
        row["evidence"] = ev + MARK + "; ".join(parts).replace("\t", " ")
        row["status"] = r["verdict"]
        out.append("\t".join(row[h] for h in header))
        n += 1
    with open(curated, "w", newline="") as f:
        f.write("\n".join(out))
    print(f"{n} rows updated in {curated}")
    return 0 if n == len(v) else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
