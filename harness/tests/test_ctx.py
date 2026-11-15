#!/usr/bin/python3 -I
"""Self-test of the context-sharing commands (nrpic-ctx, nrpic-wt) in a scratch repository.

    harness/tests/test_ctx.py [--keep] [--transcript FILE]

Builds <main checkout>/scratch/harness/ctx-<UTC>-XXXX/ with a bare origin and a repository of
five owners (orch on main, core on core/nrpic plus a temporary core/rng, kb on kb/main,
A-emd-pbh, B-emd-gw), each in its own linked worktree created by nrpic-wt; the harness under
test is copied into the seed commit, and every session runs its worktree's own copy. Then:

  isolation  every write command changes only the caller's worktree and branch ref;
             every read command (inbox, board, brief, show, audit, digest, owners) changes no
             worktree file, no index, no ref, and creates no merge
  once       every message appears exactly once in the inbox of each recipient, before and after
             copies of outboxes travel through main (gate merge, syncs, core merging core/rng)
  round trip acceptance test 2 of brief 11.7: A -> B, B's brief, B's ack, A's board
  proposal   acceptance test 3: A -> orch interface-change, orch writes DECISIONS, every track syncs
  conflict   a track that edited a shared path: sync aborts and reports, audit names the commit
  audit      foreign paths, a file above 1 MB, a tracked file under scratch/, proposal branch
  cold start acceptance test 7: brief (also as a SessionStart hook) shows the next command
  refusals   -C on write commands, posting to oneself, board --write outside main, dirty sync
  wt         nrpic-wt new/list/check; retire refuses before the push and only prints after it

Exit status 0 when every check passes. The scratch repository is removed on success (after a
check that the path lies under scratch/harness/), kept on failure or with --keep.
"""
import argparse
import datetime as dt
import json
import os
import pwd
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
HARNESS = os.path.dirname(HERE)
OWNERS = ["orch", "core", "kb", "A-emd-pbh", "B-emd-gw"]
BRANCH = {"orch": "main", "core": "core/nrpic", "kb": "kb/main", "A-emd-pbh": "track/A-emd-pbh", "B-emd-gw": "track/B-emd-gw"}


def env():
    pw = pwd.getpwuid(os.getuid())
    return {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": pw.pw_dir, "USER": pw.pw_name, "LOGNAME": pw.pw_name,
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"}


def live_main():
    common = subprocess.run(["git", "-C", HERE, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            capture_output=True, text=True, env=env(), check=True).stdout.strip()
    return os.path.dirname(os.path.realpath(common))


class T:
    def __init__(self, root, transcript):
        self.root = root                       # the scratch directory (repo/ and origin.git/ inside)
        self.repo = os.path.join(root, "repo")
        self.log = transcript
        self.passed = self.failed = 0
        self.section = ""
        self.sections = {}

    def wt(self, oid):
        return self.repo if oid == "orch" else os.path.join(self.repo, "wt", "core-rng" if oid == "core-rng" else oid)

    def rel(self, p):
        return os.path.relpath(p, self.repo) if p.startswith(self.repo) else p

    def head(self, title):
        self.section = title
        self.log.append(f"\n### {title}\n")
        print(f"\n== {title}")

    def sh(self, cmd, cwd, inp=None, show=True, quiet_ok=False):
        p = subprocess.run(cmd, cwd=cwd, input=inp, capture_output=True, text=True, env=env())
        shown = " ".join(c if not c.startswith(self.root) else self.rel(c) for c in cmd)
        shown = re.sub(r"(?:^|(?<=\s))(?:wt/[^/\s]+/)?harness/(bin|tests)/", r"harness/\1/", shown)
        if show:
            out = (p.stdout + (("\n" if p.stdout and p.stderr else "") + p.stderr if p.stderr else "")).rstrip()
            lines = out.splitlines()
            if len(lines) > 30:
                lines = lines[:26] + [f"... ({len(lines) - 26} more lines)"]
            self.log.append(f"```\n[{self.rel(cwd) if cwd != self.repo else '.'}]$ {shown}\n" + "\n".join(lines) + f"\n(exit {p.returncode})\n```")
        return p

    def ctx(self, oid, *args, inp=None, show=True):
        w = self.wt(oid)
        return self.sh([os.path.join(w, "harness", "bin", "nrpic-ctx"), *args], w, inp=inp, show=show)

    def git(self, cwd, *args, check=True):
        p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=env())
        if check and p.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} in {cwd}: {p.stderr}")
        return p.stdout

    def check(self, cond, label):
        if cond:
            self.passed += 1
        else:
            self.failed += 1
        self.sections.setdefault(self.section, [0, 0])[0 if cond else 1] += 1
        self.log.append(f"- {'PASS' if cond else 'FAIL'}: {label}")
        print(f"  {'PASS' if cond else 'FAIL'}: {label}")
        return cond

    # -- state of every worktree and every ref
    def snap(self):
        state = {}
        for oid in ["orch", "core", "core-rng", "kb", "A-emd-pbh", "B-emd-gw"]:
            w = self.wt(oid)
            files = {}
            for r, ds, fs in os.walk(w):
                if r == w:
                    ds[:] = [d for d in ds if d not in ("wt", "scratch", ".git")]   # the shared object store is
                                                                                     # covered by refs and index
                for f in fs:
                    if r == w and f == ".git":
                        continue
                    p = os.path.join(r, f)
                    st = os.lstat(p)
                    files[os.path.relpath(p, w)] = (st.st_size, st.st_mtime_ns)
            idx = self.git(w, "rev-parse", "--git-path", "index").strip()
            idx = idx if os.path.isabs(idx) else os.path.join(w, idx)
            st = os.stat(idx)
            state[oid] = {"files": files, "head": self.git(w, "rev-parse", "HEAD").strip(), "index": (st.st_size, st.st_mtime_ns)}
        state["refs"] = dict(ln.split(" ", 1)[::-1] for ln in self.git(self.repo, "for-each-ref", "--format=%(objectname) %(refname)").splitlines())
        state["merges"] = self.git(self.repo, "rev-list", "--merges", "--all", "--count").strip()
        return state

    def changed(self, a, b):
        """Owners whose worktree changed, and refs that changed."""
        owners = [o for o in a if o not in ("refs", "merges") and a[o] != b[o]]
        refs = sorted(k for k in set(a["refs"]) | set(b["refs"]) if a["refs"].get(k) != b["refs"].get(k))
        return owners, refs


def inbox_paths(out):
    return re.findall(r"^\s+\S+:(tracks/[^/\s]+/outbox/\S+)$", out, re.M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--transcript")
    ap.add_argument("--json", help="write {section: [passed, failed]} to this file")
    args = ap.parse_args()
    base = os.path.join(live_main(), "scratch", "harness")
    os.makedirs(base, exist_ok=True)
    root = tempfile.mkdtemp(prefix="ctx-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-", dir=base)
    log = []
    t = T(root, log)
    ok = False
    try:
        run_all(t)
        ok = t.failed == 0
    except Exception as e:                      # a crash is a failure, reported with the transcript
        import traceback
        t.check(False, f"the test crashed: {type(e).__name__}: {e}")
        log.append("```\n" + traceback.format_exc() + "```")
    summary = f"{t.passed} checks passed, {t.failed} failed"
    print(f"\n{summary}; scratch repository {root}")
    if args.transcript:
        with open(args.transcript, "w") as fh:
            fh.write(f"Self-test `harness/tests/test_ctx.py`, {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}, "
                     f"scratch repository `{os.path.relpath(root, live_main())}/repo`: **{summary}**.\n")
            fh.write("\n".join(log) + "\n")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"passed": t.passed, "failed": t.failed, "root": os.path.relpath(root, live_main()),
                       "sections": t.sections}, fh, indent=1)
    if ok and not args.keep:
        real = os.path.realpath(root)
        if os.path.dirname(real) == os.path.realpath(base) and os.path.basename(real).startswith("ctx-") and not os.path.islink(root):
            shutil.rmtree(real)
            print("scratch repository removed")
    return 0 if ok else 1


def run_all(t):
    repo = t.repo
    # ------------------------------------------------------------------------------ set-up
    t.head("Set-up: a scratch repository with five owners, worktrees by nrpic-wt")
    os.makedirs(repo)
    t.git(t.root, "init", "-q", "--bare", "origin.git")
    t.git(repo, "init", "-q", "-b", "main")
    for k, v in (("user.name", "nrpic-test"), ("user.email", "test@localhost"), ("commit.gpgsign", "false")):
        t.git(repo, "config", k, v)
    t.git(repo, "remote", "add", "origin", os.path.join(t.root, "origin.git"))
    shutil.copytree(HARNESS, os.path.join(repo, "harness"), symlinks=False,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests", "claude"))
    rows = "\n".join(f"| {o} | `{'.' if o == 'orch' else 'wt/' + o}` | `{BRANCH[o]}` | test |" for o in OWNERS)
    open(os.path.join(repo, "CLAUDE.md"), "w").write(
        "# scratch\n\n| Owner id | Worktree | Branch | Subject |\n|---|---|---|---|\n" + rows + "\n")
    open(os.path.join(repo, ".gitignore"), "w").write("wt/\nscratch/\nkb-data/\ncache/\nlocks/\n/runs/\n__pycache__/\n")
    os.makedirs(os.path.join(repo, "coord", "DECISIONS"))
    open(os.path.join(repo, "coord", "CHARTER.md"), "w").write("# Charter (scratch)\n\nline one\n")
    open(os.path.join(repo, "coord", "DECISIONS", "0001-layout.md"), "w").write("# 0001 Layout\n\nStatus: ACCEPTED\n")
    t.git(repo, "add", "-A")
    t.git(repo, "commit", "-q", "-m", "harness and charter")
    for o in OWNERS[1:]:
        d = os.path.join(repo, "tracks", o)
        os.makedirs(os.path.join(d, "outbox"))
        open(os.path.join(d, "outbox", ".gitkeep"), "w").close()
        for name in ("STATUS", "HANDOFF", "JOURNAL"):
            p = t.ctx("orch", "template", name, "--id", o, show=(o == "A-emd-pbh" and name == "HANDOFF"))
            open(os.path.join(d, name + ".md"), "w").write(p.stdout)
        open(os.path.join(d, "OWNERSHIP"), "w").write(
            f"# one glob per line: paths outside tracks/{o}/ that this owner may edit\n" + ("athenak/src/**\n" if o == "core" else ""))
    st = os.path.join(repo, "tracks", "A-emd-pbh", "HANDOFF.md")
    text = open(st).read().replace("`the exact command to run first`", "`python3 tracks/A-emd-pbh/analysis/expball.py --check`")
    with open(st, "w") as fh:
        fh.write(text)
    t.git(repo, "add", "-A")
    t.git(repo, "commit", "-q", "-m", "seed the owners from harness/templates")
    t.git(repo, "push", "-q", "origin", "main")
    t.check(t.git(repo, "rev-parse", "--show-toplevel").strip() == os.path.realpath(repo), "the scratch repository is its own toplevel")
    for o in ["core", "kb", "A-emd-pbh", "B-emd-gw"]:
        p = t.sh([os.path.join(repo, "harness", "bin", "nrpic-wt"), "new", o], repo)
        t.check(p.returncode == 0 and "[wt] PASS" in p.stdout, f"nrpic-wt new {o}: created, [wt] and [build] PASS")
    p = t.sh([os.path.join(repo, "harness", "bin", "nrpic-wt"), "new", "core", "--name", "core-rng", "--branch", "core/rng"], repo)
    t.check(p.returncode == 0 and "temporary worktree of core" in p.stdout, "nrpic-wt new core --name core-rng --branch core/rng")
    p = t.sh([os.path.join(repo, "harness", "bin", "nrpic-wt"), "new", "A-emd-pbh", "--branch", "track/B-emd-gw"], repo)
    t.check(p.returncode != 0, "nrpic-wt new refuses a branch of another owner")
    p = t.sh([os.path.join(t.wt("A-emd-pbh"), "harness", "bin", "nrpic-wt"), "new", "kb", "--name", "kb-x", "--branch", "kb/x"], t.wt("A-emd-pbh"))
    t.check(p.returncode != 0 and "main checkout" in p.stderr, "nrpic-wt new refuses to run outside the main checkout")
    p = t.sh([os.path.join(repo, "harness", "bin", "nrpic-wt"), "list"], repo)
    t.check(p.stdout.count("\n") == 7 and "owners without a worktree" not in p.stdout, "nrpic-wt list: six worktrees, every owner has one")
    p = t.ctx("orch", "owners")
    t.check(all(o in p.stdout for o in OWNERS) and "core/rng" in p.stdout, "nrpic-ctx owners: five owners from CLAUDE.md, core/rng as core's temporary branch")

    # --------------------------------------------------------------------------- messages
    t.head("Messages: each post writes only the poster's worktree and branch")
    posted = []

    def post(oid, to, typ, slug, extra=()):
        a = t.snap()
        p = t.ctx(oid, "post", "--to", to, "--type", typ, "--slug", slug, "--body", f"{typ} from {oid}: {slug}.", *extra)
        b = t.snap()
        m = re.search(r"wrote (\S+)", p.stdout)
        sender = "core" if oid == "core-rng" else oid
        branch = "core/rng" if oid == "core-rng" else BRANCH[oid]
        owners, refs = t.changed(a, b)
        t.check(p.returncode == 0 and m is not None, f"{oid} posts {typ} to {to}: {slug}")
        t.check(owners == [oid] and refs == [f"refs/heads/{branch}"],
                f"only {t.rel(t.wt(oid)) if oid != 'orch' else 'the main checkout'} and refs/heads/{branch} changed (changed: {owners}, {refs})")
        if m:
            posted.append({"path": m.group(1), "from": sender, "to": re.search(r"__to-([A-Za-z0-9-]+)__", m.group(1)).group(1),
                           "slug": slug})
        return p

    post("A-emd-pbh", "B-emd-gw", "request", "deposit-order", ["--reply-by", "2026-11-27", "--refs", "arXiv:2611.12831,run:A-test"])
    post("A-emd-pbh", "all", "info", "hello-all")
    post("core-rng", "A", "info", "rng-draft")
    post("core", "all", "interface-change", "deposit-api")
    post("orch", "all", "info", "wave-start")
    post("kb", "orch", "kb-request", "snapshot")
    p = t.ctx("A-emd-pbh", "show", "A-emd-pbh", "outbox/" + os.path.basename(posted[0]["path"]))
    t.check(p.stdout.startswith("---\nfrom: A-emd-pbh\nto: B-emd-gw\ntype: request\nneeds_reply_by: 2026-11-27\nrefs: [arXiv:2611.12831, run:A-test]\n---\n"),
            "the message file has the front matter of brief 11.3 (from harness/templates/outbox_message.md)")

    def expected(oid):
        return sorted(m["path"] for m in posted if m["from"] != oid and m["to"] in (oid, "all"))

    def once(label):
        for oid in OWNERS:
            p = t.ctx(oid, "inbox", show=(oid == "B-emd-gw"))
            got = inbox_paths(p.stdout)
            t.check(sorted(got) == expected(oid) and len(got) == len(set(got)),
                    f"{label}: inbox of {oid} lists {len(got)} message(s), each exactly once (expected {len(expected(oid))})")

    t.head("Exactly once, before any merge")
    once("no merge yet")

    t.head("Read commands write nothing and merge nothing")
    a = t.snap()
    nread = 0
    for oid in OWNERS + ["core-rng"]:
        for args in (["inbox"], ["inbox", "--all", "--show"], ["board"], ["brief"], ["show", "B"], ["show", "core", "OWNERSHIP"],
                     ["owners"], ["audit"], ["digest"]):
            t.ctx(oid, *args, show=False)
            nread += 1
    p = t.sh([os.path.join(repo, "harness", "bin", "nrpic-ctx"), "brief", "--hook"], repo, inp=json.dumps({"cwd": t.wt("B-emd-gw")}), show=False)
    b = t.snap()
    owners, refs = t.changed(a, b)
    t.check(owners == [] and refs == [] and a["merges"] == b["merges"],
            f"{nread + 1} read commands in six worktrees (inbox, board, brief, show, owners, audit, digest; brief as a hook): "
            "no worktree file, index, HEAD or ref changed; no merge commit")

    t.head("Copies of outboxes travel through main: still exactly once")
    t.sh(["git", "merge", "--no-edit", "-q", "track/A-emd-pbh"], repo)
    p = t.ctx("B-emd-gw", "sync")
    t.check(p.returncode == 0 and "merged" in p.stdout, "B syncs main (which now holds A's outbox and orch's outbox)")
    t.check(os.path.isfile(os.path.join(t.wt("B-emd-gw"), posted[0]["path"])), "B's branch now carries a copy of A's message")
    t.sh(["git", "merge", "--no-edit", "-q", "core/rng"], t.wt("core"))
    t.ctx("kb", "sync", show=False)
    t.ctx("core", "sync", show=False)
    once("after the gate merge, two syncs and core merging core/rng")
    p = t.ctx("B-emd-gw", "inbox")
    t.check(f"track/A-emd-pbh:{posted[0]['path']}" in p.stdout, "B reads A's message from A's branch, not from its own copy")

    # --------------------------------------------------------------------------- round trip
    t.head("Acceptance test 2: context round trip A -> B")
    p = t.ctx("B-emd-gw", "brief")
    t.check("inbox:       4 unacknowledged" in p.stdout and "request from A-emd-pbh: deposit-order" in p.stdout,
            "B's start-up brief shows the request from A")
    t.check(len(p.stdout.splitlines()) <= 40, f"the brief has at most 40 lines ({len(p.stdout.splitlines())})")
    a = t.snap()
    p = t.ctx("B-emd-gw", "ack", os.path.basename(posted[0]["path"]), "--note", "will answer by 2026-11-20")
    b = t.snap()
    owners, refs = t.changed(a, b)
    t.check(p.returncode == 0 and owners == ["B-emd-gw"] and refs == ["refs/heads/track/B-emd-gw"],
            f"B's acknowledgement is committed on track/B-emd-gw only (changed: {owners}, {refs})")
    p = t.ctx("B-emd-gw", "inbox")
    t.check(posted[0]["path"] not in p.stdout and "3 unacknowledged" in p.stdout, "the request has left B's inbox")
    p = t.ctx("B-emd-gw", "inbox", "--all", show=False)
    t.check(posted[0]["path"] in p.stdout and "acked" in p.stdout, "inbox --all still lists it, as acknowledged")
    p = t.ctx("A-emd-pbh", "board")
    row = next((ln for ln in p.stdout.splitlines() if "[deposit-order]" in ln), "")
    t.check("| B-emd-gw | — |" in row, f"A's board shows the acknowledgement by B: {row.strip()[:150]}")
    p = t.ctx("A-emd-pbh", "ack", "1", show=False)
    t.check(p.returncode == 0, "A acknowledges by number")

    # --------------------------------------------------------------------------- proposal
    t.head("Acceptance test 3: proposal round trip A -> orch -> DECISIONS -> every track")
    post("A-emd-pbh", "orch", "interface-change", "pusher-order", ["--reply-by", "2026-11-30"])
    tree = t.git(t.wt("A-emd-pbh"), "rev-parse", "HEAD^{tree}").strip()
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=t.wt("A-emd-pbh"), input="# pusher interface (proposal)\n",
                          capture_output=True, text=True, env=env()).stdout.strip()
    idx_env = dict(env(), GIT_INDEX_FILE=os.path.join(t.root, "proposal.index"))
    subprocess.run(["git", "read-tree", tree], cwd=t.wt("A-emd-pbh"), env=idx_env, check=True)
    subprocess.run(["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},coord/INTERFACES/pusher.md"], cwd=t.wt("A-emd-pbh"), env=idx_env, check=True)
    ptree = subprocess.run(["git", "write-tree"], cwd=t.wt("A-emd-pbh"), env=idx_env, capture_output=True, text=True, check=True).stdout.strip()
    pc = subprocess.run(["git", "commit-tree", ptree, "-p", "HEAD", "-m", "A(proposal): pusher interface"], cwd=t.wt("A-emd-pbh"),
                        env=env(), capture_output=True, text=True, check=True).stdout.strip()
    t.git(t.wt("A-emd-pbh"), "update-ref", "refs/heads/proposal/A-emd-pbh/pusher-order", pc)
    t.log.append("A also opens `proposal/A-emd-pbh/pusher-order` with the code of the proposal (`coord/INTERFACES/pusher.md`).")
    p = t.ctx("orch", "inbox")
    t.check(inbox_paths(p.stdout).count(posted[-1]["path"]) == 1, "the proposal appears once in the orchestrator's inbox")
    adr = t.ctx("orch", "template", "ADR", show=False).stdout.replace("# NNNN Title that states the decision", "# 0002 Pusher order (accepted)")
    open(os.path.join(repo, "coord", "DECISIONS", "0002-pusher-order.md"), "w").write(adr)
    t.sh(["git", "add", "coord/DECISIONS/0002-pusher-order.md"], repo, show=False)
    t.sh(["git", "commit", "-q", "-m", "Decision 0002: pusher order", "--", "coord/DECISIONS/0002-pusher-order.md"], repo)
    p = t.ctx("orch", "ack", os.path.basename(posted[-1]["path"]), "--note", "accepted as decision 0002")
    t.check(p.returncode == 0, "the orchestrator acknowledges the proposal on main")
    for oid in ["A-emd-pbh", "B-emd-gw", "core", "kb"]:
        p = t.ctx(oid, "sync", show=(oid == "A-emd-pbh"))
        f = os.path.join(t.wt(oid), "coord", "DECISIONS", "0002-pusher-order.md")
        t.check(p.returncode == 0 and os.path.isfile(f) and "decision: coord/DECISIONS/0002-pusher-order.md" in p.stdout,
                f"after sync {oid} reads decision 0002 in its own worktree")
    p = t.ctx("A-emd-pbh", "board", show=False)
    row = next((ln for ln in p.stdout.splitlines() if "[pusher-order]" in ln), "")
    t.check("| orch | — |" in row, "A's board shows the proposal acknowledged by orch")

    # --------------------------------------------------------------------------- conflict
    t.head("A boundary crossing: sync refuses to merge, audit names the commit")
    charter_b = os.path.join(t.wt("B-emd-gw"), "coord", "CHARTER.md")
    open(charter_b, "a").write("B edits the charter (forbidden)\n")
    t.sh(["git", "commit", "-q", "-am", "B edits a shared file"], t.wt("B-emd-gw"))
    open(os.path.join(repo, "coord", "CHARTER.md"), "a").write("orch edits the charter\n")
    t.sh(["git", "commit", "-q", "-m", "orch edits the charter", "--", "coord/CHARTER.md"], repo)
    head_b = t.git(t.wt("B-emd-gw"), "rev-parse", "HEAD").strip()
    p = t.ctx("B-emd-gw", "sync")
    merging = t.git(t.wt("B-emd-gw"), "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).strip()
    t.check(p.returncode == 1 and "coord/CHARTER.md" in p.stderr, "sync fails and names coord/CHARTER.md")
    t.check(not merging and t.git(t.wt("B-emd-gw"), "rev-parse", "HEAD").strip() == head_b and
            t.git(t.wt("B-emd-gw"), "status", "--porcelain").strip() == "", "the merge was aborted: B's branch and tree are as before")

    t.head("Audit: foreign paths, large file, tracked file under an ignored root, read-only")
    big = os.path.join(t.wt("A-emd-pbh"), "tracks", "A-emd-pbh", "analysis", "big.bin")
    os.makedirs(os.path.dirname(big), exist_ok=True)
    open(big, "wb").write(os.urandom(1536 * 1024))
    os.makedirs(os.path.join(t.wt("A-emd-pbh"), "scratch", "A-emd-pbh"), exist_ok=True)
    open(os.path.join(t.wt("A-emd-pbh"), "scratch", "A-emd-pbh", "leak.txt"), "w").write("output\n")
    t.sh(["git", "add", "tracks/A-emd-pbh/analysis/big.bin"], t.wt("A-emd-pbh"), show=False)
    t.sh(["git", "add", "-f", "scratch/A-emd-pbh/leak.txt"], t.wt("A-emd-pbh"), show=False)
    t.sh(["git", "commit", "-q", "-m", "A commits a 1.5 MB file and force-adds scratch output"], t.wt("A-emd-pbh"))
    a = t.snap()
    p = t.ctx("orch", "audit")
    b = t.snap()
    out = p.stdout
    s1 = out.split("## 1.")[1].split("## 2.")[0]
    s2 = out.split("## 2.")[1].split("## 3.")[0]
    s3 = out.split("## 3.")[1].split("## Notes")[0]
    t.check(p.returncode == 1, "audit exits 1 when it has findings")
    t.check("track/B-emd-gw" in s1 and "coord/CHARTER.md" in s1 and "B edits a shared file" in s1,
            "section 1 names B's commit touching coord/CHARTER.md")
    t.check("proposal/A-emd-pbh/pusher-order" in s1 and "proposal branch" in s1, "section 1 lists the proposal branch as a proposal")
    t.check("tracks/A-emd-pbh/analysis/big.bin` 1.50 MB" in s2, "section 2 lists the 1.5 MB file")
    t.check("scratch/A-emd-pbh/leak.txt" in s3 and "root `scratch/`" in s3, "section 3 lists the tracked file under scratch/")
    a_block = s1.split("**`track/A-emd-pbh`**")[1].split("**`")[0] if "**`track/A-emd-pbh`**" in s1 else ""
    t.check("scratch/A-emd-pbh/leak.txt" in a_block and "tracks/A-emd-pbh/" not in a_block,
            "section 1 names A's commit of scratch/A-emd-pbh/leak.txt, and none of A's own paths")
    t.check("core/rng" not in s1 and "core/nrpic" not in s1 and "kb/main" not in s1, "no false positives: core (with its merge of core/rng) and kb pass")
    m = re.search(r"Findings: (\d+) \(section 1: (\d+), section 2: (\d+), section 3: (\d+)\)", out)
    t.check(m is not None and m.groups() == ("4", "2", "1", "1"), f"findings counted: {m.group(0) if m else 'no summary line'}")
    owners, refs = t.changed(a, b)
    t.check(owners == [] and refs == [] and a["merges"] == b["merges"], "audit changed nothing")
    p = t.ctx("orch", "audit", "--branch", "core/nrpic", show=False)
    t.check(p.returncode == 0, "audit --branch core/nrpic: no findings on core")

    # --------------------------------------------------------------------------- cold start
    t.head("Acceptance test 7: cold start from HANDOFF.md and the brief")
    p = t.ctx("A-emd-pbh", "brief")
    t.check("handoff:     Run next: `python3 tracks/A-emd-pbh/analysis/expball.py --check`" in p.stdout and "gate:" in p.stdout,
            "A's brief carries the gate and the exact next command of HANDOFF.md")
    p = t.sh([os.path.join(repo, "harness", "bin", "nrpic-ctx"), "brief", "--hook"], t.root, inp=json.dumps({"cwd": t.wt("A-emd-pbh")}))
    t.check("you are A-emd-pbh" in p.stdout and p.returncode == 0, "as a SessionStart hook (cwd from the JSON on stdin) it briefs A")
    p = t.sh([os.path.join(repo, "harness", "bin", "nrpic-ctx"), "brief", "--hook"], t.root, inp="{}")
    t.check(p.returncode == 0 and "unavailable" in p.stdout, "a hook call outside any worktree exits 0 with a one-line notice")

    # --------------------------------------------------------------------------- refusals
    t.head("Refusals")
    a = t.snap()
    p = t.sh([os.path.join(t.wt("A-emd-pbh"), "harness", "bin", "nrpic-ctx"), "-C", t.wt("B-emd-gw"), "post", "--to", "core",
              "--type", "info", "--slug", "x", "--body", "x"], t.wt("A-emd-pbh"))
    t.check(p.returncode == 2 and "worktree you are in" in p.stderr, "post with -C naming another worktree is refused")
    p = t.ctx("A-emd-pbh", "post", "--to", "A", "--type", "info", "--slug", "self", "--body", "x")
    t.check(p.returncode == 2, "a message to oneself is refused")
    p = t.ctx("A-emd-pbh", "post", "--to", "core", "--type", "gossip", "--slug", "x", "--body", "x")
    t.check(p.returncode == 2, "an unknown message type is refused")
    p = t.ctx("A-emd-pbh", "board", "--write")
    t.check(p.returncode == 2, "board --write outside the main checkout is refused")
    b = t.snap()
    owners, refs = t.changed(a, b)
    t.check(owners == [] and refs == [], "the refused commands wrote nothing")
    open(os.path.join(t.wt("kb"), "tracks", "kb", "STATUS.md"), "a").write("dirty\n")
    p = t.ctx("kb", "sync")
    t.check(p.returncode == 2 and "uncommitted" in p.stderr, "sync refuses a worktree with uncommitted tracked changes")
    t.sh(["git", "checkout", "-q", "--", "tracks/kb/STATUS.md"], t.wt("kb"), show=False)

    # --------------------------------------------------------------------------- retire
    t.head("nrpic-wt retire: checks, never removes")
    wtcmd = os.path.join(repo, "harness", "bin", "nrpic-wt")
    p = t.sh([wtcmd, "retire", "A-emd-pbh"], repo)
    t.check(p.returncode == 1 and "may NOT be retired" in p.stdout, "retire refuses while A's tip is neither pushed, tagged nor on main")
    t.sh(["git", "push", "-q", "origin", "track/A-emd-pbh"], t.wt("A-emd-pbh"))
    t.sh(["git", "fetch", "-q", "origin"], repo, show=False)
    p = t.sh([wtcmd, "retire", "A-emd-pbh"], repo)
    t.check(p.returncode == 0 and "git worktree remove wt/A-emd-pbh" in p.stdout and os.path.isdir(t.wt("A-emd-pbh")),
            "after the push it prints the command for a person; the worktree is still there")
    p = t.sh([wtcmd, "check", "A-emd-pbh"], repo)
    t.check(p.returncode == 0, "nrpic-wt check A-emd-pbh passes")

    t.head("The orchestrator's generated files")
    p = t.ctx("orch", "board", "--write")
    bd = os.path.join(repo, "coord", "BOARD.md")
    t.check(p.returncode == 0 and os.path.isfile(bd) and all(f"| {o} |" in open(bd).read() for o in OWNERS),
            "board --write in the main checkout writes coord/BOARD.md with every owner")
    p = t.ctx("orch", "digest", "--write", "--week", "2026-W46")
    dg = os.path.join(repo, "coord", "digests", "2026-W46.md")
    t.check(p.returncode == 0 and os.path.isfile(dg) and "## Cross-owner requests" in open(dg).read() and "## Audit" in open(dg).read(),
            "digest --write writes coord/digests/2026-W46.md with the requests and the audit")
    p = t.ctx("kb", "ack", os.path.basename(posted[0]["path"]))
    t.check(p.returncode == 2, "kb cannot acknowledge a message addressed to B")

    t.head("nrpic-doctor rows of this harness, inside the scratch repository")
    p = t.sh([os.path.join(t.wt("A-emd-pbh"), "harness", "bin", "nrpic-doctor"), "--rows", "wt,build,ctx"], t.wt("A-emd-pbh"))
    t.check(p.returncode == 0 and p.stdout.count("PASS") >= 3, "nrpic-doctor --rows wt,build,ctx passes in wt/A-emd-pbh")
    t.ctx("orch", "board")
    t.ctx("orch", "digest", show=False)


if __name__ == "__main__":
    sys.exit(main())
