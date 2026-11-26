# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md). G2 in progress, NOT ready
             for its verifier: new failures await rulings (outbox g2-state-after-batch-23) and the note's G2 sections,
             schematics, rerun list and slice mosaic are not written (stage/G2/OPEN.md). No item waits for a card.
headline:    S1L's late first shell crossing is not a coordinate effect: on the dust's own clock (the probe particle,
             a first-crossing worldline) it falls in (5.99, 6.80] t_H against 3.62 for converged Newton and 4.35 for
             Zel'dovich. The constraint floor the evolution builds falls with the mesh at order ~0.35 only (C3).
last-result: batch 23 (2026-11-25 evening, processors only; every ended run closed before reading):
             - C3 mesh leg (threshold_ball entry 14, A-20261126-022624-c663e0f): smooth CIC member, M/16 vs M/32:
               orders 1.5, 1.07, 0.34, 0.36 at t = 0.25-1; M/32 at 0.101 at t = 1: prediction G REFUTED. C3 FAILED.
             - A2X (periodic_threshold 18:21 PST): sign of det(dx/dq) changes between 6.19 and 7.21 t_H
               (A-20261126-022438-a08cc5f); probe particle's proper time (5.99, 6.80] (A-20261126-022545-5af99fb);
               the dust-clock bound from snapshots was empty (three runs kept). N-z128 3.62 t_H
               (A-20261126-022631-dafbb4f): AZ1's 5 per cent clause refuted (64^3 force mesh late by 26 per cent).
             - P0L6 (q0013, 4.87 card-hours; A-20261126-022753-f9e9c40): D1, D5 hold; D2, D3, D4 refuted. The
               single "found" (t = 118.1) is a false acceptance; the finder stalls on a resolved horizon from t = 136.
             - Szekeres (q0040, q0041): N64, N128 guard-stopped at tau 30.25, 37.47 (P17 refuted for N128); N256 one
               segment only (tau 21.2). Orders N64->N128: szekeres JOURNAL entry 11 (A-20261126-023242-f3f0578).
cards:       none used this session. Queue: q0015 a-s1l-cont (waiting; SCOPE section 7, not a checklist item).
processors:  detached: A-20261126-023245-1dd80ad (Szekeres N128/N256 reader, 1 core, ~3-4 h); close it with
             `harness/bin/nrpic-run finish A-20261126-023245-1dd80ad`.
next:        1. Rulings (four asked): then write the note's G2 sections, schematics on v0.7, the rerun list
                (stage/G2/VERIFY) and a slice mosaic from the Szekeres N256 dumps; collect/verify/report; verifier.
             2. Read A-20261126-023245-1dd80ad (P19-P21 at 128 -> 256, tau 10 and 20).
             3. C3: particle-number leg of S2c-A (x8, processors), prediction first; core's PCS answer.
blockers:    C3 FAILED (defect not explained); C1 (ii) finder fails on P0L6; A2 FAILED (cause in the GR evolution,
             not named); Szekeres members do not reach tau = 40.
needs:       orch: four rulings (outbox g2-state-after-batch-23). core: finder (finder-false-accept-and-stall-p0l6),
             PCS deposit at refinement boundaries (pcs-deposit-refinement-boundary; core's test running).
offers:      periodic_threshold/scripts/a2_invariant.py (shift-invariant Jacobian sign, probe clock on crossing
             worldlines); threshold_ball/scripts/edge_compare.py; szekeres/scripts/analyse_code_runs.py.
budget:      card-hours this session 0 (q0013 4.87, q0040 0.09, q0041 ~0.98 dispatched earlier); processors about
             4 cores for 1 h plus the detached reader.
