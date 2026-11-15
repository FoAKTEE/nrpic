# Harness rules and commands

State on 2026-11-15 (wave 2). The commands live in `harness/bin/` on main and reach every branch with
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
repositories in `scratch/<caller>/tmp/nrpic-doctor-*` that it removes. The guard, main, scratch
and stop rows feed the JSON of a Claude Code hook to `harness/hooks/pre_tool_guard.py` and
`stop_gate.sh`. State of `--all` after wave 1: every row PASS in all nine worktrees except
`venv` where the owner has not run `nrpic-env create --no-kokkos` yet, `kb` (MISSING until
main merges kb/main; it checks that `kb-data/db/current` cannot be opened for writing) and
`git` (MISSING until the pre-commit hook is installed, decision 0008).

## nrpic-run: runs (brief 11.6, 13.1; decisions 0006, 0012, 0014)

`harness/bin/nrpic-run --help` has the whole usage. What every owner needs:

```text
submit --kind scouting|production --gate G<k> --purpose TEXT [--launcher local|batch|chain]
       [--package DIR]... [--input PATH]... [--cores N] [--list FILE] [--gpu-hours H] [-- <cmd>]
status [<run_id>] · finish <run_id> · verify <run_id> · budget · stop <run_id> · lint [--all]
```

- Run id (decision 0012): `<short owner>-<YYYYMMDD-HHMMSS UTC>-<commit7>`, short owner A..F,
  `core`, `kb` (the brief's example, 11.6). Wave-1 ids with the full owner id
  (`A-emd-pbh-20261115-...`) stay valid; every command reads both.
- Clean tree: the code of the run must be the commit. Helpers sharing one worktree pass
  `--package <their directory>`: then the package, the inputs and the shared code (athenak/,
  python/, scripts/, harness/, problems/, ...) must be clean; other helpers' work elsewhere in
  `tracks/<ID>/` is recorded in `manifest.git.outside_package`, not refused.
- A local `python ...` command needs the worktree's `.venv` (`nrpic-env create --no-kokkos`;
  `.venv/` is ignored, the tree stays clean); `--allow-no-venv` for a standard-library script.
- Budget: the GPU-hour allotment of decision 0006 as amended by 0014 on main, per gate, summed
  over all branches of the owner; card-hours of hand-written manifests (`card_hours`) count
  toward their gate. A request above eight card-hours is noted (0014: announce it in STATUS.md).
  One lock per owner (`locks/nrpic-run.<ID>.lock`) covers the budget check and the run id.
- Hand-written manifests (wave 1, decision 0012) are read with defaults and never fatal: status
  words done/finished/ok -> completed, "failed (exit 1)" -> failed, cancelled -> stopped,
  superseded kept, none -> unknown; output directory from `outputs.dir`, `output_dir` or
  `output_directory`. `lint` lists what was read with defaults (`--all`: every owner);
  `finish` and `stop` refuse runs nrpic-run did not register; `verify` checks what they record.
  New manifests should be written by `submit` (it fills every field of
  `harness/templates/run_manifest.json`); a hand-written one is a last resort, said so in it.

## nrpic-stage: stage check (brief 13.3; decision 0012)

`collect <ID> G<k>` (kb: `KB-G<k>`, brief 12.10; `--stdout` prints instead of writing),
`verify <ID> G<k>`, `report <ID> G<k> [--decision TEXT]`. A package `tracks/<ID>/stage/G<k>/`
is STAGE_REPORT.md (from `report`), EVIDENCE.md, OPEN.md, CHECKLIST.md (from `collect`),
REVIEW.md where the lead rechecked helpers, and the scoping text (SCOPE.md or SCOPING.md beside
them, or the track's scope directory, named in the report). No REPORT.md. `report` run again
keeps the "Decision requested" text and every section it does not generate; write your own
analysis in sections of your own. `collect` adds the orchestrator's rulings on the criteria
(decision 0013) and keeps the status and evidence of unchanged items.

## nrpic-fetch-arxiv: arXiv and INSPIRE (decision 0015)

The only way to download from arXiv and INSPIRE; call the main checkout's copy from anywhere:
`python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv ...` (`--help`).

| Mode | Fetches | Writes under `kb-data/` |
|---|---|---|
| `<id>...` | `arxiv.org/e-print/<id>` | `raw/arxiv/<key>/<vN>/source.bin`, `src/`; record `meta/arxiv/<key>.json` |
| `--pdf <id>...` | `arxiv.org/pdf/<id><vN>` (entries without TeX) | `raw/arxiv/<key>/<vN>/source.pdf`; `meta/arxiv-pdf/<key>.json` |
| `--meta [--service arxiv\|inspire\|both] <id>...` | arXiv API (batches of 20, at most 50), INSPIRE (10, at most 25) | `meta/arxiv-api/<key>.{xml,json}`, `meta/inspire/<key>.json`; answers as served in `batches/` |
| `--inspire-query "<q>"` | INSPIRE literature search | `meta/inspire/query/<sha16>.json` |
| `--check <id>...` | nothing (content checks of the store) | nothing |

`<key>` is the id with `/` as `_`; `--ids-from FILE`, `--refresh`. One lock per service for the
machine (`locks/arxiv.lock`, `locks/inspire.lock`), three seconds between two requests, a
generic client name, no proxy or variable from the environment. Limits: download 512 MiB (PDF
200, metadata 32), gzip 2 GiB, 20000 members, 256 MiB per file, 1 GiB in all. Never recorded as
ok: an HTML or error page, an empty answer, a PDF without `%%EOF`, an API answer without the
requested ids, XML with a DOCTYPE. Gzipped PostScript stays `src/main.tex` (as before) with
`"content": "postscript"` and a hint to use `--pdf`.

## nrpic-env, the pre-commit hook

- `nrpic-env create [--no-kokkos]` makes `<worktree>/.venv` from `harness/env/uv.lock`; in a
  linked worktree it then checks out Kokkos by reference; in the main checkout it never touches
  Kokkos. `nrpic-env check` skips wt/ and the data roots of the main checkout.
- The machine file's default executables are the core-v0.3 builds (`.work/build_gpu_v03`,
  `.work/build_cpu_v03`); `--exe` chooses another, e.g. `scratch/core/exe/<branch>/` (0013).
- `harness/hooks/pre-commit` (brief 13.1) rejects files above 5 MB, added lines that look
  like secrets, run manifests that are not JSON objects or whose run_id differs from the
  directory, and paths outside `tracks/<ID>/` and OWNERSHIP on an owner's branch. It is not
  installed (`git config core.hooksPath <main>/harness/hooks` would change every worktree's
  commits; decision 0008).

## Other commands

| Command | Purpose | Usage |
|---|---|---|
| `nrpic-run` | register, start, query, close and verify runs; budgets | above; `harness/bin/nrpic-run --help` |
| `nrpic-env` | venv, Kokkos, builds, environment hash, `exec` with a clean environment | `harness/bin/nrpic-env --help` |
| `nrpic-stage` | the automated steps of the stage check | above; `harness/bin/nrpic-stage --help` |
| `nrpic-fetch-arxiv` | the only way to download from arXiv and INSPIRE | above |

Templates (`harness/templates/`): STATUS, JOURNAL and JOURNAL-entry, HANDOFF, ADR,
STAGE_REPORT, outbox_message, run_manifest.json. Figure libraries: `harness/style/`.

## Tests

`harness/tests/test_ctx.py` builds a scratch repository with five owners under
`scratch/harness/` and checks the context commands (81 checks, about 20 s);
`harness/tests/acceptance_ctx.py` adds the read-only runs on the live repository and writes
`coord/digests/bootstrap.md`. `harness/tests/run-runs-config-tests` runs the self-tests of
nrpic-env (15), nrpic-run (55), the style libraries (10), nrpic-stage (37, the stage-check
rehearsal), the hooks (99), the proposed configuration (51), nrpic-fetch-arxiv (29, against a
loopback server: no request leaves the machine) and the pre-commit hook (13); each test's log is
kept in `scratch/harness/logs/`. Tests never touch the live branches: anything that needs
branches or worktrees of its own runs in a scratch repository.

## Plain git, if a command fails

| Purpose | Plain git |
|---|---|
| sync | `git merge --no-edit main` |
| read another owner's file | `git show <branch>:tracks/<ID>/STATUS.md` |
| messages to me | for each other owner's branch: `git ls-tree -r --name-only <branch> -- tracks/<owner>/outbox`, names containing `__to-<me>__` or `__to-all__` |
| send a message | write `tracks/<ID>/outbox/<UTC>__to-<owner>__<slug>.md` with the front matter of `harness/templates/outbox_message.md`, commit it |
