# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 34 (wave 3), 2026-11-27 ~17:30 PST.

State in three lines: G0 and G1 are signed. Gate G2 was NOT PASSED (decision 0047); the second review is limited to
conditions (a)-(d), whose state is in stage/G2/OPEN.md. (b) is met on the existing restart files; (a) is narrowed
(the non-converging part enters at the ball's outer faces; a level face in the matter adds to the rest); (c) and (d)
are queued on cards. Do not soften any of it.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list | grep A-emd; harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `periodic_threshold/JOURNAL.md` from "2026-11-27 16:39 PST" to
the end (A2Q, F1-F3, FD, SM-q/SM-F); `threshold_ball/JOURNAL.md` entry 18 (C3-G withdrawn, OH, R-split, OB, LF, FR);
`stage/REVIEW-wave3.md` section 14; `coord/DECISIONS/0047-track-a-g2-not-passed.md`.

## Card runs of A (shared queue, priority 2, release card build core-v0.8)

| queue id | label | run | what it is | read with | prediction |
|---|---|---|---|---|---|
| q0089 | a-s1l-quarter | A-20261128-011607-3e2d530 (job 5545, submitted 17:16 PST) | S1L at mu = 0.075 (data A-20261128-003940-60a3521), deck peak_leak.athinput, to t = 410, chain cap 2.6 card-hours | `a2_invariant.py --run <dir> --reference 34.8 --band 32.0 35.5 --label S1L-q`, `a2_crossing.py`, `a2_probe_check.py` (as for S1L-h, periodic_threshold JOURNAL 2026-11-26 13:36) | A2Q (16:39 PST): crossing bracket inside [32.0, 35.5] t_H, along z at the centre |
| q0090 | a-s1l-finder | waiting at 17:17 PST | S1L from t = 0 on deck peak_leak_f.athinput (flow = shear, 4000 it, polish 100, start radius 0.16, finder from t = 150), to t = 205, cap 1.6 | `peak.horizon_status_0.txt` (found only there), `peak.region.hst` columns 38-42 (inside/outside the horizon, region_horizon = 0) at the first found row | F1: first found in (178, 195]; F2: bound at detection ABOVE 0.1; F3: history repeats S1L |

Close each with `harness/bin/nrpic-run finish <run_id>` before reading. The chain continues itself; do not resubmit.

## Processor run that may still be going

FR (core-v0.6 outer-face set on S2c-A, `threshold_ball/scripts/fr_run.sh`), registered by nrpic-run at ~17:18 PST
(run id in `tracks/A-emd-pbh/runs/`, newest `A-20261128-0118*`); if its outcome is not in threshold_ball entry 18,
close it and read it: `ratio_split.py --tmax 2 S2c-A=<S2c-A> S2c-AL32=<OB> S2c-AFR=<FR dir>/S2c-AFR` against
prediction FR (entry 18, 17:20 PST).

## What batch 34 established (0 card-hours used; 4.2 capped in the queue)

- (b): `flow = shear` finds the box horizons from any start (FD, A-20261128-004123-bc1fcf8): S1L t = 190.0 m 7.6056,
  198.7 m 8.3362, 220.0 m 10.73958; P0L6 t = 140 m 6.303242; nothing at P0L6 t = 130. New deck peak_leak_f.
- (a): R-split (A-20261128-004947-8fc6ba9): the failing line ratio is dominated by the outermost cells next to the
  outflow faces; OB (A-20261128-004659-f512816, reader A-20261128-010702-44edae6): faces at 32 cut that part 300-fold.
  Matter part converges (0.059 -> 0.016 at t = 1, M/16 -> M/32); taper on the M/2 level 0.07-0.08 on M/16. LF
  (A-20261128-005331-874ec88, reader A-20261128-011717-7db1434): a level face in the matter keeps the interior
  residual 2.4x higher at t = 2. OH UNDECIDED (A-20261128-005454-eb7b26b). C3-G's batch-31 reading withdrawn.
- (c), (d): queued (above). D-q held; SM-q's step clause refuted (queued anyway, reason on record); SM-F held.
- S1L's own region ratio outside r = 0.6 is 0.43 at t = 190 (periodic: violation in the collapsing matter) -> F2.

## Next, in order

1. Read q0090 and q0089 when they end (predictions above); record outcomes in periodic_threshold/JOURNAL.md, update
   OPEN.md (d), (c). If F2 fails as predicted: a resolution pair in the box (region ratios of P0L four levels vs P0L6
   six levels at equal times) to see whether the box violation falls with the mesh.
2. Condition (a): core's answer on outer faces (outbox b34-finder-confirmed-outer-faces); retest S2c-A/S2c-B with
   core's deposit-fix build (`scratch/core/exe/core_faces-finder/athena_cpu_omp`, scouting) and the best face remedy,
   to t = 2, per region (ratio_split.py); LF again with the fixed build. Then smooth CIC bracket members on two meshes
   to the horizon (cards, priority 2), ratio at detection.
3. Newtonian quarter control (N-z128 at mu = 0.075, processors) to test A2Q's scaling premise.

## Packages

| Package | State | What remains |
|---|---|---|
| `periodic_threshold/` | FD, D-q, SM-q, SM-F judged; A2Q, F1-F3 wait for cards | q0089, q0090 readings |
| `threshold_ball/` | entry 18: R-split, OB, LF, OH judged; FR running | FR outcome; deposit-fix and face-remedy retests |
| `conv_ball/` | prep_bh.py --custom added (custom level lists) | turnaround columns and A-R1.35 unchecked by any verifier |
| `note/`, `szekeres/` | unchanged this batch | new results of the next review |

## Traps

- Box decks: `flow = shear` (global `<fastflow>` key, not per horizon); trapped_tol only on the faces-finder build
  after core's card check q0086.
- The SCOPE section-3 line ratio uses weight x^2 dx over 0 < x < outer face: outer cells dominate it; always split it
  by region (ratio_split.py) before reading a cause into it. The gate review's "outside the finder radius" ratio at
  detection is a different normalization.
- Frozen-matter tests (particles held at rest, geometry evolving) make constraint violation by construction.
- Restart files of S1L: rst 15, 16, 19 are t = 190.0, 198.7, 220.0 (not 180/190).
- `nrpic-run submit` refuses a dirty worktree, and the dispatcher submits queued entries from this worktree: commit
  before leaving anything for the queue. Found or not found is ONLY in `<base>.horizon_status_<n>.txt`.
- GR particle files carry psi^6 in the masses. At most 6 cores per session; never write `||H||` inside a table row.
