# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (signed 2026-11-20).
Its G1 package is complete for the independent gate review: all 18 items judged PASS by the
lead of batch 3 (A4' adopted by decision 0021; the note's G1 products exist); G1 is not passed
until orch's review. G2 has begun: the USR case ran on the cards at 64^3-256^3 (package `usr`).

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show

Packages still in progress (left alone by the lead of batch 3):
- `window` (G2, window sensitivity L9): card job 4740 ran on 2026-11-20 (run
  E-20261120-222424-0eb754b; the lead of batch 3 closed its manifest with `nrpic-run finish`,
  721 files checksummed). Remains: `window/scripts/analyse_window.py` (committed) against the
  predictions W1-W8 of `window/JOURNAL.md` entry 1, figures, README. Processors only.
- `a4res` (check of core's resolution explanation for strict A4): a helper session of batch 3
  worked on it in this worktree at the same time as the lead (commits c4061303, b23055be,
  94dfa93e, aed608d2: predictions in `a4res/JOURNAL.md` entry 3, analysis script, README) and
  submitted card job 4798 (run E-20261121-131000-b23055b, 24 SR runs at 64^3/128^3, pending at
  13:30Z). Its own report says what remains; the lead of batch 3 did not review it. When the job
  has run: `nrpic-run finish E-20261121-131000-b23055b`, then the analysis of `a4res/scripts/`.

Then, depending on answers (outbox of 2026-11-21 13:10Z):
- orch schedules the G1 gate review (`outbox/*__to-orch__g1-package-complete.md`); the reviewer
  reads `stage/G1/{STATUS,CHECKLIST,OPEN,VERIFIER}.md` and `stage/REVIEW-wave3.md` (B4: the
  ledger cross-check, 13 rows track-only).
- orch rules on U-A2' (U-A2 at 256^3 on the odd part of a mirrored pair) and U-A4' (halving on
  floor-corrected parts) (`outbox/*__to-orch__usr-acceptance-after-data.md`); then write the
  USR criteria into `spec/scope/SCOPE.md` and start `stage/G2/` (`nrpic-stage collect
  E-stoch-inf G2`).
- Card: P256 on the release card build `.work/build_gpu_v05/src/athena` with
  `ladder/inputs/jobA.list` (0.5 card-hours) against E-20261115-172618-f948386 (risk R1, G1
  reservation 1). USR runs on the release core-v0.5 (contains scalar-3).
- core answers the lockstep request (`outbox/*__to-core__lockstep-record-substep.md`).

Files to read first: `STATUS.md`; `stage/G1/STATUS.md`, `OPEN.md`; `stage/REVIEW-wave3.md`
Part B; `usr/README.md` (Results, Requests) and `usr/JOURNAL.md` entries 9-15; `RISKS.md`
(R1, R7-R9, R17, R19, R21, R22); `JOURNAL.md` (last entry).

Decisions pending: G1 sign-off (orch, after an independent review); U-A2'/U-A4' (orch);
whether "the USR case is reproduced" (owner, at the G2 package, after window and resolution).

Traps:
- `nrpic-stage verify` fails on `runs` while a card job of a package is "submitted" (now 4798 of
  `a4res`) and on `clean` while a helper has uncommitted files; never commit or delete another
  package's files to silence it.
- Executables: release core-v0.5 (`.work/build_{gpu,cpu}_v05`) contains scalar-2 and scalar-3;
  the G1 SR runs used `core_scalar-2` a58e95b, the USR card runs `core_scalar-3` 5cc2821
  (scouting). No SR/USR run has used the threaded processor build `athena_cpu_omp` of
  core-v0.5 yet (its READY tests the deposit): compare it with the serial build first. The guard `<z4c_guard>` is on by default in core-v0.5 (exit status 3).
- Pair dumps of two runs only at equal recorded times (|dt| <= 1e-9) (the "385" came from this).
- Cold 128^3-256^3 dumps: read sequentially (seek + fromfile), never through numpy's memmap; two
  256^3 runs read together take about 50-70 s per dump when the disk is shared.
- `<abs M/[M]>` of the record is not even in s late in USR (U256 and U256m differ at 7e-4 at
  N_f); compare pairs on the dumps' odd and even parts, not on record ratios.
- Large figure PDFs stay in run directories; commit PNGs. `note/main.pdf` (1.3 MB) is exempt
  from the 1 MB guideline (decision 0021 item 3).
- Commit path-limited (`git commit -- <paths>`); `nrpic-run finish` and `nrpic-ctx post/ack`
  commit by themselves.
- `$NRPIC_RUN_DIR` in a command: inside `bash -c '...'` (RULES.md). A local `nrpic-run submit`
  blocks until the run ends: never wrap it in `timeout`.
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  verification suite 834-860, context protocol 957-1004, M11 544-547.
