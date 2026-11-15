"""Run registration for the newton3 scripts (CLAUDE.md rule 4, by hand).

Each script calls ``start_run(purpose, inputs, kind, cores)`` first: it creates the run id
F-hills-<UTC YYYYMMDD-HHMMSS>-<commit7>, the output directory
scratch/F-hills/<run_id>/ and tracks/F-hills/runs/<run_id>/manifest.json; at the end
``finish_run(run, status)`` adds wall time, core-hours and the sha256 of every output.
"""
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys
import time

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/F-hills"
PKG = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _git(*args):
    return subprocess.run(["git", "-C", WT, *args], capture_output=True, text=True).stdout.strip()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def package_inputs():
    """Every source file of the package (modules and scripts) with its checksum."""
    out = []
    for sub in ("hills3", "scripts"):
        d = os.path.join(PKG, sub)
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".py"):
                p = os.path.join(d, fn)
                out.append({"path": os.path.relpath(p, WT), "sha256": sha256(p)})
    return out


def _under_harness():
    """Run started by harness/bin/nrpic-run (wave 2): it registered the run, owns the
    manifest and writes the checksums; the script only uses its id and directory."""
    rid, rdir = os.environ.get("NRPIC_RUN_ID"), os.environ.get("NRPIC_RUN_DIR")
    return (rid, rdir) if rid and rdir else None


def start_run(purpose, kind="scouting", cores=1, extra_inputs=(), notes="", preregistered=None):
    h = _under_harness()
    if h is not None:
        rid, rdir = h
        os.makedirs(rdir, exist_ok=True)
        info = {"run_id": rid, "purpose_of_script": purpose, "cores": cores,
                "inputs": package_inputs() + [{"path": p, "sha256": sha256(p)} for p in extra_inputs],
                "preregistered_in": preregistered, "notes": notes}
        with open(os.path.join(rdir, "script_inputs.json"), "w") as fh:
            json.dump(info, fh, indent=2)
        print(f"run {rid} (registered by nrpic-run) -> {rdir}", flush=True)
        return {"id": rid, "dir": rdir, "manifest": None, "t0": time.time(), "cores": cores}
    sha = _git("rev-parse", "HEAD")
    # other helpers of F-hills register runs in the same second: retry on a collision
    for _ in range(30):
        now = _dt.datetime.now(_dt.timezone.utc)
        run_id = f"F-hills-{now:%Y%m%d-%H%M%S}-{sha[:7]}"
        outdir = os.path.join(SCRATCH, run_id)
        mdir = os.path.join(WT, "tracks", "F-hills", "runs", run_id)
        if os.path.exists(outdir) or os.path.exists(mdir):
            time.sleep(1.1)
            continue
        try:
            os.makedirs(outdir, exist_ok=False)
            os.makedirs(mdir, exist_ok=False)
        except FileExistsError:
            time.sleep(1.1)
            continue
        break
    else:
        raise RuntimeError("could not allocate a run id")
    inputs = package_inputs() + [{"path": p, "sha256": sha256(p)} for p in extra_inputs]
    dirty_pkg = _git("status", "--porcelain", "--", "tracks/F-hills/newton3")
    man = {
        "run_id": run_id,
        "track": "F-hills",
        "package": "newton3 (F-pre-1)",
        "gate": "G1",
        "purpose": purpose,
        "preregistered_in": preregistered,
        "kind": kind,
        "command": [sys.executable, "-I"] + sys.argv if sys.flags.isolated else [sys.executable] + sys.argv,
        "cwd": os.getcwd(),
        "git": {"sha": sha, "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
                "dirty_package": bool(dirty_pkg), "merge_base_main": _git("merge-base", "HEAD", "main")},
        "code": {"core_tag": None, "athenak": "not used (reference ODE solution, decision 0010)"},
        "env": {"host": os.uname().nodename, "python": sys.version.split()[0],
                "numpy": __import__("numpy").__version__, "scipy": __import__("scipy").__version__},
        "inputs": inputs,
        "resources": {"nodes": 1, "gpus": 0, "cores": cores, "card_hours": 0.0},
        "outputs": {"dir": os.path.relpath(outdir, "/data/haiyangw/nrpic"), "sha256sums": "sha256sums.txt"},
        "status": "running",
        "exit_code": None,
        "started": now.isoformat(timespec="seconds"),
        "ended": None,
        "walltime_s": None,
        "core_hours": None,
        "notes": notes,
    }
    path = os.path.join(mdir, "manifest.json")
    with open(path, "w") as fh:
        json.dump(man, fh, indent=2)
    print(f"run {run_id} -> {outdir}", flush=True)
    return {"id": run_id, "dir": outdir, "manifest": path, "t0": time.time(), "cores": cores}


def finish_run(run, status="completed", exit_code=0, results=None):
    if run["manifest"] is None:          # nrpic-run closes the run (status, checksums)
        with open(os.path.join(run["dir"], "script_result.json"), "w") as fh:
            json.dump({"status": status, "exit_code": exit_code,
                       "walltime_s": round(time.time() - run["t0"], 1), "results": results},
                      fh, indent=2, default=float)
        print(f"run {run['id']} {status} in {time.time() - run['t0']:.0f} s", flush=True)
        if exit_code:
            raise SystemExit(exit_code)
        return
    with open(run["manifest"]) as fh:
        man = json.load(fh)
    wall = time.time() - run["t0"]
    sums = []
    for root, _, files in os.walk(run["dir"]):
        for fn in sorted(files):
            if fn == "sha256sums.txt":
                continue
            p = os.path.join(root, fn)
            sums.append(f"{sha256(p)}  {os.path.relpath(p, run['dir'])}")
    with open(os.path.join(run["dir"], "sha256sums.txt"), "w") as fh:
        fh.write("\n".join(sums) + "\n")
    man.update(status=status, exit_code=exit_code,
               ended=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
               walltime_s=round(wall, 1), core_hours=round(wall * run["cores"] / 3600, 3))
    man["outputs"]["files"] = len(sums)
    if results is not None:
        man["results"] = results
    with open(run["manifest"], "w") as fh:
        json.dump(man, fh, indent=2)
    print(f"run {run['id']} {status} in {wall:.0f} s", flush=True)
