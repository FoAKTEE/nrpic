#!/usr/bin/python3 -I
"""Checks the proposed Claude Code configuration in harness/claude/ without installing it
(decision 0008: no .claude/ directory is created anywhere, not even in the scratch repository).

    python3 -I harness/tests/test_claude_config.py

1. settings.json parses; its keys, permission rules and hook events have the documented shapes;
   every hook command points at an executable under harness/hooks/.
2. agents/*.md and skills/*/SKILL.md have front matter with name (= file or directory name) and
   description; rules/*.md front matter, where present, has a list of path globs.
3. Each hook command of settings.json is run exactly as written (through bash, with
   CLAUDE_PROJECT_DIR set to a scratch worktree) on sample inputs: start brief, a denied and an
   allowed edit, a denied push, a blocked and a passing stop.
4. A simple model of the permission rules (deny before ask before allow; `Bash(prefix *)` matches the
   prefix and anything after a space) puts sample commands where the proposal intends.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402

CFG = os.path.join(F.LIVE, "harness", "claude")
EVENTS = {"PreToolUse", "PostToolUse", "Stop", "SessionStart", "SubagentStop", "UserPromptSubmit",
          "Notification", "PreCompact", "SessionEnd"}
TOOLS = {"Read", "Grep", "Glob", "Bash", "Write", "Edit", "NotebookEdit", "WebFetch", "WebSearch"}


def front_matter(path):
    text = open(path).read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+- ", line) and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(line.split("- ", 1)[1].strip().strip('"'))
            continue
        k, _, v = line.partition(":")
        key = k.strip()
        fm[key] = v.strip() if v.strip() else []
    return fm, text[m.end():]


def rule_matches(rule, cmd):
    m = re.fullmatch(r"Bash\((.*)\)", rule)
    if not m:
        return False
    pat = m.group(1)
    if pat.endswith(" *"):
        pre = pat[:-2]
        return cmd == pre or cmd.startswith(pre + " ")
    return cmd == pat


def permission(perms, cmd):
    for kind in ("deny", "ask", "allow"):
        if any(rule_matches(r, cmd) for r in perms.get(kind, [])):
            return kind
    return "prompt"


def main():
    c = F.Checks("proposed Claude Code configuration (harness/claude/)")
    s = json.load(open(os.path.join(CFG, "settings.json")))
    c.ok(s.get("autoMemoryEnabled") is False and s.get("env", {}).get("NRPIC_HARNESS") == "1",
         "settings.json parses; autoMemoryEnabled false and env NRPIC_HARNESS (brief 11.5)")
    rules = [r for k in ("allow", "ask", "deny") for r in s["permissions"][k]]
    c.ok(all(re.fullmatch(r"(Bash|Read|Edit)\(.+\)", r) for r in rules), f"{len(rules)} permission rules well formed")
    c.ok(set(s["hooks"]) <= EVENTS and set(s["hooks"]) == {"SessionStart", "PreToolUse", "Stop"},
         "hook events SessionStart, PreToolUse, Stop")
    cmds = []
    for ev, groups in s["hooks"].items():
        for g in groups:
            for h in g["hooks"]:
                cmds.append((ev, g.get("matcher"), h["command"]))
                rel = h["command"].replace('"$CLAUDE_PROJECT_DIR"/', "")
                c.ok(h["type"] == "command" and os.access(os.path.join(F.LIVE, rel), os.X_OK) and h.get("timeout"),
                     f"{ev}: {rel} exists, is executable, has a timeout")
    c.ok(any(m == "Edit|Write|NotebookEdit|MultiEdit|Bash" for _, m, _ in cmds), "guard matcher covers edits and Bash")

    for fn in sorted(os.listdir(os.path.join(CFG, "agents"))):
        fm, body = front_matter(os.path.join(CFG, "agents", fn))
        tools = {t.strip() for t in (fm or {}).get("tools", "").split(",") if t.strip()}
        c.ok(fm and fm.get("name") == fn[:-3] and fm.get("description") and tools <= TOOLS
             and fm.get("model") in ("opus", "inherit") and len(body.split()) > 80,
             f"agent {fn[:-3]}: front matter, tools {sorted(tools)}, model {fm.get('model') if fm else None}")
    want_agents = {"verifier", "kb-librarian", "figure-checker", "upstream-watch"}
    c.ok({f[:-3] for f in os.listdir(os.path.join(CFG, "agents"))} == want_agents, "the four agents of brief 11.1")
    for d in sorted(os.listdir(os.path.join(CFG, "skills"))):
        fm, body = front_matter(os.path.join(CFG, "skills", d, "SKILL.md"))
        c.ok(fm and fm.get("name") == d and fm.get("description"), f"skill /{d}: front matter")
    fm, body = front_matter(os.path.join(CFG, "skills", "stage-check", "SKILL.md"))
    c.ok(fm.get("disable-model-invocation") == "true" and all(f"{k}." in body for k in range(1, 11)),
         "/stage-check: person-invoked only, ten steps")
    c.ok(set(os.listdir(os.path.join(CFG, "skills"))) == {"stage-check", "ctx", "run", "kb"}, "the four skills of brief 11.1")
    for fn in sorted(os.listdir(os.path.join(CFG, "rules"))):
        fm, body = front_matter(os.path.join(CFG, "rules", fn))
        c.ok(fm is None or (isinstance(fm.get("paths"), list) and fm["paths"]),
             f"rule {fn}: " + ("global" if fm is None else f"scoped to {len(fm['paths'])} globs"))
    c.ok(set(os.listdir(os.path.join(CFG, "rules"))) == {"git.md", "numerics.md", "writing.md", "safety.md"},
         "the four rule files of brief 11.1")

    # hook commands as written, in a scratch repository (no .claude/ anywhere)
    fx = F.make_repo("test-config", owners=("A-emd-pbh", "B-emd-gw"))
    A = fx["wt"]["A-emd-pbh"]

    def run_hook(ev, payload):
        cmd = next(cm for e, _, cm in cmds if e == ev)
        env = dict(F.H.boot_env(), CLAUDE_PROJECT_DIR=A)
        return F.sh(["bash", "-c", cmd], env=env, input_text=json.dumps(payload), check=False, cwd=A)

    r = run_hook("SessionStart", {"hook_event_name": "SessionStart", "source": "startup", "cwd": A, "session_id": "c"})
    c.ok(r.returncode == 0 and "A-emd-pbh" in r.stdout and len(r.stdout.splitlines()) <= 40,
         "SessionStart command as written: brief of A", r.stdout + r.stderr)
    r = run_hook("PreToolUse", {"tool_name": "Edit", "tool_input": {"file_path": f"{A}/coord/CHARTER.md"}, "cwd": A})
    c.ok('"deny"' in r.stdout and "proposal" in r.stdout, "PreToolUse as written: edit of coord/ denied", r.stdout + r.stderr)
    r = run_hook("PreToolUse", {"tool_name": "Write", "tool_input": {"file_path": f"{A}/tracks/A-emd-pbh/notes/n.md"}, "cwd": A})
    c.ok(r.returncode == 0 and r.stdout.strip() == "", "PreToolUse as written: edit of the own track allowed")
    r = run_hook("PreToolUse", {"tool_name": "Bash", "tool_input": {"command": "git push --force"}, "cwd": A})
    c.ok('"deny"' in r.stdout, "PreToolUse as written: force push denied")
    open(os.path.join(A, "tracks", "A-emd-pbh", "notes", "loose.md"), "w").write("x\n")
    r = run_hook("Stop", {"hook_event_name": "Stop", "stop_hook_active": False, "cwd": A, "session_id": "c"})
    c.ok(r.returncode == 2 and "STATUS.md" in r.stderr, "Stop as written: dirty tree blocked once", r.stderr)
    r = run_hook("Stop", {"hook_event_name": "Stop", "stop_hook_active": True, "cwd": A, "session_id": "c"})
    c.ok(r.returncode == 0, "Stop as written: passes while stop_hook_active")
    live_home = F.live_home()
    c.ok(not any(os.path.isdir(os.path.join(d, ".claude")) for d in (fx["repo"], A, F.LIVE, live_home)),
         f"no .claude/ directory exists in the scratch repository, its worktree, or {live_home}")

    # permission model
    P = s["permissions"]
    samples = [("git push -u origin track/A-emd-pbh", "allow"), ("git push --force origin x", "deny"),
               ("git push -f", "deny"), ("git push --force-with-lease", "deny"), ("git commit -m x", "allow"),
               ("git commit --no-verify -m x", "deny"), ("git commit -n -m x", "deny"),
               ("git merge --no-edit main", "allow"), ("git merge other", "prompt"), ("git tag -a x", "ask"),
               ("git reset --hard", "ask"), ("git worktree remove wt/B", "deny"), ("git branch -D x", "deny"),
               ("harness/bin/nrpic-run submit --kind scouting", "allow"), ("harness/bin/nrpic-wt new X", "ask"),
               ("sbatch job.sh", "deny"), ("curl https://x", "deny"), ("pkill -f athena", "deny"),
               ("scripts/submit_chain.sh --status runs/x", "allow"), ("rm -r tracks/A/x", "ask"),
               ("python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv 2611.12831", "allow")]
    for cmd, want in samples:
        got = permission(P, cmd)
        c.ok(got == want, f"permission model: `{cmd}` -> {want}", f"got {got}")
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
