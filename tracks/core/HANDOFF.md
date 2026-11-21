# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21 20:50Z, batch 5, session core-lead-7; no source change): release
core-v0.6 is fully closed (its release card build passed, job 4810). Gate G2 of core is
NOT met (`stage/G2/OPEN.md`, first section). This session queued the first level of the
ladder-row-4 bisection on a static M/8 mesh: six card chains, of which two are eligible
and four held; a sequencer outside the session releases the held ones.
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Six card chains are pending (ladder row 4, bisection level 1)

Rule, measured quantities and predictions P1-P4 were written before the runs:
`tracks/core/JOURNAL.md`, entry of 2026-11-21T20:26Z. Package:
`tracks/core/verify/row4/` (deck `st_m8.athinput`, initial data `make_row4.py`, fate
analysis `row4_fate.py`, `sequencer.sh`). Initial data: run core-20261121-202643-d66c4ee.

| Model | Run id | First job | At 20:44Z |
|---|---|---|---|
| 0.605 kick | core-20261121-204230-3bcb118 | 4839 | eligible |
| 0.755 kick | core-20261121-204232-f74c942 | 4840 | eligible |
| 0.680 kick | core-20261121-204234-d010783 | 4841 | held |
| 0.605 control | core-20261121-204235-0b25077 | 4842 | held |
| 0.755 control | core-20261121-204237-ae00ca2 | 4843 | held |
| 0.680 control | core-20261121-204239-2be5ac2 | 4844 | held |

The sequencer (pid 2668479, own session; a copy of `verify/row4/sequencer.sh` in
`scratch/core/tmp/lead_b5/`) releases 4841, 4842, 4843, 4844 in that order whenever fewer
than two jobs named `core-...` are running or pending without a hold (two looks 90 s
apart). Log: `scratch/core/tmp/lead_b5/sequencer.log`. Stop it with
`touch /data/haiyangw/nrpic/scratch/core/tmp/lead_b5/sequencer.stop` or `kill 2668479`.
If it died with jobs still held: `scontrol release <jobid>` by hand, at most two core
jobs eligible. Each chain asks 2.0 card-hours (at most two 59-minute segments); about
0.6 card-hours per run is expected. A chain's job id changes per segment.

Read them (exact commands):

    cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main
    S=/data/haiyangw/nrpic/scratch/core
    R="core-20261121-204230-3bcb118 core-20261121-204232-f74c942 core-20261121-204234-d010783 core-20261121-204235-0b25077 core-20261121-204237-ae00ca2 core-20261121-204239-2be5ac2"
    cat $S/tmp/lead_b5/sequencer.log; squeue -h -u $(id -un) -o "%i %j %T %r" | grep core-
    for r in $R; do scripts/submit_chain.sh --status $S/$r; done
    # each chain whose status is DONE (or FAILED: look at $S/<run>/chain/ first):
    for r in $R; do harness/bin/nrpic-run finish $r; done
    # fates by the rule of 20:26Z (also works on runs still going: marked PROVISIONAL)
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
      --purpose "row 4 M/8 level 1: fates against controls (rule of JOURNAL 20:26Z)" -- \
      python3 tracks/core/verify/row4/row4_fate.py --out '$NRPIC_RUN_DIR' \
      0.605=$S/core-20261121-204230-3bcb118,$S/core-20261121-204235-0b25077 \
      0.680=$S/core-20261121-204234-d010783,$S/core-20261121-204239-2be5ac2 \
      0.755=$S/core-20261121-204232-f74c942,$S/core-20261121-204237-ae00ca2

Then look at `fig_row4_m8.png` of that run, write the outcomes of P1-P4 into the journal
(also the failed ones), the card time per M (P4: from `chain/` logs or the athena logs'
cpu time), and a row "Row 4, batch 5: M/8" in `verify/LADDER.md`. Next level by the rule:
the midpoint of (y_lo, y_hi) with its control, new initial data with
`make_row4.py --yc <mid>`, chains as above (two eligible at a time). An UNDECIDED middle
(0.680) is first continued with its control to 600 M (restarts are exact): a new
registered run with `--parent <old run>` that starts from the old run's 300 M restart file
with `time/tlim=600`, as Track C's drift (vi) did (`git show
track/C-sidm:tracks/C-sidm/drift/inputs/job_vi.list`); the restart needs the executable
that wrote it (`.work/build_gpu_v06/src/athena`, also copied into each run's `chain/`). Seen while testing the script on the
wave-2 M/4 runs (run core-20261121-204433-1c720e0, pairs chosen only to exercise the
code): their late central-lapse swings are larger than the 0.01 band of the rule, so a
100 M mean may be off by about 0.01; the rule stands as written, but say so if a member
lands within 0.01 of a class border.

## Done in this session

- Job 4810 judged (G6): PASS on both release card checks; the 1e-12 history bound of
  G6 (ii) refuted in the normalized constraint columns only (journal, RELEASE-v0.6.md,
  READY of `scratch/core/exe/core_nrpic_v06`).
- REQUESTS_WAVE3.md section 5a: W24 enters core-v0.7 as a mitigation
  (`lapse_leak_hole`, branch core/gauge-2 tip 61c8fc4d); W30 is the cure, with the three
  candidates of `JOURNAL-gauge-2.md` entry 11 (decision 0025 item 3).
- Outbox to orch: the nine run ids of decision 0023 item 5 with proposed WAIVERS lines.

## Files to read first

`tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md`;
`tracks/core/stage/G2/OPEN.md` (first section); `tracks/core/interfaces/REQUESTS_WAVE3.md`
sections 5 and 5a (order of work for core-v0.7).

## Open with other owners

- orch: waiver lines (outbox 20261121T204332Z); an analysis session for row 4.
- Track C: its drift package (`git show track/C-sidm:tracks/C-sidm/drift/README.md`) is the
  reason for M/8; its run (vi) to 680 M showed the M/8 control contracting steadily
  (alpha_c -0.022 by 680 M, no turn) - read it beside the 0.755 control.
- Track D: null tests and long runs around a black hole without `lapse_leak` until W30
  (decision 0025 item 3).
- Branches core/clump-table (tip ff11719d) and core/oblate (tip 4f01a81f) merge main
  before core-v0.7; core/gauge-2 (tip 61c8fc4d) is the W24 mitigation.

## Traps

- `nrpic-run` builds the job environment itself (`build_env` reads no caller variable):
  a Slurm dependency cannot be passed through it; that is why the sequencer holds and
  releases instead.
- `refinement = static` leaves `num_levels` unused (AthenaK warns); the deck's levels
  come from its refined regions.
- `nrpic-ctx ack` commits by itself; `nrpic-stage verify` needs `--no-checksums` on
  core's 1480 runs; exit status 3 of AthenaK is the guard's stop; `runs/` in .gitignore
  hides `tracks/core/runs/` (a hand-written manifest needs `git add -f`).
- The clock: `date -u`. Temporary files of the lead: `scratch/core/tmp/lead_b5/`.
