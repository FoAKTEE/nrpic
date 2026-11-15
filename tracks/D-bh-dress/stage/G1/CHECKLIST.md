# Checklist: D-bh-dress G1

Collected by `harness/bin/nrpic-stage collect D-bh-dress G1` on 2026-11-15T15:00:40Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [ ] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: G1/STATUS.md rows D-pre-1..4
- [ ] **C2** The analysis pipeline validated on them
  - status: OPEN
  - evidence: pipelines validated for D-pre-2 and D-pre-4; the Einstein-Straus analysis (tracer areal radius, AH mass against wall proper time) not yet run
- [ ] **C3** Interface proposals submitted
  - status: PASS
  - evidence: outbox/20261115T1510Z__to-core__*.md

## Main products of G1 (charter 9.2)

- [ ] **C4** Baseline data and figures
  - status: PASS
  - evidence: G0/EVIDENCE.md
- [ ] **C5** Interface documents
  - status: OPEN
  - evidence: requests written as outbox files; no interface document of D's own yet (accretion diagnostics spec is in the outbox file)

## Track-specific criteria of D-bh-dress for G1 (9.7 Track D: black-hole growth and dark-matter dress (S4))

- [ ] **C6** Derivation and offline check of D-pre-1
  - status: PASS
  - evidence: einstein_straus/DERIVATION.md; runs -042626-f3da881, -042704-f3da881, -043406-4df1e76
- [ ] **C7** The baselines of D-pre-2 and D-pre-3
  - status: OPEN
  - evidence: Schwarzschild spike and D-pre-3 semi-analytic done; Kerr spike and AthenaK Newtonian-mode run open
- [ ] **C8** The noise floor of D-pre-4
  - status: PASS
  - evidence: puncture_drift; runs -121313/-121314-284ec4f, -130954-49ed46f; lead re-check -145546-5259f48

## Minimum figures at G1 (brief 13.4)

- [ ] **C9** Schematic: Updated architecture
  - status: OPEN
  - evidence: not drawn
- [ ] **C10** Schematic: Data-flow diagram
  - status: OPEN
  - evidence: not drawn
- [ ] **C11** Data figure: Baseline results
  - status: PASS
  - evidence: spike/figs/ref_*.png, secondary_infall/figs/*.png, puncture_drift/figs/drift_*.png
- [ ] **C12** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: spike/figs/stationarity_*.png, einstein_straus/figs/code_t0.png, puncture_drift/figs/drift_finder.png

## Package (brief 13.3; judged by the session)

- [ ] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: all package figures from registered runs with figstyle; looked at by their makers, key ones by the lead (G0/EVIDENCE.md, L)
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: not drawn
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: no note yet
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no fresh verifier yet
- [ ] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs kept: -121837-987643b, -122303-4e8e8af, -125449-60a62b8, -125724-464611f; refuted predictions in the journals
- [ ] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of 2026-11-15
