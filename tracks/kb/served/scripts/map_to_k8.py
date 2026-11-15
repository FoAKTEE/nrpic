"""Map each served statement to the claims of the K8 seed (kb claim seed) that cover it.

A served statement and a K8 claim match when they have the same track and paper and one of
their locators names the same file with overlapping lines (claim_locators of the K8 layer).
Read-only.

    python3 -I map_to_k8.py <checked.jsonl> <db> <out.tsv>
"""
import json
import os
import sqlite3
import sys


def main(checked, db, out):
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    locs = {}
    for cid, pid, f, a, b, track, label, status, origin in c.execute(
            "SELECT l.claim_id, l.paper_id, l.file, l.line_start, l.line_end, m.track, c.label, m.status, m.seed_key "
            "FROM claim_locators l JOIN claim_meta m USING(claim_id) JOIN claims c USING(claim_id) "
            "WHERE c.origin NOT LIKE 'served:%'"):
        locs.setdefault((track, pid), []).append((cid, os.path.basename(f or ""), a, b, label, status, origin))
    rows = [json.loads(l) for l in open(checked) if l.strip()]
    n_match = 0
    with open(out, "w") as g:
        g.write("key\towner\tpaper_id\tranges\tk8_claim_ids\tk8_labels\tk8_status\tk8_seed_keys\n")
        for r in rows:
            hits = []
            for cid, f, a, b, label, status, origin in locs.get((r["owner"], r["paper_id"]), []):
                if f != os.path.basename(r["file"]) or a is None:
                    continue
                if any(lo <= (b or a) and hi >= a for lo, hi in r["ranges"]):
                    hits.append((cid, label, status, origin))
            hits = sorted(set(hits))
            n_match += bool(hits)
            g.write(f"{r['key']}\t{r['owner']}\t{r['paper_id']}\t{r['ranges']}\t"
                    f"{','.join(str(h[0]) for h in hits)}\t{','.join(h[1] for h in hits)}\t"
                    f"{','.join(h[2] or '' for h in hits)}\t{','.join(h[3] or '' for h in hits)}\n")
    print(f"{n_match} of {len(rows)} served statements are covered by K8 claims")


if __name__ == "__main__":
    main(*sys.argv[1:4])
