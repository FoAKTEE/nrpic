#!/usr/bin/env python3
"""T18 of the work package cosmo-amr: which cases of a repeated test give the same bytes
as the earlier run (prediction: tracks/core/JOURNAL-cosmo-amr.md).

    t18_cmp.py --out DIR OLD_RUN_DIR:NEW_RUN_DIR [...]

Every sub-directory of OLD_RUN_DIR that holds an input deck (*.athinput) and exists in
NEW_RUN_DIR is a case.  Its output files are compared byte by byte; log.txt, status.txt
and the decks (they hold the paths of the run) are skipped.  Writes DIR/t18_summary.json:
per pair and case the number of files compared and the names of those that differ or
are missing."""
import argparse
import filecmp
import glob
import json
import os
import sys

SKIP = ("log.txt", "status.txt")


def files(d):
    out = []
    for root, _, names in os.walk(d):
        for n in names:
            if n in SKIP or n.endswith(".athinput"):
                continue
            out.append(os.path.relpath(os.path.join(root, n), d))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("pairs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for pair in a.pairs:
        old, new = (os.path.abspath(p) for p in pair.split(":"))
        r = {}
        for deck in sorted(glob.glob(os.path.join(old, "*", "*.athinput"))):
            case = os.path.basename(os.path.dirname(deck))
            if not os.path.isdir(os.path.join(new, case)):
                continue
            fo, fn = files(os.path.join(old, case)), files(os.path.join(new, case))
            diff = [f for f in fo if f in fn and not filecmp.cmp(
                os.path.join(old, case, f), os.path.join(new, case, f), shallow=False)]
            miss = sorted(set(fo) ^ set(fn))
            r[case] = {"files": len(fo), "differ": diff, "only_in_one": miss}
        same = [c for c, v in r.items() if not v["differ"] and not v["only_in_one"]]
        other = [c for c in r if c not in same]
        print(f"{os.path.basename(old)} against {os.path.basename(new)}: {len(r)} cases")
        print("  identical:", " ".join(same))
        for c in other:
            print(f"  differs:   {c}: {' '.join(r[c]['differ'])}"
                  + (f"  (only in one: {' '.join(r[c]['only_in_one'])})"
                     if r[c]["only_in_one"] else ""))
        res[f"{os.path.basename(old)}:{os.path.basename(new)}"] = r
    with open(os.path.join(a.out, "t18_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
