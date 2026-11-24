# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-24, batch 11, session core-lead-11; analysis round, no AthenaK source
change): gate G2 of core is NOT met (`stage/G2/OPEN.md`, first section; CHECKLIST 13
PASS, 5 FAIL: C1/C7 ladder rows 3 and 4 partial, C2 three-way convergence, C6
reproducibility package, C12 package documents). This session closed the six level-2
chains of ladder row 4 on cells of M/8, judged them by the rule written before the runs,
found collapse within 300 M BRACKETED between y_c = 0.7175 and 0.73625, saw that the
surviving pairs drift inward steadily (so the bracket may be set by the 300-M window),
queued level 3 to test that, rebuilt the working note, recorded T5 of branch
core/noise-level2 (PASS on the card, run by Track E), and posted a follow-up to Track A
(step limit in work) and a correction to kb (link M18).
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## What G2 still lacks (plain statement)

1. Ladder row 3: the oblate collapse has no released component (branch core/oblate,
   unmerged), and the prolate horizon-mass deficit (3 per cent) needs a third resolution.
2. Ladder row 4: a stability threshold that does not depend on the length of the runs.
   Collapse within 300 M is bracketed on M/8 (0.7175-0.73625), but the surviving pairs
   drift towards collapse; level 3 says whether they collapse by 600 M. Then the
   threshold (or the drift rate) at a second cell size or particle number.
3. Three-way convergence (C2) on one coupled set-up (particle number, cell size, gauge
   together); each direction is shown today on a different set-up.
4. Package items: the reproducibility package (C6: the run check fails while chains are
   open; rows 2 and 4 rest in part on pre-program directories without manifests) and the
   package documents (C12: REVIEW.md, SCOPE.md).

## Six card chains are pending (ladder row 4 on M/8, level 3)

Rule: `tracks/core/JOURNAL.md`, entry 2026-11-21T20:26Z (unchanged; it reads t <= 300 M).
Predictions P10-P15 and the design: entry 2026-11-24T12:51Z, section "Level 3".
Package `tracks/core/verify/row4/`. Initial data of 0.726875: run
core-20261124-130236-68d4ee5.

| Model | Run id | Parent (300-M restart) | First job |
|---|---|---|---|
| 0.726875 member, 0-600 M | core-20261124-130310-597d9ca | - | 5154 eligible |
| 0.73625 control, 300-600 M | core-20261124-130321-ed96d4d | core-20261123-020500-9b192cd | 5155 eligible |
| 0.726875 control, 0-600 M | core-20261124-130340-31cf5e8 | - | 5156 held |
| 0.73625 member, 300-600 M | core-20261124-130347-7d6a10d | core-20261123-020458-dfc38d7 | 5157 held |
| 0.755 control, 300-600 M | core-20261124-130356-d9d09bf | core-20261121-204237-ae00ca2 | 5158 held |
| 0.755 member, 300-600 M | core-20261124-130406-09319a0 | core-20261121-204232-f74c942 | 5159 held |

Each chain asks 1.97 card-hours (two segments); 11.82 asked, about 5.1 expected (7.5 s
of card time per M). The continuations run `verify/row4/athena_resume.sh` (release card
build of core-v0.6, copied as chain/nrcr-<hash>; the first segment starts with `-r` from
the parent's `rst/st.00015.rst`). Sequencer pid 3904230 (own session; a copy of
`verify/row4/sequencer.sh` in `scratch/core/tmp/lead_b11/`; stop file
`scratch/core/tmp/lead_b11/sequencer.stop`; log `sequencer.log` there, a "waiting" line
every 15 min) releases 5156-5159 in that order when fewer than two core jobs are
eligible. If it died with jobs still held: `scontrol release <jobid>` by hand, two core
jobs eligible at most. At 13:04Z seven jobs of other owners were ahead.

Read them (exact commands):

    cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main
    S=/data/haiyangw/nrpic/scratch/core
    R="core-20261124-130310-597d9ca core-20261124-130321-ed96d4d core-20261124-130340-31cf5e8 core-20261124-130347-7d6a10d core-20261124-130356-d9d09bf core-20261124-130406-09319a0"
    cat $S/tmp/lead_b11/sequencer.log; squeue -h -u $(id -un) -o "%i %j %T %r" | grep core-
    for r in $R; do scripts/submit_chain.sh --status $S/$r | head -1; done
    # a chain cut by its segment cap after a preemption ends FAILED although it is only cut:
    # continue it from its own newest restart (re-run its submit_chain start command on the
    # same run directory, or a new registered run with --parent), never repeat it
    # finish hashes 17-35 GB per run (8-15 minutes each when others hash too): background
    for r in $R; do harness/bin/nrpic-run finish $r; done
    # fates of all seven models, continuations joined with '+'
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
      --purpose "row 4 M/8 levels 1-3: fates against controls (rule of JOURNAL 2026-11-21T20:26Z); P10-P15 of JOURNAL 2026-11-24" -- \
      python3 tracks/core/verify/row4/row4_fate.py --out '$NRPIC_RUN_DIR' \
      0.605=$S/core-20261121-204230-3bcb118,$S/core-20261121-204235-0b25077 \
      0.680=$S/core-20261121-204234-d010783,$S/core-20261121-204239-2be5ac2 \
      0.69875=$S/core-20261123-020454-8fec6b2,$S/core-20261123-020456-884f550 \
      0.7175=$S/core-20261123-020450-7e42037,$S/core-20261123-020452-e635a8e \
      0.726875=$S/core-20261124-130310-597d9ca,$S/core-20261124-130340-31cf5e8 \
      0.73625=$S/core-20261123-020458-dfc38d7+$S/core-20261124-130347-7d6a10d,$S/core-20261123-020500-9b192cd+$S/core-20261124-130321-ed96d4d \
      0.755=$S/core-20261121-204232-f74c942+$S/core-20261124-130406-09319a0,$S/core-20261121-204237-ae00ca2+$S/core-20261124-130356-d9d09bf

The script classifies by the rule (300 M) and prints `t_c_all` (collapse over the whole
record) and writes 50-M window means (`windows_50M` in `row4_fate.json`) for P11-P13.
P14 (join without a jump): compare the continuation's first record of `st.nrpic.hst`
(column 13) with its parent's record at 300 M. P15: "cpu time used" in the chain logs.
Then: look at `fig_row4_m8.png`, write P10-P15 outcomes into the journal (failed ones
too), add a "Level 3" table to `verify/LADDER.md` row 4, add the level-3 pairs to
`note/scripts/fig_row4_m8.py` (PAIRS; continuations as "first+continuation"; initial
data of 0.726875 from core-20261124-130236-68d4ee5: add it to the models loop) and rows to
`note/scripts/ledger.py`, commit, rerun the note (`note/README.md`, "How to rerun"), copy
`figures/` and `tables/`, edit section III D of `note/main.tex`, compile, run the checker,
read the pages. What the outcomes mean was written before the runs (journal, end of the
level-3 section).

## Done in this session (batch 11)

- Six level-2 chains closed (`nrpic-run finish`); fates of all six models, run
  core-20261124-130055-9fc9901: 0.69875 member and control collapse (244.25, 259.75 M),
  0.7175 both (294.25, 293.5 M), 0.73625 stays (D = +0.0014). Bracket (0.7175, 0.73625),
  valid. P5, P6, P7, P9 hold; P8 refuted just (0.043 > 0.04). LADDER row 4, journal.
- `verify/row4/row4_fate.py`: continuations joined, colours by y_c, 50-M windows;
  `sequencer.sh` logs why a job waits (decision 0030 item 4) and takes `SEQ_STOP`;
  new `athena_resume.sh` (stub-tested).
- Level 3 queued (above), predictions P10-P15 first.
- T5 of branch core/noise-level2 recorded (journal, section "T5"): Track E's card smoke
  PASS (E-20261123-035724-b661081, check E-20261123-090718-6203c87): card/processor
  1.7e-13 (means), 2.0e-11 (rms) over 30 cycles; level 2 / level 0 wall 1.156 (SR), 1.136
  (USR), inside the +5 to +20 per cent predicted. AL2S of E's ablation was cut by its
  segment cap (not a fault); E continues it.
- Working note rebuilt (run core-20261124-133602-3e31713, 10 pages, checker clean, pages read): Fig. 5 now shows levels 1+2 in units of the equilibrium lapse
  with the 50-M drift means; 20 new ledger rows; section III D, abstract, summary.
- Stage G2: OPEN.md item 2 and item 4, CHECKLIST C1 and C7; collect, verify, report rerun.
- Outbox 20261124T130733Z to Track A (W31 is in work this batch in core's source slot
  "step-limit", which posts the executable and option itself; rule cfl <= 0.6 meanwhile);
  20261124T130734Z to kb (correction: M18 is verified by id_solver T1 in mode code, which
  converges to the continuum psi; the monitor after the solve does not test the matter
  term, since the solver drives that very residual).

## Files to read first

`tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md` (batch 11);
`tracks/core/stage/G2/OPEN.md` (first section, item 2); `tracks/core/verify/LADDER.md`
row 4; `tracks/core/interfaces/REQUESTS_WAVE3.md` sections 5, 5a, 5b (core-v0.7).

## Open with other owners

- orch: interface corrections into coord/INTERFACES (outbox 20261121T233031Z); waiver
  lines (outbox 20261121T204332Z); merge of core/nrpic (carries the cpu_run.sh fix).
- Inbox of core still unacknowledged (not in this session's task): messages 1-10 of
  `nrpic-ctx inbox` (B round1 findings; F chain-stray-resubmission, hnorm-transient-r8,
  hrna-pair-force-slicing, wave-extraction-lmax; D lapse-leak-growth-data,
  newtonian-mode-edges, ah-excision-growth-guard; E a4res-claims-c1-c4; A
  bh1r-inte-deficit-two-levels).
- Track A: W31 (gauge speeds in the step limit) in work in batch 11 by core's source slot
  "step-limit" (its own worktree and branch; its outbox message names the executable).
- Track C: the M/8 bracket and the inward drift bear on its threshold scan (block A on
  M/8) and its drift run.
- Branch core/noise-level2: T5 closed; Fable review of its diff ran beside this session in
  wt/core-s2 (not touched); merge for core-v0.7 after that review.
- Branches core/clump-table, core/oblate, core/gauge-2 merge main before core-v0.7.

## Traps

- `nrpic-run finish` hashes every output file (17 GB per 300-M row-4 run, about twice for
  600 M): run it in the background; it commits by itself (path-limited, waits on
  index.lock).
- `nrpic-run` builds the job environment itself: a Slurm dependency or `--hold` cannot be
  passed through it; that is why jobs are held right after submission and the sequencer
  releases them.
- `make_row4.py` names directories with y_c rounded to three digits (yc0p727 for
  0.726875); the files inside carry the exact value.
- A chain continuation needs the executable that wrote the restart file: the release card
  build of core-v0.6 (`athena_resume.sh` checks its sha256).
- `nrpic-ctx post --type` accepts info, request, proposal, interface-change, blocker,
  kb-request; use `--no-commit` and commit the outbox file yourself.
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/lead_b11/`.
