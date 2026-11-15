# Checklist: C-sidm G1

Collected by `harness/bin/nrpic-stage collect C-sidm G1` on 2026-11-15T19:39:53Z from `coord/CHARTER.md` (last changed in b7b431dd) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [ ] **C1** Baseline results obtainable without the NRPIC coupling
  - status: OPEN
  - evidence: 
- [ ] **C2** The analysis pipeline validated on them
  - status: OPEN
  - evidence: 
- [ ] **C3** Interface proposals submitted
  - status: OPEN
  - evidence: 

## Main products of G1 (charter 9.2)

- [ ] **C4** Baseline data and figures
  - status: OPEN
  - evidence: 
- [ ] **C5** Interface documents
  - status: OPEN
  - evidence: 

## Track-specific criteria of C-sidm for G1 (9.6 Track C: relativistic collapse of an SIDM core (S3))

- [ ] **C6** All tests of C-pre-1 pass
  - status: OPEN
  - evidence: 
- [ ] **C7** The baseline is reproduced
  - status: OPEN
  - evidence: 

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [ ] **C8** Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013)
  - status: OPEN
  - evidence: 

## Minimum figures at G1 (brief 13.4)

- [ ] **C9** Schematic: Updated architecture
  - status: OPEN
  - evidence: 
- [ ] **C10** Schematic: Data-flow diagram
  - status: OPEN
  - evidence: 
- [ ] **C11** Data figure: Baseline results
  - status: OPEN
  - evidence: 
- [ ] **C12** Data figure: Validation figures for the analysis pipeline
  - status: OPEN
  - evidence: 

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: 
- [ ] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: 
- [ ] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: 
- [ ] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: 
- [ ] **C17** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: 
- [ ] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: OPEN
  - evidence: 
- [ ] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: 
