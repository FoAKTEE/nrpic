"""Lead check W6: count of claims and sha256 of claims 1..N (text, label, locator, paper, origin)
and of their claim_meta rows, read-only. Usage: python3 -I w2_claims_digest.py DB [N]"""
import hashlib
import sqlite3
import sys

db = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 618
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
h = hashlib.sha256()
for r in c.execute("select claim_id, text, label, locator, paper_id, origin from claims where claim_id<=? "
                   "order by claim_id", (n,)):
    h.update(repr(r).encode())
for r in c.execute("select claim_id, seed_key, status, label_set_by from claim_meta where claim_id<=? "
                   "order by claim_id", (n,)):
    h.update(repr(r).encode())
tot, lo, hi = c.execute("select count(*), min(claim_id), max(claim_id) from claims").fetchone()
lab = dict(c.execute("select label, count(*) from claims where claim_id>? group by label", (n,)).fetchall())
print(f"claims {tot} ids {lo}-{hi} digest(1..{n}) {h.hexdigest()[:16]} labels(>{n}) {lab}")
