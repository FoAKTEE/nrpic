#!/usr/bin/env python3
"""Run one analysis script of this package and register it (CLAUDE.md rule 4).

    python3 tracks/A-emd-pbh/newton/run_and_register.py <script.py> "<purpose>" [args...]

from the worktree root. The run id is A-emd-pbh-<UTC YYYYMMDD-HHMMSS>-<commit7>; the
script writes into scratch/A-emd-pbh/<run_id>/ and the manifest goes to
tracks/A-emd-pbh/runs/<run_id>/manifest.json. Refuses to run with uncommitted changes in
the package directory, so that the commit in the manifest is the code that ran.
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PKG = "tracks/A-emd-pbh/newton"
SCRATCH = "/data/haiyangw/nrpic/scratch/A-emd-pbh"


def sha(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    script, purpose, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
    dirty = subprocess.run(["git", "status", "--porcelain", "--", PKG], cwd=ROOT,
                           capture_output=True, text=True).stdout
    dirty = [ln for ln in dirty.splitlines() if ln.endswith(".py")]
    if dirty:
        sys.exit("uncommitted changes in the package code:\n" + "\n".join(dirty))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"A-emd-pbh-{stamp}-{commit[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=True)
    cmd = ["python3", f"{PKG}/{script}", "--out", out] + extra
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(out, "stdout.txt"), "w") as f:
        rc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    inputs = [dict(path=f"{PKG}/{n}", sha256=sha(f"{PKG}/{n}"))
              for n in (script, "tophat.py", "ellipsoid.py")]
    inputs.append(dict(path="python/nrpic/figstyle.py", sha256=sha("python/nrpic/figstyle.py")))
    man = dict(run_id=run_id, owner="A-emd-pbh", helper="newton", command=" ".join(cmd),
               cwd=ROOT, commit=commit, inputs=inputs, output_dir=out + "/",
               purpose=purpose, kind="scouting",
               machine="anta, login node, one processor core (OMP_NUM_THREADS=1)",
               wall_time_s=round(wall, 2), cores=1, card_hours=0.0,
               status="done" if rc == 0 else f"failed (exit {rc})")
    mdir = os.path.join(ROOT, "tracks/A-emd-pbh/runs", run_id)
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(run_id, man["status"], f"{wall:.1f} s")


if __name__ == "__main__":
    main()
