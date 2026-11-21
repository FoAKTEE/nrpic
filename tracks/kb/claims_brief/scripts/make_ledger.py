#!/usr/bin/env python3
"""Ledger of package claims_brief from the database (read only) and the step-2 plan.

Writes into --out:
  LEDGER.tsv          one row per brief seed: brief line, label as written, seed label, claim
                      id, outcome (label and status now), evidence (CHECK.md rows, errata ids)
  DEFECTS.tsv         one row per defect claim: entry key, part, claim id, paper, label,
                      status, supersedes, locator, errata row
  CHECK_UNJOINED.tsv  the CHECK.md rows that joined no seed, with the reason
  counts.json         counts for the README, the outbox message and the figures
Usage: python3 -I make_ledger.py --db DB --plan-run DIR --out DIR
"""
import argparse
import collections
import csv
import json
import os
import sqlite3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--plan-run", required=True, help="run directory of plan_outcomes.py")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    plan = {int(r["claim_id"]): r for r in
            csv.DictReader(open(os.path.join(a.plan_run, "plan_seeds.tsv"), encoding="utf-8"), delimiter="\t")}
    rows = list(csv.DictReader(open(os.path.join(a.plan_run, "plan_rows.tsv"), encoding="utf-8"), delimiter="\t"))
    seeds = con.execute(
        "SELECT c.claim_id, m.origin_line, m.source_label, c.label, m.status, m.section, c.paper_id, c.track_tags, "
        "m.seed_key, m.status_detail, c.locator FROM claims c JOIN claim_meta m USING(claim_id) "
        "WHERE m.seed_key LIKE 'brief:v2:%' ORDER BY m.origin_line, m.seed_key").fetchall()
    first = {}
    for cid, *_ in seeds:
        ev = con.execute("SELECT to_label FROM claim_events WHERE claim_id=? AND action='seed'", (cid,)).fetchone()
        first[cid] = ev[0] if ev else ""
    os.makedirs(a.out, exist_ok=True)
    cnt = collections.Counter()
    by_sec = collections.defaultdict(collections.Counter)
    with open(os.path.join(a.out, "LEDGER.tsv"), "w") as f:
        f.write("brief_line\tsection\tlabel_as_written\tseed_label\tclaim_id\toutcome\tlabel_now\tstatus_now\t"
                "paper_id\ttracks\tevidence\n")
        for cid, line, src, lab, st, sec, pid, tr, key, det, loc in seeds:
            p = plan.get(cid)
            if lab == "fulltext":
                outcome = "verified"
            elif lab == "refuted":
                outcome = "refuted"
            elif p and p["action"] == "annotate-partial":
                outcome = "annotated, partial"
            elif p:
                outcome = "annotated, located" if first[cid] != "judgement" else "judgement, annotated"
            else:
                outcome = "judgement, no CHECK row" if lab == "judgement" else "open, no CHECK row"
            ev = ""
            if p:
                ev = f"{p['evidence_rows']} [{p['verdicts']}]"
                if p["errata"]:
                    ev += f"; errata {p['errata']} ({p['errata_prov']})"
                if lab == "fulltext":
                    ev += f"; locator {loc}"
            secno = sec.split(".")[0]
            f.write("\t".join(str(x) for x in (line, sec, src, first[cid], cid, outcome, lab, st, pid or "", tr or "",
                                               ev)) + "\n")
            cnt[outcome] += 1
            by_sec[secno][outcome] += 1
    defects = con.execute(
        "SELECT c.claim_id, m.seed_key, c.paper_id, c.label, m.status, c.supersedes, c.locator, m.section "
        "FROM claims c JOIN claim_meta m USING(claim_id) WHERE m.seed_key LIKE 'brief-defect:%' "
        "ORDER BY c.claim_id").fetchall()
    with open(os.path.join(a.out, "DEFECTS.tsv"), "w") as f:
        f.write("entry\tpart\tclaim_id\tpaper_id\tlabel\tstatus\tsupersedes\terrata_row\tlocator\n")
        for cid, key, pid, lab, st, sup, loc, sec in defects:
            _, entry, part = key.split(":")
            f.write("\t".join(str(x) for x in (entry, part, cid, pid, lab, st, sup or "", sec, loc or "")) + "\n")
    with open(os.path.join(a.out, "CHECK_UNJOINED.tsv"), "w") as f:
        f.write("package\tn\tbrief_line\tverdict\treason\terrata_prov\n")
        for r in rows:
            if not r["claim_id"]:
                f.write("\t".join((r["package"], r["n"], r["brief_line"], r["verdict"], r["how"], r["errata_prov"]))
                        + "\n")
    joined = [r for r in rows if r["claim_id"]]
    out = {
        "seeds": len(seeds),
        "seed_labels_at_seeding": dict(collections.Counter(first.values())),
        "seed_labels_now": dict(collections.Counter(s[3] for s in seeds)),
        "seed_status_now": dict(collections.Counter(s[4] for s in seeds)),
        "outcomes": dict(cnt),
        "outcomes_by_section": {k: dict(v) for k, v in sorted(by_sec.items(), key=lambda kv: int(kv[0]))},
        "check_rows": len(rows), "check_rows_joined": len(joined),
        "check_rows_unjoined_by_reason": dict(collections.Counter(r["how"] for r in rows if not r["claim_id"])),
        "check_rows_by_package": {p: {"rows": sum(1 for r in rows if r["package"] == p),
                                      "joined": sum(1 for r in joined if r["package"] == p)}
                                  for p in sorted({r["package"] for r in rows})},
        "defect_claims": len(defects),
        "defect_labels": dict(collections.Counter(d[3] for d in defects)),
        "defect_status": dict(collections.Counter(d[4] for d in defects)),
        "defect_supersedes": sum(1 for d in defects if d[5]),
        "defect_locators": list(con.execute(
            "SELECT count(*), sum(l.resolved) FROM claim_locators l JOIN claim_meta m USING(claim_id) "
            "WHERE m.seed_key LIKE 'brief-defect:%'").fetchone()),
        "seed_locators": list(con.execute(
            "SELECT count(*), sum(l.resolved) FROM claim_locators l JOIN claim_meta m USING(claim_id) "
            "WHERE m.seed_key LIKE 'brief:v2:%'").fetchone()),
    }
    json.dump(out, open(os.path.join(a.out, "counts.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
