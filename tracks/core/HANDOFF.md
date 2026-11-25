# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-25T03:12Z = 2026-11-24 19:12 PST, batch 14, session core-lead-14): **release
candidate core-v0.7 is built, tested on processors and recorded; its card check waits in
the shared queue.** Nothing is half-done. Before that: batch 12 handed the six level-3
card runs of ladder row 4 to the shared queue (section below, unchanged except that q0028
has run), batch 11 was the analysis round of row 4 (journal). Gate G2 of core is NOT met
(`stage/G2/OPEN.md`, first section; CHECKLIST 13 PASS, 5 FAIL).
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.

## Release candidate core-v0.7 (this session)

`tracks/core/RELEASE-v0.7.md`, first line `RELEASE core-v0.7
5f75e5b9cd02fee45eead0b4c3445189d8362dde REGRESSION PASS`. Source commit 5f75e5b9 = the
last of four merges on top of release core-v0.6, one merge commit per branch, no conflict:

| Branch | Merge | What |
|---|---|---|
| core/noise-level2 (5c98beef) | da904f55 | level 2 of the stochastic backreaction, R on the mesh (`<scalar_field> noise_level = 2`, `noise_mode_eq`, four more options) |
| core/step-limit (3a9a3498) | 76ac67a2 | `<z4c> dt_gauge`; start-up warning; restart outputs on SIGTERM (every run); chain script |
| core/gauge-2 (61c8fc4d) | 31ae23e6 | `<z4c> lapse_leak_hole`, a MITIGATION (decision 0025 item 3) |
| core/clump-table (ff11719d) | 5f75e5b9 | table components of `nrpic_cf` with momentum (`comp<c>_boost_file`, ...) |

core/oblate is left out (not ready). Later commits of `core/nrpic` add records and the
drivers `analysis/release/{quick_v07.py,card_v07.py,card_v07.list}` only.

Done and where: predictions and outcomes in `JOURNAL.md` (entry of 2026-11-25T02:12Z);
changelog section core-v0.7 (nine options, the changes that act without an option, the
scripts); `stage/G2/OPEN.md` section core-v0.7 (restart defects a and b, mitigation
status c, limits of level 2 d); executables with COMMIT, SHA256SUMS and READY under
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v07/`; outbox message
20261125T030800Z to orch (for the release clerk).

Results, all on processors (S = /data/haiyangw/nrpic/scratch/core):
- byte regression against release core-v0.6, new options absent: 75 of 75 items
  identical (S/core-20261125-023046-30aba6c); MPI build on one rank 75 of 75
  (S/core-20261125-023646-eca713c); no file differs because of the changes that act
  without an option;
- quick tests PASS (S/core-20261125-023641-7a1c47d; its decks `<case>/new/in.athinput`
  are the inputs of the card list): each branch's example byte-identical with the
  branch executable, SIGTERM cases S1 and S2, chain script, two combinations;
- threaded build at one thread: 32 of 75 identical, rest at rounding level (not a byte
  reference; S/core-20261125-030151-8c0c306).

### Pending: the card check K7 of the merged card executable, queue entry q0039

Label `core-v07-card`, priority 2, 0.3 card-hours asked, 22 cases (seven new, fifteen of
core-v0.6). It was not waited for. When `harness/bin/nrpic-queue show q0039` names a run
(field `run`) and `batch.list.status` in its directory has 22 lines:

    cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main
    S=/data/haiyangw/nrpic/scratch/core; K7=<run id of q0039>
    harness/bin/nrpic-run finish $K7
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, new cases" -- python3 tracks/core/analysis/release/card_v07.py --card $S/$K7 --quick $S/core-20261125-023641-7a1c47d --out '$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, six cases of core-v0.6" -- python3 tracks/core/analysis/release/card_v06.py --card $S/$K7 --quick $S/core-20261121-130813-710b3cc --r2 $S/core-20261121-131250-f8df905 --out '$NRPIC_RUN_DIR'
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "card check K7 judged, nine cases of core-v0.5" -- python3 tracks/core/analysis/release/card_v05.py --card $S/$K7 --cpu $S/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'

Each prints CARD PASS or CARD FAIL. Prediction K7 (journal, entry of 02:12Z with its
amendment of 03:01Z) holds if all three pass. Then: look at the three figures, write the
outcome into the journal, replace "PENDING" in `RELEASE-v0.7.md` (third line and section
"Card checks pending"), in `scratch/core/exe/core_nrpic_v07/READY` (STATUS of
athena_gpu) and in `stage/G2/OPEN.md` (section core-v0.7, item i). If a case fails: the
normalized constraint columns of `*.cstat.hst` and `sr.sf.con.hst` are known to differ
between card and processors (not bounded); anything else is a finding to report before
the tag is used for card production.
Also pending, judged by their packages (not by the lead unless asked): q0035
`nl2-review-R5` (`tracks/core/verify/noise_level2_close/README.md`), q0036
`step-limit-card` (`tracks/core/analysis/step_limit/HANDOFF.md`).

After the tag: the clerk builds `.work/build_{gpu,cpu}_v07`; compare the release
processor build with the candidate by `regress_v04.py` (command at the end of
`RELEASE-v0.7.md`), not by checksums.

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
| q0028 (ran: job 5221, queue state done; not yet finished or read) | row4-l3-0p726875-member-cont | 0.726875 member, 0-600 M | core-20261124-130310-597d9ca, continued IN PLACE (job 5154 computed 0-287.5 M, own restart at 280 M) by `verify/row4/continue_chain.sh`, one segment left | - |
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

## Files to read first

`tracks/core/STATUS.md`; `tracks/core/RELEASE-v0.7.md`; the last entry of
`tracks/core/JOURNAL.md` (batch 14); `tracks/core/stage/G2/OPEN.md` (first section, and
the section of core-v0.7); `tracks/core/verify/LADDER.md` row 4.

## Open with other owners

- orch (release clerk): merge of core/nrpic, tag core-v0.7, release builds, interface
  documents into coord/INTERFACES, announcement (outbox 20261125T030800Z; the CLAUDE.md
  text of core/step-limit, outbox 20261125T004353Z). Older: interface corrections
  (outbox 20261121T233031Z), waiver lines (outbox 20261121T204332Z).
- Inbox of core still unacknowledged (not in this session's task): messages 1-10 of
  `nrpic-ctx inbox` (B round1 findings; F chain-stray-resubmission, hnorm-transient-r8,
  hrna-pair-force-slicing, wave-extraction-lmax; D lapse-leak-growth-data,
  newtonian-mode-edges, ah-excision-growth-guard; E a4res-claims-c1-c4; A
  bh1r-inte-deficit-two-levels), and whatever arrived since.
- Track A: `dt_gauge` (W31) is in the candidate. Track D: `lapse_leak_hole` is a
  mitigation only. Track E: level 2 is in the candidate; R5 (q0035) is its card check.
  Track F: moving table clusters are in the candidate.
- Track C: the M/8 bracket and the inward drift of row 4 bear on its threshold scan.
- Branch core/oblate: not merged (not ready).

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

- A merge of a source branch brings its run manifests and journals with it; the merge
  commits of batch 14 are da904f55, 76ac67a2, 31ae23e6, 5f75e5b9.
- `quick_v07.py` takes about 18 minutes on 3 cores (the five coarse-mesh gauge runs,
  6 minutes each); `regress_v04.py` about 6. Two `nrpic-run submit --launcher local` at
  once worked (their commits did not collide), but do not edit tracked files meanwhile.
- The chain script of core-v0.6 with an executable of core-v0.7 fails a chain on an
  outside SIGTERM (changelog core-v0.7, run scripts, item 5): continue row-4 chains with
  the release card build of core-v0.6 they started with, as `athena_resume.sh` checks.
- Temporary files of this session: `scratch/core/tmp/v07rc/` (build logs, drafts).
