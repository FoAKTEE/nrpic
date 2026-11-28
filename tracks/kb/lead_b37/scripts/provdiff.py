#!/usr/bin/env python3
"""Provenance diff of package claims5 (kb lead, batch 37; the check RISKS.md asks of every lead
review of a claims package).

Opens two snapshots read-only, BEFORE (claims4's last, kb-20261128-fcd969d) and AFTER (claims5's,
kb-20261128-bd57a33), and lists every claim whose claims row, claim_meta row or locator rows
differ, or that is new. Compares that set with the ids claims5's LEDGER.tsv names (read ids and
successors). Writes provdiff.json and a figure into OUTDIR.

    python provdiff.py --out OUTDIR
"""
import argparse
import csv
import hashlib
import json
import os
import sqlite3
import sys

DB = "/data/haiyangw/nrpic/kb-data/db"
BEFORE = os.path.join(DB, "kb-20261128-fcd969d.sqlite")
AFTER = os.path.join(DB, "kb-20261128-bd57a33.sqlite")
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.abspath(os.path.join(HERE, "..", "..", "claims5", "LEDGER.tsv"))


def digest(path):
    c = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    out = {}
    for table, order in (("claims", "claim_id"), ("claim_meta", "claim_id"),
                         ("claim_locators", "claim_id, ord")):
        cur = c.execute(f"SELECT * FROM {table} ORDER BY {order}")
        cols = [d[0] for d in cur.description]
        i = cols.index("claim_id")
        for row in cur:
            h = out.setdefault(row[i], hashlib.sha256())
            h.update((table + repr(row)).encode())
    links = c.execute("SELECT COUNT(*) FROM claim_links").fetchone()[0]
    return {k: v.hexdigest() for k, v in out.items()}, links


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    b, lb = digest(BEFORE)
    f, la = digest(AFTER)
    new = sorted(set(f) - set(b))
    gone = sorted(set(b) - set(f))
    changed = sorted(k for k in set(b) & set(f) if b[k] != f[k])
    with open(LEDGER) as fh:
        led = list(csv.DictReader(fh, delimiter="\t"))
    read = {int(r["claim_id"]) for r in led}
    succ = set()
    for r in led:
        for s in (r.get("successor") or "").replace(";", ",").replace("+", ",").split(","):
            s = s.strip()
            if s.isdigit():
                succ.add(int(s))
    named = read | succ
    touched = set(new) | set(changed)
    res = {"before": os.path.basename(BEFORE), "after": os.path.basename(AFTER),
           "claims_before": len(b), "claims_after": len(f), "new": new, "gone": gone,
           "n_changed_existing": len(changed), "links_before": lb, "links_after": la,
           "ledger_read": len(read), "ledger_successors": sorted(succ),
           "touched_not_in_ledger": sorted(touched - named),
           "ledger_read_not_touched": sorted(read - touched),
           "successors_existing_changed": sorted(succ & set(changed))}
    with open(os.path.join(a.out, "provdiff.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    sys.path.insert(0, HERE)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    lab = ["unchanged", "changed, in ledger", "changed, not in ledger", "new"]
    unchanged = len(set(b) & set(f)) - len(changed)
    inled = len(set(changed) & named)
    vals = [unchanged, inled, len(set(changed) - named), len(new)]
    fig, ax = plt.subplots(figsize=(figstyle.COLUMN_WIDTH + 0.6, 2.6))
    cols = ["grey", figstyle.PAL["blue"], figstyle.PAL["red"], figstyle.PAL["green"]]
    ax.barh(range(4), vals, color=cols)
    for i, v in enumerate(vals):
        ax.text(v + 8, i, str(v), va="center", fontsize=8)
    ax.set_yticks(range(4))
    ax.set_yticklabels(lab, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, max(vals) * 1.15)
    ax.set_xlabel("claims (fcd969d -> bd57a33)")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out, f"fig_provdiff.{ext}"), dpi=160)


if __name__ == "__main__":
    main()
