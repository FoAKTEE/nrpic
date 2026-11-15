#!/usr/bin/env python3
"""Run a command as a registered run of owner core (CLAUDE.md, rule 4), by hand:
`harness/bin/nrpic-run submit` stops in this worktree with KeyError 'outputs' while it
reads core's manifests of wave 1 (journal of package scalar2, entry 3).

  runreg.py --purpose TEXT [--kind scouting|production] [--gate G2] [--cores N] [--card]
            [--input FILE ...] -- command [args ...]

Creates the run id core-<UTC date>-<UTC time>-<commit7>, the output directory
scratch/core/<run_id>/ (the command runs in the worktree root; "{out}" in an argument is
replaced by the output directory, "{repo}" by the worktree) and
tracks/core/runs/<run_id>/manifest.json with the command, the working directory, the
commit, the inputs with their sha256, the output directory, the purpose, the kind, the
wall time and the cores or card-hours.  With --card the command submits to one card
through Slurm; the card time is read from {out}/card_seconds.txt (written by the job:
seconds between its start and its end), the wall time of the command includes the wait
in the queue.  The keys track, gate, outputs and status repeat the information in the
layout of harness/templates/run_manifest.json.
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
MAIN = "/data/haiyangw/nrpic"
SCRATCH = os.path.join(MAIN, "scratch", "core")


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
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--gate", default="G2")
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
             if "tracks/core/runs/" not in ln]
    while True:
        run_id = "core-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-" + commit[:7]
        out = os.path.join(SCRATCH, run_id)
        try:
            os.makedirs(out)
            break
        except FileExistsError:
            time.sleep(1.1)
    cmd = [c.replace("{out}", out).replace("{repo}", REPO) for c in cmd]
    inputs = []
    for p in args.input:
        ap_ = os.path.abspath(os.path.join(REPO, p))
        inputs.append({"path": os.path.relpath(ap_, REPO) if ap_.startswith(REPO + "/")
                       else ap_, "sha256": sha256(ap_)})
    man = {
        "run_id": run_id,
        "owner": "core",
        "track": "core",
        "gate": args.gate,
        "purpose": args.purpose,
        "kind": args.kind,
        "command": cmd,
        "cwd": REPO,
        "commit": commit,
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "uncommitted_changes": dirty,
        "inputs": inputs,
        "output_directory": out,
        "outputs": {"dir": os.path.relpath(out, MAIN)},
        "host": socket.gethostname(),
        "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cores": args.cores,
        "registered_by": "tracks/core/analysis/scalar2/runreg.py (by hand: nrpic-run "
                         "submit fails with KeyError 'outputs')",
        "status": "running",
    }
    mdir = os.path.join(REPO, "tracks", "core", "runs", run_id)
    os.makedirs(mdir)

    def write():
        with open(os.path.join(mdir, "manifest.json"), "w") as fp:
            json.dump(man, fp, indent=1)
            fp.write("\n")

    write()
    env = dict(os.environ)
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[v] = "1"
    env["NRPIC_RUN_DIR"] = out
    env["NRPIC_RUN_ID"] = run_id
    print(f"{run_id}  started  out {out}", flush=True)
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        proc = subprocess.run(cmd, cwd=REPO, stdout=log, stderr=subprocess.STDOUT, env=env)
    wall = time.time() - t0
    man["wall_time_s"] = round(wall, 2)
    man["exit_status"] = proc.returncode
    man["status"] = "completed" if proc.returncode == 0 else "failed"
    man["end_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if args.card:
        cs = os.path.join(out, "card_seconds.txt")
        if os.path.exists(cs):
            sec = float(open(cs).read().split()[0])
            man["card_seconds"] = sec
            man["card_hours"] = round(sec/3600.0, 5)
        else:
            man["card_hours"] = None
            man["note"] = "no card_seconds.txt: the job did not report its card time"
    else:
        man["core_hours"] = round(args.cores*wall/3600.0, 4)
    write()
    print(f"{run_id}  exit {proc.returncode}  wall {wall:.1f} s  out {out}")
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
