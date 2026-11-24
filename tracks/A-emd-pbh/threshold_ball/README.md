# threshold_ball: threshold scan of the expanding ball (Track A, wave 3)

The first scan across a threshold of black-hole formation, in the spherical expanding ball (data
set 3 of conv_ball: compensated top hat, H R_b = 0.7, core contrast delta_c the amplitude). In
pressureless spherical collapse without dispersion the only threshold is the finite-duration one
(scope/SCOPE.md section 3): black hole if the core edge is trapped by t_end = 45 M in its own proper
time. Design: DESIGN.md (exact events per delta_c: design run A-20261121-202520-3164672, data run
A-20261121-202812-cae4436). Predictions and outcomes: JOURNAL.md (entry 1 predictions T1-T6; entry 4
outcomes; entries 5-10 the follow-up tests).

## Files

| path | content |
|---|---|
| `DESIGN.md` | threshold definition, exact events, members, meshes, cost model |
| `JOURNAL.md` | predictions before every run, outcomes, failed predictions |
| `decks/` | conv_ball's nested decks with `<fastflow> diagnostics` declared |
| `queue.txt` | the sequencer's queue of batch 5 (lines 3-15, all submitted) |
| `scripts/design_scan.py`, `prep_scan.py` | exact events; data and nested lattices per delta_c (dc0p4C: nestC of 0.40, batch 11) |
| `scripts/compare_tb.py` | conv_ball's compare.py (copy, changes marked): chain logs, every line output kept |
| `scripts/analyse.py` | T1-T6 per member: finder persistence from every search, ddet, dmmed, line MOTS vs finder, line constraint ratio, cost |
| `scripts/constraint_conv.py`, `hpeak.py`, `k4_floor.sh`, `k4_compare.py` | constraint-floor tests K, K2, K3, K4 (entries 6-10) |
| `scripts/a_guard_restart.sh` | processor restarts of the A-mesh guard stop (G1-G3, entry 5) |
| `scripts/sequencer.sh` | card sequencer (two jobs per owner; logs why it waits) |

## Results (analysis A-20261124-131120-5c974ce; JOURNAL entry 4)

| member | exact tau_AH | horizon persistent from t | tau_det | ddet (M) | dmmed |
|---|---|---|---|---|---|
| B-d1.00 | 15.386 | 17.000 | 15.513 | +0.126 | -3.8e-4 |
| B-d0.70 | 23.405 | 25.250 | 23.472 | +0.059 | -1.9e-3 |
| B-d0.50 | 35.160 | 37.188 | 35.131 | -0.040 | -9.4e-3 |
| B-d0.45 | 40.054 | 42.250 | 40.117 | +0.043 | +1.9e-3 |
| B-d0.42 | 43.656 | 45.875 | 43.686 | +0.015 | +2.8e-3 |
| B-d0.40 | 46.415 | 48.625 | 46.402 | -0.045 | +3.2e-4 |
| B-d0.35 | 54.980 | 58.312 | 54.929 | -0.142 | +2.4e-3 |
| B-d0.20 | 114.574 | none to t = 70 (core turned around, contracting) | - | - | - |
| A-d0.42 | 43.656 | none: guard stop at 47.92 after 3 finds | 43.442 | -0.232 | -3.8e-2 |
| A-d0.40 | 46.415 | none: guard stop at 50.66 after 3 finds | 46.103 | -0.331 | -4.6e-2 |
| C-R1.25 (conv_ball leg) | 9.551 | found in every search | 9.603 | +0.040 | -1.2e-4 |

- The code's bracket of the finite-duration threshold at t_end = 45 on mesh B (M/32) is (0.40, 0.42],
  the exact one; linear interpolation of tau_det gives 0.4103 on B and 0.4103 exact (0.4083 on A from
  first detections). Mesh C: C-d0.42 continuing, C-d0.40 queued (T7).
- First-detection mass excess (up to 4-7 per cent at threshold) is carried by the slice's own
  marginally trapped sphere on the line, not added by the finder (finder vs line within 0.3-1.5 per cent).
- Failed predictions: T4's reason, T5 (ball-radius effect at M/64 0.024 M > 0.02), T6 (A guard stops;
  constraint ratio 0.3-3 on the line > 0.1), K, K2, K3 (constraint floor: entries 6-9).

## How to rerun

1. Data: `python tracks/A-emd-pbh/threshold_ball/scripts/prep_scan.py --out DIR --jobs 4 [--only NAME]`.
2. Cards: each line of `queue.txt` (and `../periodic_threshold/queue_b11.txt`) is the argument list of
   `harness/bin/nrpic-run submit`; the sequencer submits them two at a time.
3. Analysis: `python -I tracks/A-emd-pbh/threshold_ball/scripts/analyse.py --out DIR --jobs 4 [--member NAME ...]`
   (registered: see the manifest of A-20261124-131120-5c974ce).
