#!/usr/bin/python3 -I
"""Self-test of harness/hooks/pre-commit in a scratch repository (brief 13.1; doctor row [git]).

    python3 -I harness/tests/test_precommit.py [--hook PATH]

The hook is installed in the scratch repository only (core.hooksPath of that repository); the live
repository is not touched (decision 0008). --hook tests another copy of the hook (the one before the
corrections of the dry run of wave 3a fails the checks marked "dry run").

Covered: a clean own-path commit, a path-limited commit (temporary index), a file above 5 MB, a
private key block, an API key assignment, a foreign path, an OWNERSHIP glob, the main branch, a merge
from main, a manifest that is not JSON, one whose run_id differs from its directory, a hand-written
manifest accepted with a note; from the dry run over the history (coord/digests/hook-dryrun.md):
documentation placeholders accepted (a key header with a stub, the AWS EXAMPLE key, a run of
consecutive characters), real-shaped fakes rejected (an AWS secret, a key in a string with \\n
escapes), a '++' content line or a quoted file name or diff.noprefix no longer hide a secret, a
conflicted merge that takes main's content (secret-looking test fixture, 6 MB file) accepted while a
resolution that adds a secret is rejected, core's python/tests/ refused until main's OWNERSHIP of
core lists it. The fakes are made at run time, so that no line of this file looks like a secret.
"""
import argparse
import base64
import json
import os
import random
import shutil
import string
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402

RND = random.Random(20261119)


def token(n, alphabet=string.ascii_letters + string.digits):
    return "".join(RND.choice(alphabet) for _ in range(n))


def key_block(name="OPENSSH", sep="\n"):
    body = base64.b64encode(bytes(RND.getrandbits(8) for _ in range(300))).decode()
    lines = [body[i:i + 70] for i in range(0, 400, 70)]
    return sep.join([f"-----BEGIN {name} " + "PRIVATE KEY-----"] + lines + [f"-----END {name} " + "PRIVATE KEY-----"]) + sep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hook")
    a = ap.parse_args()
    fx = F.make_repo("test-precommit")
    repo, A, core = fx["repo"], fx["wt"]["A-emd-pbh"], fx["wt"]["core"]
    if a.hook:
        shutil.copy2(a.hook, os.path.join(repo, "harness", "hooks", "pre-commit"))
    F.sh(["git", "-C", repo, "config", "core.hooksPath", os.path.join(repo, "harness", "hooks")])
    c = F.Checks(f"pre-commit hook (scratch repo {repo})")

    def write(wt, rel, data, mode="w"):
        p = os.path.join(wt, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, mode) as f:
            f.write(data)
        return p

    def commit(wt, rel, data, *, paths=True, mode="w"):
        p = write(wt, rel, data, mode)
        F.sh(["git", "-C", wt, "add", "-f", "--", rel])
        r = F.sh(["git", "-C", wt, "commit", "-q", "-m", f"test {rel}"] + (["--", rel] if paths else []), check=False)
        if r.returncode != 0:
            F.sh(["git", "-C", wt, "reset", "-q", "HEAD", "--", rel], check=False)
            if os.path.exists(p):
                os.remove(p)
        return r

    def plant(wt, files, msg):
        """Commit without the hook (content from before the hook, or a foreign path set up for a test)."""
        for rel, data, mode in files:
            write(wt, rel, data, mode)
            F.sh(["git", "-C", wt, "add", "-f", "--", rel])
        F.sh(["git", "-C", wt, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", msg])

    aws_real = token(40, string.ascii_letters + string.digits + "/+")
    api_real = token(32)

    r = commit(A, "tracks/A-emd-pbh/notes/a.md", "a small clean note\n")
    c.ok(r.returncode == 0, "a small file in the own track: accepted (path-limited commit, temporary index)", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/notes/b.md", "another\n", paths=False)
    c.ok(r.returncode == 0, "a plain commit of the staged index: accepted", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/big.bin", os.urandom(6 * 1024 * 1024), mode="wb")
    c.ok(r.returncode == 1 and "above the 5 MB limit" in r.stderr, "a 6 MB file: rejected", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/key.txt", key_block())
    c.ok(r.returncode == 1 and "private key" in r.stderr, "a private key block with its key material: rejected", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/cfg.py", "API_" + f'KEY = "{api_real}"\n')
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

    # ---- the corrections of the dry run over the history (wave 3a)
    stub = 'fh.write("-----BEGIN OPENSSH ' + 'PRIVATE KEY-----\\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ\\n-----END OPENSSH ' \
           + 'PRIVATE KEY-----\\n"\n'
    r = commit(A, "tracks/A-emd-pbh/notes/stub.py", stub)
    c.ok(r.returncode == 0, "dry run: a key header with a 42-character stub (nrpic-doctor before wave 3a): accepted", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/notes/aws_doc.txt", "aws_secret_" + "access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCY" + "EXAMPLEKEY\n")
    c.ok(r.returncode == 0, "dry run: the AWS documentation key (EXAMPLE): accepted", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/notes/placeholder.py", "API_" + 'KEY = "' + string.ascii_lowercase + '012345"\n')
    c.ok(r.returncode == 0, "dry run: a placeholder API key of consecutive letters (test_precommit.py before wave 3a): accepted",
         r.stderr)
    r = commit(A, "tracks/A-emd-pbh/notes/aws.txt", "aws_secret_" + f"access_key = {aws_real}\n")
    c.ok(r.returncode == 1 and "AWS secret" in r.stderr, "dry run: an AWS secret of real shape: rejected", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/notes/key.json", json.dumps({"private_key": key_block("RSA")}) + "\n")
    c.ok(r.returncode == 1 and "private key" in r.stderr, "dry run: a key inside a JSON string (\\n escapes): rejected", r.stderr)
    r = commit(A, "tracks/A-emd-pbh/notes/plusplus.md", "++ a line that starts with two plus signs\n" + "aws_secret_"
               + f"access_key = {aws_real}\n")
    c.ok(r.returncode == 1 and "AWS secret" in r.stderr, "dry run: a '++' content line no longer hides a later secret", r.stderr)
    r = commit(A, 'tracks/A-emd-pbh/notes/we"ird.txt', "aws_secret_" + f"access_key = {aws_real}\n")
    c.ok(r.returncode == 1 and "AWS secret" in r.stderr, "dry run: a file name git quotes no longer hides a secret", r.stderr)
    F.sh(["git", "-C", repo, "config", "diff.noprefix", "true"])
    r = commit(A, "tracks/A-emd-pbh/notes/noprefix.txt", "aws_secret_" + f"access_key = {aws_real}\n")
    F.sh(["git", "-C", repo, "config", "--unset", "diff.noprefix"])
    c.ok(r.returncode == 1 and "AWS secret" in r.stderr, "dry run: diff.noprefix in the git configuration no longer hides a secret",
         r.stderr)

    # conflicted merges: main brings content checked (or planted) there; the track resolves a conflict
    plant(repo, [("notes/shared.md", "base\n", "w")], "shared file")
    F.sh(["git", "-C", A, "merge", "-q", "--no-edit", "main"])
    plant(repo, [("notes/shared.md", "main's version\n", "w"), ("harness/tests/fixture.txt", "aws_secret_" + f"access_key = {aws_real}\n", "w"),
                 ("data/big.bin", os.urandom(6 * 1024 * 1024), "wb")], "main: a fixture that looks like a secret, a 6 MB file")
    plant(A, [("notes/shared.md", "A's version\n", "w")], "A edits a shared file (planted)")
    r = F.sh(["git", "-C", A, "merge", "--no-edit", "main"], check=False)
    conflicted = r.returncode != 0
    write(A, "notes/shared.md", "main's version\n")
    F.sh(["git", "-C", A, "add", "notes/shared.md"])
    r = F.sh(["git", "-C", A, "commit", "-q", "--no-edit"], check=False)
    c.ok(conflicted and r.returncode == 0,
         "dry run: a conflicted merge of main resolved to main's side (main brings a secret-looking fixture and a 6 MB file): "
         "accepted", (r.stderr or "") + ("" if conflicted else " (the merge did not conflict)"))
    plant(repo, [("notes/shared.md", "main again\n", "w")], "main edits the shared file")
    plant(A, [("notes/shared.md", "A again\n", "w")], "A edits the shared file (planted)")
    r = F.sh(["git", "-C", A, "merge", "--no-edit", "main"], check=False)
    conflicted = r.returncode != 0
    write(A, "notes/shared.md", "main again\nA again\n" + "aws_secret_" + f"access_key = {token(40)}\n")
    F.sh(["git", "-C", A, "add", "notes/shared.md"])
    r = F.sh(["git", "-C", A, "commit", "-q", "--no-edit"], check=False)
    c.ok(conflicted and r.returncode == 1 and "AWS secret" in r.stderr and "big.bin" not in r.stderr,
         "dry run: a resolution that adds a secret line: rejected (and only that line is reported)", r.stderr)
    F.sh(["git", "-C", A, "merge", "--abort"], check=False)

    r = commit(core, "python/tests/test_new_tool.py", "def test_x():\n    assert True\n")
    c.ok(r.returncode == 1 and "outside tracks/core/" in r.stderr,
         "dry run: core writing python/tests/ while main's OWNERSHIP of core lacks python/tests/**: rejected", r.stderr)
    plant(repo, [("tracks/core/OWNERSHIP", "python/tests/**\n", "a")], "orchestrator: python/tests/** to core")
    r = commit(core, "python/tests/test_new_tool.py", "def test_x():\n    assert True\n")
    c.ok(r.returncode == 0, "dry run: the same after main adds python/tests/** to core's OWNERSHIP: accepted", r.stderr)
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
