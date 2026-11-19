# Harness of wave 2b (2026-11-19, 14:05-14:45Z)

Written by the harness helper of the orchestrator, from the main checkout. Commits on main:
`a25110d` (nrpic-stage, nrpic-ctx, nrpic-run, the library, the proposed configuration, RULES.md,
self-tests), `a611868` (the charter's section "Gates of the knowledge base"), and the commit of
this digest with `coord/BOARD.md` and `coord/REQUESTS.md`. Owners get the commands with
`nrpic-ctx sync`; kb gets the KB-G2 thresholds the same way.

## What changed, against decision 0016 and the requests of wave 2

| Asked by | Answer |
|---|---|
| 0016 item 1; B `verifier-report-name`, D `verifier-file-name` | `nrpic-stage report` takes `stage/G<k>/VERIFIER.md` as the verifier's report (VERIFIER_REPORT.md still accepted); `collect`, `verify`, the template, the verifier agent and the stage-check skill of `harness/claude/` say VERIFIER.md |
| 0016 item 3; B `stage-verify-runs-check` | `nrpic-stage verify`: a hand-written manifest dated before 2026-11-19 that an EVIDENCE.md of the track names (this gate's or an earlier one's; the full id or its `-HHMMSS-<commit7>` suffix) is waived: its failures go to `runs-waived` (WARN). Ranges "X ... Y" are not expanded (they would cover runs nobody listed). Hand registrations that copied the nrpic-run schema (A, B, C, D, core: `registered_by`, launcher "local (hand registration)", fields such as `card_hours`, `output_dir`) are now read as hand-written, so they are checked for what they record and not against the template |
| 0016 item 2 | run ids with `orch` are read; RULES.md states the short form as the rule |
| 0016 item 6; kb `kb-g2-thresholds`, `kb-g2-hit-level` | `coord/CHARTER.md` "Gates of the knowledge base"; `collect kb KB-G2` adds the two thresholds as their own checklist items |
| harness wave-2 report; kb's acknowledgements | `nrpic-ctx inbox`, `board`, `digest` read an `inbox_acks.txt` line without the leading `tracks/` (also `<branch>:<path>`, a file name) as the same message; `audit` notes such lines |
| E `harness-and-brief-notes` (1) | `nrpic-ctx audit` section 4: run manifests with a non-standard status word; waves 1 and 2 summed per owner (not counted), each later one a finding |
| kb `nrpic-run-literal-run-dir`, A `harness-wave2-notes` (3), B, D, E, F, core | `nrpic-run` local launcher replaces `$NRPIC_RUN_DIR`, `${NRPIC_RUN_DIR}`, `$NRPIC_RUN_ID` written in single quotes in the command's arguments (`launch.json` keeps both forms, `run.log` prints the expanded argv); RULES.md explains the trap, which Python is first on PATH (the worktree's `.venv`, else `/usr/bin/python3`, no `python`), where a run's records are written |
| D `nrpic-run-outdir-and-root-files` (2) | with `--package`, an untracked file outside `tracks/` and the shared code (a finder's summary in the worktree root) is recorded in `manifest.git.outside_package`, not refused; a tracked change outside `tracks/` still is |

Two defects found and fixed on the way: `nrpic-stage verify` crashed when it ran twice on one
commit within one second (same export directory); the stage self-test picked the hand-written
manifest instead of the registered run in one in N orderings of `os.listdir` (the 36/37 of wave 2),
and the nrpic-run self-test raced the background wrapper's start.

## Live checks (read-only, from the main checkout, 14:28-14:32Z)

`nrpic-stage verify <ID> <gate> --no-rerun --no-checksums` (exports under
`scratch/orch/tmp/stage-verify/`, nothing written into a worktree):

| Package | runs | waived | still failing |
|---|---|---|---|
| A-emd-pbh G1 | 132 | 0 | 1 run of today still running; main not merged |
| B-emd-gw G0 | 156 | 0 | 7 runs of today running or submitted; main not merged |
| B-emd-gw G1 | 158 | 0 | 9 runs of today running or submitted; main not merged |
| C-sidm G0 | 82 | 0 | 2 runs of today running; main not merged |
| D-bh-dress G1 | 128 | 3 (G0's EVIDENCE.md) | 1 run of today submitted; main not merged |
| E-stoch-inf G0 | 82 | 0 | E-20261115-174600-81652ff left "running" in wave 2, 1 run of today; main not merged |
| F-hills G0 | 121 | 0 | none: PASS |

Before these changes the same packages failed on 33 schema-copying hand registrations of D
("fields missing: input") and 8 of B ("fields missing: code, env, input"); those are gone. The
remaining failures are runs in flight and one stranded run of E.

`nrpic-ctx audit` (14:31Z): findings 4, all section 2 (files above 1 MB on branches); section 4
from wave 2b on: none; waves 1 and 2: core none x700, 'done' x72, 'finished' x11, 'cancelled' x6;
kb 'finished' x74; A 'failed (exit 1)' x2; B 'done' x48; C 'done' x5; D none x14.
`nrpic-run lint --all`: 1774 manifests, none unreadable.

## Self-tests (scratch repositories under scratch/harness/, never the live branches)

test_ctx 87/87; run-runs-config-tests: nrpic-env 15/15, nrpic-run 57/57, style 10/10, nrpic-stage
45/45, hooks 99/99, configuration 51/51, nrpic-fetch-arxiv 29/29, pre-commit 13/13. Logs in
`scratch/harness/logs/`.

## Open

- `nrpic-run submit` still refuses `orch` (decision 0016 item 2 names it as an owner of run ids);
  registering the orchestrator's own analysis runs needs `tracks/orch/runs/` and a decision on
  committing manifests on main while other agents commit there.
- core `requests-b-card-state` item 3: an executable per line of a batch list (not built).
- `nrpic-run finish`, `stop` and `lint` still tell hand-written manifests by the `schema` field
  only; a hand registration that copied the schema counts there as written by nrpic-run
  (`nrpic-stage` and `nrpic-run verify` use the wider rule of `H.hand_marker`).
- B's run B-20261115-164157-40b9f6d (outputs moved after `finish`) fails its checksums and is
  not hand-written: it needs the orchestrator's ruling, not the waiver.
