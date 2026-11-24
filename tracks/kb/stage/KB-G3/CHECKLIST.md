# Checklist: kb KB-G3

Collected by `harness/bin/nrpic-stage collect kb KB-G3` on 2026-11-24T23:36:49Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G3 (brief 12.10; charter 9.10)

- [ ] **C1** Every statement in the evidence queue that bears on G1 of the six tracks has been processed
  - status: FAIL
  - evidence: Met for every track queue (A-F, core: each to_verify claim has a processing event; 409, 447, 449, 450 verified and 452 annotated this batch). Not met for two brief seeds that bear on G1 of A, B, D, F: 803 (FLRW stability) and 805 (three derivations). Evidence: EVIDENCE.md table (snapshot kb-20261124-9872d21), runs kb-20261124-233445-89478ae, kb-20261124-233504-c6530a6, kb-20261124-233637-3d710a8, kb-20261124-233726-3b6e5b9; OPEN.md O1, O2.

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [x] **C2** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: PASS
  - evidence: `kb` opens kb-data/db/current by default (kb status: snapshot kb-20261124-9872d21.sqlite); every `kb show` view ends with the snapshot id (C6b of KB-G2, met since batch 9).
- [x] **C3** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: PASS
  - evidence: `kb snapshot` at the end of this stage: kb-20261124-9872d21 (sha256 9872d212...; run kb-20261124-233515-0ed31c7); EVIDENCE.md names it for every number; the messages to A, C, D, F and orch carry it.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C4** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md, SCOPE.md in tracks/kb/stage/KB-G3/.
- [x] **C5** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot
  - status: PASS
  - evidence: VERIFIER.md of a fresh helper session (batch 11): 54/60 sampled claims right; its numbers recomputed from its own runs on snapshot kb-20261121-aa0a2ae. It predates this batch's corrections; a second verifier after O1-O3 is OPEN.md O6.
- [x] **C6** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed run kb-20261124-233445-89478ae (three relocates without --by) on record with manifest and JOURNAL outcome C1; prediction outcomes R1, C1 (failed in part), C1b, C2, C3, S1, Q2 in tracks/kb/JOURNAL.md.
- [x] **C7** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md rewritten in this session (batch 13).
