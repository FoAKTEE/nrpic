#!/usr/bin/env python3
"""Run one script of this package as a registered run of D-bh-dress.

Usage (from the worktree root):
    python3 tracks/D-bh-dress/secondary_infall/register_run.py <script.py> "<purpose>" \
        [--kind scouting|production] [--inputs path ...] -- [script args]

Makes the run id D-bh-dress-<UTC YYYYMMDD-HHMMSS>-<commit7>, the output directory
scratch/D-bh-dress/<run_id>/, runs `python3 <script> --out <dir> [args]` with one thread
per numerical library, and writes tracks/D-bh-dress/runs/<run_id>/manifest.json
(command, cwd, commit, inputs with sha256, outputs with sha256, wall time, cores).
Refuses to run when the package directory has uncommitted changes, so that the commit in
the manifest holds the code that ran.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

from common import HERE, ROOT, FIGSTYLE, sha256

SCRATCH = "/data/haiyangw/nrpic/scratch/D-bh-dress"


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def main():
    argv = sys.argv[1:]
    if "--" in argv:
        k = argv.index("--")
        own, rest = argv[:k], argv[k + 1:]
    else:
        own, rest = argv, []
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("purpose")
    ap.add_argument("--kind", default="scouting")
    ap.add_argument("--inputs", nargs="*", default=[])
    args = ap.parse_args(own)
    script = os.path.abspath(args.script)
    dirty = git("status", "--porcelain", "--", os.path.relpath(HERE, ROOT))
    if dirty:
        sys.exit("uncommitted changes in the package directory; commit first:\n" + dirty)
    sha = git("rev-parse", "HEAD")
    now = datetime.datetime.now(datetime.timezone.utc)
    run_id = f"D-bh-dress-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=False)
    cmd = ["python3", os.path.relpath(script, ROOT), "--out", out, *rest]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", MPLBACKEND="Agg")
    t0 = time.time()
    with open(os.path.join(out, "stdout.txt"), "w") as fo:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=fo, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    end = datetime.datetime.now(datetime.timezone.utc)
    files = sorted(f for f in os.listdir(out) if os.path.isfile(os.path.join(out, f)))
    sums = {f: sha256(os.path.join(out, f)) for f in files}
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        for k, v in sums.items():
            f.write(f"{v}  {k}\n")
    inputs = [script, os.path.join(HERE, "common.py"), FIGSTYLE] + \
        [os.path.abspath(p) for p in args.inputs]
    man = {
        "run_id": run_id, "track": "D-bh-dress", "package": "secondary_infall",
        "gate": "G1", "purpose": args.purpose, "kind": args.kind,
        "command": cmd, "cwd": ROOT,
        "env_overrides": {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                          "MKL_NUM_THREADS": "1"},
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "dirty_package": False},
        "code": {"core_tag": None, "problem": None,
                 "interpreter": "python3 " + sys.version.split()[0]},
        "inputs": [{"path": p, "sha256": sha256(p)} for p in inputs],
        "resources": {"nodes": 1, "cores": 1, "gpus": 0, "card_hours": 0.0,
                      "walltime_s": round(wall, 2), "particles": 0},
        "outputs": {"dir": out, "sha256sums": "sha256sums.txt", "files": files},
        "status": "completed" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "started": f"{now:%Y-%m-%dT%H:%M:%SZ}", "ended": f"{end:%Y-%m-%dT%H:%M:%SZ}",
        "parents": [],
        "notes": "Registered by register_run.py of tracks/D-bh-dress/secondary_infall "
                 "(helper of D-bh-dress). Predictions and outcome: "
                 "tracks/D-bh-dress/secondary_infall/JOURNAL.md.",
    }
    mdir = os.path.join(ROOT, "tracks", "D-bh-dress", "runs", run_id)
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(run_id, man["status"], f"{wall:.1f} s", out)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
