# Proposed Claude Code configuration: what it is, how to install it, what can go wrong

Status: PROPOSED, NOT INSTALLED (decision 0008). Nothing here is active: the live configuration of
this project is `.claude/` at the top of each worktree, and no such directory exists. Installing it
changes how every session of the project executes tools, so it waits for the user's decision.

## Contents

| Proposed path | Source here | What it does |
|---|---|---|
| `.claude/settings.json` | `harness/claude/settings.json` | permissions (allow / ask / deny), `autoMemoryEnabled: false`, three hooks |
| `.claude/rules/*.md` | `harness/claude/rules/` | git, numerics (path-scoped), writing (path-scoped), safety |
| `.claude/agents/*.md` | `harness/claude/agents/` | verifier, kb-librarian, figure-checker, upstream-watch |
| `.claude/skills/<name>/SKILL.md` | `harness/claude/skills/` | `/stage-check` (person-invoked only), `/ctx`, `/run`, `/kb` |
| (stays in place) | `harness/hooks/session_start.sh` | prints `nrpic-ctx brief --hook` (at most 40 lines); fills `CLAUDE_ENV_FILE` |
| (stays in place) | `harness/hooks/pre_tool_guard.py` | denies writes outside the owner's paths and the forbidden commands, with a reason |
| (stays in place) | `harness/hooks/stop_gate.sh` | blocks a turn's end once on a dirty tree or a stale STATUS.md |

The hooks are referenced as `"$CLAUDE_PROJECT_DIR"/harness/hooks/...`, so each session runs the
copy on its own worktree's branch.

Tests, run without installing anything: `python3 -I harness/tests/test_hooks.py` (99 sample
inputs: edits, shell commands, stop and start events) and `python3 -I
harness/tests/test_claude_config.py` (the files parse; the hook commands of settings.json, run
exactly as written, behave as intended in a scratch repository; the permission lists put each
sample command where intended).

## Steps (for the user to decide and do, in this order)

1. **Choose the open options** listed under "Decisions" below and edit `harness/claude/settings.json`
   on main accordingly; rerun the two tests.
2. **Make every branch carry the hooks.** In each worktree, at a moment when its owner is idle:
   `harness/bin/nrpic-ctx sync` (or `git -C wt/<ID> merge --no-edit main` by the orchestrator).
   Check: `ls wt/*/harness/hooks/pre_tool_guard.py` lists every worktree.
3. **Restart the track sessions the way brief 11.2 prescribes**, one session per worktree started
   inside it: `cd /data/haiyangw/nrpic/wt/<ID> && claude --name track-<X>`. The guard identifies a
   session by `$CLAUDE_PROJECT_DIR` (where the session started). A session started in the main
   checkout counts as the orchestrator; that is how the agents of wave 1 run now (see risk 1).
4. **Try it on one worktree first.** In a scratch clone (`python3 -I -c 'import sys;
   sys.path.insert(0, "harness/tests"); import rc_fixture as F; print(F.make_repo("try-config")["root"])'`
   prints one), copy the tree into the clone's `.claude/` and start `claude` in its
   `repo/wt/A-emd-pbh`. Run `/hooks` (three hooks listed), ask for an edit of `coord/CHARTER.md`
   (denied, with the proposal hint), `git push --force` (denied), `scripts/gpu_run.sh x y`
   (denied: use nrpic-run), leave a file uncommitted and end the turn (blocked once).
5. **Install on main**:
   ```bash
   cd /data/haiyangw/nrpic
   mkdir .claude
   cp harness/claude/settings.json .claude/settings.json
   cp -r harness/claude/rules harness/claude/agents harness/claude/skills .claude/
   git add .claude && git commit -m "Install the project's Claude Code configuration (decision 0008)" -- .claude
   git push
   ```
   Then repeat step 2 so every worktree gets `.claude/` on its branch ("tracked, identical on every
   branch", brief 11.5), and restart the sessions (step 3). Record the decision in
   `coord/DECISIONS/0008-claude-code-configuration.md` (status ACCEPTED, date, options chosen).
6. **Check** in one track session: `/hooks`, `/agents`, `/stage-check` appear; `harness/bin/nrpic-doctor`
   reports the rows [guard], [main], [stop] (the other harness owner's command).

Rolling back: `git rm -r .claude && git commit -m "Remove the Claude Code configuration" -- .claude`
on main, push, sync every worktree, restart sessions. For an immediate stop of all hooks of one
person without a commit, `{"disableAllHooks": true}` in `.claude/settings.local.json` of the
worktree concerned (whether the main checkout's local file also reaches the linked worktrees, as
brief 11.4 says for approvals, is [TO VERIFY] on the installed version).

## Decisions for the user

1. **Auto memory** (`"autoMemoryEnabled": false`, the brief's default, decision 0007). With false,
   sessions neither read nor write the memory directory, which holds standing instructions from
   earlier sessions (roles, figures for every test, commit and push, the machine's Slurm rules,
   kill by PID). Most of them are already in `CLAUDE.md`, decisions 0003, 0009, 0010 and
   `harness/claude/rules/`; the ones that are not (for example the user's Google Doc of the figure
   style, the agy roles for the PRD paper) would no longer reach sessions. Alternatives: delete the
   key (memory stays on for everyone, tracks are told not to write it), or keep false and copy what
   is missing into a rule file.
2. **`git push`**: here `allow` (decision 0003, accepted: every owner pushes its branch at the end of
   every session); the brief had `ask`, which in an unattended session means the push never happens.
   The guard still denies force pushes, deletions, other owners' branches and tags pushed by tracks.
3. **`sbatch`**: here `deny` for the Bash tool (simulations start through `nrpic-run`, which calls
   the repository's scripts itself and is not affected); the brief had `ask`. `git tag` moved from
   `allow` to `ask` (tags are the orchestrator's, decision 0003).
4. **Fail-open guard**: if the guard crashes or times out, Claude Code's default (`onFailure:
   continue`) lets the action through. `"onFailure": "block"` on the guard's entry makes it
   fail-closed: safer against mistakes, but a broken guard then stops every tool call of every
   session. Proposed: fail-open.
5. **Scope of the stop gate**: it also applies to the orchestrator in the main checkout, where
   helpers' uncommitted files are normal during a wave; it blocks once per state and session.
   Restricting it to track worktrees is one line in `stop_gate.sh`.

## Risks

1. **The current wave would stall.** The agents of wave 1 are started by the orchestrator from the
   main checkout and work in `wt/<ID>` by path; with the guard installed they count as the
   orchestrator, and the orchestrator may not write `wt/**`, so every edit they make in a worktree
   is denied. Install only between waves, after sessions are started inside their worktrees.
2. **Everything changes at once.** Settings and hooks apply to every session started after the
   change, including the orchestrator's; a faulty hook affects all tracks together (decision 0008).
   Per the hooks documentation a running session keeps the hooks it started with ([TO VERIFY] on
   the installed version), so restart deliberately.
3. **The guard is a safety net, not a boundary.** It reads command text: writes made inside a
   script, `python -c`, `eval`, `find -exec`, variables in paths, or a `cd` through a variable are
   not seen. The real boundaries remain the worktree isolation of Claude Code, the review of every
   stage package, and `nrpic-ctx audit`. Brief 11.5 says the same of permission patterns.
4. **False refusals.** The guard may deny a legitimate command (for example a `cp` whose last
   argument is not the destination, or a write into a directory reached through a symbolic link
   that resolves elsewhere). Each denial carries a reason; the session can rephrase or ask the
   orchestrator.
5. **Approvals are shared.** A "don't ask again" answered in any worktree is saved in the main
   checkout's `.claude/settings.local.json` and applies to all worktrees (brief 11.4): approve with
   care, and never approve the ask rules permanently.
6. **Stop gate interplay.** If `stop_hook_active` is missing in the installed version, the
   per-session marker under `locks/stop-gate/` still prevents a loop (tested); a session that keeps
   the tree dirty is reminded once per new state.
7. **Cost per tool call.** The guard runs three or four `git` commands per tool call (tens of
   milliseconds); the session start runs `nrpic-ctx brief` (seconds on a large repository, timeout
   30 s).

## Deviations from brief 11.5 and why

| Brief | Here | Why |
|---|---|---|
| `git push *` under ask | allow, guard checks the target | decision 0003 is accepted; ask stalls unattended sessions |
| `git tag *` under allow | ask | decision 0003: tags are the orchestrator's |
| `sbatch *` under ask | deny | runs start through `nrpic-run` (CLAUDE.md rule 4), which is unaffected |
| `harness/bin/nrpic-wt` not listed | ask | worktrees are the orchestrator's |
| matcher `Edit\|Write\|NotebookEdit\|Bash` | adds `MultiEdit` | harmless if the tool does not exist |
| stage-check step 9 `git add -A` and `git tag` | path-limited commit; tag by the orchestrator | other sessions share trees; decision 0003 |
| deny list | adds `git push --force-with-lease`, `git commit -n`, `pkill`, `killall` | brief 13.1, CLAUDE.md machine rules |
