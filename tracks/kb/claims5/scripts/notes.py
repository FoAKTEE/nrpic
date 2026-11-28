#!/usr/bin/env python3
"""claims5: one information note per citing owner: which of the claims it cites changed and how,
with the places in its files where each claim is cited (claims4's order.tsv, column cited_by).

    python3 -I notes.py --order ORDER_RUN_DIR --apply APPLY_RUN_DIR --out DIR

Reads work/verdicts_T.tsv, the apply run's result.json (successor ids) and plans/P1_claims5.json
(extended locators); reads the successor texts from the database read-only. Writes
DIR/NOTE_<owner>.md. Standard library only.
"""
import argparse
import csv
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
DB = "/data/haiyangw/nrpic/kb-data/db/kb.sqlite"
HOW = {"fragment": "a fragment of a note row (subject or predicate cut away)",
       "wrong_label": "a track's reading or verdict stored as a paper statement",
       "wrong": "says more than, or other than, the source",
       "part_unsupported": "one part is not at its locator or is not a statement of the paper"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True)
    ap.add_argument("--apply", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(PKG, "work", "verdicts_T.tsv")) as f:
        rows = {int(r["claim_id"]): r for r in csv.DictReader(f, delimiter="\t")}
    meta = {}
    with open(os.path.join(a.order, "order.tsv")) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            meta[int(r["claim_id"])] = r
    res = json.load(open(os.path.join(a.apply, "result.json")))
    succ = {x["id"]: x["new"] for x in res["results"] if x["do"] == "supersede"}
    plan = json.load(open(os.path.join(PKG, "plans", "P1_claims5.json")))
    newloc = {x["id"]: x["locator"] for x in plan["actions"] if x["do"] == "verify" and x.get("locator")}
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    def text(cid):
        r = con.execute("SELECT c.text, c.label FROM claims c WHERE claim_id=?", (cid,)).fetchone()
        return r if r else ("?", "?")

    by_owner = {}
    for cid, r in rows.items():
        for c in meta[cid]["cited_by"].split(";"):
            if not c:
                continue
            owner, path, line = c.split(":", 2)
            by_owner.setdefault(owner, {}).setdefault(cid, []).append(f"{path}:{line}")
    for owner, cids in sorted(by_owner.items()):
        changed = [c for c in sorted(cids) if rows[c]["right"] == "0"]
        relocated = [c for c in sorted(cids) if c in newloc]
        verified = [c for c in sorted(cids) if rows[c]["right"] == "1"]
        L = [f"# Information note (kb, package claims5, 2026-11-27) to {owner}: cited claims that changed", "",
             "Package claims5 read at their sources all 131 machine-located claims that a track cites and that "
             "nobody had read (class T of claims4; with claims4's 13 the class is now read in full). Writes: run "
             "kb-20261128-024327-81f35d6 (dry run kb-20261128-024311-9e8af45 identical); rates run "
             "kb-20261128-024452-cfc4954; snapshot kb-20261128-bd57a33 (run kb-20261128-024540-477cbc9). "
             "Ledger: tracks/kb/claims5/LEDGER.tsv on kb/main. Places are the citing lines found by the claims4 "
             "classifier on your branch at 2026-11-27 17:05 PST (`git show <branch>:<path>`).", ""]
        if changed:
            L += [f"## Superseded ({len(changed)}): quote the successor id where your files cite the old one", ""]
            for c in changed:
                r = rows[c]
                new = succ.get(c)
                t, lab = text(new) if new else ("?", "?")
                old, _ = text(c)
                L.append(f"- **{c} -> {new}** ({r['verdict']}: {HOW.get(r['verdict'], r['verdict'])}). Old: "
                         f"\"{old[:150]}{'...' if len(old) > 150 else ''}\". New [{lab}]: \"{t}\". Why: {r['note']}. "
                         f"Cited at: {', '.join(sorted(set(cids[c])))}.")
            L.append("")
        else:
            L += ["## Superseded: none of the claims you cite.", ""]
        if relocated:
            L += ["## Verified with an extended locator (text unchanged)", ""]
            for c in relocated:
                L.append(f"- {c}: locator now {newloc[c]}. Cited at: {', '.join(sorted(set(cids[c])))}.")
            L.append("")
        L += [f"## Verified as worded ({len(verified)}; text unchanged, status now checked)", "",
              ", ".join(str(c) for c in verified) if verified else "none", "",
              "No action is needed for verified claims. Borderline ones (noun phrases, locator debris left in "
              "the text) are verified as they stand; LEDGER.tsv marks them.", ""]
        with open(os.path.join(a.out, f"NOTE_{owner}.md"), "w") as f:
            f.write("\n".join(L))
        print(owner, "cites", len(cids), "changed", len(changed), "relocated", len(relocated))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
