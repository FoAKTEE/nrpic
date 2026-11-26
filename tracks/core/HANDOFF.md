# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-26T03:18Z = 2026-11-25 19:18 PST, batch 23, session core-lead-23): a round
without AthenaK source change. **Nothing is half-done** except what the queue runs.
Release core-v0.7 is on main (tag 5f75e5b9). `core/nrpic` now holds `core/restart-finder`
(merge b755cdcf; source of the tree = 01d4aeeb of that branch) and is the candidate of
**core-v0.8, not released**: the release waits for the card check q0049.
Gate G2 of core is NOT met (`stage/G2/OPEN.md`, first section; CHECKLIST 13 PASS, 5 FAIL).
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Done in this session (journal entry 2026-11-26T02:25Z, predictions and outcomes)

1. **Queue order.** q0033 (0.755 member, row 4) removed and added again as **q0059**, same
   26 arguments (saved in `scratch/core/tmp/b23_q0033.json`), priority 2, `--after
   step-limit-card` (q0036, the check the dispatcher takes last). q0032 (0.755 control) was
   already in Slurm (job 5346): untouched. The four card checks (q0049, q0039, q0035, q0036)
   now come before any row-4 entry of core.
2. **Row 4 level 3**: q0030 (3dad12c) and q0031 (d2db1ed) closed (`nrpic-run finish`);
   fates run core-20261126-023040-b755cdc: 0.726875 STABLE by the 300-M rule (D = +0.0061),
   **bracket (0.7175, 0.726875)**; beyond 300 M every model to 0.73625 collapses (members
   180.5 ... 405.0 M, controls of 0.726875 and 0.73625 at 333.75 and 421.25 M). P10, P11,
   P12, P15 hold; P13 waits for 0.755; P14 of the member's join not computed. `verify/LADDER.md`
   row 4 "Level 3, second reading".
3. **Track A's PCS question** (answered, outbox 20261126T024622Z): test
   `analysis/deposit_levels/dep_levels.py`, run core-20261126-022953-21b8455 (three earlier
   attempts on record, failed on the reader, the emulation, the figure scale). The PCS/TSC
   error at a static level face is the documented rule (code = independent 1D emulation to
   1.1e-15); CIC with cell-centred particles is exact. Two defects found on the way, at the
   head of `NEXT_SOURCE.md`: item 0 `deposit_fine_shape` with CIC is not inert at a level face
   without a cap (+-12.5 per cent dipole); item 0b the compensation is not conservative
   across a level face (+0.13 per cent of the mass on the test).
4. **0042 item 4** (diagnostics after a restart): cause `parameter_input.cpp` 370-409; the
   workaround `athena -r <rst> -i add.athinput` works (run core-20261126-023323-c8fad52,
   prediction F1 held); source fix = `NEXT_SOURCE.md` item 1 with that test. Answered D, F
   and B (B's `restart-new-parameters` has the same cause); inbox items acked.
5. **core-v0.8 prepared on processors**: merge b755cdcf; serial build
   `scratch/core/b23_build_cpu/src/athena` (628 s); **R8 held**: byte regression 75 of 75
   identical with core-v0.7 (run core-20261126-024438-1fa17dd, figure -031446-af637b5);
   **Q8 held**: `restart_test.py` ALL OK (run core-20261126-024518-e1e16dc).
   `RELEASE-v0.8.md` written (first line REGRESSION PASS, "NOT RELEASED", card check
   PENDING); `CHANGELOG.md` heading of v0.8 and `OPEN.md` core-v0.7 items a, b state the merge.

## Pending in the shared queue (none waited for)

| Queue id | Label | Worktree | What | How to judge |
|---|---|---|---|---|
| q0049 | core-rf-card | wt/core-s4 | card check of core/restart-finder, K1-K5 | below |
| q0039 | core-v07-card | wt/core | card check K7 of v0.7 (22 cases) | `RELEASE-v0.7.md`, "Card checks pending" |
| q0035 | nl2-review-R5 | wt/core-s2 | reviewed level-2 card build | `verify/noise_level2_close/README.md` |
| q0036 | step-limit-card | wt/core-s3 | step-limit card smoke | `analysis/step_limit/HANDOFF.md` |
| q0032 | row4-l3-0p755-control | wt/core | job 5346, 0.755 control 300-600 M | row 4 below |
| q0059 | row4-l3-0p755-member | wt/core | 0.755 member 300-600 M, after q0036 | row 4 below |

**q0049, then the release** (`JOURNAL-restart-finder.md` entry 20, merged into this branch):

    cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main
    R=<run id that `harness/bin/nrpic-queue show q0049` names>; S=/data/haiyangw/nrpic/scratch/core
    harness/bin/nrpic-run finish $R
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check of core/restart-finder judged, K1-K5" -- python3 tracks/core/analysis/restart_finder/card_check.py --card $S/$R --cpu-restart $S/core-20261125-142556-a424739 --cpu-finder $S/core-20261125-141832-01d4aee --out '$NRPIC_RUN_DIR'

`card_check.py` has never read real card output: expect to debug it (wall time from "cpu
time used" in the logs). If K1-K5 hold: write `RELEASE-v0.8.md` (model `RELEASE-v0.7.md`; R8
and Q8 of this session are its processor evidence), build `.work/build_{cpu,gpu}_v08` from the
merged source in the main checkout only if the orchestrator asks (the release clerk did it for
v0.7), publish `scratch/core/exe/core_nrpic_v08/` (new directory; never replace one), ask orch
to merge and tag, and send the CLAUDE.md sentence (restart defects a, b fixed; finder
polishing; `ah_exc_max_growth`; figstyle without a date).

**Row 4**, when q0032 and q0059 have run (`nrpic-run finish` hashes 17-35 GB: background):

    S=/data/haiyangw/nrpic/scratch/core
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "row 4 M/8 level 3 complete: fates, P13" -- python3 tracks/core/verify/row4/row4_fate.py --out '$NRPIC_RUN_DIR' 0.605=$S/core-20261121-204230-3bcb118,$S/core-20261121-204235-0b25077 0.680=$S/core-20261121-204234-d010783,$S/core-20261121-204239-2be5ac2 0.69875=$S/core-20261123-020454-8fec6b2,$S/core-20261123-020456-884f550 0.7175=$S/core-20261123-020450-7e42037,$S/core-20261123-020452-e635a8e 0.726875=$S/core-20261124-130310-597d9ca,$S/core-20261125-180320-3dad12c 0.73625=$S/core-20261123-020458-dfc38d7+$S/core-20261125-225600-d2db1ed,$S/core-20261123-020500-9b192cd+$S/core-20261125-080049-dcc9ea1 0.755=$S/core-20261121-204232-f74c942+$S/<run of q0059>,$S/core-20261121-204237-ae00ca2+$S/core-20261126-021633-50968b9

Then P13 (journal 2026-11-24T13:05Z), the LADDER table, the note (section III D of
`note/main.tex`, `note/scripts/fig_row4_m8.py`, ledger, compile, checker, read pages).

## What G2 still lacks (plain statement)

1. Ladder row 3: the oblate collapse has no released component (core/oblate, unmerged).
2. Ladder row 4: a threshold that does not depend on the window. Level 3 says the 300-M
   bisection brackets "collapse within 300 M"; the drift (N- or cell-dependence) is open.
3. Three-way convergence (C2) on one coupled set-up.
4. Package items: reproducibility package (C6), REVIEW.md and SCOPE.md (C12).

## Files to read first

`STATUS.md`; the last entry of `JOURNAL.md`; `NEXT_SOURCE.md`; `JOURNAL-restart-finder.md`
entry 20; `RELEASE-v0.7.md`; `verify/LADDER.md` row 4; `stage/G2/OPEN.md`.

## Open with other owners

- A: new request in the inbox, `finder-false-accept-and-stall-p0l6` (2026-11-26 02:30Z), not
  read in this session.
- orch: outbox 20261125T121047Z (marker RULES text), 20261125T030800Z; the CLAUDE.md row of
  v0.8 when released.
- Inbox of core still unanswered (`harness/bin/nrpic-ctx inbox`): older items listed in the
  batch-17 handoff (B round 1; F chain-stray-resubmission, hnorm-transient-r8, hrna-pair-force,
  wave-extraction-lmax; D lapse-leak-growth-data, newtonian-mode-edges; E a4res-claims; A
  bh1r-inte-deficit-two-levels); `NEXT_SOURCE.md` places those a gate waits for.

## Traps

- The dispatcher runs q0039 (and q0059) in THIS worktree: keep it committed and never leave
  a merge in progress, or the entry waits.
- nrpic-run's local launcher refuses a test whose script names sbatch, srun, gpu_batch.sh or
  submit_chain.sh (fakes included): `tracks/core/tools/hand_run.py`.
- `nrpic-run finish` hashes every output file: background; it commits by itself.
- A row-4 continuation needs the release card build of core-v0.6 (`athena_resume.sh` checks
  its sha256).
- A parameter absent from a restart's stored input cannot be given on the command line of
  the continuation; give it with `-i <small file>` (run core-20261126-023323-c8fad52).
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/` (this session: `b23_*`).
