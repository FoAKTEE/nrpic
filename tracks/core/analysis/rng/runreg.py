#!/usr/bin/env python3
"""Run a command as a registered run of owner core (CLAUDE.md, rule 4).

  runreg.py --purpose TEXT [--kind scouting|production] [--cores N] [--card]
            [--input FILE ...] -- command [args ...]

Creates the run id core-<UTC date>-<UTC time>-<commit7>, the output directory
scratch/core/<run_id>/ (the command runs there; "{out}" in an argument is replaced by
it, "{repo}" by the worktree), and tracks/core/runs/<run_id>/manifest.json with the
command, the commit, the inputs with their sha256, the wall time and the exit status.
With --card the command is expected to use one card through Slurm itself; the card time
recorded is the wall time of the command.
"""
import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for blk in iter(lambda: fp.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True,
                          text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="production", choices=["scouting", "production"])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--card", action="store_true")
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        ap.error("no command")

    commit = git("rev-parse", "HEAD")
    dirty = [ln for ln in git("status", "--porcelain").splitlines()
             if not ln.startswith("?? tracks/core/runs/")]
    while True:
        run_id = "core-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-" + commit[:7]
        out = os.path.join(SCRATCH, run_id)
        try:
            os.makedirs(out)
            break
        except FileExistsError:
            time.sleep(1.1)
    cmd = [c.replace("{out}", out).replace("{repo}", REPO) for c in cmd]
    inputs = [{"path": os.path.relpath(p, REPO) if os.path.abspath(p).startswith(REPO)
               else os.path.abspath(p), "sha256": sha256(p)} for p in args.input]
    man = {
        "run_id": run_id,
        "owner": "core",
        "purpose": args.purpose,
        "kind": args.kind,
        "command": cmd,
        "cwd": out,
        "commit": commit,
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "uncommitted_changes": dirty,
        "inputs": inputs,
        "output_directory": out,
        "host": socket.gethostname(),
        "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cores": args.cores,
    }
    mdir = os.path.join(REPO, "tracks", "core", "runs", run_id)
    os.makedirs(mdir)
    env = dict(os.environ)
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[v] = str(args.cores)
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        proc = subprocess.run(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT, env=env)
    wall = time.time() - t0
    man["wall_time_s"] = round(wall, 2)
    man["exit_status"] = proc.returncode
    if args.card:
        man["card_hours"] = round(wall / 3600.0, 4)
    else:
        man["core_hours"] = round(args.cores * wall / 3600.0, 4)
    with open(os.path.join(mdir, "manifest.json"), "w") as fp:
        json.dump(man, fp, indent=1)
        fp.write("\n")
    print(f"{run_id}  exit {proc.returncode}  wall {wall:.1f} s  out {out}")
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
