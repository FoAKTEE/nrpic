#!/usr/bin/python3 -I
"""Self-test of harness/hooks/pre-commit in a scratch repository (brief 13.1; doctor row [git]).

    python3 -I harness/tests/test_precommit.py

The hook is installed in the scratch repository only (core.hooksPath of that repository); the live
repository is not touched (decision 0008). Covered: a clean own-path commit, a path-limited commit
(temporary index), a file above 5 MB, a fake secret, a foreign path, an OWNERSHIP glob, the main
branch, a merge from main, a manifest that is not JSON, one whose run_id differs from its directory,
a hand-written manifest accepted with a note.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402


def main():
    fx = F.make_repo("test-precommit")
    repo, A, core = fx["repo"], fx["wt"]["A-emd-pbh"], fx["wt"]["core"]
    F.sh(["git", "-C", repo, "config", "core.hooksPath", os.path.join(repo, "harness", "hooks")])
    c = F.Checks(f"pre-commit hook (scratch repo {repo})")

    def commit(wt, rel, data, *, paths=True, mode="w"):
        p = os.path.join(wt, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, mode) as f:
            f.write(data)
        F.sh(["git", "-C", wt, "add", "-f", "--", rel])
        r = F.sh(["git", "-C", wt, "commit", "-q", "-m", f"test {rel}"] + (["--", rel] if paths else []), check=False)
        if r.returncode != 0:
            F.sh(["git", "-C", wt, "reset", "-q", "HEAD", "--", rel], check=False)
            if os.path.exists(p):
                os.remove(p)
        return r

    r = commit(A, "tracks/A-emd-pbh/notes/a.md", "a small clean note\n")
    c.ok(r.returncode == 0, "a small file in the own track: accepted (path-limited commit, temporary index)", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/notes/b.md", "another\n", paths=False)
    c.ok(r.returncode == 0, "a plain commit of the staged index: accepted", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/big.bin", os.urandom(6 * 1024 * 1024), mode="wb")
    c.ok(r.returncode == 1 and "above the 5 MB limit" in r.stderr, "a 6 MB file: rejected", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/key.txt", "-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----\n")
    c.ok(r.returncode == 1 and "private key" in r.stderr, "a private key block: rejected", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/cfg.py", 'API_KEY = "abcdefghijklmnopqrstuvwxyz012345"\n')
    c.ok(r.returncode == 1 and "key or password" in r.stderr, "an API key assignment: rejected", r.stderr)
    r = commit(A, "tracks/B-emd-gw/STATUS.md", "gate: hijacked\n", mode="a")
    c.ok(r.returncode == 1 and "outside tracks/A-emd-pbh/" in r.stderr, "A writing B's STATUS.md: rejected", r.stderr)
    r = commit(A, "coord/CHARTER.md", "\nedit\n", mode="a")
    c.ok(r.returncode == 1 and "proposal" in r.stderr, "A writing coord/CHARTER.md: rejected with the way to propose", r.stderr)
    r = commit(core, "athenak/src/new.cpp", "// core's OWNERSHIP covers athenak/src/**\n")
    c.ok(r.returncode == 0, "core writing athenak/src/ (its OWNERSHIP glob): accepted", r.stderr)
    r = commit(repo, "coord/notes.md", "orchestrator\n")
    c.ok(r.returncode == 0, "the orchestrator on main writing coord/: accepted", r.stderr)
    r = F.sh(["git", "-C", A, "merge", "--no-edit", "main"], check=False)
    c.ok(r.returncode == 0, "a merge of main into the track (shared paths arrive): accepted", r.stderr)
    rd = "tracks/A-emd-pbh/runs/A-20261115-120000-abcdef0/manifest.json"
    r = commit(A, rd, "{not json")
    c.ok(r.returncode == 1 and "not JSON" in r.stderr, "a manifest that is not JSON: rejected", r.stderr)
    r = commit(A, rd, json.dumps({"run_id": "A-20261115-120001-abcdef0"}))
    c.ok(r.returncode == 1 and "differs from its directory" in r.stderr, "a manifest whose run_id differs from its directory: rejected",
         r.stderr)
    rd2 = "tracks/A-emd-pbh/runs/A-emd-pbh-20261115-120000-abcdef0/manifest.json"
    r = commit(A, rd2, json.dumps({"run_id": "A-emd-pbh-20261115-120000-abcdef0", "status": "done"}))
    c.ok(r.returncode == 0 and "hand-written manifest" in r.stderr,
         "a hand-written manifest in the full-id form with status 'done': accepted with a note", r.stderr)
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
