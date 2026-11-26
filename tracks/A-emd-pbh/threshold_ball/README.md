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

## Results (analysis A-20261124-131120-5c974ce; JOURNAL entry 4; corrected in batch 19, entry 12)

Corrections after the fresh verifier (stage/G2/VERIFIER-C18.md; analysis A-20261125-151126-7f79a83,
`scripts/c18_answer.py`, fig_c18_mass_bracket.png): searches are read from horizon_status_0.txt (the
summary repeats the last surface after a failed search); every persistence time and classification
below stands. The mass column is now the bracket of the median error that the tracked set allows:
the exact mass on the code's slice lies between the shell of the outermost trapped tracked particle
and the next tracked particle outward (bracket width 1e-3 to 1e-2 relative). The committed
convention (running median of 9 of tau_p - tau_AH over particles ordered by R_i, sign change linear
in R_i) reproduces the former numbers to 1e-5 but places the surface inside the outermost trapped
particle near threshold; values smaller than the bracket width are not measurements. ddet: the
committed interpolation (proper time and label linear in coordinate radius, exact tau_AH at the
label) with the range of three interpolations at the first find in brackets where it exceeds 0.01 M.
Time measure of the threshold: t_end = 45 M is the proper time of the core edge (the first trapped
shell), equal to the synchronous time of the exact solution; the outer comoving layers read
46.5 M at B-d0.42's first detection on the code's slice (DESIGN section 1; entry 12).

| member | exact tau_AH | horizon persistent from t | tau_det | ddet (M) | dmmed |
|---|---|---|---|---|---|
| B-d1.00 | 15.386 | 17.000 | 15.513 | +0.126 | -3.8e-4 |
| B-d0.70 | 23.405 | 25.250 | 23.472 | +0.059 | -1.9e-3 |
| B-d0.50 | 35.160 | 37.188 | 35.131 | -0.040 | -9.4e-3 |
| B-d0.45 | 40.054 | 42.250 | 40.117 | +0.043 | +1.9e-3 |
| B-d0.42 | 43.656 | 45.875 | 43.686 | +0.015 (0.015-0.098 by interpolation) | [-5.6e-3, -0.5e-3] (committed convention +2.8e-3 lies outside) |
| B-d0.40 | 46.415 | 48.625 | 46.402 | -0.045 (-0.045 to +0.003) | [-9.6e-3, -3.7e-3] (committed +3.2e-4 outside) |
| B-d0.35 | 54.980 | 58.312 (first find 57.312, 14 isolated finds before) | 54.929 | -0.142 | [-7.7e-3, +0.5e-3] (committed +2.4e-3 outside) |
| B-d0.20 | 114.574 | none to t = 70 (core turned around, contracting) | - | - | - |
| A-d0.42 | 43.656 | none: guard stop at 47.92 after 3 finds | 43.442 | -0.232 | 3 finds: between -2.6e-2 and -0.8e-2 (the former -3.8e-2 counted 14 repeated summary rows; withdrawn) |
| A-d0.40 | 46.415 | none: guard stop at 50.66 after 3 finds | 46.103 | -0.331 | 3 finds: between -4.5e-2 and -2.7e-2 (former -4.6e-2 withdrawn; no median of 3) |
| C-R1.25 (conv_ball leg) | 9.551 | found in every search | 9.603 | +0.040 | -1.2e-4 |
| C-d0.42 (M/64; A-20261125-115027-17b419e, entry 11) | 43.656 | 45.906 (163 of 936 searches, all from there) | 43.705 | -0.014 (-0.013 to +0.044 by interpolation) | [-4.2e-3, +5.9e-3] (committed +2.4e-2 outside: its smoothed trapped surface lies inside the outermost trapped tracked particle in the first-detection transient; common times: line MOTS 2.1e-3 vs 5.2e-3 on B, A-20261125-115550-fe60ff1) |

- Under the detection rule of entry 1 (which leaves out the constraint clause of SCOPE section 3), the
  code's bracket of the finite-duration threshold at t_end = 45 on mesh B (M/32) is (0.40, 0.42], the
  exact one. Under the outcome rule of SCOPE section 3 as written EVERY ball run is UNDECIDED: the line
  ratio ||H||/||16 pi E|| outside the finder radius at the sample nearest the first persistent detection
  is 1.11 (B-d0.42) and 1.44 (B-d0.40) in the bracket members, above 0.1 in all ten members with a
  detection (gate review, run A-20261126-232456-42c8c8f; decision 0047). Under the entry-1 rule: linear interpolation of tau_det gives 0.4103 on B and 0.4103 exact (0.4083 on A from
  first detections). Mesh C (M/64): C-d0.42 is a black hole with tau_det 43.705 < 45, so the upper end
  holds on the finest mesh (entry 11); C-d0.40 was withdrawn unrun (no G2 item waits for it; T7 untested).
- A-mesh guard stop (entry 5, A-20261124-132016-ecf12c3, A-20261125-120158-b76bfe3): deterministic
  (G1 repeats the card stop exactly); lapse_leak 0 moves it by 0.5 M; alpha_exc 0.3 passes it to t = 48.5;
  in no variant is the horizon persistent on M/16.
- First-detection mass excess (up to 4-7 per cent at threshold) is measured against the exact shell at the
  finder's coordinate radius, which maps 0.02-0.07 in label inside the core edge; against the outermost
  exactly trapped shell there is none on B (verifier, VERIFIER-C18 section 7). Finder = line MOTS is
  confirmed by the verifier on C (-0.6 per cent) only; "carried by the slice" stands for mesh C only.
- Failed predictions: T4's reason, T5 (ball-radius effect at M/64 0.024 M > 0.02), T6 (A guard stops;
  constraint ratio 0.3-3 on the line > 0.1), K, K2, K3 (constraint floor: entries 6-9), T4's mesh-C
  halving (entry 11: bounds below the search interval; medians over unequal windows), G3's "stops like G1".

## How to rerun

1. Data: `python tracks/A-emd-pbh/threshold_ball/scripts/prep_scan.py --out DIR --jobs 4 [--only NAME]`.
2. Cards: each line of `queue.txt` (and `../periodic_threshold/queue_b11.txt`) is the argument list of
   `harness/bin/nrpic-run submit`; since decision 0033 they go through `harness/bin/nrpic-queue add -- <those
   arguments>` (the sequencer is retired); cut chains continue with `scripts/continue_chain.sh <run_id> <max>`.
3. Analysis: `python -I tracks/A-emd-pbh/threshold_ball/scripts/analyse.py --out DIR --jobs 4 [--member NAME ...]`
   (registered: see the manifest of A-20261124-131120-5c974ce).
4. Mesh comparison on common times: `python -I scripts/t4_common.py --ana <analyse.py run dir> --out DIR`
   (A-20261125-115550-fe60ff1). Guard-stop restarts: `scripts/a_guard_restart.sh`, figure `scripts/guard_g123.py
   --run <run dir> --out DIR` (A-20261125-120158-b76bfe3).
