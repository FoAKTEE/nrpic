#!/usr/bin/env python3
"""The weak class of the KB-G3 verifier, by query, and the seeded draw of its sample.

    python3 -I weak_class.py count [--db PATH]
    python3 -I weak_class.py draw --seed SEED --n 30 --out DIR [--db PATH]

Definition (written before the draw; JOURNAL.md entry 1, prediction P3):

  P  claims whose current label says that a source supports the text: fulltext, abstract,
     title_only.
  W  claims of P whose label was set by a pipeline step, not by a reading of the claim against
     its own wording:
       WA  label_set_by = 'auto': the seeder and the automatic locator/number check
           (status located or partial; nobody read the passage);
       WQ  label set by the queue processing of claims_tracks (label_set_by 'kb-claims_tracks'):
           a person read the source to answer the track's question; whether the claim's text
           says what was read was not part of the step (the case of 682);
       WB  label set by claims_brief (label_set_by 'kb-claims_brief'): the brief-check join and
           the defect table; the reading was that of another package (CHECK.md rows);
       WM  label set by the 12.8 map of claims_brief (label_set_by 'kb-claims_brief (12.8 map)'):
           the brief's own bracket, mapped to a label.
     minus every claim that a person already read against its own wording:
       - an event of the audits that judged the wording ('kb claims helper (manual read, audit
         P2)'; evidence starting '[audit 2026-11-21' of claims_tracks/AUDIT.md);
       - an event of the leads' own readings ('kb lead (wave 2), read at the source',
         'kb lead (wave 2b)', 'kb-lead-b13');
       - a claim in the KB-G3 verifier's verdict files (sample_verdicts.tsv, refutations.tsv);
       - the claims this package processes by name (803, 805, the fragments of item 4).
Strata are WA, WQ, WB, WM; allocation proportional (largest remainder), at least one per
non-empty stratum. Read-only on the database; standard library only.
"""
import argparse
import csv
import json
import os
import random
import sqlite3

HOME = "/data/haiyangw/nrpic"
DB = os.path.join(HOME, "kb-data", "db", "kb.sqlite")
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
VERDICTS = os.path.join(WT, "tracks", "kb", "stage", "KB-G3", "verifier", "verdicts")

READ_BY = ("kb claims helper (manual read, audit P2)", "kb lead (wave 2), read at the source",
           "kb lead (wave 2b)", "kb-lead-b13")
AUDIT_PREFIX = "[audit 2026-11-21"
NAMED = {803, 805, 81, 84, 85, 171, 179, 187, 192, 213, 277, 290, 314, 424, 431, 549,
         619, 620, 621, 622, 623, 625}
STRATUM_OF = {"auto": "WA", "kb-claims_tracks": "WQ", "kb-claims_brief": "WB",
              "kb-claims_brief (12.8 map)": "WM"}


def verifier_ids():
    out = set()
    for name in ("sample_verdicts.tsv", "refutations.tsv"):
        with open(os.path.join(VERDICTS, name)) as f:
            for row in csv.DictReader(f, delimiter="\t"):
                try:
                    out.add(int(row["claim_id"]))
                except (KeyError, ValueError):
                    pass
    return out


def population(con):
    rows = con.execute(
        "SELECT c.claim_id, c.label, m.status, m.label_set_by, m.track, c.paper_id, c.locator, c.text "
        "FROM claims c JOIN claim_meta m USING(claim_id) "
        "WHERE c.label IN ('fulltext','abstract','title_only') ORDER BY c.claim_id").fetchall()
    read = {r[0] for r in con.execute(
        "SELECT DISTINCT claim_id FROM claim_events WHERE by IN (%s) OR evidence LIKE ?"
        % ",".join("?" * len(READ_BY)), READ_BY + (AUDIT_PREFIX + "%",))}
    ver = verifier_ids()
    strata, excluded = {}, {"read": 0, "verifier": 0, "named": 0, "other_setter": 0}
    for cid, label, status, set_by, track, pid, loc, text in rows:
        if cid in NAMED:
            excluded["named"] += 1
            continue
        if cid in ver:
            excluded["verifier"] += 1
            continue
        if cid in read:
            excluded["read"] += 1
            continue
        s = STRATUM_OF.get(set_by)
        if s is None:
            excluded["other_setter"] += 1
            continue
        strata.setdefault(s, []).append({"claim_id": cid, "stratum": s, "label": label, "status": status,
                                         "track": track, "paper_id": pid, "locator": loc,
                                         "text160": (text or "")[:160].replace("\t", " ").replace("\n", " ")})
    return len(rows), strata, excluded


def allocate(strata, n):
    tot = sum(len(v) for v in strata.values())
    quota = {s: n * len(v) / tot for s, v in strata.items()}
    alloc = {s: max(1, int(q)) for s, q in quota.items()}
    rest = n - sum(alloc.values())
    # largest remainder among the strata not already raised to the minimum of one
    cand = [s for s in quota if int(quota[s]) >= 1]
    for s in sorted(cand, key=lambda s: (-(quota[s] - int(quota[s])), s))[:max(rest, 0)]:
        alloc[s] += 1
    return alloc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("count", "draw"))
    ap.add_argument("--db", default=DB)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    n_p, strata, excl = population(con)
    counts = {s: len(v) for s, v in sorted(strata.items())}
    info = {"db": a.db, "P": n_p, "W": sum(counts.values()), "strata": counts, "excluded": excl}
    if a.what == "count":
        print(json.dumps(info, indent=1))
        return 0
    if a.seed is None or not a.out:
        ap.error("draw needs --seed and --out")
    alloc = allocate(strata, a.n)
    rng = random.Random(a.seed)
    sample = []
    for s in sorted(strata):
        sample += rng.sample(strata[s], alloc[s])
    sample.sort(key=lambda r: (r["stratum"], r["claim_id"]))
    os.makedirs(a.out, exist_ok=True)
    cols = ("k", "claim_id", "stratum", "label", "status", "track", "paper_id", "locator", "text160")
    with open(os.path.join(a.out, "weak_sample.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for k, r in enumerate(sample, 1):
            r["k"] = k
            f.write("\t".join(str(r[c] if r[c] is not None else "") for c in cols) + "\n")
    with open(os.path.join(a.out, "weak_population.tsv"), "w") as f:
        f.write("claim_id\tstratum\tlabel\tstatus\ttrack\n")
        for s in sorted(strata):
            for r in strata[s]:
                f.write(f"{r['claim_id']}\t{s}\t{r['label']}\t{r['status']}\t{r['track']}\n")
    info.update({"seed": a.seed, "n": a.n, "allocation": alloc})
    with open(os.path.join(a.out, "weak_draw.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
