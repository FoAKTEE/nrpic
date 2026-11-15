#!/usr/bin/env python3
"""Register and run one run of this package by hand (CLAUDE.md rule 4), for when
`harness/bin/nrpic-run submit` refuses: it requires a clean worktree, and the other helpers
of A-emd-pbh keep untracked files in the same worktree while they work (README, Requests).

    register.py local --purpose TEXT [--kind scouting] [--cores N] [--input F ...] -- CMD ...
    register.py batch --purpose TEXT --list LIST [--wall hh:mm:ss] [--exe EXE] [--input F ...]
    register.py finish RUN_ID

from the worktree root. Run id A-emd-pbh-<UTC YYYYMMDD-HHMMSS>-<commit7>; output directory
scratch/A-emd-pbh/<run_id>/ (exported to the command as NRPIC_RUN_DIR); manifest
tracks/A-emd-pbh/runs/<run_id>/manifest.json with command, cwd, commit, inputs with
sha256, output directory, purpose, kind, cores or card-hours, wall time, exit status.
`local` blocks until the command ends and then completes the manifest. `batch` submits
the list (lines `<name> <athinput> [athena args]`) with scripts/gpu_batch.sh, one Slurm
job on one card; `finish` reads the job's elapsed time from sacct, checksums the outputs
and completes the manifest. Refuses to start when this package's code is uncommitted.
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
GPU_EXE = "/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena"
WHY = ("registered by hand: harness/bin/nrpic-run submit refused (worktree not clean: "
       "untracked files of other helpers of A-emd-pbh in the same worktree)")


def sha(path):
    h = hashlib.sha256()
    with open(path if os.path.isabs(path) else os.path.join(ROOT, path), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def new_run():
    dirty = [ln for ln in git("status", "--porcelain", "--", PKG).splitlines()
             if not ln.endswith("/")]
    if dirty:
        sys.exit("uncommitted changes in the package:\n" + "\n".join(dirty))
    commit = git("rev-parse", "HEAD")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"A-emd-pbh-{stamp}-{commit[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=False)
    return run_id, commit, out


def mpath(run_id):
    return os.path.join(ROOT, "tracks/A-emd-pbh/runs", run_id, "manifest.json")


def write(man):
    p = mpath(man["run_id"])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(man, f, indent=1)
        f.write("\n")


def checksums(out):
    lines = []
    for dp, _, fns in os.walk(out):
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            if os.path.islink(p) or fn.endswith(".exe") or fn == "sha256sums.txt":
                continue
            lines.append(f"{sha(p)}  {os.path.relpath(p, out)}")
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        f.write("\n".join(sorted(lines, key=lambda s: s.split("  ")[1])) + "\n")
    return len(lines), sha(os.path.join(out, "sha256sums.txt"))


def parse(argv):
    o = dict(purpose=None, kind="scouting", cores=1, inputs=[], list=None, wall="00:25:00",
             exe=GPU_EXE, cmd=[])
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--":
            o["cmd"] = argv[i + 1:]
            break
        key = a.lstrip("-").replace("-", "_")
        if key == "input":
            o["inputs"].append(argv[i + 1])
        elif key in ("purpose", "kind", "list", "wall", "exe"):
            o[key] = argv[i + 1]
        elif key == "cores":
            o["cores"] = int(argv[i + 1])
        else:
            sys.exit(f"unknown option {a}")
        i += 2
    if not o["purpose"]:
        sys.exit("--purpose is required")
    return o


def base_manifest(run_id, commit, out, o, launcher):
    inputs = [dict(path=p, sha256=sha(p)) for p in o["inputs"]]
    return dict(run_id=run_id, owner="A-emd-pbh", helper="newton", launcher=launcher,
                kind=o["kind"], purpose=o["purpose"], commit=commit,
                branch=git("rev-parse", "--abbrev-ref", "HEAD"), cwd=ROOT, inputs=inputs,
                outputs=dict(dir=os.path.relpath(out, "/data/haiyangw/nrpic")),
                output_dir=out + "/", registered=datetime.datetime.now(
                    datetime.timezone.utc).isoformat(timespec="seconds"),
                machine="anta", notes=WHY)


def local(argv):
    o = parse(argv)
    if not o["cmd"]:
        sys.exit("give the command after --")
    run_id, commit, out = new_run()
    man = base_manifest(run_id, commit, out, o, "local")
    for a in o["cmd"][1:]:
        if os.path.isfile(os.path.join(ROOT, a)) and not any(x["path"] == a for x in man["inputs"]):
            man["inputs"].append(dict(path=a, sha256=sha(a)))
    man.update(command=o["cmd"], cores=o["cores"], card_hours=0.0, status="running")
    write(man)
    print(f"registered {run_id}; output {out}", flush=True)
    env = dict(os.environ, NRPIC_RUN_DIR=out, NRPIC_RUN_ID=run_id,
               OMP_NUM_THREADS=str(o["cores"]), OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               MPLCONFIGDIR=os.path.join(SCRATCH, "tmp", "mpl"))
    t0 = time.time()
    with open(os.path.join(out, "run.log"), "w") as log:
        rc = subprocess.run(o["cmd"], cwd=ROOT, env=env, stdout=log,
                            stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    nfiles, ssum = checksums(out)
    man.update(status="completed" if rc == 0 else "failed", exit_code=rc,
               wall_time_s=round(wall, 1), core_hours=round(wall * o["cores"] / 3600.0, 4),
               ended=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               sha256sums="sha256sums.txt", sha256sums_sha256=ssum, n_output_files=nfiles)
    write(man)
    print(f"{run_id} {man['status']} {wall:.1f} s", flush=True)
    return rc


def batch(argv):
    o = parse(argv)
    if not o["list"]:
        sys.exit("--list is required")
    run_id, commit, out = new_run()
    entries = []
    with open(o["list"]) as f:
        for ln in f:
            s = ln.strip()
            if s and not s.startswith("#"):
                parts = s.split()
                entries.append(parts)
    lst = os.path.join(out, "batch.list")
    with open(lst, "w") as f:
        for parts in entries:
            f.write(" ".join([os.path.join(out, parts[0])] + parts[1:]) + "\n")
    man = base_manifest(run_id, commit, out, o, "batch")
    man["inputs"] += [dict(path=o["list"], sha256=sha(o["list"])), dict(path=o["exe"], sha256=sha(o["exe"]))]
    decks = sorted({p[1] for p in entries})
    man["inputs"] += [dict(path=d, sha256=sha(d)) for d in decks]
    man.update(command=[os.path.join(ROOT, "scripts", "gpu_batch.sh"), lst],
               batch_entries=[dict(name=p[0], input=p[1], args=p[2:]) for p in entries],
               exe=o["exe"], wall_limit=o["wall"], cores=1, status="submitted")
    env = dict(os.environ, ATHENA_EXE=o["exe"], TIME=o["wall"], JOB_NAME=run_id,
               PARTITION="preempt")
    r = subprocess.run(man["command"], cwd=ROOT, env=env, capture_output=True, text=True)
    print(r.stdout, r.stderr)
    ids = [w for w in r.stdout.split() if w.isdigit()]
    man["slurm_job_ids"] = ids[:1]
    if r.returncode != 0 or not ids:
        man["status"] = "failed (submission)"
    write(man)
    print(f"registered {run_id}; job {ids[:1]}; output {out}")
    return r.returncode


def finish(run_id):
    p = mpath(run_id)
    with open(p) as f:
        man = json.load(f)
    out = man["output_dir"].rstrip("/")
    if man["launcher"] == "batch" and man.get("slurm_job_ids"):
        jid = man["slurm_job_ids"][0]
        r = subprocess.run(["sacct", "-j", jid, "-X", "-n", "-P", "-o",
                            "State,ElapsedRaw,Start,End"], capture_output=True, text=True)
        st, el, start, end = r.stdout.strip().split("\n")[0].split("|")
        man.update(slurm_state=st, wall_time_s=int(el), card_hours=round(int(el) / 3600.0, 4),
                   started=start, ended=end)
        status_file = os.path.join(out, "batch.list.status")
        if os.path.exists(status_file):
            man["entry_status"] = open(status_file).read().split("\n")[:-1]
        man["status"] = "completed" if st == "COMPLETED" else st.lower()
    nfiles, ssum = checksums(out)
    man.update(sha256sums="sha256sums.txt", sha256sums_sha256=ssum, n_output_files=nfiles)
    write(man)
    print(json.dumps({k: man[k] for k in ("run_id", "status", "wall_time_s") if k in man}))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "local":
        sys.exit(local(sys.argv[2:]))
    if cmd == "batch":
        sys.exit(batch(sys.argv[2:]))
    if cmd == "finish":
        finish(sys.argv[2])
        sys.exit(0)
    sys.exit(__doc__)
