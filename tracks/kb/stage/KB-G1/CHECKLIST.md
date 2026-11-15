# Checklist: kb KB-G1

Collected by `harness/bin/nrpic-stage collect kb KB-G1` on 2026-11-15T18:29:11Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G1 (brief 12.10; charter 9.10)

- [ ] **C1** The inventory report
  - status: OPEN
  - evidence: 
- [ ] **C2** All priority-3 papers ingested
  - status: OPEN
  - evidence: 
- [ ] **C3** Code index and parameter index of AthenaK
  - status: OPEN
  - evidence: 
- [ ] **C4** The answers to the first questions
  - status: OPEN
  - evidence: 

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [ ] **C5** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: OPEN
  - evidence: 
- [ ] **C6** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: OPEN
  - evidence: 

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C7** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: 
- [ ] **C8** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md: the package's numbers recomputed from the run manifests and the snapshot
  - status: OPEN
  - evidence: 
- [ ] **C9** Null results and failed runs are on record (manifests and JOURNAL)
  - status: OPEN
  - evidence: 
- [ ] **C10** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: 
