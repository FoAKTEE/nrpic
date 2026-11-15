"""(Adapted from the note package of Track A.) Register and run one local analysis run by hand when harness/bin/nrpic-run refuses.

Writes tracks/D-bh-dress/runs/<run_id>/manifest.json with the fields of
harness/templates/run_manifest.json that apply to a local Python run, runs the command with
NRPIC_RUN_DIR set to scratch/D-bh-dress/<run_id>/, then records exit status, wall time and
sha256sums.txt of the output directory. Run id: D-bh-dress-<YYYYMMDD-HHMMSS UTC>-<commit7>.
Usage (from the worktree root):
  .venv/bin/python tracks/D-bh-dress/note/scripts/handreg.py --purpose TEXT --refusal TEXT -- <command...>
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

SCRATCH = "/data/haiyangw/nrpic/scratch/D-bh-dress"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--refusal", required=True, help="why nrpic-run was not used")
    ap.add_argument("--gate", default="G0")
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    sha = git("rev-parse", "HEAD")
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"D-bh-dress-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out)
    status_pkg = git("status", "--porcelain", "--", "tracks/D-bh-dress/note")
    inputs = [dict(path=p, sha256=sha256(p), bytes=os.path.getsize(p))
              for p in a.input + [c for c in cmd if os.path.isfile(c)]]
    man = {
        "schema": "nrpic-run/1 (by hand)",
        "registered_by": "tracks/D-bh-dress/note/scripts/handreg.py",
        "harness_refusal": a.refusal,
        "run_id": run_id, "track": "D-bh-dress", "gate": a.gate, "kind": "scouting",
        "purpose": a.purpose, "launcher": "local", "command": cmd, "cwd": os.getcwd(),
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "package_dirty": bool(status_pkg), "merge_base_main": git("merge-base", "HEAD", "main")},
        "inputs": inputs, "parents": [],
        "resources": {"cores": 2, "gpus": 0, "walltime_s": None, "gpu_hours": 0.0},
        "outputs": {"dir": f"scratch/D-bh-dress/{run_id}", "sha256sums": "sha256sums.txt"},
        "status": "running", "exit_code": None, "started": now.isoformat(timespec="seconds"), "ended": None,
        "notes": "registered by hand because harness/bin/nrpic-run refused (see harness_refusal)",
    }
    mdir = os.path.join("tracks", "D-bh-dress", "runs", run_id)
    os.makedirs(mdir)
    mpath = os.path.join(mdir, "manifest.json")
    json.dump(man, open(mpath, "w"), indent=1)
    env = dict(os.environ, NRPIC_RUN_ID=run_id, NRPIC_RUN_DIR=out, OMP_NUM_THREADS="2")
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        log.write(f"# hand-registered {run_id} start={man['started']} cwd={os.getcwd()}\n# cmd: {' '.join(cmd)}\n")
        log.flush()
        r = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
        end = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        log.write(f"# exit={r.returncode} end={end}\n")
    lines = []
    for dp, dn, fns in os.walk(out):
        dn.sort()
        for fn in sorted(fns):
            if fn == "sha256sums.txt":
                continue
            full = os.path.join(dp, fn)
            lines.append(f"{sha256(full)}  {os.path.relpath(full, out)}")
    open(os.path.join(out, "sha256sums.txt"), "w").write("\n".join(lines) + "\n")
    man.update(status="completed" if r.returncode == 0 else "failed", exit_code=r.returncode, ended=end)
    man["resources"]["walltime_s"] = round(time.time() - t0, 2)
    man["outputs"]["files"] = len(lines)
    json.dump(man, open(mpath, "w"), indent=1)
    print(f"{run_id}: {man['status']} (exit {r.returncode}); manifest {mpath}; output {out}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
