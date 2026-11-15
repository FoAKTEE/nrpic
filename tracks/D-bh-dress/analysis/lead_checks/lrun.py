#!/usr/bin/env python3
"""Run one registered analysis or simulation of the lead re-checks (owner
D-bh-dress) and write its manifest.

    nrun.py --purpose TEXT [--kind scouting|production] [--inputs FILE ...]
            [--cores N] [--tag NAME] -- command ...

run_id = D-bh-dress-<YYYYMMDD-HHMMSS>-<commit7>; the command runs with the output
directory /data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/ as working directory, the
string {out} in its arguments is replaced by that directory, stdout and stderr go to
log.txt there. The manifest goes to tracks/D-bh-dress/runs/<run_id>/manifest.json of this
worktree: command, cwd, commit, worktree_dirty, inputs (path, sha256), output_directory,
purpose, kind, wall_time_s, cores, card_hours (0: processor runs only), exit_status.
The last line printed is the run id.
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
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/D-bh-dress"
RUNS = os.path.join(WT, "tracks", "D-bh-dress", "runs")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT] + list(args), check=True, capture_output=True,
                          text=True).stdout.strip()


def main():
    argv = sys.argv[1:]
    if "--" not in argv:
        sys.exit("usage: nrun.py --purpose TEXT [...] -- command ...")
    i = argv.index("--")
    argv, cmd = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--inputs", nargs="*", default=[])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--tag", default="")
    a = ap.parse_args(argv)
    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--untracked-files=no", "--", "tracks/D-bh-dress/analysis/lead_checks"))
    while True:
        # UTC, as harness/bin/nrpic-run (run ids before 2026-11-15T15Z of this package are
        # local time, UTC-8; see tracks/D-bh-dress/JOURNAL.md, lead entry of 2026-11-15)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
        run_id = f"D-bh-dress-{stamp}-{commit[:7]}"
        out = os.path.join(SCRATCH, run_id)
        try:
            os.makedirs(out)
            break
        except FileExistsError:
            time.sleep(1.1)
    cmd = [c.replace("{out}", out) for c in cmd]
    inputs = [dict(path=os.path.abspath(p), sha256=sha256(p)) for p in a.inputs]
    env = dict(os.environ)
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        env[k] = str(a.cores)
    t0 = time.time()
    with open(os.path.join(out, "log.txt"), "w") as log:
        rc = subprocess.run(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT, env=env).returncode
    wall = time.time() - t0
    man = dict(run_id=run_id, owner="D-bh-dress", package="lead_checks", tag=a.tag,
               purpose=a.purpose, kind=a.kind, command=cmd, cwd=out, commit=commit,
               worktree_dirty=dirty, inputs=inputs, output_directory=out,
               outputs=sorted(os.listdir(out)), wall_time_s=round(wall, 1), cores=a.cores,
               card_hours=0.0, exit_status=rc, started=stamp)
    os.makedirs(os.path.join(RUNS, run_id), exist_ok=True)
    with open(os.path.join(RUNS, run_id, "manifest.json"), "w") as fo:
        json.dump(man, fo, indent=1)
    print(open(os.path.join(out, "log.txt")).read()[-3000:])
    print("exit status", rc, "wall", round(wall, 1), "s")
    print(run_id)


if __name__ == "__main__":
    main()
