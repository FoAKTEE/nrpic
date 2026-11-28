# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-28 ~07:55Z = 2026-11-27 23:55 PST, batch 40, session core-lead-40): a round
without AthenaK source change. **Release core-v0.9 is final on `core/nrpic`: REGRESSION
PASS, CARD CHECK PASS; executables published in `scratch/core/exe/core_nrpic_v09/`.** The
release clerk merges `core/nrpic` into main and tags `core-v0.9` on ad54460e next. Release
core-v0.8 is on main (tag on 01d4aeeb). Gate G2 of core is NOT met (`stage/G2/OPEN.md`;
CHECKLIST 13 PASS, 5 FAIL). Owner: core, branch `core/nrpic`, worktree
`/data/haiyangw/nrpic/wt/core`.

## Done in this session (journal: `JOURNAL.md`, entries from 2026-11-28T07:27Z)

1. **Card check of core-v0.9**: q0094's job 5601 COMPLETED (sacct, 24 s, 0.0067
   card-hours). Run core-20261128-052151-e5a2d55 closed with `nrpic-run finish`. Judged by
   the registered analysis core-20261128-072820-d5fa2ca (`analysis/faces_finder/
   card_check.py`; prediction K of `JOURNAL-faces-finder.md` entry 5, restated before the
   analysis): CARD CHECK PASS, K1 to K4 held (card = processors to 2e-15 in the deposit,
   conservation 9.9e-16, finder masses to 1e-15, parameter added on restart). Figure looked at.
2. **Release records**: `RELEASE-v0.9.md` final (form of v0.8; section "For the release
   clerk" with the commands); `CHANGELOG.md` section core-v0.9 complete; interface texts
   ready to copy: `interfaces/level_faces.md`, `restart_parameters.md`, `finder_box.md`
   (section 0 new: finder decks without `puncture_setup` must name `start_time_<n>` and
   `stop_time_<n>`; decision 0049 item 3), `finder_stop.md` (two paragraphs added).
3. **Executables** `scratch/core/exe/core_nrpic_v09/`: athena_cpu (`.work/build_cpu_v09rc`,
   b7a48e9a), athena_cpu_mpi (`.work/build_cpu_mpi_v09rc`, a44b7c85), athena_cpu_omp and
   athena_gpu (copies of `core_faces-finder`, 2e31b69e and 20172cae); COMMIT,
   SHA256SUMS, READY. The branch directory `core_faces-finder/READY` points there.
4. **Outbox** 20261128T074000Z to A, D, F (executable for retests; what changes in their
   decks, read from their worktrees: 17 of A's nested-ball decks change from the first
   deposit; none of D's or F's); 20261128T074500Z to orch (clerk request, proposed
   CLAUDE.md row) and to C (start/stop answered). Inbox 32, 33 acknowledged.
5. **v0.8 release builds**: nothing more owed by my reading: the processor build was
   compared in batch 35 (75 of 75, run core-20261128-020855-e27868f); the card build was
   not, as for v0.7 (reason and the 0.15-card-hour command in `RELEASE-v0.8.md`; offered
   again in the orch outbox).

## Pending in the shared queue

None for core. (`nrpic-queue audit` lists q0028, an old row-4 chain handled in batch 17,
and q0086, superseded by q0094, as NOT COMPLETED; nothing to do.)

## What G2 still lacks (plain statement, unchanged)

1. Ladder row 3: the oblate collapse has no released component (core/oblate, unmerged).
2. Ladder row 4: a threshold that does not depend on the window (0.755 drifts to 0.80 of
   its equilibrium lapse by 600 M); bracket (0.7175, 0.726875); P14 (joins) uncomputed;
   the note section III D lacks the fourth reading.
3. Three-way convergence (C2) on one coupled set-up.
4. Package items: reproducibility package (C6), REVIEW.md and SCOPE.md (C12).

## Files to read first

`STATUS.md`; `RELEASE-v0.9.md`; the last entries of `JOURNAL.md`; `CHANGELOG.md` section
core-v0.9; `NEXT_SOURCE.md`; `stage/G2/OPEN.md`.

## Open with other owners

- orch/clerk: merge and tag core-v0.9 (outbox 20261128T074500Z); copy the four interface
  texts; CLAUDE.md row. A release card build can be checked with `card.list` and
  `card_check.py`.
- A: its constraint-floor retest (decision 0047 item 2(a)) and finder settings run on
  core-v0.9; members continued from core-v0.8 restart files change at the restart.
- D, F: nothing changes in their decks; core-v0.9 only for options added to running chains.
- Not done in core-v0.9, candidates for the next source session (`NEXT_SOURCE.md`): level
  faces between MPI ranks; the cost of the compensated deposit on a card and inside a
  coupled run; a continuation across core-v0.8 and core-v0.9 executables [TO VERIFY].

## Traps

- **The queue lists a preempted batch job as done** under the old rule: always `sacct -j
  <job>` before reading a run (`nrpic-queue audit` lists such entries).
- `restart_test.py` skips `rst/` in its comparisons: it does not show that restart files
  of two executables are byte-identical.
- `rerun_compare.py` replaces the old run id and the branch's build paths by the new ones;
  for other pairs of builds edit `OLD_BUILDS`/`NEW_BUILD`.
- `nrpic-run submit` refuses a dirty worktree; `finish` commits by itself.
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/`.
