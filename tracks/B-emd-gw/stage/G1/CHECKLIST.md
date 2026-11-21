# Checklist: B-emd-gw G1

Collected by `harness/bin/nrpic-stage collect B-emd-gw G1` on 2026-11-21T06:41:54Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: vacuum Z4c in periodic boxes (periodic_z4c, wave 1); linear waves of test F (flat, oblique) and X (expanding box) with both diagnostics (waves, runs in EVIDENCE.md); semi-analytic Zel'dovich and ellipsoid baseline (run B-emd-gw-20261115-115752-840e994); AthenaK Newtonian mode, pancake and ellipsoid (newton_tests) and the EMD random-field box at 32^3 and 64^3 (population, runs B-20261119-143828-0ef9b5b, -143832-85cbe25, -145324-525e4fd)
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: gw_diag validated on analytic fields and AthenaK output (wave 1; verifier run B-20261115-170546-4507b05); criterion-1 pipeline read three times: waves (B-20261119-164402-7438a99, B-20261120-221708-d8eae03), verifier3 with its own code (B-20261121-025826-80973e3, -030121-58fe5dc), the lead's third reading of X at N = 64 (B-20261121-063617-6183015, -063835-826c461); first-source pipeline reread by the lead (B-20261115-190007-e09a0d2) and by verifier2 (B-20261119-142332-dd28d1d); stage/REVIEW-wave2.md, stage/REVIEW-wave3.md
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: 14 messages of wave 1 and the wave-2 messages (outbox/); core answered in tracks/core/interfaces/REQUESTS_B.md and released the oblique generator, double-precision output and jitter in core-v0.4 (tag on f9323185); wave-3 requests in outbox/20261121T*

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: first_source/figs (scan, res_compare, late_rise, conv_null, conv_delta, null_spectrum); waves/figs (final_*, x10_check); newton_tests/figs; population/figs; all from registered runs, looked at by the helpers and the lead (stage/review_wave2/figs, stage/review_wave3/figs)
- [x] **C5** Interface documents
  - status: PASS
  - evidence: gw_diag/README.md (TT, energy, spectra, helicity, Weyl, readers; gwdiag/binio.py reads single and double precision, commit 5499ec6c); first_source/README.md (gauge piece G_tot); requests and core's REQUESTS_B.md; coord/INTERFACES/newtonian_mode.md and the core-v0.4 interfaces used

## Track-specific criteria of B-emd-gw for G1 (9.5 Track B: gravitational waves from EMD structure formation (S2))

- [x] **C6** The two diagnostics agree on analytic linear waves
  - status: PASS
  - evidence: met for both set-ups [lead's judgement, verified]: test F (k = 2 pi (1,1,1), N = 16-64) and test X (tensor mode in the matter-era box, N = 16-64, x10): TT projection and Weyl/Psi_4 recover amplitude, phase and both polarizations against the exact solutions with the errors of the code's stencils and integrator (F within 2.1 percent of the symbol-plus-RK4 prediction; X cross within 0.5 percent of the RK4()4[2S] prediction); the diagnostics agree to <= 6.4e-11 (F, forward combination; theta^6/1120 with h alone) and 2.4e-8 (X); X plus at N >= 48 is rounding-limited (1/A, x10 run B-20261119-155758-458cf17). Runs: waves B-20261119-142016-ee73a03, -142233-70d5043, -142021-8f4c441, -142234-85da208, -142124-feb2daf; analyses -164402-7438a99, B-20261120-221708-d8eae03; independent verifier stage/G1/verifier3/VERIFIER.md section 4; lead's recheck stage/REVIEW-wave3.md
- [x] **C7** The Newtonian baseline reproduces the scaling of the literature
  - status: PASS
  - evidence: lead's judgement: emitted-spectrum scaling sigma^(7/2), omega_peak ~ sigma^(3/2) reproduced by the semi-analytic baseline (run -115752-840e994; verifier run B-20261115-170518-c1b61a3); AthenaK's Newtonian mode: single patch E ~ (2 alpha)^(7/2) to 3e-14 (N3), crossing time and energy converge to the ODE (N1), pancake errors equal the seven-point-Laplacian prediction; confirmed independently by verifier2 (ellipsoid crossing 23.852370 t_k, order 2.28; sheet errors within 3 percent; run B-20261119-142135-e582e09). Reservation carried from G0 and still [TO VERIFY]: Omega today ~ sigma^(7/2) of 2403.15126:1074 against sigma^(5/2) from its eq. (result_OmZ); the criterion is judged on the emitted energy
- [x] **C8** Background error and constraint convergence with the stand-in matter
  - status: NA
  - evidence: struck by decision 0013 (particles do it directly); the particle FLRW background: lapse = a to 1.9e-7 (a = 4) and 7.0e-8 (a = 36), run B-emd-gw-20261115-115414-7ffbde1; Hamiltonian constraint in stage/G1/STATUS.md (corrected values)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C9** Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013)
  - status: PASS
  - evidence: applied: C8 struck; the N-body baseline runs in AthenaK's Newtonian mode (newton_tests); the multi-code row (shearing dust, GR against the Newtonian mode) is G2 work; item 3 amended (coord/notes/derivations_to_check.md, decision 0013)

## Minimum figures at G1 (brief 13.4)

- [x] **C10** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png (G1 version, boxes classified by evidence: verified in a run, on a tested branch, to be written; run B-20261120-223319-cc5320d), looked at by the lead
- [x] **C11** Schematic: Data-flow diagram
  - status: PASS
  - evidence: note/figures/schem_dataflow.png (initial data, AthenaK, outputs, analysis, comparison, ledger; run B-20261120-223319-cc5320d), looked at by the lead
- [x] **C12** Data figure: Baseline results
  - status: PASS
  - evidence: note/figures/fig_scan.png, fig_waves.png, fig_r2.png, fig_newton.png; first_source/figs/scan_kk0.png, res_compare.png; newton_tests/figs/pancake_east.png, ell_convergence.png
- [x] **C13** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: note/figures/fig_waves.png (both diagnostics against exact waves), fig_gauge.png; first_source/figs/t0_gauge.png, scan_null.png; stage/G1/verifier3/figs (v3_F_conv, v3_X_conv, v3_F_diag_diff, v3_X_diag_diff, v4_gauge_test); stage/review_wave3/figs/lw3_crit1.png

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, STATUS.md, VERIFIER.md (verifier2) and verifier3/VERIFIER.md in stage/G1/; the lead's rechecks are stage/REVIEW-wave2.md and stage/REVIEW-wave3.md (task-given names); scoping text scope/SCOPE.md
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: every data figure from a registered run with one script each (figstyle), looked at; the note's figures and tables are byte copies of run B-20261120-223319-cc5320d (28 of 28, cmp by the lead)
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: schem_architecture (exists / on a tested branch / to be written) and schem_timeline (G0 passed, G1 needs) with paperfig, note/scripts/schem_*.py, run B-20261120-223319-cc5320d; looked at
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: note/main.pdf v2, 21 pages (REVTeX), built from run B-20261120-223319-cc5320d; latexmk: 0 undefined references or citations, 0 overfull boxes; the paper-writing checker is clean in the main text except the allowed delta = 0.0025 hits (note/JOURNAL.md, outcome N16); all pages read by the note helper. Rewordings owed for v3: ledger rows 101, 118-119, 168 (stage/REVIEW-wave3.md)
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: in part: independent verifiers recomputed the G1 claims of wave 1 (stage/G0/VERIFIER.md), the wave-2 first-source and Newtonian runs (stage/G1/VERIFIER.md, verifier2: 12 confirmed, 3 in part, none wrong) and the criterion-1 table and gauge rows 101, 115-119 (verifier3); not recomputed by an independent agent: the second-round table of the ledger (jittered nulls, delta = 0.0025, rerun floor, parity; checked only by the note helper's own second reading, N13-N15), gauge rows 120-125, eps = 0.1 and 0.3 of rows 116-117, and the wave-1 rows outside the G0 claims. Owed: one verifier package that recomputes every remaining ledger row (no card time) (OPEN.md item 1)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed predictions and runs on record: first_source/JOURNAL.md (P1 as worded, P4, P6 with G), newton_tests/JOURNAL.md (P1a, P1b, P2a, H1a, H1c, H1d-3, N1d, N1e), waves/JOURNAL.md (F4, F6, X6, X3 at N = 32, A3, plus phase at N >= 48, cost), note/JOURNAL.md (N8 in part, N12 plus phase at N = 32, N16 page count), verifier2 and verifier3 journals (P3.5, P4.5, P4.7), population/JOURNAL.md (P2, P5, P8, P10b, I1), stage/review_wave2 (R5, R6) and stage/review_wave3 (L1 marginal, L2, L2b, L3); failed runs kept: B-20261115-161656-03d75e1, -164104-886798f, -170149-75036cf, B-20261119-142234-85da208, -145125-51e9f8f, -141813-91cfe8e, -143836-644f0a9, B-20261120-222232-3d7d57e, -223445-3686145, B-20261121-025612-ed4a875, -030110-52ae004
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten by the lead at the end of batch 2a (2026-11-20)
