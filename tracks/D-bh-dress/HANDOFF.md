# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21, end of the lead session of batch 5): G0 and G1 signed (G1 with reservations,
coord/GATES.md). G2 in scouting: ES-F met the matter criterion at one resolution and one
boundary (g2runs/JOURNAL.md entry 10); five long card chains are registered and queued
(package `g2long`), and one processor run (Q16-256) is running. Owner D-bh-dress, branch
`track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && squeue -u $USER -o '%i %j %T %r' | grep ' D-' && tail -5
  /data/haiyangw/nrpic/scratch/D-bh-dress/g2long_seq/log && harness/bin/nrpic-run status | grep -E '\?|\*'`
  (a "?" is a run whose session was cut: check `scratch/D-bh-dress/<id>/.nrpic/result.json`, then
  `nrpic-run finish <id>`; a chain's state: `scripts/submit_chain.sh --status <rundir>`).

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 1-4 (criteria N and G, every prediction,
  the job table, smoke outcomes); `stage/REVIEW-wave3.md` sections 11-12; `g2runs/JOURNAL.md` entry 10
  (ES-F); `secondary_infall/JOURNAL.md` 20:36Z (Q16-256 prediction).

## Card runs (all `nrpic-run` chains, release core-v0.6 card executable, plain 1+log, faces +-768 M)

S = /data/haiyangw/nrpic/scratch/D-bh-dress. Run directory = $S/<run id>.

| Run | Run id | First job | Cap | Input | Reads it |
|---|---|---|---|---|---|
| R1 V-1L (vacuum control, 500 M) | D-20261121-203124-a34cf1f | 4830 | 3.5 h, 3 seg | g2long/inputs/v1l.athinput | null test N, V1-V4 |
| R2 ES-1L (null test, 500 M) | D-20261121-203131-8ee2a49 | 4831 | 4.0 h, 4 seg | g2long/inputs/es1l.athinput | N, E1-E4 |
| R3 ES-FL (dust-filled bubble, 500 M) | D-20261121-203150-15f2bad | 4833 (held) | 4.0 h, 4 seg | g2long/inputs/esfl.athinput | G, F1-F6 |
| R4 V-1L16 (M/16, 300 M) | D-20261121-203151-37e7b2d | 4834 (held) | 5.0 h, 5 seg | g2long/inputs/v1l16.athinput | H1-H4 |
| R5 ES-1L16 (M/16, 300 M) | D-20261121-203151-59c54fb | 4835 (held) | 6.0 h, 6 seg | g2long/inputs/es1l16.athinput | H3 |

- Sequencer: a bash process started with setsid nohup from `$S/g2long_seq/` (copy of
  `g2long/tools/sequencer.sh`; pid in `$S/g2long_seq/pid`; log `$S/g2long_seq/log`, one line per
  release and one per hour; queue `$S/g2long_seq/queue`, released `$S/g2long_seq/released`). It
  releases R3, then R4, then R5 (`scontrol release`) whenever fewer than two D jobs are running or
  pending without a hold, and exits when all are released. See it: `ps -p $(cat $S/g2long_seq/pid)`.
  Stop it: `touch $S/g2long_seq/STOP` (or `kill <pid>` by number). If it died (no pid, log silent for
  more than an hour while a job is still held): release by hand, `scontrol release <jobid>`, keeping at
  most two D jobs eligible.
- Each chain's process name was set by hand to D-v1l, D-es1l, D-esfl, D-v1l16, D-es1l16
  (`chain/config.sh`, entry 3 of g2long/JOURNAL.md).
- A chain that stops at its cap before tlim shows FAILED "MAX_SEGMENTS reached": resume it with
  `cd /data/haiyangw/nrpic/wt/D-bh-dress && MAX_SEGMENTS=<n> ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
  scripts/submit_chain.sh $S/<run id> tracks/D-bh-dress/g2long/inputs/<name>.athinput` (restarts are exact;
  first raise the reservation: say it in STATUS.md) or judge it at the time reached.
- When a chain is DONE: `harness/bin/nrpic-run finish <run id>`, then the analyses, each registered
  (`nrpic-run submit --launcher local --cores 1 --package tracks/D-bh-dress/g2long ... -- python3 ...`):
  `g2runs/tools/compare_horizons.py --out '$NRPIC_RUN_DIR' V-1L=$S/<R1>:v1l ES-1L=$S/<R2>:es1l
  V-1B=$S/D-20261120-222625-63abd72:v1b ES-1=$S/D-20261115-172726-60ba4c2:es` (null test N, V2, E1;
  its drift reference is t = 100 M as entry 1 defines, but its window end is fixed, `TEND = 199.5`
  at line 24, and its verdicts are those of g2runs entry 1: give it a `--tend 500` option or copy it
  into g2long/tools with the criteria of g2long entry 1); for ES-FL `flux_tools/esf_analyse.py --run $S/<R3> --data $S/D-20261121-203042-82deeec
  --control $S/<R1>/v1l.horizon_summary_0.txt --out '$NRPIC_RUN_DIR'` and `g2runs/tools/esf_criteria.py`
  with the same arguments (criterion G, F1-F6; (iii) to tau_rem <= 650 M needs `TAU_MAX = 250.0`
  at line 40 of esf_criteria.py made an option). Look at every figure; write outcomes into g2long/JOURNAL.md.
- Expected card-hours ~14 of the 22.5 capped; G2 had 26.8 left before this session.

## Processor run

- Q16-256 D-20261121-205226-3cfbc20 (secondary_infall; nm_run.py, nx 256, six threads, started
  12:52 PST, expected 1-2.5 h; started with --background, so nobody closes it): when
  `$S/<id>/.nrpic/result.json` exists, run `harness/bin/nrpic-run finish D-20261121-205226-3cfbc20`, then the analysis as for Q16
  (README "Wave 3": shells with the cell-centre kernel for dx = 3.469 M, `nm_analyze.py`, `nm_energy.py`)
  and judge QR1-QR5 of secondary_infall/JOURNAL.md 20:36Z.

## Packages still open (each writes only its own directory)

- `drift_controls` (cut 2026-11-20): its three tools `tools/compare_runs.py`, `count_blocks.py`,
  `slice_profiles.py` are UNTRACKED and untested, left as found; remains its judgement of Pb3-Pb4, the
  finder pre-flight outcome, part B, README. Its question is answered elsewhere (vacuum: boundary;
  lapse_leak: gauge); low priority.
- `flux_tools`: ES-F judged (by the lead in g2runs entry 10); remains its README pointing there and V-0.
- `note` v2 (not started): ES-1G, ES-1GB/V-1GB, Q16, ES-F, then the long runs, with run ids.

Decisions pending: none from orch for D (G1 signed). core: the older requests in STATUS.md `needs`.

Traps: (1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`.
  (2) ES data: puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball:
  read masses as Misner-Sharp or horizon masses. (4) core-v0.5 on: a non-finite run exits 3 with
  `<base>.guard.txt`. (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time is
  index 12. (7) The finder writes into `-d` (v0.5 on). (8) The finder summary writes t = 0 twice; use unique
  times. (9) Never kill by pattern; never remove files through a path built from a shell variable.
  (10) `nrpic-ctx ack` renumbers the inbox: ack by file name. (11) A processor re-search of a card dump
  differs from the card's finder by ~3e-8. (12) Q16 snapshots fall near, not on, round a/a_i.
  (13) `nrpic-run submit` refuses an unclean worktree: pass `--package <dir>` while drift_controls has
  untracked files. (14) Format-2 tables end where their maker stopped: ES-F's default table covers only
  the +-192 M corner (exterior = zero); any larger mesh needs `esf_data.py --rbar_max` (g2long entry 2).
  (15) nrpic-run passes no caller variable to a chain (PROC_NAME, SLURM_EXTRA): edit `chain/config.sh`
  before the first segment starts if needed.
