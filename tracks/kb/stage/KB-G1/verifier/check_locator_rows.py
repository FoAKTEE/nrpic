"""Follow-up of test C (claim 25): for every claim with a locator string, compare the number
of ';'-separated locators in claims.locator with the rows in claim_locators.

Usage: python3 check_locator_rows.py <outdir>   (writes <outdir>/locator_rows.json)
"""
import json
import os
import re
import sqlite3
import sys

DB = "/data/haiyangw/nrpic/kb-data/db/current"


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = c.execute("select claim_id, label, locator from claims where locator is not null").fetchall()
    bad = []
    for cid, lab, loc in rows:
        parts = [p for p in re.split(r";\s*", loc) if p.strip()]
        k = c.execute("select count(*) from claim_locators where claim_id=?", (cid,)).fetchone()[0]
        if len(parts) != k:
            bad.append({"claim_id": cid, "label": lab, "locators_in_string": len(parts),
                        "rows": k, "locator": loc})
    unresolved = c.execute("select count(*) from claim_locators where resolved=0").fetchone()[0]
    res = {"claims_with_locator": len(rows), "mismatch": bad, "unresolved_rows": unresolved}
    json.dump(res, open(os.path.join(out, "locator_rows.json"), "w"), indent=1)
    print(f"{len(rows)} claims with a locator string; {len(bad)} with fewer or more rows: "
          f"{[(b['claim_id'], b['locators_in_string'], b['rows']) for b in bad]}; "
          f"unresolved locator rows {unresolved}")


if __name__ == "__main__":
    main()
