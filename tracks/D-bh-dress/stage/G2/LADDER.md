# G2 verification ladder of D-bh-dress (checklist C1)

Rows of brief section 10 (charter copy) that Track D owns, and the rows it depends on, with the
test run on the code paths D uses (release core-v0.6 unless stated), the criterion fixed before
the run, the outcome and the evidence. Paths relative to `tracks/D-bh-dress/`; run ids are
manifests in `runs/`. State of 2026-11-24 09:30 PST (lead, batch 11b); the rows pending then were brought to the final
state of the signed package on 2026-11-27 (lead, batch 34; gate review correction b).

## Rows Track D owns

| Row (section 10) | D's test | Criterion (fixed before) | Outcome | Evidence |
|---|---|---|---|---|
| Black hole in a vacuum bubble (Einstein-Straus type): horizon mass does not change with the expansion | ES-1L against the matched vacuum control V-1L, faces +-768 M, plain 1+log, M/8, to 500 M | N: max |D_ES - D_V| on 100-500 M <= max(2 F_V(500), 1e-4) (g2long entry 1, commit 53afc1a) | HOLDS: 2.28e-4 against 2.51e-4 | D-20261121-203124-a34cf1f, -203131-8ee2a49; judge_long D-20261123-020550-f9a3482 |
| (same row, mesh) | ES-1L16 against V-1L16 (M/16 on +-3 M), to 300 M | H3: difference at M/16 not larger than at M/8 on the same window | HOLDS: 1.99e-4 against 2.28e-4 (100-300 M) | D-20261121-203151-37e7b2d, -203151-59c54fb; judge_long D-20261124-131138-0b8ffc5 |
| (same row, mesh) | ES-1L4 against V-1L4 (M/4) | P5 (entry 6) | FAILED (on record): 4.57e-3 at 300 M; M/4 lies outside the convergent regime and is labelled so (decision 0039 item 4) | D-20261123-022726-1b133af; judge_conv D-20261125-122227-3eb563a |
| (same row, finder) | tight finder (mass_tol 1e-9) re-search of the restart dumps of V-1L, V-1L16, V-1L4, ES-1L, ES-1L16 (tests FP, FP-ext; entries 10, 11) | FP1-FP5, FP-ext (i), (ii) | FP1, FP2, FP3, FP5, FP-ext (i) HOLD: vacuum drift 1.8e-5 (M/8, to 500 M), 3.9e-6 (M/16); the 1.2e-4 plateaus are the finder's stopping rule. Null difference <= 7.3e-5 (M/8, 100-500 M), <= 5.5e-5 (M/16, 100-300 M), no trend; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes (test FE, entry 17, D-20261124-175356-0f40f1a). FP4 REFUTED (offset changes sign over M/4, M/8, M/16); FP-ext (ii) missed its 5e-5 bound, not refuted (g2long entry 14) | D-20261124-130935-fdca920, -140606-286a302; fp_analyse D-20261124-172508-c847ee4 |
| Self-similar secondary infall: density profile of the virialised region | AthenaK Newtonian mode (release), Q16 and Q16-256 (two resolutions) | QR1-QR5 (secondary_infall JOURNAL) | QR1, QR2, QR5 hold; QR3 per-bin and QR4 slope fail narrowly | D-20261121-205226-3cfbc20; analyses D-20261123-020626-183c254, -020756-e9922e7 |

## Track D's own G2 criterion beyond section 10: growth against flux and exact dust

| Test | Criterion | Outcome | Evidence |
|---|---|---|---|
| ES-FL (dust filling the bubble, M/8, 850724 particles, 500 M) | G: (iii) every 10 M bin of tau_rem <= 650 M within +-1 per cent of exact LTB; D2 (entry 1) | HOLDS: largest 0.62 per cent; D2 at all 960 samples | D-20261121-203150-15f2bad; esf_criteria D-20261123-020614-7ba5874 |
| ES-FL4 (M/4) | P12-P14 (entry 6) | P12 HOLDS with its own-mesh control (V-1L4 held at its last value after 299 M; 280 D2 samples lie within the control), fails with the M/8 control; P13 FAILED as written (growth 10-43 per cent below M/8); P14 holds; outside the convergent regime (g2long entry 20) | D-20261123-022727-1c17e73; esf_criteria D-20261125-121123-143a007 |
| ES-FLK (horizon excision kept to 6.4 M) | P7-P11 (entry 6) | P7-P10 HOLD (excision on to 399.5 M, all 119848 removals by reason 3; (iii) bins 0.16-0.25 per cent after 280 M: the step of ES-FL is the end of excision), P11 (cost) FAILED; criterion G of FK: 50 bins, largest 0.249 per cent, D2 at every sample, D3 no violation (smallest value -1.4e-4 inside the allowance -3e-4) (g2long entry 19) | D-20261123-022725-a553496; fk_compare D-20261125-115637-7ee26c1; esf_criteria D-20261125-115647-fd2f3f7 |
| ES-FLK4N, ES-FLKQ (4N, N/4), ES-FL16 (M/16) | N1-N4, XN, Q1-Q3, XQ, L1-L5 (entries 10, 12, 15) | all HOLD (g2long entries 22, 26, 27); criterion G at 4N (largest bin 0.239 per cent), N/4 (0.290; D3 fails after ~220 M, on record), M/16 (38 bins to 300 M, 0.485, own control V-1L16); particle leg ordered, window ratios 1.9-3.1; mesh leg two members inside the regime, no order; M/16 - M/8 envelope 1.0e-3 with a systematic part +5.8e-4 over 250-299 M | D-20261124-134157-b17938b, D-20261124-172725-2f426b6, D-20261124-172745-72472ed; esf_criteria D-20261125-122827-c5735f8, D-20261126-054616-a13a888, D-20261126-055158-30ae09c; conv3 D-20261126-055249-505b079 |

## Rows Track D depends on (owner)

| Row | What D takes | State |
|---|---|---|
| Geodesics on a fixed background (CORE) | pusher accuracy (E 1.2e-7, L_z 5e-6 after 1000 M on a mesh metric, scope/SCOPE.md section 6) | core ladder row 1 (core stage G2) |
| Oppenheimer-Snyder and its time reverse (CORE, A) | expanding-ball data and gauge | core ladder row 2 |
| LTB dust (A) | the exact LTB mass of ES-F/ES-FL (flux_tools/esf_data.py, esf_growth.csv) | D's own reference, checked in G1 (verifier_g1 V1) |
| Einstein-Vlasov steady states (CORE, C) | relaxation of 1e2-1e4-particle clusters | core ladder row 4, bracket only (decision 0030 item 3) |
| Kerr spike (D-pre-2, G1) | stationarity of the a = 0.8 spike in AthenaK | G1 (signed with reservation 3) |
