# Checklist: A-emd-pbh G1

Collected by `harness/bin/nrpic-stage collect A-emd-pbh G1` on 2026-11-21T03:01:41Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: stage/G1/STATUS.md section 2: expball exact solution and data sets (A-emd-pbh-20261115-121749-90764e1, -121753-90764e1, -130609-947c898), newton references (-113103-9832afd), criteria (-115120-2eb3117), gauge toys (-113614-374a41a, -113755-cac3c4b)
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: stage/G1/STATUS.md section 2 (wave 2): runs_ball/compare.py recovers the exact expanding ball in AthenaK runs (core |R/R_exact - 1| 7.6e-4 at tau = 16.894, dx = M/4; analysis A-20261115-182657-53da696), re-derived by the lead's own reader (A-20261115-182314-bebd0cf); newton/analyze_newton.py against the cycloid and the ellipsoid on Newtonian-mode runs (A-emd-pbh-20261115-164420-4528861, rerun A-20261115-182402-a46812c identical); periodic analyse_scouting.py reproduced byte for byte (A-20261115-182347-8ee3fcc); wave-1 snapshot analysis on synthetic snapshots (A-emd-pbh-20261115-113822-87cba08)
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: outbox 20261115T1320Z__* (wave 1, 7 messages) and the wave-2 requests of this session (outbox 20261115T18*Z__*)

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: expball/figures/, newton/figs/, gauge/figs/, scope/results/ from registered runs; data in scratch/A-emd-pbh/<run_id>/
- [x] **C5** Interface documents
  - status: PASS
  - evidence: stage/G1/STATUS.md section 3 (scouting-run specification); newton/SCAN.md sections 4-5; gauge/GAUGE.md, gauge/DIAGNOSTICS.md; outbox requests to core

## Track-specific criteria of A-emd-pbh for G1 (9.4 Track A: EMD primordial-black-hole formation (S1))

- [x] **C6** The constraint residuals of A-pre-1 converge at the expected order
  - status: PASS
  - evidence: stage/G1/STATUS.md T1: A-emd-pbh-20261115-121654-6bfb707, -122121-aa1c84d, -122117-aa1c84d; rerun A-emd-pbh-20261115-130402-f5566fb identical; cross-checks A-20261115-130257-a7374a4
- [x] **C7** The prediction table of A-pre-2
  - status: PASS
  - evidence: stage/G1/STATUS.md T2: criteria/predict.py, runs A-emd-pbh-20261115-120425-80492f8, -115120-2eb3117 (wave 1: 33 of 37, failures on record); lead rerun A-20261115-130252-01e8b64; wave-2 state: A-emd-pbh-20261115-161813-6c820fb (all checks) and -163358-9b2d048 (T2 after the T2.6 fix): 41 of 41 pass, 4 diagnostics without a verdict, confirmed by the G1 verifier (VERIFIER.md 2.2) and recounted in A-20261120-222454-d16dbc6 (g1close)
- [x] **C8** The scan design from A-pre-3
  - status: PASS
  - evidence: met by decision 0013 (reference-based design, newton/SCAN.md sections 1-6); wave 2 adds the Newtonian-mode runs: top-hat second order (t_ta +7.2e-4 at 128^3), first-collapse time t_1 of the 9 scan points at 128^3 with >= 2.7e5 particles other than the spindle within +2.2e-4 to +6.3e-4 of the isolated ellipsoid (spindle +1.5e-3; 64^3 controls +8.8e-4, +1.5e-3; 3.4e4-particle controls -2.4e-4, -4.6e-4; 14 points in all; sentence corrected 2026-11-20 after VERIFIER.md section 4 item 2, counted in run A-20261120-222454-d16dbc6), range of the full-relativity scan (SCAN.md section 8; runs A-emd-pbh-20261115-153409/-153415/-153437-dc27b98, -164420-4528861, -164757-b8bc9a3; lead's rerun A-20261115-182402-a46812c identical; own estimator A-20261115-182314-bebd0cf agrees)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C9** Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013)
  - status: PASS
  - evidence: applied as at G0 (C9 there): T3 judged on the reference-based design, Newtonian-mode runs done as G2 work ahead of time; the ruling's reason corrected (verifier C1c; SCOPE.md 10.9(a); proposal to orch)

## Minimum figures at G1 (brief 13.4)

- [x] **C10** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png (script note/scripts/schem_architecture.py), drawn in wave 2 after the release core-v0.3, so it is the current architecture (exists / to be ported / new); the wave-2 runs change no box of it [JUDGEMENT]; PNG looked at by the note helper
- [x] **C11** Schematic: Data-flow diagram
  - status: PASS
  - evidence: note/figures/schem_dataflow.png (script note/scripts/schem_dataflow.py, vendored paperfig.py): four lanes (expanding ball, periodic box, Newtonian mode, criteria and scope) from initial data through AthenaK and raw outputs to the analysis, products, common.py/ledger.py and main.pdf, with the registration of runs and the verifier's path; drawn by the G1 verifier (run A-20261119-143347-37240f3, commit e2999bb2); common.py box updated for the integrity listing (commit 2c115cb1); in the note as Fig. 7 with caption in App. B (commit 2c115cb1); regenerated in runs A-20261120-223316-92c27f5 and A-20261121-030037-3f015fa; PNG looked at (VERIFIER.md C11; g1close/JOURNAL.md entry 5) and on page 9 of note/main.pdf
- [x] **C12** Data figure: Baseline results
  - status: PASS
  - evidence: expball/figures/fig_exact_shells.png, fig_constraint_convergence.png; newton/figs/fig_scan_hoop_time.png; scouting predictions fig_scouting_predictions.png (A-20261115-130948-5a2b58a)
- [x] **C13** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: newton/figs/fig_axes_selftest.png; lead fig_crosscheck.png (A-20261115-130257-a7374a4)

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, STATUS.md (criterion by criterion), VERIFY (commands) in stage/G1; lead's re-check ../REVIEW-wave2.md; scoping text scope/SCOPE.md
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: as G0 C13
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: as G0 C16: note/scripts/schem_architecture.py and schem_timeline.py with the vendored paperfig.py; the timeline brought to the wave-3 state (G0 passed, G1 at its review, what G2 needs) in run A-20261121-030037-3f015fa (commit 8b7304f5), PNG looked at
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: note v1 (12 pages, 2026-11-20): check_manuscript.py --compile on note/main.tex with the guide's --forbid list, 0 undefined references and citations, 0 overfull boxes; 5.5/5.8 candidates only in the ledger appendix and the scripts (WRITING_GUIDE.md exception 1; schem_dataflow.py and Fig. 7 still to be named in it, request to the lead); every page read (g1close/JOURNAL.md entries 6-7)
- [x] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS [JUDGEMENT of the g1close helper; the gate reviewer decides]
  - evidence: stage/G1/VERIFIER.md by a fresh verifier of wave 2b (run A-20261119-142905-c813c01; predictions committed before any run, commit 2256c860; scripts c813c017; sections 1-3 written before reading the track's review, 37240f39; comparison section 4, db950ae8): own code for the note's ledger (42 rows: 39 confirmed, 2 wrong labels/statements, 1 not recomputed: the predicted card-hours of a cost model), the criteria checks (19 of 19), newton/ (17 of 17), runs_ball (12 of 12, SR-2 turnaround estimator-dependent), the note's statements (15 of 17). Its corrections, each checked at the source (run A-20261120-222454-d16dbc6) and applied or partly rebutted (g1close/JOURNAL.md entries 1-4): median label, bang time in the taper, units M_0, six threshold names, checksum sentence (integrity listing run A-20261120-222620-0304d9d), wave-2 state, STATUS T3/C8 band (9 points, not 4), SR-1 breakdown criterion, SR-2 estimator; commits d34bcb87, f26e7f58, 2c115cb1, 3f015fa0, 8b7304f5. Not recomputed by a fresh verifier (named in note App. B and OPEN.md item 1): the predicted card-hours, the four cross-check differences (read from crosscheck.json), and five rows added in note v1 to Table IV from the wave-2 analyses (tracked-particle residuals, constraint norm at t = 20, two central-lapse rows, compactness on the axes). Judged PASS on the scope the gate asked of the verifier (OPEN.md of wave 2, item 2: ledger, newton/, criteria/); a strict reading of "every number" leaves these rows open
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: as G0 C17
- [ ] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: FAIL
  - evidence: stage/G1/STATUS.md brought to the wave-3 state by g1close (2026-11-20); the owner's STATUS.md, JOURNAL.md and HANDOFF.md were last changed on 2026-11-15 (git log) and still give G0 as not passed and the wave-1/2 statements the verifier corrected (STATUS.md line 13 "14 scan points within 6.3e-4"); the lead rewrites them at the end of wave 3 round 1 (helpers do not write them)
