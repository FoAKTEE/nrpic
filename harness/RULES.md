# Harness rules and commands

State on 2026-11-15. The commands live in `harness/bin/` on main and reach every branch with
`nrpic-ctx sync`. Call your own worktree's copy, `harness/bin/<command>`, from your worktree
(the commands act on the worktree you are in; a command started in a data root of the main
checkout such as `scratch/` refuses). Each prints its usage with `--help`. They build their
environment from fixed values and the passwd entry, never from the session's variables, and
run with `python3 -I`. Owners, branches, worktrees: `CLAUDE.md`. Specification: brief 11.3-11.7.

## Every session

```text
start   harness/bin/nrpic-ctx sync            merge main into your branch (refuses uncommitted tracked
                                               changes; on a conflict it aborts and names the files)
        harness/bin/nrpic-ctx brief           who you are, gate, next, inbox, how far main is ahead
        harness/bin/nrpic-ctx inbox --show    messages to you or to all, not yet acknowledged
        harness/bin/nrpic-ctx ack <n|file>... acknowledge what you have read (committed)
work    harness/bin/nrpic-ctx show <ID> [file]   another owner's file at the tip of its branch
        harness/bin/nrpic-ctx post ...           a message or proposal to another owner (committed)
        harness/bin/nrpic-run submit ...         every simulation and analysis run (registered)
end     rewrite tracks/<ID>/STATUS.md (keys below, at most 60 lines) and tracks/<ID>/HANDOFF.md
        (keep a line `Run next: <exact command>`); append to JOURNAL.md
        (`nrpic-ctx template JOURNAL-entry` prints an entry); commit; git push -u origin <branch>
```

## nrpic-ctx: context sharing (brief 11.3)

| Command | What it does | Writes |
|---|---|---|
| `sync` | `git merge --no-edit main` into the own branch; lists new decisions and changed areas | own branch (merge) |
| `brief [--hook]` | at most 40 lines: owner, gate, headline, next, blockers, inbox, main ahead, remote, tree, HANDOFF's `Run next:`; `--hook` takes the cwd from the JSON of a SessionStart hook on stdin and never fails | nothing |
| `inbox [--all] [--show] [--count]` | messages addressed to me or to `all`, not acknowledged; numbered | nothing |
| `ack <n\|file\|path>... \| --all [--note T]` | appends `<path> TAB <UTC> TAB <note>` to `tracks/<me>/inbox_acks.txt` and commits it | own branch |
| `post --to <ID\|all> --type T --slug S --body ...` | writes `tracks/<me>/outbox/<UTC>__to-<ID>__<slug>.md` from `harness/templates/outbox_message.md` and commits it; `--reply-by YYYY-MM-DD`, `--refs a,b`, `--body-file F\|-` | own branch |
| `show <ID> [file] [--branch B] [--log N]` | a file of `tracks/<ID>/` at the tip of ID's branch (default `STATUS.md`; a leading `/` means a path from the repository root) | nothing |
| `board [--write]` | every owner: branch tip, behind/ahead of main, gate, headline, next, blockers, inbox, budget; other branches; every message with who acknowledged it; `--write` puts it into `coord/BOARD.md` (orchestrator) | nothing, or `coord/BOARD.md` |
| `digest [--week YYYY-Www] [--write]` | gates, results, blockers, commits of the week, cross-owner requests picked up or not, the audit; `--write` puts it into `coord/digests/<week>.md` (orchestrator) | nothing, or the digest |
| `audit [--since REV] [--branch B]` | read-only: (1) commits on a branch (range `main..<branch>`) touching paths outside `tracks/<ID>/` and main's `tracks/<ID>/OWNERSHIP`, conflict resolutions in merges, merges of another owner's branch; (2) files above 1 MB added on a branch, and the known ones on main; (3) tracked files under an ignored root; notes: ignore rules that hide owners' files, run directories without a manifest, figures without a script, uncommitted worktrees, malformed messages. Exit 1 on findings | nothing |
| `owners`, `template NAME [--id ID]` | the owner table; a template of `harness/templates/` with the placeholders filled | nothing |

Rules the command enforces or relies on:

- Write commands (`sync`, `post`, `ack`, `board --write`, `digest --write`) act only on the
  worktree you are in and only on an owner's branch; `-C` is refused for them. The
  orchestrator posts from the main checkout into `tracks/orch/outbox/` on main.
- `post` and `ack` commit path-limited (`git commit -- <file>`), retrying while
  `index.lock` exists. One writer of the index per worktree: a helper passes `--no-commit`
  and hands the file to the lead.
- Reading: a message is read from the sender's own directory `tracks/<sender>/outbox/` on
  the sender's own branches only (canonical branch first, then its temporary branches; the
  first copy wins), never from copies that reached other branches through main. Every
  message therefore appears exactly once, before and after merges.
- A message is never edited after it is posted; a correction is a new message. The file
  name routes it (`__to-<ID>__`); the front matter must agree (audit notes disagreements).
  Types: `info`, `request`, `proposal`, `interface-change`, `blocker`, `kb-request`.
- A proposal that changes shared content or core is a message of type `proposal` or
  `interface-change` to `orch` (or `core`), with code on a branch `proposal/<ID>/<slug>`.
  Once accepted it becomes `coord/DECISIONS/NNNN-*.md` (template `harness/templates/ADR.md`)
  and reaches everyone with the next `sync`.
- STATUS.md keys read by `board` and `brief`: `gate`, `headline`, `last-result`, `next`
  (`1. ... 2. ... 3. ...`), `blockers`, `needs`, `offers`, `budget`, one per line as
  `key: value`, continuation lines indented (template `harness/templates/STATUS.md`).

## nrpic-wt: worktrees (brief 11.2)

| Command | What it does |
|---|---|
| `list` | every worktree: branch, owner, head, clean or dirty, behind/ahead of main, pushed or not |
| `check [ID\|name\|path]` | rows `[wt]` (path `wt/<ID>`, branch of the owner), `[build]` (no symbolic link into another worktree or the main checkout), `[copy]`, `[kokkos]` |
| `new ID [--name N] [--branch B] [--base REF] [--kokkos]` | orchestrator, main checkout only: `git worktree add` on the owner's branch (existing, or new from main); temporary worktrees are `wt/<ID>-<x>` on `core/<x>`, `kb/<x>` or `track/<ID>--<x>`; copies the files of `harness/wt_copy.list`; `--kokkos` initialises the submodule by reference; then `check` |
| `retire ID` | checks that the tree is clean and the tip is pushed, tagged or on main, and prints `git worktree remove ...` for a person; it removes nothing (brief 11.2: after asking the user) |

## nrpic-doctor: isolation self-test (brief 11.4)

`harness/bin/nrpic-doctor` in your worktree prints one line per row: `wt build venv env
scratch guard main kb gpu ctx git stop`, each PASS, FAIL, MISSING (the component is not built,
installed or synced yet) or SKIP (does not apply to this owner); exit 0 only if all pass or
skip. `--rows a,b` selects rows, `--all` checks every owner's worktree read-only (from the main
checkout). It writes no worktree: a probe file in `scratch/<ID>/tmp/` and throwaway
repositories in `scratch/<caller>/tmp/nrpic-doctor-*` that it removes. The guard and hook
rows feed the JSON of a Claude Code hook to `harness/hooks/pre_tool_guard.py` and
`stop_gate.sh`; until those exist and decision 0008 installs the configuration, they read
MISSING.

## Other commands

| Command | Purpose | Usage |
|---|---|---|
| `nrpic-run` | register, start, query, close and verify runs; budgets of decision 0006 | `harness/bin/nrpic-run --help` |
| `nrpic-env` | venv, Kokkos, builds, environment hash, `exec` with a clean environment | `harness/bin/nrpic-env --help` |
| `nrpic-fetch-arxiv` | the only way to download arXiv sources (one lock, three seconds apart) | `python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv <id>` |

Templates (`harness/templates/`): STATUS, JOURNAL and JOURNAL-entry, HANDOFF, ADR,
STAGE_REPORT, outbox_message, run_manifest.json. Figure libraries: `harness/style/`.

## Tests

`harness/tests/test_ctx.py` builds a scratch repository with five owners under
`scratch/harness/` and checks the context commands (81 checks, about 20 s);
`harness/tests/acceptance_ctx.py` adds the read-only runs on the live repository and writes
`coord/digests/bootstrap.md`. Tests never touch the live branches: anything that needs
branches or worktrees of its own runs in a scratch repository.

## Known issue (state on 2026-11-15)

`.gitignore` line 12, `runs/`, is not anchored, so it also ignores `tracks/<ID>/runs/`: run
manifests are tracked only when added with `git add -f` (the audit reports it; `nrpic-run`
can force-add its manifests). Until main anchors the pattern as `/runs/`, anything else under
`tracks/<ID>/runs/` must be added with `git add -f`.

## Plain git, if a command fails

| Purpose | Plain git |
|---|---|
| sync | `git merge --no-edit main` |
| read another owner's file | `git show <branch>:tracks/<ID>/STATUS.md` |
| messages to me | for each other owner's branch: `git ls-tree -r --name-only <branch> -- tracks/<owner>/outbox`, names containing `__to-<me>__` or `__to-all__` |
| send a message | write `tracks/<ID>/outbox/<UTC>__to-<owner>__<slug>.md` with the front matter of `harness/templates/outbox_message.md`, commit it |
