# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-28 ~02:25Z = 2026-11-27 18:25 PST, batch 35, session core-lead-35): a round
without AthenaK source change. **Candidate core-v0.9 is merged into `core/nrpic` and
checked on processors; it is NOT RELEASED until its card check has passed** (shared-queue
entry **q0094**, waiting). Release core-v0.8 is on main (tag on 01d4aeeb). Gate G2 of core
is NOT met (`stage/G2/OPEN.md`; CHECKLIST 13 PASS, 5 FAIL). Owner: core, branch
`core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Done in this session (journal: `JOURNAL.md`, entries from 2026-11-28T02:02Z)

1. **Merge**: `origin/core/faces-finder` (source session of batch 34a; journal
   `JOURNAL-faces-finder.md`) into `core/nrpic` at 8139c969, no conflict; `git diff
   ad54460e HEAD -- athenak/src` is empty. Serial build `.work/build_cpu_v09rc/src/athena`
   (sha256 b7a48e9a..., not published).
2. **Processor checks of the merged tree**, predictions written first (journal 02:02Z):
   R9 byte regression against `.work/build_cpu_v08` PASS 75 of 75 (run
   core-20261128-020122-3a1a3dd, figure -020936-0826227); T9 the branch's six tests again,
   compared byte for byte with the branch session's runs by the new
   `analysis/faces_finder/rerun_compare.py`: 416 files, 371 identical, 45 identical up to
   the run directory's name, verdicts equal (run -021251-d4575ac; the first pass
   -021119-fb199ef failed only on the scripts' own summary.json files: wall times and
   executable path); Q9 `restart_test.py` ALL OK (run -020910-9292e5d). Figures looked at.
3. **Card check q0086 was preempted**: `sacct -j 5544` PREEMPTED after 5 s while the queue
   listed it as done. Its run core-20261128-002929-335815e closed as stopped. Queued again:
   **q0094** (label core-ff-card2, priority 2, 0.2 card-hours, same list and executable).
4. **Records**: `RELEASE-v0.9.md` (first line says NOT RELEASED; processor evidence, T9
   table, how to judge the card check, executables to publish afterwards); `CHANGELOG.md`
   section core-v0.9 (which runs each change without an option touches; four finder
   options; not done: level faces between ranks, cost of the compensated deposit).
   `scratch/core/exe/core_faces-finder/READY` notes q0094.
5. **Release builds of core-v0.8** (clerk's request): `.work/build_cpu_v08` against
   `core_nrpic_v08/athena_cpu` 75 of 75 identical (V8, run core-20261128-020855-e27868f,
   figure -021505-7852e7f); the card build not compared by a run (reason and the command
   in `RELEASE-v0.8.md`, last section).
6. **Inbox**: A's finder requests answered by the source session (said so); A's outer
   faces (decision 0048 item 5): the core-v0.6 set `extrap_order 4, ghost_falloff,
   sbc_variant nonwave, sbc_speed metric` applies to its expanding ball, and the run that
   decides the cause is the face part of the line ratio at M/16 against M/32 with the set
   at faces 16, against faces at 32 (outbox 20261128T021000Z). F: "found" is the mass rule;
   column 10 is the integral of H; `hmean_tol` (100) is an abort test; v0.5 restarts under
   v0.8 untested, with a processor check that decides it (outbox 20261128T021500Z);
   `interfaces/finder_stop.md` section 2 has the new paragraph. Acknowledged inbox items
   28, 32, 33, 35, 36 and orch's finder-diagnostics note.

## Pending in the shared queue

| Queue id | Label | What | How to judge |
|---|---|---|---|
| q0094 | core-ff-card2 | card check of candidate core-v0.9 (8 cases, list `analysis/faces_finder/card.list`) | below |

When q0094's job has ended: `sacct -j <job>` must say COMPLETED (the queue still lists
preempted batch jobs as done; if PREEMPTED, close the run as stopped and `nrpic-queue
add` it again at priority 2). Then from `wt/core`: `harness/bin/nrpic-run finish <run>`,
and the registered `card_check.py` line written out in `RELEASE-v0.9.md` (section "Card
check"), against prediction K of `JOURNAL-faces-finder.md` entry 5. If it passes: rewrite
`RELEASE-v0.9.md` in the form of `RELEASE-v0.8.md` (first line "... CARD CHECK PASS"),
publish `scratch/core/exe/core_nrpic_v09/` (athena_cpu = `.work/build_cpu_v09rc`,
athena_cpu_omp and athena_gpu copied from `core_faces-finder`, an MPI build of the tree:
`.work/build_cpu_mpi_v09rc`, smoke test `analysis/release/mpi_smoke_v08.py`; COMMIT,
SHA256SUMS, READY), and write the request to the clerk in `tracks/core/outbox/` (merge,
tag on ad54460e, release builds, interface texts `level_faces.md`,
`restart_parameters.md`, `finder_box.md`, updated `finder_stop.md`, CLAUDE.md row).

Row 4 (from batch 27), done this session: q0059's run core-20261126-110234-a72e07c closed
(job 5378 COMPLETED on 2026-11-26; 0.6547 card-hours); fates run
core-20261128-021941-61b61a1: the 0.755 member does not collapse by 600 M, P13 holds for
both runs (member 400-450 M mean 0.9262 against 0.9638 at 250-300 M), bracket (0.7175,
0.726875) unchanged (`verify/LADDER.md` row 4, fourth reading; journal 02:22Z). Left: the
note (section III D of `note/main.tex`, `note/scripts/fig_row4_m8.py`, ledger, compile,
checker, read pages); P14 (joins) is not computed by `row4_fate.py`.

## What G2 still lacks (plain statement, unchanged)

1. Ladder row 3: the oblate collapse has no released component (core/oblate, unmerged).
2. Ladder row 4: a threshold that does not depend on the window (0.755 drifts to 0.80 of
   its equilibrium lapse by 600 M).
3. Three-way convergence (C2) on one coupled set-up.
4. Package items: reproducibility package (C6), REVIEW.md and SCOPE.md (C12).

## Files to read first

`STATUS.md`; `RELEASE-v0.9.md`; the last entries of `JOURNAL.md`; `CHANGELOG.md` section
core-v0.9; `JOURNAL-faces-finder.md` entries 5 and 6; `NEXT_SOURCE.md`; `stage/G2/OPEN.md`.

## Open with other owners

- orch/clerk: nothing to merge until q0094 has passed. The clerk's v0.8 request (release
  builds against core's builds) is answered in `RELEASE-v0.8.md`.
- A: may ask for a deck check of the face set over ~45 M; core's tests reach t = 40 only.
- F: may report the v0.5-to-v0.8 restart check (outbox 20261128T021500Z item 3).
- D: their excision-guard test (EG8, q0085) is theirs; their outcome comes to the inbox.

## Traps

- **The queue lists a preempted batch job as done**: always `sacct -j <job>` before
  reading a run (decision 0048 item 6; the correction of the tool may not be in force).
- `rerun_compare.py` replaces the old run id and the branch's build paths
  (`wt/core-s5/.work/build_cpu_ff`, `build_omp_ff`) by the new ones; for other pairs of
  builds edit `OLD_BUILDS`/`NEW_BUILD` or the comparison counts them as differing.
- `restart_test.py` labels its reference cuts "v0.7" in the figure whatever `--ref-exe`
  is (Q9 used core-v0.8).
- `nrpic-run submit` refuses a dirty worktree; `finish` commits by itself: do not commit
  by hand while a background finish is about to end. Runs registered in a helper worktree
  (core-s5 for faces-finder) have their manifests on that branch: merge first.
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/` (this session: `b35_*`).
