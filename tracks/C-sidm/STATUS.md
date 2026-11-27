# STATUS of C-sidm

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2
             package complete for the independent review: 19 of 20 items pass, C18 (fresh
             verifier) open; nrpic-stage verify --no-checksums PASS, report verdict FAIL only on
             C18 and the missing VERIFIER.md; verify --full started for the review (log
             scratch/C-sidm/tmp/verify_full_g2.log)
headline:    the collisionless threshold of the King b = 1 family lies in (0.324, 0.344), around
             the turning point y_max = 0.334032, with the same fates at N = 1e6 on M/8 and M/16
             and with shift_eta 2.0 and 1.0, and at N = 1e5 on M/8. Collapse = lapse marker
             alpha_min = 0.3; no run had the horizon finder
last-result: batch-32 analyses (JOURNAL 2026-11-27T08:46Z; figures read):
             - B20.1 held: A16b324 (M/16) holds 600 M, block means -0.0171..+0.0107
               (C-20261127-084538-8e98060)
             - B20.3 second half held: N6b324e1 holds 600 M, central lapse within 1.4e-5 of
               shift_eta 2.0 (C-20261127-084417-79c0e4d)
             - note: G2 figures (threshold legs, slice mosaic, ladder, schematics at G2) from
               run C-20261127-084828-b6ca5ce; compiled, checker clean apart from G1 exceptions;
               N5.1-N5.3 held
runs:        none of C-sidm queued or running; A16b324 (6.3844) and N6b324e1 (2.6175 card-hours)
             closed this session
next:        1. fresh G2 verifier (orch): recompute the fates of the eleven threshold runs and
                the band readings first (stage/G2/OPEN.md)
             2. read verify --full (scratch/C-sidm/tmp/verify_full_g2.log) before the review
             3. G3 scope: collapsed mass fraction against Kn on thermal cores, with the horizon
                finder (diagnostics and polishing of core-v0.8) and at least three seeds
blockers:    none
needs:       orch: a fresh G2 verifier; the G3 allotment once G2 is judged
offers:      readers longruns/scripts/{nseries,d2_analysis,blockA_delta,horizon_audit}.py; note
             scripts fig_g2_threshold.py, fig_g2_mosaic.py (particle-slab mosaic from snapshots);
             N = 1e6 King samples of y0 0.324, 0.334032, 0.344; collision tests (collide/)
budget:      G2: 54.76 card-hours used, 0 reserved, 25.24 left of 80 (2026-11-27 08:53Z)
