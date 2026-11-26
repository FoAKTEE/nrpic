# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21. G2 NOT PASSED on the independent review
             (coord/GATES.md; decision 0047; stage/G2/GATE_REVIEW.md, batch 30): the threshold as defined at G0
             cannot be measured with the present capability in either set-up. Five conditions for the next review
             (0047 item 2; state in stage/G2/OPEN.md): (a) cause of the constraint floor and the section-3 bound met
             at the bracket, falling with the mesh; (b) finder on the restart files of the periodic chain and the
             triaxial run; (c) cause of the triaxial lag named; (d) one triaxial run to a found horizon with the
             bound; (e) corrections. No amplitude is compared with arXiv:2609.14218 before (c).
headline:    (b) partly met on processors: the core-v0.8 finder finds P0L6's horizon at t = 140 from the deck's
             start radius with 4000 flow iterations (area mass 6.30 at r 0.104; line 6.28 at 0.103) and S1L's at
             t = 220 from r 0.16 (10.73 at 0.161), but not S1L from the decks' radii; no false acceptance in 139
             searches (A-20261126-233542-fd9f9f0, A-20261126-234232-84f3e98). (a) narrowed: no first-step jump;
             the early H rise is the t = 0 momentum residual and converges; the floor is a source acting during
             the evolution (A-20261126-234222-dbf8624, A-20261126-234642-8a4784b).
last-result: batch 31 (15:30-16:4x PST; processors only, 0 card-hours):
             - FP: FP0, FP1, FP2, FP3, FP5 hold; FP4 refuted for P0L6 (the finder works with more iterations).
             - FPb: FP6 refuted (S1L first trapped round sphere in t (180, 190] = (18.4, 19.4] t_H); FP7, FP8 hold.
             - C3-F: CF0, CF2 hold; CF1 refuted as written (S_x = 0 on the line at t = 0; normalization wrong).
             - C3-G (frozen gauge, S2c-A to t = 1): see threshold_ball entry 17 / HANDOFF.
             - S1-S3 of S1L job 2 judged (A-20261126-234332-ec02d47): S1, S3 hold; S2 refuted as written.
             - Corrections (e): note V.A-V.D, VI, Summary, Fig. 7(a) ticks, Table V ranges and signal; READMEs;
               CHECKLIST C9, C18 (PASS), C21-C23 (SCOPE section 7, open); EVIDENCE, OPEN; note run
               A-20261126-234358-f761d8d, compiled, 0 undefined, 0 overfull.
             - Full checksum pass of the stage check (gate reviewer, 3fcd428): PASS, every byte read; kept.
cards:       none submitted; nothing of A in the shared queue.
processors:  nothing running at the end (C3-G finished or listed in HANDOFF).
next:        1. Core's answers: deposit fixes at level faces, finder request finder-slow-convergence-box; then the
                condition-(a) retest on two meshes to the horizon (cards, prediction first).
             2. C3: the review's offline-H test from a 3D dump; frozen lapse with live shift if C3-G fell.
             3. Box decks for G3: flow_iterations_0 = 4000 with polishing; a start rule from round-sphere scans.
blockers:    G2 not passed; C3 cause unnamed; S1L's horizon not found from the decks' start radii; A2 lag unnamed.
needs:       core: deposit fixes; finder convergence advice and the t = 118.1 false-acceptance question.
             orch: a processor session for the next C3 tests; cards for (a) after core's fixes.
offers:      periodic_threshold/scripts/finder_probe_box.py (restart-file finder probe with round-sphere scan,
             --replot), threshold_ball/scripts/c3_first_step.py (H and M_x line ratios every cycle).
budget:      card-hours batch 31: 0. Processors: up to 6 cores, ~75 min.
