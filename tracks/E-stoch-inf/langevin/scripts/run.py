#!/usr/bin/env python3
"""Register and execute one analysis run of the langevin package.

    python3 tracks/E-stoch-inf/langevin/scripts/run.py --purpose TEXT --kind scouting \
        --cores N -- python3 tracks/E-stoch-inf/langevin/scripts/<script>.py [args]

Run id: E-stoch-inf-<YYYYMMDD-HHMMSS UTC>-<commit7>. Writes
tracks/E-stoch-inf/runs/<run_id>/manifest.json before the run and completes it afterwards
(wall time, exit status, sha256 of the outputs). The run directory is
scratch/E-stoch-inf/<run_id>/, passed to the script as the environment variable RUN_DIR
(and RUN_ID). Refuses to start when the package code differs from the commit, so the
commit in the manifest is the code that ran. Executed from the worktree root.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

OWNER = "E-stoch-inf"
PKG = "tracks/E-stoch-inf/langevin"
SCRATCH = "/data/haiyangw/nrpic/scratch/E-stoch-inf"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", choices=["scouting", "production"], default="scouting")
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    os.chdir(root)
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", PKG + "/sdn",
                                     PKG + "/scripts"], text=True).strip()
    if dirty:
        sys.exit("refused: package code differs from HEAD:\n" + dirty)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"{OWNER}-{stamp}-{commit[:7]}"
    outdir = os.path.join(SCRATCH, run_id)
    os.makedirs(outdir, exist_ok=False)
    inputs = sorted(set(
        [os.path.join(PKG, "sdn", f) for f in os.listdir(os.path.join(PKG, "sdn")) if f.endswith(".py")]
        + [c for c in cmd if c.endswith(".py") and os.path.exists(c)] + a.input))
    man = dict(run_id=run_id, owner=OWNER, command=" ".join(cmd), cwd=root, commit=commit,
               inputs=[dict(path=p, sha256=sha256(p)) for p in inputs],
               output_dir=outdir, purpose=a.purpose, kind=a.kind, launcher="local",
               cores=a.cores, card_hours=0.0,
               started_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               status="running")
    mdir = os.path.join("tracks", OWNER, "runs", run_id)
    os.makedirs(mdir)
    mpath = os.path.join(mdir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(man, f, indent=2)
    env = dict(os.environ, RUN_DIR=outdir, RUN_ID=run_id, OMP_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NRPIC_CORES=str(a.cores))
    t0 = time.time()
    with open(os.path.join(outdir, "stdout.txt"), "w") as log:
        rc = subprocess.call(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    outs = []
    for dp, _, fs in os.walk(outdir):
        for fn in sorted(fs):
            p = os.path.join(dp, fn)
            outs.append(dict(path=os.path.relpath(p, outdir), sha256=sha256(p)))
    man.update(status="completed" if rc == 0 else "failed", exit_code=rc,
               wall_time_s=round(wall, 1),
               core_hours=round(wall * a.cores / 3600.0, 3),
               finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               outputs=outs)
    with open(mpath, "w") as f:
        json.dump(man, f, indent=2)
    print(run_id, "exit", rc, "wall %.1f s" % wall)
    with open(os.path.join(outdir, "stdout.txt")) as f:
        sys.stdout.write(f.read()[-4000:])
    sys.exit(rc)


if __name__ == "__main__":
    main()
