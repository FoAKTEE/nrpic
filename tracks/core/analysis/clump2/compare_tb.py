#!/usr/bin/env python3
"""Test M1 of tracks/core/JOURNAL-clump2.md: the static tests TB run with two executables
(the one before and the one after the merge of main) give the same numbers.

    compare_tb.py --a RUN_A/tb --b RUN_B/tb --diag-a A.json --diag-b B.json [--out DIR]

Compares (1) every history file of the cases that both directories hold, byte by byte,
(2) the cell data of every `bin` dump of those cases (the lines before the embedded
parameter dump and the payload after it; the dump itself lists the parameters with their
defaults, which the releases core-v0.4 and core-v0.5 added to), (3) every number
of the two files tb_residual_diag.json (largest relative difference). Writes
compare_tb.json; exit status 0 only if (1) and (2) are identical and (3) is below 1e-12.
"""
import argparse
import glob
import json
import os
import sys

SCR = "/data/haiyangw/nrpic/scratch/core"


def numbers(x, path=""):
    if isinstance(x, dict):
        for k in sorted(x):
            yield from numbers(x[k], f"{path}/{k}")
    elif isinstance(x, (list, tuple)):
        for i, v in enumerate(x):
            yield from numbers(v, f"{path}[{i}]")
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        yield path, float(x)


def payload(path):
    """bytes of a bin dump after its parameter dump (the header gives its size)"""
    with open(path, "rb") as f:
        raw = f.read()
    key = b"header offset="
    i = raw.index(key)
    j = raw.index(b"\n", i)
    n = int(raw[i + len(key):j])
    return raw[:i], raw[j + 1 + n:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--diag-a", required=True)
    ap.add_argument("--diag-b", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    full = lambda p: p if os.path.isabs(p) else os.path.join(SCR, p)  # noqa: E731
    A, B = full(a.a), full(a.b)
    os.makedirs(a.out, exist_ok=True)
    cases = sorted(d for d in os.listdir(B)
                   if os.path.isdir(os.path.join(B, d, "bin")) and os.path.isdir(os.path.join(A, d)))
    res = dict(a=A, b=B, cases={})
    ok = True
    for c in cases:
        r = dict(hst={}, bin={})
        for fb in sorted(glob.glob(os.path.join(B, c, "*.hst"))):
            fa = os.path.join(A, c, os.path.basename(fb))
            same = os.path.exists(fa) and open(fa, "rb").read() == open(fb, "rb").read()
            r["hst"][os.path.basename(fb)] = same
            ok = ok and same
        for fb in sorted(glob.glob(os.path.join(B, c, "bin", "*.bin"))):
            fa = os.path.join(A, c, "bin", os.path.basename(fb))
            if not os.path.exists(fa):
                r["bin"][os.path.basename(fb)] = "missing in a"
                ok = False
                continue
            (ha, pa), (hb, pb) = payload(fa), payload(fb)
            same = ha == hb and pa == pb
            r["bin"][os.path.basename(fb)] = dict(identical=same, bytes=len(pb),
                                                  whole_file=open(fa, "rb").read() == open(fb, "rb").read())
            ok = ok and same
        res["cases"][c] = r
        print(c, "hst", all(r["hst"].values()), "bin",
              all(isinstance(v, dict) and v["identical"] for v in r["bin"].values()), flush=True)
    da = dict(numbers(json.load(open(full(a.diag_a)))))
    db = dict(numbers(json.load(open(full(a.diag_b)))))
    common = sorted(set(da) & set(db))
    worst, where = 0.0, None
    for k in common:
        d = abs(da[k] - db[k]) / max(abs(da[k]), abs(db[k]), 1e-300) if da[k] != db[k] else 0.0
        if d > worst:
            worst, where = d, k
    res["diag"] = dict(numbers_compared=len(common), only_a=len(set(da) - set(db)),
                       only_b=len(set(db) - set(da)), max_rel_diff=worst, where=where)
    ok = ok and worst < 1e-12 and len(common) > 0
    print("diag:", res["diag"])
    res["identical"] = ok
    with open(os.path.join(a.out, "compare_tb.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("M1 IDENTICAL" if ok else "M1 DIFFERENCES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
