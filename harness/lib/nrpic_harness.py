"""Shared code of the harness commands nrpic-env, nrpic-run and nrpic-stage (standard library only).

Every command runs with `python3 -I` and builds the environment of its subprocesses from files
(the machine file harness/env/machines/<host>.sh, the passwd entry), never from the caller's
environment variables. The worktree a command acts on is the one that contains the command's
own file (harness/bin/<cmd> inside a worktree), unless -C <path> names another one.

Layout facts (decision 0001): the linked worktrees are wt/<ID> inside the main checkout; the data
roots scratch/, kb-data/, cache/, locks/ are inside the main checkout too.
"""
import concurrent.futures
import datetime
import fnmatch
import hashlib
import json
import os
import pwd
import re
import socket
import subprocess
import sys
import time

BOOT_PATH = "/usr/local/bin:/usr/bin:/bin"
TRACK_IDS = ("A-emd-pbh", "B-emd-gw", "C-sidm", "D-bh-dress", "E-stoch-inf", "F-hills")
OWNER_IDS = ("core", "kb") + TRACK_IDS
GATES = ("G0", "G1", "G2", "G3", "G4")


class HarnessError(Exception):
    """A refusal or failure with a message for the user; the command exits nonzero."""


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def boot_env():
    """Minimal environment for git and friends before the machine file is read."""
    pw = pwd.getpwuid(os.getuid())
    return {"PATH": BOOT_PATH, "HOME": pw.pw_dir, "USER": pw.pw_name, "LOGNAME": pw.pw_name,
            "LANG": "C.UTF-8"}


def run(cmd, cwd=None, env=None, check=True, capture=True, input_text=None, timeout=None):
    r = subprocess.run(cmd, cwd=cwd, env=env if env is not None else boot_env(), text=True,
                       capture_output=capture, input=input_text, timeout=timeout)
    if check and r.returncode != 0:
        err = (r.stderr or "").strip() if capture else ""
        raise HarnessError(f"command failed ({r.returncode}): {' '.join(cmd)}\n{err}")
    return r


def git(wt, *args, check=True, env=None):
    return run(["git", "-C", wt] + list(args), check=check, env=env).stdout.strip()


def sha256_file(path, bufsize=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


# ------------------------------------------------------------------ owners and worktrees

def owner_of(branch):
    """Branch name -> owner id (brief section 11.3), or None."""
    if branch == "main":
        return "orch"
    if branch.startswith("track/"):
        return branch[len("track/"):].split("--", 1)[0]     # temporary branches track/<ID>--<x>
    if branch.startswith("core/"):
        return "core"
    if branch.startswith("kb/"):
        return "kb"
    if branch.startswith("proposal/"):
        parts = branch.split("/")
        return parts[1] if len(parts) > 2 else None
    return None


def owner_short(owner):
    """A-emd-pbh -> A; core -> core; kb -> kb (prefix of run ids and commit subjects)."""
    if owner in TRACK_IDS:
        return owner.split("-")[0]
    return owner


class Worktree:
    """The worktree a command acts on: root, branch, owner, main checkout."""

    def __init__(self, path):
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            raise HarnessError(f"not a directory: {path}")
        r = run(["git", "-C", path, "rev-parse", "--show-toplevel"], check=False)
        if r.returncode != 0:
            raise HarnessError(f"not inside a git worktree: {path}")
        self.root = os.path.realpath(r.stdout.strip())
        common = git(self.root, "rev-parse", "--path-format=absolute", "--git-common-dir")
        self.home = os.path.realpath(os.path.dirname(common))   # the main checkout
        self.branch = git(self.root, "rev-parse", "--abbrev-ref", "HEAD")
        self.owner = owner_of(self.branch)
        self.is_main = self.root == self.home

    @property
    def short(self):
        return owner_short(self.owner)

    def head(self):
        return git(self.root, "rev-parse", "HEAD")

    def track_dir(self):
        return os.path.join(self.root, "tracks", self.owner)

    def scratch(self, owner=None):
        return os.path.join(self.home, "scratch", owner or self.owner)

    def rel(self, path):
        return os.path.relpath(os.path.realpath(path), self.root)

    def inside(self, path):
        p = os.path.realpath(path)
        return p == self.root or p.startswith(self.root + os.sep)

    def dirty(self):
        """Porcelain status lines (tracked changes and untracked files; ignored files excluded)."""
        out = run(["git", "-C", self.root, "status", "--porcelain", "--untracked-files=normal"]).stdout
        return [l for l in out.splitlines() if l.strip()]

    def require_owner(self):
        if self.owner is None:
            raise HarnessError(f"branch {self.branch!r} of {self.root} belongs to no owner "
                               "(expected track/<ID>, core/*, kb/*, main)")
        return self.owner


def worktree_from_args(cmd_file, c_opt):
    """The worktree of -C <path>, or the one holding the command file. Refuses when the caller's
    working directory lies in a different worktree of the same repository (a likely mistake:
    calling the main checkout's copy from a track worktree) and -C was not given."""
    if c_opt:
        return Worktree(c_opt)
    wt = Worktree(os.path.dirname(os.path.abspath(cmd_file)))
    try:
        here = Worktree(os.getcwd())
    except HarnessError:
        return wt
    if here.home == wt.home and here.root != wt.root:
        raise HarnessError(
            f"this copy of the command belongs to {wt.root} (branch {wt.branch}) but you are in "
            f"{here.root} (branch {here.branch}). Call the copy in your worktree "
            f"({os.path.join(here.root, 'harness/bin', os.path.basename(cmd_file))}; run "
            f"`git merge --no-edit main` first if it is missing) or pass -C {here.root}.")
    return wt


def ownership_globs(wt, owner=None):
    """Globs of tracks/<ID>/OWNERSHIP (one per line, # comments)."""
    owner = owner or wt.owner
    path = os.path.join(wt.root, "tracks", owner, "OWNERSHIP")
    globs = []
    if os.path.isfile(path):
        for line in open(path):
            line = line.split("#", 1)[0].strip()
            if line:
                globs.append(line)
    return globs


def glob_match(rel, pattern):
    """Path glob with ** (any depth) and * (within one segment)."""
    rx = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            rx += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            rx += ".*"
            i += 2
        elif pattern[i] == "*":
            rx += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            rx += "[^/]"
            i += 1
        else:
            rx += re.escape(pattern[i])
            i += 1
    return re.fullmatch(rx, rel) is not None


# ------------------------------------------------------------------ machine file and environment

def host():
    return socket.gethostname().split(".")[0]


def machine_file(wt):
    path = os.path.join(wt.root, "harness", "env", "machines", host() + ".sh")
    if not os.path.isfile(path):
        raise HarnessError(f"no machine file for host {host()!r}: {path}")
    return path


_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def read_machine_file(path, base):
    """KEY=VALUE lines (shell-compatible, values may be quoted, ${VAR} refers to earlier keys or
    to the base variables). Nothing is executed."""
    vals = {}
    for n, line in enumerate(open(path), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[len("export "):]
        m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)", s)
        if not m:
            raise HarnessError(f"{path}:{n}: not a KEY=VALUE line: {line.rstrip()}")
        key, v = m.group(1), m.group(2).strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        scope = dict(base)
        scope.update(vals)
        v = _VAR.sub(lambda mm: scope.get(mm.group(1), ""), v)
        vals[key] = v
    return vals


def track_extra_requirements(wt):
    if wt.owner is None:
        return None
    p = os.path.join(wt.root, "tracks", wt.owner, "env", "requirements.txt")
    return p if os.path.isfile(p) else None


def env_identity(wt):
    """Components and combined hash of the environment (brief section 11.4)."""
    mf = machine_file(wt)
    lock = os.path.join(wt.root, "harness", "env", "uv.lock")
    comp = {
        "host": host(),
        "machine_file": os.path.relpath(mf, wt.root),
        "machine_file_sha256": sha256_file(mf),
        "uv_lock_sha256": sha256_file(lock) if os.path.isfile(lock) else None,
        "container_digest": None,
    }
    extra = track_extra_requirements(wt)
    comp["track_requirements_sha256"] = sha256_file(extra) if extra else None
    text = (f"machine:{comp['machine_file_sha256']}\nuvlock:{comp['uv_lock_sha256']}\n"
            f"container:{comp['container_digest'] or 'none'}\n")
    if extra:
        text += f"track-requirements:{comp['track_requirements_sha256']}\n"
    comp["env_hash"] = sha256_text(text)
    return comp


THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
               "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS", "BLIS_NUM_THREADS")
PROTECTED = ("NRPIC_HOME", "NRPIC_WT", "NRPIC_TRACK", "NRPIC_BRANCH", "NRPIC_SCRATCH", "NRPIC_KB",
             "NRPIC_ENV_HASH", "PATH", "HOME", "VIRTUAL_ENV", "PYTHONNOUSERSITE")


def nrpic_vars(wt):
    """The variables that identify the worktree (doctor row [env])."""
    owner = wt.owner or "unknown"
    return {
        "NRPIC_HOME": wt.home,
        "NRPIC_WT": wt.root,
        "NRPIC_TRACK": owner,
        "NRPIC_BRANCH": wt.branch,
        "NRPIC_SCRATCH": os.path.join(wt.home, "scratch", owner),
        "NRPIC_KB": os.path.join(wt.home, "kb-data"),
        "NRPIC_HARNESS": "1",
    }


def build_env(wt, threads=1, extra=None):
    """The complete environment of `nrpic-env exec`. Reads no variable of the caller."""
    base = boot_env()
    base.update(nrpic_vars(wt))
    mvals = read_machine_file(machine_file(wt), base)
    env = dict(base)
    for k, v in mvals.items():
        if k.startswith("NRPIC_") and k in nrpic_vars(wt):
            continue                                   # identity variables are not overridable
        env[k] = v
    venv = os.path.join(wt.root, ".venv")
    path = mvals.get("PATH", BOOT_PATH)
    if os.path.isdir(venv) and not os.path.islink(venv):
        env["VIRTUAL_ENV"] = venv
        path = os.path.join(venv, "bin") + ":" + path
    env["PATH"] = path
    env["PYTHONNOUSERSITE"] = "1"
    env["MPLBACKEND"] = "Agg"
    env["MPLCONFIGDIR"] = os.path.join(wt.home, "cache", "mplconfig", os.path.basename(wt.root))
    env["UV_CACHE_DIR"] = mvals.get("UV_CACHE_DIR", os.path.join(wt.home, "cache", "uv"))
    env["UV_PROJECT_ENVIRONMENT"] = venv
    env["UV_LINK_MODE"] = "copy"
    env["UV_NO_CONFIG"] = "1"
    if "NRPIC_PYTHON" in mvals:
        env["UV_PYTHON"] = mvals["NRPIC_PYTHON"]
    for k in THREAD_VARS:
        env[k] = str(threads)
    env["NRPIC_ENV_HASH"] = env_identity(wt)["env_hash"]
    for k, v in (extra or {}).items():
        if k in PROTECTED or k.startswith("NRPIC_") and k in nrpic_vars(wt):
            raise HarnessError(f"--set {k}: this variable is fixed by nrpic-env")
        env[k] = v
    return env


# ------------------------------------------------------------------ the account's Slurm queue (decision 0033)

# Guardrail set by the user on 2026-11-24 (decision 0033): at most this many jobs of the account may be
# in the Slurm queue at once, pending, held and running ones together, over all owners. No option and
# no environment variable lifts it. nrpic-run (submit) and nrpic-queue (the dispatcher) read it here.
QUEUE_CAP = 5


def queue_jobs(env=None):
    """The jobs of this account in the Slurm queue (every state squeue lists: pending, held, running,
    completing, ...) as a list of {"id", "name", "state", "workdir"}, or None if squeue fails or does not
    answer within 60 s. env: the environment the tool uses for its Slurm commands (build_env), so that the
    count and the submission ask the same Slurm. One line is one job; `-r` lists every task of a job array on
    a line of its own, so that an array of N tasks counts N. workdir (`%Z`) is the job's working directory
    ('' when squeue gives none): the cap keeper tells this program's jobs from the user's others by it."""
    e = env if env is not None else os.environ
    user = e.get("USER") or e.get("LOGNAME") or os.environ.get("USER") or ""
    try:
        r = subprocess.run(["squeue", "-h", "-r", "-u", user, "-o", "%i|%j|%T|%Z"], capture_output=True,
                           text=True, timeout=60, env=env)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    jobs = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in (line.split("|", 3) if "|" in line else line.split())] + ["", "", "", ""]
        jobs.append({"id": parts[0], "name": parts[1], "state": parts[2], "workdir": parts[3]})
    return jobs


def program_job(job, home):
    """Why a job of the account is this program's ("run id": its name is a run id of nrpic-run, the owner one
    of the harness's; "under the repository": its working directory lies under the main checkout `home`,
    which holds wt/* and scratch/*), or None: a job of the user's own, which the cap keeper never cancels.
    (A job of a queue entry is the program's too; nrpic-queue checks that itself.)"""
    if parse_run_id(job.get("name") or ""):
        return "run id"
    wd = job.get("workdir") or ""
    if os.path.isabs(wd):                     # squeue may print "(null)" or a relative path: never "under" anything
        p, h = os.path.realpath(wd), os.path.realpath(home)
        if p == h or p.startswith(h + os.sep):
            return "under the repository"
    return None


def queue_count(env=None):
    """Number of jobs of this account in the Slurm queue (queue_jobs), or None if squeue fails."""
    jobs = queue_jobs(env)
    return None if jobs is None else len(jobs)


# Commands that reach Slurm (decision 0033, one route). Outside a dispatch of the shared queue, a local run of
# nrpic-run and `nrpic-env exec` put harness/shims/slurm first on the command's PATH: there sbatch, srun and
# salloc are stubs that print the rule and exit 2, whatever form the command takes (a prefix such as timeout or
# env, a script that calls another, Python, ...). Inside a valid dispatch the PATH is left as it is, so that
# nothing of the stubs reaches a job (a chain's job resubmits its next segment with the real sbatch). A call by
# absolute path (/usr/bin/sbatch) or with a PATH of its own passes: only a limit on the Slurm side or the
# tool-guard hook closes that. The one textual refusal left: the command's own first word.
SLURM_COMMANDS = ("sbatch", "srun", "salloc")


def slurm_shim_dir(root):
    """harness/shims/slurm of the worktree `root`."""
    return os.path.join(root, "harness", "shims", "slurm")


def with_slurm_shims(env, wt):
    """A copy of env with harness/shims/slurm first on PATH (outside a dispatch of the shared queue)."""
    d = slurm_shim_dir(wt.root)
    if not all(os.access(os.path.join(d, c), os.X_OK) for c in SLURM_COMMANDS):
        raise HarnessError(f"{d}/{{sbatch,srun,salloc}} are missing: merge main first (git merge --no-edit main)")
    env = dict(env)
    env["PATH"] = d + ":" + env.get("PATH", BOOT_PATH)
    return env


# One route for card runs (decision 0033): only the dispatcher of the shared queue (harness/bin/nrpic-queue
# run) submits them. For each entry's command it sets QUEUE_DISPATCH_VAR=<entry id>:<token> (a wrapper given
# with --cmd inherits it), keeps the entry in state `submitting` with that token, and holds the submit lock
# while the command runs. nrpic-run reads the variable (the one variable of the caller it reads; a job it
# submits gets an environment built from files, without it) to let a card submission through. A job that a
# --cmd wrapper submits itself (sbatch, the scripts) inherits the variable, where it is no longer valid once
# the dispatch has ended: wrappers test their dispatch with `nrpic-queue check-dispatch`, which calls
# queue_dispatch_problem, never by the variable being set. The marker gates the route only; it does not lift
# the cap, which nrpic-run checks for every card submission as before.
QUEUE_DISPATCH_VAR = "NRPIC_QUEUE_DISPATCH"


def queue_dir(home):
    """The state directory of the shared card queue (untracked)."""
    return os.path.join(home, "locks", "queue")


def queue_submit_lock(home):
    """Held by the dispatcher around the count, the entry's command and the count after it."""
    return os.path.join(queue_dir(home), "submit.lock")


def queue_dispatch_problem(wt, environ=None):
    """None when this process runs inside a dispatch of the shared queue for an entry of this worktree, else
    why not: no marker; a marker that names no entry, or an entry that is not being dispatched with that
    token, or one of another owner or worktree; or no dispatch in progress (the submit lock is free)."""
    import fcntl
    env = os.environ if environ is None else environ
    mark = env.get(QUEUE_DISPATCH_VAR, "")
    if not mark:
        return "this call does not come from the dispatcher"
    eid, _, tok = mark.partition(":")
    if not re.fullmatch(r"q\d{4,}", eid) or not tok:
        return f"{QUEUE_DISPATCH_VAR}={mark!r} is not a dispatch marker"
    try:
        e = read_json(os.path.join(queue_dir(wt.home), "entries", eid + ".json"))
    except (OSError, ValueError):
        return f"{QUEUE_DISPATCH_VAR} names entry {eid}, which does not exist"
    if not isinstance(e, dict) or e.get("state") != "submitting" or e.get("dispatch_token") != tok:
        return f"entry {eid} is not being dispatched with this marker"
    if e.get("owner") != wt.owner or os.path.realpath(str(e.get("worktree", ""))) != wt.root:
        return f"entry {eid} belongs to {e.get('owner')} in {e.get('worktree')}, not to {wt.root}"
    try:
        with open(queue_submit_lock(wt.home), "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return None                   # held by the dispatcher: a dispatch is in progress
            fcntl.flock(f, fcntl.LOCK_UN)
    except OSError as ex:
        return f"cannot open the submit lock: {ex}"
    return "no dispatch is in progress (the dispatcher's submit lock is free)"


# ------------------------------------------------------------------ budgets (decisions 0006, 0014)

BUDGET_FILE = "coord/DECISIONS/0006-compute-budget.md"
DECISIONS_DIR = "coord/DECISIONS"


def _decision_texts(wt):
    """{file name: text} of coord/DECISIONS/*.md on main (the orchestrator's copy is
    authoritative), else of the worktree's own copy."""
    out = {}
    r = run(["git", "-C", wt.root, "ls-tree", "--name-only", "main", DECISIONS_DIR + "/"], check=False)
    names = [n for n in r.stdout.split() if n.endswith(".md")] if r.returncode == 0 else []
    for n in names:
        s = run(["git", "-C", wt.root, "show", f"main:{n}"], check=False)
        if s.returncode == 0:
            out[os.path.basename(n)] = s.stdout
    if not out:
        d = os.path.join(wt.root, DECISIONS_DIR)
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if n.endswith(".md"):
                out[n] = open(os.path.join(d, n)).read()
    return out


def owner_from_short(s):
    """A -> A-emd-pbh, A-emd-pbh -> A-emd-pbh, core -> core, orch -> orch (decision 0016 item 2);
    None if no owner."""
    if s in OWNER_IDS or s == "orch":
        return s
    for t in TRACK_IDS:
        if s == t.split("-")[0]:
            return t
    return None


def budget_table(wt, with_source=False):
    """{owner: {"gpu_hours": float, "cores": int}}: the table of decision 0006, then the GPU-hour
    allotments of every later decision that amends 0006 (its first lines say "amends 0006"; the
    sentence "To the next gate: core 40, A 60, ..." is read). Decisions on main are authoritative."""
    texts = _decision_texts(wt)
    base = texts.get(os.path.basename(BUDGET_FILE))
    if base is None:
        raise HarnessError(f"no budget table: {BUDGET_FILE} on main or in {wt.root}")
    table = {}
    for line in base.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and re.fullmatch(r"[0-9.]+", cells[1]) and re.fullmatch(r"[0-9]+", cells[2]):
            table[cells[0]] = {"gpu_hours": float(cells[1]), "cores": int(cells[2])}
    if not table:
        raise HarnessError(f"could not parse the budget table of {BUDGET_FILE}")
    sources = [os.path.basename(BUDGET_FILE)]
    for name in sorted(texts):
        if name <= os.path.basename(BUDGET_FILE):
            continue
        text = texts[name]
        if not re.search(r"amends\s+0006", "\n".join(text.splitlines()[:6]), re.I):
            continue
        m = re.search(r"To the next gate:\s*(.*?)(?:\.\s|\.$|\n\n)", text, re.S)
        if not m:
            continue
        changed = False
        for who, val in re.findall(r"([A-Za-z][A-Za-z-]*)\s+([0-9]+(?:\.[0-9]+)?)", m.group(1)):
            o = owner_from_short(who)
            if o is None:
                continue
            table.setdefault(o, {"gpu_hours": 0.0, "cores": 16})["gpu_hours"] = float(val)
            changed = True
        if changed:
            sources.append(name)
    return (table, sources) if with_source else table


# ------------------------------------------------------------------ git writes

def commit_paths(wt, paths, subject, body="", trailers=None, force_add=False):
    """Path-limited commit of `paths` (relative to the worktree) on the worktree's own branch.
    Waits five seconds and retries while another writer holds index.lock. force_add adds these
    exact paths even when an ignore pattern matches them (run manifests: the repository's
    .gitignore line `runs/` also matches tracks/<ID>/runs/)."""
    msg = subject + ("\n\n" + body.strip() if body.strip() else "")
    if trailers:
        msg += "\n\n" + "\n".join(f"{k}: {v}" for k, v in trailers)
    for attempt in range(60):
        r1 = run(["git", "-C", wt.root, "add"] + (["-f"] if force_add else []) + ["--"] + paths, check=False)
        if r1.returncode == 0:
            r2 = run(["git", "-C", wt.root, "commit", "-q", "-m", msg, "--"] + paths, check=False)
            if r2.returncode == 0:
                return git(wt.root, "rev-parse", "HEAD")
            err = r2.stderr + r2.stdout
        else:
            err = r1.stderr
        if "index.lock" in err:
            time.sleep(5)
            continue
        raise HarnessError(f"git commit failed: {err.strip()}")
    raise HarnessError("git index.lock held for five minutes; commit not made")


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=False)
        f.write("\n")
    os.replace(tmp, path)


def read_json(path):
    with open(path) as f:
        return json.load(f)


def strip_options_prefix(argv):
    """Split ['-C', 'x', 'sub', ...] style global options: returns (c_opt, rest)."""
    c_opt = None
    rest = list(argv)
    while rest and rest[0] in ("-C",):
        if len(rest) < 2:
            raise HarnessError("-C needs a path")
        c_opt = rest[1]
        rest = rest[2:]
    return c_opt, rest


def fnmatch_any(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


# ------------------------------------------------------------------ run manifests (nrpic-run, nrpic-stage)
#
# Two kinds of manifests exist under tracks/<ID>/runs/<run_id>/manifest.json: those written by
# nrpic-run ("schema": "nrpic-run-manifest/1", every field of harness/templates/run_manifest.json)
# and the hand-written ones of wave 1 (decision 0012: the harness reads them as well), whose field
# names and status words vary. manifest_view() reads either kind into one shape and never raises;
# what it had to guess is listed in view["issues"].

SCHEMA = "nrpic-run-manifest/1"
FINAL_STATUSES = ("completed", "failed", "stopped", "superseded")
ACTIVE_STATUSES = ("registered", "running", "submitted")
STATUS_WORDS = {
    "completed": "completed", "complete": "completed", "done": "completed", "finished": "completed",
    "ok": "completed", "success": "completed", "succeeded": "completed", "passed": "completed",
    "pass": "completed",
    "failed": "failed", "fail": "failed", "error": "failed", "crashed": "failed", "aborted": "failed",
    "stopped": "stopped", "cancelled": "stopped", "canceled": "stopped", "killed": "stopped",
    "timeout": "stopped", "preempted": "stopped", "interrupted": "stopped",
    "superseded": "superseded", "obsolete": "superseded", "replaced": "superseded",
    "registered": "registered", "running": "running", "submitted": "submitted", "queued": "submitted",
    "pending": "submitted",
}
RUN_ID_RX = re.compile(r"^(?P<owner>[A-Za-z][A-Za-z0-9-]*?)-(?P<date>\d{8})-(?P<time>\d{6})-(?P<commit>[0-9a-f]{7,40})$")
STANDARD_STATUS_WORDS = FINAL_STATUSES + ACTIVE_STATUSES      # what manifest_view reads without a default
# Decision 0016 item 3: hand-written manifests of waves 1 and 2 count as registered; from wave 2b
# (resumed on 2026-11-19 UTC) on, runs go through `nrpic-run submit`. A run is "of waves 1 and 2"
# when its date (run id, else the manifest's own dates) lies before this day.
WAVE_2B_START = "20261119"


def parse_run_id(rid):
    """(owner id, 'YYYYMMDD-HHMMSS', commit) of a run id in either form (decision 0016 item 2: the
    short form A-20261115-... that nrpic-run writes, with A..F, core, kb, orch; the long form
    A-emd-pbh-20261115-... of waves 1 and 2 stays valid), or None."""
    m = RUN_ID_RX.match(rid or "")
    if not m:
        return None
    owner = owner_from_short(m.group("owner"))
    return (owner, m.group("date") + "-" + m.group("time"), m.group("commit")) if owner else None


def run_date(rid, m=None):
    """'YYYYMMDD' (UTC) of a run: from its id (either form; also a directory name that only carries
    `-YYYYMMDD-HHMMSS-<commit>`), else from the manifest's started/registered/ended/date field; None
    when neither tells."""
    for s in (rid, m.get("run_id") if isinstance(m, dict) else None):
        mm = re.search(r"(?:^|-)(\d{8})-\d{6}-[0-9a-f]{7,40}$", s or "")
        if mm:
            return mm.group(1)
    if isinstance(m, dict):
        for k in ("started", "registered", "ended", "date", "created"):
            mm = re.match(r"^\s*(\d{4})-?(\d{2})-?(\d{2})", str(m.get(k) or ""))
            if mm:
                return "".join(mm.groups())
    return None


def is_wave12(date):
    """A run date before wave 2b (decision 0016 item 3)."""
    return bool(date) and date < WAVE_2B_START


WAIVERS_FILE = "coord/WAIVERS.md"                 # decision 0019 item 6
_WAIVER_LEAD = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|\|\s*)?`?([A-Za-z][A-Za-z0-9-]*-\d{8}-\d{6}-[0-9a-f]{7,40})`?"
                          r"(?![0-9A-Za-z_-])(.*)$")


def parse_waivers(text):
    """{run id: reason} of the text of coord/WAIVERS.md: one run id per line, at the start of the line
    (also as a list item or the first cell of a table row, in backticks or not), followed by the reason.
    Headings, prose, table headers and lines that begin with anything else are ignored."""
    out = {}
    for line in (text or "").splitlines():
        m = _WAIVER_LEAD.match(line)
        if not m or not parse_run_id(m.group(1)):
            continue
        reason = m.group(2).strip().strip("|").strip()
        reason = re.sub(r"^[-:–—|]+\s*", "", reason).strip().rstrip("|").strip()
        out.setdefault(m.group(1), reason or "(no reason given)")
    return out


def waivers(root):
    """{run id: reason} of main's committed coord/WAIVERS.md (decision 0019 item 6), read through
    git from any worktree of the repository; {} when main has none. A working-tree copy is never
    read: the orchestrator grants a waiver by committing it on main."""
    r = run(["git", "-C", root, "show", f"main:{WAIVERS_FILE}"], check=False)
    return parse_waivers(r.stdout) if r.returncode == 0 else {}


def _num(x):
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, dict):                         # e.g. {"run1": 3.38, "run2": 1.48}
        vals = [_num(v) for v in x.values()]
        vals = [v for v in vals if v is not None]
        return sum(vals) if vals else None
    if isinstance(x, str):
        m = re.match(r"^\s*([0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?)\s*(s|sec|seconds|h|hours|min)?\s*$", x)
        if m:
            v = float(m.group(1))
            return v * 3600 if m.group(2) in ("h", "hours") else v * 60 if m.group(2) == "min" else v
    return None


def _first(*vals):
    for v in vals:
        if v is not None and v != "":
            return v
    return None


# every top-level key any version of nrpic-run has written (submit and finish), and `continuations`, which a
# wrapper of the shared card queue adds when it continues a chain in place (decision 0039 item 5; below)
NRPIC_RUN_KEYS = ("schema", "run_id", "track", "gate", "kind", "purpose", "preregistered_in", "launcher", "command",
                  "cwd", "git", "code", "env", "input", "inputs", "batch_entries", "resources", "slurm", "outputs",
                  "status", "exit_code", "registered", "started", "ended", "finished", "parents", "notes",
                  "budget_at_submit", "continuations")


# ------------------------------------------------------------------ runs continued in place (decision 0039 item 5)
#
# A chain cut by preemption, by the queue cap or by its segment cap is continued IN PLACE by a wrapper given to
# `nrpic-queue add --cmd` (C: tracks/C-sidm/longruns/seq/qitem.sh; D: tracks/D-bh-dress/g2long/tools/
# continue_chain.sh): scripts/submit_chain.sh is started again on the run's own directory and resumes from its
# newest restart file, under the run's own id. The wrapper appends one record to the manifest's optional
# top-level list `continuations` and commits the manifest:
#
#   "continuations": [ {"at": "2026-11-24T12:59:33Z",              when (ISO 8601 to the second, with a zone:
#                                                                   Z, +HH:MM or +HHMM)                  required
#                       "from_restart": "<path of the .rst>" | null, the restart file it resumes from; null when
#                                                                   the chain had none yet (its waiting job was
#                                                                   cancelled before it ran)             required
#                       "job_id": "5210",                          the Slurm job it submitted (digits; null when
#                                                                   not known yet)                     } at least
#                       "segments_used_before": 5,                 the chain's segment counter before (int >= 0)} one of
#                       "max_segments": 12,                        the segment cap after (int >= 1)    } these
#                       "by" | "via": "<wrapper> (queue entry ...)", who continued it (non-empty)   required, one
#                       ...: any further keys (reason, kind, status_before, extra_athena_args, predictions) } ]
#
# Records are appended in order of `at`. A manifest that was final before the continuation (its `finished`,
# else `ended`, earlier than the last record) is open again: `nrpic-run finish <run_id>` closes it again without
# --status, from the chain's STATUS, and counts the card-hours of every job of the chain. A manifest whose
# `continuations` is malformed is refused by finish, by the stage check's run check and by the pre-commit hook,
# with what is wrong.
CONTINUATION_WHO = ("by", "via")
CONTINUATION_POINT = ("job_id", "segments_used_before", "max_segments")
_ISO_RX = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d+)?(Z|[+-]\d{2}:?\d{2})")


def parse_time(s):
    """An aware datetime of 'YYYY-MM-DDTHH:MM:SS[.fff](Z|+HH:MM|+HHMM)', or None."""
    if not isinstance(s, str):
        return None
    m = _ISO_RX.fullmatch(s.strip())
    if not m:
        return None
    zone = "+0000" if m.group(3) == "Z" else m.group(3).replace(":", "")
    try:
        return datetime.datetime.strptime(m.group(1) + zone, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return None


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def continuation_problems(value):
    """[] when `value` (a manifest's `continuations`) is a well-formed list of records (schema above), else one
    sentence per fault, naming the record by its index."""
    if not isinstance(value, list):
        return [f"`continuations` must be a list of records, one per continuation (it is a {type(value).__name__})"]
    out, last = [], None
    for i, rec in enumerate(value):
        w = f"record [{i}]"
        if not isinstance(rec, dict):
            out.append(f"{w} is a {type(rec).__name__}, not an object")
            continue
        at = parse_time(rec.get("at"))
        if "at" not in rec:
            out.append(f"{w} has no `at` (when it was continued, ISO 8601 with a zone, e.g. 2026-11-24T12:59:33Z)")
        elif at is None:
            out.append(f"{w}: `at` {rec.get('at')!r} is not an ISO 8601 time to the second with a zone "
                       "(Z, +HH:MM or +HHMM)")
        if "from_restart" not in rec:
            out.append(f"{w} has no `from_restart` (the restart file it resumes from, or null when there was none)")
        elif rec["from_restart"] is not None and not (isinstance(rec["from_restart"], str) and rec["from_restart"].strip()):
            out.append(f"{w}: `from_restart` must be the path of a restart file or null (it is {rec['from_restart']!r})")
        who = [k for k in CONTINUATION_WHO if k in rec]
        if not who:
            out.append(f"{w} names nobody: give `by` (or `via`), the wrapper and queue entry that continued it")
        for k in who:
            if not (isinstance(rec[k], str) and rec[k].strip()):
                out.append(f"{w}: `{k}` must be a non-empty string (it is {rec[k]!r})")
        if not any(rec.get(k) is not None for k in CONTINUATION_POINT):
            out.append(f"{w} names no job or segment: give `job_id`, `segments_used_before` or `max_segments`")
        j = rec.get("job_id")
        if j is not None and not ((isinstance(j, str) and j.isdigit()) or (_is_int(j) and j >= 0)):
            out.append(f"{w}: `job_id` must be a Slurm job id of digits (it is {j!r})")
        s = rec.get("segments_used_before")
        if s is not None and not (_is_int(s) and s >= 0):
            out.append(f"{w}: `segments_used_before` must be an integer >= 0 (it is {s!r})")
        s = rec.get("max_segments")
        if s is not None and not (_is_int(s) and s >= 1):
            out.append(f"{w}: `max_segments` must be an integer >= 1 (it is {s!r})")
        if at is not None:
            if last is not None and at < last:
                out.append(f"{w} is dated before the record above it: records are appended in order of `at`")
            last = at
    return out


def reopened_at(m):
    """The `at` of the last continuation when it is later than the manifest's `finished` (else `ended`): a run that
    was closed and then continued in place, so that finish must close it again. None otherwise (also when the
    times cannot be read)."""
    if not isinstance(m, dict) or not isinstance(m.get("continuations"), list) or not m["continuations"]:
        return None
    rec = m["continuations"][-1]
    at = parse_time(rec.get("at")) if isinstance(rec, dict) else None
    closed = parse_time(m.get("finished")) or parse_time(m.get("ended"))
    if at is None or closed is None or at <= closed:
        return None
    return rec.get("at")


def continuation_job_ids(m):
    """The job ids the continuation records name (strings, in order, without repeats)."""
    out = []
    recs = m.get("continuations") if isinstance(m, dict) else None
    for rec in recs if isinstance(recs, list) else []:
        j = rec.get("job_id") if isinstance(rec, dict) else None
        if j is not None and str(j).isdigit() and str(j) not in out:
            out.append(str(j))
    return out


# ------------------------------------------------------------------ checksums of outputs (decision 0039 item 5)
#
# Outputs are hashed with an incremental cache per run directory, <output dir>/.nrpic/sha256cache.json (beside
# .nrpic/launch.json and result.json, in the part of the directory that is never checksummed): one entry per
# relative path with the file's size and modification time in nanoseconds when it was hashed, and its sha256. A
# file is hashed again only when it is new, or its size or modification time differs from its entry, or its
# entry is "racy" (the file had been modified less than RACY_NS before it was hashed, so a later write within the
# same clock tick could keep the time; such a file is hashed at the next pass too). --full (finish and both
# verify commands) hashes every file and rewrites the cache. Up to HASH_THREADS files are hashed at once (hashlib
# releases the GIL on large buffers); never more. A checksum taken from the cache proves CACHE_SENTENCE.
HASH_THREADS = 4
SHA_CACHE = (".nrpic", "sha256cache.json")
SHA_CACHE_SCHEMA = "nrpic-sha256-cache/1"
RACY_NS = 2 * 10 ** 9
CACHE_SENTENCE = ("a checksum taken from the cache proves unchanged size and modification time since it was hashed, "
                  "not bytes read again")


def hash_stats():
    """Counters of one or more passes of OutputHasher (added with add_hash_stats)."""
    return {"files": 0, "rehashed": 0, "rehashed_bytes": 0, "cached": 0, "cached_bytes": 0, "full": False,
            "notes": []}


def add_hash_stats(into, s):
    for k in ("files", "rehashed", "rehashed_bytes", "cached", "cached_bytes"):
        into[k] += s[k]
    into["full"] = into["full"] or s["full"]
    into["notes"] += s["notes"]
    return into


def gb(n):
    return f"{n / 1e9:.2f} GB" if n >= 1e8 else f"{n / 1e6:.1f} MB"


def hash_summary(s, always=False):
    """One line for a report: how many output files were hashed again and how many taken from the cache, with
    CACHE_SENTENCE whenever the cache gave any (always: also when it gave none, for the stage report)."""
    if not s["files"]:
        return "no output files checksummed"
    line = (f"{s['files']} output files: {s['rehashed']} hashed again (bytes read, {gb(s['rehashed_bytes'])}), "
            f"{s['cached']} taken from the cache ({gb(s['cached_bytes'])})" + (" (--full)" if s["full"] else ""))
    if s["cached"]:
        line += f"; {CACHE_SENTENCE}; --full reads every byte"
    elif always:
        line += f"; every byte read again (none taken from the cache, where {CACHE_SENTENCE})"
    return line


class OutputHasher:
    """sha256 of files of one output directory `root`, with its cache (SHA_CACHE). digests(rels) hashes what the
    cache cannot vouch for, in up to HASH_THREADS threads; save() writes the entries of the files of this pass
    (those not looked at are dropped). The cache is never required: unreadable, it is ignored (a note), and
    not writable, the pass is still complete (a note)."""

    def __init__(self, root, full=False):
        self.root = root
        self.path = os.path.join(root, *SHA_CACHE)
        self.full = full
        self.stats = hash_stats()
        self.stats["full"] = bool(full)
        self.errors = {}
        self.seen = {}
        self.old = {}
        try:
            doc = read_json(self.path)
            if isinstance(doc, dict) and doc.get("schema") == SHA_CACHE_SCHEMA and isinstance(doc.get("entries"), dict):
                self.old = doc["entries"]
            else:
                self.stats["notes"].append(f"{self.path} is not a cache of {SHA_CACHE_SCHEMA}: ignored, files hashed")
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as e:
            self.stats["notes"].append(f"{self.path} unreadable ({e}): ignored, files hashed")

    @staticmethod
    def _trusted(e, st):
        return (isinstance(e, dict) and e.get("size") == st.st_size and e.get("mtime_ns") == st.st_mtime_ns
                and isinstance(e.get("sha256"), str) and len(e["sha256"]) == 64 and _is_int(e.get("hashed_ns"))
                and st.st_mtime_ns <= e["hashed_ns"] - RACY_NS)

    def _hash_one(self, rel):
        p = os.path.join(self.root, rel)
        t0 = time.time_ns()
        st = os.stat(p)
        d = sha256_file(p)
        st2 = os.stat(p)
        same = (st.st_size, st.st_mtime_ns) == (st2.st_size, st2.st_mtime_ns)
        return d, st, ({"size": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": d, "hashed_ns": t0} if same else None)

    def digests(self, rels):
        """{rel: sha256} for the relative paths `rels`; a file that cannot be read is left out and its error
        is in self.errors[rel]."""
        out, todo = {}, []
        for rel in rels:
            try:
                st = os.stat(os.path.join(self.root, rel))
            except OSError as e:
                self.errors[rel] = str(e)
                continue
            e = None if self.full else self.old.get(rel)
            if self._trusted(e, st):
                out[rel] = e["sha256"]
                self.seen[rel] = e
                self.stats["cached"] += 1
                self.stats["cached_bytes"] += st.st_size
            else:
                todo.append((st.st_size, rel))
        todo.sort(reverse=True)                  # the largest first, so that the threads end together
        if todo:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(HASH_THREADS, len(todo))) as ex:
                futs = {ex.submit(self._hash_one, rel): rel for _, rel in todo}
                for f in concurrent.futures.as_completed(futs):
                    rel = futs[f]
                    try:
                        d, st, entry = f.result()
                    except OSError as e:
                        self.errors[rel] = str(e)
                        continue
                    out[rel] = d
                    if entry is not None:
                        self.seen[rel] = entry
                    else:
                        self.stats["notes"].append(f"{rel} changed while it was hashed (not cached)")
                    self.stats["rehashed"] += 1
                    self.stats["rehashed_bytes"] += st.st_size
        self.stats["files"] += len(out)
        return out

    def save(self):
        doc = {"schema": SHA_CACHE_SCHEMA, "algorithm": "sha256", "dir": self.root, "written": utcnow(),
               "meaning": CACHE_SENTENCE, "entries": dict(sorted(self.seen.items()))}
        tmp = f"{self.path}.tmp{os.getpid()}"
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(tmp, "w") as f:
                json.dump(doc, f, indent=0)
                f.write("\n")
            os.replace(tmp, self.path)
            return True
        except OSError as e:
            self.stats["notes"].append(f"cache not written ({e}); the next pass hashes again")
            try:
                os.remove(tmp)
            except OSError:
                pass
            return False


_INPUT_MEMO = {}


def sha256_memo(path):
    """sha256 of an input file, read once per process for a given (path, size, modification time): the stage
    check meets one executable in many manifests. Bytes are read in every process (no cache on disk)."""
    st = os.stat(path)
    key = (os.path.realpath(path), st.st_size, st.st_mtime_ns)
    if key not in _INPUT_MEMO:
        _INPUT_MEMO[key] = sha256_file(path)
    return _INPUT_MEMO[key]


def hand_marker(m):
    """Why a manifest that names the nrpic-run schema was nevertheless written by hand (waves 1 and 2:
    helpers' registration scripts copied the schema), or '': a `registered_by` field, a launcher other
    than local, batch, chain ("local (hand registration)"), or another top-level key nrpic-run never
    writes (card_hours, output_dir, commit, ...)."""
    if not isinstance(m, dict):
        return ""
    if m.get("registered_by"):
        return f"registered_by: {str(m['registered_by'])[:80]}"
    la = m.get("launcher")
    if la is not None and la not in ("local", "batch", "chain"):
        return f"launcher {str(la)[:60]!r}"
    extra = sorted(k for k in m if k not in NRPIC_RUN_KEYS)
    if extra:
        return "fields nrpic-run never writes: " + ", ".join(extra[:5])
    return ""


def manifest_view(m, home, where=""):
    """One manifest of either kind, read into a fixed shape. Never raises.

    Keys: ok (a JSON object), schema (names the nrpic-run schema), hand (written by hand: no schema, or
    a hand_marker), run_id, owner, status (one of
    FINAL_STATUSES, ACTIVE_STATUSES or "unknown"), status_raw, final, gate, kind, purpose, launcher,
    outdir (absolute, or None), outdir_rel, gpu_hours (used, None if not recorded),
    gpu_hours_requested, walltime_s, cores, exit_code, sha, inputs (list of {path, sha256, tracked}),
    continuations (number of records), reopened (the `at` of a continuation after the close, else None),
    issues (what was not in the nrpic-run schema; a malformed `continuations`), where."""
    v = {"ok": isinstance(m, dict), "where": where, "issues": [], "raw": m}
    if not isinstance(m, dict):
        v.update(schema=False, hand=True, run_id=None, owner=None, status="unknown", status_raw=None, final=True,
                 gate=None, kind=None, purpose="", launcher=None, outdir=None, outdir_rel=None,
                 gpu_hours=None, gpu_hours_requested=0.0, walltime_s=None, cores=1, exit_code=None,
                 sha=None, inputs=[], continuations=0, reopened=None)
        v["issues"].append(f"not a JSON object ({type(m).__name__})")
        return v
    res = m.get("resources") if isinstance(m.get("resources"), dict) else {}
    outs = m.get("outputs")
    git_ = m.get("git") if isinstance(m.get("git"), dict) else {}
    v["schema"] = m.get("schema") == SCHEMA
    v["run_id"] = m.get("run_id") if isinstance(m.get("run_id"), str) else None
    v["owner"] = _first(m.get("track"), m.get("owner"))
    raw = m.get("status")
    v["status_raw"] = raw
    word = re.split(r"[\s(:;,]+", raw.strip().lower())[0] if isinstance(raw, str) and raw.strip() else None
    st = STATUS_WORDS.get(word)
    ec = _first(m.get("exit_code"), m.get("exit_status"), m.get("rc"))
    v["exit_code"] = ec
    if st is None:
        if isinstance(ec, int) and not isinstance(ec, bool):
            st = "completed" if ec == 0 else "failed"
            v["issues"].append(f"status {raw!r} read as {st} from exit code {ec}")
        else:
            st = "unknown"
            v["issues"].append("no status" if raw is None else f"status {raw!r} not understood")
    elif raw != st:
        v["issues"].append(f"status {raw!r} read as {st}")
    v["status"] = st
    v["final"] = st not in ACTIVE_STATUSES
    v["gate"] = m.get("gate") if isinstance(m.get("gate"), str) else None
    v["kind"] = m.get("kind")
    v["purpose"] = str(_first(m.get("purpose"), m.get("label"), m.get("tag"), m.get("test")) or "")
    v["launcher"] = m.get("launcher") if isinstance(m.get("launcher"), str) else None
    od = None
    if isinstance(outs, dict):
        od = _first(outs.get("dir"), outs.get("directory"), outs.get("path"))
    elif isinstance(outs, str):
        od = outs
    od = _first(od, m.get("output_dir"), m.get("output_directory"), m.get("outputs_dir"), m.get("out_dir"))
    if not isinstance(od, str):
        od = None
    if od is None:
        v["issues"].append("no output directory recorded")
        v["outdir"] = v["outdir_rel"] = None
    else:
        p = od if os.path.isabs(od) else os.path.join(home, od)
        v["outdir"] = os.path.normpath(p)
        v["outdir_rel"] = os.path.relpath(v["outdir"], home)
        if not (isinstance(outs, dict) and outs.get("dir")):
            v["issues"].append("output directory read from a field other than outputs.dir")
    gh = _num(_first(res.get("gpu_hours"), res.get("card_hours"), m.get("gpu_hours"), m.get("card_hours")))
    v["gpu_hours"] = gh
    v["gpu_hours_requested"] = _num(res.get("gpu_hours_requested")) or 0.0
    v["walltime_s"] = _num(_first(res.get("walltime_s"), m.get("wall_time_s"), m.get("walltime_s"),
                                  m.get("wall_time")))
    v["cores"] = int(_num(_first(res.get("cores"), m.get("cores"))) or 1)
    v["sha"] = _first(git_.get("sha"), m.get("commit"), m.get("git_rev"), m.get("sha"))
    if not isinstance(v["sha"], str):
        v["sha"] = None
    ins = []
    for rec in m.get("inputs") or []:
        if not isinstance(rec, dict):
            continue
        p = _first(rec.get("path"), rec.get("file"))
        if isinstance(p, str):
            ins.append({"path": p, "sha256": rec.get("sha256"), "tracked": rec.get("tracked")})
    v["inputs"] = ins
    v["hand"] = (not v["schema"]) or bool(hand_marker(m))
    if not v["schema"]:
        v["issues"].insert(0, "hand-written (not the nrpic-run schema)")
    v["continuations"] = len(m["continuations"]) if isinstance(m.get("continuations"), list) else 0
    if "continuations" in m:
        v["issues"] += ["continuations: " + p for p in continuation_problems(m["continuations"])]
    v["reopened"] = reopened_at(m) if v["final"] else None
    if v["reopened"]:
        v["issues"].append(f"continued in place at {v['reopened']} after it was closed: close it again with finish")
    if v["run_id"] is None:
        v["issues"].append("no run_id")
    elif parse_run_id(v["run_id"]) is None:
        v["issues"].append(f"run_id {v['run_id']!r} is not <owner>-<YYYYMMDD-HHMMSS>-<commit7>")
    if v["gate"] is None:
        v["issues"].append("no gate")
    return v


def read_branch_manifests(root, branches, owner):
    """{(branch, path): (text or None, error or None)} for every tracks/<owner>/runs/*/manifest.json
    on the given branches, read in one `git cat-file --batch` (identical blobs are read once)."""
    entries, blobs = [], {}
    for br in branches:
        r = run(["git", "-C", root, "ls-tree", "-r", br, "--", f"tracks/{owner}/runs"], check=False)
        for line in r.stdout.splitlines():
            meta, _, path = line.partition("\t")
            parts = meta.split()
            if len(parts) == 3 and parts[1] == "blob" and path.endswith("/manifest.json"):
                entries.append((br, path, parts[2]))
                blobs[parts[2]] = None
    if blobs:
        p = subprocess.run(["git", "-C", root, "cat-file", "--batch"],
                           input=("\n".join(blobs) + "\n").encode(), capture_output=True, env=boot_env())
        data, pos = p.stdout, 0
        for sha in list(blobs):
            nl = data.find(b"\n", pos)
            if nl < 0:
                break
            head = data[pos:nl].split()
            pos = nl + 1
            if len(head) == 3 and head[1] == b"blob":
                size = int(head[2])
                blobs[sha] = data[pos:pos + size].decode("utf-8", "replace")
                pos += size + 1
    return {(br, path): blobs.get(sha) for br, path, sha in entries}


def git_blob_sha256(root, rev, path):
    r = subprocess.run(["git", "-C", root, "show", f"{rev}:{path}"], capture_output=True, env=boot_env())
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def verify_run(home, root, m, outputs=True, full=False, stats=None):
    """Problems found when re-checking one run manifest (either kind; see manifest_view): a malformed
    `continuations`, a run continued after it was closed; output checksums against sha256sums.txt (and
    that file against the manifest), through the run directory's cache unless full (OutputHasher; the
    counters are added to `stats`, a hash_stats() dict, when given); tracked inputs against their blobs at
    the run's commit, untracked inputs against the files still on disk. For a hand-written manifest of
    wave 1, what it does not record is a note, not a problem. Returns (problems, notes, n_outputs)."""
    problems, notes, n = [], [], 0
    v = manifest_view(m, home)
    if not v["ok"]:
        return [v["issues"][0]], notes, 0
    hand = v["hand"]
    if "continuations" in m:
        problems += ["continuations: " + p for p in continuation_problems(m["continuations"])]
    if v["status"] in ACTIVE_STATUSES:
        problems.append(f"status is {v['status_raw']}: not finished (nrpic-run finish)")
    elif v["status"] == "unknown":
        (notes if hand else problems).append(f"status {v['status_raw']!r}: cannot tell whether the run finished")
    elif v["status_raw"] != v["status"]:
        notes.append(f"status {v['status_raw']!r} read as {v['status']}")
    if v["reopened"]:
        (notes if hand else problems).append(
            f"continued in place at {v['reopened']}, after it was closed as {v['status_raw']}: its outputs and "
            f"card-hours are those of the close; close it again (nrpic-run finish {v['run_id']})")
    outdir = v["outdir"]
    if outputs:
        sums = os.path.join(outdir, "sha256sums.txt") if outdir else None
        if outdir is None:
            (notes if hand else problems).append("no output directory recorded")
        elif not os.path.isfile(sums):
            if hand:
                notes.append(f"no {os.path.relpath(sums, home)} (hand-written manifest; outputs not re-verifiable)")
            else:
                problems.append(f"missing {sums}")
        else:
            outs = m.get("outputs") if isinstance(m.get("outputs"), dict) else {}
            rec = outs.get("sha256sums_sha256")
            if rec and sha256_file(sums) != rec:
                problems.append("sha256sums.txt differs from the one recorded in the manifest")
            listed, rows = set(), []
            for line in open(sums, errors="replace"):
                if not line.strip():
                    continue
                digest, sep, rel = line.rstrip("\n").partition("  ")
                if not sep:
                    digest, _, rel = line.strip().partition(" ")
                    rel = rel.lstrip("*").strip()
                listed.add(os.path.normpath(rel))
                n += 1
                rows.append((rel, digest))
            present = []
            for rel, digest in rows:
                if not os.path.isfile(os.path.join(outdir, rel)):
                    problems.append(f"missing output {rel}")
                else:
                    present.append(rel)
            hasher = OutputHasher(outdir, full=full)
            got = hasher.digests(list(dict.fromkeys(present)))
            for rel, digest in rows:
                if rel in hasher.errors:
                    problems.append(f"cannot read output {rel}: {hasher.errors[rel]}")
                elif rel in got and got[rel] != digest:
                    problems.append(f"changed output {rel}")
            hasher.save()
            if stats is not None:
                add_hash_stats(stats, hasher.stats)
            if not hand:
                for dirpath, dirnames, filenames in os.walk(outdir):
                    rel = os.path.relpath(dirpath, outdir)
                    if rel == ".":
                        dirnames[:] = [d for d in dirnames if d != ".nrpic"]
                    for fn in filenames:
                        relf = os.path.normpath(os.path.join(rel, fn))
                        if (relf != "sha256sums.txt" and relf not in listed
                                and not os.path.islink(os.path.join(dirpath, fn))):
                            problems.append(f"output not in sha256sums.txt: {relf}")
    sha = v["sha"]
    for rec in v["inputs"]:
        path, digest = rec["path"], rec["sha256"]
        if not isinstance(digest, str):
            notes.append(f"input {path}: no sha256 recorded")
            continue
        if rec.get("tracked") and sha:
            got = git_blob_sha256(root, sha, path)
            if got is None:
                problems.append(f"input {path} not in commit {sha[:7]}")
            elif got != digest:
                problems.append(f"input {path}: blob at {sha[:7]} differs from the recorded sha256")
            continue
        p = path if os.path.isabs(path) else os.path.join(root, path)
        if os.path.isfile(p):
            if sha256_memo(p) != digest:
                (notes if hand else problems).append(f"input {path} changed since the run (sha256 differs)")
        else:
            notes.append(f"input {path} no longer present (not re-verifiable)")
    return problems, notes, n
