# What G2 of A-emd-pbh still lacks (lead of batch 28, 2026-11-26 afternoon)

State: every run the rulings asked for before the verifier has ended and been judged (decision 0043 item 1). What
remains open is (a) the failures on record with their rulings, which stay failures, (b) the fresh verifier of the
whole gate (C18), and (c) the last Szekeres readings, which only add rows to a passed item.

| item | state | what is open | serves it |
|---|---|---|---|
| C1 (i) expanding ball, threshold of the ball | passed | | conv_ball A-20261121-120257-a2eb839, threshold_ball A-20261124-131120-5c974ce |
| C1 (ii) LTB peak P0L6 | FAILED on record, horizon part (decision 0043 1(b)) | shells r0 >= 1.5 follow LTB to 1-4 per cent; the finder accepts one false surface (t = 118.1) and stalls on a resolved horizon (A-20261126-022753-f9e9c40) | core's finder fix (outbox finder-false-accept-and-stall-p0l6); a periodic science run that needs a horizon waits for it; G2 does not |
| C1 (iii) Szekeres | passed with clauses refuted on record (szekeres entries 11, 13) | P24 and the tau 30/40 rows of N256: readers A-20261126-212138-49b9a2d (tau 30) and A-20261126-212141-7eeb046 (tau 40), detached, ~1 h each, started 13:21 PST | next session: close both, judge P24, P19/P20 at tau 30 (entry 14) |
| C1 (iv) A2 | FAILED as written (decisions 0040 item 7, 0043 1(d)) | A2H HOLDS (A-20261126-213147-f274b2e: crossing (13.85, 14.36] t_H in [12.5, 15.2]): the lag scales as an effect first order in the amplitude; the effect within that class is not named | none before G2 |
| C3 constraints | FAILED as written (decisions 0039 2(c), 0043 1(a)) | cause of the floor UNEXPLAINED: mesh leg order ~0.35 (G refuted, A-20261126-022624-c663e0f); particle-number leg H holds for the evolution (x8 particles change t = 1-2 by 2-8 per cent, A-20261126-212340-4ea9fb2), so sampling is excluded; t = 0 clause of H refuted (x9.6, interior CIC smoothing) | **retest after core's source session (after 2026-11-27)** that fixes the two deposit defects at level faces (compensation not conservative across a level face; deposit_fine_shape with CIC not inert there; tracks/core/NEXT_SOURCE.md items 0 and 0b): rerun S2c-A (M/16) and S2c-B (M/32) to t = 1 on the fixed build, same reading (edge_compare.py), prediction first |
| C5, C14 package documents | written this session | | STAGE_REPORT.md by nrpic-stage report |
| C6 rerun list | written | | stage/G2/RERUN.md (commands of every G2 number from the manifests), stage/G2/VERIFY |
| C10, C16 schematics | drawn | | note schem_ladder.png, schem_architecture.png (core-v0.8), run A-20261126-213903-08eaf25 |
| C11, C13 figures | drawn | gauge leg not run (charter 9.2: "gauge or boundary"; boundary leg chosen) | fig_g2_convergence, fig_slice_mosaic (same run) |
| C17 note G2 sections | written, compiled, checker run (see CHECKLIST C17) | | note/main.tex Sec. "Verification of the code paths" |
| C18 fresh verifier | OPEN | VERIFIER-C18.md covers conv_ball and threshold_ball only; nothing yet for Szekeres, A2/A2H, P0L6, the smoothed edge and the note's G2 ledger | the verifier of the whole gate (request to orch) |

Failed criteria that stay failed: C3, A2, C1 (ii) horizon part; earlier T4, T5, T6, K, K2, K3, F1, F2, G, AZ1's second
clause, D2-D4, A2X's bound. New in batch 28: P17's lapse clause on N128/N256, P18 for N256 at tau 10 (better than
predicted), P21 at tau 20, H's t = 0 clause.
