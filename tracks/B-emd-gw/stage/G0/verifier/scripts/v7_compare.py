"""Compare the rerun outputs of v7_track_tests.sh with the results committed by the track.

    python3 v7_compare.py TRACKDIR RUNDIR

Walks both JSON trees and reports, per file, the number of numeric leaves compared, the
largest relative difference and the keys that differ by more than 1e-9 relative.
"""
import json
import os
import sys


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    elif isinstance(o, bool) or o is None or isinstance(o, str):
        yield path, o
    elif isinstance(o, (int, float)):
        yield path, float(o)


def compare(a, b):
    la, lb = dict(leaves(a)), dict(leaves(b))
    n, worst, bad, missing = 0, 0.0, [], []
    for k, va in la.items():
        if k not in lb:
            missing.append(k)
            continue
        vb = lb[k]
        if isinstance(va, float) and isinstance(vb, float):
            n += 1
            d = abs(va - vb)/max(abs(va), abs(vb), 1e-300)
            if d > worst:
                worst = d
            if d > 1e-9 and abs(va - vb) > 1e-14:
                bad.append((k, va, vb, d))
        elif va != vb and not k.endswith("figure") and "png" not in str(va):
            bad.append((k, va, vb, None))
    return n, worst, bad, missing


def main():
    T, R = sys.argv[1], sys.argv[2]
    pairs = [("scope/results/check_item3.json", "scope/check_item3.json", None),
             ("scope/results/crossed_waves_tt.json", "scope/crossed_waves_tt.json", None),
             ("scope/results/regime_estimates.json", "scope/regime_estimates.json", None),
             ("baseline/results/baseline_results.json", "baseline/baseline_results.json",
              ("T1", "T2"))]
    for ref, new, keys in pairs:
        pr, pn = os.path.join(T, ref), os.path.join(R, new)
        if not (os.path.exists(pr) and os.path.exists(pn)):
            print(f"{ref}: missing ({os.path.exists(pr)}, {os.path.exists(pn)})")
            continue
        a, b = json.load(open(pr)), json.load(open(pn))
        if keys:
            a = {k: a.get(k) for k in keys}
            b = {k: b.get(k) for k in keys}
        n, worst, bad, missing = compare(a, b)
        print(f"{ref}: {n} numbers, largest relative difference {worst:.3e}, "
              f"{len(bad)} differing, {len(missing)} missing in rerun")
        for row in bad[:15]:
            print("   ", row)
        for m in missing[:5]:
            print("    missing:", m)


if __name__ == "__main__":
    main()
