"""Register, submit and close one AthenaK card run by hand (README.md, Requests: nrpic-run
refuses the shared worktree while other helpers' files are untracked).

    python3 card_run.py submit --purpose TEXT --input F [--input F ...] --wall 00:40:00
                               --athinput PATH -- [athena overrides ...]
    python3 card_run.py finish RUN_ID

submit: writes tracks/A-emd-pbh/runs/<run_id>/manifest.json (status "submitted"), the
batch list <out>/batch.list with one line "<out>/run <athinput> <overrides>", and
submits it with scripts/gpu_batch.sh (ATHENA_EXE = the release card executable, TIME =
--wall, JOB_NAME = run id). finish: reads the Slurm accounting of the job, the status
file of the list and the AthenaK log, records exit status, wall time, card-hours and the
checksums of the output directory.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys

WT = "/data/haiyangw/nrpic/wt/A-emd-pbh"
SCRATCH = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
EXE = "/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena"
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


def mpath(run_id):
    return os.path.join(WT, "tracks/A-emd-pbh/runs", run_id, "manifest.json")


def submit(a):
    sha = git("rev-parse", "HEAD")
    now = dt.datetime.now(dt.timezone.utc)
    run_id = f"A-emd-pbh-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out)
    over = a.overrides[1:] if a.overrides and a.overrides[0] == "--" else a.overrides
    athinput = os.path.abspath(a.athinput)
    lst = os.path.join(out, "batch.list")
    with open(lst, "w") as f:
        f.write(f"{out}/run {athinput} " + " ".join(over) + "\n")
    inputs = [{"path": os.path.abspath(p), "sha256": sha256(p)}
              for p in [athinput, EXE] + a.input]
    env = dict(os.environ, ATHENA_EXE=EXE, TIME=a.wall, JOB_NAME=run_id)
    r = subprocess.run([os.path.join(WT, "scripts", "gpu_batch.sh"), lst], env=env,
                       capture_output=True, text=True, cwd=WT)
    print(r.stdout, r.stderr)
    m = re.search(r"submitted job (\d+)", r.stdout)
    man = {
        "run_id": run_id, "owner": "A-emd-pbh", "track": "A-emd-pbh", "gate": "G2",
        "package": "periodic_threshold", "purpose": a.purpose, "kind": "scouting",
        "command": ["scripts/gpu_batch.sh", lst], "batch_line": open(lst).read().strip(),
        "cwd": WT, "commit": sha,
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "package_dirty": bool(git("status", "--porcelain", "--", PKG))},
        "host": os.uname().nodename, "inputs": inputs, "output_dir": out,
        "outputs": {"dir": f"scratch/A-emd-pbh/{run_id}"},
        "launcher": "batch (scripts/gpu_batch.sh), one card", "slurm_wall": a.wall,
        "slurm_job": m.group(1) if m else None, "cores": 1, "card_hours": None,
        "registered_by": "hand (scripts/card_run.py): nrpic-run refuses the worktree "
                         "while other helpers' untracked files are present",
        "status": "submitted" if m else "submit-failed", "started": now.isoformat(),
    }
    os.makedirs(os.path.dirname(mpath(run_id)), exist_ok=True)
    with open(mpath(run_id), "w") as f:
        json.dump(man, f, indent=1)
        f.write("\n")
    print(run_id)


def finish(a):
    p = mpath(a.run_id)
    man = json.load(open(p))
    job = man.get("slurm_job")
    acct = subprocess.run(["sacct", "-j", str(job), "-X", "-n", "-P", "-o",
                           "JobID,State,ElapsedRaw,Start,End,ExitCode"],
                          capture_output=True, text=True).stdout.strip().splitlines()
    if acct:
        jid, state, el, start, end, ec = acct[0].split("|")
        man["slurm_state"] = state
        man["wall_time_s"] = int(el)
        man["card_hours"] = round(int(el)/3600.0, 4)
        man["slurm_start"], man["slurm_end"], man["slurm_exit"] = start, end, ec
    out = man["output_dir"]
    st = os.path.join(out, "batch.list.status")
    man["batch_status"] = open(st).read().strip() if os.path.exists(st) else None
    log = os.path.join(out, "run", "athena.log")
    if os.path.exists(log):
        tail = open(log, errors="replace").read().splitlines()[-6:]
        man["athena_log_tail"] = tail
    sums = []
    for root, _, files in os.walk(out):
        for fn in sorted(files):
            q = os.path.join(root, fn)
            if os.path.islink(q):
                continue
            sums.append(f"{sha256(q)}  {os.path.relpath(q, out)}")
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        f.write("\n".join(sums) + "\n")
    man["outputs"]["sha256sums"] = "sha256sums.txt"
    man["status"] = a.status
    man["ended"] = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(p, "w") as f:
        json.dump(man, f, indent=1)
        f.write("\n")
    print(json.dumps({k: man.get(k) for k in ("run_id", "slurm_state", "wall_time_s",
                                                "card_hours", "batch_status")}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("submit")
    s.add_argument("--purpose", required=True)
    s.add_argument("--input", action="append", default=[])
    s.add_argument("--wall", default="00:40:00")
    s.add_argument("--athinput", required=True)
    s.add_argument("overrides", nargs=argparse.REMAINDER)
    f = sub.add_parser("finish")
    f.add_argument("run_id")
    f.add_argument("--status", default="completed")
    a = ap.parse_args()
    if a.cmd == "submit":
        submit(a)
    else:
        finish(a)


if __name__ == "__main__":
    main()
