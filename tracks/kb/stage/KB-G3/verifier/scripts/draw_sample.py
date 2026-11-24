"""Item 1: stratified seeded draw of 60 claims from the snapshot (design in JOURNAL entry 1).

python3 -I draw_sample.py --seed SEED --out DIR
Writes DIR/population.tsv (every claim with stratum and track), DIR/allocation.json,
DIR/sample.tsv (the 60 drawn claims).
"""
import argparse
import collections
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vcommon as vc  # noqa: E402

ALLOC = {"S1": 18, "S2": 18, "S3": 12, "S4": 12}


def stratum(label, status):
    if label == "fulltext" and status == "checked":
        return "S1"
    if label == "fulltext":
        return "S2"
    if label == "to_verify":
        return "S3"
    if label in ("judgement", "background"):
        return "S4"
    return "excluded:" + str(label)


def allocate(n, sizes):
    """Largest remainder in proportion to sizes, at least one per present cell."""
    tot = sum(sizes.values())
    quota = {k: n * v / tot for k, v in sizes.items()}
    base = {k: max(1, int(q)) for k, q in quota.items()}
    rem = n - sum(base.values())
    order = sorted(sizes, key=lambda k: (-(quota[k] - int(quota[k])) if base[k] == int(quota[k]) else 1.0, k))
    i = 0
    while rem > 0:
        k = order[i % len(order)]
        if base[k] < sizes[k]:
            base[k] += 1
            rem -= 1
        i += 1
    while rem < 0:  # more minima than seats: take from the largest cells
        k = max(base, key=lambda x: (base[x], x))
        base[k] -= 1
        rem += 1
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    c = vc.connect()
    rows = c.execute(
        "select c.claim_id, c.label, m.status, m.track, c.paper_id,"
        " (select count(*) from claim_locators l where l.claim_id=c.claim_id)"
        " from claims c join claim_meta m using(claim_id) order by c.claim_id").fetchall()
    cells = collections.defaultdict(list)
    with open(os.path.join(a.out, "population.tsv"), "w") as f:
        f.write("claim_id\tstratum\ttrack\tlabel\tstatus\tpaper_id\tn_locators\n")
        for cid, lab, st, tr, pid, nl in rows:
            s = stratum(lab, st)
            f.write("%d\t%s\t%s\t%s\t%s\t%s\t%d\n" % (cid, s, tr, lab, st, pid, nl))
            cells[(s, tr)].append(cid)
    rng = random.Random(a.seed)
    alloc = {}
    sample = []
    for s in sorted(ALLOC):
        sizes = {tr: len(v) for (ss, tr), v in cells.items() if ss == s}
        al = allocate(ALLOC[s], sizes)
        alloc[s] = {"size": sum(sizes.values()), "cells": {tr: {"N": sizes[tr], "n": al[tr]} for tr in sorted(sizes)}}
        for tr in sorted(sizes):
            ids = sorted(cells[(s, tr)])
            for cid in rng.sample(ids, al[tr]):
                sample.append((s, tr, cid))
    excluded = {k[0]: 0 for k in cells if k[0].startswith("excluded")}
    for (s, tr), v in cells.items():
        if s.startswith("excluded"):
            excluded[s] += len(v)
    with open(os.path.join(a.out, "allocation.json"), "w") as f:
        json.dump({"seed": a.seed, "snapshot": vc.SNAPSHOT, "n_claims": len(rows),
                   "strata": alloc, "excluded": excluded}, f, indent=1)
    lab = {r[0]: r for r in rows}
    with open(os.path.join(a.out, "sample.tsv"), "w") as f:
        f.write("k\tclaim_id\tstratum\ttrack\tlabel\tstatus\tpaper_id\tn_locators\n")
        for k, (s, tr, cid) in enumerate(sample, 1):
            r = lab[cid]
            f.write("%d\t%d\t%s\t%s\t%s\t%s\t%s\t%d\n" % (k, cid, s, tr, r[1], r[2], r[4], r[5]))
    print(json.dumps(alloc, indent=1))
    print("excluded", excluded)
    print("sample", [x[2] for x in sample])


if __name__ == "__main__":
    main()
