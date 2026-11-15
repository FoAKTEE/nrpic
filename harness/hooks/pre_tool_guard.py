#!/usr/bin/python3 -I
"""PreToolUse guard of the NRPIC-cosmology program (brief section 11.5). PROPOSED, NOT INSTALLED
(decision 0008): harness/claude/settings.json wires it to Edit|Write|NotebookEdit|MultiEdit|Bash.

Input: the hook JSON on stdin (tool_name, tool_input, cwd). The session's identity is the worktree
of $CLAUDE_PROJECT_DIR (where the session was started), else of the input cwd; its branch gives the
owner (track/<ID>[--x] -> <ID>, core/* -> core, kb/* -> kb, main -> orch).

Denied, with a reason that says what to do instead:
  Edit/Write/NotebookEdit/MultiEdit outside the owner's paths: own worktree's tracks/<ID>/** and the
    globs of tracks/<ID>/OWNERSHIP; scratch/<ID>/** of the main checkout; kb-data/** for kb only;
    for orch everything in the main checkout except wt/**, tracks/** (asked for .claude/**);
    Claude Code's plan files; memory files for orch only (decision 0007).
  Bash: explicit write targets (redirections, cp/mv/rsync/install/ln destinations, rm/mkdir/touch/
    tee/chmod/truncate arguments, sed -i files, dd of=) checked by the same rule; git write commands
    run in (or -C into) another worktree; force pushes, --no-verify, pushes of another branch or of
    tags by a track; git worktree remove/prune, git branch -d/-D; simulations started without
    harness/bin/nrpic-run (athena, scripts/gpu_run.sh, gpu_batch.sh, submit_chain.sh other than
    --status/--stop, sbatch, srun, salloc); rm with a path built from a shell variable; pkill,
    killall, kill $(pgrep ...); curl, wget.
Anything else gets no output (the normal permission flow continues). Outside the nrpic repository,
on unreadable input or on an internal error the guard allows (fail-open: a broken guard must not
stall every session); harness/claude/INSTALL.md discusses this choice.
"""
import json
import os
import re
import shlex
import subprocess
import sys

TRACKS = ("A-emd-pbh", "B-emd-gw", "C-sidm", "D-bh-dress", "E-stoch-inf", "F-hills")
OWNERS = ("core", "kb") + TRACKS
WRAPPERS = {"env", "timeout", "nohup", "nice", "time", "stdbuf", "taskset", "ionice", "command", "exec",
            "builtin", "xargs", "srun_wrapper"}
SIM_SCRIPTS = {"gpu_run.sh", "gpu_batch.sh", "_athena_job.sh", "submit_chain.sh"}
SLURM_LAUNCH = {"sbatch", "srun", "salloc"}
GIT_WRITE = {"commit", "add", "merge", "push", "checkout", "switch", "reset", "rebase", "stash", "tag",
             "worktree", "branch", "rm", "mv", "restore", "cherry-pick", "revert", "am", "apply", "pull",
             "clean", "update-ref", "notes", "submodule"}


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                             "permissionDecisionReason": reason}}))
    sys.exit(0)


def git(path, *args):
    r = subprocess.run(["git", "-C", path] + list(args), capture_output=True, text=True,
                       env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": os.path.expanduser("~")})
    return r.stdout.strip() if r.returncode == 0 else None


def owner_of(branch):
    if branch == "main":
        return "orch"
    if branch.startswith("track/"):
        return branch[6:].split("--", 1)[0]
    if branch.startswith("core/"):
        return "core"
    if branch.startswith("kb/"):
        return "kb"
    if branch.startswith("proposal/") and branch.count("/") >= 2:
        return branch.split("/")[1]
    return None


class Ctx:
    pass


def context(d):
    if not d or not os.path.isdir(d):
        return None
    root = git(d, "rev-parse", "--show-toplevel")
    if not root:
        return None
    common = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if not common:
        return None
    c = Ctx()
    c.root = os.path.realpath(root)
    c.home = os.path.realpath(os.path.dirname(common))
    if not (os.path.isdir(os.path.join(c.home, "tracks")) and os.path.isdir(os.path.join(c.root, "harness"))):
        return None                                     # not the nrpic repository (tracks/ and harness/)
    c.branch = git(c.root, "rev-parse", "--abbrev-ref", "HEAD") or "?"
    c.owner = owner_of(c.branch)
    c.is_main = c.root == c.home
    c.globs = []
    if c.owner and c.owner != "orch":
        p = os.path.join(c.root, "tracks", c.owner, "OWNERSHIP")
        if os.path.isfile(p):
            c.globs = [l.split("#", 1)[0].strip() for l in open(p) if l.split("#", 1)[0].strip()]
    return c


def glob_match(rel, pattern):
    rx, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            rx, i = rx + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            rx, i = rx + ".*", i + 2
        elif pattern[i] == "*":
            rx, i = rx + "[^/]*", i + 1
        elif pattern[i] == "?":
            rx, i = rx + "[^/]", i + 1
        else:
            rx, i = rx + re.escape(pattern[i]), i + 1
    return re.fullmatch(rx, rel) is not None


def under(p, d):
    return p == d or p.startswith(d.rstrip("/") + "/")


def proposal_hint(c):
    return (f"write a proposal into tracks/{c.owner}/outbox/ (harness/bin/nrpic-ctx post --to orch "
            "--type proposal ...) instead" if c.owner and c.owner != "orch" else "")


def write_verdict(c, path):
    """None if the owner may write `path` (absolute, normalised), else (decision, reason)."""
    p = os.path.realpath(path)
    home_dir = os.path.expanduser("~")
    if under(p, os.path.join(home_dir, ".claude", "plans")):
        return None
    if re.match(re.escape(os.path.join(home_dir, ".claude", "projects")) + r"/[^/]+/memory(/|$)", p):
        return None if c.owner == "orch" else ("deny", "track sessions write no memory (decision 0007); "
                                               f"durable knowledge goes into tracks/{c.owner}/ under git")
    if under(p, "/dev"):
        return None
    if not under(p, c.home):
        tmp = f"scratch/{c.owner}/tmp/" if c.owner else "scratch/<ID>/tmp/"
        return ("deny", f"{p} is outside the repository; temporary files go to {c.home}/{tmp} (never /tmp)")
    me = c.owner or "?"
    if not c.is_main and under(p, c.root):
        rel = os.path.relpath(p, c.root)
        if rel == ".git" or rel.startswith(".git/"):
            return ("deny", "the git directory is changed only through git commands")
        if c.owner in (None, "orch"):
            return ("deny", f"branch {c.branch} of this worktree belongs to no owner")
        if rel.startswith(f"tracks/{c.owner}/") or any(glob_match(rel, g) for g in c.globs):
            return None
        m = re.match(r"tracks/([^/]+)/", rel)
        if m:
            return ("deny", f"{rel} belongs to {m.group(1)}; read it with nrpic-ctx show, never edit it")
        return ("deny", f"{rel} is a shared path (not in tracks/{c.owner}/ or its OWNERSHIP); "
                + proposal_hint(c))
    rel = os.path.relpath(p, c.home)
    top = rel.split("/", 1)[0]
    if top == "scratch":
        parts = rel.split("/")
        if len(parts) >= 2 and parts[1] == (c.owner or ""):
            return None
        if len(parts) >= 2 and parts[1] == "harness" and c.owner == "orch":
            return None
        return ("deny", f"{rel}: another owner's scratch; write only scratch/{me}/")
    if top == "kb-data":
        return None if c.owner == "kb" else ("deny", "kb-data/ is read-only for everyone but kb")
    if top in ("cache", "locks"):
        return ("deny", f"{top}/ is managed by the harness commands")
    if top == "wt":
        return ("deny", f"{rel} is another worktree; write only in your own ({c.root})")
    if top == ".git":
        return ("deny", "the git directory is changed only through git commands")
    if c.owner != "orch":
        return ("deny", f"{rel} is in the main checkout, which only the orchestrator writes; "
                + (proposal_hint(c) or "work in your own worktree"))
    if top == "tracks":
        return ("deny", f"{rel}: tracks/<ID>/ changes only on that track's branch; the orchestrator "
                "merges it, never edits it on main")
    if top == ".claude":
        return ("ask", "the live Claude Code configuration (decision 0008): changing it affects every session")
    return None


# ------------------------------------------------------------------ shell parsing

def strip_heredocs(cmd):
    out, pending = [], []
    for line in cmd.split("\n"):
        if pending:
            delim, dash = pending[0]
            if (line.lstrip("\t") if dash else line) == delim:
                pending.pop(0)
            continue
        out.append(line)
        for m in re.finditer(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2", line):
            pending.append((m.group(3), m.group(1) == "-"))
    return "\n".join(out)


def newlines_to_semicolons(cmd):
    out, q, esc = [], None, False
    for ch in cmd:
        if esc:
            esc = False
            if ch == "\n":
                out.pop()                              # line continuation
                continue
            out.append(ch)
            continue
        if ch == "\\" and q != "'":
            esc = True
            out.append(ch)
            continue
        if q:
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == "\n":
            ch = ";"
        out.append(ch)
    return "".join(out)


OPS = {";", "&&", "||", "|", "&", "|&", "(", ")", ";;"}
REDIR = {">", ">>", "&>", ">|", "&>>"}


def simple_commands(cmd):
    """[(argv, [redirect targets])] for each simple command; raises ValueError when unparsable."""
    text = newlines_to_semicolons(strip_heredocs(cmd))
    lex = shlex.shlex(text, posix=True, punctuation_chars=True)
    lex.wordchars += "$%+,:@^!{}[]="
    toks = list(lex)
    cmds, argv, red = [], [], []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in OPS:
            if argv or red:
                cmds.append((argv, red))
            argv, red = [], []
        elif t in REDIR or t in (">&",):
            tgt = toks[i + 1] if i + 1 < len(toks) else ""
            if argv and argv[-1].isdigit():
                argv.pop()
            if t != ">&" and not tgt.isdigit() and tgt != "-":
                red.append(tgt)
            i += 1
        elif t in ("<", "<<", "<<<", "<&"):
            if argv and argv[-1].isdigit():
                argv.pop()
            i += 1
        else:
            argv.append(t)
        i += 1
    if argv or red:
        cmds.append((argv, red))
    return cmds


def unwrap(argv):
    """Strip wrappers (env VAR=x, timeout 60, nohup, nice -n 5, bash -c ..., nrpic-env exec ... --)."""
    a = list(argv)
    while a:
        b = os.path.basename(a[0])
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", a[0]):
            a = a[1:]
        elif b in WRAPPERS:
            a = a[1:]
            while a and (a[0].startswith("-") or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", a[0])
                         or (b in ("timeout",) and re.fullmatch(r"[0-9.]+[smhd]?", a[0]))
                         or (b == "nice" and a[0].lstrip("-").isdigit())):
                a = a[1:]
                if b == "taskset" and a and not a[0].startswith("-"):
                    a = a[1:]
        elif b == "nrpic-env" and "exec" in a:
            a = a[a.index("--") + 1:] if "--" in a else []
        else:
            break
    return a


def resolve(cwd, p):
    p = os.path.expanduser(p)
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(cwd, p))


def write_targets(argv):
    if not argv:
        return []
    b = os.path.basename(argv[0])
    args = argv[1:]
    pos = [x for x in args if not x.startswith("-")]
    if b in ("cp", "mv", "rsync", "install", "ln", "scp"):
        if "-t" in args and args.index("-t") + 1 < len(args):
            return [args[args.index("-t") + 1]]
        tl = [x for x in args if x.startswith("--target-directory=")]
        if tl:
            return [tl[0].split("=", 1)[1]]
        return pos[-1:] if len(pos) >= 2 else []
    if b in ("rm", "rmdir", "mkdir", "touch", "truncate", "chmod", "chown", "shred", "unlink", "tee"):
        if b in ("chmod", "chown") and pos:
            pos = pos[1:]
        if b == "truncate":
            pos = [x for x in pos if not re.fullmatch(r"[0-9]+[KMGkmg]?", x)]
        return pos
    if b in ("sed", "perl") and any(x == "-i" or x.startswith("-i") or x == "--in-place" for x in args):
        if b == "sed" and not any(x in ("-e", "-f") or x.startswith("--expression") for x in args):
            return pos[1:]
        return pos
    if b == "dd":
        return [x[3:] for x in args if x.startswith("of=")]
    return []


def sim_reason(a):
    b = os.path.basename(a[0])
    if b == "athena" or re.fullmatch(r"athena\..*\.exe", b) or a[0].endswith("/src/athena"):
        return "an AthenaK run"
    if b in SIM_SCRIPTS:
        if b == "submit_chain.sh" and any(x in ("--status", "--stop", "-h", "--help") for x in a[1:]):
            return None
        return f"scripts/{b}"
    if b in SLURM_LAUNCH:
        return f"a Slurm job ({b})"
    return None


def commit_skips_hooks(rest):
    """Does `git commit <rest>` contain -n (short for --no-verify), also inside a cluster like -an?"""
    takes_value = "mFCct"
    j = 0
    while j < len(rest):
        x = rest[j]
        if x in ("--author", "--date", "--fixup", "--squash", "--file", "--message", "--template", "--trailer"):
            j += 2
            continue
        if re.fullmatch(r"-[a-zA-Z]+", x):
            for ch in x[1:]:
                if ch == "n":
                    return True
                if ch in takes_value:
                    break
            if x[-1] in takes_value:
                j += 2
                continue
        j += 1
    return False


def check_git(c, a, cwd):
    """Reasons to deny a git command, or None."""
    i, target = 1, cwd
    while i < len(a) and a[i].startswith("-"):
        if a[i] == "-C" and i + 1 < len(a):
            target = resolve(target, a[i + 1])
            i += 2
        elif a[i] in ("-c", "--git-dir", "--work-tree", "--namespace"):
            i += 2
        else:
            i += 1
    if i >= len(a):
        return None
    sub, rest = a[i], a[i + 1:]
    if "--no-verify" in rest or (sub == "commit" and commit_skips_hooks(rest)):
        return "--no-verify (or commit -n) skips the commit hooks, which is never allowed (brief 13.1)"
    if sub == "worktree" and rest[:1] and rest[0] in ("remove", "prune"):
        return "worktrees are removed only by the orchestrator after asking the user"
    if sub == "branch" and any(x in ("-d", "-D", "--delete") for x in rest):
        return "branches are never deleted (decision 0003; ask the user)"
    if sub == "push":
        if any(x in ("-f", "--force", "--mirror", "-d", "--delete", "--prune") or x.startswith("--force")
               for x in rest):
            return "force pushes and remote deletions are never allowed (decision 0003)"
        refs = [x for x in rest if not x.startswith("-")][1:]
        if any(r.startswith("+") or r.startswith(":") for r in refs):
            return "force pushes and remote deletions are never allowed (decision 0003)"
        if c.owner != "orch":
            if "--tags" in rest or "--follow-tags" in rest or any("refs/tags/" in r or r.startswith("stage/") or
                                                                   r.startswith("core-v") for r in refs):
                return "tags are created and pushed by the orchestrator (decision 0003)"
            for r in refs:
                dst = r.split(":", 1)[-1].replace("refs/heads/", "")
                if dst not in ("HEAD", c.branch):
                    return f"a track pushes only its own branch {c.branch} (not {dst})"
        else:
            for r in refs:
                dst = r.split(":", 1)[-1].replace("refs/heads/", "")
                if dst not in ("HEAD", "main") and not re.match(r"(refs/tags/)?(stage/|core-v|run/)", dst):
                    return f"the orchestrator pushes main and tags, not {dst}"
    if sub in GIT_WRITE and sub not in ("push",):
        if sub in ("branch", "tag", "stash", "worktree", "submodule", "notes") and not rest:
            return None
        if sub == "branch" and all(x.startswith("-") and x in ("-a", "-r", "-v", "-vv", "--list", "--show-current",
                                                              "--contains", "--merged") for x in rest):
            return None
        if sub == "tag" and (rest[:1] in (["-l"], ["--list"]) or (rest and rest[0].startswith("-n"))):
            return None
        if sub == "worktree" and rest[:1] == ["list"]:
            return None
        tc = context(target)
        if tc is not None and tc.root != c.root:
            return (f"git {sub} would write in {tc.root} (branch {tc.branch}); a session writes only in its own "
                    f"worktree {c.root}")
    return None


def check_bash(c, cmd, cwd):
    raw = cmd
    if re.search(r"(^|[\s;&|(])(pkill|killall)(\s|$)", raw) or re.search(r"kill\s+[^;&|]*\$\(\s*pgrep", raw) \
            or re.search(r"kill\s+[^;&|]*`\s*pgrep", raw):
        decide("deny", "pkill, killall and kill $(pgrep ...) match your own shell (CLAUDE.md): kill by numeric "
                       "process id, scancel <jobid>, or scripts/submit_chain.sh --stop")
    try:
        cmds = simple_commands(cmd)
    except ValueError:
        if re.search(r"git\s+push\b[^;&|]*(\s-f\b|--force)", raw):
            decide("deny", "force pushes are never allowed (decision 0003)")
        if "--no-verify" in raw:
            decide("deny", "--no-verify is never allowed (brief 13.1)")
        return
    cur = cwd
    for argv, red in cmds:
        a = unwrap(argv)
        if a:
            b = os.path.basename(a[0])
            if b == "cd":
                cur = resolve(cur, a[1]) if len(a) > 1 and "$" not in a[1] else os.path.expanduser("~")
                continue
            if b in ("bash", "sh", "zsh") and "-c" in a and a.index("-c") + 1 < len(a):
                check_bash(c, a[a.index("-c") + 1], cur)
                continue
            if b in ("bash", "sh") and len(a) > 1 and not a[1].startswith("-"):
                a = a[1:]
                b = os.path.basename(a[0])
            if b in ("curl", "wget"):
                decide("deny", "downloads go through harness/bin/nrpic-fetch-arxiv (arXiv) or the kb session; "
                               "curl and wget are not used (brief 11.5)")
            if b == "nrpic-run" or a[0].endswith("harness/bin/nrpic-run"):
                continue
            why = sim_reason(a)
            if why:
                decide("deny", f"{why} must be registered: use harness/bin/nrpic-run submit --kind scouting|production "
                               "--gate G<k> --purpose ... [--launcher local|batch|chain] (CLAUDE.md rule 4); "
                               "it wraps scripts/gpu_batch.sh and scripts/submit_chain.sh")
            if b == "rm" and any("$" in x or "`" in x for x in a[1:]):
                decide("deny", "never remove files through a path built from a shell variable (CLAUDE.md): "
                               "spell the path out")
            if b == "find" and ("-delete" in a or "rm" in a) and any("$" in x for x in a[1:]):
                decide("deny", "never remove files through a path built from a shell variable (CLAUDE.md)")
            if b == "git":
                why = check_git(c, a, cur)
                if why:
                    decide("deny", why)
        for t in list(red) + write_targets(a):
            if not t or "$" in t or "`" in t or t.startswith("&"):
                continue
            v = write_verdict(c, resolve(cur, t))
            if v:
                decide(v[0], f"write to {t}: {v[1]}")


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    c = context(os.environ.get("CLAUDE_PROJECT_DIR") or cwd) or context(cwd)
    if c is None:
        return 0
    if tool in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        p = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
        if p:
            v = write_verdict(c, resolve(cwd, p))
            if v:
                decide(v[0], v[1])
    elif tool == "Bash":
        check_bash(c, ti.get("command") or "", cwd)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:                    # fail-open, but say so on stderr (shown in the transcript)
        print(f"pre_tool_guard: internal error, allowing: {e!r}", file=sys.stderr)
        sys.exit(0)
