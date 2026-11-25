#!/usr/bin/env python3
"""Strata, counts and the seeded draw of 40 claims (item 2), and the item-1 list (second verifier).

    python3 -I draw.py --seed SEED --out DIR        # writes strata.json, sample.tsv, item1.tsv

Population: live claims whose label says a source supports the text (fulltext, abstract,
title_only; status checked, located, partial), minus the claims re-read already (item 1 of
this package, the first verifier's verdict files, claims3's 30 sampled claims), so the draw is
new information. Strata (disjoint; definitions written in JOURNAL.md entry 1 before the draw):
  P  checked by a person: status checked and not in W
  M  located by machine: in W with label_set_by 'auto' (claims3's WA)
  Q  rest of the weak class: in W, label set by claims_tracks, claims_brief or its 12.8 map
     (claims3's WQ, WB, WM)
  W  = the weak class: label set by a pipeline step and no event of a person's reading.
Allocation 14 / 13 / 13 (near equal, for an interval per stratum); population estimates are
weighted by stratum sizes in tally.py. Read-only; standard library only.
"""
import argparse
import csv
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2lib  # noqa: E402

WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5))
V1 = os.path.join(WT, "tracks", "kb", "stage", "KB-G3", "verifier", "verdicts")
C3 = os.path.join(WT, "tracks", "kb", "claims3", "SAMPLE_VERDICTS.tsv")
ALLOC = {"P": 14, "M": 13, "Q": 13}


def ids_from_tsv(path, col="claim_id"):
    out = set()
    with open(path) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            try:
                out.add(int(row[col]))
            except (KeyError, ValueError, TypeError):
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    con = v2lib.connect()
    item1 = {c for v in v2lib.ITEM1.values() for c in v}
    v1 = ids_from_tsv(os.path.join(V1, "sample_verdicts.tsv")) | ids_from_tsv(os.path.join(V1, "refutations.tsv"))
    c3 = ids_from_tsv(C3)
    read = v2lib.person_read_ids(con)
    rows = con.execute(
        "SELECT c.claim_id, c.label, m.status, m.label_set_by, m.track FROM claims c "
        "JOIN claim_meta m USING(claim_id) WHERE c.label IN ('fulltext','abstract','title_only') "
        "AND m.status IN ('checked','located','partial') ORDER BY c.claim_id").fetchall()
    strata = {"P": [], "M": [], "Q": []}
    other, excluded = [], {"item1": 0, "verifier1": 0, "claims3_sample": 0}
    w_all = {"M": 0, "Q": 0}          # weak class before the 'new information' exclusions
    for cid, label, status, setter, track in rows:
        in_w = setter in v2lib.PIPELINE_SETTERS and cid not in read and cid not in v1
        if in_w and cid not in item1 and cid not in c3:
            w_all[v2lib.PIPELINE_SETTERS[setter]] += 1
        if cid in item1:
            excluded["item1"] += 1
            continue
        if cid in v1:
            excluded["verifier1"] += 1
            continue
        if cid in c3:
            excluded["claims3_sample"] += 1
            continue
        if in_w:
            strata[v2lib.PIPELINE_SETTERS[setter]].append((cid, label, status, setter, track))
        elif status == "checked":
            strata["P"].append((cid, label, status, setter, track))
        else:
            other.append((cid, label, status, setter, track))
    # claims3's own count of its class on today's snapshot (its README: 548 = 543 + 5 annotated)
    read_c3 = {r[0] for r in con.execute(
        "SELECT DISTINCT claim_id FROM claim_events WHERE by IN (%s) OR evidence LIKE ?"
        % ",".join("?" * 4), v2lib.PERSON_READ_BY[:4] + (v2lib.AUDIT_PREFIX + "%",))}
    c3_named = {803, 805, 81, 84, 85, 171, 179, 187, 192, 213, 277, 290, 314, 424, 431, 549,
                619, 620, 621, 622, 623, 625}
    all_pos = con.execute(
        "SELECT c.claim_id, m.label_set_by FROM claims c JOIN claim_meta m USING(claim_id) "
        "WHERE c.label IN ('fulltext','abstract','title_only')").fetchall()
    c3_style = sum(1 for cid, s in all_pos if s in v2lib.PIPELINE_SETTERS and cid not in read_c3
                   and cid not in v1 and cid not in c3_named)
    info = {"snapshot": v2lib.SNAP_ID, "population_positive_live": len(rows),
            "excluded": excluded, "strata_sizes": {k: len(v) for k, v in strata.items()},
            "other_not_sampled": len(other),
            "other_breakdown": {}, "weak_class_unread_today": sum(w_all.values()),
            "weak_class_unread_today_by_stratum": w_all,
            "weak_class_claims3_query_today": c3_style, "alloc": ALLOC, "seed": a.seed}
    for r in other:
        k = f"{r[2]}|{r[3]}"
        info["other_breakdown"][k] = info["other_breakdown"].get(k, 0) + 1
    rng = random.Random(a.seed)
    sample = []
    for s in ("P", "M", "Q"):
        pick = rng.sample(strata[s], ALLOC[s])
        sample += [(s,) + p for p in sorted(pick)]
    with open(os.path.join(a.out, "sample.tsv"), "w") as f:
        f.write("k\tstratum\tclaim_id\tlabel\tstatus\tlabel_set_by\ttrack\n")
        for k, r in enumerate(sample, 1):
            f.write("\t".join([str(k)] + [str(x) for x in r]) + "\n")
    with open(os.path.join(a.out, "item1.tsv"), "w") as f:
        f.write("group\tclaim_id\tlabel\tstatus\tlabel_set_by\tchecked_by\ttrack\n")
        for g, ids in v2lib.ITEM1.items():
            for cid in ids:
                d = v2lib.claim(con, cid)
                f.write("\t".join(str(x) for x in (g, cid, d["label"], d["status"], d["label_set_by"],
                                                   d["checked_by"], d["track"])) + "\n")
    with open(os.path.join(a.out, "strata.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
