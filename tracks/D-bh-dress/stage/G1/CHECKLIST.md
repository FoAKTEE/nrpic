# Checklist: D-bh-dress G1

Collected by `harness/bin/nrpic-stage collect D-bh-dress G1` on 2026-11-21T06:38:54Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: G1/STATUS.md rows D-pre-1..4
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: D-pre-2 (binning, invariants, crossing times; lead recheck D-20261115-193844-df4523c), D-pre-3 (masses; lead's own implementation D-20261115-193823-88f7f86), D-pre-4 (finder re-search); Einstein-Straus pipeline on AthenaK output of ES-1/V-1 (D-20261115-172726-60ba4c2, -172730-c6d151b; analysis D-20261119-141839-8686bd7, -142929-bb375ff; lead Y1-Y6 D-20261119-151039-b2ce968) and of ES-1G (D-20261119-142633-6f72922; analysis D-20261120-221754-ae3dafe, -222424-230f936; lead Z1-Z2 D-20261121-063617-3f2036f: horizon, wall 1.68e-4, crossings, proper time reproduced to the printed digits); fresh verifier V1 reproduced the ES-1/V-1 numbers (stage/G1/VERIFIER.md). Vacuum-bubble floor at M/8 with the faces at +-384 M: 4.8e-5 over 100-200 M (V-1B D-20261120-222625-63abd72, lead Z3); that is G2 material
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: outbox/20261115T1510Z__to-core__*.md (8); core answered 6 (core/requests-adf outbox dfix-answers; scratch/core/exe/core_requests-adf/READY items 1-5)

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: G0/EVIDENCE.md
- [x] **C5** Interface documents
  - status: PASS
  - evidence: D's specifications (outbox accretion-diagnostics, analytic-metric-excision, newtonian-mode-point-mass, tracer rule) are documented as options by core: core/requests-adf tracks/core/interfaces/REQUESTS_ADF.md and READY; D has no interface document of its own

## Track-specific criteria of D-bh-dress for G1 (9.7 Track D: black-hole growth and dark-matter dress (S4))

- [x] **C6** Derivation and offline check of D-pre-1
  - status: PASS
  - evidence: einstein_straus/DERIVATION.md; runs -042626-f3da881, -042704-f3da881, -043406-4df1e76
- [ ] **C7** The baselines of D-pre-2 and D-pre-3
  - status: OPEN
  - evidence: D-pre-2 MET: equatorial Kerr reference confirmed by the fresh verifier (V3: constant f 0.85/0.88 per cent, Hernquist a = 0 1.67 per cent, a = 0.8 peak 4.5 per cent below FdRW with the gap in FdRW's curve [JUDGEMENT]); AthenaK stationarity confirmed (V4); axis curve NOT CONFIRMED. D-pre-3: growth MET (M_ta within 0.3 per cent of the kernel shells at a/a_i = 2, 4, 8; dress within 1.1 per cent from a/a_i = 3, 0.5-3.3 per cent at 2: verifier V2, lead Z4 D-20261121-063617-3f2036f); profile about 25 per cent from the self-similar solution at a/a_i = 8, sensitive to r_ta; the criterion as written (r^-9/4) fails for an exact code: ruling d-pre-3-criterion open at orch since 2026-11-15, or the run to a/a_i = 30 (secondary_infall, design and references done, production run not started)
- [x] **C8** The noise floor of D-pre-4
  - status: PASS
  - evidence: puncture_drift; runs -121313/-121314-284ec4f, -130954-49ed46f; lead re-check -145546-5259f48

## Minimum figures at G1 (brief 13.4)

- [x] **C9** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png redrawn (run D-20261120-222429-026731f; P10 of note/JOURNAL.md): exists / provided by core / new for Track D, core's wave-2 capabilities (tracers on timelike orbits, removal record, flux spheres, analytic excision, Newtonian point mass, relaxed lapse, threaded build) and the run chain; looked at by the lead (../REVIEW-wave3.md section 6)
- [x] **C10** Schematic: Data-flow diagram
  - status: PASS
  - evidence: note/figures/schem_architecture.png is drawn as the data flow: initial data -> evolution in AthenaK -> analysis against references -> deliverables (run D-bh-dress-20261115-171627-18706fb)
- [x] **C11** Data figure: Baseline results
  - status: PASS
  - evidence: spike/figs/ref_*.png, kerr_ref_*.png, secondary_infall/figs/nm_*.png, puncture_drift/figs/drift_*.png, note/figures/fig_*.png
- [x] **C12** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: spike/figs/stationarity_*.png, kerr_main_*.png, slice_control.png; secondary_infall/figs/nm_field.png, nm_clumpstab.png; einstein_straus/figs/code_t0.png; puncture_drift/figs/drift_finder.png; lead: stage/review_wave2 figures (runs D-20261115-193819-df9f812 ... -193844-df4523c)

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report, 2026-11-21), EVIDENCE.md, OPEN.md, CHECKLIST.md, VERIFIER.md (fresh verifier, 2026-11-21), REVIEW.md (-> ../REVIEW-wave2.md sections 1-3, 6, 8 and ../REVIEW-wave3.md), STATUS.md (the G1 criteria one by one); scoping text scope/SCOPE.md
- [x] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: all package figures from registered runs with figstyle/czstyle, one script each; looked at by their makers; lead looked at the key ones (REVIEW-wave2.md)
- [x] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/scripts/schem_architecture.py, schem_timeline.py (paperfig.py)
- [ ] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: note v0 (main.pdf, 2026-11-15) passed check_manuscript.py --compile (0 undefined, 0 overfull); the v1 text and figures (commit c2e0571d; runs D-20261120-222413-4a67fa2 ... -223535-24f7f90) are committed but the PDF was not rebuilt and the checker not rerun on them (package note cut on 2026-11-20; P11-P12 open)
- [x] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: stage/G1/VERIFIER.md (copy of verifier_g1/VERIFIER.md, helper verifier_g1, fresh context, verdicts committed in 102d696b before any review was read): V1-V6, 34 ledger rows agree, no row WRONG; WRONG as worded: dress at a/a_i = 2 (corrected in STATUS.md); NOT CONFIRMED: Hernquist axis curve, eight ledger rows; the track's action on each item: ../REVIEW-wave3.md section 2. Runs D-20261120-222209-871e07f, D-20261121-031031-e23da04, -031711-0d79cb3, -033209-9c0bd44, -034048-17427b0, -035106-0c619ee, -040417-8a3c402, -035114-8a3cb38, -040636-e8d5352, -040826-9d5051a (verify PASS)
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs kept: -121837-987643b, -122303-4e8e8af, -125449-60a62b8, -125724-464611f, -171733-633d422 (stopped); superseded: D-20261115-170326-dfb2a02, -193755-3a53b08, D-20261119-151012-b4afa8a, and the verifier's reference counts of D-20261121-034048-17427b0, -035106-0c619ee, -040417-8a3c402; refuted predictions in the journals (es_runs entries 1-3, 4-7, and entry 9: G2 failed, G6 refuted, J5, K1, K2 refuted; spike K1-K3; secondary_infall wave 2; note P4-P6; flux_tools entry 6b: momentum residual and growth-summary predictions; drift_controls A2 asphericity, pre-flight C1 at 3.1e-8 against 1e-8; the verifier's own V4 error, recorded)
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of batch 2a (2026-11-21)
