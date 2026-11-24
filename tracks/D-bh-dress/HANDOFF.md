# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-24 13:10 PST, short session of batch 12): G0 and G1 signed (G1 with reservations,
coord/GATES.md). G2 in scouting: criteria N (null test) and G (growth) hold at the meshes run; the
vacuum "floor" of 1.2e-4 is the finder's stopping rule (test FP, g2long entry 14), the converged-finder
floor is 1.8e-5 at M/8. Of the six card runs, FF4 and FE4 ran to tlim (chain STATUS DONE, not yet
closed in the run tool); FK, FN4, FNQ, FL16 wait in the shared card queue (q0008-q0011, decision
0033). Missing for G2: their outcomes (three-way convergence), note text, a G2 verifier, a rerun
script (stage/G2/OPEN.md). Owner D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress && squeue -u $USER -o '%i %j %T %r' |
  grep ' D-'; harness/bin/nrpic-run status | grep -E '\?|\*'`
  (a "?" is a run whose session or chain ended: check `scratch/D-bh-dress/<id>/chain/STATUS` or
  `.nrpic/result.json`, then `nrpic-run finish <id>`; a chain's state: `scripts/submit_chain.sh --status <rundir>`).
  `nrpic-run finish` of a chain checksums 20-70 GB of restart files: 10-30 min each; run them in the
  background (they commit path-limited; your own commits should be path-limited too: `git commit -- <paths>`).

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 6 (P1-P14), 10 (FN4/FNQ/FL16 predictions),
12 (XN), 14 (FP outcomes), 15 (XQ, L5, restart cadence), 16-17 (test FE); `stage/G2/OPEN.md`,
`stage/G2/LADDER.md`; `stage/REVIEW-wave3.md` sections 17-18.

## Card runs (nrpic-run chains, release core-v0.6 card executable, plain 1+log, faces +-768 M)

S = /data/haiyangw/nrpic/scratch/D-bh-dress. Run directory = $S/<run id>. On 2026-11-24 12:00 PST the
orchestrator stopped this owner's sequencer (pid 3757609, `$S/g2long_seq3/`, dead: do not restart it) and
cancelled the waiting jobs 5181 (FK), 5170 (FN4), 5174 (FNQ), 5175 (FL16) under the cap of five
(decision 0033). None of the four was closed: each is continued IN PLACE (same run id, manifest,
predictions, card-hour reservation, chain/config.sh with PROC_NAME, MAX_SEGMENTS, EXTRA_ARGS) through
the shared queue with `tracks/D-bh-dress/g2long/tools/continue_chain.sh <run id>` (submits one job:
scripts/submit_chain.sh on the run directory, JOB_NAME = run id; resumes from the newest restart or
from t = 0; byte-checks deck and executable; appends to the manifest's `continuations` and commits it
path-limited; `--dry-run` checks without submitting; dry runs of all four passed 13:03 PST).

| Run | Run id | Queue id (label, prio) | State (2026-11-24 13:05 PST) | Read by |
|---|---|---|---|---|
| FF4 ES-FL4 (M/4, 500 M) | D-20261123-022727-1c17e73 | - | chain DONE (job 5152 ended 10:39); `nrpic-run finish` pending | P12-P14: `g2runs/tools/esf_criteria.py --tau_max 650 --base esfl4` and `flux_tools/esf_analyse.py` (both drop duplicated removal records) |
| FE4 ES-1L4 (M/4, 300 M) | D-20261123-022726-1b133af | - | chain DONE (job 5153 ended 11:14); `nrpic-run finish` pending | P5-P6: `g2long/tools/judge_conv.py` with ES-1L4=$S/<id>:es1l4 added; then probe_long.py on its dumps (tight finder) + fe_analyse-style S(t) at M/4 |
| FK ES-FLK (initial_radius 1.6, 400 M) | D-20261123-022725-a553496 | q0008 (D-FK, 2) | waiting; resumes from rst/esflk.00005.rst, 5 of 12 segments used | P7-P11: esf_criteria/esf_analyse with `--base esflk` |
| FN4 ES-FLK4N (4N, 400 M) | D-20261124-134157-b17938b | q0009 (D-FN4, 2) | waiting; from t = 0 (never ran), 0 of 7 segments | N1-N4, XN: esf_criteria/esf_analyse with `--data $S/D-20261124-130942-29c5de2`; xc_plane.py; `esflk4n.region.hst` |
| FNQ ES-FLKQ (N/4, 400 M) | D-20261124-172725-2f426b6 | q0010 (D-FNQ, 2) | waiting; from t = 0 (never ran), 0 of 6 segments | Q1-Q3, XQ: the same with `--data $S/D-20261124-131050-ed0a535` |
| FL16 ES-FL16 (M/16 growth, 300 M) | D-20261124-172745-72472ed | q0011 (D-FL16, 2) | waiting; from t = 0 (never ran), 0 of 9 segments | L1-L5: esf_criteria/esf_analyse `--base esfl16`; L3 needs FF4 and ES-FL too |

- Priority 2: stage/G2/OPEN.md item 1 waits for all four. No `--after`: the four are independent (L3 reads
  FF4 and ES-FL, both done); the queue takes them in the order added. When the account had 5 of 5 jobs
  (13:05 PST) they were first in the dispatcher's order. Follow them: `harness/bin/nrpic-queue list --owner
  D-bh-dress`, `show q0008`; a chain's state: `scripts/submit_chain.sh --status $S/<run id>`.
- Never submit by another route (no sbatch, no submit_chain.sh by hand, no held jobs, no sequencer). A
  chain that ends "FAILED (MAX_SEGMENTS reached)" before tlim, or is cancelled again while waiting, is added
  again: `harness/bin/nrpic-queue add --label D-FK-2 --priority 2 --cmd 'tracks/D-bh-dress/g2long/tools/
  continue_chain.sh <run id> [new total max_segments]'` (dry run first with `--dry-run`). If an entry fails,
  `nrpic-queue show <id>` and `locks/queue/out/<id>.<n>.log`; look at squeue before `retry`.
- Close FF4 and FE4 (`nrpic-run finish <id>`; checksums 20-70 GB, 10-30 min each: run in the background,
  it commits path-limited; keep your own commits path-limited meanwhile).
- Card allotment toward G2: 3.86 card-hours left with all six reserved (nrpic-run budget 09:32); continuing
  in place registers nothing new, so the reservation is unchanged.

## Processor runs of this session (all registered)

- FP D-20261124-130935-fdca920 and FP-ext D-20261124-140606-286a302 closed; judged by fp_analyse
  D-20261124-172410-e8afc73 and D-20261124-172508-c847ee4 (layout only) in g2long entry 14.
- Ladder schematic D-20261124-172838-3a30e48 (stage/G2 C9).
- FE D-20261124-173137-f358715 (tight finder on the 50 M dumps of V-1L, ES-1L and the 50-200 M dumps of
  V-1L16, ES-1L16) judged by fe_analyse D-20261124-175356-0f40f1a (entry 17): FE1, FE2 missed their bounds
  (not refuted), FE3 holds; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes.
- Ladder schematic redrawn after FE: D-20261124-175505-a1053fa.
- `nrpic-stage verify D-bh-dress G2`: with checksums it ran > 35 min (hashing restart files) and was stopped by
  pid; `--no-checksums` (2 min, log `$S/tmp/stage_verify_g2_b11b_nock.log`) passes everything but `runs` (six
  open card runs; G1 gate-review run D-20261121-165420-5d1c245 with a changed scratch input).

## G2: what the next sessions add (stage/G2/OPEN.md)

1. Outcomes of the six card runs (table above), then the redrawn ladder schematic.
2. Note v3: the long runs, FP/FE (finder floor and the null-test step), XC, ladder, mosaic.
3. A fresh-context G2 verifier (VERIFIER.md), then `nrpic-stage verify D-bh-dress G2` again without a timeout.
4. A rerun script for G2 (C6).

Decisions pending: core: finder-stopping-rule (posted 2026-11-24), ah-excision-growth-guard and the
older requests in STATUS.md `needs`.

Traps: (1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`.
  (2) ES data: puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball:
  read masses as Misner-Sharp or horizon masses. (4) A non-finite run exits 3 with `<base>.guard.txt`.
  (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time is index 12. (7) The finder
  writes into `-d`. (8) The finder summary repeats times across restarts: take the LAST record of a time
  (fluxio.read_horizon, fp_analyse, fe_analyse do; judge_long.py takes the first). (9) Never kill by pattern;
  never remove files through a path built from a shell variable. (10) `nrpic-ctx ack` renumbers the inbox:
  ack by file name. (11) A processor re-search of a card dump reproduces the card's finder to 4e-6 (FP1).
  (12) Restart numbers are not times: wall-time restarts sit between the 50 M ones; probe_long reads the
  time from the dump. (13) `nrpic-run submit` refuses an unclean package: pass `--package <dir>`.
  (14) Format-2 tables end where their maker stopped (ES-F: use the 1340 M table). (15) nrpic-run passes no
  PROC_NAME (athena arguments after the deck do reach EXTRA_ARGS): holding a job to edit config.sh is no
  longer allowed (decision 0033); a new chain runs under the default nrc-<hash> name (still not "athena"). (16) Horizon
  excision stops once the smallest horizon radius exceeds 4 x `initial_radius_0` (nrpic.cpp:451-455).
  (17) The production finder (mass_tol 1e-5) sits up to ~6e-5 off the converged mass, on the side it
  comes from; A16 sits 1.8e-4 below A32 on every mesh (FP). (18) A chain segment killed without its own
  restart rewrites the removal record from the resumption on: use `fluxio.drop_overlaps`. (19) The budget
  tool counts running chains at their caps: `nrpic-run budget` before registering.
