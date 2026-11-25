#!/usr/bin/env python3
"""Run a processor test that nrpic-run's local launcher refuses, and register it by hand.

    python3 tracks/core/tools/hand_run.py --purpose "..." [--input PATH ...] -- <command ...>

nrpic-run refuses a local command whose script names sbatch, srun or the scripts that call
them (decision 0033, one route; harness/RULES.md), also when every Slurm program the command
reaches is a fake on PATH, as in scripts/tests/test_submit_chain.py and test_queue_marker.py.
CLAUDE.md rule 4 then allows a manifest by hand, said so. This helper writes
tracks/core/runs/<run_id>/manifest.json in the layout nrpic-run uses (schema
nrpic-run-manifest/1), with run_id = core-<UTC stamp>-<commit7>, runs the command in the
worktree root with $NRPIC_RUN_DIR = scratch/core/<run_id>, writes run.log and
sha256sums.txt there, and records status, exit code and wall time. It refuses a dirty
worktree (the commit must name the code that ran). It commits nothing: the lead commits the
manifest. Standard library only.
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
WT = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"], capture_output=True,
                    text=True, check=True).stdout.strip()
HOME = "/data/haiyangw/nrpic"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", WT] + list(a), capture_output=True, text=True,
                          check=True).stdout.strip()


def utc(t=None):
    return datetime.datetime.fromtimestamp(t or time.time(), datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--gate", default="G2")
    ap.add_argument("--notes", default="")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        sys.exit("hand_run: no command")
    if git("status", "--porcelain"):
        sys.exit("hand_run: the worktree is not clean; commit first")
    sha = git("rev-parse", "HEAD")
    t0 = time.time()
    run_id = "core-" + datetime.datetime.fromtimestamp(t0, datetime.timezone.utc).strftime(
        "%Y%m%d-%H%M%S") + "-" + sha[:7]
    out_rel = f"scratch/core/{run_id}"
    out = os.path.join(HOME, out_rel)
    os.makedirs(out)
    argv = [x.replace("$NRPIC_RUN_DIR", out) for x in cmd]
    inputs = []
    for p in [x for x in cmd if os.path.isfile(os.path.join(WT, x))] + a.input:
        ap_ = p if os.path.isabs(p) else os.path.join(WT, p)
        tracked = subprocess.run(["git", "-C", WT, "ls-files", "--error-unmatch", ap_],
                                 capture_output=True).returncode == 0
        inputs.append({"path": p, "role": "argv" if p in cmd else "input", "sha256": sha256(ap_),
                       "bytes": os.path.getsize(ap_), "tracked": tracked})
    env = dict(os.environ, NRPIC_RUN_DIR=out, OMP_NUM_THREADS="1")
    with open(os.path.join(out, "run.log"), "w") as log:
        r = subprocess.run(argv, cwd=WT, env=env, stdout=log, stderr=subprocess.STDOUT)
    t1 = time.time()
    files, total = [], 0
    for dp, _, fns in os.walk(out):
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p) or fn == "sha256sums.txt":
                continue
            files.append((os.path.relpath(p, out), sha256(p)))
            total += os.path.getsize(p)
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        for rel, h in sorted(files):
            f.write(f"{h}  {rel}\n")
    m = {
        "schema": "nrpic-run-manifest/1", "run_id": run_id, "track": "core", "gate": a.gate,
        "kind": "scouting", "purpose": a.purpose, "preregistered_in": None, "launcher": "local",
        "command": cmd, "cwd": ".",
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"), "dirty": False,
                "merge_base_main": git("merge-base", "HEAD", "main"), "worktree": "wt/core"},
        "code": {"core_tag": "core-v0.7", "athenak_upstream_sha": "c5a0d7f",
                 "kokkos_sha": "6739bc623081648af9e752b616d9671527922cbf", "problem": None},
        "env": {"host": os.uname().nodename, "python": sys.version.split()[0] + " " + sys.executable},
        "input": None, "inputs": inputs, "batch_entries": None,
        "resources": {"nodes": 1, "gpus": 0, "cores": 1, "walltime_s": round(t1 - t0, 3),
                      "wall_limit": None, "segments_max": None, "gpu_hours_requested": 0.0,
                      "gpu_hours": None, "particles": None},
        "slurm": None,
        "outputs": {"dir": out_rel, "sha256sums": "sha256sums.txt",
                    "sha256sums_sha256": sha256(os.path.join(out, "sha256sums.txt")),
                    "bytes": total, "files": len(files)},
        "status": "completed" if r.returncode == 0 else "failed", "exit_code": r.returncode,
        "registered": utc(t0), "started": utc(t0), "ended": utc(t1), "parents": [],
        "notes": ("registered by hand with tracks/core/tools/hand_run.py: nrpic-run's local "
                  "launcher refuses a command whose script names sbatch or submit_chain.sh, also "
                  "when they are fakes on PATH (decision 0033; CLAUDE.md rule 4). " + a.notes).strip(),
        "finished": utc(t1),
    }
    md = os.path.join(WT, "tracks", "core", "runs", run_id)
    os.makedirs(md)
    with open(os.path.join(md, "manifest.json"), "w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")
    print(f"{run_id} {m['status']} exit {r.returncode} wall {t1 - t0:.1f} s; out {out_rel}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
