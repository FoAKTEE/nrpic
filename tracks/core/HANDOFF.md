# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21 23:31Z, batch 8, session core-lead-8; no source change, no card job):
gate G2 of core is NOT met (`stage/G2/OPEN.md`, first section; CHECKLIST 13 PASS, 5
FAIL: C1/C7 ladder rows 3 and 4 partial, C2 three-way convergence, C6 clean-export
verify of batch 8 fails only on the six row-4 chains still queued, C12 package documents). This session corrected the texts the fresh
verifier found, put the restart limit and the Gamma-driver step rule into OPEN.md,
named the pre-program run directories, and wrote core's working note.
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Six card chains are pending (ladder row 4, bisection level 1; from batch 5, untouched)

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

After the fates are judged, bring the note up to date: add the M/8 runs to
`note/scripts/fig_clusters.py` (or a new `fig_row4_m8.py`) and their numbers to
`note/scripts/ledger.py`, commit, run `note/scripts/run_all.py` as a registered run
(`note/README.md`, "How to rerun"), copy its `figures/` and `tables/` into `note/`,
edit section III D of `note/main.tex`, compile, run the checker, read the pages.

## Done in this session (batch 8)

- Verifier corrections (VERIFIER.md section 3): CHECKLIST C3 (Theta-norm2 is a
  proper-volume integral of Theta^2; pointwise max|Theta| 2.27e-7), `interfaces/
  scalar_field.md` test 1 (absolute vs relative frequency difference),
  `newtonian_mode.md` 5.2 (706 tracers), `id_solver.md` T1 and `id_solver2.md` C
  (measures), `verify/LADDER.md` row 2 (0.9986707). C16 PASS with the verifier's limit.
- OPEN.md items u (restart limit, decision 0027 item 3) and v (step rule with a
  Gamma-driver, 0027 item 2); REQUESTS_WAVE3.md section 5b, W31 (Track A's
  periodic-gamma-driver-step: gauge speeds in the step limit, `lapse_leak` x dt warning,
  `scripts/cpu_run.sh` footer); the cfl rule beside `dt_lightspeed` in `cosmo_amr.md`
  2.4. Track A's messages 9 and 11 of the inbox acknowledged.
- `verify/preprogram/` (README, INVENTORY.md, `inventory.py`; run
  core-20261121-231825-135474c): the old run directories of ladder rows 2-4 with sha256
  of inputs, executable copies, logs, histories.
- Working note `note/` (main.tex/pdf, 8 pages; WRITING_GUIDE.md, NOTATION.md one level
  up; figures and ledger by run core-20261121-232936-d979f1c). C14, C15 PASS.
- Outbox to orch 20261121T233031Z: carry the interface corrections into coord/INTERFACES.

## Files to read first

`tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md` (batch 8);
`tracks/core/stage/G2/OPEN.md` (first section, items u and v); `tracks/core/note/README.md`;
`tracks/core/interfaces/REQUESTS_WAVE3.md` sections 5, 5a, 5b (order of work for core-v0.7).

## Open with other owners

- orch: interface corrections into coord/INTERFACES (outbox 20261121T233031Z); waiver
  lines (outbox 20261121T204332Z); an analysis session for row 4.
- Inbox of core not read in this session (task scope): messages 1-8 and 10 of
  `nrpic-ctx inbox` (F wave-extraction-lmax; D lapse-leak-growth-data,
  newtonian-mode-edges; E a4res-claims-c1-c4; A bh1r-inte-deficit-two-levels; older).
- Track A: W31 accepted for core-v0.7; A runs `cfl_number = 0.5` meanwhile and will
  report its refined-mesh test.
- Track C: its drift package is the reason for M/8 (read its run (vi) beside the 0.755
  control). Track D: no `lapse_leak` around a black hole until W30.
- Branches core/clump-table (tip ff11719d), core/oblate (tip 4f01a81f), core/gauge-2
  (tip 61c8fc4d) merge main before core-v0.7.

## Traps

- `nrpic-run` builds the job environment itself (`build_env` reads no caller variable):
  a Slurm dependency cannot be passed through it; that is why the sequencer holds and
  releases instead.
- `refinement = static` leaves `num_levels` unused (AthenaK warns); the deck's levels
  come from its refined regions.
- `nrpic-ctx ack` commits by itself; `nrpic-stage verify` needs `--no-checksums` on
  core's 1480 runs; exit status 3 of AthenaK is the guard's stop; `runs/` in .gitignore
  hides `tracks/core/runs/` (a hand-written manifest needs `git add -f`).
- The clock: `date -u`. Temporary files of the lead: `scratch/core/tmp/lead_b8/` (this
  session), `lead_b5/` (the sequencer).
- The note's scripts check inputs by sha256 only where a run recorded one: wave-1 runs
  have none (31 inputs "not recorded" in the log); the pre-program files are checked
  against the inventory run.
