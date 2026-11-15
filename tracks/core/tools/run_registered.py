#!/usr/bin/env python3
"""Run a command as a registered run of owner core (CLAUDE.md, rule 4).

    run_registered.py --purpose "..." [--kind scouting|production] [--cores N]
                      [--card-hours H] [--input FILE ...] [--tag NAME] -- command ...

The run id is core-<UTC date>-<UTC time>-<commit7>; the command runs with the output
directory scratch/core/<run_id>/ as its working directory, where every --input file is
linked under its own name. The manifest tracks/core/runs/<run_id>/manifest.json holds the
command, the working directory, the commit, the inputs with their sha256, the output
directory, the purpose, the kind, the wall time, the exit status and the cores or
card-hours. The run id is printed on the last line.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=("scouting", "production"))
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--card-hours", type=float, default=0.0)
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--tag", default="")
    ap.add_argument("command", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.command[1:] if a.command and a.command[0] == "--" else a.command
    if not cmd:
        ap.error("no command")

    commit = subprocess.run(["git", "-C", WORKTREE, "rev-parse", "--short=7", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", WORKTREE, "status", "--porcelain", "--", "athenak/src",
                            "python", "problems"], capture_output=True, text=True,
                           check=True).stdout.strip()
    now = datetime.datetime.now(datetime.timezone.utc)
    run_id = "core-%s-%s" % (now.strftime("%Y%m%d-%H%M%S"), commit)
    out = os.path.join(SCRATCH, run_id)
    while os.path.exists(out):                 # two runs in the same second
        time.sleep(1.0)
        now = datetime.datetime.now(datetime.timezone.utc)
        run_id = "core-%s-%s" % (now.strftime("%Y%m%d-%H%M%S"), commit)
        out = os.path.join(SCRATCH, run_id)
    os.makedirs(out)
    inputs = []
    for path in a.input:
        p = os.path.abspath(path)
        inputs.append({"path": os.path.relpath(p, WORKTREE) if p.startswith(WORKTREE) else p,
                       "sha256": sha256(p)})
        link = os.path.join(out, os.path.basename(p))
        if not os.path.exists(link):
            os.symlink(p, link)
    exe = cmd[0]
    if os.path.isfile(exe):
        inputs.append({"path": os.path.abspath(exe), "sha256": sha256(exe),
                       "role": "executable"})

    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        proc = subprocess.run(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT)
    wall = time.time() - t0

    man = {
        "run_id": run_id,
        "owner": "core",
        "command": cmd,
        "cwd": out,
        "commit": commit,
        "source_modified_since_commit": bool(dirty),
        "inputs": inputs,
        "output_directory": out,
        "purpose": a.purpose,
        "kind": a.kind,
        "tag": a.tag,
        "wall_time_s": round(wall, 2),
        "exit_status": proc.returncode,
        "cores": a.cores,
        "card_hours": a.card_hours,
        "started_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    mdir = os.path.join(WORKTREE, "tracks", "core", "runs", run_id)
    os.makedirs(mdir)
    with open(os.path.join(mdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
        f.write("\n")
    print("exit %d, wall %.1f s, output %s" % (proc.returncode, wall, out))
    print(run_id)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
