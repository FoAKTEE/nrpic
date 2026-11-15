#!/usr/bin/env python3
"""Run one registered simulation or analysis of the work package "gauge" (owner core).
Registration by hand: `harness/bin/nrpic-run submit` fails for owner core with
KeyError 'outputs' in budget_state (it reads the hand-written manifests of wave 1);
see tracks/core/JOURNAL-gauge.md, entry 1.

    grun.py --purpose TEXT [--kind scouting|production] [--inputs FILE ...]
            [--gpu] [--exe PATH] [--time HH:MM:SS] [--tag NAME]
            (--athinput FILE [athena args ...] | -- command ...)

The run id is core-<YYYYMMDD-HHMMSS>-<commit7> (UTC, decision 0012); outputs go to
scratch/core/<run_id>/ of the main checkout, the manifest to
tracks/core/runs/<run_id>/manifest.json of this worktree (command, cwd, commit, inputs
with sha256, output directory, purpose, kind, wall time, cores or card-hours; the
card-hours are the time between the start and end stamps of the card log, the wall time
includes the wait in the queue).

With --athinput the executable (--exe, a processor build by default) is run as
`athena -i <input> -d <out> <args>` with the output directory as working directory; with
--gpu it goes through scripts/gpu_run.sh (one card, blocking srun).  Otherwise the
command after `--` is run with the output directory as working directory; the string
{out} in its arguments is replaced by that directory.
The last line printed is the run id.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT] + list(args), check=True,
                          capture_output=True, text=True).stdout.strip()


def main():
    argv = sys.argv[1:]
    rest = []
    if "--" in argv:
        i = argv.index("--")
        argv, rest = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--inputs", nargs="*", default=[])
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--exe", default=os.path.join(WT, ".work/build_cpu/src/athena"))
    ap.add_argument("--time", default="00:30:00")
    ap.add_argument("--tag", default="")
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--athinput", nargs="+", default=None)
    ap.add_argument("--source-commit", default="",
                    help="commit the executable was built from, if not HEAD (it names "
                         "the run and is recorded as commit; HEAD goes into head_at_run)")
    a = ap.parse_args(argv)

    head = git("rev-parse", "HEAD")
    commit = git("rev-parse", a.source_commit) if a.source_commit else head
    dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    while True:                          # two runs within one second
        run_id = f"core-{stamp}-{commit[:7]}"
        out = os.path.join(SCRATCH, run_id)
        try:
            os.makedirs(out)
            break
        except FileExistsError:
            time.sleep(1.1)
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")

    inputs = [os.path.abspath(p) for p in a.inputs]
    env = dict(os.environ)
    env.setdefault("OMP_NUM_THREADS", "1")
    if a.athinput is not None:
        inp = os.path.abspath(a.athinput[0])
        exe = os.path.abspath(a.exe)
        inputs = [inp, exe] + inputs
        if a.gpu:
            env["ATHENA_EXE"] = exe
            env["TIME"] = a.time
            env["JOB_NAME"] = "core-gauge"
            cmd = [os.path.join(WT, "scripts/gpu_run.sh"), out, inp] + a.athinput[1:]
        else:
            cmd = [exe, "-i", inp, "-d", out] + a.athinput[1:]
    else:
        cmd = [c.replace("{out}", out) for c in rest]
    if not cmd:
        sys.exit("nothing to run")

    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        rc = subprocess.run(cmd, cwd=out, env=env, stdout=log,
                            stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0

    card_s = 0.0
    if a.gpu:
        # time on the card: from the start and end stamps of the log of gpu_run.sh
        # (the wall time above includes the wait in the queue)
        try:
            with open(os.path.join(out, "athena.log")) as f:
                txt = f.read()
            fmt = "%Y-%m-%dT%H:%M:%S"
            t_a = txt.split("start=", 1)[1][:19]
            t_b = txt.rsplit("end=", 1)[1][:19]
            card_s = (datetime.datetime.strptime(t_b, fmt)
                      - datetime.datetime.strptime(t_a, fmt)).total_seconds()
        except (OSError, IndexError, ValueError):
            card_s = wall

    man = {
        "run_id": run_id,
        "owner": "core",
        "package": "gauge",
        "tag": a.tag,
        "purpose": a.purpose,
        "kind": a.kind,
        "command": cmd,
        "cwd": out,
        "commit": commit,
        "head_at_run": head,
        "worktree_dirty": dirty,
        "inputs": [{"path": p, "sha256": sha256(p)} for p in inputs if os.path.isfile(p)],
        "output_directory": out,
        "wall_time_s": round(wall, 1),
        "cores": a.cores,
        "card_hours": round(card_s / 3600.0, 5) if a.gpu else 0.0,
        "exit_status": rc,
        "started": stamp,
    }
    mdir = os.path.join(WT, "tracks/core/runs", run_id)
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
        f.write("\n")
    print(f"exit {rc}  wall {wall:.1f} s  out {out}")
    print(run_id)
    sys.exit(rc)


if __name__ == "__main__":
    main()
