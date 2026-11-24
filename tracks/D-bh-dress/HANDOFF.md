# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-24, lead session of batch 11b, ended about 10:20 PST): G0 and G1 signed (G1 with reservations,
coord/GATES.md). G2 in scouting: criteria N (null test) and G (growth) hold at the meshes run; the
vacuum "floor" of 1.2e-4 is the finder's stopping rule (test FP, g2long entry 14), the converged-finder
floor is 1.8e-5 at M/8. Six card runs registered and waiting (cards held by another user's priority
jobs until about the morning of 2026-11-25). Missing for G2: their outcomes (three-way convergence),
note text, a G2 verifier, a rerun script (stage/G2/OPEN.md). Owner D-bh-dress, branch
`track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && squeue -u $USER -o '%i %j %T %r' | grep ' D-' && tail -3
  /data/haiyangw/nrpic/scratch/D-bh-dress/g2long_seq3/log && harness/bin/nrpic-run status | grep -E '\?|\*'`
  (a "?" is a run whose session or chain ended: check `scratch/D-bh-dress/<id>/chain/STATUS` or
  `.nrpic/result.json`, then `nrpic-run finish <id>`; a chain's state: `scripts/submit_chain.sh --status <rundir>`).
  `nrpic-run finish` of a chain checksums 20-70 GB of restart files: 10-30 min each; run them in the
  background (they commit path-limited; your own commits should be path-limited too: `git commit -- <paths>`).

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 6 (P1-P14), 10 (FN4/FNQ/FL16 predictions),
12 (XN), 14 (FP outcomes), 15 (XQ, L5, restart cadence), 16-17 (test FE); `stage/G2/OPEN.md`,
`stage/G2/LADDER.md`; `stage/REVIEW-wave3.md` sections 17-18.

## Card runs (nrpic-run chains, release core-v0.6 card executable, plain 1+log, faces +-768 M)

S = /data/haiyangw/nrpic/scratch/D-bh-dress. Run directory = $S/<run id>. Order of release by the sequencer:
FK, FN4, FNQ, FL16 (FE4 and FF4 are already eligible).

| Run | Run id | Job | State (2026-11-24 09:30) | Read by |
|---|---|---|---|---|
| FF4 ES-FL4 (M/4, 500 M) | D-20261123-022727-1c17e73 | 5152 | from 456.1 M; pending (priority jobs) | P12-P14: `g2runs/tools/esf_criteria.py --tau_max 650 --base esfl4` and `flux_tools/esf_analyse.py` (both drop duplicated removal records) |
| FE4 ES-1L4 (M/4, 300 M) | D-20261123-022726-1b133af | 5153 | from t = 0; pending | P5-P6: `g2long/tools/judge_conv.py` with ES-1L4=$S/<id>:es1l4 added; then probe_long.py on its dumps (tight finder) + fe_analyse-style S(t) at M/4 |
| FK ES-FLK (initial_radius 1.6, 400 M) | D-20261123-022725-a553496 | 5144 | from the newest restart (200-225 M); held, first | P7-P11: esf_criteria/esf_analyse with `--base esflk` |
| FN4 ES-FLK4N (4N, 400 M) | D-20261124-134157-b17938b | 5170 | held, second | N1-N4, XN: esf_criteria/esf_analyse with `--data $S/D-20261124-130942-29c5de2`; xc_plane.py; `esflk4n.region.hst` |
| FNQ ES-FLKQ (N/4, 400 M) | D-20261124-172725-2f426b6 | 5174 | held, third | Q1-Q3, XQ: the same with `--data $S/D-20261124-131050-ed0a535` |
| FL16 ES-FL16 (M/16 growth, 300 M) | D-20261124-172745-72472ed | 5175 | held, fourth | L1-L5: esf_criteria/esf_analyse `--base esfl16`; L3 needs FF4 and ES-FL too |

- Sequencer `$S/g2long_seq3/` (copy of `g2long/tools/sequencer.sh`, setsid nohup, pid 3757609, alive at
  09:30; releases one held job whenever fewer than two D jobs are active; exits when the queue is
  released; see `log`, `queue`, `released`). Stop: `touch $S/g2long_seq3/STOP`. If it died with jobs held:
  restart it (`setsid nohup tracks/D-bh-dress/g2long/tools/sequencer.sh $S/g2long_seq3 > /dev/null 2>&1 &`;
  it skips the released lines) or `scontrol release <jobid>` by hand, at most two D jobs eligible.
- Chain configs (`chain/config.sh`): MAX_SEGMENTS FF4 10, FE4 10, FK 12, FN4 7, FNQ 6, FL16 9 (preemptions
  consume segments); EXTRA_ARGS `output2/dt=25` (FK, FN4, FNQ) and `output2/dt=12.5` (FL16): a restart
  every ~10 card-minutes (decision 0032 item 2). A chain that ends "FAILED (MAX_SEGMENTS reached)" before
  tlim is only cut: resume it with `PROC_NAME=<name in chain/config.sh> JOB_NAME=<run id> MAX_SEGMENTS=<n>
  ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena scripts/submit_chain.sh $S/<run id>
  tracks/D-bh-dress/g2long/inputs/<name>.athinput` (it restarts from the newest restart file; check that
  EXTRA_ARGS survived in config.sh).
- Card allotment toward G2: 3.86 card-hours left with all six reserved (nrpic-run budget 09:32).

## Processor runs of this session (all registered)

- FP D-20261124-130935-fdca920 and FP-ext D-20261124-140606-286a302 closed; judged by fp_analyse
  D-20261124-172410-e8afc73 and D-20261124-172508-c847ee4 (layout only) in g2long entry 14.
- Ladder schematic D-20261124-172838-3a30e48 (stage/G2 C9).
- FE D-20261124-173137-f358715 (tight finder on the 50 M dumps of V-1L, ES-1L and the 50-200 M dumps of
  V-1L16, ES-1L16) judged by fe_analyse D-20261124-175356-0f40f1a (entry 17): FE1, FE2 missed their bounds
  (not refuted), FE3 holds; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes.
- Ladder schematic redrawn after FE: D-20261124-175505-a1053fa.
- `nrpic-stage verify D-bh-dress G2` ran without a timeout (log `$S/tmp/stage_verify_g2_b11b.log`).

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
  PROC_NAME: set it in `chain/config.sh` before the first segment (hold the job at once). (16) Horizon
  excision stops once the smallest horizon radius exceeds 4 x `initial_radius_0` (nrpic.cpp:451-455).
  (17) The production finder (mass_tol 1e-5) sits up to ~6e-5 off the converged mass, on the side it
  comes from; A16 sits 1.8e-4 below A32 on every mesh (FP). (18) A chain segment killed without its own
  restart rewrites the removal record from the resumption on: use `fluxio.drop_overlaps`. (19) The budget
  tool counts running chains at their caps: `nrpic-run budget` before registering.
