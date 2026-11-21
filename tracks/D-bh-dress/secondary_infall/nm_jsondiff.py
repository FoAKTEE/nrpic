#!/usr/bin/env python3
"""Regression check of an analysis script: compare two nm_analysis.json files (the same run
analysed by two versions of nm_analyze.py). Every numeric leaf present in both (lists
compared element by element up to the shorter length, because the wave-3 bins extend the
wave-2 bins) is compared; prints the largest absolute and relative differences, the
leaves that differ beyond --tol, and the keys present in only one file.

Usage: python3 nm_jsondiff.py OLD.json NEW.json --label N128Lc [--tol 1e-12] [--out DIR]
"""
import argparse
import json
import math
import os


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out["only_new"].append(f"{path}/{k}")
            elif k not in b:
                out["only_old"].append(f"{path}/{k}")
            else:
                walk(a[k], b[k], f"{path}/{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out["length_differs"].append(f"{path}: {len(a)} -> {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if (isinstance(a, float) and math.isnan(a)) or (isinstance(b, float) and math.isnan(b)):
            if not ((isinstance(a, float) and math.isnan(a)) and (isinstance(b, float) and math.isnan(b))):
                out["diff"].append((path, a, b, float("inf")))
            return
        d = abs(b - a)
        r = d / max(abs(a), 1e-300) if a != 0 else (0.0 if b == 0 else float("inf"))
        out["n"] += 1
        out["max_abs"] = max(out["max_abs"], d)
        out["max_rel"] = max(out["max_rel"], r if math.isfinite(r) else 0.0)
        if d > out["tol"] * max(abs(a), 1.0):
            out["diff"].append((path, a, b, r))
    else:
        if a != b and not (a is None and b is None):
            out["other"].append(f"{path}: {a!r} -> {b!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--label", required=True)
    ap.add_argument("--tol", type=float, default=1e-12)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    A = json.load(open(a.old))[a.label]
    B = json.load(open(a.new))[a.label]
    out = dict(n=0, max_abs=0.0, max_rel=0.0, tol=a.tol, diff=[], only_old=[], only_new=[],
               length_differs=[], other=[])
    walk(A, B, a.label, out)
    lines = [f"compared numeric leaves: {out['n']}; largest abs diff {out['max_abs']:.3e}, "
             f"largest rel diff {out['max_rel']:.3e}; beyond tol {a.tol:g}: {len(out['diff'])}",
             f"keys only in old: {len(out['only_old'])}; only in new: {len(out['only_new'])}; "
             f"lists of different length: {len(out['length_differs'])}; other differences: {len(out['other'])}"]
    lines += ["  DIFF " + f"{p}: {x!r} -> {y!r} (rel {r:.3e})" for p, x, y, r in out["diff"][:60]]
    lines += ["  ONLY_OLD " + s for s in out["only_old"][:40]]
    lines += ["  ONLY_NEW " + s for s in out["only_new"][:40]]
    lines += ["  LENGTH " + s for s in out["length_differs"][:40]]
    lines += ["  OTHER " + s for s in out["other"][:40]]
    txt = "\n".join(lines) + "\n"
    print(txt)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, f"jsondiff_{a.label}.txt"), "w") as f:
            f.write(txt)


if __name__ == "__main__":
    main()
