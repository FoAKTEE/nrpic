# Checklist: kb KB-G3

Collected by `harness/bin/nrpic-stage collect kb KB-G3` on 2026-11-24T23:36:49Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G3 (brief 12.10; charter 9.10)

- [ ] **C1** Every statement in the evidence queue that bears on G1 of the six tracks has been processed
  - status: OPEN
  - evidence: 

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [ ] **C2** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: OPEN
  - evidence: 
- [ ] **C3** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: OPEN
  - evidence: 

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C4** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: 
- [ ] **C5** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot
  - status: OPEN
  - evidence: 
- [ ] **C6** Null results and failed runs are on record (manifests and JOURNAL)
  - status: OPEN
  - evidence: 
- [ ] **C7** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: 
