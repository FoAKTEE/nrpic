#!/usr/bin/python3 -I
"""Watch of the installed pre-commit hook (wave 3, decision 0019 item 5). Read-only.

    python3 -I harness/tests/hook_watch.py [--after ISO|EPOCH] [--json FILE] [--repo DIR]

--after defaults to the installation, 2026-11-20T21:57Z. Three looks, none of which writes anything:

1. Commits on the owner branches (main, core/*, kb/*, track/*) committed after --after, passed through
   the checks of the hook as it stands (`evaluate(view)` of harness/hooks/pre-commit, main's OWNERSHIP
   of now; merges evaluated for what they add, as the hook does). A refused commit is either a bypass
   (`git commit --no-verify`, allowed once by CLAUDE.md's escape rule) or a gap of the hook (a merge
   finished by hand, cherry-pick, rebase); every one is listed.
2. Lines added after --after on each owner's branch under its own tracks/<owner>/ that mention the hook:
   its refusal text "commit rejected (harness/hooks/pre-commit", "pre-commit", "no-verify" (journals,
   outbox requests, notes).
3. The same words in files of the worktrees (wt/*/tracks/<owner>/) modified after --after and not yet
   committed: a session that was refused may not have committed its journal.

Exit 0; the report is the result. Used every hour during wave 3 by the harness helper; when a class of
legitimate commit is refused, the hook is corrected with a test in harness/tests/test_precommit.py.
"""
import argparse
import calendar
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import nrpic_harness as H  # noqa: E402
import precommit_dryrun as D  # noqa: E402

INSTALLED = "2026-11-20T21:57:00Z"
WORDS = re.compile(r"commit rejected \(harness/hooks/pre-commit|pre-commit|no-verify|--no-verify", re.I)
TEXT_EXT = (".md", ".txt", ".tsv", ".json", ".log", ".tex", ".py", ".sh", "")


def epoch(s):
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return float(s)
    return calendar.timegm(time.strptime(s.replace("Z", ""), "%Y-%m-%dT%H:%M:%S"))


def refused_commits(repo, after):
    g = D.Git(repo)
    hook = D.load_hook(os.path.join(repo, "harness", "hooks", "pre-commit"))
    brs = D.branches(g, [])
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(after))
    meta = D.metadata(g, brs, [f"--since={stamp}"])
    commits = [c for c in g.lines("rev-list", "--topo-order", "--reverse", f"--since={stamp}", *brs)
               if c in meta and meta[c][1] >= after]
    if not commits:
        return {"commits": 0, "refused": [], "merges": 0}
    where = {}
    for b in brs:                                  # first-parent attribution, as the dry run does
        for c in g.lines("rev-list", "--first-parent", f"--since={stamp}", b):
            where.setdefault(c, b)
    tip = g.run("rev-parse", "main").strip()
    out = {"commits": len(commits), "refused": [], "merges": 0}
    for c in commits:
        if c not in meta:
            continue
        parents, ct, author, subj = meta[c]
        br = where.get(c, "unknown")
        merging = len(parents) > 1
        out["merges"] += int(merging)
        view = D.make_view(hook, g, c, parents, br, merging, tip, {})
        problems, notes = hook.evaluate(view)
        if problems:
            out["refused"].append({"commit": c[:10], "branch": br, "time": time.strftime("%H:%M:%SZ", time.gmtime(ct)),
                                   "merge": merging, "subject": subj[:100],
                                   "problems": [f"{p[0]}: {p[2][:160]}" for p in problems[:5]]})
    return out


def mentions_on_branches(repo, after):
    g = D.Git(repo)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(after))
    hits = []
    for b in D.branches(g, []):
        owner = H.owner_of(b)
        if not owner:
            continue
        own = f"tracks/{owner}/"
        log = g.run("log", f"--since={stamp}", "--format=@@COMMIT %H %ct", "-p", "-U0", "--no-color", "--no-merges",
                    "-G", "pre-commit|no-verify", b, "--", own, check=False)
        cur, path, ct = None, None, 0
        for line in log.splitlines():
            if line.startswith("@@COMMIT "):
                _, cur, ct = line.split()
                ct = int(ct)
                continue
            if line.startswith("+++ "):
                path = line[6:] if line.startswith("+++ b/") else None
                continue
            if line.startswith("+") and path and ct >= after and WORDS.search(line):
                hits.append({"branch": b, "commit": cur[:10], "path": path, "line": line[1:].strip()[:220]})
    seen, uniq = set(), []
    for h in hits:                                  # the same line on a temporary branch and its parent
        k = (h["path"], h["line"])
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    return uniq


def mentions_in_worktrees(repo, after):
    hits = []
    for w in H.run(["git", "-C", repo, "worktree", "list", "--porcelain"]).stdout.split("\n\n"):
        m = re.search(r"^worktree (.+)$", w, re.M)
        b = re.search(r"^branch refs/heads/(.+)$", w, re.M)
        if not m or not b:
            continue
        path, owner = m.group(1), H.owner_of(b.group(1))
        if not owner or owner == "orch":
            continue
        st = H.run(["git", "-C", path, "status", "--porcelain", "--untracked-files=all", "--", f"tracks/{owner}"],
                   check=False).stdout.splitlines()
        for s in st:
            rel = s[3:].split(" -> ")[-1].strip('"')
            full = os.path.join(path, rel)
            if not os.path.isfile(full) or os.path.getmtime(full) < after or os.path.getsize(full) > 4 << 20:
                continue
            if os.path.splitext(full)[1] not in TEXT_EXT:
                continue
            try:
                text = open(full, errors="replace").read()
            except OSError:
                continue
            head = H.run(["git", "-C", path, "show", f"HEAD:{rel}"], check=False)
            old = set(head.stdout.splitlines()) if head.returncode == 0 else set()
            for ln in text.splitlines():
                if ln not in old and WORDS.search(ln):
                    hits.append({"worktree": os.path.relpath(path, repo), "path": rel, "line": ln.strip()[:220]})
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--after", default=INSTALLED)
    ap.add_argument("--json")
    ap.add_argument("--repo")
    a = ap.parse_args()
    repo = D.home_of(a.repo or HERE)
    after = epoch(a.after)
    t0 = time.time()
    rc = refused_commits(repo, after)
    mb = mentions_on_branches(repo, after)
    mw = mentions_in_worktrees(repo, after)
    print(f"hook watch {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}: commits since "
          f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(after))} on the owner branches: {rc['commits']} "
          f"({rc.get('merges', 0)} merges); the hook refuses {len(rc['refused'])} of them")
    for r in rc["refused"]:
        print(f"  REFUSED {r['commit']} {r['branch']} {r['time']}{' merge' if r['merge'] else ''}: {r['subject']}")
        for p in r["problems"]:
            print(f"      {p}")
    print(f"mentions of the hook added on the branches: {len(mb)}")
    for h in mb:
        print(f"  {h['branch']} {h['commit']} {h['path']}: {h['line']}")
    print(f"mentions in uncommitted worktree files: {len(mw)}")
    for h in mw:
        print(f"  {h['worktree']} {h['path']}: {h['line']}")
    print(f"({time.time() - t0:.0f} s, read-only)")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"after": after, "refused": rc, "branches": mb, "worktrees": mw}, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
