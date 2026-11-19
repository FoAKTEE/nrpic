# Harness rules and commands

State on 2026-11-19 (wave 2b; decision 0016). The commands live in `harness/bin/` on main and reach every branch with
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
| `ack <n\|file\|path>... \| --all [--note T]` | appends `<path> TAB <UTC> TAB <note>` to `tracks/<me>/inbox_acks.txt` and commits it; a line written by hand that names the message without the leading `tracks/` (`<ID>/outbox/<file>`), as `<branch>:<path>` or by its file name counts as the same message for `inbox`, `board` and `digest` | own branch |
| `post --to <ID\|all> --type T --slug S --body ...` | writes `tracks/<me>/outbox/<UTC>__to-<ID>__<slug>.md` from `harness/templates/outbox_message.md` and commits it; `--reply-by YYYY-MM-DD`, `--refs a,b`, `--body-file F\|-` | own branch |
| `show <ID> [file] [--branch B] [--log N]` | a file of `tracks/<ID>/` at the tip of ID's branch (default `STATUS.md`; a leading `/` means a path from the repository root) | nothing |
| `board [--write]` | every owner: branch tip, behind/ahead of main, gate, headline, next, blockers, inbox, budget; other branches; every message with who acknowledged it; `--write` puts it into `coord/BOARD.md` (orchestrator) | nothing, or `coord/BOARD.md` |
| `digest [--week YYYY-Www] [--write]` | gates, results, blockers, commits of the week, cross-owner requests picked up or not, the audit; `--write` puts it into `coord/digests/<week>.md` (orchestrator) | nothing, or the digest |
| `audit [--since REV] [--branch B]` | read-only: (1) commits on a branch (range `main..<branch>`) touching paths outside `tracks/<ID>/` and main's `tracks/<ID>/OWNERSHIP`, conflict resolutions in merges, merges of another owner's branch; (2) files above 1 MB added on a branch, and the known ones on main; (3) tracked files under an ignored root; (4) run manifests whose status is not a standard word (completed, failed, stopped, superseded, registered, running, submitted): those of waves 1 and 2 summed per owner and not counted (decision 0016), each later one a finding; notes: ignore rules that hide owners' files, run directories without a manifest, figures without a script, uncommitted worktrees, malformed messages, acknowledgement lines not written as `tracks/<ID>/outbox/<file>`. Exit 1 on findings | nothing |
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

- Run id (decision 0016 item 2, amending 0012): the form `nrpic-run` writes is the rule,
  `<short owner>-<YYYYMMDD-HHMMSS UTC>-<commit7>` with short owner A..F, `core`, `kb`, `orch`
  (`A-20261119-093015-3f9c2ab`). The long form of waves 1 and 2 (`A-emd-pbh-20261115-...`) stays
  valid for the runs that carry it; every command reads both. Do not invent a run id by hand.
- `$NRPIC_RUN_DIR` (the output directory `scratch/<ID>/<run_id>/`) and `$NRPIC_RUN_ID` exist only
  inside the run: in its environment, and as text that nrpic-run itself replaces in the command's
  arguments. The local launcher starts the command WITHOUT a shell. So write them in single
  quotes, `-- python3 x.py --out '$NRPIC_RUN_DIR'` (nrpic-run substitutes it, from wave 2b on), or
  let the script read `os.environ["NRPIC_RUN_DIR"]`, or `-- bash -c 'python3 x.py --out
  "$NRPIC_RUN_DIR"'`. Unquoted or in double quotes your own shell expands it first, to nothing
  (the variable is not set in your session). Before wave 2b a single-quoted `'$NRPIC_RUN_DIR'`
  reached the program literally and made a directory of that name in the worktree root (core,
  A, B, D, E, F and kb in wave 2): delete such a directory by its literal path, never commit it.
- Which Python: under `nrpic-run` (and `nrpic-env exec`) PATH is built from the machine file, with
  `<worktree>/.venv/bin` first when the venv exists. `python` and `python3` in a command are then
  the worktree's venv (packages of `harness/env/uv.lock` plus `tracks/<ID>/env/requirements.txt`),
  not your session's interpreter and not another venv: a tool with its own environment (kb's
  `kb/.venv`) is called by its full path or adds what it needs to the track's requirements.
  Without a venv `python3` is `/usr/bin/python3` (no numpy) and `python` does not exist.
- Where a run's records are written: the manifest `tracks/<ID>/runs/<run_id>/manifest.json`
  (committed on the own branch at submit and again at finish); in `scratch/<ID>/<run_id>/` the
  outputs, `run.log` (local runs), `sha256sums.txt` (at finish) and `.nrpic/launch.json`,
  `.nrpic/result.json` (how the run was started and ended; not checksummed). Nothing else is
  written into the worktree.
- Clean tree: the code of the run must be the commit. Helpers sharing one worktree pass
  `--package <their directory>`: then the package, the inputs and the shared code (athenak/,
  python/, scripts/, harness/, problems/, ...) must be clean; other helpers' work elsewhere in
  `tracks/<ID>/`, and from wave 2b an untracked file outside `tracks/` and the shared code (a
  finder's summary written into the worktree root, D in wave 2), is recorded in
  `manifest.git.outside_package`, not refused. A tracked file changed outside `tracks/` is refused.
- A local `python ...` command needs the worktree's `.venv` (`nrpic-env create --no-kokkos`;
  `.venv/` is ignored, the tree stays clean); `--allow-no-venv` for a standard-library script.
- Budget: the GPU-hour allotment of decision 0006 as amended by 0014 on main, per gate, summed
  over all branches of the owner; card-hours of hand-written manifests (`card_hours`) count
  toward their gate. A request above eight card-hours is noted (0014: announce it in STATUS.md).
  One lock per owner (`locks/nrpic-run.<ID>.lock`) covers the budget check and the run id.
- Hand-written manifests of waves 1 and 2 count as registered (decision 0016 item 3). They are
  read with defaults and never fatal: status words done/finished/ok -> completed, "failed (exit
  1)" -> failed, cancelled -> stopped, superseded kept, none -> unknown; output directory from
  `outputs.dir`, `output_dir` or `output_directory`. `lint` lists what was read with defaults
  (`--all`: every owner); `finish` and `stop` refuse runs nrpic-run did not register; `verify`
  checks what they record. A stage package lists them in EVIDENCE.md and `nrpic-stage verify`
  then waives their failures of the manifest check.
- From wave 2b (2026-11-19) on every run goes through `nrpic-run submit` (helpers sharing a
  worktree: `--package DIR`) and is closed with `finish`. `nrpic-ctx audit` counts a later
  manifest with a non-standard status word as a finding; its failures are not waived.

## nrpic-stage: stage check (brief 13.3; decision 0012)

`collect <ID> G<k>` (kb: `KB-G<k>`, brief 12.10; `--stdout` prints instead of writing),
`verify <ID> G<k>`, `report <ID> G<k> [--decision TEXT]`. A package `tracks/<ID>/stage/G<k>/`
is STAGE_REPORT.md (from `report`), EVIDENCE.md, OPEN.md, CHECKLIST.md (from `collect`),
VERIFIER.md (the verifier's report, decision 0016 item 1; VERIFIER_REPORT.md is accepted too),
REVIEW.md where the lead rechecked helpers, and the scoping text (SCOPE.md or SCOPING.md beside
them, or the track's scope directory, named in the report). No REPORT.md. `report` run again
keeps the "Decision requested" text and every section it does not generate; write your own
analysis in sections of your own. `collect` adds the orchestrator's rulings on the criteria
(decisions 0013, 0016) and keeps the status and evidence of unchanged items; for kb's KB-G2 it
adds the thresholds of the charter's section "Gates of the knowledge base" (0016 item 6).

`verify` and the hand-written manifests of waves 1 and 2 (decision 0016 item 3). Hand-written
means not written by nrpic-run: no `schema`, or a hand registration that copied it (a
`registered_by` field, a launcher such as "local (hand registration)", top-level fields
nrpic-run never writes such as `card_hours` or `output_dir`); such a manifest is checked for
what it records, not against the template. One dated before 2026-11-19 whose run an EVIDENCE.md
of the track names (this gate's or an earlier gate's; the full run id, or its
`-HHMMSS-<commit7>` suffix as in "analyses -174912-b122e01") counts as registered: its failures
of the manifest check are listed under `runs-waived` (WARN) and do not fail the package. A range
"X ... Y" is not expanded; name each run. An unlisted one still fails `runs`, and the message
says how many to list.

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

`<key>` is the id with `/` as `_`; `--ids-from FILE`, `--refresh`. Metadata lives where this
command writes it (decision 0016 item 6): `kb-data/meta/arxiv-api/<key>.{xml,json}` and
`kb-data/meta/inspire/<key>.json`, not `meta/arxiv/` (kb's inventory reads every file there as an
e-print record). One lock per service for the
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
`scratch/harness/` and checks the context commands (87 checks, about 30 s);
`harness/tests/acceptance_ctx.py` adds the read-only runs on the live repository and writes
`coord/digests/bootstrap.md`. `harness/tests/run-runs-config-tests` runs the self-tests of
nrpic-env (15), nrpic-run (57), the style libraries (10), nrpic-stage (45, the stage-check
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
