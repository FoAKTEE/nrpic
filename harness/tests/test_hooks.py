#!/usr/bin/python3 -I
"""Feeds sample hook inputs to harness/hooks/ in a scratch repository (brief 11.4 rows [guard],
[scratch], [main], [stop]; acceptance test 5 of 11.7). Nothing is installed; the hooks are run
the way Claude Code runs them: JSON on stdin, $CLAUDE_PROJECT_DIR set to the session's worktree.

    python3 -I harness/tests/test_hooks.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402


def hook(fx, name, payload, project):
    env = dict(F.H.boot_env(), CLAUDE_PROJECT_DIR=project)
    if isinstance(payload, dict):
        payload = json.dumps(payload)
    return F.sh([os.path.join(fx["repo"], "harness", "hooks", name)], env=env, input_text=payload, check=False)


def guard(fx, project, tool, tool_input, cwd=None):
    r = hook(fx, "pre_tool_guard.py", {"session_id": "t", "hook_event_name": "PreToolUse", "tool_name": tool,
                                        "tool_input": tool_input, "cwd": cwd or project}, project)
    if r.stdout.strip():
        o = json.loads(r.stdout)["hookSpecificOutput"]
        return o["permissionDecision"], o["permissionDecisionReason"]
    return "none", r.stderr


def main():
    fx = F.make_repo("test-hooks")
    repo, W = fx["repo"], fx["wt"]
    A, B, CORE, KB = W["A-emd-pbh"], W["B-emd-gw"], W["core"], W["kb"]
    c = F.Checks(f"hooks (scratch repo {repo})")

    edits = [  # (session worktree, tool, path, expected decision)
        (A, "Write", f"{A}/tracks/A-emd-pbh/notes/derivation.md", "none"),
        (A, "Edit", "tracks/A-emd-pbh/STATUS.md", "none"),
        (A, "NotebookEdit", f"{A}/tracks/A-emd-pbh/analysis/a.ipynb", "none"),
        (A, "Edit", f"{A}/coord/CHARTER.md", "deny"),
        (A, "Edit", f"{A}/harness/bin/nrpic-run", "deny"),
        (A, "Edit", f"{A}/tracks/B-emd-gw/STATUS.md", "deny"),
        (A, "Edit", f"{B}/tracks/B-emd-gw/STATUS.md", "deny"),
        (A, "Edit", f"{repo}/CLAUDE.md", "deny"),
        (A, "Write", f"{repo}/scratch/A-emd-pbh/tmp/x.txt", "none"),
        (A, "Write", f"{repo}/scratch/B-emd-gw/x.txt", "deny"),
        (A, "Write", "/tmp/x.txt", "deny"),
        (A, "Write", f"{repo}/kb-data/raw/x", "deny"),
        (KB, "Write", f"{repo}/kb-data/raw/x", "none"),
        (KB, "Write", f"{KB}/kb/tool.py", "none"),
        (A, "Write", f"{A}/athenak/src/pgen/x.cpp", "deny"),
        (CORE, "Write", f"{CORE}/athenak/src/pgen/x.cpp", "none"),
        (CORE, "Write", f"{CORE}/scripts/new.sh", "none"),
        (repo, "Write", f"{repo}/harness/bin/new-tool", "none"),
        (repo, "Write", f"{repo}/coord/notes/n.md", "none"),
        (repo, "Edit", f"{repo}/tracks/A-emd-pbh/STATUS.md", "deny"),
        (repo, "Edit", f"{A}/tracks/A-emd-pbh/STATUS.md", "deny"),
        (repo, "Write", f"{repo}/.claude/settings.json", "ask"),
        (A, "Write", os.path.expanduser("~/.claude/projects/x/memory/note.md"), "deny"),
    ]
    for proj, tool, path, want in edits:
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        d, why = guard(fx, proj, tool, {key: path})
        who = os.path.relpath(proj, repo) if proj != repo else "main"
        c.ok(d == want, f"[{who}] {tool} {os.path.relpath(path, repo) if path.startswith(repo) else path}: {want}"
             + (f" ({why[:90]})" if d == "deny" and want == "deny" else ""), f"got {d}: {why}")

    sA = f"{repo}/scratch/A-emd-pbh"
    bashes = [  # (session, command, expected)
        (A, "git status && git diff", "none"),
        (A, "git push -u origin track/A-emd-pbh", "none"),
        (A, "git push", "none"),
        (A, "git push --force origin track/A-emd-pbh", "deny"),
        (A, "git push -f", "deny"),
        (A, "git push --force-with-lease origin track/A-emd-pbh", "deny"),
        (A, "git push origin +track/A-emd-pbh", "deny"),
        (A, "git push origin :track/A-emd-pbh", "deny"),
        (A, "git push origin track/B-emd-gw", "deny"),
        (A, "git push origin main", "deny"),
        (A, "git push --tags", "deny"),
        (A, "git commit --no-verify -m x", "deny"),
        (A, "git commit -n -m x", "deny"),
        (A, "git commit -anm x", "deny"),
        (A, "git commit -m 'explain the -n option'", "none"),
        (A, "git commit -am fix", "none"),
        (A, "git worktree remove wt/B-emd-gw", "deny"),
        (A, "git branch -D track/B-emd-gw", "deny"),
        (A, "git branch --show-current", "none"),
        (A, f"git -C {B} commit -m x", "deny"),
        (A, "cd ../B-emd-gw\ngit commit -m x", "deny"),
        (A, "git -C . log --oneline -3", "none"),
        (A, f"echo hi > {repo}/scratch/B-emd-gw/x", "deny"),
        (A, "echo hi > ../../scratch/B-emd-gw/x", "deny"),
        (A, f"mkdir -p {sA}/tmp && cp a.txt {sA}/tmp/", "none"),
        (A, f"cp a.txt {repo}/scratch/B-emd-gw/", "deny"),
        (A, f"cp {repo}/scratch/B-emd-gw/out.txt tracks/A-emd-pbh/analysis/", "none"),
        (A, f"cat {repo}/scratch/B-emd-gw/out.txt | head", "none"),
        (A, "echo x > tracks/A-emd-pbh/notes/a.md", "none"),
        (A, "echo x >> coord/CHARTER.md", "deny"),
        (A, "sed -i s/a/b/ harness/RULES.md", "deny"),
        (A, "sed -i s/a/b/ tracks/A-emd-pbh/STATUS.md", "none"),
        (A, "python3 x.py > /tmp/out.txt", "deny"),
        (A, "ls > /dev/null 2>&1", "none"),
        (A, "python3 a.py 2>&1 | tee tracks/A-emd-pbh/analysis/log.txt", "none"),
        (A, "/data/haiyangw/nrpic/.work/build_gpu_c3/src/athena -i x.athinput", "deny"),
        (A, "timeout 60 athena -i x.athinput", "deny"),
        (A, "scripts/gpu_run.sh runs/x problems/x.athinput", "deny"),
        (A, "BATCH=1 TIME=00:50:00 scripts/gpu_run.sh runs/x x.athinput", "deny"),
        (A, "harness/bin/nrpic-env exec -- scripts/gpu_batch.sh list.txt", "deny"),
        (A, "bash -c 'srun -p preempt athena -i x'", "deny"),
        (A, "sbatch job.sh", "deny"),
        (A, "scripts/submit_chain.sh runs/x x.athinput", "deny"),
        (A, "scripts/submit_chain.sh --status runs/x", "none"),
        (A, "squeue -u $USER; scancel 1234", "none"),
        (A, "harness/bin/nrpic-run submit --kind scouting --gate G1 --purpose p -- athena -i x", "none"),
        (A, "cat > tracks/A-emd-pbh/notes/run.sh <<'EOF'\nathena -i x\nsbatch y\nEOF", "none"),
        (A, "rm -rf $DIR/x", "deny"),
        (A, "rm -rf ${SCRATCH}", "deny"),
        (A, "rm tracks/A-emd-pbh/notes/old.md", "none"),
        (A, "pkill -f athena", "deny"),
        (A, "killall python3", "deny"),
        (A, "kill $(pgrep -f foo)", "deny"),
        (A, "kill 12345", "none"),
        (A, "curl -O https://example.org/x", "deny"),
        (A, "wget https://example.org/x", "deny"),
        (A, "python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv 2611.12831", "none"),
        (A, "echo 'unbalanced", "none"),
        (repo, "echo x > coord/notes/a.md", "none"),
        (repo, "git push origin main", "none"),
        (repo, "git push origin stage/A-emd-pbh/G0-pass-20261120", "none"),
        (repo, "git push origin track/A-emd-pbh", "deny"),
        (repo, "echo x > tracks/A-emd-pbh/STATUS.md", "deny"),
    ]
    for proj, cmd, want in bashes:
        d, why = guard(fx, proj, "Bash", {"command": cmd})
        who = os.path.relpath(proj, repo) if proj != repo else "main"
        short = cmd.replace(repo, "<repo>").replace("\n", "\\n")[:70]
        c.ok(d == want, f"[{who}] Bash `{short}`: {want}", f"got {d}: {why}")

    outside = os.path.join(fx["root"], "other-repo")      # a repository that is not nrpic
    os.makedirs(outside)
    F.sh(["git", "-C", outside, "init", "-q"])
    d, _ = guard(fx, outside, "Write", {"file_path": "/tmp/x"})
    c.ok(d == "none", "outside the nrpic repository the guard stays silent")
    r = hook(fx, "pre_tool_guard.py", "not json", A)
    c.ok(r.returncode == 0 and r.stdout == "", "unreadable input: allow (fail-open), exit 0")

    # Stop gate
    def stop(proj, active=False, sid="s1"):
        return hook(fx, "stop_gate.sh", {"session_id": sid, "hook_event_name": "Stop", "stop_hook_active": active,
                                         "cwd": proj}, proj)
    r = stop(A)
    c.ok(r.returncode == 0, "stop: clean worktree, STATUS current -> pass", r.stderr)
    junk = os.path.join(A, "tracks", "A-emd-pbh", "notes", "draft.md")
    open(junk, "w").write("draft\n")
    r = stop(A)
    c.ok(r.returncode == 2 and "uncommitted" in r.stderr and "STATUS.md" in r.stderr,
         "stop: dirty worktree -> blocked with instructions (exit 2)", r.stderr)
    r = stop(A, active=True)
    c.ok(r.returncode == 0, "stop: stop_hook_active -> pass (no loop)")
    r = stop(A)
    c.ok(r.returncode == 0, "stop: same state again in the same session -> pass (fallback loop guard)")
    r = stop(A, sid="s2")
    c.ok(r.returncode == 2, "stop: another session with the same dirty state -> blocked once")
    F.sh(["git", "-C", A, "add", "--", "tracks/A-emd-pbh/notes/draft.md"])
    F.sh(["git", "-C", A, "commit", "-q", "-m", "A(note): draft", "--", "tracks/A-emd-pbh/notes/draft.md"])
    r = stop(A, sid="s3")
    c.ok(r.returncode == 2 and "STATUS.md is older" in r.stderr, "stop: commit newer than STATUS.md -> blocked", r.stderr)
    F.commit_file(A, "tracks/A-emd-pbh/STATUS.md", open(os.path.join(A, "tracks/A-emd-pbh/STATUS.md")).read()
                  + "last-result: draft written\n", "A(status): update")
    r = stop(A, sid="s3")
    c.ok(r.returncode == 0, "stop: after the STATUS commit -> pass", r.stderr)
    r = stop(outside)
    c.ok(r.returncode == 0, "stop: outside the nrpic repository -> pass")

    # SessionStart
    envf = os.path.join(fx["root"], "claude_env_file")
    open(envf, "w").close()
    env = dict(F.H.boot_env(), CLAUDE_PROJECT_DIR=A, CLAUDE_ENV_FILE=envf)
    r = F.sh([os.path.join(repo, "harness", "hooks", "session_start.sh")], env=env, check=False,
             input_text=json.dumps({"session_id": "x", "hook_event_name": "SessionStart", "source": "startup", "cwd": A}))
    lines = r.stdout.splitlines()
    c.ok(r.returncode == 0 and 0 < len(lines) <= 40 and "A-emd-pbh" in r.stdout,
         f"session start: brief of A ({len(lines)} lines)", r.stdout + r.stderr)
    c.ok(f"export NRPIC_TRACK=A-emd-pbh" in open(envf).read() and f"NRPIC_WT={A}" in open(envf).read(),
         "session start: NRPIC_* variables written to CLAUDE_ENV_FILE")
    r = F.sh([os.path.join(repo, "harness", "hooks", "session_start.sh")],
             env=dict(F.H.boot_env(), CLAUDE_PROJECT_DIR=outside), check=False, input_text="{}")
    c.ok(r.returncode == 0 and r.stdout == "", "session start: silent outside the nrpic repository")
    print("brief seen by A's session:\n    " + "\n    ".join(lines[:12]))
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
