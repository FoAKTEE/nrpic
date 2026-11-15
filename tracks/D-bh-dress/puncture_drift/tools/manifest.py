#!/usr/bin/env python3
"""Write or update the manifest of a run of the package puncture_drift (by hand, as the
harness's nrpic-run refuses a worktree shared by several helpers).

    manifest.py new --purpose TEXT --kind scouting|production --cmd JSON_LIST
                    [--input PATH ...] [--cores N] [--gpus N] [--env K=V ...]
                    [--notes TEXT] [--status STATUS]          -> prints the run id
    manifest.py update RUN_ID [--status S] [--walltime-s X] [--card-hours X]
                    [--started ISO] [--ended ISO] [--notes TEXT] [--outputs-files ...]
                    [--add-input PATH ...]

run_id = D-bh-dress-<YYYYMMDD-HHMMSS UTC>-<commit7>; manifest at
tracks/D-bh-dress/runs/<run_id>/manifest.json; output directory
/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/ (created here).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

WT = "/data/haiyangw/nrpic/wt/D-bh-dress"
RUNS = os.path.join(WT, "tracks/D-bh-dress/runs")
SCRATCH = "/data/haiyangw/nrpic/scratch/D-bh-dress"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT, *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_new(a):
    sha = git("rev-parse", "HEAD")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"D-bh-dress-{stamp}-{sha[:7]}"
    mdir = os.path.join(RUNS, run_id)
    os.makedirs(mdir, exist_ok=False)
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=True)
    dirty = bool(git("status", "--porcelain", "--", "tracks/D-bh-dress/puncture_drift"))
    m = {
        "run_id": run_id,
        "track": "D-bh-dress",
        "gate": "G1",
        "package": "puncture_drift (D-pre-4)",
        "purpose": a.purpose,
        "kind": a.kind,
        "command": json.loads(a.cmd),
        "cwd": a.cwd,
        "env_overrides": dict(kv.split("=", 1) for kv in (a.env or [])),
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "dirty_package_dir": dirty,
                "merge_base_main": git("merge-base", "HEAD", "main")},
        "code": {"core_tag": None},
        "inputs": [{"path": os.path.abspath(p), "sha256": sha256(p)} for p in (a.input or [])],
        "resources": {"nodes": 1, "cores": a.cores, "gpus": a.gpus,
                      "card_hours": None if a.gpus else 0.0, "walltime_s": None},
        "outputs": {"dir": out},
        "status": a.status,
        "started": now_iso() if a.status in ("running", "submitted") else None,
        "ended": None,
        "parents": a.parent or [],
        "notes": a.notes or "",
    }
    with open(os.path.join(mdir, "manifest.json"), "w") as f:
        json.dump(m, f, indent=1)
        f.write("\n")
    print(run_id)


def cmd_update(a):
    p = os.path.join(RUNS, a.run_id, "manifest.json")
    m = json.load(open(p))
    if a.status:
        m["status"] = a.status
    if a.walltime_s is not None:
        m["resources"]["walltime_s"] = a.walltime_s
    if a.card_hours is not None:
        m["resources"]["card_hours"] = a.card_hours
    if a.started:
        m["started"] = a.started
    if a.ended:
        m["ended"] = a.ended
    if a.notes:
        m["notes"] = (m.get("notes", "") + " " + a.notes).strip()
    if a.outputs_files:
        m["outputs"]["files"] = a.outputs_files
    for pth in a.add_input or []:
        m["inputs"].append({"path": os.path.abspath(pth), "sha256": sha256(pth)})
    if a.exit_code is not None:
        m["exit_code"] = a.exit_code
    with open(p, "w") as f:
        json.dump(m, f, indent=1)
        f.write("\n")
    print(p)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    n = sp.add_parser("new")
    n.add_argument("--purpose", required=True)
    n.add_argument("--kind", required=True, choices=["scouting", "production"])
    n.add_argument("--cmd", required=True, help="JSON list")
    n.add_argument("--cwd", default=WT)
    n.add_argument("--input", nargs="*")
    n.add_argument("--cores", type=int, default=1)
    n.add_argument("--gpus", type=int, default=0)
    n.add_argument("--env", nargs="*")
    n.add_argument("--notes")
    n.add_argument("--parent", nargs="*")
    n.add_argument("--status", default="submitted")
    u = sp.add_parser("update")
    u.add_argument("run_id")
    u.add_argument("--status")
    u.add_argument("--walltime-s", type=float)
    u.add_argument("--card-hours", type=float)
    u.add_argument("--started")
    u.add_argument("--ended")
    u.add_argument("--notes")
    u.add_argument("--outputs-files", nargs="*")
    u.add_argument("--add-input", nargs="*")
    u.add_argument("--exit-code", type=int)
    a = ap.parse_args()
    {"new": cmd_new, "update": cmd_update}[a.mode](a)


if __name__ == "__main__":
    sys.exit(main())
