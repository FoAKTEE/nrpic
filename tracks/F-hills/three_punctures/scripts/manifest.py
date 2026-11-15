#!/usr/bin/env python3
"""Run one analysis command of the three_punctures package and register it.

Usage (from the worktree root):
    python3 tracks/F-hills/three_punctures/scripts/manifest.py <purpose> <kind> \
        <input>[,<input>...] -- <command ...>

The run id is F-hills-<UTC date-time>-<commit7>; the command gets the output directory
scratch/F-hills/<run_id>/ appended as its last argument (or substituted for the token
OUTDIR). stdout and stderr go to <outdir>/stdout.txt. The manifest is written to
tracks/F-hills/runs/<run_id>/manifest.json with the checksums of the inputs and of every
file in the output directory. Processors only: cores 1, card-hours 0.
"""
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

HOME = "/data/haiyangw/nrpic"
WT = os.path.join(HOME, "wt/F-hills")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    argv = sys.argv[1:]
    sep = argv.index("--")
    purpose, kind, inputs = argv[0], argv[1], argv[2]
    cmd = argv[sep + 1:]
    commit = subprocess.run(["git", "-C", WT, "rev-parse", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    stamp = dt.datetime.now(dt.timezone.utc)
    rid = f"F-hills-{stamp:%Y%m%d-%H%M%S}-{commit[:7]}"
    out = os.path.join(HOME, "scratch/F-hills", rid)
    os.makedirs(out, exist_ok=False)
    if "OUTDIR" in cmd:
        cmd = [out if c == "OUTDIR" else c for c in cmd]
    else:
        cmd = cmd + [out]
    dirty = subprocess.run(["git", "-C", WT, "status", "--porcelain", "--",
                            "tracks/F-hills/three_punctures"], capture_output=True,
                           text=True).stdout.strip() != ""
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(out, "stdout.txt"), "w") as fo:
        rc = subprocess.run(cmd, cwd=WT, stdout=fo, stderr=subprocess.STDOUT, env=env).returncode
    wall = time.time() - t0
    ins = []
    for p in [s for s in inputs.split(",") if s]:
        ap = p if os.path.isabs(p) else os.path.join(WT, p)
        ins.append({"path": p, "sha256": sha256(ap) if os.path.isfile(ap) else None})
    outs = {}
    for root, _, files in os.walk(out):
        for f in sorted(files):
            fp = os.path.join(root, f)
            if os.path.getsize(fp) < 200 * 1024 * 1024:
                outs[os.path.relpath(fp, out)] = sha256(fp)
    man = {
        "run_id": rid, "track": "F-hills", "package": "three_punctures (F-pre-3, F-pre-4 plan)",
        "purpose": purpose, "kind": kind, "command": cmd, "cwd": WT,
        "git": {"sha": commit, "branch": "track/F-hills", "dirty_package": dirty},
        "inputs": ins, "parents": [],
        "resources": {"cores": 1, "gpus": 0, "card_hours": 0.0,
                      "core_hours": round(wall / 3600.0, 5)},
        "outputs": {"dir": f"scratch/F-hills/{rid}", "sha256": outs},
        "status": "completed" if rc == 0 else "failed", "exit_code": rc,
        "started": stamp.isoformat(timespec="seconds"),
        "ended": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "wall_time_s": round(wall, 1),
    }
    mdir = os.path.join(WT, "tracks/F-hills/runs", rid)
    os.makedirs(mdir, exist_ok=False)
    with open(os.path.join(mdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(rid, man["status"], f"{wall:.1f} s")
    return rc


if __name__ == "__main__":
    sys.exit(main())
