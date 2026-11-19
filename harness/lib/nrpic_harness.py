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


# every top-level key any version of nrpic-run has written (submit and finish)
NRPIC_RUN_KEYS = ("schema", "run_id", "track", "gate", "kind", "purpose", "preregistered_in", "launcher", "command",
                  "cwd", "git", "code", "env", "input", "inputs", "batch_entries", "resources", "slurm", "outputs",
                  "status", "exit_code", "registered", "started", "ended", "finished", "parents", "notes",
                  "budget_at_submit")


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
    issues (what was not in the nrpic-run schema), where."""
    v = {"ok": isinstance(m, dict), "where": where, "issues": [], "raw": m}
    if not isinstance(m, dict):
        v.update(schema=False, hand=True, run_id=None, owner=None, status="unknown", status_raw=None, final=True,
                 gate=None, kind=None, purpose="", launcher=None, outdir=None, outdir_rel=None,
                 gpu_hours=None, gpu_hours_requested=0.0, walltime_s=None, cores=1, exit_code=None,
                 sha=None, inputs=[])
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


def verify_run(home, root, m, outputs=True):
    """Problems found when re-checking one run manifest (either kind; see manifest_view): output
    checksums against sha256sums.txt (and that file against the manifest), tracked inputs against
    their blobs at the run's commit, untracked inputs against the files still on disk. For a
    hand-written manifest of wave 1, what it does not record is a note, not a problem.
    Returns (problems, notes, n_outputs)."""
    problems, notes, n = [], [], 0
    v = manifest_view(m, home)
    if not v["ok"]:
        return [v["issues"][0]], notes, 0
    hand = v["hand"]
    if v["status"] in ACTIVE_STATUSES:
        problems.append(f"status is {v['status_raw']}: not finished (nrpic-run finish)")
    elif v["status"] == "unknown":
        (notes if hand else problems).append(f"status {v['status_raw']!r}: cannot tell whether the run finished")
    elif v["status_raw"] != v["status"]:
        notes.append(f"status {v['status_raw']!r} read as {v['status']}")
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
            listed = set()
            for line in open(sums, errors="replace"):
                if not line.strip():
                    continue
                digest, sep, rel = line.rstrip("\n").partition("  ")
                if not sep:
                    digest, _, rel = line.strip().partition(" ")
                    rel = rel.lstrip("*").strip()
                listed.add(os.path.normpath(rel))
                n += 1
                p = os.path.join(outdir, rel)
                if not os.path.isfile(p):
                    problems.append(f"missing output {rel}")
                elif sha256_file(p) != digest:
                    problems.append(f"changed output {rel}")
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
            if sha256_file(p) != digest:
                (notes if hand else problems).append(f"input {path} changed since the run (sha256 differs)")
        else:
            notes.append(f"input {path} no longer present (not re-verifiable)")
    return problems, notes, n
