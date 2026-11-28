# Gate review: F-hills G1 (independent reviewer, decision 0019 item 3)

Reviewer: fresh session (batch 34a, 2026-11-27 PST), not the author of any of the material
reviewed. Branch `track/F-hills` at `eaa0b643c` (main merged, "Already up to date"). No tag
`stage/F-hills/G1-pass-*` exists (`git tag -l`: only `stage/F-hills/G0-pass-20261120`).

## 0. Predictions for the reviewer's own check (written and committed before it runs)

My own reader (`scratch/F-hills/tmp/gate_review_g1/review_check.py`, registered with
`nrpic-run`, one core) reads the raw AthenaK outputs of A2 (F-20261124-210400-902c650) and A
(F-20261121-203144-b2cf16b): every kept tracker copy plus the live file, the horizon summaries
of A and A2, the three status files of A2 (133-186 M) and A2's history. I have read the
package's claims (STAGE_REPORT, STATUS, OPEN, VERIFIER parts 1 and 2, the lead's batch-34
journal); the predictions below are therefore that the claims reproduce, with bands that a
wrong claim would leave. Refuted if a value falls outside its band.

| # | Quantity (definition) | Claim | Predicted band |
|---|---|---|---|
| R1 | last tracker time of A2 (all copies joined); largest time step between consecutive distinct tracker times over 61.8 M to the end | 186.0 M; one step (2^-9 M) | last time in [185.95, 186.05] M; largest gap <= 2 x 2^-9 M |
| R2 | m2 (tracker 1) to M (tracker 2), coordinate distance: minimum after 120 M and its time; value at the last record | 8.733 M at 134.3 M; 17.53 M | minimum in [8.70, 8.76] M at t in [134.1, 134.5] M; last value in [17.4, 17.6] M |
| R3 | m1 (tracker 0) to M: first time below 1 M; value at the last record | 138.33-138.35 M; 1.3e-9 M | first time in [138.2, 138.5] M; last value < 1e-6 M |
| R4 | status file of finder 2 (M), A2, distinct search times 133.0-186.0 M: found flag; first time with area mass > 1.05; area mass at the last search | found at all 1697; 137.5 M; 1.1137 | all found; first time in [137.4, 137.6] M; last area mass in [1.110, 1.117] |
| R5 | status file of finder 1 (m2): found flag; area mass range | found at all 1697; 0.12954 within 6.4e-4 | all found; every area mass in [0.1285, 0.1305] |
| R6 | failure signature in the horizon summaries (a row whose columns 3-12 equal the previous row's, or a mass <= 0 or not finite), A (0-61.8 M) and A2 (61.8 M to the end), after removing exact restart repeats of the same time | finders 1, 2: none; finder 0: none before 139.5 M | zero for finders 1 and 2 over A + A2; zero for finder 0 before 139.5 M, and failures of finder 0 after 141 M |
| R7 | rms H = sqrt(H-norm2 / Volume) from A2's history (`hills.z4c.user.hst`, comment lines skipped): maximum and its time | 6.19e-5 at 135.5 M | maximum in [6.0e-5, 6.4e-5], at t in [134, 138] M; below 1e-4 at every record |

A figure (`fig_review_g1.png`: the three distances, finder 2's area mass, rms H) is drawn by the
same run and read before any verdict rests on it.
