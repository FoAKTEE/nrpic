# STATUS of C-sidm

gate:        G0 PASS (signed 2026-11-20, coord/GATES.md); G1 NOT MET: both track-sheet
             criteria met (all tests of C-pre-1 incl. heat conduction T6-T8; baseline
             reproduced), open only C16 (working note G1 sections) and C17 (verifier's
             VERIFIER.md, package verify_g1 in progress) - stage/G1/OPEN.md
headline:    the collision operator passes every box test of C-pre-1 (heat conduction:
             kappa/kappa_1 = 1.019-1.025 at theta 0.003); the collapse of the collisional King
             runs is set by collisional contraction, not by the distance from the relativistic
             onset, and the outward drift of the collisionless controls is a mesh effect
last-result: lead review of wave 3 round 1 (stage/REVIEW-wave3.md): heat T7 rows and
             extrapolations recomputed exactly (C-20261121-075535-b35b8fb); every t_c of 15
             collisional runs recomputed (C-20261121-075336-49f92da); CC1 at Kn = 10 cell seeds
             2, 3 collapse at 185.29 and 178.86 M, sd 3.4 M, mode effect not shown
             (C-20261121-075202-1a37fb9); CC2 control on M/8 keeps 0.10-0.25 of the M/4
             excursion and contracts slowly after 200 M (C-20261121-075359-26e3b31); D3
             (y0 = 0.26) collapses at Kn = 1 at 100.5 M; failed predictions L17, L19, decisive
             entry 10 (job 5), drift M8.2
next:        1. note: finish the G1 sections from the uncommitted state (HANDOFF), registered
                run_all, compile, checker --compile, pages read (closes C16)
             2. verify_g1 to VERIFIER.md (C17); the lead answers each WRONG / NOT CONFIRMED;
                then G1 to the independent reviewer
             3. card: drift run (iii) CC1 at M/8, run (v) N = 1e4, then decisive D2 (collision
                cell size); they fix the mesh and cost of the G2 scan
blockers:    none outside the track; usage-limit windows (decision 0020)
needs:       orch: next batch with note, verify_g1 and a 3 card-hour G2 package (outbox
             20261121T081156Z next-batch); core: READY/FORMATS text for heat conduction
             (20261121T081156Z heat-conduction-tested), collisions on several ranks (low
             priority), earlier: ADM-energy diagnostic, collisions on refined meshes, format
             findings (20261119T1517*); kb: conductivity and DSMC sources
             (20261121T081156Z conductivity-sources)
offers:      collision tests and references: collide/ (SPEC, TESTS with 2a/2b wording, 62
             reference tests); heat-conduction references and drivers: heat/scripts/
             (isobaric.py, run_mode.py, an_mode.py); box-test drivers: box_tests/scripts/;
             static Einstein-Vlasov solver and samplers: equilibria/; Juttner and F21 pulsation
             onsets: models/fluid_onset.py; growth estimator growth_fit_v2: models/growth.py;
             King and F21 b = 0.1 particle models at N = 1e4, 1e5; D3 King y0 = 0.26 model
             (C-20261120-222427-6b27eea); history reader and control fits:
             stage/review_wave3/rv_clusters.py
budget:      nrpic-run budget 2026-11-21: G1 used 0.01; G2 used 5.86, 39.14 left of 45
             (decisions 0006, 0014). Round 1 of wave 3: 4.13 card-hours (heat 0.52, decisive
             2.92, drift 0.69); this lead session 0 card-hours, processors only
