#!/usr/bin/env python3
"""Register and run one analysis run of this package on the processors.

    python3 runreg.py --purpose TEXT [--kind scouting] [--cores 4] [--input PATH ...] \
        -- python3 make_equilibria.py --out {out}

Creates run_id = C-sidm-<YYYYMMDD-HHMMSS UTC>-<commit7>, the output directory
scratch/C-sidm/<run_id>/ (substituted for {out} in the command), runs the command in this
directory with OMP_NUM_THREADS = cores, and writes tracks/C-sidm/runs/<run_id>/manifest.json
(command, cwd, commit, inputs with sha256, output directory, purpose, kind, wall time,
cores, core-hours, card-hours = 0) and sha256sums.txt of the outputs. It does not commit.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HOME = "/data/haiyangw/nrpic"
OWNER = "C-sidm"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", WT, *a], capture_output=True, text=True).stdout.strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--purpose", required=True)
    p.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    p.add_argument("--cores", type=int, default=4)
    p.add_argument("--input", action="append", default=[])
    p.add_argument("--parent", action="append", default=[])
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    a = p.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        p.error("no command")
    sha = git("rev-parse", "HEAD")
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"{OWNER}-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
    out = os.path.join(HOME, "scratch", OWNER, run_id)
    os.makedirs(out)
    cmd = [c.replace("{out}", out) for c in cmd]
    # inputs: the package sources plus the files named
    srcs = sorted(f for f in os.listdir(HERE) if f.endswith(".py"))
    inputs = [os.path.join(HERE, f) for f in srcs]
    inputs += [os.path.join(WT, "python", "nrpic", f) for f in ("io.py", "sampling.py", "st_cluster.py",
                                                                 "figstyle.py")]
    inputs += [os.path.abspath(f) for f in a.input]
    dirty = git("status", "--porcelain", "--", os.path.relpath(HERE, WT))
    env = dict(os.environ, OMP_NUM_THREADS=str(a.cores), OPENBLAS_NUM_THREADS=str(a.cores),
               MKL_NUM_THREADS=str(a.cores), NRPIC_RUN_ID=run_id, NRPIC_RUN_DIR=out)
    man = dict(run_id=run_id, track=OWNER, package="equilibria", command=" ".join(cmd), cwd=HERE,
               commit=sha, branch=git("rev-parse", "--abbrev-ref", "HEAD"),
               package_dirty=bool(dirty), package_status=dirty.splitlines(),
               inputs=[dict(path=os.path.relpath(f, WT) if f.startswith(WT) else f,
                            sha256=sha256(f)) for f in inputs],
               output_dir=os.path.relpath(out, HOME), purpose=a.purpose, kind=a.kind,
               cores=a.cores, card_hours=0.0, parents=a.parent,
               env={k: env[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS")},
               started_utc=now.isoformat(timespec="seconds"), status="running")
    mdir = os.path.join(WT, "tracks", OWNER, "runs", run_id)
    os.makedirs(mdir)
    mpath = os.path.join(mdir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    t0 = time.time()
    with open(os.path.join(out, "stdout.log"), "w") as lo:
        rc = subprocess.run(cmd, cwd=HERE, env=env, stdout=lo, stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    sums = []
    for root, _, files in os.walk(out):
        for fn in sorted(files):
            fp = os.path.join(root, fn)
            if fn != "sha256sums.txt":
                sums.append(f"{sha256(fp)}  {os.path.relpath(fp, out)}")
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        f.write("\n".join(sums) + "\n")
    man.update(status="done" if rc == 0 else "failed", exit_code=rc,
               finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               wall_time_s=round(wall, 1), core_hours=round(wall * a.cores / 3600.0, 4),
               outputs=dict(files=len(sums), sha256sums="sha256sums.txt",
                            sha256sums_sha256=sha256(os.path.join(out, "sha256sums.txt"))))
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    print(run_id)
    print(open(os.path.join(out, "stdout.log")).read()[-4000:])
    return rc


if __name__ == "__main__":
    sys.exit(main())
