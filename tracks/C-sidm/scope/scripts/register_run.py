#!/usr/bin/env python3
"""Register and run one analysis run of the C-sidm scoping package.

    python3 tracks/C-sidm/scope/scripts/register_run.py --purpose TEXT \
        [--kind scouting|production] [--input PATH ...] -- <command ...>

Writes tracks/C-sidm/runs/<run_id>/manifest.json with run_id = C-sidm-<YYYYMMDD-HHMMSS>-<commit7>
(UTC, commit of HEAD), creates scratch/C-sidm/<run_id>/, runs the command with the
environment variable NRPIC_RUN_DIR set to that directory and one thread per numerical
library, then records exit status, wall time, cores and the sha256 of every output file.
Run from the worktree root. The command's own files must be committed first, so that the
recorded commit contains them (refused otherwise).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

OWNER = "C-sidm"
SCRATCH = "/data/haiyangw/nrpic/scratch/C-sidm"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        sys.exit("no command given")
    root = git("rev-parse", "--show-toplevel")
    os.chdir(root)
    inputs = sorted(set(a.input + [c for c in cmd if os.path.isfile(c)]))
    dirty = git("status", "--porcelain", "--", *inputs) if inputs else ""
    if dirty:
        sys.exit("inputs not committed:\n" + dirty)
    commit = git("rev-parse", "HEAD")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"{OWNER}-{stamp}-{commit[:7]}"
    outdir = os.path.join(SCRATCH, run_id)
    os.makedirs(outdir, exist_ok=False)
    mdir = os.path.join(root, "tracks", OWNER, "runs", run_id)
    os.makedirs(mdir, exist_ok=False)
    man = dict(run_id=run_id, owner=OWNER, kind=a.kind, purpose=a.purpose,
               command=cmd, cwd=root, commit=commit, branch=git("branch", "--show-current"),
               inputs=[dict(path=p, sha256=sha256(p)) for p in inputs],
               output_directory=outdir, launcher="local (processors)", cores=1,
               card_hours=0.0, started_utc=stamp, status="running")
    mpath = os.path.join(mdir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(man, f, indent=2)
    env = dict(os.environ, NRPIC_RUN_DIR=outdir, OMP_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
               MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    with open(os.path.join(outdir, "stdout.txt"), "w") as fo:
        rc = subprocess.run(cmd, env=env, stdout=fo, stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    outs = []
    for dp, _, fs in os.walk(outdir):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            outs.append(dict(path=os.path.relpath(p, outdir), sha256=sha256(p)))
    man.update(status="completed" if rc == 0 else "failed", exit_status=rc,
               wall_time_s=round(wall, 2),
               finished_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S"),
               outputs=outs)
    with open(mpath, "w") as f:
        json.dump(man, f, indent=2)
    print(run_id, man["status"], f"{wall:.1f} s")
    sys.exit(rc)


if __name__ == "__main__":
    main()
