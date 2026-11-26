# G3 of Track E: what is open (batch 23, 2026-11-25 evening)

G3 is not ready for review. Scope: spec/scope/SCOPE.md 4d with 4d.9 A1-A14 (A12 now carries the measured pilot cost).

1. Reference proper: as in batch 20 (direct 4e6 E-20261125-152832-c301e92 and repeat E-20261125-163825-ca2ebaa; tilted
   nu = 4 E-20261125-160658-855db8c, A9 met); the sigma = 0.1 coarse-graining bound of A10 NOT reached (R39).
2. zeta reader: cleared to judge G3 runs (decision 0042 item 1). Passes Z0, Z1 with the variational expected values at the
   lockstep state (E-20261126-030949-30c5d47), Z2(i), Z2(iii'); Z2(iii) and Z1 as first run stay FAILED as written.
   On the 128^3 pilot dump b000 the lead's and the verifier's maps agree per cell to 4.3e-9 (E-20261126-024954-1c0a893).
3. BLOCKING for reading G3: the map costs of order 1.5 core-hours a 128^3 member at 1000 steps and about 6 at 4000 on this
   machine (R41; g3/JOURNAL.md entries 7-8). A cheaper evaluation of the same map (table along the box relation plus the
   second-order correction across it, checked against map_rk4 on sampled and tail cells) is needed before the baseline
   is read; zeta of the pilot (P5-3, P5-5) is not judged.
4. Pilot (E-20261126-002413-65295f3): G3P-1 (baseline 0.0351 card-h a run) and G3P-2 hold; G3P-3 holds except its sd
   clause (1.403 against 1.4); level 2 and kdriver not measured (failed at start-up, R42); A8 record owed (G3L00).
5. Card runs: G3C q0051 running (job 5348); waiting G3R q0052, G3B00/G3B01 q0053/q0054, G3B02-06 q0061-q0065 (pairs
   19-73), G3L00 q0066. Not yet queued: pairs 74-127 (54 pairs, about 5 jobs), level-2 pairs 5-15 (after G3L00 measures
   the level-2 cost).
6. Reservations carried: geodesic slicing only (A8); U-A4'(a) of G2 stays FAILED as written (answered by G3-C).
7. Package items (C5, C6, C9-C17): result figures, ledger, schematic, working-note section, fresh verifier: after the runs.
