"""Test C of the KB-G1 verifier: ten claims of label 'fulltext', read at their locators.

Usage: python3 check_claims.py <outdir>
Writes <outdir>/claims_sample.json (claim text and locators, no paper text) and
<outdir>/claims_excerpts.txt (the source lines at each locator, two lines of context; paper
text: stays in scratch, never committed). The verdicts are written by hand after reading.
"""
import json
import os
import random
import sqlite3
import sys

ROOT = "/data/haiyangw/nrpic/kb-data"
DB = os.path.join(ROOT, "db", "current")
SEED = 20261119
CONTEXT = 2


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    ids = [r[0] for r in c.execute(
        "select claim_id from claims c where label='fulltext' and paper_id is not null and "
        "exists(select 1 from claim_locators l where l.claim_id=c.claim_id) and "
        "not exists(select 1 from claim_locators l where l.claim_id=c.claim_id and l.resolved=0) "
        "order by claim_id").fetchall()]
    pick = sorted(random.Random(SEED).sample(ids, 10))
    sample = []
    lines_out = []
    for cid in pick:
        cl = c.execute("select claim_id, kind, paper_id, locator, text, origin, track_tags, verified_by "
                       "from claims where claim_id=?", (cid,)).fetchone()
        locs = c.execute("select paper_id, version, file, line_start, line_end, written from claim_locators "
                         "where claim_id=? order by ord", (cid,)).fetchall()
        rec = {"claim_id": cl[0], "kind": cl[1], "paper_id": cl[2], "locator": cl[3], "text": cl[4],
               "origin": cl[5], "track": cl[6], "verified_by": cl[7],
               "locators": [dict(zip(("paper_id", "version", "file", "line_start", "line_end", "written"), l))
                            for l in locs]}
        sample.append(rec)
        lines_out.append("=" * 100)
        lines_out.append(f"claim {cl[0]} [{cl[1]}] paper {cl[2]} locator {cl[3]} track {cl[6]}")
        lines_out.append(f"TEXT: {cl[4]}")
        for (pid, ver, fn, a, b, w) in locs:
            path = os.path.join(ROOT, "raw", "arxiv", pid.replace("/", "_"), ver, "src", fn)
            lines_out.append(f"--- {pid} {ver} {fn} L{a}-{b}  ({path})")
            try:
                with open(path, "rb") as f:
                    raw = f.read().decode("utf-8", "replace").split("\n")
            except OSError as e:
                lines_out.append(f"    cannot read: {e}")
                continue
            for i in range(max(1, a - CONTEXT), min(len(raw), b + CONTEXT) + 1):
                mark = ">" if a <= i <= b else " "
                lines_out.append(f"{mark}{i:6d}: {raw[i - 1]}")
    with open(os.path.join(out, "claims_sample.json"), "w") as f:
        json.dump({"seed": SEED, "db": os.path.realpath(DB), "population": len(ids), "claims": sample},
                  f, indent=1)
    with open(os.path.join(out, "claims_excerpts.txt"), "w") as f:
        f.write("\n".join(lines_out) + "\n")
    print(f"population {len(ids)}; picked {pick}")


if __name__ == "__main__":
    main()
