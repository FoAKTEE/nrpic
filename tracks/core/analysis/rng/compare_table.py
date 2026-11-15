#!/usr/bin/env python3
"""Agreement test of the random-number interface.

Reads tables written by the problem generator ``rng_test`` (or by standalone_table.cpp),
recomputes every column with the Python twin ``nrpic.rng`` and compares bit by bit;
compares the tables with each other; and compares the raw words with
``numpy.random.Philox`` (an independent implementation) for a sample of the keys.

Usage: compare_table.py [--numpy N] [--json out.json] table.bin [table2.bin ...]
Exit status 0 only if nothing differs.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import rng  # noqa: E402

INT_COLS = ["word0", "word1", "word2", "word3", "index", "mulhi"]
REAL_COLS = ["uniform0", "uniform1", "uniform2", "uniform3", "normal1", "normal2",
             "dir_x", "dir_y", "dir_z"]


def read_table(path):
    with open(path, "rb") as fp:
        raw = fp.read()
    if raw[:8] != b"NRRNGTB1":
        raise ValueError(f"{path}: bad magic")
    n = int(np.frombuffer(raw, dtype=np.int64, count=1, offset=8)[0])
    off = 16
    keys = np.frombuffer(raw, dtype=np.uint64, count=6 * n, offset=off).reshape(n, 6)
    off += 48 * n
    ints = np.frombuffer(raw, dtype=np.uint64, count=6 * n, offset=off).reshape(n, 6)
    off += 48 * n
    reals = np.frombuffer(raw, dtype=np.float64, count=9 * n, offset=off).reshape(n, 9)
    if off + 72 * n != len(raw):
        raise ValueError(f"{path}: wrong length")
    return keys, ints, reals, hashlib.sha256(raw).hexdigest()


def twin(keys):
    """All columns of the table from the Python twin."""
    kw = dict(seed=keys[:, 0], stream=keys[:, 1], entity=keys[:, 2],
              entity_hi=keys[:, 3], step=keys[:, 4], draw=keys[:, 5])
    w = rng.bits4(**kw)
    ints = np.empty((keys.shape[0], 6), dtype=np.uint64)
    ints[:, :4] = w
    ints[:, 4] = rng.index(n=1000003, **kw)
    ints[:, 5] = rng.mulhi64(w[:, 0], w[:, 1])
    reals = np.empty((keys.shape[0], 9), dtype=np.float64)
    reals[:, :4] = rng.uniform4(**kw)
    z1, z2 = rng.normal2(**kw)
    reals[:, 4] = z1
    reals[:, 5] = z2
    reals[:, 6:] = rng.direction(**kw)
    # the single-value functions are the first members
    assert np.array_equal(rng.bits(**kw), w[:, 0])
    assert np.array_equal(rng.uniform(**kw).view(np.uint64),
                          reals[:, 0].copy().view(np.uint64))
    assert np.array_equal(rng.normal(**kw).view(np.uint64), z1.view(np.uint64))
    return ints, reals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--numpy", type=int, default=10000,
                    help="number of keys compared with numpy.random.Philox")
    ap.add_argument("--json", default="")
    ap.add_argument("tables", nargs="+")
    args = ap.parse_args()

    res = {"tables": {}, "columns": {}, "ok": True}
    keys0 = None
    for path in args.tables:
        keys, ints, reals, sha = read_table(path)
        res["tables"][path] = {"sha256": sha, "nkeys": int(keys.shape[0])}
        if keys0 is None:
            keys0, ints0, reals0, sha0 = keys, ints, reals, sha
        else:
            same = (sha == sha0)
            res["tables"][path]["identical_to_first"] = bool(same)
            if not same:
                res["ok"] = False
                ndiff = int(np.count_nonzero(ints != ints0)
                            + np.count_nonzero(reals.view(np.uint64)
                                               != reals0.view(np.uint64)))
                res["tables"][path]["differing_values"] = ndiff
    n = keys0.shape[0]
    tints, treals = twin(keys0)
    for c, name in enumerate(INT_COLS):
        nd = int(np.count_nonzero(tints[:, c] != ints0[:, c]))
        res["columns"][name] = nd
    tb = np.ascontiguousarray(treals).view(np.uint64)
    cb = np.ascontiguousarray(reals0).view(np.uint64)
    for c, name in enumerate(REAL_COLS):
        nd = int(np.count_nonzero(tb[:, c] != cb[:, c]))
        res["columns"][name] = nd
        if nd:
            res["columns"][name + "_max_abs_diff"] = float(
                np.max(np.abs(treals[:, c] - reals0[:, c])))
    if any(v for k, v in res["columns"].items() if not k.endswith("_diff")):
        res["ok"] = False

    # independent implementation: numpy.random.Philox
    gen = np.random.default_rng(7)
    pick = np.unique(np.concatenate([np.arange(min(n, 2000)),
                                     gen.integers(0, n, size=args.numpy)]))
    nbad = 0
    for i in pick:
        sd, st, en, eh, sp, dr = (int(v) for v in keys0[i])
        ref = rng.numpy_philox_words((en, eh, sp, dr << 8), (sd, st))
        if not np.array_equal(ref, ints0[i, :4]):
            nbad += 1
    res["numpy_philox"] = {"keys": int(pick.size), "differing": nbad}
    if nbad:
        res["ok"] = False

    # properties of the columns
    res["uniform_min"] = float(reals0[:, :4].min())
    res["uniform_max"] = float(reals0[:, :4].max())
    res["normal_abs_max"] = float(np.abs(reals0[:, 4:6]).max())
    res["direction_norm_dev_max"] = float(
        np.abs(np.sum(reals0[:, 6:] ** 2, axis=1) - 1.0).max())
    res["index_max"] = int(ints0[:, 4].max())

    print(json.dumps(res, indent=1))
    if args.json:
        with open(args.json, "w") as fp:
            json.dump(res, fp, indent=1)
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
