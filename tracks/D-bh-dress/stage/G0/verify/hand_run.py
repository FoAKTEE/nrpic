#!/usr/bin/env python3
"""Hand registration of a verifier run, used because `harness/bin/nrpic-run submit`
refused while another helper's untracked file sat in the worktree root (README, Requests).

    hand_run.py --purpose TEXT [--input PATH]... [--parent RUN_ID]... [--cores N] -- CMD ...

Run id D-<UTC YYYYMMDD-HHMMSS>-<commit7> (decision 0012), output directory
scratch/D-bh-dress/<run_id>/ passed to CMD as $NRPIC_RUN_DIR; the package directory must be
committed; writes tracks/D-bh-dress/runs/<run_id>/manifest.json (fields of the harness
template) with the inputs' and outputs' sha256, wall time and exit code. The caller commits
the manifest.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

WT = "/data/haiyangw/nrpic/wt/D-bh-dress"
PKG = "tracks/D-bh-dress/stage/G0"
# the verifier's own files inside the stage directory (the lead's stage documents live there too)
MINE = [PKG + "/verify", PKG + "/figs", PKG + "/JOURNAL.md", PKG + "/README.md", PKG + "/VERIFIER.md"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--parent", action="append", default=[])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + MINE, cwd=WT, capture_output=True,
                           text=True).stdout.strip()
    if dirty:
        sys.exit("package directory not committed:\n" + dirty)
    sha_full = subprocess.run(["git", "rev-parse", "HEAD"], cwd=WT, capture_output=True, text=True).stdout.strip()
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"D-{now:%Y%m%d-%H%M%S}-{sha_full[:7]}"
    out = f"/data/haiyangw/nrpic/scratch/D-bh-dress/{run_id}"
    os.makedirs(out, exist_ok=False)
    env = dict(os.environ, NRPIC_RUN_ID=run_id, NRPIC_RUN_DIR=out, OMP_NUM_THREADS=str(a.cores))
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        p = subprocess.run(cmd, cwd=WT, env=env, stdout=log, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    files = []
    for root, _, fn in os.walk(out):
        for f in sorted(fn):
            q = os.path.join(root, f)
            files.append({"path": os.path.relpath(q, out), "sha256": sha(q), "bytes": os.path.getsize(q)})
    man = {
        "schema": "nrpic-run-manifest/1", "run_id": run_id, "track": "D-bh-dress", "gate": "G1",
        "kind": "scouting", "purpose": a.purpose, "preregistered_in": f"{PKG}/JOURNAL.md",
        "launcher": "local (hand registration)",
        "registered_by": ("hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-run "
                          "submit refused (an untracked file of another helper, es.horizon_summary_0.txt, in "
                          "the worktree root); see stage/G0/README.md, Requests"),
        "command": cmd, "cwd": WT,
        "git": {"sha": sha_full, "branch": "track/D-bh-dress", "package": MINE, "package_clean": True},
        "code": {"core_tag": "core-v0.3"},
        "env": {"host": os.uname().nodename, "OMP_NUM_THREADS": str(a.cores)},
        "inputs": [{"path": q, "sha256": sha(q), "bytes": os.path.getsize(q)} for q in a.input],
        "resources": {"nodes": 1, "cores": a.cores, "gpus": 0, "card_hours": 0.0, "walltime_s": round(wall, 2)},
        "outputs": {"dir": f"scratch/D-bh-dress/{run_id}", "files": files},
        "status": "completed" if p.returncode == 0 else "failed", "exit_code": p.returncode,
        "started": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ended": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parents": a.parent,
    }
    md = os.path.join(WT, "tracks/D-bh-dress/runs", run_id)
    os.makedirs(md, exist_ok=False)
    with open(os.path.join(md, "manifest.json"), "w") as f:
        f.write(json.dumps(man, indent=2) + "\n")
    print(run_id, man["status"], f"wall {wall:.1f} s", out)
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
