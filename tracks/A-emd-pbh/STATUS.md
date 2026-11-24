# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md). G2 in progress: interim
             package stage/G2 (9 PASS, 10 OPEN, 1 FAIL: C3 constraints); not ready for review.
headline:    The code finds the finite-duration black-hole threshold of the expanding ball where the exact solution puts it:
             on mesh M/32 the bracket at t_end = 45 is (0.40, 0.42] and the interpolated threshold 0.4103 equals the exact
             0.4103 (horizon times within 0.05 M of exact at the bracket). The periodic box now runs stably at cfl 0.5 on the
             refined mesh, but its horizon (coordinate r ~ 0.075, under four finest cells) is not found by the finder.
last-result: batch 11 (2026-11-24): threshold scan judged, A-20261124-131120-5c974ce: T1-T3 hold (8 mesh-B members, |ddet|
               <= 0.14 M, |dmmed| <= 9.4e-3); T4 holds only through guard stops on mesh A; T5 (C-R1.25 ddet 0.040 vs 0.017)
               and T6 (constraint ratio 0.3-3 > 0.1; A guard stops) partly refuted; first-detection mass excess is in the
               slice, not the finder (finder vs line MOTS within 0.3-1.5 per cent).
             constraints: K and K2 refuted (A-20261124-132249-2e6b5f2, -132342-d5dc06e): norms flat in mesh and particle
               number before t ~ 6.
             periodic job 2: P0L to t = 140 (A-20261122-235305-4ea0aa5); remedy Q1a/c/d, Q2, Q3 hold (A-20261124-130507-
               10510ac); P3 refuted (no horizon found); F1: slice traps from t = 132 at r 0.075 (A-20261124-131430-d1a2ee6);
               F2: finder converges from no start radius (A-20261124-131232-e7b58f8). Posted to core.
cards:       all in the shared queue (decision 0033; batch 12): q0012 C-d0.42 cont. (p2), q0013 P0L6 (p2), q0014 C-d0.40 (p2),
               q0015 S1L cont. (p5); no sequencer of this owner runs (HANDOFF, "Card runs and what reads them").
processors:  A-20261124-132016-ecf12c3 G1-G3: G1 repeats the card stop exactly, G2 stops 0.5 M later elsewhere; G3 ended
             (run.log exit 0, 06:31 PST), not yet judged or closed. K4 (entry 10) not started.
next:        1. Read C-d0.42 and S1L when they end (HANDOFF commands); judge T4 (mesh C) and S1-S3; then P0L6 (D1-D5).
             2. Constraint floor (C3): smoothed-edge top hat on two meshes (prep_bh.py --edge-w), predictions first.
             3. G2 package items: verifier of conv_ball + threshold_ball numbers, ladder schematic, slice mosaic, note G2
                sections, schematics on v0.6; Szekeres card series.
blockers:    none in the source for the ball. Periodic horizon: resolution (six-level run queued); if the finder still fails,
             a request to core. Mesh A at threshold: guard stop, cause not named.
needs:       orch: ruling on the 0.1 constraint bound of SCOPE section 3 (outbox constraint-bound-ruling).
             core: none open beyond periodic-gamma-driver-step (W31 in work) and bh1r-inte-deficit-two-levels.
offers:      threshold_ball/scripts/analyse.py + compare_tb.py (finder persistence, ddet, dmmed, line MOTS vs finder,
               constraint ratio); constraint_conv.py; periodic_threshold/scripts/job2_q.py (Gamma-driver checks from
               histories with restart-repeated records), line_trapped.py (Misner-Sharp trapped spheres on a z4c line);
               threshold_ball/scripts/sequencer.sh (now logs why it waits).
budget:      card-hours G2 (nrpic-run budget, 05:40 PST, finishes still running): see HANDOFF; this session's own card use 0
               (continuations add ~3-5 card-h; queue_b11 asks 21, model ~13.5). Processors: <= 6 cores.
