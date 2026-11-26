# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md). G2 in progress, NOT ready
             for its verifier: orch ruled (0043 item 1): C3, A2 stay FAILED as written, C1 (ii) horizon part FAILED
             on record; the Szekeres N256 continuation and the half-amplitude S1L member are wanted first (queued
             q0067, q0068 in batch 24); the note's G2 sections, schematics, rerun list and slice mosaic are unwritten.
headline:    S1L's late first shell crossing is not a coordinate effect: the central particle (at rest, a vertex of
             the first-crossing cells) is older than 5.99 t_H on the last uncrossed slice, against 3.62 t_H for
             Newton at 128^3 and 4.35 for Zel'dovich. The constraint floor the evolution builds falls with the mesh at order ~0.35 only (C3).
last-result: batch 24 (19:17-19:50 PST): predictions P17/P24 and A2H written first; half-amplitude data
             A-20261126-032537-f1060e7 and smoke test A-20261126-032800-48a3825 (one clause each refuted, see journal);
             both card runs queued. Batch 23 (processors only; every ended run closed before reading):
             - C3 mesh leg (threshold_ball entry 14, A-20261126-022624-c663e0f): smooth CIC member, M/16 vs M/32:
               orders 1.5, 1.07, 0.34, 0.36 at t = 0.25-1; M/32 at 0.101 at t = 1: prediction G REFUTED. C3 FAILED.
             - A2X (periodic_threshold 18:21 PST): sign of det(dx/dq) changes between 6.19 and 7.21 t_H
               (A-20261126-022438-a08cc5f); central particle at rest (A-20261126-023551-f800cf5): proper time >= 5.99 t_H
               on the last uncrossed slice; the probe column is a coordinate point's clock (reading withdrawn, PC). N-z128 3.62 t_H
               (A-20261126-022631-dafbb4f): AZ1's 5 per cent clause refuted (64^3 force mesh late by 26 per cent).
             - P0L6 (q0013, 4.87 card-hours; A-20261126-022753-f9e9c40): D1, D5 hold; D2, D3, D4 refuted. The
               single "found" (t = 118.1) is a false acceptance; the finder stalls on a resolved horizon from t = 136.
             - Szekeres (q0040, q0041): N64, N128 guard-stopped at tau 30.25, 37.47 (P17 refuted for N128); N256 one
               segment only (tau 21.2). P17 refuted for N128, P18 holds for N64 at tau 10 (entry 11); orders wait for the detached readers.
cards:       none used in batches 23-24. Shared queue (priority 2, waiting): q0067 a-szk-n256-cont (Szekeres N256 to
             tau 40; szekeres entry 12), q0068 a-s1l-half (S1L-h, A2H; periodic_threshold 19:25 PST); q0015 a-s1l-cont.
processors:  Szekeres readers: A-20261126-024724-425ed7f (N64/N128) ended and closed, figures unread;
             A-20261126-023245-1dd80ad (N128/N256, 1 core) still running; C3 particle-number leg A-20261126-024922-97a2f14
             (2 threads, prediction H, threshold_ball entry 15). Close each with `harness/bin/nrpic-run finish <id>`.
next:        1. Read q0067 and q0068 when they end (HANDOFF table): P17/P24 and A2H, figures looked at.
             2. Szekeres readers: P18-P21 (szekeres entry 13). 3. C3 particle-number leg (H); then the G2 package
                per 0043 (note sections, schematics, VERIFY, mosaic; collect/verify/report; verifier).
blockers:    C3 FAILED (defect not explained); C1 (ii) finder fails on P0L6; A2 FAILED (cause in the GR evolution,
             not named); Szekeres members do not reach tau = 40.
needs:       orch: none open (0043 answered the four questions). core: finder (finder-false-accept-and-stall-p0l6),
             core answered the PCS question (a property of the deposit rule; CIC exact at cell centres; acked).
offers:      periodic_threshold/scripts/a2_invariant.py (shift-invariant Jacobian sign, probe clock on crossing
             worldlines); threshold_ball/scripts/edge_compare.py; szekeres/scripts/analyse_code_runs.py.
budget:      card-hours batch 24: 0 used; queued ~0.8 (q0067, cap 2) + ~1.2 (q0068, cap 2). Processors: 1 core ~20 min.
