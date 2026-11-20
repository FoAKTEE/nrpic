#!/usr/bin/python3 -I
"""Self-test of the dry run of the pre-commit hook over a history (harness/tests/precommit_dryrun.py).

    python3 -I harness/tests/test_precommit_dryrun.py

Builds a scratch repository with a known history (no hook installed while it is made) and checks
that the dry run finds what the hook would have refused and nothing else: a foreign path on a track
branch, a real-shaped secret on main, a docs/ commit of core refused with main's OWNERSHIP of its
time and accepted with today's, a clean merge (hook not run) and a conflicted one (hook run with
MERGE_HEAD), the branch of a commit that only a merge message names, and that the repository under
test is not written (refs, index, worktrees). The live repository is not touched.
"""
import base64
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402
import precommit_dryrun as D  # noqa: E402

RND = random.Random(3)


def main():
    fx = F.make_repo("test-precommit-dryrun")
    repo, A, core = fx["repo"], fx["wt"]["A-emd-pbh"], fx["wt"]["core"]
    c = F.Checks(f"dry run of the pre-commit hook (scratch repo {repo})")
    hook = os.path.join(repo, "harness", "hooks", "pre-commit")
    root = F.sh(["git", "-C", repo, "rev-list", "--max-parents=0", "main"]).stdout.strip()

    def put(wt, rel, data, msg):
        p = os.path.join(wt, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(data)
        F.sh(["git", "-C", wt, "add", "-f", "--", rel])
        F.sh(["git", "-C", wt, "commit", "-q", "-m", msg])
        return F.sh(["git", "-C", wt, "rev-parse", "HEAD"]).stdout.strip()

    secret = "aws_secret_" + "access_key = " + base64.b64encode(bytes(RND.getrandbits(8) for _ in range(30))).decode()
    own = put(A, "tracks/A-emd-pbh/notes/own.md", "own note\n", "A: own note")
    foreign = put(A, "coord/x.md", "A writes coord\n", "A: foreign path")
    sec = put(repo, "harness/tests/leak.txt", secret + "\n", "main: a real-shaped secret")
    put(repo, "notes/shared.md", "base\n", "main: shared file")
    F.sh(["git", "-C", A, "merge", "-q", "--no-edit", "main"])
    clean_merge = F.sh(["git", "-C", A, "rev-parse", "HEAD"]).stdout.strip()
    put(repo, "notes/shared.md", "main's version\n", "main: shared edited")
    put(A, "notes/shared.md", "A's version\n", "A: shared edited (foreign)")
    r = F.sh(["git", "-C", A, "merge", "--no-edit", "main"], check=False)
    with open(os.path.join(A, "notes", "shared.md"), "w") as f:
        f.write("main's version\n")
    F.sh(["git", "-C", A, "add", "notes/shared.md"])
    F.sh(["git", "-C", A, "commit", "-q", "--no-edit"])
    resolved_merge = F.sh(["git", "-C", A, "rev-parse", "HEAD"]).stdout.strip()
    tmp = os.path.join(repo, "wt", "core-tmp")
    F.sh(["git", "-C", repo, "worktree", "add", "-q", "-b", "core/tmp", tmp, "core/nrpic"])
    src = put(tmp, "athenak/src/z.cpp", "// z\n", "core/tmp: source")
    docs = put(tmp, "docs/Z.md", "how to use z\n", "core/tmp: docs before docs/** is in OWNERSHIP")
    F.sh(["git", "-C", core, "merge", "-q", "--no-ff", "--no-edit", "core/tmp"])
    time.sleep(1.5)                          # main's OWNERSHIP changes a second later than the docs commit
    with open(os.path.join(repo, "tracks", "core", "OWNERSHIP"), "a") as f:
        f.write("docs/**\n")
    F.sh(["git", "-C", repo, "commit", "-q", "-am", "main: docs/** to core (as decision 0011)"])

    def state():
        refs = F.sh(["git", "-C", repo, "for-each-ref", "--format=%(refname) %(objectname)"]).stdout
        sts = [F.sh(["git", "-C", w, "status", "--porcelain"]).stdout for w in (repo, A, core, tmp)]
        heads = [F.sh(["git", "-C", w, "rev-parse", "HEAD"]).stdout for w in (repo, A, core, tmp)]
        return refs, sts, heads

    before = state()
    branches = ["main", "core/nrpic", "kb/main", "track/A-emd-pbh", "track/B-emd-gw"]      # core/tmp left out
    at = D.run_dryrun(repo, hook, since=root, wanted=branches, ownership="at-time", log=None)
    tip = D.run_dryrun(repo, hook, since=root, wanted=branches, ownership="tip", log=None)
    after = state()
    ref = {r["commit"]: r for r in at["refusals"]}
    reft = {r["commit"]: r for r in tip["refusals"]}

    c.ok(own not in ref, "an own-path commit of A: not refused")
    c.ok(foreign in ref and ref[foreign]["branch"] == "track/A-emd-pbh" and ref[foreign]["problems"][0]["check"] == "foreign",
         "A writing coord/: refused (foreign) on track/A-emd-pbh", str(ref.get(foreign)))
    c.ok(sec in ref and ref[sec]["branch"] == "main" and ref[sec]["problems"][0]["check"] == "secret",
         "a real-shaped secret committed on main: refused (secret)", str(ref.get(sec)))
    c.ok(at["merges"].get(clean_merge, {}).get("state") == "clean" and clean_merge not in ref,
         "a merge of main without conflict: replayed as clean, the secret it brings is not counted", str(at["merges"].get(clean_merge)))
    c.ok(r.returncode != 0 and at["merges"].get(resolved_merge, {}).get("state") == "resolved" and resolved_merge not in ref,
         "a conflicted merge resolved by hand: replayed as resolved, not refused (content from main)",
         str(at["merges"].get(resolved_merge)))
    c.ok(src not in ref and docs in ref and ref[docs]["branch"] == "core/tmp",
         "a commit only a merge message names: attributed to core/tmp; docs/ refused with the OWNERSHIP of its time",
         str(ref.get(docs)))
    c.ok(docs not in reft and foreign in reft, "with today's OWNERSHIP (tip) the docs/ commit passes, the foreign one does not",
         str(list(reft)))
    c.ok(at["commits"] == len(set(F.sh(["git", "-C", repo, "rev-list", *branches]).stdout.split())),
         "every commit of the branches is evaluated once", f"{at['commits']}")
    c.ok(before == after, "the repository under test is not written (refs, index, worktrees)")
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
