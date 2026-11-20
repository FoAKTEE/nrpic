"""Step 1 of the KB-G2 verifier: draw the papers of the blind held-out set.

Stratified random draw from all papers of the snapshot:
  * every group (papers.grp) gets one slot; the remaining slots go to groups drawn
    with probability proportional to their size (without replacement);
  * priority quotas over the slots (default 4 x priority 3, 7 x priority 2,
    13 x priority 1: priority 3 oversampled, the rest about proportional);
  * priorities are assigned to slots by a seeded shuffle that is retried until every
    (group, priority) cell has enough papers; papers are then drawn inside each cell.
Writes draw.json into $NRPIC_RUN_DIR and prints a table.
"""
import argparse
import collections
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--quota", default="3:4,2:7,1:13")
    ap.add_argument("--db", default=C.SNAP)
    a = ap.parse_args()

    quota = {int(k): int(v) for k, v in (x.split(":") for x in a.quota.split(","))}
    assert sum(quota.values()) == a.n
    con = C.open_ro(a.db)
    rows = con.execute(
        "select paper_id, grp, priority, parse_status, source_kind, version, main_tex"
        " from papers order by paper_id").fetchall()
    rng = random.Random(a.seed)
    cells = collections.defaultdict(list)
    for r in rows:
        cells[(r["grp"], r["priority"])].append(dict(r))
    groups = sorted({r["grp"] for r in rows})
    size = collections.Counter(r["grp"] for r in rows)
    slots = list(groups)
    extra = a.n - len(groups)
    pool = list(groups)
    for _ in range(extra):
        w = [size[g] for g in pool]
        g = rng.choices(pool, weights=w, k=1)[0]
        pool.remove(g)
        slots.append(g)
    slots.sort()
    labels = [p for p, k in sorted(quota.items(), reverse=True) for _ in range(k)]
    for attempt in range(1, 100001):
        rng.shuffle(labels)
        need = collections.Counter(zip(slots, labels))
        if all(len(cells[c]) >= k for c, k in need.items()):
            break
    else:
        raise SystemExit("no feasible assignment")
    picks = []
    for c, k in sorted(need.items()):
        picks.extend(rng.sample(sorted(cells[c], key=lambda d: d["paper_id"]), k))
    picks.sort(key=lambda d: (d["grp"], -d["priority"], d["paper_id"]))
    out = dict(seed=a.seed, n=a.n, quota=quota, db=a.db, population=len(rows),
               assignment_attempts=attempt, picks=picks)
    path = os.path.join(C.run_dir(), "draw.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"seed {a.seed}; population {len(rows)}; attempts {attempt}; written {path}")
    for d in picks:
        print(d["grp"], d["priority"], d["paper_id"], d["parse_status"], d["source_kind"],
              d["version"], d["main_tex"])
    print("by priority", collections.Counter(d["priority"] for d in picks))
    print("by status", collections.Counter(d["parse_status"] for d in picks))


if __name__ == "__main__":
    main()
