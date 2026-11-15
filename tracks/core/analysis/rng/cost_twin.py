#!/usr/bin/env python3
"""Cost per call of the Python twin nrpic.rng (NumPy, one core): fastest of three
evaluations of 2^20 keys per function. Writes cost_twin.json in the current directory.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import rng  # noqa: E402


def main():
    n = 1 << 20
    key = dict(seed=20261115, stream=rng.stream(rng.STREAM_TESTS, 4),
               entity=np.arange(n, dtype=np.uint64), step=7, draw=0)
    funcs = {"bits4": rng.bits4, "uniform": rng.uniform, "uniform4": rng.uniform4,
             "index": lambda **k: rng.index(n=1000003, **k), "normal2": rng.normal2,
             "direction": rng.direction}
    res = {"keys": n}
    for name, f in funcs.items():
        best = 1e30
        for _ in range(3):
            t0 = time.perf_counter()
            f(**key)
            best = min(best, time.perf_counter() - t0)
        res[name + "_ns_per_call"] = round(1e9 * best / n, 1)
    with open("cost_twin.json", "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
