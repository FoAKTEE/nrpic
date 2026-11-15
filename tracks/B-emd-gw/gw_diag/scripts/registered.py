#!/usr/bin/env python3
"""Run one analysis command as a registered run of B-emd-gw.

    python3 scripts/registered.py --purpose TEXT [--kind scouting|production]
        [--input PATH ...] [--cores N] -- <command ...>

Creates run_id = B-emd-gw-<UTC YYYYMMDD-HHMMSS>-<commit7>, the output directory
/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/ (passed to the command as $RUN_DIR and by
replacing the token {RUN_DIR} in its arguments), writes
tracks/B-emd-gw/runs/<run_id>/manifest.json before the start (status running) and again at
the end (status, exit code, wall time, sha256 of the outputs). Inputs are checksummed.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

WT = "/data/haiyangw/nrpic/wt/B-emd-gw"
SCRATCH = "/data/haiyangw/nrpic/scratch/B-emd-gw"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT] + list(args), capture_output=True,
                          text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--", "tracks/B-emd-gw/gw_diag"))
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"B-emd-gw-{now:%Y%m%d-%H%M%S}-{commit[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out)
    cmd = [c.replace("{RUN_DIR}", out) for c in cmd]
    inputs = [{"path": p, "sha256": sha256(p)} for p in a.input]
    for c in cmd:
        if c.endswith(".py") and os.path.exists(c):
            inputs.append({"path": os.path.abspath(c), "sha256": sha256(c)})
    man = {"run_id": run_id, "owner": "B-emd-gw", "package": "gw_diag",
           "command": " ".join(cmd), "cwd": os.getcwd(), "commit": commit,
           "worktree_dirty_gw_diag": dirty, "inputs": inputs, "output_dir": out,
           "purpose": a.purpose, "kind": a.kind, "cores": a.cores, "card_hours": 0.0,
           "env": {k: os.environ.get(k, str(a.cores)) for k in
                   ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
           "started_utc": now.isoformat(timespec="seconds"), "status": "running"}
    mdir = os.path.join(WT, "tracks/B-emd-gw/runs", run_id)
    os.makedirs(mdir)
    mpath = os.path.join(mdir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    env = dict(os.environ, RUN_DIR=out)
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        env.setdefault(k, str(a.cores))
    t0 = time.time()
    with open(os.path.join(out, "stdout.txt"), "w") as so:
        rc = subprocess.run(cmd, stdout=so, stderr=subprocess.STDOUT, env=env).returncode
    wall = time.time() - t0
    outs = {}
    for root, _, files in os.walk(out):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            outs[os.path.relpath(p, out)] = sha256(p)
    man.update({"status": "completed" if rc == 0 else "failed", "exit_code": rc,
                "wall_time_s": round(wall, 2),
                "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "outputs_sha256": outs})
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    print(run_id, man["status"], f"{wall:.1f} s")
    sys.exit(rc)


if __name__ == "__main__":
    main()
