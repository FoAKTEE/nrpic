# Checklist: D-bh-dress G1

Collected by `harness/bin/nrpic-stage collect D-bh-dress G1` on 2026-11-19T15:24:07Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: G1/STATUS.md rows D-pre-1..4
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: D-pre-2 (binning, invariants, crossing times; lead recheck D-20261115-193844-df4523c), D-pre-3 (masses; lead's own implementation D-20261115-193823-88f7f86), D-pre-4 (finder re-search); Einstein-Straus pipeline on AthenaK output of ES-1/V-1 (D-20261115-172726-60ba4c2, -172730-c6d151b): wall tracers on the exact curve to 2.2e-3 for tau <= 200 M, crossings of R = 2M to 6e-4 and 5.6e-3 M, horizon mass against the matched control (analysis D-20261119-141839-8686bd7, -142929-bb375ff); reproduced by the lead's independent code, Y1-Y6 held (D-20261119-151039-b2ce968; ../REVIEW-wave2.md section 6). The null-test floor in the ES set-up is not yet stated (late common drift after 165 M, cause open): that is G2 work
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
  - evidence: D-pre-2 met (Schwarzschild and Kerr reference, AthenaK stationarity a = 0 and 0.8; Hernquist Kerr 4 per cent below FdRW, TO VERIFY); D-pre-3: growth of the dress met in AthenaK's Newtonian mode (0.1-0.5 per cent against matched shells); the profile criterion as written (r^-9/4, slope -9/4 +- 0.05) fails for an exact code (verifier C4): restatement proposed to orch (outbox)
- [x] **C8** The noise floor of D-pre-4
  - status: PASS
  - evidence: puncture_drift; runs -121313/-121314-284ec4f, -130954-49ed46f; lead re-check -145546-5259f48

## Minimum figures at G1 (brief 13.4)

- [ ] **C9** Schematic: Updated architecture
  - status: OPEN
  - evidence: note/figures/schem_architecture.png (wave 2) predates core's wave-2 executables (tracer rule, accretion diagnostics, analytic excision, Newtonian point mass on core/requests-adf; lapse_leak on core/gauge) and the ES-1/V-1/ES-1G chain: to be redrawn (not done in wave 2b)
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
  - evidence: STAGE_REPORT.md (nrpic-stage report, 2026-11-19), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (-> ../REVIEW-wave2.md sections 1-3, 6, 8), STATUS.md (the G1 criteria one by one); scoping text scope/SCOPE.md
- [x] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: all package figures from registered runs with figstyle/czstyle, one script each; looked at by their makers; lead looked at the key ones (REVIEW-wave2.md)
- [x] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/scripts/schem_architecture.py, schem_timeline.py (paperfig.py)
- [x] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: note/main.pdf; check_manuscript.py --compile: 0 undefined, 0 overfull; 2 of 16 checks with candidates only in the ledger appendix and registration scripts
- [ ] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no fresh-context verifier of the G1 material yet (decision 0016 item 4: a verifier of later material belongs to G1); ../G0/VERIFIER.md covers the plan and the wave-1 baselines; the wave-2 baselines (Kerr spike, Newtonian mode) and the ES-1/V-1 outcome were rechecked by the leads with the helpers' reports in hand (../REVIEW-wave2.md), which does not count as fresh context; requested from orch (outbox 2026-11-19)
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs kept: -121837-987643b, -122303-4e8e8af, -125449-60a62b8, -125724-464611f, -171733-633d422 (stopped); superseded: D-20261115-170326-dfb2a02, -193755-3a53b08, D-20261119-151012-b4afa8a; refuted predictions in the journals (es_runs entries 1-3; entries 4-7 of wave 2b: the 3e-5 drift, ES-1 within V-1's floor, the +1.5e-3 horizon level, the 1+log plateau model A2 and prediction 4, A3's lapse minimum, the boundary hypothesis E2 and its probe tests; spike K1-K3, secondary_infall wave 2, note P4-P6)
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of wave 2b (2026-11-19); the wave-2 lead was cut off before rewriting them
