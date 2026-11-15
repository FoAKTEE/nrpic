#!/usr/bin/env python3
"""Run one registered analysis run of the noise package and write its manifest.

    python3 runreg.py --purpose TEXT [--kind scouting] [--cores 4]
        [--inputs FILE ...] -- COMMAND ...

The run id is E-stoch-inf-<UTC YYYYmmdd-HHMMSS>-<commit7 of the worktree>; the output
directory scratch/E-stoch-inf/<run_id>/ is created and every "{out}" in COMMAND is
replaced by it. The command runs with that directory as working directory; its standard
output and error go to run.log there. The manifest goes to
tracks/E-stoch-inf/runs/<run_id>/manifest.json; if the command leaves a file
summary.txt in the output directory, its first 2000 characters become "results".
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

WT = "/data/haiyangw/nrpic/wt/E-stoch-inf"
SCRATCH = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
OWNER = "E-stoch-inf"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--inputs", nargs="*", default=[])
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        sys.exit("no command")
    commit = subprocess.run(["git", "-C", WT, "rev-parse", "--short=7", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", WT, "status", "--porcelain", "--",
                            "tracks/E-stoch-inf/noise"], capture_output=True,
                           text=True).stdout.strip()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"{OWNER}-{stamp}-{commit}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=False)
    cmd = [c.replace("{out}", out) for c in cmd]
    env = dict(os.environ)
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        env[v] = str(a.cores)
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        rc = subprocess.run(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT,
                            env=env).returncode
    wall = time.time() - t0
    results = ""
    sp = os.path.join(out, "summary.txt")
    if os.path.exists(sp):
        with open(sp) as f:
            results = f.read()[:2000]
    man = {
        "run_id": run_id,
        "owner": OWNER,
        "package": "noise (E-pre-4)",
        "kind": a.kind,
        "purpose": a.purpose,
        "cwd": out,
        "command": " ".join(cmd),
        "commit": commit,
        "worktree_dirty_paths": dirty.splitlines(),
        "inputs": [{"path": os.path.abspath(p), "sha256": sha256(p)} for p in a.inputs],
        "output_dir": out + "/",
        "wall_time": f"{wall:.1f} s",
        "cores": a.cores,
        "card_hours": 0.0,
        "status": "completed" if rc == 0 else f"failed (exit {rc})",
        "results": results,
    }
    mdir = os.path.join(WT, "tracks", OWNER, "runs", run_id)
    os.makedirs(mdir, exist_ok=False)
    with open(os.path.join(mdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
        f.write("\n")
    print(run_id, man["status"], man["wall_time"])
    sys.exit(rc)


if __name__ == "__main__":
    main()
