#!/usr/bin/env python3
"""Parameter-by-parameter comparison of the prepared rerun input
problems/jeans/jeans_mc.athinput with what run jeans/n1e4_v19 actually used: its
chain/input.athinput with the command-line overrides of chain/config.sh applied.

    check_jeans_mc_input.py [--out FILE.json]

Prints every parameter that is added, removed or changed (block/name: old -> new) and
exit status 0 only if the differences are exactly the expected ones: the six clump
momenta comp1_p1..3, comp2_p1..3 added (equal to the momenta that test T5 used) and
the free text of <comment>. Values are compared as numbers where both parse as numbers
(so 80 and 80.0 agree), else as strings. Standard library only.
"""
import argparse
import json
import re
import sys

V19 = "/data/haiyangw/nrpic/runs/jeans/n1e4_v19"
NEW = "problems/jeans/jeans_mc.athinput"
EXPECTED_ADDED = {f"problem/comp{c}_p{k}" for c in (1, 2) for k in (1, 2, 3)}
FREE_TEXT = {"comment/problem"}


def parse(path):
    """athinput -> {block/name: value}, comments and blank lines dropped."""
    out, block = {}, None
    with open(path) as f:
        for line in f:
            s = line.split("#", 1)[0].strip()
            if not s:
                continue
            m = re.fullmatch(r"<\s*([^>]+?)\s*>", s)
            if m:
                block = m.group(1)
                continue
            if "=" not in s or block is None:
                continue
            k, v = s.split("=", 1)
            out[f"{block}/{k.strip()}"] = v.strip()
    return out


def overrides():
    with open(f"{V19}/chain/config.sh") as f:
        args = re.search(r"EXTRA_ARGS=\((.*)\)", f.read()).group(1).split()
    return dict(a.split("=", 1) for a in args)


def same(a, b):
    try:
        return float(a) == float(b)
    except ValueError:
        return a == b


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    a = ap.parse_args()
    old = parse(f"{V19}/chain/input.athinput")
    ov = overrides()
    missing = sorted(k for k in ov if k not in old)
    old.update(ov)
    new = parse(NEW)
    added = sorted(k for k in new if k not in old)
    removed = sorted(k for k in old if k not in new)
    changed = sorted(k for k in new if k in old and not same(old[k], new[k]))
    for k in added:
        print(f"added    {k} = {new[k]}")
    for k in removed:
        print(f"removed  {k} (was {old[k]})")
    for k in changed:
        print(f"changed  {k}: {old[k]} -> {new[k]}")
    if missing:
        print("overrides of the run without a parameter in its input file:", missing)
    ok = (set(added) == EXPECTED_ADDED and not removed and set(changed) <= FREE_TEXT
          and not missing)
    rep = dict(reference=f"{V19}/chain/input.athinput + chain/config.sh EXTRA_ARGS",
               new=NEW, parameters_reference=len(old), parameters_new=len(new),
               added={k: new[k] for k in added}, removed=removed,
               changed={k: [old[k], new[k]] for k in changed}, overrides=len(ov),
               only_expected_differences=ok)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(rep, f, indent=1)
    print(f"{len(old)} parameters in the run, {len(new)} in the prepared input; "
          + ("ONLY THE EXPECTED DIFFERENCES" if ok else "UNEXPECTED DIFFERENCES"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
