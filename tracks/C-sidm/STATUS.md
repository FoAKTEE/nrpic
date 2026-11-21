# STATUS of C-sidm

gate:        G0 PASS (signed 2026-11-20, coord/GATES.md). G1: every checklist item met (C16
             note v1, C17 VERIFIER.md answered, batch 4a); package complete for the
             independent review, requested (outbox gate-status-batch4a); not passed by the
             lead. Limits: stage/G1/OPEN.md
headline:    the collision operator passes every box test of C-pre-1 (heat conduction
             kappa/kappa_1 = 1.019-1.025 at theta 0.003); a fresh verifier found no wrong
             number, only definitions now named (TESTS 2c, strict T9 reading failed on
             record). For G2: the outward drift of the M/4 controls is the mesh, but on M/8
             the stable King control contracts steadily to 680 M, so block A waits
last-result: lead review of batch 4a (stage/REVIEW-wave3.md sections 9-12): T10 count
             (C-20261121-155049-ecf8893) and T9 KS (C-20261121-155116-ba83d16) confirmed;
             note checker --compile and ledger rows (C-20261121-155226-8ea9e47); CC1 on M/8
             keeps 0.138 of the M/4 excursion, energy diffusion recomputed with own cells
             0.97-1.01 of the package (C-20261121-155049-ecf8893); run (vi): CC2 on M/8
             alpha_c -0.0216, r50 -6.3 % at 680 M, no turn, no collapse
             (C-20261121-140023-b0f113e, C-20261121-163109-c8fff37); failed predictions
             L28 (interval), drift VI.2, M8.2', M8.5', D2.2
next:        1. drift run (v), N = 1e4 on M/4 (0.3 card-hours; command drift/README.md
                "Pending runs"; predictions N.1-N.6): does the M/8 contraction scale as 1/N?
             2. G1 independent review (orch); answer its findings
             3. then block A of threshold_scan/SCAN.md at the N and mesh (v) points to
                (14-23 card-hours, announced first), and decisive D2 (collision cell size)
blockers:    none outside the track; the cause of the M/8 contraction blocks block A
needs:       orch: G1 review (20261121T*__to-orch__gate-status-batch4a), next batch
             (20261121T163254Z next-batch-drift-close); core: ADM-energy diagnostic,
             collisions on several ranks (accepted, no date), format findings F1-F3
             (deferred); kb: conductivity and DSMC sources (received, waits for claims_tracks)
offers:      collision tests and references: collide/ (SPEC, TESTS with 2a/2b/2c wording, 62
             reference tests); heat-conduction references and drivers: heat/scripts/;
             box-test drivers: box_tests/scripts/; static Einstein-Vlasov solver and
             samplers: equilibria/; Juttner and F21 pulsation onsets: models/fluid_onset.py;
             growth estimator growth_fit_v2: models/growth.py; King and F21 b = 0.1 particle
             models at N = 1e4, 1e5; M/8 decks and drift readers: drift/scripts/; own
             readers of histories and trajectory files: stage/review_wave3/rv_batch4a.py
budget:      nrpic-run budget 2026-11-21 16:00 UTC: G1 used 0.01; G2 used 6.54, reserved
             0.90 (run (vi), now finished: 0.87), left 37.56 of 45. This lead session
             submitted no card job (0 card-hours); drift package 2.25 of its 3.0 cap
