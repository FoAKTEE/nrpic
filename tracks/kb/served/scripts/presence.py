"""Where each requested arXiv id stands: manifest, raw store, downloads table, papers table.

Read-only: opens a database with mode=ro and lists kb-data/raw/arxiv; reads nothing inside
a download. Usage:
    python3 -I presence.py <db path> <out.tsv>
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from requested_ids import IDS  # noqa: E402

RAW = "/data/haiyangw/nrpic/kb-data/raw/arxiv"
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", "..", "kb", "manifests", "arxiv.tsv")


def manifest():
    out = {}
    with open(MANIFEST) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            if p[0] == "id":
                continue
            out[p[0]] = (p[1], p[2])
    return out


def main(db, out):
    man = manifest()
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = []
    for req, items in IDS.items():
        for pid, want in items:
            key = pid.replace("/", "_")
            vers = sorted(os.listdir(os.path.join(RAW, key))) if os.path.isdir(os.path.join(RAW, key)) else []
            d = c.execute("select status, version, source_kind from downloads where paper_id=?", (pid,)).fetchone()
            p = c.execute("select parse_status, grp, priority, version from papers where paper_id=?", (pid,)).fetchone()
            nsec = c.execute("select count(*) from sections where paper_id=?", (pid,)).fetchone()[0]
            neq = c.execute("select count(*) from equations where paper_id=?", (pid,)).fetchone()[0]
            nbib = c.execute("select count(*) from bib_entries where paper_id=?", (pid,)).fetchone()[0]
            g, pr = man.get(pid, ("-", "-"))
            rows.append([req, pid, want, g, pr, ",".join(vers) or "-",
                         (d[0] if d else "-"), (d[2] if d else "-"),
                         (p[0] if p else "-"), (p[1] or "-") if p else "-",
                         str(nsec), str(neq), str(nbib)])
    hdr = ["request", "id", "want", "manifest_grp", "manifest_prio", "raw_versions",
           "download_status", "source_kind", "parse_status", "db_grp", "sections",
           "equations", "bib_entries"]
    with open(out, "w") as f:
        f.write("\t".join(hdr) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    for r in rows:
        print("\t".join(r))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
