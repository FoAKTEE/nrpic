"""Test E5 of the embed package: tag counts of kb/curated/equation_tags.yaml over all equations,
the tags of the labelled equations of 2611.12831, and a random sample of 10 tagged equations per
tag for a precision judgement by reading.

    kb/.venv/bin/python -I tracks/kb/embed/scripts/sample_tags.py OUT_DIR [--db PATH]

OUT_DIR/counts.json: counts and sampled eq ids (no paper text; goes into the journal).
OUT_DIR/sample_for_reading.txt: context and TeX of the sampled equations, for reading on this
machine only (scratch, never committed).
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(WT, "kb"))

from kbtool import db as _db            # noqa: E402
from kbtool import eq_tags as T         # noqa: E402
from kbtool.paths import layout         # noqa: E402

CHECK = {"eq:vlasov": "vlasov", "eq:first-order-shape": "deposition", "eq:z4-einstein": "z4c",
         "eq:plummer-hamiltonian": "hamiltonian_constraint"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--db")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20261115)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lay = layout()
    path = a.db or lay.db_work
    rules = T.load_rules()
    con = _db.connect_ro(path)
    rows = con.execute("SELECT eq_id, paper_id, label, number, context, tex_norm FROM equations").fetchall()
    con.close()
    by_tag = {t: [] for t in rules["tags"]}
    which = {}                                # how each equation matched: label clause or context clause
    for eid, pid, label, num, ctx, tn in rows:
        for t in T.tags_for(rules, label, ctx, tn):
            by_tag[t].append(eid)
            via = [k for k, cl in enumerate(rules["tags"][t]["clauses"]) if T.match_clause(cl, label, ctx, tn)]
            which[(eid, t)] = via
    rng = random.Random(a.seed)
    sample = {t: sorted(rng.sample(ids, min(a.n, len(ids)))) for t, ids in by_tag.items()}
    info = {r[0]: r for r in rows}
    out = {"database": os.path.realpath(path), "rules_sha256": rules["sha256"], "rules_version": rules["version"],
           "seed": a.seed, "equations": len(rows),
           "per_tag": {t: len(v) for t, v in by_tag.items()},
           "papers_per_tag": {t: len({info[i][1] for i in v}) for t, v in by_tag.items()},
           "via_label_clause": {t: sum(1 for i in v if 0 in which[(i, t)]) for t, v in by_tag.items()},
           "sample": {t: [[i, info[i][1], info[i][2], info[i][3]] for i in ids] for t, ids in sample.items()},
           "check_2611": {}}
    for label, want in CHECK.items():
        r = [x for x in rows if x[1] == "2611.12831" and x[2] == label]
        got = T.tags_for(rules, r[0][2], r[0][4], r[0][5]) if r else None
        out["check_2611"][label] = {"want": want, "got": got, "ok": bool(got and want in got)}
    with open(os.path.join(a.out, "counts.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(a.out, "sample_for_reading.txt"), "w") as f:
        for t, ids in sample.items():
            f.write(f"\n######## {t} ({len(by_tag[t])} tagged)\n")
            for i in ids:
                _, pid, label, num, ctx, tn = info[i]
                f.write(f"\n--- eq {i} {pid} ({num}) {label} via clauses {which[(i, t)]}\n")
                f.write(f"CONTEXT: {(ctx or '')[:700]}\nTEX: {(tn or '')[:300]}\n")
    print(json.dumps({k: v for k, v in out.items() if k != "sample"}, indent=1))


if __name__ == "__main__":
    main()
