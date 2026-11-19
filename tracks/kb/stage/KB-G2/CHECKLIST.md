# Checklist: kb KB-G2

Collected by `harness/bin/nrpic-stage collect kb KB-G2` on 2026-11-19T16:21:41Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G2 (brief 12.10; charter 9.10)

- [ ] **C1** All papers and repositories ingested
  - status: OPEN
  - evidence: 
- [ ] **C2** The QA report meets the parse success rate and retrieval hit rate written in CHARTER (thresholds: coord/CHARTER.md, "Gates of the knowledge base"; items below)
  - status: OPEN
  - evidence: 

## Thresholds of KB-G2 (coord/CHARTER.md, "Gates of the knowledge base"; decision 0016 item 6)

- [ ] **C3** Parse success rate: at least 95 per cent of the ingested papers are parsed successfully.
  - status: OPEN
  - evidence: 
- [ ] **C4** Retrieval hit rate: at least 80 per cent of the golden questions are answered with the right paper among the top ten results; the hit at the answer location is reported, not gating.
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
- [ ] **C8** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot
  - status: OPEN
  - evidence: 
- [ ] **C9** Null results and failed runs are on record (manifests and JOURNAL)
  - status: OPEN
  - evidence: 
- [ ] **C10** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: 
