"""Register a run of verify_cosmo by hand (CLAUDE.md rule 4; harness/bin/nrpic-run refuses
a worktree that other helpers are writing in).

    python3 register.py new --purpose TEXT --kind scouting --command CMD [--input PATH ...]
                            [--cores N] [--card-hours H] [--notes TEXT]
        prints the run id and creates tracks/B-emd-gw/runs/<id>/manifest.json and
        scratch/B-emd-gw/<id>/
    python3 register.py finish <run_id> --status completed|failed [--wall-s S]
                               [--card-hours H] [--notes TEXT]
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess

WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                  "..", ".."))
OWNER = "B-emd-gw"
SCRATCH = "/data/haiyangw/nrpic/scratch/" + OWNER


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", WT] + list(args), text=True).strip()


def manifest_path(run_id):
    return os.path.join(WT, "tracks", OWNER, "runs", run_id, "manifest.json")


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
n = sub.add_parser("new")
n.add_argument("--purpose", required=True)
n.add_argument("--kind", default="scouting", choices=("scouting", "production"))
n.add_argument("--command", required=True)
n.add_argument("--cwd", default=WT)
n.add_argument("--input", action="append", default=[])
n.add_argument("--cores", type=int, default=1)
n.add_argument("--card-hours", type=float, default=0.0)
n.add_argument("--notes", default="")
f = sub.add_parser("finish")
f.add_argument("run_id")
f.add_argument("--status", required=True, choices=("completed", "failed", "stopped"))
f.add_argument("--wall-s", type=float, default=None)
f.add_argument("--card-hours", type=float, default=None)
f.add_argument("--notes", default="")
f.add_argument("--input", action="append", default=[],
               help="inputs known only after the start (added with checksums)")
a = ap.parse_args()

if a.cmd == "new":
    now = dt.datetime.now(dt.timezone.utc)
    commit = git("rev-parse", "HEAD")
    run_id = f"{OWNER}-{now:%Y%m%d-%H%M%S}-{commit[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=True)
    man = {
        "run_id": run_id, "command": a.command, "cwd": a.cwd, "commit": commit,
        "worktree_dirty": bool(git("status", "--porcelain")),
        "inputs": [{"path": p, "sha256": sha256(p)} for p in a.input],
        "output_dir": out, "purpose": a.purpose, "kind": a.kind,
        "cores": a.cores, "card_hours": a.card_hours,
        "started_utc": now.isoformat(timespec="seconds"), "status": "running",
        "package": "tracks/B-emd-gw/verify_cosmo", "notes": a.notes,
    }
    os.makedirs(os.path.dirname(manifest_path(run_id)), exist_ok=True)
    with open(manifest_path(run_id), "w") as fh:
        json.dump(man, fh, indent=1)
    print(run_id)
else:
    p = manifest_path(a.run_id)
    with open(p) as fh:
        man = json.load(fh)
    now = dt.datetime.now(dt.timezone.utc)
    man["status"] = a.status
    man["finished_utc"] = now.isoformat(timespec="seconds")
    if a.wall_s is None:
        start = dt.datetime.fromisoformat(man["started_utc"])
        a.wall_s = (now - start).total_seconds()
    man["wall_time_s"] = round(a.wall_s, 1)
    if a.card_hours is not None:
        man["card_hours"] = a.card_hours
    if a.notes:
        man["notes"] = (man.get("notes", "") + " " + a.notes).strip()
    for q in a.input:
        man["inputs"].append({"path": q, "sha256": sha256(q)})
    with open(p, "w") as fh:
        json.dump(man, fh, indent=1)
    print(p)
