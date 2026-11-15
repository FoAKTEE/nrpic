"""Run a command as a registered analysis run of C-sidm and write its manifest.

    python3 -E register.py --purpose TEXT [--kind scouting|production] [--input PATH ...]
                           [--cores N] [--notes TEXT] -- <command ...>

Every argument "{OUT}" of the command is replaced by the output directory
scratch/C-sidm/<run_id>/. The run id is C-sidm-<YYYYMMDD-HHMMSS UTC>-<commit7> of HEAD of the
worktree. Writes tracks/C-sidm/runs/<run_id>/manifest.json (fields of
harness/templates/run_manifest.json) and <outdir>/sha256sums.txt, and copies stdout and
stderr to <outdir>/log.txt. It refuses to run when the package directory has uncommitted
changes, so that the commit names the code that ran.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HOME = os.path.abspath(os.path.join(WT, "..", ".."))
OWNER = "C-sidm"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", WT] + list(args), capture_output=True, text=True,
                          check=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--kind", default="scouting", choices=["scouting", "production"])
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--notes", default="")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    rel_pkg = os.path.relpath(HERE, WT)
    dirty = git("status", "--porcelain", "--", rel_pkg)
    if dirty:
        sys.exit(f"refused: uncommitted changes under {rel_pkg}:\n{dirty}")
    sha = git("rev-parse", "HEAD")
    while True:      # one run id per second: wait for a free one
        now = dt.datetime.now(dt.timezone.utc)
        run_id = f"{OWNER}-{now.strftime('%Y%m%d-%H%M%S')}-{sha[:7]}"
        outdir = os.path.join(HOME, "scratch", OWNER, run_id)
        try:
            os.makedirs(outdir)
            break
        except FileExistsError:
            time.sleep(1.0)
    argv = [c.replace("{OUT}", outdir) for c in cmd]
    inputs = []
    for p in a.input + [x for x in argv if os.path.isfile(x)]:
        p = os.path.abspath(p)
        if any(i["path"] == p for i in inputs):
            continue
        inputs.append({"path": p, "sha256": sha256(p)})
    env = dict(os.environ)
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        env[k] = str(a.cores)
    t0 = time.time()
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    proc = subprocess.run(argv, cwd=HERE, env=env, capture_output=True, text=True)
    wall = time.time() - t0
    ended = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with open(os.path.join(outdir, "log.txt"), "w") as fh:
        fh.write(proc.stdout)
        fh.write(proc.stderr)
    files = []
    for root, _, names in os.walk(outdir):
        for n in sorted(names):
            if n == "sha256sums.txt":
                continue
            p = os.path.join(root, n)
            files.append(f"{sha256(p)}  {os.path.relpath(p, outdir)}")
    with open(os.path.join(outdir, "sha256sums.txt"), "w") as fh:
        fh.write("\n".join(files) + "\n")
    manifest = {
        "schema": "nrpic-run-manifest/1",
        "run_id": run_id,
        "track": OWNER,
        "gate": "G1",
        "kind": a.kind,
        "purpose": a.purpose,
        "launcher": "local (tracks/C-sidm/gravothermal/register.py)",
        "command": argv,
        "cwd": os.path.relpath(HERE, HOME),
        "git": {"sha": sha, "branch": git("rev-parse", "--abbrev-ref", "HEAD"), "dirty": False,
                "merge_base_main": git("merge-base", "HEAD", "main"),
                "worktree": os.path.relpath(WT, HOME)},
        "inputs": [{"path": os.path.relpath(i["path"], HOME), "sha256": i["sha256"]}
                   for i in inputs],
        "env": {"python": sys.version.split()[0], "threads": a.cores},
        "resources": {"nodes": 1, "gpus": 0, "cores": a.cores, "walltime_s": round(wall, 1),
                      "gpu_hours": 0.0, "core_hours": round(wall * a.cores / 3600.0, 4)},
        "outputs": {"dir": os.path.relpath(outdir, HOME), "sha256sums": "sha256sums.txt",
                    "sha256sums_sha256": sha256(os.path.join(outdir, "sha256sums.txt")),
                    "files": len(files)},
        "status": "completed" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "registered": started,
        "started": started,
        "ended": ended,
        "parents": [],
        "notes": a.notes,
    }
    mdir = os.path.join(WT, "tracks", OWNER, "runs", run_id)
    os.makedirs(mdir)
    with open(os.path.join(mdir, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    print(proc.stdout[-4000:])
    print(proc.stderr[-2000:], file=sys.stderr)
    print(f"run {run_id}: exit {proc.returncode}, wall {wall:.1f} s, output {outdir}")
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
