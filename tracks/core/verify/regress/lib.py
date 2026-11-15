"""Shared helpers of the core regression suite (tracks/core/verify/regress/).

Paths, the release executables, run ids, checksums and run manifests. Every script of
the suite imports this module; nothing here runs a simulation.

Run id: core-<YYYYMMDD-HHMMSS>-<commit7> (harness/RULES.md), output directory
scratch/core/<run_id>/, manifest tracks/core/runs/<run_id>/manifest.json.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
WT = HERE.parents[3]                       # the worktree (wt/core)
MAIN = Path("/data/haiyangw/nrpic")        # main checkout: release executables, runs/
SCRATCH = MAIN / "scratch" / "core"
RUNS_REG = WT / "tracks" / "core" / "runs"
FIGS = WT / "tracks" / "core" / "verify" / "figs"
MIRROR = WT / "tracks" / "core" / "verify" / "manifests"
CRITERIA = HERE / "criteria.json"

EXE_GPU = MAIN / ".work" / "build_gpu_c3" / "src" / "athena"
EXE_CPU = MAIN / ".work" / "build_cpu_c1" / "src" / "athena"
OLD_RUNS = MAIN / "runs"                   # earlier results (untracked, read-only)


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def commit7():
    return subprocess.run(["git", "-C", str(WT), "rev-parse", "--short=7", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def worktree_dirty(paths=("athenak/src", "python", "problems", "cosmo/ic",
                          "tracks/core/verify/regress")):
    out = subprocess.run(["git", "-C", str(WT), "status", "--porcelain", "--", *paths],
                         check=True, capture_output=True, text=True).stdout
    return out.strip() != ""


def new_run_id(when=None):
    when = when or _dt.datetime.now()
    return f"core-{when:%Y%m%d-%H%M%S}-{commit7()}"


def run_dir(run_id):
    d = SCRATCH / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def manifest_path(run_id):
    return RUNS_REG / run_id / "manifest.json"


def write_manifest(run_id, **fields):
    """Create or update tracks/core/runs/<run_id>/manifest.json (fields merged)."""
    p = manifest_path(run_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    m = json.loads(p.read_text()) if p.exists() else {}
    if not m:
        m = dict(run_id=run_id, owner="core", package="verify",
                 commit=subprocess.run(["git", "-C", str(WT), "rev-parse", "HEAD"],
                                       check=True, capture_output=True,
                                       text=True).stdout.strip(),
                 worktree_dirty=worktree_dirty(),
                 created=_dt.datetime.now().isoformat(timespec="seconds"),
                 output_dir=str(SCRATCH / run_id))
    m.update(fields)
    p.write_text(json.dumps(m, indent=1) + "\n")
    # tracks/core/runs/ is excluded by the ignore rule 'runs/' of .gitignore (and nothing
    # the ignore list excludes is committed, CLAUDE.md): a tracked copy is kept here
    MIRROR.mkdir(parents=True, exist_ok=True)
    (MIRROR / f"{run_id}.json").write_text(json.dumps(m, indent=1) + "\n")
    return p


def read_manifest(run_id):
    return json.loads(manifest_path(run_id).read_text())


def file_record(path):
    path = Path(path)
    return dict(path=str(path), sha256=sha256(path), bytes=path.stat().st_size)


def exe_record(path):
    path = Path(path)
    st = path.stat()
    return dict(path=str(path), sha256=sha256(path),
                mtime=_dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"))


def load_criteria():
    return json.loads(CRITERIA.read_text())


def athena_log_info(rundir):
    """Wall time, exit code, termination message and Slurm job of the newest athena log
    written by scripts/gpu_run.sh (header '# host=... slurm_job=...', footer '# exit=')."""
    rundir = Path(rundir)
    logs = sorted(p for p in rundir.glob("athena.*.log") if not p.is_symlink())
    if not logs:
        return dict(ok=False, reason="no log")
    txt = logs[-1].read_text(errors="replace")
    info = dict(log=str(logs[-1]))
    m = re.search(r"slurm_job=(\S+)", txt)
    info["slurm_job"] = m.group(1) if m else None
    m = re.search(r"start=(\S+)", txt)
    start = m.group(1) if m else None
    m = re.search(r"# exit=(\d+) end=(\S+)", txt)
    if m:
        info["exit"] = int(m.group(1))
        end = m.group(2)
        if start:
            t0 = _dt.datetime.fromisoformat(start)
            t1 = _dt.datetime.fromisoformat(end)
            info["wall_time_s"] = (t1 - t0).total_seconds()
    m = re.search(r"cpu time used\s*=\s*(\S+)", txt)
    if m:
        info["athena_cpu_time_s"] = float(m.group(1))
    info["terminated_on_time_limit"] = "Terminating on time limit" in txt
    info["ok"] = info.get("exit") == 0 and info["terminated_on_time_limit"]
    return info


def verdict_line(name, value, lo=None, hi=None, fmt="{:.4g}"):
    """One judged quantity: dict with pass flag and a printable line."""
    ok = True
    if lo is not None and not value >= lo:
        ok = False
    if hi is not None and not value <= hi:
        ok = False
    rng = f"[{'' if lo is None else fmt.format(lo)}, {'' if hi is None else fmt.format(hi)}]"
    return dict(name=name, value=value, lo=lo, hi=hi, ok=bool(ok),
                line=f"{'PASS' if ok else 'FAIL'}  {name} = {fmt.format(value)}  allowed {rng}")


def env_threads(n=1):
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        os.environ[k] = str(n)
