#!/usr/bin/env python3
"""Byte comparison of the repeats of T1, T2, T3 with the final executables (source
3f75eb8) against the first runs of those tests (earlier builds of this branch).

    repeat_check.py OLD_RUN NEW_RUN [OLD_RUN NEW_RUN ...]

For every pair: every regular file below OLD_RUN that also exists below NEW_RUN, except
logs, manifests and the copies of the inputs, is compared byte for byte. Writes
repeat_check.json into $NRPIC_RUN_DIR.
"""
import json
import os
import sys

SKIP_SUFFIX = (".log", ".out", ".json", ".athinput", ".csv", ".txt", ".png", ".pdf")


def files(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            if os.path.islink(p) or f.endswith(SKIP_SUFFIX) or f.startswith("exe_"):
                continue
            out[os.path.relpath(p, root)] = p
    return out


def main():
    args = sys.argv[1:]
    res = {}
    for old, new in zip(args[0::2], args[1::2]):
        fo, fn = files(old), files(new)
        both = sorted(set(fo) & set(fn))
        diff = [k for k in both if open(fo[k], "rb").read() != open(fn[k], "rb").read()]
        # a differing file that is equal once the run directory names are masked (the
        # parameter dump of a continued run holds the path of its restart file)
        bo, bn = os.path.basename(old.rstrip("/")).encode(), os.path.basename(new.rstrip("/")).encode()
        masked = [k for k in diff
                  if open(fo[k], "rb").read().replace(bo, b"RUN") == open(fn[k], "rb").read().replace(bn, b"RUN")]
        res[os.path.basename(old) + " vs " + os.path.basename(new)] = {
            "compared": len(both), "differ": diff,
            "equal_with_run_directory_masked": masked,
            "differ_after_masking": [k for k in diff if k not in masked],
            "only_old": sorted(set(fo) - set(fn))[:20], "only_new": sorted(set(fn) - set(fo))[:20]}
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    with open(os.path.join(out, "repeat_check.json"), "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
