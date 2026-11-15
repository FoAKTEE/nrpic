#!/usr/bin/env python3
"""Hand registration of a run of this package, the fallback of harness/RULES.md when
`harness/bin/nrpic-run submit` refuses (here: it refuses while another helper's untracked
file lies in the shared worktree root). Writes tracks/D-bh-dress/runs/<run_id>/manifest.json
with the fields of harness/templates/run_manifest.json, commits it path-limited, and runs
the command detached with NRPIC_RUN_DIR set; `finish` records the exit, wall time and the
checksums of the output and commits the manifest again.

  python3 nm_register.py start --purpose TEXT [--kind scouting] [--gate G1] -- CMD ...
  python3 nm_register.py finish RUN_ID
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
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OWNER = "D-bh-dress"
SCRATCH = "/data/haiyangw/nrpic/scratch/D-bh-dress"
PKG = os.path.relpath(HERE, ROOT)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True)


def commit(paths, msg):
    for _ in range(24):
        git("add", *paths)
        r = git("commit", "-q", "-m", msg, "--", *paths)
        if r.returncode == 0 or "nothing to commit" in r.stdout + r.stderr:
            return
        if "index.lock" in r.stderr:
            time.sleep(5)
            continue
        sys.exit("commit failed: " + r.stderr)
    sys.exit("commit failed: index.lock persists")


def manifest_path(run_id):
    return os.path.join(ROOT, "tracks", OWNER, "runs", run_id, "manifest.json")


def start(a):
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    dirty = git("status", "--porcelain", "--", PKG).stdout.strip()
    if dirty:
        sys.exit("package not clean; commit first:\n" + dirty)
    sha_full = git("rev-parse", "HEAD").stdout.strip()
    run_id = "D-%s-%s" % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S"),
                          sha_full[:7])
    out = os.path.join(SCRATCH, run_id)
    os.makedirs(out, exist_ok=False)
    inputs = []
    for p in a.input + [c for c in cmd if os.path.isfile(os.path.join(ROOT, c)) or os.path.isfile(c)]:
        full = p if os.path.isabs(p) else os.path.join(ROOT, p)
        inputs.append(dict(path=p, sha256=sha(full), bytes=os.path.getsize(full)))
    m = dict(schema="nrpic-run-manifest/1", run_id=run_id, track=OWNER, gate=a.gate, kind=a.kind,
             purpose=a.purpose, preregistered_in=None, launcher="local (hand registration)",
             registered_by="hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because "
             "harness/bin/nrpic-run submit refused (an untracked file of another helper in the "
             "worktree root); see the package README, Requests",
             command=cmd, cwd=".", git=dict(sha=sha_full, branch=git(
                 "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(), dirty=False, package=[PKG]),
             code=dict(core_tag="core-v0.3", problem="nrpic_newton"),
             env=dict(host=os.uname().nodename, python=sys.version.split()[0],
                      OMP_NUM_THREADS="1"),
             inputs=inputs, resources=dict(cores=1, gpus=0, card_hours=0.0, walltime_s=None),
             outputs=dict(dir=os.path.relpath(out, "/data/haiyangw/nrpic"),
                          sha256sums="sha256sums.txt", bytes=None),
             status="running", exit_code=None, started=utc(), ended=None, parents=a.parent,
             notes=a.notes)
    os.makedirs(os.path.dirname(manifest_path(run_id)), exist_ok=True)
    with open(manifest_path(run_id), "w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")
    commit([os.path.relpath(manifest_path(run_id), ROOT)],
           "D(run): register %s by hand (%s)" % (run_id, a.purpose[:60]))
    env = dict(os.environ, NRPIC_RUN_ID=run_id, NRPIC_RUN_DIR=out, OMP_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               MPLCONFIGDIR=os.path.join(SCRATCH, "tmp", "mpl"))
    with open(os.path.join(out, "command.json"), "w") as f:
        json.dump(cmd, f)
    p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "_wrap", run_id], cwd=ROOT,
                         env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    print("registered %s (hand); wrapper pid %d; output %s" % (run_id, p.pid, out))


def wrap(run_id):
    out = os.path.join(SCRATCH, run_id)
    with open(os.path.join(out, "command.json")) as f:
        cmd = json.load(f)
    t0, started = time.time(), utc()
    with open(os.path.join(out, "run.log"), "w") as log:
        log.write("# %s start=%s cmd: %s\n" % (run_id, started, " ".join(cmd)))
        log.flush()
        r = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        log.write("# exit=%d end=%s\n" % (r.returncode, utc()))
    with open(os.path.join(out, "result.json"), "w") as f:
        json.dump(dict(exit_code=r.returncode, started=started, ended=utc(),
                       walltime_s=round(time.time() - t0, 3)), f)


def finish(run_id):
    out = os.path.join(SCRATCH, run_id)
    with open(os.path.join(out, "result.json")) as f:
        res = json.load(f)
    lines, total = [], 0
    for dp, dn, fn in os.walk(out):
        dn.sort()
        for n in sorted(fn):
            if n == "sha256sums.txt":
                continue
            full = os.path.join(dp, n)
            total += os.path.getsize(full)
            lines.append("%s  %s" % (sha(full), os.path.relpath(full, out)))
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(manifest_path(run_id)) as f:
        m = json.load(f)
    m.update(status="completed" if res["exit_code"] == 0 else "failed",
             exit_code=res["exit_code"], ended=res["ended"])
    m["resources"]["walltime_s"] = res["walltime_s"]
    m["outputs"]["bytes"] = total
    with open(manifest_path(run_id), "w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")
    commit([os.path.relpath(manifest_path(run_id), ROOT)],
           "D(run): finish %s (%s, hand registration)" % (run_id, m["status"]))
    print("finished %s: %s, %.0f s, %d files" % (run_id, m["status"], res["walltime_s"], len(lines)))


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "_wrap":
        return wrap(sys.argv[2])
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    s = sub.add_parser("start")
    s.add_argument("--purpose", required=True)
    s.add_argument("--kind", default="scouting", choices=("scouting", "production"))
    s.add_argument("--gate", default="G1")
    s.add_argument("--input", action="append", default=[])
    s.add_argument("--parent", action="append", default=[])
    s.add_argument("--notes", default="")
    s.add_argument("cmd", nargs=argparse.REMAINDER)
    f = sub.add_parser("finish")
    f.add_argument("run_id")
    a = ap.parse_args()
    if a.mode == "start":
        start(a)
    else:
        finish(a.run_id)


if __name__ == "__main__":
    main()
