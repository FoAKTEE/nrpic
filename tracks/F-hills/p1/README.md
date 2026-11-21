# p1: resuming the passage P1 (F-hills, wave 3 round 1)

Package of a helper of F-hills. P1 is run F-20261119-150017-b45ec5f
(`/data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f`, written only by its chain).
Predictions and outcomes: `JOURNAL.md` (entries 0-5). Requests: `REQUESTS.md`.

## State (2026-11-20 22:35Z; the session stopped on the pause flag)

- Segment 7 (Slurm 4684) was killed by `pkill -x athena` run by a session of another project of
  the same account, not by a preemption (JOURNAL entry 0, with the evidence).
- Chain resumed 2026-11-20 22:21:54Z: Slurm job **4738**, PENDING, from `rst/hills.00022.rst`
  (t = 110.0), MAX_SEGMENTS = 18 (11 more segments, about 9.2 card-hours, the package cap is
  10), the real executable a byte-identical copy of the release card build named
  `p1-ak03-gpu` (`scratch/F-hills/tmp/p1/exe/`; do not delete it while the chain runs).
- **The binary merged at t = 48.8 M** (common horizon, mass 0.268), 24.9 M from M, long before
  the passage. P1 prediction item 2 (separation, ejection) is refuted; no reference has a merger
  [VERIFIED]; the cause is most likely the members' resolution, m/8 [JUDGEMENT, TO VERIFY with
  an isolated binary at m/8 and m/16]. JOURNAL entry 4 has every item.
- Not done: the ps check that the resumed segment runs as `p1-ak03-gpu` (entry 1 item 6), the
  outcome of the resumed-chain prediction (entry 1), any analysis beyond t = 112.38.

## Contents

| Path | What |
|---|---|
| `scripts/p1lib.py` | readers: run directory (via `nr_first/scripts/nrread.py`), chain logs, restart headers, sacct, baseline arrays |
| `scripts/baselines_tracks.py` | Newton (hole free) and HRNA (hole fixed) trajectories to t = 300 from the P1 input (needs numba: `scratch/F-hills/venv-gb`) |
| `scripts/checks.py` | numbers of the decidable items: trackers, history, horizons (hrms < 1e-3), tree, rate, merger, distances, energies, E_rad |
| `scripts/fig_*.py` | one script per figure: tracks in the plane, separations, horizons, segments, energies |
| `scripts/ledger.py` | card ledger from sacct and the segment logs |
| `scripts/run_all.sh` | all of the above into `$NRPIC_RUN_DIR` |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/` | `p1_checks.json`, `ledger.json`, `baseline_tracks.json` (run F-20261120-223252-ca18a81), `p1_analysis.json` (F-20261120-222808-0e709b6) |
| `figures/` | PNGs of the same runs, all read |

## Card ledger (sacct; run F-20261120-223252-ca18a81)

| seg | job | sacct | elapsed | card-h | t [M] | advance | cycles | MeshBlocks start/end | MB-cycles/s | ended |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4650 | COMPLETED | 0:50:09 | 0.8358 | 0.00-14.27 | 14.27 | 0-3654 | 1716/1716 | 2242 | wall clock |
| 2 | 4669 | COMPLETED | 0:50:06 | 0.835 | 14.27-30.57 | 16.30 | 3654-7826 | 1716/1576 | 2186 | wall clock |
| 3 | 4672 | COMPLETED | 0:50:06 | 0.835 | 30.57-47.65 | 17.08 | 7826-12199 | 1576/1282 | 2171 | wall clock |
| 4 | 4675 | COMPLETED | 0:50:06 | 0.835 | 47.65-65.88 | 18.23 | 12199-16865 | 1282/1366 | 2061 | wall clock |
| 5 | 4678 | COMPLETED | 0:50:05 | 0.8347 | 65.88-85.11 | 19.23 | 16865-21788 | 1366/1310 | 2028 | wall clock |
| 6 | 4681 | COMPLETED | 0:50:07 | 0.8353 | 85.11-103.34 | 18.23 | 21788-26454 | 1310/1352 | 1963 | wall clock |
| 7 | 4684 | FAILED | 0:25:06 | 0.4183 | 103.34-112.11 | 8.77 | 26454-28700 | 1352/- | - | exit 143 (outside pkill) |

Total 5.429 card-hours. Segment 8 onwards: job 4738 (pending).

## Commands for the next session (from `/data/haiyangw/nrpic/wt/F-hills`)

    scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f
    ps -u $USER -o pid,comm,args | grep p1-ak03     # while a segment runs: process name check

Resume after an outside kill (exit 143/137, no termination message; check `sacct -a` and the
segment log first), only when no job of the chain is queued:

    ATHENA_EXE=/data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh \
    NRPIC_REAL_ATHENA=/data/haiyangw/nrpic/scratch/F-hills/tmp/p1/exe/p1-ak03-gpu \
    MAX_SEGMENTS=18 JOB_NAME=F-20261119-150017-b45ec5f \
    scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f \
        /data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/inputs/p1_q4.athinput

(raise MAX_SEGMENTS only with the lead's card-hours). Stop: `scripts/submit_chain.sh --stop
<rundir>`. Analysis redo when segments have landed (registered; commit first):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/p1 --cores 1 \
        --parent F-20261119-150017-b45ec5f --purpose "p1: P1 analysis at t = <latest>" \
        -- bash tracks/F-hills/p1/scripts/run_all.sh
    ... --purpose "..." -- .venv/bin/python tracks/F-hills/nr_first/scripts/p1_analysis.py \
        /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f '--out=$NRPIC_RUN_DIR' \
        --baselines=tracks/F-hills/nr_first/results/baselines_p1.json

Only when `chain/STATUS` is DONE: `harness/bin/nrpic-run finish F-20261119-150017-b45ec5f`, then
the two analyses above, and judge every open item.

## Prediction items still open

- Resumed chain (JOURNAL entry 1): restart point t = 110, tracker continuity across it, 15-21 M
  per segment, tree 1000-1800, 9-11 segments, process name.
- P1 item 1: trackers to t = 280, cost and segment count; item 2: no common horizon of the
  remnant with M by t = 280; item 4: junk energy (package junk_gauge; the merger burst after
  t = 48.8 is not junk).
- Entry 3 item 3b: closest approach of the remnant to M (it is at 11.8 M and approaching at
  t = 112.38).
