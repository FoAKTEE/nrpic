# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-26 ~13:00Z = 05:00 PST, batch 27, session core-lead-27): a round without
AthenaK source change. **Release core-v0.8 is final on `core/nrpic` and waits for the
release clerk** (merge into main, tag on the source commit 01d4aeeb, release builds
`.work/build_{cpu,gpu}_v08`, CLAUDE.md rows; request in outbox 20261126T115635Z).
Gate G2 of core is NOT met (`stage/G2/OPEN.md`, first section; CHECKLIST 13 PASS, 5 FAIL).
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Done in this session (journals: `JOURNAL-restart-finder.md` entries 21-23, `JOURNAL.md`
entries 2026-11-26T11:55Z to 12:15Z and the last one, `JOURNAL-step-limit.md` entry 17)

1. **q0049 judged; core-v0.8 final.** Card run core-20261126-070946-7971fde (job 5364;
   manifest merged from `core/restart-finder` and closed here), judged by
   core-20261126-114747-a6f2385 (the first pass -114526-2b1f001 failed on the reader:
   tables of 5 and 7 columns compared by shape; fixed in `card_check.py`). K1, K2, K4, K5
   held; K3 held for the polished and tight finder rules (card = processors within
   3.3e-16) and FAILED for `mass_tol` 1e-5 without polishing (8.8e-6, two accepts of
   sixteen differ). Verdict [JUDGEMENT]: PASS for what the release changes; the failure
   concerns the unchanged rule of core-v0.7 and is a warning in the interface text.
   Cost per finder search on a card: 0.33 s for 100 polishing iterations.
   `RELEASE-v0.8.md`, `CHANGELOG.md` (section core-v0.8 with card check and "not done"),
   `interfaces/restart_outputs.md` and `finder_stop.md` (headers say "ready to be copied"),
   `stage/G2/OPEN.md` (new top section; restart defects a, b closed on one rank).
2. **Executables published** in the new directory `scratch/core/exe/core_nrpic_v08/`
   (COMMIT, SHA256SUMS, READY with recommended values): athena_cpu (b23 serial build),
   athena_cpu_mpi (built this session, `.work/build_cpu_mpi_v08rc`), athena_cpu_omp and
   athena_gpu (copies of `core_restart-finder`, same tree). MPI smoke test
   core-20261126-115451-893a30e: M1, M2 held (one rank = serial byte for byte; two
   ranks = one rank, 0.0).
3. **core-v0.7 card checks**: K7 CARD PASS (q0039 run core-20261126-045719-019b478; analyses
   -115658-8af7dd7, -115708-140bafa, -115725-9a8d381); step-limit q0036 (run
   -080805-3a9a349, analysis -121103-1070457): P4a, P4c held, P4b held in its test and
   failed in its time; level-2 R5 q0035 (run -040704-5c98bee, analysis -115933-9fb0e47):
   outcome in the last entry of `JOURNAL.md` and `JOURNAL-noise-level2.md` entry 18.
   `RELEASE-v0.7.md` has a section "Card checks (judged 2026-11-26)".
4. **Row 4**: q0032 closed (core-20261126-021633-50968b9, 0.6403 card-hours); fates run
   core-20261126-121143-aaae1b7: bracket (0.7175, 0.726875) unchanged; 0.755 control no
   collapse by 600 M, drift 0.9640 -> 0.9345 -> 0.8022 (50-M means at 250-300, 400-450,
   550-600 M); P13 holds for the control. `verify/LADDER.md` row 4 "third reading".
5. **Messages**: orch (release v0.8 ready, CLAUDE.md row words and Machine sentence; and
   the v0.7 row words, outbox of this session), D (executable and values for the guard
   test and polishing), F (executable and values for polishing; moving-puncture polishing
   untested).

## Pending in the shared queue (none waited for)

| Queue id | Label | What | How to judge |
|---|---|---|---|
| q0059 | row4-l3-0p755-member | job 5378, 0.755 member continued 300-600 M | below |

When q0059 has run (`nrpic-run finish` hashes about 17 GB: start it in the background):

    S=/data/haiyangw/nrpic/scratch/core
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "row 4 M/8 level 3 complete: fates, P13" -- python3 tracks/core/verify/row4/row4_fate.py --out '$NRPIC_RUN_DIR' 0.605=$S/core-20261121-204230-3bcb118,$S/core-20261121-204235-0b25077 0.680=$S/core-20261121-204234-d010783,$S/core-20261121-204239-2be5ac2 0.69875=$S/core-20261123-020454-8fec6b2,$S/core-20261123-020456-884f550 0.7175=$S/core-20261123-020450-7e42037,$S/core-20261123-020452-e635a8e 0.726875=$S/core-20261124-130310-597d9ca,$S/core-20261125-180320-3dad12c 0.73625=$S/core-20261123-020458-dfc38d7+$S/core-20261125-225600-d2db1ed,$S/core-20261123-020500-9b192cd+$S/core-20261125-080049-dcc9ea1 0.755=$S/core-20261121-204232-f74c942+$S/<run of q0059>,$S/core-20261121-204237-ae00ca2+$S/core-20261126-021633-50968b9

Then the member half of P13 (journal 2026-11-24, `JOURNAL.md` line ~1700), the LADDER table,
the note (section III D of `note/main.tex`, `note/scripts/fig_row4_m8.py`, ledger, compile,
checker, read pages).

## What G2 still lacks (plain statement)

1. Ladder row 3: the oblate collapse has no released component (core/oblate, unmerged).
2. Ladder row 4: a threshold that does not depend on the window: every model to 0.73625
   collapses by 421 M and 0.755 drifts to 0.80 of its equilibrium lapse by 600 M.
3. Three-way convergence (C2) on one coupled set-up.
4. Package items: reproducibility package (C6), REVIEW.md and SCOPE.md (C12).

## Files to read first

`STATUS.md`; the last entries of `JOURNAL.md`; `RELEASE-v0.8.md`; `NEXT_SOURCE.md` (items 0,
0b, 1 for the next Fable source session); `verify/LADDER.md` row 4; `stage/G2/OPEN.md`.

## Open with other owners

- orch: merge and tag core-v0.8 (outbox 20261126T115635Z); CLAUDE.md rows of v0.7 and v0.8;
  older outbox 20261125T121047Z (marker RULES text), 20261125T030800Z.
- D: their long card test of the guard (ES-FL to 240 M) with `ah_exc_max_growth`; outcome to
  core's inbox.
- A: inbox request `finder-false-accept-and-stall-p0l6` (2026-11-26 02:30Z) not read yet;
  the card-check result (unpolished rule differs between builds) is likely relevant to it.
- Inbox of core still unanswered (`harness/bin/nrpic-ctx inbox`): older items in the
  batch-17 handoff; `NEXT_SOURCE.md` places those a gate waits for.

## Traps

- Runs registered in a helper worktree (core-s2, s3, s4) have their manifests on that
  branch: merge the registration commit into `core/nrpic` before `nrpic-run finish` here
  (this session: 895e18ac, 4c17f531, 11a33507).
- `nrpic-run submit` refuses a dirty worktree; `finish` commits by itself: do not commit
  by hand while a background finish is about to end.
- `card_review.py` reads Track E's dumps with small reads: about 20 minutes on this
  filesystem.
- nrpic-run's local launcher refuses a test whose script names sbatch, srun, gpu_batch.sh
  or submit_chain.sh (fakes included): `tracks/core/tools/hand_run.py`.
- A row-4 continuation needs the release card build of core-v0.6 (`athena_resume.sh`
  checks its sha256).
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/` (this session: `b27_*`).

## Source session faces-finder (batch 34a, 2026-11-27 PST), written by that session on branch core/faces-finder

Not merged into `core/nrpic`. Everything is in `tracks/core/JOURNAL-faces-finder.md`
(entries 1 to 6), the three interface proposals `interfaces/level_faces.md`,
`restart_parameters.md`, `finder_box.md`, the top section of `CHANGELOG.md`, and the READY
of `/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/` (source ad54460e).
- Done on processors: items 0, 0b, 1 of `NEXT_SOURCE.md` and the finder in periodic boxes;
  byte regression against core-v0.8 PASS 75 of 75 (run core-20261128-000404-015d78b).
- **Pending: the card check, shared-queue entry q0086** (label core-ff-card). How to judge
  it: journal entry 6. Until then the card executable is untested.
- For the maintainer's merge: the lines of shared files are listed at the end of journal
  entry 6; `tracks/core/analysis/restart_diag/diag_restart.py` now expects case a to
  start (`--expect v08` keeps the old expectation).
- Outbox of this session: three messages of 2026-11-28T00:13Z (A, D, F).
- The finder's failure in Track A's boxes is the default flow function; `flow = shear`
  cures it with release core-v0.8 already (`finder_box.md` sections 1 and 2).
