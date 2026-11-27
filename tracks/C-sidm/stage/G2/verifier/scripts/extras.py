#!/usr/bin/env python3
"""Verifier's further checks X.1-X.5 (block A controls, D2 control band, NS.1 at 400 M, the
guard stop of D2eta1), with the readers of fates.py (self-test run first)."""
import argparse
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fates  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"self_test": fates.self_test(os.path.join(a.out, "selftest"))}
    if not res["self_test"]["ok"]:
        sys.exit(1)
    runs = {"A344s1c": "C-20261122-213602-729aeed", "A324s1c": "C-20261123-032324-938ecbd",
            "A334s1c": "C-20261121-214601-40dc927", "N6c": "C-20261124-221122-928c9eb",
            "D2ctl": "C-20261122-103854-4670b59", "A334s2c": "C-20261124-053105-2fcc8af",
            "A334s3c": "C-20261124-082221-7f03a8e"}
    for k, rid in runs.items():
        h, nr = fates.read_hist(os.path.join(fates.run_dir(rid), "cc.nrpic.hst"))
        t, amin, ac = h[:, 0], h[:, 15], h[:, 12]
        tc, _ = fates.crossing(t, amin)
        d = ac - ac[0]
        r = dict(run=rid, restarts=nr, t_end=float(t[-1]), t_cross=tc)
        for lo, hi in ((280, 300), (380, 400), (390, 410), (400, 420), (500, 600)):
            m = (t >= lo) & (t < hi) if hi < t[-1] + 1e-9 else (t >= lo) & (t <= hi)
            if m.any():
                r[f"mean_dalpha_c_{lo}_{hi}"] = float(d[m].mean())
        res[k] = r
        print(k, json.dumps(r))
    # guard stop of D2eta1
    chain = os.path.join(fates.run_dir("C-20261126-034500-4b34b1c"), "chain")
    ev = open(os.path.join(chain, "events.log")).read()
    log = open(os.path.join(chain, "seg001.job5350.a1.log"), errors="replace").read()
    m = re.search(r"NRPIC guard: the run stops at time ([0-9.eE+-]+)", log)
    res["D2eta1_guard"] = dict(status_line=[ln for ln in ev.splitlines() if "STATUS" in ln],
                               guard_time=float(m.group(1)) if m else None,
                               reason=re.search(r"reason: (.*)", log).group(1) if "reason:" in log else None)
    print(res["D2eta1_guard"])
    json.dump(res, open(os.path.join(a.out, "extras.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
