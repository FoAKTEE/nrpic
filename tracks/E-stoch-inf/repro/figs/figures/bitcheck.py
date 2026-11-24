"""Bit identity of two dumps in their common variables (scope prediction P1: USF256 against U256ap,
RSF256 against P256v6; ablation P-A3 (i): the t = 0 dumps of the three levels against each other and
against the released runs). Reads one variable at a time (sequential reader of ladder_lib).

Usage: bitcheck.py --out FILE.json  A.dump:B.dump [A.dump:B.dump ...]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402

VARS = ["phi", "Pi", "chi", "K", "alpha", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz",
        "Axx", "Axy", "Axz", "Ayy", "Ayz", "Azz"]


def compare(pa, pb):
    ha, hb = fl.ll.read_header(pa), fl.ll.read_header(pb)
    res = dict(a=pa, b=pb, time_a=ha["time"], time_b=hb["time"], cycle_a=ha["cycle"],
               cycle_b=hb["cycle"], vars={})
    common = [v for v in VARS if v in ha["names"] and v in hb["names"]]
    identical = True
    for v in common:
        _, fa = fl.ll.read_dump(pa, [v])
        _, fb = fl.ll.read_dump(pb, [v])
        a, b = fa[v], fb[v]
        d = np.abs(a - b)
        scale = float(np.max(np.abs(a - a.mean()))) or 1.0
        res["vars"][v] = dict(max_abs=float(d.max()), max_rel_to_pert=float(d.max() / scale),
                              n_diff=int(np.count_nonzero(a != b)))
        identical &= bool(np.array_equal(a, b))
        del fa, fb, a, b, d
    res["bit_identical"] = identical
    res["max_rel_to_pert"] = max(r["max_rel_to_pert"] for r in res["vars"].values())
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("pairs", nargs="+")
    args = ap.parse_args()
    out = []
    for p in args.pairs:
        a, b = p.split(":")
        r = compare(a, b)
        print(os.path.basename(a), os.path.basename(b), "t", r["time_a"], r["time_b"],
              "identical" if r["bit_identical"] else f"max rel {r['max_rel_to_pert']:.3e}",
              flush=True)
        out.append(r)
    with open(args.out, "w") as fp:
        json.dump(out, fp, indent=1)


if __name__ == "__main__":
    main()
