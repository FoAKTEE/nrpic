"""Shared code of the harness commands nrpic-env, nrpic-run and nrpic-stage (standard library only).

Every command runs with `python3 -I` and builds the environment of its subprocesses from files
(the machine file harness/env/machines/<host>.sh, the passwd entry), never from the caller's
environment variables. The worktree a command acts on is the one that contains the command's
own file (harness/bin/<cmd> inside a worktree), unless -C <path> names another one.

Layout facts (decision 0001): the linked worktrees are wt/<ID> inside the main checkout; the data
roots scratch/, kb-data/, cache/, locks/ are inside the main checkout too.
"""
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


# ------------------------------------------------------------------ budgets (decision 0006)

BUDGET_FILE = "coord/DECISIONS/0006-compute-budget.md"


def budget_table(wt):
    """{owner: {"gpu_hours": float, "cores": int}} from the table of decision 0006 on main
    (the orchestrator's copy is authoritative); the worktree's copy if main lacks it."""
    r = run(["git", "-C", wt.root, "show", f"main:{BUDGET_FILE}"], check=False)
    text = r.stdout if r.returncode == 0 else None
    if text is None:
        p = os.path.join(wt.root, BUDGET_FILE)
        if not os.path.isfile(p):
            raise HarnessError(f"no budget table: {BUDGET_FILE} on main or in {wt.root}")
        text = open(p).read()
    table = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and re.fullmatch(r"[0-9.]+", cells[1]) and re.fullmatch(r"[0-9]+", cells[2]):
            table[cells[0]] = {"gpu_hours": float(cells[1]), "cores": int(cells[2])}
    if not table:
        raise HarnessError(f"could not parse the budget table of {BUDGET_FILE}")
    return table


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


# ------------------------------------------------------------------ run verification (nrpic-run, nrpic-stage)

FINAL_STATUSES = ("completed", "failed", "stopped")


def git_blob_sha256(root, rev, path):
    r = subprocess.run(["git", "-C", root, "show", f"{rev}:{path}"], capture_output=True, env=boot_env())
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def verify_run(home, root, m, outputs=True):
    """Problems found when re-checking one run manifest: output checksums against sha256sums.txt
    (and that file against the manifest), tracked inputs against their blobs at the run's commit,
    untracked inputs against the files still on disk. Returns (problems, notes, n_outputs)."""
    problems, notes, n = [], [], 0
    if m.get("status") not in FINAL_STATUSES:
        problems.append(f"status is {m.get('status')}: not finished (nrpic-run finish)")
    outdir = os.path.join(home, m.get("outputs", {}).get("dir", ""))
    sums = os.path.join(outdir, "sha256sums.txt")
    if outputs:
        if not os.path.isfile(sums):
            problems.append(f"missing {sums}")
        else:
            rec = m["outputs"].get("sha256sums_sha256")
            if rec and sha256_file(sums) != rec:
                problems.append("sha256sums.txt differs from the one recorded in the manifest")
            listed = set()
            for line in open(sums):
                if not line.strip():
                    continue
                digest, rel = line.rstrip("\n").split("  ", 1)
                listed.add(rel)
                n += 1
                p = os.path.join(outdir, rel)
                if not os.path.isfile(p):
                    problems.append(f"missing output {rel}")
                elif sha256_file(p) != digest:
                    problems.append(f"changed output {rel}")
            for dirpath, dirnames, filenames in os.walk(outdir):
                rel = os.path.relpath(dirpath, outdir)
                if rel == ".":
                    dirnames[:] = [d for d in dirnames if d != ".nrpic"]
                for fn in filenames:
                    relf = os.path.normpath(os.path.join(rel, fn))
                    if (relf != "sha256sums.txt" and relf not in listed
                            and not os.path.islink(os.path.join(dirpath, fn))):
                        problems.append(f"output not in sha256sums.txt: {relf}")
    sha = m.get("git", {}).get("sha")
    for rec in m.get("inputs", []):
        if rec.get("tracked"):
            got = git_blob_sha256(root, sha, rec["path"])
            if got is None:
                problems.append(f"input {rec['path']} not in commit {str(sha)[:7]}")
            elif got != rec["sha256"]:
                problems.append(f"input {rec['path']}: blob at {sha[:7]} differs from the recorded sha256")
            continue
        p = rec["path"] if os.path.isabs(rec["path"]) else os.path.join(root, rec["path"])
        if os.path.isfile(p):
            if sha256_file(p) != rec["sha256"]:
                problems.append(f"input {rec['path']} changed since the run (sha256 differs)")
        else:
            notes.append(f"input {rec['path']} no longer present (not re-verifiable)")
    return problems, notes, n
