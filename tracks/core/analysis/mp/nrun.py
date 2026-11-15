#!/usr/bin/env python3
"""Run AthenaK once and register the run (rule 4 of CLAUDE.md).

    nrun.py --label by_static_n64 --purpose "..." [--kind scouting] [--exe cpu|gpu|PATH]
            --input problems/puncture/by_static.athinput [--file extra ...]
            [--time 00:30:00] [--] block/par=value ...

Run id: core-<UTC YYYYMMDD-HHMMSS>-<commit7>. Outputs: /data/haiyangw/nrpic/scratch/core/
<run_id>/ (the working directory of the run; the input and the extra files are copied
there). Manifest: tracks/core/runs/<run_id>/manifest.json. A card run goes through srun
(partition preempt, one card, one core) and blocks until it ends. The source state is the
commit; the manifest records whether the worktree had uncommitted changes under
athenak/src.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

WT = "/data/haiyangw/nrpic/wt/core-mp"
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
EXES = {"cpu": WT + "/.work/build_cpu/src/athena",
        "gpu": WT + "/.work/build_gpu/src/athena",
        "cpu_base": WT + "/.work/athena_cpu_base",
        "gpu_base": WT + "/.work/athena_gpu_base"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT] + list(args), capture_output=True,
                          text=True, check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--exe", default="cpu")
    ap.add_argument("--input", required=True)
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--time", default="00:30:00")
    ap.add_argument("args", nargs="*")
    a = ap.parse_args()

    exe = EXES.get(a.exe, a.exe)
    on_card = a.exe.startswith("gpu") or "gpu" in os.path.basename(os.path.dirname(
        os.path.dirname(exe)))
    commit = git("rev-parse", "--short=7", "HEAD")
    dirty = git("status", "--porcelain", "--", "athenak/src") != ""
    while True:
        run_id = "core-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-" + commit
        mdir = os.path.join(WT, "tracks/core/runs", run_id)
        try:
            os.makedirs(mdir)
            break
        except FileExistsError:
            time.sleep(1.1)
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out)
    inp = os.path.abspath(a.input)
    inputs = []
    for src in [inp] + [os.path.abspath(f) for f in a.file]:
        dst = os.path.join(out, os.path.basename(src))
        shutil.copy(src, dst)
        inputs.append({"path": os.path.relpath(src, WT) if src.startswith(WT) else src,
                       "sha256": sha256(src)})
    inputs.append({"path": exe, "sha256": sha256(exe), "role": "executable"})
    cmd = [exe, "-i", os.path.basename(inp), "-d", out] + a.args
    if on_card:
        # time stamps inside the allocation: the card time excludes the wait in the queue
        # and the memory of the card is sampled every 5 s into .gpumem (MiB)
        wrap = ('date +%s.%N > .t_start; '
                '(while true; do nvidia-smi --query-gpu=memory.used '
                '--format=csv,noheader,nounits >> .gpumem 2>/dev/null; sleep 5; done) & '
                'smp=$!; "$@"; rc=$?; kill $smp; date +%s.%N > .t_end; exit $rc')
        cmd = ["srun", "-p", "preempt", "--gres=gpu:1", "-c", "1", "-t", a.time,
               "-J", a.label[:12], "/bin/bash", "-c", wrap, "athena"] + cmd
    env = dict(os.environ, OMP_NUM_THREADS="1")
    man = {"run_id": run_id, "label": a.label, "owner": "core", "purpose": a.purpose,
           "kind": a.kind, "command": " ".join(cmd), "cwd": out, "commit": commit,
           "source_dirty": dirty, "inputs": inputs, "output_directory": out,
           "resources": "1 card (A100), 1 core" if on_card else "1 core",
           "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "status": "running"}
    mpath = os.path.join(mdir, "manifest.json")
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    t0 = time.time()
    with open(os.path.join(out, "athena.log"), "w") as log:
        rc = subprocess.run(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT,
                            env=env).returncode
    wall = time.time() - t0
    queued = 0.0
    if on_card:
        try:
            ts = float(open(os.path.join(out, ".t_start")).read())
            te = float(open(os.path.join(out, ".t_end")).read())
            queued = max(0.0, wall - (te - ts))
            wall = te - ts
        except (OSError, ValueError):
            pass
    try:
        mem = [float(v) for v in open(os.path.join(out, ".gpumem")).read().split()]
        man["card_memory_peak_mib"] = max(mem)
    except (OSError, ValueError):
        pass
    man.update({"status": "done" if rc == 0 else "failed", "exit_code": rc,
                "wall_time_s": round(wall, 1), "queue_wait_s": round(queued, 1),
                "card_hours": round(wall / 3600.0, 4) if on_card else 0.0,
                "core_hours": round(wall / 3600.0, 4)})
    with open(mpath, "w") as f:
        json.dump(man, f, indent=1)
    shutil.copy(mpath, os.path.join(out, "manifest.json"))
    print(run_id, a.label, "exit", rc, "wall %.1f s" % wall)
    return rc


if __name__ == "__main__":
    sys.exit(main())
