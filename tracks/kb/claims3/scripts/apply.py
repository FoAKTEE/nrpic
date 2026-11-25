#!/usr/bin/env python3
"""Apply one plan of claim actions of package claims3 to the working database, in one
transaction inside the kb writer lock (locks/kb-writer.lock), with a before/after record.

    python3 -I apply.py PLAN.json [--out DIR] [--dry-run]

PLAN.json: {"by": "kb-claims3", "actions": [ {...}, ... ]}, each action one of
  {"do": "verify",     "id": N, "evidence": E, ["locator": L]}       verify (+ locator rows)
  {"do": "relocate",   "id": N, "locator": L, "evidence": E}          locator rows only
  {"do": "supersede",  "id": N, "evidence": E, "text": T, "label": L, "locator": L, ["kind", "paper", "track"]}
  {"do": "supersede",  "id": N, "evidence": E, "to": M}               (M may be "@k": the claim made by action k)
  {"do": "withdraw",   "id": N, "evidence": E}
  {"do": "annotate",   "id": N, "evidence": E}                         event only, label and status kept
  {"do": "add",        "text": T, "label": L, "kind": K, "paper": P, "locator": L, "track": T, "evidence": E}
Writes DIR/before.tsv, DIR/after.tsv (id, label, status, locator rows resolved/total, links) for
every claim touched or created, DIR/others.json (a hash of all other claim rows, before and
after: they must agree), DIR/result.json (what each action did). Refuses to run outside
nrpic-run unless --out is given. Nothing under kb-data/raw is executed or imported; the
store is read as text by kbtool.claims_check.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "kb"))

from kbtool import claims_brief as cb  # noqa: E402
from kbtool import claims_cli  # noqa: E402
from kbtool import claims_db as cdb  # noqa: E402
from kbtool.lock import writer_lock  # noqa: E402
from kbtool.paths import layout  # noqa: E402


def state(con, cid):
    r = con.execute("SELECT c.label, m.status, c.locator FROM claims c JOIN claim_meta m USING(claim_id) "
                    "WHERE claim_id=?", (cid,)).fetchone()
    if not r:
        return None
    n, ok = con.execute("SELECT count(*), coalesce(sum(resolved),0) FROM claim_locators WHERE claim_id=?",
                        (cid,)).fetchone()
    ln = ";".join(f"{l['from_id']}->{l['to_id']}:{l['relation']}" for l in cdb.links(con, cid))
    return {"claim_id": cid, "label": r[0], "status": r[1], "locator": r[2] or "", "loc_rows": n,
            "loc_resolved": ok, "links": ln}


def others_hash(con, ids):
    h = hashlib.sha256()
    q = ("SELECT c.claim_id, c.text, c.label, c.locator, m.status, m.evidence FROM claims c JOIN claim_meta m "
         "USING(claim_id) ORDER BY c.claim_id")
    n = 0
    for row in con.execute(q):
        if row[0] in ids:
            continue
        h.update(json.dumps(row, default=str).encode())
        n += 1
    return {"rows": n, "sha256": h.hexdigest()}


def annotate(con, cid, by, evidence):
    if cb.own_claim(con, cid):
        return cb.annotate(con, cid, by, evidence)
    r = con.execute("SELECT c.label, m.status FROM claims c JOIN claim_meta m USING(claim_id) WHERE claim_id=?",
                    (cid,)).fetchone()
    if not r:
        raise KeyError(cid)
    cdb.event(con, cid, by, "annotate", r[0], r[0], r[1], r[1], evidence)
    return True


def write_tsv(path, rows):
    cols = ("claim_id", "label", "status", "loc_rows", "loc_resolved", "links", "locator")
    with open(path, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not a.out:
        ap.error("no output directory (run under nrpic-run or give --out)")
    os.makedirs(a.out, exist_ok=True)
    plan = json.load(open(a.plan))
    by = plan["by"]
    acts = plan["actions"]
    lay = layout()
    touched = sorted({x["id"] for x in acts if "id" in x} |
                     {x["to"] for x in acts if isinstance(x.get("to"), int)})
    results, made = [], {}
    with writer_lock(lay, what="claims3 apply"):
        con = cdb.connect(lay.db_work)
        try:
            cdb.ensure(con)
            before = [s for s in (state(con, c) for c in touched) if s]
            oh_before = others_hash(con, set(touched))
            store = claims_cli._store(lay, con)
            con.execute("BEGIN")
            for k, x in enumerate(acts):
                do = x["do"]
                cid = x.get("id")
                ev = x.get("evidence", "")
                if do == "verify":
                    cdb.verify(con, cid, by, ev, x.get("locator"))
                    out = cdb.relocate(con, cid, x["locator"], store, by, "verify") if x.get("locator") else None
                    if out and out[1] != out[0]:
                        raise ValueError(f"action {k}: claim {cid}: {out[0] - out[1]} locator rows do not resolve")
                    results.append({"k": k, "do": do, "id": cid, "rows": out})
                elif do == "relocate":
                    out = cdb.relocate(con, cid, x["locator"], store, by, ev)
                    results.append({"k": k, "do": do, "id": cid, "rows": out})
                elif do == "supersede":
                    to = x.get("to")
                    if isinstance(to, str) and to.startswith("@"):
                        to = made[int(to[1:])]
                    new = cdb.supersede(con, cid, by, ev, text=x.get("text"), to=to, label=x.get("label", "fulltext"),
                                        kind=x.get("kind"), paper_id=x.get("paper"), locator=x.get("locator"),
                                        track=x.get("track"), origin=x.get("origin", "tracks/kb/claims3"),
                                        store=store)
                    made[k] = new
                    results.append({"k": k, "do": do, "id": cid, "new": new})
                elif do == "withdraw":
                    cdb.withdraw(con, cid, by, ev)
                    results.append({"k": k, "do": do, "id": cid})
                elif do == "annotate":
                    results.append({"k": k, "do": do, "id": cid, "written": annotate(con, cid, by, ev)})
                elif do == "add":
                    new = cdb.add_claim(con, x["text"], x.get("kind", "result"), x.get("paper"), x.get("locator"),
                                        x["label"], by, x.get("origin", "tracks/kb/claims3"), x.get("track", "kb"), ev)
                    out = cdb.relocate(con, new, x["locator"], store, by, "add") if x.get("locator") else None
                    if out and out[1] != out[0]:
                        raise ValueError(f"action {k}: new claim: {out[0] - out[1]} locator rows do not resolve")
                    made[k] = new
                    results.append({"k": k, "do": do, "new": new, "rows": out})
                else:
                    raise ValueError(f"action {k}: unknown action {do!r}")
            new_ids = sorted(set(made.values()))
            after = [s for s in (state(con, c) for c in sorted(set(touched) | set(new_ids))) if s]
            oh_after = others_hash(con, set(touched) | set(new_ids))
            if a.dry_run:
                con.rollback()
            else:
                con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
    write_tsv(os.path.join(a.out, "before.tsv"), before)
    write_tsv(os.path.join(a.out, "after.tsv"), after)
    agree = oh_before == oh_after
    json.dump({"before": oh_before, "after": oh_after, "agree": agree}, open(os.path.join(a.out, "others.json"), "w"),
              indent=1)
    json.dump({"plan": a.plan, "dry_run": a.dry_run, "results": results, "new_claims": new_ids},
              open(os.path.join(a.out, "result.json"), "w"), indent=1)
    print(json.dumps({"actions": len(results), "new_claims": new_ids, "others_unchanged": agree,
                      "dry_run": a.dry_run}))
    return 0 if agree else 3


if __name__ == "__main__":
    raise SystemExit(main())
