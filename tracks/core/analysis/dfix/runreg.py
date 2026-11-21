#!/usr/bin/env python3
"""Register a run of owner core by hand (CLAUDE.md, rule 4) and run its command.

    runreg.py --purpose TEXT [--kind scouting|production] [--cores N] [--card]
              [--input FILE ...] -- command [args ...]

Used in work package dfix because `harness/bin/nrpic-run submit` stops in budget_state()
with KeyError 'outputs' on a hand-written manifest of wave 1 (journal, entry T1). The run
id is core-<UTC date>-<UTC time>-<commit7>, the output directory scratch/core/<run_id>/
(exported as NRPIC_RUN_DIR; "{run}" in an argument is replaced by it, "{repo}" by the
worktree root). tracks/core/runs/<run_id>/manifest.json is written before the command
starts and completed when it ends: command, cwd, commit, inputs with sha256, output
directory, purpose, kind, wall time, cores or card-hours. Inputs: every --input, and
every existing file named on the command line or in a case list given on it (executables
and input decks). With --card the command uses one card through Slurm itself and prints
a line `CARD_SECONDS <s>`; that time is recorded as card-hours.
The command runs in the worktree root. A dirty worktree is recorded, not refused.
"""
import argparse
import hashlib
import json
import os
import re
import shlex
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


def files_of(words):
    """existing regular files among the words; a *.list file also contributes the files
    named in it"""
    out = []
    for w in words:
        w = w.replace("{repo}", REPO)
        if os.path.isfile(w):
            p = os.path.abspath(w)
            if p not in out:
                out.append(p)
            if p.endswith(".list"):
                for line in open(p):
                    line = line.strip()
                    if line and not line.startswith(("#", "@")):
                        for q in files_of(shlex.split(line)):
                            if q not in out:
                                out.append(q)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
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
        mdir = os.path.join(REPO, "tracks", "core", "runs", run_id)
        try:
            os.makedirs(out)
            os.makedirs(mdir)
            break
        except FileExistsError:
            time.sleep(1.1)
    cmd = [c.replace("{run}", out).replace("{repo}", REPO) for c in cmd]
    inputs = []
    for p in files_of(list(args.input) + cmd):
        rel = os.path.relpath(p, REPO) if p.startswith(REPO + os.sep) else p
        inputs.append({"path": rel, "sha256": sha256(p)})
    man = {
        "run_id": run_id,
        "owner": "core",
        "registered_by": "tracks/core/analysis/dfix/runreg.py (by hand: nrpic-run submit fails)",
        "purpose": args.purpose,
        "kind": args.kind,
        "command": cmd,
        "cwd": REPO,
        "commit": commit,
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "uncommitted_changes": dirty,
        "inputs": inputs,
        "output_directory": out,
        "outputs": {"dir": os.path.relpath(out, "/data/haiyangw/nrpic")},
        "host": socket.gethostname(),
        "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cores": args.cores,
        "status": "running",
    }
    mpath = os.path.join(mdir, "manifest.json")

    def write():
        with open(mpath, "w") as fp:
            json.dump(man, fp, indent=1)
            fp.write("\n")

    write()
    env = dict(os.environ)
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[v] = "1"
    env["NRPIC_RUN_DIR"] = out
    env["NRPIC_RUN_ID"] = run_id
    env["MPLCONFIGDIR"] = os.path.join(SCRATCH, "tmp", "dfix", "mpl")
    os.makedirs(env["MPLCONFIGDIR"], exist_ok=True)
    print(f"{run_id}  out {out}", flush=True)
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        log.write("# " + " ".join(cmd) + "\n")
        log.flush()
        proc = subprocess.run(cmd, cwd=REPO, stdout=log, stderr=subprocess.STDOUT, env=env)
    wall = time.time() - t0
    man["wall_time_s"] = round(wall, 2)
    man["exit_status"] = proc.returncode
    man["status"] = "completed" if proc.returncode == 0 else "failed"
    man["end_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if args.card:
        secs = None
        for line in open(os.path.join(out, "run.log")):
            mm = re.match(r"CARD_SECONDS\s+([0-9.]+)", line)
            if mm:
                secs = float(mm.group(1))
        man["card_hours"] = round((secs if secs is not None else wall)/3600.0, 4)
        man["card_time_source"] = "Slurm elapsed" if secs is not None else "wall time"
    else:
        man["core_hours"] = round(args.cores*wall/3600.0, 4)
    write()
    print(f"{run_id}  exit {proc.returncode}  wall {wall:.1f} s")
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
