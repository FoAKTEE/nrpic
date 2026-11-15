#!/usr/bin/env python3
"""Write tracks/F-hills/runs/<run_id>/manifest.json for an analysis run made by hand.

Usage: python3 write_manifest.py <run_id> <status> <purpose> <notes> <command> <input> [<input> ...]
The output directory is scratch/F-hills/<run_id>/; wall time is read from its wall.txt.
"""
import hashlib
import json
import os
import subprocess
import sys

HOME = "/data/haiyangw/nrpic"
WT = os.path.join(HOME, "wt/F-hills")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def inp(p):
    """A file on disk, or 'git:<rev>:<path>' for a file as committed (scripts of a run)."""
    if p.startswith("git:"):
        _, rev, path = p.split(":", 2)
        blob = subprocess.run(["git", "-C", WT, "show", f"{rev}:{path}"], capture_output=True).stdout
        return {"path": path, "git_rev": rev, "sha256": hashlib.sha256(blob).hexdigest(),
                "bytes": len(blob)}
    return {"path": p, "sha256": sha256(p), "bytes": os.path.getsize(p)}


rid, status, purpose, notes, command = sys.argv[1:6]
inputs = sys.argv[6:]
out = os.path.join(HOME, "scratch/F-hills", rid)
wall = None
if os.path.exists(os.path.join(out, "wall.txt")):
    wall = float(open(os.path.join(out, "wall.txt")).read().split("=")[-1])
sha = rid.rsplit("-", 1)[1]
full = subprocess.run(["git", "-C", WT, "rev-parse", sha], capture_output=True, text=True).stdout.strip()
outputs = sorted(os.listdir(out)) if os.path.isdir(out) else []
m = {
    "run_id": rid,
    "track": "F-hills",
    "package": "novelty",
    "kind": "scouting",
    "status": status,
    "purpose": purpose,
    "launcher": "local",
    "command": command,
    "cwd": WT,
    "git": {"sha": full, "branch": "track/F-hills"},
    "inputs": [inp(p) for p in inputs],
    "output_dir": os.path.relpath(out, HOME),
    "outputs": outputs,
    "wall_seconds": wall,
    "cores": 1,
    "gpu_hours": 0.0,
    "notes": notes,
}
d = os.path.join(WT, "tracks/F-hills/runs", rid)
os.makedirs(d, exist_ok=True)
with open(os.path.join(d, "manifest.json"), "w") as f:
    json.dump(m, f, indent=1)
print(os.path.join(d, "manifest.json"))
