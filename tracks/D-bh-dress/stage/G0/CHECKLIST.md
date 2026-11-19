# Checklist: D-bh-dress G0

Collected by `harness/bin/nrpic-stage collect D-bh-dress G0` on 2026-11-19T15:24:07Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: REPORT.md sections 1-4; scope/SCOPE.md
- [x] **C2** The statements of the key references verified in the knowledge base
  - status: PASS
  - evidence: scope/REFERENCES.md (18 sources, locators); REPORT.md section 5 (re-read by the lead)
- [x] **C3** Risk list
  - status: PASS
  - evidence: REPORT.md section 6; RISKS.md; scope/SCOPE.md section 8
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: REPORT.md section 7; runs D-bh-dress-20261115-120304-795eee9, -145950-23fa1c7

## Main products of G0 (charter 9.2)

- [x] **C5** Working note v0
  - status: PASS
  - evidence: note/main.tex, note/main.pdf (REVTeX, 10 pages; figures and tables of run D-bh-dress-20261115-171627-18706fb); lead: clean compile and ledger rerun byte for byte, run D-20261115-193951-be7b41d; lapse sentence corrected (REVIEW-wave2 section 4)
- [x] **C6** Architecture schematic
  - status: PASS
  - evidence: note/figures/schem_architecture.png (note/scripts/schem_architecture.py, run D-bh-dress-20261115-171627-18706fb); looked at by the lead (note p. 2)
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png (note/scripts/schem_timeline.py, run D-bh-dress-20261115-171627-18706fb); text in REPORT.md section 8

## Track-specific criteria of D-bh-dress for G0 (9.7 Track D: black-hole growth and dark-matter dress (S4))

- [x] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: the sheet has no G0-specific criterion

## Minimum figures at G0 (brief 13.4)

- [x] **C9** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: PASS
  - evidence: note/figures/schem_architecture.png (exists / to be ported / new), run D-bh-dress-20261115-171627-18706fb
- [x] **C10** Schematic: Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png, run D-bh-dress-20261115-171627-18706fb
- [x] **C11** Data figure: None required
  - status: NA
  - evidence: none required
- [x] **C12** Data figure: Data from the literature may be redrawn
  - status: NA
  - evidence: optional

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (-> ../REVIEW-wave2.md); scoping text scope/SCOPE.md; REPORT.md of wave 1 kept (decision 0012)
- [x] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: scope/figs/scoping_estimates.png (run D-bh-dress-20261115-120304-795eee9, figstyle); note/figures/fig_*.png (five, czstyle, one script each, run D-bh-dress-20261115-171627-18706fb); verifier figures stage/G0/figs/*.png; looked at (lead: fig pages 1-3 of the note, v2_drift, v4b_compare)
- [x] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/scripts/schem_architecture.py, schem_timeline.py with the vendored paperfig.py (unchanged copy of harness/style/)
- [x] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: paper-writing guide and notation (WRITING_GUIDE.md, NOTATION.md); check_manuscript.py --compile after the lead's fix: 0 undefined references or citations, 0 overfull boxes; 2 of 16 checks have candidates, all in the ledger appendix (run ids) and the registration scripts, which the guide exempts
- [x] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: stage/G0/VERIFIER.md (fresh-context verifier of the plan, decision 0016 items 1 and 4: eight claims recomputed from the artefacts; runs D-20261115-170002-8cefc3e, -170224-924d1d9, -171508-94e8cb1, -171532-ba23a99, -171534-ff5b0e9, -171543-d966aba, -171545-d7e01a7, -171953-908afff, -171818-a5aefe8, -173149-7c6dd72); its WRONG (C8 cost) and NOT CONFIRMED (C4 criterion) items with what the track does: ../REVIEW-wave2.md sections 5 and 8; the note's numbers recomputed by note/tables/claims.md (36) and rerun byte for byte by the lead (D-20261115-193951-be7b41d)
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs kept (EVIDENCE.md); refuted predictions in JOURNAL.md, es_runs/JOURNAL.md, spike/JOURNAL.md, secondary_infall/JOURNAL.md, note/JOURNAL.md, stage/G0/JOURNAL.md; superseded runs D-20261115-170326-dfb2a02, -171733-633d422, -193755-3a53b08
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of wave 2 (2026-11-15T20:40Z)
