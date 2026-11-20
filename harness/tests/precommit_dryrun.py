#!/usr/bin/python3 -I
"""Dry run of the pre-commit hook over the history (decision 0017 item 4). Read-only on every branch.

    python3 -I harness/tests/precommit_dryrun.py [--repo DIR] [--hook PATH] [--since REV] [--branch B]...
                 [--ownership at-time|tip] [--ownership-add OWNER=GLOB]... [--no-replay] [--clone NAME]
                 [--json FILE] [--quiet]

Every commit reachable from a local owner branch (main, core/*, kb/*, track/*) and not from the
parent of --since (default 52c44eb, the start of the program; the commit itself is included) is
passed through the checks of the hook, `evaluate(view)` of harness/hooks/pre-commit (or --hook PATH),
with a view of that commit instead of the index: the files it changed against its first parent, their
blobs and sizes, the added lines, the branch it was made on, and OWNERSHIP as the hook would have
read it (`--ownership at-time`: main's copy at the commit's time, the default; `tip`: main's copy
now; `--ownership-add core='python/tests/**'` adds a proposed line). Nothing is committed and no live
branch, index or worktree is written. --repo (default: the main checkout of this file) lets the
self-test run it on a scratch repository.

The branch of a commit: the first branch in the order main, kb/main, core/nrpic, track/<ID>, then the
temporary branches (a temporary branch only for commits made after it was created, by its reflog), on
whose first-parent chain the commit lies; a commit on no such chain came in through a merge, and its
branch is read from that merge's message ("Merge branch 'X'").

Merges: `git merge` does not run pre-commit; the hook runs only when a conflicted merge (or one made
with --no-commit) is finished with `git commit`. Each merge is replayed in a scratch clone
(<repo>/scratch/harness/hook-dryrun/clone, `git clone --shared`, reused between runs): if the
automatic merge gives the recorded tree, the hook was not invoked ("clean"); otherwise it was
("resolved") and the view carries MERGE_HEAD. Clean merges are evaluated as well and reported apart,
as what the hook would say had the merge been finished by hand.

Prints one line per refused commit and a summary; --json writes every refusal with its commit,
branch, owner, check, path and reason. Exit 0 (the result is the report, not a pass or fail).
"""
import argparse
import importlib.machinery
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import nrpic_harness as H  # noqa: E402

PRIORITY = ["main", "kb/main", "core/nrpic"] + [f"track/{t}" for t in H.TRACK_IDS]
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def home_of(path):
    common = subprocess.run(["git", "-C", path, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, env=H.boot_env(), check=True).stdout.strip()
    return os.path.dirname(common)


def load_hook(path):
    loader = importlib.machinery.SourceFileLoader("nrpic_precommit_hook", path)
    spec = importlib.util.spec_from_loader("nrpic_precommit_hook", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class Git:
    def __init__(self, repo):
        self.repo = repo

    def run(self, *args, check=True, binary=False, input_bytes=None):
        r = subprocess.run(["git", "-C", self.repo, "-c", "core.quotePath=false"] + list(args), capture_output=True,
                           env=H.boot_env(), input=input_bytes)
        if check and r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)}: {r.stderr.decode(errors='replace')}")
        return r.stdout if binary else r.stdout.decode(errors="replace")

    def lines(self, *args):
        return [l for l in self.run(*args).splitlines() if l]


def show_ownership(g, hook, revs, owner, extra):
    globs = None
    for rev in revs:
        if not rev:
            continue
        r = subprocess.run(["git", "-C", g.repo, "show", f"{rev}:tracks/{owner}/OWNERSHIP"], capture_output=True,
                           env=H.boot_env())
        if r.returncode == 0:
            globs = hook.parse_ownership(r.stdout.decode(errors="replace"))
            break
    return (globs or []) + list(extra.get(owner, []))


def make_view(hook, g, commit, parents, branch, merging, main_rev, extra):
    """A view of a past commit for the hook given: hook.View (the corrected interface) or the first one."""
    base = parents[0] if parents else EMPTY_TREE
    raw = g.run("diff-tree", "-r", "-z", "--no-renames", "--raw", "--no-abbrev", "--no-commit-id", base, commit)

    if hasattr(hook, "View"):
        class CommitView(hook.View):
            def __init__(self):
                self.changes = hook.parse_raw(raw)
                self.head = base
                self.merge_heads = parents[1:] if merging else []

            def run(self, *args, check=False, binary=False, input_bytes=None):
                return g.run(*args, check=check, binary=binary, input_bytes=input_bytes)

            def context(self):
                self.branch, self.merging = branch, merging

            def diff(self):
                return g.run("diff", *hook.DIFF_OPTS, base, commit)

            def ownership(self, owner):
                return show_ownership(g, hook, (main_rev, parents[0] if parents else None), owner, extra)
        return CommitView()

    class LegacyCommitView:                     # the hook before the corrections: evaluate(view) on paths
        def __init__(self):
            parts = [p for p in raw.split("\0") if p != ""]
            self.changes, self._sha = [], {}
            for k in range(0, len(parts) - 1, 2):
                meta, path = parts[k].lstrip(":").split(), parts[k + 1]
                self.changes.append((meta[4][0], path))
                self._sha[path] = (meta[1], meta[3])
            self._sizes = None

        def context(self):
            self.branch, self.merging = branch, merging

        def size(self, path):
            if self._sizes is None:
                want = [(p, s[1]) for p, s in self._sha.items() if s[0] not in ("160000", "000000")]
                out = g.run("cat-file", "--batch-check", input_bytes=("\n".join(s for _, s in want) + "\n").encode())
                self._sizes = {}
                for (p, _), line in zip(want, out.splitlines()):
                    f = line.split()
                    if len(f) == 3 and f[2].isdigit():
                        self._sizes[p] = int(f[2])
            return self._sizes.get(path)

        def blob(self, path):
            return g.run("show", f"{commit}:{path}", check=False, binary=True)

        def diff(self):
            return g.run("diff", "-U0", "--no-color", "--no-ext-diff", "--text", base, commit)

        def ownership(self, owner):
            return show_ownership(g, hook, (main_rev, parents[0] if parents else None), owner, extra)
    return LegacyCommitView()


def branches(g, wanted):
    heads = g.lines("for-each-ref", "--format=%(refname:short)", "refs/heads/")
    owned = [b for b in heads if b == "main" or b.startswith(("core/", "kb/", "track/"))]
    if wanted:
        owned = [b for b in owned if b in wanted]
    return [b for b in PRIORITY if b in owned] + sorted(b for b in owned if b not in PRIORITY)


def merge_branch_name(msg):
    m = re.match(r"Merge (?:remote-tracking )?branch(?:es)? '([^']+)'", msg)
    if m:
        name = m.group(1)
        return name[7:] if name.startswith("origin/") else name
    return None


def metadata(g, brs, stop):
    """commit -> (parents, committer time, author, subject), for every commit of the range."""
    meta = {}
    raw = g.run("log", "--topo-order", "--format=%H%x1f%P%x1f%ct%x1f%an%x1f%s%x1e", *brs, *stop)
    for rec in raw.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        h, ps, ct, an, subj = rec.split("\x1f", 4)
        meta[h] = (ps.split(), int(ct), an, subj)
    return meta


def created(g, b):
    """Time the branch was created, from its reflog (None if there is no reflog)."""
    t = g.lines("log", "-g", "--format=%ct", f"refs/heads/{b}")
    return int(t[-1]) if t else None


def attribute(g, brs, stop, meta):
    """commit -> branch it was made on."""
    where = {}
    for b in brs:
        since = None if b in PRIORITY else created(g, b)
        for c in g.lines("rev-list", "--first-parent", b, *stop):
            if c in where or (since is not None and c in meta and meta[c][1] < since):
                continue
            where[c] = b
    for b in brs:                                # commits older than every reflog: first branch that has them
        for c in g.lines("rev-list", "--first-parent", b, *stop):
            where.setdefault(c, b)
    for m, (ps, _, _, subj) in meta.items():
        if len(ps) < 2:
            continue
        name = merge_branch_name(subj)
        for p in ps[1:]:
            for c in g.lines("rev-list", "--first-parent", p, "--not", ps[0], *stop[1:]):
                if c not in where:
                    where[c] = name or f"merged-into:{where.get(m, '?')}"
    return where


def main_at(g, stop):
    """List of (committer time, sha) of main's first-parent chain, oldest first."""
    rows = []
    for line in g.lines("log", "--first-parent", "--format=%ct %H", "main", *stop):
        t, h = line.split()
        rows.append((int(t), h))
    rows.reverse()
    return rows


def main_rev_at(rows, t):
    best = None
    for ct, h in rows:
        if ct <= t:
            best = h
        else:
            break
    return best or (rows[0][1] if rows else "main")


def clone_for_merges(repo, name="clone"):
    root = os.path.join(repo, "scratch", "harness", "hook-dryrun")
    clone = os.path.join(root, name)
    env = H.boot_env()
    if not os.path.isdir(os.path.join(clone, ".git")):
        os.makedirs(root, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", repo, clone], env=env, check=True,
                       capture_output=True)
    else:
        subprocess.run(["git", "-C", clone, "fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*"],
                       env=env, check=True, capture_output=True)
    for k, v in (("user.name", "hook-dryrun"), ("user.email", "hook-dryrun@localhost"), ("commit.gpgsign", "false"),
                 ("core.hooksPath", "/dev/null")):
        subprocess.run(["git", "-C", clone, "config", k, v], env=env, check=True)
    return clone


def replay_merge(clone, commit, parents):
    """'clean' if `git merge` of parents[1:] into parents[0] gives the recorded tree, else 'resolved'."""
    env = H.boot_env()
    gc = ["git", "-C", clone]
    subprocess.run(gc + ["reset", "-q", "--hard"], env=env, capture_output=True)
    subprocess.run(gc + ["checkout", "-q", "-f", "--detach", parents[0]], env=env, check=True, capture_output=True)
    subprocess.run(gc + ["merge", "--no-commit", "--no-ff", "-q"] + parents[1:], env=env, capture_output=True)
    unmerged = subprocess.run(gc + ["ls-files", "-u"], env=env, capture_output=True, text=True).stdout.strip()
    state = "resolved"
    if not unmerged:
        w = subprocess.run(gc + ["write-tree"], env=env, capture_output=True, text=True)
        want = subprocess.run(gc + ["rev-parse", f"{commit}^{{tree}}"], env=env, capture_output=True,
                              text=True).stdout.strip()
        if w.returncode == 0 and w.stdout.strip() == want:
            state = "clean"
    subprocess.run(gc + ["merge", "--abort"], env=env, capture_output=True)
    subprocess.run(gc + ["reset", "-q", "--hard"], env=env, capture_output=True)
    return state


def run_dryrun(repo, hook_path, since="52c44eb", wanted=None, ownership="at-time", replay=True, extra=None,
               log=print, clone_name="clone"):
    hook = load_hook(hook_path)
    extra = extra or {}
    g = Git(repo)
    r = subprocess.run(["git", "-C", repo, "rev-parse", "-q", "--verify", f"{since}^"], capture_output=True,
                       text=True, env=H.boot_env())
    stop = ["--not", r.stdout.strip()] if r.returncode == 0 else []
    brs = branches(g, wanted)
    meta = metadata(g, brs, stop)
    allc = g.lines("rev-list", "--topo-order", "--reverse", *brs, *stop)
    where = attribute(g, brs, stop, meta)
    rows = main_at(g, stop)
    tip = g.run("rev-parse", "main").strip()
    clone = clone_for_merges(repo, clone_name) if replay else None
    out = {"hook": hook_path, "since": since, "branches": brs, "ownership": ownership, "ownership_add": extra,
           "commits": len(allc), "refusals": [], "merges": {}, "by_branch": {}, "notes": 0}
    t0 = time.time()
    for i, c in enumerate(allc):
        parents, ct, author, subj = meta[c]
        br = where.get(c, "unknown")
        merging = len(parents) > 1
        mstate = None
        if merging:
            mstate = replay_merge(clone, c, parents) if clone else "unknown"
            out["merges"][c] = {"branch": br, "state": mstate, "subject": subj}
        mrev = main_rev_at(rows, ct) if ownership == "at-time" else tip
        view = make_view(hook, g, c, parents, br, merging, mrev, extra)
        problems, notes = hook.evaluate(view)
        out["notes"] += len(notes)
        out["by_branch"][br] = out["by_branch"].get(br, 0) + 1
        if problems:
            out["refusals"].append({"commit": c, "short": c[:8], "branch": br, "owner": hook.owner_of(br) or "orch",
                                    "time": ct, "author": author, "subject": subj, "merge": mstate,
                                    "problems": [{"check": p[0], "path": p[1], "text": p[2]} for p in problems]})
        if log and (i + 1) % 500 == 0:
            log(f"  ... {i + 1}/{len(allc)} commits, {time.time() - t0:.0f} s")
    out["seconds"] = round(time.time() - t0, 1)
    return out


def summary(out):
    lines = []
    invoked = [r for r in out["refusals"] if r["merge"] != "clean"]
    clean = [r for r in out["refusals"] if r["merge"] == "clean"]
    ms = out["merges"]
    add = "; ".join(f"{o}+{','.join(gs)}" for o, gs in out.get("ownership_add", {}).items())
    lines.append(f"hook {out['hook']}; ownership {out['ownership']}{' (' + add + ')' if add else ''}; "
                 f"{out['commits']} commits since {out['since']} on {len(out['branches'])} branches; merges {len(ms)} "
                 f"(clean {sum(1 for m in ms.values() if m['state'] == 'clean')}, "
                 f"resolved {sum(1 for m in ms.values() if m['state'] == 'resolved')}); {out['seconds']} s")
    lines.append(f"refused where the hook runs: {len(invoked)} commits; refused clean merges (hook not run by "
                 f"`git merge`): {len(clean)}")
    for r in invoked + clean:
        checks = sorted({p["check"] for p in r["problems"]})
        tag = " [clean merge, hook not run]" if r["merge"] == "clean" else (" [resolved merge]" if r["merge"] else "")
        lines.append(f"  {r['short']} {r['branch']:<22} {','.join(checks):<16} {len(r['problems']):>4} path(s)  "
                     f"{r['subject'][:70]}{tag}")
        for p in r["problems"][:3]:
            lines.append(f"      {p['check']}: {p['path']}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", help="repository (default: the main checkout this file belongs to)")
    ap.add_argument("--hook", help="hook file (default: <repo>/harness/hooks/pre-commit)")
    ap.add_argument("--since", default="52c44eb")
    ap.add_argument("--branch", action="append", default=[])
    ap.add_argument("--ownership", choices=("at-time", "tip"), default="at-time")
    ap.add_argument("--ownership-add", action="append", default=[], metavar="OWNER=GLOB")
    ap.add_argument("--no-replay", action="store_true", help="do not replay merges (their state is 'unknown')")
    ap.add_argument("--clone", default="clone", help="name of the scratch clone (runs in parallel need their own)")
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    repo = home_of(a.repo or HERE)
    hook = os.path.realpath(a.hook) if a.hook else os.path.join(repo, "harness", "hooks", "pre-commit")
    extra = {}
    for kv in a.ownership_add:
        o, _, glob = kv.partition("=")
        extra.setdefault(o, []).append(glob)
    out = run_dryrun(repo, hook, a.since, a.branch, a.ownership, not a.no_replay, extra,
                     log=None if a.quiet else print, clone_name=os.path.basename(a.clone))
    if a.json:
        with open(a.json, "w") as f:
            json.dump(out, f, indent=1)
    print(summary(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
