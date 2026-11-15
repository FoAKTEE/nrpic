#!/usr/bin/env python3
"""Run a list of AthenaK cases on processors, one registered run per case.

    python3 launch.py CASES.json [-P 8] [--only NAME ...] [--dry]

CASES.json: list of {"name", "input", "overrides": [block/par=value ...],
"purpose", "kind": "scouting"|"production", "extra_inputs": [paths], "set"}.
For every case: run id B-emd-gw-<UTC YYYYMMDD-HHMMSS>-<commit7> (one second apart),
output directory scratch/B-emd-gw/<run_id>/, manifest
tracks/B-emd-gw/runs/<run_id>/manifest.json written before the start (status
"running") and completed after the end (wall time, exit status). The executable is the
processor build of the main checkout, read-only (CLAUDE.md, "Machine").
One core per case (Kokkos Serial build); OMP_NUM_THREADS=1.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/B-emd-gw"
RUNS = os.path.join(WT, "tracks", "B-emd-gw", "runs")
EXE = "/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena"
_lock = threading.Lock()
_hash_cache = {}


def sha256(path):
    path = os.path.abspath(path)
    st = os.stat(path)
    key = (path, st.st_mtime, st.st_size)
    if key not in _hash_cache:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        _hash_cache[key] = h.hexdigest()
    return _hash_cache[key]


def git(*args):
    return subprocess.check_output(["git", "-C", WT] + list(args), text=True).strip()


def new_run_id(commit7):
    with _lock:
        rid = None
        while True:
            stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
            rid = f"B-emd-gw-{stamp}-{commit7}"
            if not os.path.exists(os.path.join(RUNS, rid)):
                os.makedirs(os.path.join(RUNS, rid))
                return rid
            time.sleep(0.3)


def write_manifest(rid, man):
    with open(os.path.join(RUNS, rid, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
        f.write("\n")


def run_case(case, commit, dirty, exe_hash, dry):
    rid = new_run_id(commit[:7])
    out = os.path.join(SCRATCH, rid)
    os.makedirs(out, exist_ok=True)
    inp = os.path.abspath(os.path.join(HERE, case["input"]))
    cmd = [EXE, "-i", inp, "-d", out] + case.get("overrides", [])
    inputs = [{"path": os.path.relpath(inp, WT), "sha256": sha256(inp)},
              {"path": EXE, "sha256": exe_hash}]
    for p in case.get("extra_inputs", []):
        inputs.append({"path": p, "sha256": sha256(p)})
    man = {"run_id": rid, "name": case["name"], "set": case.get("set", ""),
           "command": " ".join(cmd), "cwd": out, "commit": commit,
           "worktree_dirty": dirty, "inputs": inputs, "output_dir": out,
           "purpose": case["purpose"], "kind": case.get("kind", "scouting"),
           "cores": 1, "card_hours": 0.0, "env": {"OMP_NUM_THREADS": "1"},
           "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "status": "running"}
    write_manifest(rid, man)
    if dry:
        man["status"] = "dry"
        write_manifest(rid, man)
        return rid, 0, 0.0
    env = dict(os.environ, OMP_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(out, "athena.log"), "w") as log:
        rc = subprocess.call(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT, env=env)
    wall = time.time() - t0
    man.update(status="done" if rc == 0 else f"failed (exit {rc})",
               wall_time_s=round(wall, 1),
               finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               core_hours=round(wall/3600.0, 4))
    write_manifest(rid, man)
    return rid, rc, wall


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases")
    ap.add_argument("-P", type=int, default=8)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    with open(a.cases) as f:
        cases = json.load(f)
    if a.only:
        cases = [c for c in cases if c["name"] in a.only]
    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--", "tracks/B-emd-gw/periodic_z4c"))
    exe_hash = sha256(EXE)
    index = os.path.join(SCRATCH, "index.tsv")
    with ThreadPoolExecutor(max_workers=a.P) as pool:
        futs = []
        for c in cases:
            futs.append(pool.submit(run_case, c, commit, dirty, exe_hash, a.dry))
            time.sleep(1.05)          # distinct run ids
        for c, fu in zip(cases, futs):
            rid, rc, wall = fu.result()
            line = f"{c['name']}\t{rid}\t{rc}\t{wall:.1f}"
            print(line, flush=True)
            with _lock, open(index, "a") as f:
                f.write(line + "\n")


if __name__ == "__main__":
    sys.exit(main())
