# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-25T12:30Z = 04:30 PST, batch 17, session core-lead-17): a round without
AthenaK source change. **Nothing is half-done.** Release core-v0.7 is on main (tag on
5f75e5b9, merge b399f946; executables `.work/build_{gpu,cpu}_v07`). Gate G2 of core is NOT
met (`stage/G2/OPEN.md`, first section; CHECKLIST 13 PASS, 5 FAIL).
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Done in this session (journal entry 2026-11-25T11:52Z, predictions and outcomes)

1. **Queue marker out of every job** (decision 0037 item 4): `scripts/{gpu_run.sh,
   gpu_batch.sh,submit_chain.sh,_athena_job.sh}` unset every `NRPIC_QUEUE_*` variable at
   their top (submit_chain.sh also in its sbatch call); `verify/row4/continue_chain.sh`
   tests its dispatch with `harness/bin/nrpic-queue check-dispatch`. Tests (no real job):
   `scripts/tests/test_queue_marker.py --old <scripts before> --out DIR` (fake Slurm of
   `harness/tests/rc_fixture.py`; control with the old scripts shows the leak) run
   core-20261125-120211-08f4fb9, and `scripts/tests/test_submit_chain.py` run
   core-20261125-120145-665b6a0, both TEST PASS, both **registered by hand** with
   `tracks/core/tools/hand_run.py` (nrpic-run's local launcher refuses any command whose
   script names sbatch or submit_chain.sh, fakes included). Told orch (outbox
   20261125T121047Z).
2. **Provenance of E's level-2 ablation executable** (decision 0038 item 3): the seven runs
   used athena_gpu 468109496c82... (source 6ca93cbabfe6, built 2026-11-22), verified on the
   copies in their own run directories. Record `tracks/core/EXE_PROVENANCE.md`; in the
   published directory `scratch/core/exe/core_noise-level2/` a `PROVENANCE` file and hard
   links `superseded/6ca93cba/`. E answered (outbox 20261125T120549Z), its request acked.
3. **Release builds**: `.work/build_cpu_v07` against the candidate `athena_cpu`: 75 of 75
   identical (core-20261125-115428-3670218, figure core-20261125-120456-07a671a);
   `RELEASE-v0.7.md` section "Release builds against the candidate". The release card
   build has no check (CUDA; `card_v07.list` can run it later).
4. **Row 4 level 3, two of six runs read** (q0028 run 597d9ca closed as stopped at
   405.25 M, its chain cut at its segment cap; q0029 run dcc9ea1 completed to 600 M):
   fates run core-20261125-120724-246d2a5; `verify/LADDER.md` row 4 has a "Level 3,
   partial" table. 0.726875 member: no collapse by 300 M, collapse 338.25 M. 0.73625
   control (STABLE by the rule): collapse 421.25 M. Bracket (0.7175, 0.73625) stands,
   0.726875 pending inside it. `row4_fate.py` now accepts `y=<member>,` (control not run).
5. `tracks/core/NEXT_SOURCE.md`: the list for the Fable source session (items 1-3:
   outputs that survive a restart, W2 + restart defects a, b; finder stopping rule and
   excision growth guard for D; figstyle without a creation date for E).
6. Answers: C-sidm and F-hills (restart on SIGTERM is in core-v0.7; C's drift data),
   outbox 20261125T121048Z; their requests acked.

## RULE (new): a published executable is never replaced in place

Every publication under `scratch/core/exe/` gets a directory name of its own (for example
`core_<branch>_<source commit 8>/`). A later build goes to a new directory; the old name
may get a `PROVENANCE` file pointing to the new one, never new binaries. Reason: run
manifests name the path and its sha256 (E's G2 run check failed on seven runs because
`core_noise-level2/athena_gpu` was rebuilt in place on 2026-11-24). Details
`tracks/core/EXE_PROVENANCE.md`.

## Pending in the shared queue (none waited for; all "waiting" at 12:10Z)

| Queue id | Label | What | How to judge |
|---|---|---|---|
| q0039 | core-v07-card | card check K7 of the merged card executable (22 cases) | below |
| q0035 | nl2-review-R5 | card run of the reviewed level-2 build | its package, `verify/noise_level2_close/README.md` |
| q0036 | step-limit-card | card smoke run of the step-limit build | its package, `analysis/step_limit/HANDOFF.md` |
| q0030 | row4-l3-0p726875-control | 0.726875 control, 0-600 M | row 4 below |
| q0031 | row4-l3-0p73625-member | 0.73625 member, 300-600 M (parent core-20261123-020458-dfc38d7) | row 4 below |
| q0032 | row4-l3-0p755-control | 0.755 control, 300-600 M (parent -204237-ae00ca2) | row 4 below |
| q0033 | row4-l3-0p755-member | 0.755 member, 300-600 M (parent -204232-f74c942) | row 4 below |

q0039, when `harness/bin/nrpic-queue show q0039` names a run and its `batch.list.status`
has 22 lines:

    cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main
    S=/data/haiyangw/nrpic/scratch/core; K7=<run id of q0039>
    harness/bin/nrpic-run finish $K7
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, new cases" -- python3 tracks/core/analysis/release/card_v07.py --card $S/$K7 --quick $S/core-20261125-023641-7a1c47d --out '$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, six cases of core-v0.6" -- python3 tracks/core/analysis/release/card_v06.py --card $S/$K7 --quick $S/core-20261121-130813-710b3cc --r2 $S/core-20261121-131250-f8df905 --out '$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, nine cases of core-v0.5" -- python3 tracks/core/analysis/release/card_v05.py --card $S/$K7 --cpu $S/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'

Each prints CARD PASS or CARD FAIL (prediction K7: journal entry 2026-11-25T02:12Z with its
amendment of 03:01Z). Then look at the figures, write the outcome into the journal, replace
"PENDING" in `RELEASE-v0.7.md` (third line and "Card checks pending"), in
`scratch/core/exe/core_nrpic_v07/READY` and in `stage/G2/OPEN.md` (core-v0.7 item i), and
send orch the sentence for the core-v0.7 row of CLAUDE.md (it now says "card check of the
merged card build pending at tagging: shared-queue entry q0039"). Known: the normalized
constraint columns of `*.cstat.hst` and `sr.sf.con.hst` differ between card and processors.

Row 4 level 3, when q0030-q0033 have run (`nrpic-queue show q00NN` gives the run ids;
`scripts/submit_chain.sh --status $S/<run>`; a chain cut at its cap after preemptions is
only cut: continue it with `nrpic-queue add --label <l> --priority 2 --cmd
'tracks/core/verify/row4/continue_chain.sh <run_id> <max_segments>'` after `DRY=1` of the
same line; `nrpic-run finish` hashes 17-35 GB per run: run it in the background):

    S=/data/haiyangw/nrpic/scratch/core
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
      --purpose "row 4 M/8 level 3: fates by the rule (JOURNAL 2026-11-21T20:26Z); P10-P15 (JOURNAL 2026-11-24T13:05Z)" -- \
      python3 tracks/core/verify/row4/row4_fate.py --out '$NRPIC_RUN_DIR' \
      0.605=$S/core-20261121-204230-3bcb118,$S/core-20261121-204235-0b25077 \
      0.680=$S/core-20261121-204234-d010783,$S/core-20261121-204239-2be5ac2 \
      0.69875=$S/core-20261123-020454-8fec6b2,$S/core-20261123-020456-884f550 \
      0.7175=$S/core-20261123-020450-7e42037,$S/core-20261123-020452-e635a8e \
      0.726875=$S/core-20261124-130310-597d9ca,$S/<run of q0030> \
      0.73625=$S/core-20261123-020458-dfc38d7+$S/<run of q0031>,$S/core-20261123-020500-9b192cd+$S/core-20261125-080049-dcc9ea1 \
      0.755=$S/core-20261121-204232-f74c942+$S/<run of q0033>,$S/core-20261121-204237-ae00ca2+$S/<run of q0032>

Then P10-P13 in full (journal), the "Level 3" table of `verify/LADDER.md`, the note
(`note/scripts/fig_row4_m8.py` PAIRS with continuations as "first+continuation", initial
data of 0.726875 from core-20261124-130236-68d4ee5; `note/scripts/ledger.py`; rerun the note
as `note/README.md` says; section III D of `note/main.tex`; compile, checker, read pages).
The note was NOT updated in batch 17 (it waits for the complete level 3).

## What G2 still lacks (plain statement)

1. Ladder row 3: the oblate collapse has no released component (core/oblate, unmerged;
   NEXT_SOURCE.md item 4); the prolate horizon-mass deficit (3 per cent) needs a third
   resolution.
2. Ladder row 4: a threshold that does not depend on the length of the runs. Level 3 so far:
   a STABLE model of the 300-M rule collapses by 421 M; the drift is the open item (its N-
   or cell-dependence; Track C sees the same in its King controls).
3. Three-way convergence (C2) on one coupled set-up.
4. Package items: reproducibility package (C6), REVIEW.md and SCOPE.md (C12).

## Files to read first

`tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md`;
`tracks/core/NEXT_SOURCE.md`; `tracks/core/RELEASE-v0.7.md`; `verify/LADDER.md` row 4;
`stage/G2/OPEN.md` (first section and core-v0.7).

## Open with other owners

- orch: the RULES sentence on the marker after the merge of core/nrpic, and whether
  fake-Slurm self-tests may be registered by the tool (outbox 20261125T121047Z); older:
  20261125T030800Z (release clerk, done by orch), 20261121T233031Z, 20261121T204332Z.
- Inbox of core still unanswered: items 1-10 (B round 1; F chain-stray-resubmission,
  hnorm-transient-r8, hrna-pair-force-slicing, wave-extraction-lmax; D lapse-leak-growth-data,
  newtonian-mode-edges, ah-excision-growth-guard; E a4res-claims-c1-c4; A
  bh1r-inte-deficit-two-levels), 14 (D finder-stopping-rule), 15 (B newton-fft-threaded: a
  processor test, NEXT_SOURCE "already served" list), 18 (E figstyle-reproducible-pdf).
  NEXT_SOURCE.md places each one that a gate waits for.
- Track C: core's row-4 drift data sent; C's N = 1e4 and 1e6 controls decide whether the
  drift is the scheme.

## Traps

- nrpic-run's local launcher refuses a test whose script names sbatch, srun,
  gpu_batch.sh or submit_chain.sh even when they are fakes: register such a test with
  `python3 tracks/core/tools/hand_run.py --purpose "..." -- <command>` (clean worktree;
  commit the manifest it writes) and say so in the journal.
- `nrpic-run finish` hashes every output file (17-35 GB per row-4 run): background; it
  commits by itself (path-limited).
- Card runs: only `harness/bin/nrpic-queue add`; an entry waits while the worktree is not
  clean: keep it committed.
- A row-4 continuation needs the release card build of core-v0.6 (`athena_resume.sh`
  checks its sha256); its chain script is the worktree's (now of core-v0.7, which does not
  count preempted attempts).
- `make_row4.py` names directories with y_c rounded to three digits (yc0p727 for 0.726875).
- `nrpic-ctx post --type` accepts info, request, proposal, interface-change, blocker,
  kb-request; use `--no-commit` and commit the outbox file yourself.
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/` (this session: `b17_*`).
