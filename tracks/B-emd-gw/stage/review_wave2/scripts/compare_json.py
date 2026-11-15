"""Compare pairs of JSON files leaf by leaf: compare_json.py A1 B1 [A2 B2 ...].
Prints per pair the number of numeric leaves, the largest relative difference and every
non-numeric leaf that differs."""
import json
import math
import sys


def leaves(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, x


def main():
    args = sys.argv[1:]
    worst_all = 0.0
    for a, b in zip(args[::2], args[1::2]):
        A = dict(leaves(json.load(open(a))))
        B = dict(leaves(json.load(open(b))))
        n, worst, wkey, other = 0, 0.0, None, []
        for k in sorted(set(A) | set(B)):
            u, v = A.get(k), B.get(k)
            if isinstance(u, (int, float)) and isinstance(v, (int, float)) and not isinstance(u, bool):
                n += 1
                if math.isnan(u) and math.isnan(v):
                    continue
                d = abs(u - v) / max(abs(u), abs(v), 1e-300)
                if d > worst:
                    worst, wkey = d, k
            elif u != v:
                other.append((k, u, v))
        worst_all = max(worst_all, worst)
        print(f"{b}: {n} numeric leaves, largest relative difference {worst:.3e} at {wkey}; "
              f"{len(other)} other leaves differ")
        for k, u, v in other[:10]:
            print(f"   {k}: {str(u)[:60]} | {str(v)[:60]}")
    print(f"largest relative difference over all pairs: {worst_all:.3e}")


if __name__ == "__main__":
    main()
