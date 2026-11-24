# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-24, lead session of batch 11, PAUSED at 06:18 PST by the pause flag): G0 and G1 signed (G1 with reservations,
coord/GATES.md). G2 in scouting: the null test N and the growth criterion G hold (M/8; N also at
M/16); the vacuum "floor" of N looks like the finder's stopping rule, not the slice (test FP run log;
its registered judgement is the first thing to do: g2long entry 13). Missing for G2: particle-number members, the third mesh of the growth, note text, a G2
verifier (stage/G2/OPEN.md). Owner D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && squeue -u $USER -o '%i %j %T %r' | grep ' D-' && tail -3
  /data/haiyangw/nrpic/scratch/D-bh-dress/g2long_seq3/log && harness/bin/nrpic-run status | grep -E '\?|\*'`
  (a "?" is a run whose session or chain ended: check `scratch/D-bh-dress/<id>/chain/STATUS` or
  `.nrpic/result.json`, then `nrpic-run finish <id>`; a chain's state: `scripts/submit_chain.sh --status <rundir>`).
  `nrpic-run finish` of a chain checksums 20-35 GB of restart files: 10-20 min each; run them in the
  background (they commit path-limited; your own commits should be path-limited too: `git commit -- <paths>`).

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 6 (P1-P14), 10 (FP, XC, FN4/FNQ/FL16
predictions), 11-13 (outcomes); `stage/G2/OPEN.md`, `stage/G2/LADDER.md`; `stage/REVIEW-wave3.md` 15-16.

## Card runs (nrpic-run chains, release core-v0.6 card executable, plain 1+log, faces +-768 M)

S = /data/haiyangw/nrpic/scratch/D-bh-dress. Run directory = $S/<run id>.

| Run | Run id | Job | State (2026-11-24 06:30) | Read by |
|---|---|---|---|---|
| FF4 ES-FL4 (M/4, 500 M) | D-20261123-022727-1c17e73 | 5152 | resumed from 456.1 M; pending | P12-P14: `g2runs/tools/esf_criteria.py --tau_max 650 --base esfl4` and `flux_tools/esf_analyse.py` (both drop the duplicated removal records of preempted segments) |
| FE4 ES-1L4 (M/4, 300 M) | D-20261123-022726-1b133af | 5153 | restarted from t = 0 (the first segments were preempted at 28 M); pending | P5-P6: `g2long/tools/judge_conv.py` with ES-1L4=$S/<id>:es1l4 added |
| FK ES-FLK (initial_radius 1.6, 400 M) | D-20261123-022725-a553496 | 5144 | resumed from 200 M; held, first in the sequencer | P7-P11: esf_criteria/esf_analyse with `--base esflk` |
| FN4 ES-FLK4N (4N, 400 M) | D-20261124-134157-b17938b | 5170 | held, second in the sequencer | N1-N4 and XN of entries 10, 12: esf_criteria/esf_analyse with `--data $S/D-20261124-130942-29c5de2`; xc_plane.py; `esflk4n.region.hst` |

- Sequencer `$S/g2long_seq3/` (copy of `g2long/tools/sequencer.sh`, setsid nohup, started 04:54 PST;
  queue FK then FN4; releases one whenever fewer than two D jobs are active; exits when the queue is
  released; see `log`, `pid`). Stop: `touch $S/g2long_seq3/STOP`. If it died with a job held:
  `scontrol release <jobid>` by hand, at most two D jobs eligible. The batch-10a sequencer
  (`g2long_seq2`) ended normally on 2026-11-23 08:23.
- Every resumed chain has MAX_SEGMENTS raised in `chain/config.sh` (FF4, FE4 10; FK 12; FN4 7):
  preemptions consume segments. A chain that still ends "FAILED (MAX_SEGMENTS reached)" before tlim is
  only cut: resume it with `PROC_NAME=<name in chain/config.sh> JOB_NAME=<run id> MAX_SEGMENTS=<n>
  ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena scripts/submit_chain.sh $S/<run id>
  tracks/D-bh-dress/g2long/inputs/<name>.athinput` (it restarts from the newest restart file).
- Not registered (card allotment: request to orch posted 2026-11-24): FNQ ES-FLKQ (N/4, input
  `g2long/inputs/esflkq.athinput`, cap 3.0) and FL16 ES-FL16 (M/16 to 300 M, `esfl16.athinput`, cap 5.0).
  Their smoke tests held (S8, S9). Register with `nrpic-run submit --kind scouting --gate G2 --launcher
  chain --gpu-hours <cap> --exe /data/haiyangw/nrpic/.work/build_gpu_v06/src/athena --package
  tracks/D-bh-dress/g2long --purpose "..." -- tracks/D-bh-dress/g2long/inputs/<name>.athinput`, then at
  once `scontrol hold <job>`, set `PROC_NAME=D-<name>` in `chain/config.sh`, append "<run id> <job>" to
  the sequencer's queue (restart the sequencer if it has exited).

## Processor analyses of this session (all registered; outcomes in g2long entries 11-13)

- FIRST: FP D-20261124-130935-fdca920 and FP-ext D-20261124-140606-286a302 (tight-finder re-search of
  restart dumps, `g2long/tools/probe_long.py`) were still running at the pause: when
  `.nrpic/result.json` exists in each, `nrpic-run finish` them, then register `fp_analyse.py` with both
  probes.json files (command in entry 13), look at fp_analyse.png, write FP1-FP5 and FP-ext outcomes,
  then post `scratch/D-bh-dress/tmp/outbox/finder.md` to core (`nrpic-ctx post --to core --type request
  --slug finder-stopping-rule --body-file ...`) and register the ladder schematic
  (`g2long/tools/schem_ladder.py --out '$NRPIC_RUN_DIR'`, statuses updated).
- XC D-20261124-134211-c6fce88 (`xc_plane.py`); judge_long D-20261124-131138-0b8ffc5; judge_conv
  -131149-9f0166d; boundary_gauge -131657-89cd963; slice mosaic -134644-2389227; ladder schematic (entry 13).

## G2: what the next sessions add (stage/G2/OPEN.md)

1. FE4, FF4, FK, FN4 outcomes (above), then FNQ/FL16 if allotted.
2. Note v3: the long runs, FP (finder), XC, ladder (stage/G2/LADDER.md, schem_ladder.png), mosaic.
3. A fresh-context G2 verifier (VERIFIER.md), then `nrpic-stage verify D-bh-dress G2` WITHOUT a timeout
   (it reran the note scripts for more than 25 min in batch 10a).
4. New null-test inputs set `mass_tol_0 = 1e-8` (the production 1e-5 makes plateaus of 1.3e-4).

Decisions pending: orch g2-card-allotment (FNQ, FL16). core: finder-stopping-rule (new),
ah-excision-growth-guard and the older requests in STATUS.md `needs`.

Traps: (1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`.
  (2) ES data: puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball:
  read masses as Misner-Sharp or horizon masses. (4) A non-finite run exits 3 with `<base>.guard.txt`.
  (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time is index 12. (7) The finder
  writes into `-d`. (8) The finder summary repeats times across restarts: take the LAST record of a time
  (fluxio.read_horizon does; judge_long.py takes the first). (9) Never kill by pattern; never remove files
  through a path built from a shell variable. (10) `nrpic-ctx ack` renumbers the inbox: ack by file name.
  (11) A processor re-search of a card dump reproduces the card's finder to 1e-7 (FP1). (12) Q16 snapshots
  fall near, not on, round a/a_i. (13) `nrpic-run submit` refuses an unclean package: pass `--package <dir>`.
  (14) Format-2 tables end where their maker stopped (ES-F: use the 1340 M table). (15) nrpic-run passes no
  PROC_NAME: set it in `chain/config.sh` before the first segment. (16) Horizon excision stops once the
  smallest horizon radius exceeds 4 x `initial_radius_0` (nrpic.cpp:451-455). (17) The production finder
  (mass_tol 1e-5) sits up to ~6e-5 off the converged mass, on the side it comes from (FP). (18) A chain
  segment killed without its own restart rewrites the removal record from the resumption on: use
  `fluxio.drop_overlaps` (esf_criteria/esf_analyse do). (19) The budget tool counts running chains at
  their caps: `nrpic-run budget` before registering.
