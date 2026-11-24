# G2 verification ladder of D-bh-dress (checklist C1)

Rows of brief section 10 (charter copy) that Track D owns, and the rows it depends on, with the
test run on the code paths D uses (release core-v0.6 unless stated), the criterion fixed before
the run, the outcome and the evidence. Paths relative to `tracks/D-bh-dress/`; run ids are
manifests in `runs/`. State of 2026-11-24 (lead, batch 11).

## Rows Track D owns

| Row (section 10) | D's test | Criterion (fixed before) | Outcome | Evidence |
|---|---|---|---|---|
| Black hole in a vacuum bubble (Einstein-Straus type): horizon mass does not change with the expansion | ES-1L against the matched vacuum control V-1L, faces +-768 M, plain 1+log, M/8, to 500 M | N: max |D_ES - D_V| on 100-500 M <= max(2 F_V(500), 1e-4) (g2long entry 1, commit 53afc1a) | HOLDS: 2.28e-4 against 2.51e-4 | D-20261121-203124-a34cf1f, -203131-8ee2a49; judge_long D-20261123-020550-f9a3482 |
| (same row, mesh) | ES-1L16 against V-1L16 (M/16 on +-3 M), to 300 M | H3: difference at M/16 not larger than at M/8 on the same window | HOLDS: 1.99e-4 against 2.28e-4 (100-300 M) | D-20261121-203151-37e7b2d, -203151-59c54fb; judge_long D-20261124-131138-0b8ffc5 |
| (same row, mesh) | ES-1L4 against V-1L4 (M/4) | P5 (entry 6) | PENDING: ES-1L4 restarted (job 5153) | D-20261123-022726-1b133af |
| (same row, finder) | tight finder re-search of the dumps (test FP, entry 10) | FP2-FP5 | see g2long entry 11 | D-20261124-130935-fdca920 |
| Self-similar secondary infall: density profile of the virialised region | AthenaK Newtonian mode (release), Q16 and Q16-256 (two resolutions) | QR1-QR5 (secondary_infall JOURNAL) | QR1, QR2, QR5 hold; QR3 per-bin and QR4 slope fail narrowly | D-20261121-205226-3cfbc20; analyses D-20261123-020626-183c254, -020756-e9922e7 |

## Track D's own G2 criterion beyond section 10: growth against flux and exact dust

| Test | Criterion | Outcome | Evidence |
|---|---|---|---|
| ES-FL (dust filling the bubble, M/8, 850724 particles, 500 M) | G: (iii) every 10 M bin of tau_rem <= 650 M within +-1 per cent of exact LTB; D2 (entry 1) | HOLDS: largest 0.62 per cent; D2 at all 960 samples | D-20261121-203150-15f2bad; esf_criteria D-20261123-020614-7ba5874 |
| ES-FL4 (M/4) | P12-P14 (entry 6) | PENDING: at 456 M of 500, job 5152 | D-20261123-022727-1c17e73 |
| ES-FLK (horizon excision kept to 6.4 M) | P7-P11 (entry 6) | PENDING: at 225.5 M of 400, job 5144 held behind the sequencer | D-20261123-022725-a553496 |
| ES-FLK4N, ES-FLKQ (4N, N/4), ES-FL16 (M/16) | N1-N4, Q1-Q3, L1-L4 (entry 10) | QUEUED after their smoke tests | entry 10 |

## Rows Track D depends on (owner)

| Row | What D takes | State |
|---|---|---|
| Geodesics on a fixed background (CORE) | pusher accuracy (E 1.2e-7, L_z 5e-6 after 1000 M on a mesh metric, scope/SCOPE.md section 6) | core ladder row 1 (core stage G2) |
| Oppenheimer-Snyder and its time reverse (CORE, A) | expanding-ball data and gauge | core ladder row 2 |
| LTB dust (A) | the exact LTB mass of ES-F/ES-FL (flux_tools/esf_data.py, esf_growth.csv) | D's own reference, checked in G1 (verifier_g1 V1) |
| Einstein-Vlasov steady states (CORE, C) | relaxation of 1e2-1e4-particle clusters | core ladder row 4, bracket only (decision 0030 item 3) |
| Kerr spike (D-pre-2, G1) | stationarity of the a = 0.8 spike in AthenaK | G1 (signed with reservation 3) |
