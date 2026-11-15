# Checklist: D-bh-dress G0

Collected by `harness/bin/nrpic-stage collect D-bh-dress G0` on 2026-11-15T15:00:40Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [ ] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: REPORT.md sections 1-4; scope/SCOPE.md
- [ ] **C2** The statements of the key references verified in the knowledge base
  - status: PASS
  - evidence: scope/REFERENCES.md (18 sources, locators); REPORT.md section 5 (re-read by the lead)
- [ ] **C3** Risk list
  - status: PASS
  - evidence: REPORT.md section 6; RISKS.md; scope/SCOPE.md section 8
- [ ] **C4** Compute estimate
  - status: PASS
  - evidence: REPORT.md section 7; runs D-bh-dress-20261115-120304-795eee9, -145950-23fa1c7

## Main products of G0 (charter 9.2)

- [ ] **C5** Working note v0
  - status: OPEN
  - evidence: no REVTeX note yet (OPEN.md item 1)
- [ ] **C6** Architecture schematic
  - status: OPEN
  - evidence: not drawn (OPEN.md item 2)
- [ ] **C7** Stage timeline
  - status: OPEN
  - evidence: text in REPORT.md section 8; schematic not drawn

## Track-specific criteria of D-bh-dress for G0 (9.7 Track D: black-hole growth and dark-matter dress (S4))

- [ ] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: the sheet has no G0-specific criterion

## Minimum figures at G0 (brief 13.4)

- [ ] **C9** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: OPEN
  - evidence: OPEN.md item 2
- [ ] **C10** Schematic: Stage timeline
  - status: OPEN
  - evidence: OPEN.md item 2
- [ ] **C11** Data figure: None required
  - status: NA
  - evidence: none required
- [ ] **C12** Data figure: Data from the literature may be redrawn
  - status: NA
  - evidence: optional

## Package (brief 13.3; judged by the session)

- [ ] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: scope/figs/scoping_estimates.png from run D-bh-dress-20261115-120304-795eee9 with python/nrpic/figstyle.py; looked at
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: OPEN.md item 2
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: OPEN.md item 1
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: OPEN.md item 3 (lead re-checks are not artefact-only)
- [ ] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: EVIDENCE.md lists failed and superseded runs; journals
- [ ] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of 2026-11-15
