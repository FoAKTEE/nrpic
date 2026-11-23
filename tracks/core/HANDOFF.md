# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-23 02:10Z, batch 10a, session core-lead-10a; analysis round, no AthenaK
source change): gate G2 of core is NOT met (`stage/G2/OPEN.md`, first section;
CHECKLIST 13 PASS, 5 FAIL: C1/C7 ladder rows 3 and 4 partial, C2 three-way convergence,
C6 reproducibility package, C12 package documents). This session closed the six row-4
chains of batch 5, judged them by the rule written before the runs, found the cluster
stability threshold on cells of M/8 BRACKETED between y_c = 0.680 and 0.755, queued the
next level, rebuilt the working note, fixed the footer of `scripts/cpu_run.sh` and
answered Track A and the knowledge base.
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Six card chains are pending (ladder row 4 on M/8, level 2)

Rule: `tracks/core/JOURNAL.md`, entry 2026-11-21T20:26Z (unchanged). Predictions P5-P9
and the design (midpoint 0.7175 plus both points of the level after it, run together):
entry 2026-11-23T02:05Z. Package `tracks/core/verify/row4/`. Initial data: run
core-20261123-020409-4fae8fb.

| Model | Run id | First job | At 02:05Z |
|---|---|---|---|
| 0.7175 member | core-20261123-020450-7e42037 | 4923 | eligible |
| 0.7175 control | core-20261123-020452-e635a8e | 4924 | eligible |
| 0.69875 member | core-20261123-020454-8fec6b2 | 4925 | held |
| 0.69875 control | core-20261123-020456-884f550 | 4926 | held |
| 0.73625 member | core-20261123-020458-dfc38d7 | 4927 | held |
| 0.73625 control | core-20261123-020500-9b192cd | 4928 | held |

The sequencer (pid 3075029, own session; a copy of `verify/row4/sequencer.sh` in
`scratch/core/tmp/lead_b10a/` whose stop file is `scratch/core/tmp/lead_b10a/
sequencer.stop`) releases 4925-4928 in that order whenever fewer than two `core-...` jobs
are running or pending without a hold. Log `scratch/core/tmp/lead_b10a/sequencer.log`.
If it died with jobs still held: `scontrol release <jobid>` by hand, two core jobs
eligible at most. Each chain asks 2.0 card-hours; level 1 measured 0.63 per run, one
segment each. Seven jobs of other owners were ahead at 02:05Z.

Read them (exact commands):

    cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main
    S=/data/haiyangw/nrpic/scratch/core
    R="core-20261123-020450-7e42037 core-20261123-020452-e635a8e core-20261123-020454-8fec6b2 core-20261123-020456-884f550 core-20261123-020458-dfc38d7 core-20261123-020500-9b192cd"
    cat $S/tmp/lead_b10a/sequencer.log; squeue -h -u $(id -un) -o "%i %j %T %r" | grep core-
    for r in $R; do scripts/submit_chain.sh --status $S/$r | head -1; done
    # finish hashes about 17 GB per run (2-3 minutes each): run it in the background
    for r in $R; do harness/bin/nrpic-run finish $r; done
    # fates of all six models of levels 1 and 2 (the bracket is formed from all of them)
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
      --purpose "row 4 M/8 levels 1+2: fates against controls (rule of JOURNAL 2026-11-21T20:26Z)" -- \
      python3 tracks/core/verify/row4/row4_fate.py --out '$NRPIC_RUN_DIR' \
      0.605=$S/core-20261121-204230-3bcb118,$S/core-20261121-204235-0b25077 \
      0.680=$S/core-20261121-204234-d010783,$S/core-20261121-204239-2be5ac2 \
      0.69875=$S/core-20261123-020454-8fec6b2,$S/core-20261123-020456-884f550 \
      0.7175=$S/core-20261123-020450-7e42037,$S/core-20261123-020452-e635a8e \
      0.73625=$S/core-20261123-020458-dfc38d7,$S/core-20261123-020500-9b192cd \
      0.755=$S/core-20261121-204232-f74c942,$S/core-20261121-204237-ae00ca2

Then look at its `fig_row4_m8.png`, write P5-P9 outcomes into the journal (failed ones
too), add a "Level 2" table to `verify/LADDER.md` row 4, add the six runs to
`note/scripts/fig_row4_m8.py` (PAIRS) and their rows to `note/scripts/ledger.py`, commit,
rerun the note (`note/README.md`, "How to rerun"), copy `figures/` and `tables/`, edit
section III D of `note/main.tex`, compile, run the checker, read the pages. An UNDECIDED
member inside the bracket is first continued with its control to 600 M from its 300 M
restart file (restarts need the executable that wrote it; `--parent <old run>`).

## Done in this session (batch 10a)

- Six chains of batch 5 closed (`nrpic-run finish`), fates run
  core-20261123-020318-e952741: 0.605 member collapses (t_c 180.5 M, AH 188 M), its
  control moves outward; 0.680 member and control collapse (219.5 M, 251.5 M); 0.755
  stays (D = +0.0016). Bracket 0.680-0.755, valid. P1, P4 hold; P2 partly refuted
  (stable controls drift inward 0.026); P3 refuted. LADDER row 4 and its summary row.
- Working note: new `note/scripts/fig_row4_m8.py` (Fig. 5), 13 ledger rows, section III D,
  abstract and summary; run core-20261123-020543-eb1cd2a; 9 pages, checker clean.
- Stage G2: OPEN.md item 2 and item 4, CHECKLIST C1 and C7; `nrpic-stage verify`
  (VERIFY_RESULTS.md) and `report` rerun (STAGE_REPORT.md).
- `scripts/cpu_run.sh`: footer fixed (Track A request iii; W31 item iii DONE); stub test
  in the journal entry 2026-11-23T01:50Z.
- Outbox 20261123T020802Z: answer to Track A (step limit: W31 (i) for core-v0.7, rule
  cfl <= 0.6 meanwhile, (ii) no date, (iii) done); answer to kb (M23 symbol is
  NrpicWriteHistory, `nco` dead and kept for checksums, candidates for M18 = id_solver T1/T3,
  M20, M25 = dust collapse, M19 stays claimed, M24 = Track A's periodic_diag).

## Files to read first

`tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md` (batch 10a);
`tracks/core/stage/G2/OPEN.md` (first section, item 2); `tracks/core/verify/LADDER.md`
row 4; `tracks/core/interfaces/REQUESTS_WAVE3.md` sections 5, 5a, 5b (order of work for
core-v0.7).

## Open with other owners

- orch: interface corrections into coord/INTERFACES (outbox 20261121T233031Z); waiver
  lines (outbox 20261121T204332Z); merge core/nrpic (carries the cpu_run.sh fix).
- Inbox of core still unacknowledged: messages 1-8 and 103 of `nrpic-ctx inbox` (B round1
  findings; F chain-stray-resubmission, hnorm-transient-r8, hrna-pair-force-slicing,
  wave-extraction-lmax; D lapse-leak-growth-data, newtonian-mode-edges; E
  a4res-claims-c1-c4; A bh1r-inte-deficit-two-levels) and a new one from D that arrived
  at 02:11Z, `ah-excision-growth-guard` (not read in this session). kb's paper-code-links
  answered and acknowledged.
- Track A: W31 (i) for core-v0.7; A reports its refined-mesh test at cfl 0.5.
- Track C: the M/8 bracket bears on its threshold scan (block A on M/8); its drift run (vi)
  beside the 0.755 control (both drift inward).
- Branches core/clump-table (tip ff11719d), core/oblate (tip 4f01a81f), core/gauge-2
  (tip 61c8fc4d) merge main before core-v0.7.

## Traps

- `nrpic-run finish` hashes every output file (about 17 GB per row-4 run): run it in the
  background; it commits by itself, so do not commit at the same moment.
- `nrpic-run` builds the job environment itself: a Slurm dependency cannot be passed
  through it; that is why the sequencer holds and releases instead.
- `make_row4.py` names directories with y_c rounded to three digits (yc0p699 for
  0.69875); the files inside carry the exact value.
- `nrpic-ctx post --type` accepts info, request, proposal, interface-change, blocker,
  kb-request (not "answer"); `nrpic-ctx ack` commits by itself; `nrpic-stage verify`
  needs `--no-checksums` on core's 1500 runs.
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/lead_b10a/` (this session, sequencer).
