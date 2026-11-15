"""Run a command as a registered run of D-bh-dress and write its manifest by hand
(nrpic-run refuses a worktree shared with other helpers).

usage: python3 register_run.py --purpose "..." --kind scouting --inputs a b ... \
           [--cores N] [--run-id ID] -- <command ...>
The literal string {OUT} in the command is replaced by the output directory
scratch/D-bh-dress/<run_id>; the manifest goes to tracks/D-bh-dress/runs/<run_id>/.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

WT = Path("/data/haiyangw/nrpic/wt/D-bh-dress")
SCRATCH = Path("/data/haiyangw/nrpic/scratch/D-bh-dress")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout.strip()


def main():
    argv = sys.argv[1:]
    k = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting")
    ap.add_argument("--inputs", nargs="*", default=[])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--parents", nargs="*", default=[])
    ap.add_argument("--notes", default="")
    args = ap.parse_args(argv[:k])
    cmd = argv[k + 1:]
    sha = git("rev-parse", "HEAD")
    now = dt.datetime.now(dt.timezone.utc)
    run_id = args.run_id or f"D-bh-dress-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
    out = SCRATCH / run_id
    out.mkdir(parents=True, exist_ok=True)
    cmd = [c.replace("{OUT}", str(out)) for c in cmd]
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": str(args.cores), "OPENBLAS_NUM_THREADS": str(args.cores)})
    dirty = bool(git("status", "--porcelain", "--", "tracks/D-bh-dress/spike"))
    t0 = time.time()
    with open(out / "stdout.txt", "w") as fo:
        rc = subprocess.run(cmd, cwd=str(WT / "tracks/D-bh-dress/spike"), env=env,
                            stdout=fo, stderr=subprocess.STDOUT).returncode
    t1 = time.time()
    files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    with open(out / "sha256sums.txt", "w") as f:
        for p in files:
            if p != "sha256sums.txt":
                f.write(f"{sha256(out / p)}  {p}\n")
    man = {
        "run_id": run_id, "track": "D-bh-dress", "package": "D-pre-2 spike",
        "purpose": args.purpose, "kind": args.kind, "command": cmd,
        "cwd": str(WT / "tracks/D-bh-dress/spike"),
        "env_overrides": {"OMP_NUM_THREADS": str(args.cores),
                          "OPENBLAS_NUM_THREADS": str(args.cores)},
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "dirty_spike_dir": dirty},
        "inputs": [{"path": str(Path(p).resolve()), "sha256": sha256(p)} for p in args.inputs],
        "resources": {"nodes": 1, "cores": args.cores, "gpus": 0, "card_hours": 0.0,
                      "walltime_s": round(t1 - t0, 2)},
        "outputs": {"dir": str(out), "sha256sums": "sha256sums.txt", "files": files},
        "status": "completed" if rc == 0 else "failed", "exit_code": rc,
        "started": dt.datetime.fromtimestamp(t0, dt.timezone.utc).isoformat(timespec="seconds"),
        "ended": dt.datetime.fromtimestamp(t1, dt.timezone.utc).isoformat(timespec="seconds"),
        "parents": args.parents,
        "notes": args.notes or "Registered by hand with spike/register_run.py.",
    }
    md = WT / "tracks/D-bh-dress/runs" / run_id
    md.mkdir(parents=True, exist_ok=True)
    (md / "manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    print(run_id, "exit", rc, f"{t1 - t0:.1f} s")
    sys.exit(rc)


if __name__ == "__main__":
    main()
