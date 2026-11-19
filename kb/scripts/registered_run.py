#!/usr/bin/env python3
"""Run a command as a registered run of owner kb (CLAUDE.md rule 4; harness/RULES.md).

    python3 -I kb/scripts/registered_run.py --purpose TEXT [--kind scouting|production]
        [--input PATH ...] [--detach] -- COMMAND ARGS...

run_id = kb-<UTC YYYYMMDD-HHMMSS>-<commit7 of the worktree HEAD>. Output directory
scratch/kb/<run_id>/ (stdout.log, stderr.log); the literal `{run_dir}` in the command is
replaced by it. The manifest goes to tracks/kb/runs/<run_id>/manifest.json with command,
cwd, commit, inputs with sha256, output directory, purpose, kind, wall time, cores.
--detach starts the command in its own session (it outlives this process), records its
process id and status "running"; whoever finds it finished fills wall time and exit code
(`--finish RUN_ID --exit-code N`).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.dirname(os.path.dirname(HERE))
HOME = "/data/haiyangw/nrpic"
SCRATCH = os.path.join(HOME, "scratch", "kb")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def commit():
    out = subprocess.run(["git", "-C", WORKTREE, "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    dirty = subprocess.run(["git", "-C", WORKTREE, "status", "--porcelain", "--", "kb"],
                           capture_output=True, text=True).stdout.strip()
    return out.stdout.strip(), bool(dirty)


def manifest_path(run_id):
    return os.path.join(WORKTREE, "tracks", "kb", "runs", run_id, "manifest.json")


def write_manifest(run_id, m):
    p = manifest_path(run_id)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w") as f:
        json.dump(m, f, indent=1)
        f.write("\n")
    os.replace(p + ".tmp", p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose")
    ap.add_argument("--kind", default="scouting", choices=("scouting", "production"))
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--detach", action="store_true")
    ap.add_argument("--finish", metavar="RUN_ID")
    ap.add_argument("--exit-code", type=int)
    ap.add_argument("--note")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()

    if a.finish:
        p = manifest_path(a.finish)
        m = json.load(open(p))
        log = os.path.join(m["output_dir"], "stdout.log")
        end = os.path.getmtime(log) if os.path.exists(log) else time.time()
        m["wall_time_s"] = round(end - m["started_unix"], 1)
        m["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end))
        m["exit_code"] = a.exit_code
        m["status"] = "finished"
        if a.note:
            m["note"] = a.note
        write_manifest(a.finish, m)
        print(p)
        return 0

    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd or not a.purpose:
        ap.error("need --purpose and a command after --")
    sha, dirty = commit()
    t0 = time.time()
    run_id = f"kb-{time.strftime('%Y%m%d-%H%M%S', time.gmtime(t0))}-{sha[:7]}"
    run_dir = os.path.join(SCRATCH, run_id)
    os.makedirs(run_dir)
    cmd = [c.replace("{run_dir}", run_dir) for c in cmd]
    m = {"run_id": run_id, "owner": "kb", "command": cmd, "cwd": os.getcwd(), "commit": sha,
         "worktree_dirty_kb": dirty,
         "inputs": [{"path": os.path.abspath(p), "sha256": sha256(p)} for p in a.input],
         "output_dir": run_dir, "purpose": a.purpose, "kind": a.kind, "cores": a.cores, "card_hours": 0,
         "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)), "started_unix": t0}
    out = open(os.path.join(run_dir, "stdout.log"), "wb")
    err = open(os.path.join(run_dir, "stderr.log"), "wb")
    env = dict(os.environ, OMP_NUM_THREADS=str(a.cores), RUN_DIR=run_dir, RUN_ID=run_id)
    if a.detach:
        p = subprocess.Popen(cmd, stdout=out, stderr=err, stdin=subprocess.DEVNULL, env=env,
                             start_new_session=True)
        m.update({"status": "running", "pid": p.pid, "wall_time_s": None})
        write_manifest(run_id, m)
        print(json.dumps({"run_id": run_id, "pid": p.pid, "run_dir": run_dir,
                          "manifest": manifest_path(run_id)}))
        return 0
    rc = subprocess.run(cmd, stdout=out, stderr=err, env=env).returncode
    m.update({"status": "finished", "exit_code": rc, "wall_time_s": round(time.time() - t0, 2),
              "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    write_manifest(run_id, m)
    print(json.dumps({"run_id": run_id, "exit_code": rc, "run_dir": run_dir, "manifest": manifest_path(run_id)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
