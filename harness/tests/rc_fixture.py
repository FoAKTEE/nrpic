"""Scratch repository for the self-tests of nrpic-run, nrpic-env, nrpic-stage and the hooks.

make_repo(name) builds, under <main checkout>/scratch/harness/<name>-<UTC>-<pid>/:
  repo/            a fresh git repository (branch main) holding copies of this checkout's
                   harness/, scripts/, CLAUDE.md, .gitignore, coord/CHARTER.md, coord/DECISIONS/0006,
                   the brief, and seeded tracks/<ID>/ directories; athenak/kokkos is a tiny submodule
  repo/wt/<ID>     linked worktrees on track/<ID>, core/nrpic, kb/main (as decision 0001)
  fakebin/         fake sbatch, squeue, sacct, scancel, srun, nvidia-smi and a fake athena, so that
                   scripts/gpu_batch.sh and scripts/submit_chain.sh run end to end with no card used
The machine file of the scratch repository puts fakebin/ first on PATH and points NRPIC_GPU_EXE at
the fake athena. Nothing here touches the live branches or worktrees.
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.realpath(__file__))
LIVE = os.path.realpath(os.path.join(HERE, "..", ".."))       # the checkout these tests belong to
sys.path.insert(0, os.path.join(LIVE, "harness", "lib"))
import nrpic_harness as H  # noqa: E402

BRIEF = "einstein_vlasov_pic_cosmology_agent_brief.en.md"
BRANCH = {"core": "core/nrpic", "kb": "kb/main"}


def live_home():
    common = subprocess.run(["git", "-C", LIVE, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, env=H.boot_env(), check=True).stdout.strip()
    return os.path.dirname(common)


def sh(cmd, cwd=None, env=None, check=True, input_text=None, timeout=300):
    r = subprocess.run(cmd, cwd=cwd, env=env or H.boot_env(), capture_output=True, text=True,
                       input=input_text, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd} failed ({r.returncode}):\n{r.stdout}\n{r.stderr}")
    return r


FAKE_SBATCH = r'''#!/usr/bin/python3 -I
import os, subprocess, sys
STATE = "@STATE@"
args = sys.argv[1:]
two = {"-p", "-c", "-t", "-J", "-o", "-e", "-n", "-N", "-A", "--partition"}
opts, i = {}, 0
while i < len(args) and args[i].startswith("-"):
    a = args[i]
    if a in two:
        opts[a] = args[i + 1]; i += 2
    else:
        k, _, v = a.partition("="); opts[k] = v; i += 1
script, sargs = args[i], args[i + 1:]
os.makedirs(STATE, exist_ok=True)
cnt = os.path.join(STATE, "counter")
n = int(open(cnt).read()) + 1 if os.path.exists(cnt) else 1000
open(cnt, "w").write(str(n))
jid = str(n)
env = dict(os.environ)
for k in [k for k in env if k.startswith("SLURM_")]:
    del env[k]
env["SLURM_JOB_ID"] = jid
env["SLURM_JOB_NAME"] = opts.get("-J", "job")
exp = opts.get("--export", "ALL")
for kv in exp.split(",")[1:]:
    k, _, v = kv.partition("="); env[k] = v
out = opts.get("-o", os.path.join(STATE, "slurm-%j.out")).replace("%j", jid)
jd = os.path.join(STATE, jid)
os.makedirs(jd)
wrapper = 'date +%s > "$J/start"; "$0" "$@"; echo $? > "$J/rc"; date +%s > "$J/end"'
env["J"] = jd
p = subprocess.Popen(["bash", "-c", wrapper, script] + sargs, stdin=subprocess.DEVNULL,
                     stdout=open(out, "w"), stderr=subprocess.STDOUT, env=env, start_new_session=True)
open(os.path.join(jd, "pid"), "w").write(str(p.pid))
open(os.path.join(jd, "name"), "w").write(env["SLURM_JOB_NAME"])
print(jid if "--parsable" in opts else f"Submitted batch job {jid}")
'''

FAKE_SQUEUE = r'''#!/usr/bin/python3 -I
import os, sys
STATE = "@STATE@"
args = sys.argv[1:]
jobs = [args[args.index("-j") + 1]] if "-j" in args else (sorted(os.listdir(STATE)) if os.path.isdir(STATE) else [])
def alive(j):
    d = os.path.join(STATE, j)
    if not os.path.isfile(os.path.join(d, "pid")) or os.path.exists(os.path.join(d, "end")):
        return False
    try:
        os.kill(int(open(os.path.join(d, "pid")).read()), 0); return True
    except OSError:
        return False
live = [j for j in jobs if j.isdigit() and alive(j)]
if "-h" not in args:
    print("JOBID NAME STATE")
for j in live:
    if "%T" in args:
        print("RUNNING")
    else:
        print(j, open(os.path.join(STATE, j, "name")).read(), "RUNNING")
'''

FAKE_SACCT = r'''#!/usr/bin/python3 -I
import os, sys, time
STATE = "@STATE@"
args = sys.argv[1:]
j = args[args.index("-j") + 1]
d = os.path.join(STATE, j)
if os.path.isfile(os.path.join(d, "start")):
    s = int(open(os.path.join(d, "start")).read())
    e = int(open(os.path.join(d, "end")).read()) if os.path.isfile(os.path.join(d, "end")) else int(time.time())
    print(max(1, e - s))
'''

FAKE_SCANCEL = r'''#!/usr/bin/python3 -I
import os, signal, sys
STATE = "@STATE@"
for j in sys.argv[1:]:
    try:
        os.killpg(int(open(os.path.join(STATE, j, "pid")).read()), signal.SIGTERM)
    except (OSError, ValueError):
        pass
'''

FAKE_SRUN = r'''#!/bin/bash
# fake srun: drop the allocation options, run the rest
while [[ $# -gt 0 ]]; do
  case $1 in
    -p|-c|-t|-J|-n|-N|-o) shift 2 ;;
    -*) shift ;;
    *) break ;;
  esac
done
exec "$@"
'''

FAKE_ATHENA = r'''#!/bin/bash
# fake athena for the harness self-tests: no physics, a few output files and AthenaK's messages.
mode=; d=.
while [[ $# -gt 0 ]]; do
  case $1 in
    -i) mode=i; deck=$2; shift 2 ;;
    -r) mode=r; shift 2 ;;
    -d) d=$2; shift 2 ;;
    -t) shift 2 ;;
    *) shift ;;
  esac
done
mkdir -p "$d/rst"
echo "Setup complete"
sleep 1
if [[ $mode == i ]]; then
  printf '# [1]=time [2]=Volume\n0.0 1.0\n0.5 1.0\n' > "$d/fake.hst"
  echo data1 > "$d/out1.txt"; echo rst1 > "$d/rst/fake.00001.rst"
  echo "time=5.0e-01 cycle=5 dt=1.0e-01"
  if grep -q 'file_type *= *rst' "$deck"; then echo "Terminating on wall clock limit"
  else echo "Terminating on time limit"; fi
else
  printf '1.0 1.0\n' >> "$d/fake.hst"
  echo data2 > "$d/out2.txt"; echo rst2 > "$d/rst/fake.00002.rst"
  echo "time=1.0e+00 cycle=10 dt=1.0e-01"
  echo "Terminating on time limit"
fi
'''

FAKE_NVSMI = "#!/bin/bash\nexit 1\n"


def write_exe(path, text):
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, 0o755)


def seed_track(repo, owner):
    t = os.path.join(repo, "tracks", owner)
    for d in ("outbox", "runs", "stage", "notes", "analysis"):
        os.makedirs(os.path.join(t, d), exist_ok=True)
        open(os.path.join(t, d, ".gitkeep"), "w").close()
    open(os.path.join(t, "STATUS.md"), "w").write(
        f"# STATUS of {owner}\n\ngate:        G0 in progress\nheadline:    scratch fixture\n"
        "last-result: none\nnext:        1. test\nblockers:    none\nneeds:       none\noffers:      none\n"
        "budget:      0 GPU-hours used\n")
    open(os.path.join(t, "JOURNAL.md"), "w").write(f"# JOURNAL of {owner}\n")
    open(os.path.join(t, "HANDOFF.md"), "w").write(f"# HANDOFF of {owner}\n\nState: scratch fixture.\n")
    open(os.path.join(t, "RISKS.md"), "w").write(f"# RISKS of {owner}\n\n- fixture risk\n")
    own = {"core": "athenak/src/**\npython/nrpic/**\nproblems/**\nscripts/**\n", "kb": "kb/**\n"}.get(owner, "")
    open(os.path.join(t, "OWNERSHIP"), "w").write(
        f"# one glob per line: paths outside tracks/{owner}/ that this owner may edit\n" + own)


def make_repo(name, owners=("A-emd-pbh", "B-emd-gw", "core", "kb")):
    home = live_home()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    root = os.path.join(home, "scratch", "harness", f"{name}-{stamp}-{os.getpid()}")
    repo = os.path.join(root, "repo")
    fakebin = os.path.join(root, "fakebin")
    state = os.path.join(root, "slurmstate")
    os.makedirs(repo)
    os.makedirs(fakebin)
    os.makedirs(state)
    for fn, text in (("sbatch", FAKE_SBATCH), ("squeue", FAKE_SQUEUE), ("sacct", FAKE_SACCT),
                     ("scancel", FAKE_SCANCEL), ("srun", FAKE_SRUN), ("athena", FAKE_ATHENA),
                     ("nvidia-smi", FAKE_NVSMI)):
        write_exe(os.path.join(fakebin, fn), text.replace("@STATE@", state))

    ign = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(os.path.join(LIVE, "harness"), os.path.join(repo, "harness"), ignore=ign)
    shutil.copytree(os.path.join(LIVE, "scripts"), os.path.join(repo, "scripts"), ignore=ign)
    for f in ("CLAUDE.md", ".gitignore", BRIEF, "coord/CHARTER.md", "coord/DECISIONS/0006-compute-budget.md"):
        dst = os.path.join(repo, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(LIVE, f), dst)
    for o in owners:
        seed_track(repo, o)
    mf = os.path.join(repo, "harness", "env", "machines", H.host() + ".sh")
    with open(mf, "w") as f:
        f.write("# machine file of the scratch fixture (fake Slurm, fake athena)\n"
                f"NRPIC_HOST={H.host()}\nCUDA_HOME=/usr/local/cuda-12.6\nNRPIC_PYTHON=/usr/bin/python3\n"
                f"PATH={fakebin}:${{HOME}}/.local/bin:/usr/local/bin:/usr/bin:/bin\n"
                f"UV_CACHE_DIR={home}/cache/uv\n"
                f"NRPIC_GPU_EXE={fakebin}/athena\nNRPIC_CPU_EXE={fakebin}/athena\n"
                "NRPIC_PARTITION=preempt\nNRPIC_GPU_NAME=fake card (self-test)\n"
                "NRPIC_SLURM_MAX_TIME=01:00:00\nNRPIC_CHAIN_SEGMENT=00:59:00\n")

    g = ["git", "-C", repo]
    sh(g + ["init", "-q", "-b", "main"])
    sh(g + ["config", "user.name", "harness-selftest"])
    sh(g + ["config", "user.email", "selftest@localhost"])
    sh(g + ["config", "commit.gpgsign", "false"])
    # a tiny stand-in for the Kokkos submodule
    ksrc = os.path.join(root, "kokkos-src")
    os.makedirs(ksrc)
    open(os.path.join(ksrc, "CMakeLists.txt"), "w").write("# stand-in for kokkos\n")
    sh(["git", "-C", ksrc, "init", "-q", "-b", "main"])
    sh(["git", "-C", ksrc, "-c", "user.name=t", "-c", "user.email=t@l", "add", "."])
    sh(["git", "-C", ksrc, "-c", "user.name=t", "-c", "user.email=t@l", "commit", "-q", "-m", "kokkos stand-in"])
    os.makedirs(os.path.join(repo, "athenak"))
    sh(g + ["-c", "protocol.file.allow=always", "submodule", "add", "-q", ksrc, "athenak/kokkos"])
    sh(g + ["add", "-A"])
    sh(g + ["commit", "-q", "-m", "scratch fixture"])
    wts = {}
    for o in owners:
        br = BRANCH.get(o, f"track/{o}")
        p = os.path.join(repo, "wt", o)
        sh(g + ["worktree", "add", "-q", "-b", br, p, "main"])
        wts[o] = p
    return {"root": root, "repo": repo, "wt": wts, "fakebin": fakebin, "state": state}


def commit_file(wt, rel, text, msg="add test file"):
    p = os.path.join(wt, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)
    sh(["git", "-C", wt, "add", "--", rel])
    sh(["git", "-C", wt, "commit", "-q", "-m", msg, "--", rel])
    return p


class Checks:
    """Collects PASS/FAIL lines; exit status 1 if any failed."""

    def __init__(self, title):
        self.title = title
        self.rows = []
        print(f"== {title}")

    def ok(self, cond, what, detail=""):
        self.rows.append((bool(cond), what))
        print(f"  {'PASS' if cond else 'FAIL'}  {what}" + (f"\n        {detail}" if (detail and not cond) else ""))
        return bool(cond)

    def done(self):
        bad = [w for c, w in self.rows if not c]
        print(f"== {self.title}: {len(self.rows) - len(bad)}/{len(self.rows)} passed")
        return 1 if bad else 0
