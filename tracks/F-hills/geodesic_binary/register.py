"""Register and run one analysis run of this package (manifest by hand, CLAUDE.md rule 4).

    python3 -I register.py --purpose TEXT [--kind scouting|production] [--cores N]
                           [--input PATH ...] -- <command ...>

The literal token {out} in the command is replaced by the output directory
scratch/F-hills/<run_id>/.  Writes tracks/F-hills/runs/<run_id>/manifest.json (run id
F-hills-<YYYYMMDD-HHMMSS UTC>-<commit7>) before the run and again after it, with wall time,
exit code and the sha256 of every output file.  The worktree root is the cwd of the run.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/F-hills"
OWNER = "F-hills"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT, *args], capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--parent", action="append", default=[])
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    sha = git("rev-parse", "HEAD")
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"{OWNER}-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=False)
    mdir = os.path.join(WT, "tracks", OWNER, "runs", run_id)
    os.makedirs(mdir, exist_ok=False)
    cmd = [c.replace("{out}", out) for c in cmd]
    dirty = git("status", "--porcelain", "--", "tracks/F-hills/geodesic_binary")
    inputs = []
    for p in a.input:
        ap_ = p if os.path.isabs(p) else os.path.join(WT, p)
        inputs.append({"path": os.path.relpath(ap_, WT) if ap_.startswith(WT) else ap_,
                       "sha256": sha256(ap_)})
    man = {
        "run_id": run_id, "track": OWNER, "package": "geodesic_binary (F-pre-2)",
        "purpose": a.purpose, "kind": a.kind, "command": cmd, "cwd": WT,
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "dirty_package": bool(dirty)},
        "inputs": inputs, "parents": a.parent,
        "resources": {"cores": a.cores, "gpus": 0, "card_hours": 0.0},
        "outputs": {"dir": os.path.relpath(out, "/data/haiyangw/nrpic")},
        "status": "running", "started": now.isoformat(timespec="seconds"),
    }
    mpath = os.path.join(mdir, "manifest.json")
    with open(mpath, "w") as fh:
        json.dump(man, fh, indent=1)
    env = dict(os.environ, OMP_NUM_THREADS="1", NUMBA_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NRPIC_RUN_ID=run_id, NRPIC_RUN_DIR=out,
               NRPIC_CORES=str(a.cores))
    t0 = time.time()
    with open(os.path.join(out, "stdout.txt"), "w") as so:
        rc = subprocess.run(cmd, cwd=WT, env=env, stdout=so, stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    sums = {}
    for root, _, files in os.walk(out):
        for f in sorted(files):
            p = os.path.join(root, f)
            sums[os.path.relpath(p, out)] = sha256(p)
    man.update(status="completed" if rc == 0 else "failed", exit_code=rc,
               ended=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               wall_time_s=round(wall, 1))
    man["resources"]["core_hours"] = round(wall * a.cores / 3600, 4)
    man["outputs"]["sha256"] = sums
    with open(mpath, "w") as fh:
        json.dump(man, fh, indent=1)
    print(run_id, man["status"], f"{wall:.1f}s")
    sys.exit(rc)


if __name__ == "__main__":
    main()
