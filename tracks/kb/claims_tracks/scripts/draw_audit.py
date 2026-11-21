#!/usr/bin/env python3
"""Draw the audit sample: N machine-located fulltext claims (label fulltext, status located),
stratified by track with largest-remainder proportional allocation, seed recorded.

    python3 -I draw_audit.py --seed 20261121 --n 40 --out DIR

Writes DIR/audit_sample.tsv (claim_id, track, paper_id, locator, first 160 characters of the
claim text) and DIR/audit_strata.json. Read-only on kb.sqlite; standard library only.
"""
import argparse
import json
import os
import random
import sqlite3

DB = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"
ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--n", type=int, default=40)
ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
a = ap.parse_args()
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
rows = con.execute("SELECT c.claim_id, m.track, c.paper_id, c.locator, c.text FROM claims c JOIN claim_meta m "
                   "USING(claim_id) WHERE c.label='fulltext' AND m.status='located' ORDER BY c.claim_id").fetchall()
by = {}
for r in rows:
    by.setdefault(r[1], []).append(r)
tot = len(rows)
quota = {t: a.n * len(v) / tot for t, v in by.items()}
alloc = {t: int(q) for t, q in quota.items()}
for t in sorted(quota, key=lambda t: -(quota[t] - int(quota[t])))[: a.n - sum(alloc.values())]:
    alloc[t] += 1
rng = random.Random(a.seed)
sample = []
for t in sorted(by):
    sample += rng.sample(by[t], alloc[t])
sample.sort(key=lambda r: (r[1], r[0]))
with open(os.path.join(a.out, "audit_sample.tsv"), "w") as f:
    f.write("claim_id\ttrack\tpaper_id\tlocator\ttext160\n")
    for cid, t, pid, loc, text in sample:
        f.write(f"{cid}\t{t}\t{pid}\t{loc}\t{(text or '')[:160].replace(chr(9), ' ').replace(chr(10), ' ')}\n")
json.dump({"seed": a.seed, "n": a.n, "population": tot, "strata": {t: len(v) for t, v in by.items()},
           "allocation": alloc}, open(os.path.join(a.out, "audit_strata.json"), "w"), indent=1)
print(json.dumps(alloc), tot)
