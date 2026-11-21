#!/usr/bin/env python3
"""Card runs of the verify package, registered by hand (harness/bin/nrpic-run submit stops
with KeyError 'outputs' on wave-1 manifests; see README.md, Requests).

    cards.py submit --list JOB.list --purpose TEXT [--wall 00:50:00] [--parent RUN_ID]
    cards.py finish RUN_ID

submit: one Slurm job on one card through scripts/gpu_batch.sh, the lines of JOB.list
("<name> <athinput> <athena args>") run one after another into
scratch/core/<run_id>/<name>/; writes tracks/core/runs/<run_id>/manifest.json (command,
cwd, commit, inputs with sha256: input decks, files named on the command lines, the
executable; output directory; purpose; kind; Slurm job).
finish: reads the athena logs (start header, "cpu time used", exit status of each line
from the batch status file) and sacct, and records wall time, card-hours, state.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

WT = Path(__file__).resolve().parents[4]
SCRATCH = Path("/data/haiyangw/nrpic/scratch/core")
RUNS = WT / "tracks" / "core" / "runs"
EXE_GPU = Path("/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def commit7():
    return subprocess.run(["git", "-C", str(WT), "rev-parse", "--short=7", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def new_run_id():
    while True:
        now = dt.datetime.now(dt.timezone.utc)
        rid = f"core-{now:%Y%m%d-%H%M%S}-{commit7()}"
        if not (SCRATCH / rid).exists():
            return rid, now
        time.sleep(1.0)


def mpath(rid):
    return RUNS / rid / "manifest.json"


def write(rid, man):
    mpath(rid).parent.mkdir(parents=True, exist_ok=True)
    mpath(rid).write_text(json.dumps(man, indent=1) + "\n")


def submit(a):
    rid, now = new_run_id()
    out = SCRATCH / rid
    out.mkdir(parents=True)
    lines, inputs, seen = [], [], set()
    for raw in Path(a.list).read_text().splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        name, inp, *args = raw.split()
        lines.append(" ".join([str(out / name), inp] + args))
        files = [inp] + [v.split("=", 1)[1] for v in args
                         if "=" in v and os.path.isfile(v.split("=", 1)[1])]
        for f in files:
            if f not in seen:
                seen.add(f)
                inputs.append(dict(path=f, sha256=sha(f)))
    inputs.append(dict(path=str(EXE_GPU), sha256=sha(EXE_GPU), role="executable"))
    lst = out / "batch.list"
    lst.write_text("\n".join(lines) + "\n")
    env = dict(os.environ, ATHENA_EXE=str(EXE_GPU), TIME=a.wall, JOB_NAME="core-verify2")
    cmd = [str(WT / "scripts" / "gpu_batch.sh"), str(lst)]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
    m = re.search(r"submitted job (\d+)", r.stdout)
    man = dict(run_id=rid, owner="core", package="verify", kind=a.kind, gate="G2",
               purpose=a.purpose, command=cmd, batch_lines=lines, cwd=str(WT),
               commit=commit7(), inputs=inputs, output_directory=str(out),
               parents=a.parent, slurm_job=m.group(1) if m else None,
               slurm_wall_limit=a.wall, state="submitted",
               submitted_utc=now.strftime("%Y-%m-%dT%H:%M:%SZ"), card_hours=None,
               registration="by hand (tracks/core/verify/ladder2/cards.py)")
    write(rid, man)
    print(r.stdout.strip())
    print(rid)


def log_info(d):
    logs = sorted(d.glob("athena.2*.log"))
    if not logs:
        return None
    txt = logs[-1].read_text(errors="replace")
    st = re.search(r"start=(\S+)", txt)
    cpu = re.search(r"cpu time used\s*=\s*(\S+)", txt)
    last = re.findall(r"time=(\S+) cycle=(\d+)", txt)
    return dict(log=str(logs[-1]), start=st.group(1) if st else None,
                cpu_time_s=float(cpu.group(1)) if cpu else None,
                finished=bool(cpu), last_time=float(last[-1][0]) if last else None)


def finish(a):
    man = json.loads(mpath(a.run_id).read_text())
    out = Path(man["output_directory"])
    status = (out / "batch.list.status")
    st = status.read_text().splitlines() if status.exists() else []
    runs = {}
    for line in man["batch_lines"]:
        d = Path(line.split()[0])
        info = log_info(d) or {}
        rc = [s.split()[1] for s in st if s.endswith(" " + str(d))]
        info["rc"] = rc[-1] if rc else None
        runs[d.name] = info
    job = man.get("slurm_job")
    el = None
    if job:
        r = subprocess.run(["sacct", "-j", job, "-X", "-n", "-o", "ElapsedRaw,State"],
                           capture_output=True, text=True)
        f = r.stdout.split()
        if f:
            el = int(f[0])
            man["slurm_state"] = f[1]
    man["runs"] = runs
    man["wall_time_s"] = el
    man["card_hours"] = round(el / 3600.0, 4) if el else None
    done = all(v.get("finished") for v in runs.values())
    man["state"] = "finished" if done else "incomplete"
    man["finished_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    write(a.run_id, man)
    print(json.dumps(dict(state=man["state"], card_hours=man["card_hours"], runs=runs),
                     indent=1))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("submit")
    s.add_argument("--list", required=True)
    s.add_argument("--purpose", required=True)
    s.add_argument("--wall", default="00:50:00")
    s.add_argument("--kind", default="scouting")
    s.add_argument("--parent", action="append", default=[])
    f = sp.add_parser("finish")
    f.add_argument("run_id")
    a = ap.parse_args()
    submit(a) if a.cmd == "submit" else finish(a)


if __name__ == "__main__":
    sys.exit(main())
