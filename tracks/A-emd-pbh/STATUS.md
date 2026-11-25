# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md). G2 in progress: interim
             package stage/G2 (9 PASS, 10 OPEN, 1 FAIL: C3); NOT ready for review (stage/G2/OPEN.md).
headline:    The code finds the finite-duration black-hole threshold of the expanding ball where the exact solution puts
             it: on M/32 the bracket at t_end = 45 M (proper time of the core edge) is (0.40, 0.42], interpolated 0.4103
             against exact 0.4103; on M/64 the member 0.42 is a black hole (tau_det 43.705, exact 43.656).
last-result: batch 19 (2026-11-25):
             - C18 answered (A-20261125-151126-7f79a83, threshold_ball entry 12): every classification and persistence
               time stands when read from horizon_status_0.txt; the near-threshold mass medians (B-d0.42, B-d0.40,
               B-d0.35, C-d0.42) and both A medians are withdrawn: the tracked particles bound the exact mass only to a
               bracket (median width 1e-3 to 1e-2), the verifier's numbers stand. conv_ball ddet orders 1.2-1.5 and
               1.75-2.1 (interpolation spread). P12a, P12b hold; P12c, P12d refuted.
             - K4 (A-20261125-120525-8fb946e, analysis A-20261125-150851-5545f8e): K4a-c hold; the constraint floor
               does not depend on the step or the source extrapolation. K4 is not the smoothed-edge test; C3 stays FAIL.
             - A2 from S1L (A-20261125-151629-bb77171, -151715-66f198f): first crossing along z as predicted, but at
               6.1-6.4 t_H against the Zel'dovich band [3.4, 5.0] on every clock: prediction refuted, cause not named.
             batch 17: C-d0.42 closed, black hole by the rule; T4 mesh-C half refuted.
cards:       shared queue (decision 0033): q0013 a-p0l6 (p2): chain A-20261125-044641-7d5bd16 at t = 138 of 140, Slurm
               5296 pending; q0040 a-szk-n64-128, q0041 a-szk-n256 (p2, waiting); q0015 a-s1l-cont (p5, waiting; not
               needed for A2). None added this session.
processors:  this session: analyses only (1-4 cores, minutes); K4 run closed with nrpic-run finish.
next:        1. A2 cause: S1 particles under `<particles> pusher = newton`, `newton_poisson = fft` on processors, first
                crossing by a2_crossing.py (prediction first).
             2. C3: the smoothed-edge test (prep_bh.py --edge-w, meshes A and B, processors; prediction first), after
                orch's answer to outbox c3-smoothed-edge-test.
             3. Read q0013 (P0L6: D1-D5; first status-file find at t = 118.1) and q0040/q0041 (Szekeres P17-P21).
blockers:    C1 needs Szekeres (queued), the periodic horizon (in Slurm) and an explanation of A2's lag.
             C3 FAILS as written (bound 0.1 exceeded from t = 0 on every mesh).
needs:       orch: confirm how C3 is judged (K4 was not the smoothed-edge test; outbox 20261125T151524Z).
             core: none open.
offers:      threshold_ball/scripts/c18_answer.py (status-file finds, exact-mass bracket of a tracked set, ddet
               interpolations); periodic_threshold/scripts/a2_crossing.py (first shell crossing from particle snapshots).
budget:      no card time used or queued this session.
