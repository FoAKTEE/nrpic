#!/usr/bin/env python3
"""Register and run one lead run by hand.

`harness/bin/nrpic-run submit` stops with KeyError 'dir' on this branch, because the
helpers' hand-written manifests (schema "nrpic-run-manifest/1 (by hand)") have no
outputs.dir field (reported to orch in the outbox). This script writes the same fields:

    python3 tracks/C-sidm/review/register.py --purpose TEXT [--kind scouting] [--input PATH ...]
                                             [--cores N] -- <command ...>

run_id = C-sidm-<UTC YYYYMMDD-HHMMSS>-<commit7>; manifest in tracks/C-sidm/runs/<run_id>/;
output in scratch/C-sidm/<run_id>/ (NRPIC_RUN_DIR, @OUT in the command); records exit
status, wall time, cores, card-hours (0 for processor runs) and the sha256 of every output.
Refuses to start if tracks/C-sidm has uncommitted changes (the commit must be the code run).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/C-sidm"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--card-hours", type=float, default=0.0)
    ap.add_argument("--notes", default="")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    dirty = subprocess.check_output(["git", "-C", WT, "status", "--porcelain", "--",
                                     "tracks/C-sidm"], text=True)
    if dirty.strip():
        sys.exit("tracks/C-sidm has uncommitted changes; commit first:\n" + dirty)
    commit = subprocess.check_output(["git", "-C", WT, "rev-parse", "HEAD"], text=True).strip()
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"C-sidm-{now:%Y%m%d-%H%M%S}-{commit[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out)
    cmd = [c.replace("@OUT", out) for c in cmd]
    inputs = {p: sha256(os.path.join(WT, p) if not os.path.isabs(p) else p) for p in a.input}
    man = dict(schema="nrpic-run-manifest/1 (by hand)", run_id=run_id, owner="C-sidm",
               package="review (lead)", kind=a.kind, purpose=a.purpose, command=cmd, cwd=WT,
               commit=commit, inputs=inputs, output_dir=out, outputs=dict(dir=out),
               cores=a.cores, card_hours=a.card_hours, notes=a.notes,
               started_utc=now.isoformat(), status="running")
    mdir = os.path.join(WT, "tracks", "C-sidm", "runs", run_id)
    os.makedirs(mdir)
    mpath = os.path.join(mdir, "manifest.json")
    json.dump(man, open(mpath, "w"), indent=1)
    env = dict(os.environ, NRPIC_RUN_DIR=out, OMP_NUM_THREADS=str(a.cores),
               OPENBLAS_NUM_THREADS=str(a.cores), MKL_NUM_THREADS=str(a.cores))
    print(run_id, "started", flush=True)
    t0 = time.time()
    with open(os.path.join(out, "stdout.log"), "w") as lo:
        rc = subprocess.call(cmd, cwd=WT, env=env, stdout=lo, stderr=subprocess.STDOUT)
    man["wall_time_s"] = round(time.time() - t0, 1)
    man["exit_status"] = rc
    man["status"] = "completed" if rc == 0 else "failed"
    man["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    man["outputs_sha256"] = {os.path.relpath(os.path.join(r, f), out):
                             sha256(os.path.join(r, f))
                             for r, _, fs in os.walk(out) for f in sorted(fs)
                             if f != "stdout.log" or r != out}
    json.dump(man, open(mpath, "w"), indent=1)
    print(run_id, man["status"], man["wall_time_s"], "s", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
