# Checklist: A-emd-pbh G1

Collected by `harness/bin/nrpic-stage collect A-emd-pbh G1` on 2026-11-15T18:34:05Z from `coord/CHARTER.md` (last changed in b7b431dd) and the brief (sections 13.3 and 13.4).
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
  - evidence: stage/G1/STATUS.md T2: criteria/predict.py, runs A-emd-pbh-20261115-120425-80492f8, -115120-2eb3117 (33/37, failures on record); lead rerun A-20261115-130252-01e8b64
- [x] **C8** The scan design from A-pre-3
  - status: PASS
  - evidence: met by decision 0013 (reference-based design, newton/SCAN.md sections 1-6); wave 2 adds the Newtonian-mode runs: top-hat second order (t_ta +7.2e-4 at 128^3), 14 scan points within 2.2e-4 to 6.3e-4 of the isolated ellipsoid, range of the full-relativity scan (SCAN.md section 8; runs A-emd-pbh-20261115-153409/-153415/-153437-dc27b98, -164420-4528861, -164757-b8bc9a3; lead's rerun A-20261115-182402-a46812c identical; own estimator A-20261115-182314-bebd0cf agrees)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C9** Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013)
  - status: PASS
  - evidence: applied as at G0 (C9 there): T3 judged on the reference-based design, Newtonian-mode runs done as G2 work ahead of time; the ruling's reason corrected (verifier C1c; SCOPE.md 10.9(a); proposal to orch)

## Minimum figures at G1 (brief 13.4)

- [x] **C10** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png (script note/scripts/schem_architecture.py), drawn in wave 2 after the release core-v0.3, so it is the current architecture (exists / to be ported / new); the wave-2 runs change no box of it [JUDGEMENT]; PNG looked at by the note helper
- [ ] **C11** Schematic: Data-flow diagram
  - status: FAIL
  - evidence: no data-flow diagram drawn (initial data -> AthenaK -> outputs -> comparison scripts -> ledger); to be drawn with paperfig.py (HANDOFF next actions)
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
  - evidence: as G0 C16: note/scripts/schem_architecture.py and schem_timeline.py with the vendored paperfig.py
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: as G0 C17: check_manuscript.py --compile on note/main.tex, 0 undefined references and citations, 0 overfull boxes
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: FAIL
  - evidence: VERIFIER.md (stage/G0) checks the G1 criteria T1 (its C5: constraint orders 2 and 4 recomputed with its own construction of data set 2t) and T2 in part (C2, C3); it did not examine newton/ (T3) or the criteria package's 37 checks; the lead's independent checks (../REVIEW-wave2.md) are not a fresh verifier's; the note's ledger is not recomputed by a verifier (as G0 C18)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: as G0 C17
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of wave 2
