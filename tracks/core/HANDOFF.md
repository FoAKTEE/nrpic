# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-24, batch 12, session core-lead-12: the six level-3 card runs of row 4 were
handed to the shared queue, q0028-q0033, section below; nothing else changed). Before that,
batch 11, session core-lead-11 (analysis round, no AthenaK source change): gate G2 of core is NOT met (`stage/G2/OPEN.md`, first section; CHECKLIST 13
PASS, 5 FAIL: C1/C7 ladder rows 3 and 4 partial, C2 three-way convergence, C6
reproducibility package, C12 package documents). This session closed the six level-2
chains of ladder row 4 on cells of M/8, judged them by the rule written before the runs,
found collapse within 300 M BRACKETED between y_c = 0.7175 and 0.73625, saw that the
surviving pairs drift inward steadily (so the bracket may be set by the 300-M window),
queued level 3 to test that, rebuilt the working note, recorded T5 of branch
core/noise-level2 (PASS on the card, run by Track E), and posted a follow-up to Track A
(step limit in work) and a correction to kb (link M18).
The session closed at the pause flag (`locks/PAUSE`, found 2026-11-24T14:19Z): nothing is
half-done. Stage verify of this batch: rerun, compare and regenerate PASS for the first
time (the note scripts now default their output to note/); runs FAIL only on the six open
level-3 chains.
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

## Six card runs wait in the shared queue (ladder row 4 on M/8, level 3)

Batch 12 (2026-11-24T21:00-21:12Z, session core-lead-12, no analysis): orch stopped core's
sequencer (pid 3904230) and cancelled the pending and held jobs at 12:00 PST under the
user's cap of five queued jobs (decision 0033). Card runs now reach Slurm ONLY through the
shared queue `harness/bin/nrpic-queue` (harness/RULES.md, section "Shared card queue"): no
sbatch, no `submit_chain.sh` by hand, no sequencer. The six level-3 runs were handed to it,
priority 2 (the G2 package waits for them), in the plan's order, no `--after`.

Rule: `tracks/core/JOURNAL.md`, entry 2026-11-21T20:26Z (unchanged; it reads t <= 300 M).
Predictions P10-P15 and the design: entry 2026-11-24T12:51Z, section "Level 3" (they
stand). What batch 12 did and why: entry 2026-11-24T21:05Z. Package `tracks/core/verify/row4/`.
Initial data of 0.726875: run core-20261124-130236-68d4ee5.

| Queue id | Label | Model | Run | Parent (300-M restart) |
|---|---|---|---|---|
| q0028 | row4-l3-0p726875-member-cont | 0.726875 member, 0-600 M | core-20261124-130310-597d9ca, continued IN PLACE (job 5154 computed 0-287.5 M, own restart at 280 M) by `verify/row4/continue_chain.sh`, one segment left | - |
| q0029 | row4-l3-0p73625-control | 0.73625 control, 300-600 M | new run at dispatch (replaces ed96d4d, stopped: 6.5 M, no own restart) | core-20261123-020500-9b192cd |
| q0030 | row4-l3-0p726875-control | 0.726875 control, 0-600 M | new run at dispatch (replaces 31cf5e8, stopped unstarted) | - |
| q0031 | row4-l3-0p73625-member | 0.73625 member, 300-600 M | new run at dispatch (replaces 7d6a10d) | core-20261123-020458-dfc38d7 |
| q0032 | row4-l3-0p755-control | 0.755 control, 300-600 M | new run at dispatch (replaces d9d09bf) | core-20261121-204237-ae00ca2 |
| q0033 | row4-l3-0p755-member | 0.755 member, 300-600 M | new run at dispatch (replaces 09319a0) | core-20261121-204232-f74c942 |

Closed as stopped in batch 12 (`nrpic-run finish --status stopped`): ed96d4d, 31cf5e8,
7d6a10d, d9d09bf, 09319a0 (they are not read; ed96d4d's 26 history rows of 300-306.5 M stay
in its directory). The five new runs carry the same arguments as the runs they replace
(`--launcher chain --gpu-hours 1.97`, release card build of core-v0.6; the continuations
through `verify/row4/athena_resume.sh`, whose first segment starts with `-r` from the
parent's `rst/st.00015.rst`) and a note naming the run replaced. Each asks 1.97 card-hours;
597d9ca has about 0.67 left to compute (320 M at 7.55 s/M). The run id of a dispatched entry:
`harness/bin/nrpic-queue show q00NN` (field run); the manifest is committed on core/nrpic
by the dispatcher (push it at session end).

Read them (exact commands):

    cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main
    harness/bin/nrpic-queue list --owner core          # state, run id, job of each entry
    S=/data/haiyangw/nrpic/scratch/core
    # R: 597d9ca and the five run ids that `nrpic-queue show q0029` ... `q0033` name
    for r in $R; do scripts/submit_chain.sh --status $S/$r | head -1; done
    # a chain cut by its segment cap after a preemption ends FAILED although it is only cut:
    # continue it from its own newest restart with a queue entry
    #   harness/bin/nrpic-queue add --label <l> --priority 2 --cmd 'tracks/core/verify/row4/continue_chain.sh <run_id> <max_segments>'
    # (test first: DRY=1 tracks/core/verify/row4/continue_chain.sh <run_id> <n>); never resubmit by hand
    # finish hashes 17-35 GB per run (8-15 minutes each when others hash too): background
    for r in $R; do harness/bin/nrpic-run finish $r; done
    # fates of all seven models, continuations joined with '+'; fill in the new run ids
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
      --purpose "row 4 M/8 levels 1-3: fates against controls (rule of JOURNAL 2026-11-21T20:26Z); P10-P15 of JOURNAL 2026-11-24" -- \
      python3 tracks/core/verify/row4/row4_fate.py --out '$NRPIC_RUN_DIR' \
      0.605=$S/core-20261121-204230-3bcb118,$S/core-20261121-204235-0b25077 \
      0.680=$S/core-20261121-204234-d010783,$S/core-20261121-204239-2be5ac2 \
      0.69875=$S/core-20261123-020454-8fec6b2,$S/core-20261123-020456-884f550 \
      0.7175=$S/core-20261123-020450-7e42037,$S/core-20261123-020452-e635a8e \
      0.726875=$S/core-20261124-130310-597d9ca,$S/<run of q0030> \
      0.73625=$S/core-20261123-020458-dfc38d7+$S/<run of q0031>,$S/core-20261123-020500-9b192cd+$S/<run of q0029> \
      0.755=$S/core-20261121-204232-f74c942+$S/<run of q0033>,$S/core-20261121-204237-ae00ca2+$S/<run of q0032>

The script classifies by the rule (300 M) and prints `t_c_all` (collapse over the whole
record) and writes 50-M window means (`windows_50M` in `row4_fate.json`) for P11-P13.
P14 (join without a jump): compare the continuation's first record of `st.nrpic.hst`
(column 13) with its parent's record at 300 M. P15: "cpu time used" in the chain logs
(597d9ca: two segments, the first cut at 287.5 M by preemption, the second resumed from its
restart at 280 M, so 280-287.5 M is computed twice. [TO VERIFY] whether its history files
then hold 280-287.5 M twice (AthenaK appending after a restart) and whether
`row4_fate.py` copes: keep the first segment's records up to 280 M and the second's from
280 M on; check the time column for a step back before reading the fate.)
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
- Card runs: only `harness/bin/nrpic-queue add` (decision 0033); `nrpic-run submit` with a
  card launcher is refused outside the dispatcher. An entry waits while the worktree is not
  clean (nrpic-run refuses): keep it committed. `verify/row4/sequencer.sh` is retired (no
  sequencers, decision 0033).
- `make_row4.py` names directories with y_c rounded to three digits (yc0p727 for
  0.726875); the files inside carry the exact value.
- A chain continuation needs the executable that wrote the restart file: the release card
  build of core-v0.6 (`athena_resume.sh` checks its sha256).
- `nrpic-ctx post --type` accepts info, request, proposal, interface-change, blocker,
  kb-request; use `--no-commit` and commit the outbox file yourself.
- The clock: `date -u` (the shell's local time is PST). Temporary files of the lead:
  `scratch/core/tmp/lead_b11/`.
