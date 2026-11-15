#!/usr/bin/env python3
"""Registration by hand of the runs of this package, used when `harness/bin/nrpic-run`
refuses (the worktree is shared with other helpers whose files are uncommitted, so it is
rarely clean). Writes tracks/A-emd-pbh/runs/<run_id>/manifest.json with the fields of
CLAUDE.md rule 4 (command, cwd, commit, inputs with sha256, output directory under
scratch/A-emd-pbh/<run_id>/, purpose, kind, wall time, cores or card-hours), in the
schema of the harness as far as it applies, and "registered_by": "runs_ball/runreg.py".

    runreg.py local --purpose TEXT [--input F ...] [--cores N] [--parent ID ...] -- cmd ...
        runs cmd with $NRPIC_RUN_DIR set to the output directory (cwd = worktree root),
        records wall time, exit code and sha256 sums of the outputs;
    runreg.py card --purpose TEXT --list FILE [--input F ...] [--exe EXE] [--wall hh:mm:ss]
        submits the batch list through scripts/gpu_batch.sh (one Slurm job, one card; the
        names of the list become directories under the output directory; `@RUN@` in the
        list is replaced by the output directory);
    runreg.py finish RUN_ID   records the end of a card run (sacct elapsed, card-hours).
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

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OWNER = "A-emd-pbh"
SCR = f"/data/haiyangw/nrpic/scratch/{OWNER}"
RUNS = os.path.join(WT, "tracks", OWNER, "runs")
GPU_EXE = "/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena"


def sh(*a):
    return subprocess.run(a, cwd=WT, capture_output=True, text=True, check=True).stdout.strip()


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_id():
    c = sh("git", "rev-parse", "--short=7", "HEAD")
    for _ in range(100):
        rid = f"{OWNER}-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S')}-{c}"
        if not os.path.exists(os.path.join(RUNS, rid)) and not os.path.exists(os.path.join(SCR, rid)):
            return rid
        time.sleep(1.1)
    raise SystemExit("no free run id")


def inputs_of(paths, role="input"):
    out = []
    for p in paths:
        ap = p if os.path.isabs(p) else os.path.join(WT, p)
        out.append(dict(path=p, role=role, sha256=sha(ap), bytes=os.path.getsize(ap)))
    return out


def base_manifest(rid, a, launcher, command, cores, card):
    outdir = os.path.join(SCR, rid)
    dirty = sh("git", "status", "--porcelain", "--", f"tracks/{OWNER}/runs_ball")
    return dict(schema="nrpic-run/1 (by hand)", registered_by="tracks/A-emd-pbh/runs_ball/runreg.py",
                harness_refusal=a.refusal, run_id=rid, track=OWNER, gate="G2", kind=a.kind,
                purpose=a.purpose, launcher=launcher, command=command, cwd=WT if launcher == "local" else outdir,
                git=dict(sha=sh("git", "rev-parse", "HEAD"), branch=sh("git", "rev-parse", "--abbrev-ref", "HEAD"),
                         package_dirty=bool(dirty)),
                inputs=inputs_of(a.input), parents=a.parent,
                resources=dict(cores=cores, gpus=1 if card else 0, wall_limit=getattr(a, "wall", None),
                               walltime_s=None, gpu_hours=None),
                outputs=dict(dir=os.path.relpath(outdir, "/data/haiyangw/nrpic"), sha256sums="sha256sums.txt"),
                status="running" if launcher == "local" else "submitted", exit_code=None,
                registered=now(), started=None, ended=None, notes=a.notes)


def write(rid, m):
    d = os.path.join(RUNS, rid)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "manifest.json"), "w") as f:
        json.dump(m, f, indent=2)


def read(rid):
    with open(os.path.join(RUNS, rid, "manifest.json")) as f:
        return json.load(f)


def sums(outdir, skip_ext=(".rst",)):
    lines = []
    for root, _, files in os.walk(outdir):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            if fn == "sha256sums.txt" or fn.endswith(skip_ext) or os.path.getsize(p) > 2_000_000_000:
                continue
            lines.append(f"{sha(p)}  {os.path.relpath(p, outdir)}")
    with open(os.path.join(outdir, "sha256sums.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return len(lines)


def cmd_local(a):
    rid = new_id()
    outdir = os.path.join(SCR, rid)
    os.makedirs(outdir)
    m = base_manifest(rid, a, "local", a.cmd, a.cores, False)
    m["started"] = now()
    write(rid, m)
    print(f"registered {rid}; output {outdir}", flush=True)
    env = dict(os.environ, NRPIC_RUN_DIR=outdir, NRPIC_RUN_ID=rid, OMP_NUM_THREADS=str(a.cores),
               OPENBLAS_NUM_THREADS=str(a.cores), MKL_NUM_THREADS=str(a.cores))
    cmd = [c.replace("$NRPIC_RUN_DIR", outdir) for c in a.cmd]
    t0 = time.time()
    with open(os.path.join(outdir, "run.log"), "w") as log:
        r = subprocess.run(cmd, cwd=WT, env=env, stdout=log, stderr=subprocess.STDOUT)
    m["resources"]["walltime_s"] = round(time.time() - t0, 1)
    m["exit_code"] = r.returncode
    m["status"] = "completed" if r.returncode == 0 else "failed"
    m["ended"] = now()
    m["outputs"]["files"] = sums(outdir)
    write(rid, m)
    print(f"{rid}: exit {r.returncode}, {m['resources']['walltime_s']} s")
    print(open(os.path.join(outdir, "run.log")).read()[-3000:])
    return r.returncode


def cmd_card(a):
    rid = new_id()
    outdir = os.path.join(SCR, rid)
    os.makedirs(outdir)
    lst = os.path.join(outdir, "batch.list")
    entries = []
    with open(a.list) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            s = s.replace("@RUN@", outdir)
            parts = s.split()
            entries.append(dict(name=parts[0], input=parts[1], args=parts[2:]))
    with open(lst, "w") as f:
        for e in entries:
            f.write(" ".join([os.path.join(outdir, e["name"]), e["input"]] + e["args"]) + "\n")
    m = base_manifest(rid, a, "batch", ["scripts/gpu_batch.sh", lst], 1, True)
    m["inputs"] += inputs_of([a.exe], "exe") + inputs_of([lst], "list")
    for e in entries:
        if os.path.exists(e["input"]):
            m["inputs"] += inputs_of([e["input"]], f"athinput:{e['name']}")
    m["batch_entries"] = entries
    env = dict(os.environ, ATHENA_EXE=a.exe, TIME=a.wall, JOB_NAME=rid, PARTITION="preempt")
    r = subprocess.run([os.path.join(WT, "scripts", "gpu_batch.sh"), lst], cwd=WT, env=env,
                       capture_output=True, text=True)
    ids = re.findall(r"submitted job (\d+)", r.stdout)
    m["slurm"] = dict(partition="preempt", job_ids=ids, submit_stdout=r.stdout.strip(), submit_rc=r.returncode)
    m["started"] = now()
    write(rid, m)
    print(f"registered {rid}; output {outdir}; {r.stdout.strip()} {r.stderr.strip()}")
    return 0 if ids else 1


def cmd_finish(a):
    m = read(a.run_id)
    outdir = os.path.join("/data/haiyangw/nrpic", m["outputs"]["dir"])
    ids = m.get("slurm", {}).get("job_ids", [])
    el, state = 0.0, []
    for j in ids:
        out = subprocess.run(["sacct", "-j", j, "-X", "-n", "-P", "-o", "ElapsedRaw,State"],
                             capture_output=True, text=True).stdout.strip().splitlines()
        for ln in out[:1]:
            e, s = ln.split("|")
            el += float(e)
            state.append(s)
    st = os.path.join(outdir, "batch.list.status")
    rcs = re.findall(r"rc=(\d+)", open(st).read()) if os.path.exists(st) else []
    m["resources"]["walltime_s"] = el
    m["resources"]["gpu_hours"] = round(el / 3600.0, 4)
    m["slurm"]["states"] = state
    m["exit_code"] = max([int(x) for x in rcs], default=None)
    m["status"] = "completed" if rcs and all(x == "0" for x in rcs) else "failed"
    m["ended"] = now()
    m["outputs"]["files"] = sums(outdir)
    write(a.run_id, m)
    print(f"{a.run_id}: states {state}, rc {rcs}, {el:.0f} s = {el / 3600:.4f} card-hours")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd_name", required=True)
    for name in ("local", "card"):
        p = sp.add_parser(name)
        p.add_argument("--purpose", required=True)
        p.add_argument("--kind", default="scouting")
        p.add_argument("--input", action="append", default=[])
        p.add_argument("--parent", action="append", default=[])
        p.add_argument("--notes", default="")
        p.add_argument("--refusal", default="nrpic-run submit: the worktree is not clean (untracked files of other helpers)")
        if name == "local":
            p.add_argument("--cores", type=int, default=1)
            p.add_argument("cmd", nargs=argparse.REMAINDER)
        else:
            p.add_argument("--list", required=True)
            p.add_argument("--exe", default=GPU_EXE)
            p.add_argument("--wall", default="00:45:00")
    p = sp.add_parser("finish")
    p.add_argument("run_id")
    a = ap.parse_args()
    if a.cmd_name == "local":
        if a.cmd and a.cmd[0] == "--":
            a.cmd = a.cmd[1:]
        sys.exit(cmd_local(a))
    if a.cmd_name == "card":
        sys.exit(cmd_card(a))
    cmd_finish(a)


if __name__ == "__main__":
    main()
