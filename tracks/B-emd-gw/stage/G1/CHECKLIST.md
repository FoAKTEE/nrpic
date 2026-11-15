# Checklist: B-emd-gw G1

Collected by `harness/bin/nrpic-stage collect B-emd-gw G1` on 2026-11-15T19:07:31Z from `coord/CHARTER.md` (last changed in b7b431dd) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: vacuum Z4c in periodic boxes (periodic_z4c, wave 1); semi-analytic Zel'dovich and ellipsoid baseline (run B-emd-gw-20261115-115752-840e994); AthenaK Newtonian mode on the same particles, pancake and ellipsoid (newton_tests, runs in EVIDENCE.md); stage/G1/STATUS.md
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: gw_diag validated on analytic fields and AthenaK vacuum output (wave 1; verifier C7, run B-20261115-170546-4507b05); the first-source pipeline reread independently by the lead to 9e-14 of the signal (run B-20261115-190007-e09a0d2); Newtonian analyses rechecked (run B-20261115-190015-4dd3416); stage/REVIEW-wave2.md
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: 14 messages of wave 1 (outbox/20261115T1340Z__*) and the wave-2 messages of this session; core answered the eight requests to core (message 20261115T1620Z, tracks/core/interfaces/REQUESTS_B.md on core/requests-b)

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: first_source/figs/scan_*.png, res_compare.png, late_rise.png; newton_tests/figs/*.png; baseline/figs; from the registered runs of EVIDENCE.md, looked at by the helpers and by the lead (stage/review_wave2/figs)
- [x] **C5** Interface documents
  - status: PASS
  - evidence: gw_diag/README.md (TT, energy, spectra, helicity, Weyl, readers), first_source/README.md (gauge piece G_tot), the request documents in outbox/ and core's answers REQUESTS_B.md; coord/INTERFACES/newtonian_mode.md used and tested

## Track-specific criteria of B-emd-gw for G1 (9.5 Track B: gravitational waves from EMD structure formation (S2))

- [ ] **C6** The two diagnostics agree on analytic linear waves
  - status: OPEN
  - evidence: met for waves along an axis in a flat periodic box (TT and Psi_4 agree with the exact wave and with each other to 1.8e-7 A; runs -113218-0ea0f74, -120128-7dfaa38, verifier B-20261115-170546-4507b05); oblique wave: generator fixed on core/requests-b, core's card run with gw_diag (message 20261115T1850Z), the track's own run owed; expanding-box wave with both diagnostics not run (OPEN.md items 1, 2)
- [x] **C7** The Newtonian baseline reproduces the scaling of the literature
  - status: PASS
  - evidence: lead's judgement: emitted-spectrum scaling sigma^(7/2), omega_peak ~ sigma^(3/2) reproduced by the semi-analytic baseline (run -115752-840e994; verifier run B-20261115-170518-c1b61a3); in AthenaK's Newtonian mode the single patch obeys E ~ (2 alpha)^(7/2) to 3e-14 (N3) and its crossing time and energy converge to the ODE (N1: t_x second order, Richardson within 5e-5; E first order, -9.7 percent at N = 128); rechecked in run B-20261115-190015-4dd3416. Not confirmed: Omega today ~ sigma^(7/2) of 2403.15126:1074 (verifier C8); N2 waits for core
- [x] **C8** Background error and constraint convergence with the stand-in matter
  - status: NA
  - evidence: struck by decision 0013 (particles do it directly); the particle FLRW background: lapse = a to 1.9e-7 (a = 4) and 7.0e-8 (a = 36), run B-emd-gw-20261115-115414-7ffbde1; Hamiltonian constraint in stage/G1/STATUS.md (corrected values)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C9** Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013)
  - status: PASS
  - evidence: applied: C8 struck; the N-body baseline runs in AthenaK's Newtonian mode (newton_tests); the multi-code row (shearing dust, GR against the Newtonian mode) is G2 work; item 3 amended (coord/notes/derivations_to_check.md, decision 0013)

## Minimum figures at G1 (brief 13.4)

- [ ] **C10** Schematic: Updated architecture
  - status: OPEN
  - evidence: the G0 architecture schematic exists (note/figures/schem_architecture.png); the updated one (Newtonian mode, G_tot, jitter and thin boxes now exist) is not drawn (OPEN.md item 3)
- [ ] **C11** Schematic: Data-flow diagram
  - status: OPEN
  - evidence: data-flow diagram not drawn (OPEN.md item 3)
- [x] **C12** Data figure: Baseline results
  - status: PASS
  - evidence: first_source/figs/scan_kk0.png, scan_secondgauge.png, res_compare.png; newton_tests/figs/pancake_east.png, ell_convergence.png, ell_selfsim.png
- [x] **C13** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: gw_diag/figs (wave 1), first_source/figs/t0_gauge.png, scan_null.png; stage/review_wave2/figs/rv_review_first_source.png, rv_review_newton.png

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, STATUS.md in stage/G1/; the lead's recheck is stage/REVIEW-wave2.md (task-given name); scoping text scope/SCOPE.md
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: every data figure of first_source, newton_tests and the review from a registered run with one script each (figstyle), looked at; the note's figures are rerun by nrpic-stage verify
- [ ] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: G1 schematics not drawn (C10, C11)
- [ ] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: note v0 exists and its checker passed (G0 C17); its G1 sections (first-source scan, Newtonian mode) are not written (OPEN.md item 4)
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: the verifier of wave 2 covered the G1 claims of wave 1 (VERIFIER.md C6-C8); the wave-2 G1 runs are rechecked only by the lead (REVIEW-wave2.md), not by an independent agent (OPEN.md item 5)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed predictions and runs on record: first_source/JOURNAL.md (P1 as worded, P4, P6 with G), newton_tests/JOURNAL.md (P1a, P1b, P2a, H1a, H1c, H1d-3, N1d, N1e), stage/review_wave2/JOURNAL.md (R5, R6); failed runs B-20261115-161656-03d75e1, -164104-886798f, -170149-75036cf kept
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten by the lead at the end of wave 2
