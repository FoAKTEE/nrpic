"""Register and run one processor run by hand (harness/bin/nrpic-run refuses while other
helpers of the same worktree hold untracked files; README.md, Requests).

    python3 register_run.py --purpose TEXT [--kind scouting] [--cores 4] [--input F ...]
                            [--parent RUN_ID] [--prepare-only] -- <command ...>

The token {OUT} in the command is replaced by the output directory
/data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>. Writes
tracks/A-emd-pbh/runs/<run_id>/manifest.json (fields of harness/templates/run_manifest.json
that apply, plus command, cwd, commit, inputs with sha256, output_dir, wall_time_s, cores,
card_hours). With --prepare-only the manifest is written with status "registered" and the
command is not run (card runs: finish them with finish_run.py).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

WT = "/data/haiyangw/nrpic/wt/A-emd-pbh"
SCRATCH = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
PKG = "tracks/A-emd-pbh/periodic_threshold"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT, *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=("scouting", "production"))
    ap.add_argument("--gate", default="G2")
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--parent", action="append", default=[])
    ap.add_argument("--notes", default="")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--card-hours", type=float, default=0.0)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        sys.exit("no command")
    sha = git("rev-parse", "HEAD")
    pkg_dirty = bool(git("status", "--porcelain", "--", PKG))
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"A-emd-pbh-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=False)
    cmd = [c.replace("{OUT}", out) for c in cmd]
    inputs = [{"path": os.path.abspath(p), "sha256": sha256(p)} for p in a.input]
    man = {
        "run_id": run_id, "owner": "A-emd-pbh", "track": "A-emd-pbh", "gate": a.gate,
        "package": "periodic_threshold", "purpose": a.purpose, "kind": a.kind,
        "command": cmd, "cwd": os.getcwd(), "commit": sha,
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "package_dirty": pkg_dirty},
        "host": os.uname().nodename, "inputs": inputs, "output_dir": out,
        "outputs": {"dir": f"scratch/A-emd-pbh/{run_id}"},
        "cores": a.cores, "card_hours": a.card_hours, "parents": a.parent,
        "registered_by": "hand (scripts/register_run.py): nrpic-run refuses the worktree "
                         "while other helpers' untracked files are present",
        "status": "registered", "started": now.isoformat(), "notes": a.notes,
    }
    mdir = os.path.join(WT, "tracks/A-emd-pbh/runs", run_id)
    os.makedirs(mdir, exist_ok=True)
    mpath = os.path.join(mdir, "manifest.json")

    def dump():
        with open(mpath, "w") as f:
            json.dump(man, f, indent=1)
            f.write("\n")
    dump()
    print(f"run_id {run_id}\noutput {out}", flush=True)
    if a.prepare_only:
        return
    env = dict(os.environ)
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[k] = str(a.cores)
    env["NRPIC_RUN_DIR"] = out
    t0 = time.time()
    with open(os.path.join(out, "stdout.log"), "w") as fo:
        rc = subprocess.run(cmd, stdout=fo, stderr=subprocess.STDOUT, env=env).returncode
    man["wall_time_s"] = round(time.time() - t0, 2)
    man["exit_code"] = rc
    man["status"] = "completed" if rc == 0 else "failed"
    man["ended"] = dt.datetime.now(dt.timezone.utc).isoformat()
    sums = []
    for root, _, files in os.walk(out):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            sums.append(f"{sha256(p)}  {os.path.relpath(p, out)}")
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        f.write("\n".join(sums) + "\n")
    man["outputs"]["sha256sums"] = "sha256sums.txt"
    dump()
    print(f"exit {rc}, wall {man['wall_time_s']} s")
    sys.exit(rc)


if __name__ == "__main__":
    main()
