"""M1: per-dump diagnostics of the crossed-wave runs with vlib (own reader, TT, gauge piece).

Usage: python m1_measure.py [--gauge] [--kinds bin,dbin,rst] [--workers N] name=dir ...
Writes <NRPIC_RUN_DIR>/m1_<name>.json with one row per dump (kind, file, sha256 of the first
MiB and the size, the vlib.measure() numbers).
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", "/data/haiyangw/nrpic/scratch/B-emd-gw/tmp/m1")


def files(d, kind):
    if kind == "bin":
        return sorted(glob.glob(os.path.join(d, "bin", "cw.z4c.*.bin")))
    if kind == "dbin":
        return sorted(glob.glob(os.path.join(d, "bin", "cw.z4cd.*.bin")))
    if kind == "rst":
        return sorted(glob.glob(os.path.join(d, "rst", "cw.*.rst")))
    raise ValueError(kind)


def one(args):
    path, kind, gauge = args
    t0 = time.time()
    try:
        dd = vlib.read_rst(path) if kind == "rst" else vlib.read_bin(path)
        r = vlib.measure(dd, energies=True, spectrum=True, gauge=gauge)
    except Exception as e:  # keep the failure on record
        return {"file": path, "kind": kind, "error": repr(e)}
    with open(path, "rb") as f:
        head = f.read(1 << 20)
    r.update({"file": path, "kind": kind, "size": os.path.getsize(path),
              "sha256_head": hashlib.sha256(head).hexdigest(), "sec": time.time() - t0})
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gauge", action="store_true")
    ap.add_argument("--kinds", default="bin,dbin")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("cases", nargs="+")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for c in a.cases:
        name, d = c.split("=", 1)
        jobs = [(p, k, a.gauge) for k in a.kinds.split(",") for p in files(d, k)]
        with ProcessPoolExecutor(a.workers) as ex:
            rows = list(ex.map(one, jobs, chunksize=2))
        rows.sort(key=lambda r: (r["kind"], r.get("time", -1)))
        with open(os.path.join(OUT, f"m1_{name}.json"), "w") as f:
            json.dump({"case": name, "dir": d, "kinds": a.kinds, "gauge": a.gauge, "rows": rows}, f, default=float)
        nerr = sum("error" in r for r in rows)
        print(f"{name}: {len(rows)} dumps, {nerr} errors", flush=True)


if __name__ == "__main__":
    main()
