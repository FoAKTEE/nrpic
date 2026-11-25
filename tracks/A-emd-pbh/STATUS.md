# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md). G2 in progress: interim
             package stage/G2 (9 PASS, 10 OPEN, 1 FAIL: C3 constraints); NOT ready for review (stage/G2/OPEN.md).
headline:    The code finds the finite-duration black-hole threshold of the expanding ball where the exact solution puts it:
             on M/32 the bracket at t_end = 45 is (0.40, 0.42], interpolated 0.4103 against exact 0.4103; on M/64 the
             member 0.42 is a black hole too (tau_det 43.705, exact 43.656), so the upper end holds on the finest mesh.
last-result: batch 17 (2026-11-25): C-d0.42 (A-20261122-173202-f98c79f, M/64) closed DONE at tlim 51; analysis
               A-20261125-115027-17b419e: horizon in all 163 searches from t = 45.906, tau_det 43.705, ddet -0.0135,
               no guard stop, 2.20 s per cycle. T4 mesh-C half REFUTED as written (ddet not halved: both meshes below
               one search interval; dmmed +2.36e-2 against +2.8e-3, medians over different windows). Common-window
               measure A-20261125-115550-fe60ff1: line MOTS mass error 2.1e-3 (C) against 5.2e-3 (B); finder masses of
               C and B agree within 3.3e-3 after t = 46.75. Slice measures halve (trapping -0.096 vs -0.209).
             batch 11: threshold scan T1-T3 hold (A-20261124-131120-5c974ce); K, K2, K3 refuted (constraint floor before
               t ~ 6, cause not named); periodic P0L: slice traps at r 0.075 but finder finds no horizon.
cards:       shared queue (decision 0033): q0013 a-p0l6 (p2, in Slurm, job 5282 pending, run A-20261125-044641-7d5bd16);
               q0015 a-s1l-cont (p5, waiting); q0040 a-szk-n64-128 and q0041 a-szk-n256 (p2, added batch 17, Szekeres
               card series for C1). q0014 a-cd040 REMOVED (no G2 item waits for it). q0012 done.
processors:  A-mesh guard stop judged (A-20261125-120158-b76bfe3): alpha_exc 0.3 passes it to t = 48.5 (G3 refuted "stops
             like G1"); no persistent horizon on M/16 in any variant. K4 (threshold_ball entry 10) not started.
next:        1. Read q0040/q0041 (Szekeres P17-P21, analyse_code_runs.py) and q0013 (P0L6, D1-D5) when they end.
             2. C3: K4 on processors (command at the end of threshold_ball/JOURNAL.md entry 10); orch ruling on 0.1 bound.
             3. Package items without cards: threshold_ball/README.md, VERIFY list (C6), ladder schematic (C10),
                schematics on v0.7 (C16), note G2 sections (C17); C18 verifier (asked of orch).
blockers:    C1 needs Szekeres (queued), the periodic horizon (queued) and a ruling on the oblate/prolate row (asked).
             C3 FAILS as the criterion is written (0.1 bound exceeded from t = 0 in every run).
needs:       orch: rulings on the 0.1 constraint bound (2026-11-24) and on the oblate/prolate row; a C18 verifier session
               (outbox 20261125T115950Z).
             core: none open beyond periodic-gamma-driver-step (dt_gauge in v0.7: use it in new Gamma-driver decks).
offers:      threshold_ball/scripts/analyse.py, compare_tb.py, t4_common.py (common-window mesh comparison),
               constraint_conv.py; periodic_threshold/scripts/job2_q.py, line_trapped.py.
budget:      card time of C-d0.42 at finish (nrpic-run finish, see manifest); batch 17 queued ~1.6 card-h (Szekeres) and
               withdrew 14 (C-d0.40). Processors this session: 1 core, minutes (analyses only).
